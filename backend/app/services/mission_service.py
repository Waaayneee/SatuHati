"""Missions: create, confirm limits, edit. Callers commit."""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.models import Approval, Mission
from app.models.enums import MissionStatus
from app.services import approval_service, audit_service
from app.services.errors import Conflict, InvalidInput, NotFound, PermissionDenied

# Changing these on an active mission is Tier 3 (change_mission_limits, HOD only).
LIMIT_FIELDS = (
    "product",
    "quantity",
    "hard_budget_myr",
    "minimum_quality",
    "delivery_deadline",
    "max_rounds",
    "approval_policy",
)
# Committee Members and the HOD may edit these directly.
OPEN_FIELDS = ("goal_text", "target_total_myr", "notes")
# The agent may only write notes; everything else it can only suggest.
AGENT_FIELDS = ("notes",)
REQUIRED_FOR_CONFIRM = ("product", "quantity", "hard_budget_myr", "minimum_quality", "delivery_deadline", "max_rounds")
CLOSED_STATUSES = (MissionStatus.COMPLETED.value, MissionStatus.CANCELLED.value)
PRE_CONFIRM_STATUSES = (MissionStatus.DRAFT.value, MissionStatus.AWAITING_HOD_CONFIRMATION.value)


@dataclass
class UpdateResult:
    mission: Mission
    updated_fields: list[str]
    approval: Approval | None


def _now() -> datetime:
    return datetime.now(UTC)


def json_value(value: Any) -> Any:
    """Stable JSON form for snapshots and comparisons."""
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")  # 1500.00 and 1500 compare equal
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def _coerce(field: str, value: Any) -> Any:
    if value is None:
        return None
    try:
        if field in ("hard_budget_myr", "target_total_myr", "minimum_quality"):
            return Decimal(str(value))
        if field in ("quantity", "max_rounds"):
            return int(value)
        if field == "delivery_deadline":
            return value if isinstance(value, date) else date.fromisoformat(str(value))
    except (ValueError, ArithmeticError):
        raise InvalidInput(f"{field} has an invalid value") from None
    return value


def _validate(values: dict[str, Any]) -> None:
    budget, target = values.get("hard_budget_myr"), values.get("target_total_myr")
    if budget is not None and budget <= 0:
        raise InvalidInput("Hard budget must be positive")
    if target is not None and target < 0:
        raise InvalidInput("Target price cannot be negative")
    if budget is not None and target is not None and target > budget:
        raise InvalidInput("Target price cannot exceed the hard budget")
    quantity = values.get("quantity")
    if quantity is not None and quantity <= 0:
        raise InvalidInput("Quantity must be positive")
    quality = values.get("minimum_quality")
    if quality is not None and not (0 <= quality <= 5):
        raise InvalidInput("Minimum quality must be between 0 and 5")
    rounds = values.get("max_rounds")
    if rounds is not None and not (1 <= rounds <= 10):
        raise InvalidInput("Max rounds must be between 1 and 10")


def _state(mission: Mission) -> dict[str, Any]:
    return {f: getattr(mission, f) for f in (*LIMIT_FIELDS, *OPEN_FIELDS)}


def limits_of(mission: Mission) -> dict[str, Any]:
    return {f: json_value(getattr(mission, f)) for f in LIMIT_FIELDS}


def next_mission_code(db: Session) -> str:
    number = db.execute(text("SELECT nextval('mission_code_seq')")).scalar_one()
    return f"MISSION-{number:03d}"


def get_mission(db: Session, mission_id: uuid.UUID) -> Mission:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise NotFound("Mission not found")
    return mission


def resolve_mission(db: Session, ref: str) -> Mission:
    """Accepts a mission UUID or a code such as MISSION-001."""
    try:
        return get_mission(db, uuid.UUID(ref))
    except ValueError:
        pass
    mission = db.scalars(select(Mission).where(Mission.code == ref.strip().upper())).one_or_none()
    if mission is None:
        raise NotFound(f"Mission {ref} not found")
    return mission


def mission_to_dict(mission: Mission) -> dict[str, Any]:
    def money(v: Decimal | None) -> float | None:
        return float(v) if v is not None else None

    return {
        "id": str(mission.id),
        "code": mission.code,
        "status": mission.status,
        "goal_text": mission.goal_text,
        "product": mission.product,
        "quantity": mission.quantity,
        "target_total_myr": money(mission.target_total_myr),
        "hard_budget_myr": money(mission.hard_budget_myr),
        "minimum_quality": money(mission.minimum_quality),
        "delivery_deadline": mission.delivery_deadline.isoformat() if mission.delivery_deadline else None,
        "max_rounds": mission.max_rounds,
        "notes": mission.notes,
        "limits_confirmed": mission.limits_confirmed_at is not None,
    }


def _require_member(actor: Actor) -> None:
    if not (actor.is_committee_member or actor.is_hod):
        raise PermissionDenied("Only Committee Members and the HOD can do this")


def _check_complete(mission: Mission) -> None:
    missing = [f for f in REQUIRED_FOR_CONFIRM if getattr(mission, f) is None]
    if missing:
        raise InvalidInput(f"Fill these limits first: {', '.join(missing)}")


def _confirm(db: Session, actor: Actor, mission: Mission) -> None:
    mission.status = MissionStatus.ACTIVE.value
    mission.limits_confirmed_by = actor.user_id
    mission.limits_confirmed_at = _now()
    db.flush()
    audit_service.record(
        db,
        actor,
        "mission.limits_confirmed",
        mission_id=mission.id,
        input_ref={"action_type": "confirm_mission_limits", "tier": 3, "limits": limits_of(mission)},
        result_ref={"status": mission.status},
    )


def create_mission(db: Session, actor: Actor, data: dict[str, Any], confirm_limits: bool = False) -> Mission:
    """Committee Members create missions awaiting HOD confirmation. The HOD may
    create and confirm in one step."""
    _require_member(actor)
    if confirm_limits and not actor.is_hod:
        raise PermissionDenied("Only the HOD can confirm mission limits")
    allowed = set(LIMIT_FIELDS) | set(OPEN_FIELDS)
    unknown = set(data) - allowed
    if unknown:
        raise InvalidInput(f"Unknown fields: {', '.join(sorted(unknown))}")
    values = {k: _coerce(k, v) for k, v in data.items()}
    if not (values.get("goal_text") or "").strip():
        raise InvalidInput("Goal is required")
    _validate(values)

    mission = Mission(
        code=next_mission_code(db),
        owner_id=actor.user_id,
        status=MissionStatus.AWAITING_HOD_CONFIRMATION.value,
        **values,
    )
    if confirm_limits:
        _check_complete(mission)
    db.add(mission)
    db.flush()
    audit_service.record(
        db,
        actor,
        "mission.created",
        mission_id=mission.id,
        input_ref={"limits": limits_of(mission), "target_total_myr": json_value(mission.target_total_myr)},
        result_ref={"code": mission.code, "status": mission.status},
    )
    if confirm_limits:
        _confirm(db, actor, mission)
    return mission


def confirm_limits(db: Session, actor: Actor, mission: Mission) -> Mission:
    if not actor.is_hod:
        raise PermissionDenied("Only the HOD can confirm mission limits")
    if mission.status not in PRE_CONFIRM_STATUSES:
        raise Conflict(f"Mission is already {mission.status}")
    _check_complete(mission)
    _confirm(db, actor, mission)
    return mission


def update_mission(db: Session, actor: Actor, mission: Mission, changes: dict[str, Any]) -> UpdateResult:
    """Applies non-limit edits directly. Limit edits on an active mission become a
    Tier 3 change_mission_limits approval and nothing changes until the HOD approves."""
    if mission.status in CLOSED_STATUSES:
        raise Conflict(f"Mission is {mission.status}")
    unknown = set(changes) - set(LIMIT_FIELDS) - set(OPEN_FIELDS)
    if unknown:
        raise InvalidInput(f"Unknown fields: {', '.join(sorted(unknown))}")
    if actor.is_agent:
        not_allowed = set(changes) - set(AGENT_FIELDS) - set(LIMIT_FIELDS)
        if not_allowed:
            raise PermissionDenied(f"The agent cannot change {', '.join(sorted(not_allowed))}. Suggest it in notes")
    else:
        _require_member(actor)

    values = {k: _coerce(k, v) for k, v in changes.items()}
    if "goal_text" in values and not (values["goal_text"] or "").strip():
        raise InvalidInput("Goal cannot be empty")
    # Ignore fields that would not change anything.
    values = {k: v for k, v in values.items() if json_value(getattr(mission, k)) != json_value(v)}
    direct = {k: v for k, v in values.items() if k in OPEN_FIELDS}
    limit_changes = {k: v for k, v in values.items() if k in LIMIT_FIELDS}

    approval = None
    if limit_changes and mission.status == MissionStatus.ACTIVE.value:
        _validate({**_state(mission), **direct, **limit_changes})
        snapshot = {
            "mission_id": str(mission.id),
            "changes": {k: json_value(v) for k, v in limit_changes.items()},
            "previous": {k: json_value(getattr(mission, k)) for k in limit_changes},
        }
        approval = approval_service.request(db, actor, mission, "change_mission_limits", snapshot)
    elif limit_changes:
        if actor.is_agent:
            raise PermissionDenied("Before HOD confirmation only a person can change the proposed limits")
        direct.update(limit_changes)

    _validate({**_state(mission), **direct})
    for field, value in direct.items():
        setattr(mission, field, value)
    db.flush()
    audit_service.record(
        db,
        actor,
        "mission.updated",
        mission_id=mission.id,
        input_ref={"fields": sorted(values)},
        result_ref={
            "updated_fields": sorted(direct),
            "limit_change_approval_id": approval.id if approval else None,
        },
    )
    return UpdateResult(mission=mission, updated_fields=sorted(direct), approval=approval)


def apply_limit_changes(db: Session, actor: Actor, mission: Mission, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Runs an approved change_mission_limits snapshot."""
    if mission.status != MissionStatus.ACTIVE.value:
        raise Conflict(f"Mission is {mission.status}")
    changes: dict[str, Any] = snapshot.get("changes") or {}
    previous: dict[str, Any] = snapshot.get("previous") or {}
    if not changes or set(changes) - set(LIMIT_FIELDS):
        raise InvalidInput("Invalid limit change")
    for field, old in previous.items():
        if json_value(getattr(mission, field)) != old:
            raise Conflict(f"{field} changed after this request was made")
    values = {k: _coerce(k, v) for k, v in changes.items()}
    _validate({**_state(mission), **values})
    for field, value in values.items():
        setattr(mission, field, value)
    db.flush()
    audit_service.record(
        db,
        actor,
        "mission.limits_changed",
        mission_id=mission.id,
        input_ref={"previous": previous},
        result_ref={"changes": changes},
    )
    return {"mission_id": str(mission.id), "changed": changes}
