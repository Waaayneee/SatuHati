"""Risk tiers, approval requests, decisions and single-use tokens (blueprint Section 22).

The backend is the only enforcer. Rules that never bend:
- Unknown action types are Tier 3.
- A Tier 1 snapshot that states a price, budget, payment term or quantity tier is
  bumped to `send_terms_message` (Tier 2).
- Agents can never decide. Tier 1 needs a committee member who did not request the
  action, or the HOD. Tier 2 and Tier 3 always need the HOD.
- Any proposed total above the mission hard budget is refused, at request time and
  again at execution time. Opted-out stakeholders are refused at both points too.
- A token is single use, expires, and only runs the exact snapshot that was approved.
"""

import hashlib
import json
import re
import secrets
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.actor import SYSTEM, Actor
from app.config import settings
from app.models import Approval, ApprovalPolicy, Message, Mission, Stakeholder
from app.models.enums import ApprovalStatus, MessageStatus, MissionStatus, Role
from app.services import audit_service
from app.services.errors import Conflict, DomainError, InvalidInput, NotFound, PermissionDenied, Refused

UNKNOWN_TIER = 3
TERMS_ACTION = "send_terms_message"
HOD_ONLY = [Role.HOD.value]
TIER1_DEFAULT_ROLES = [Role.COMMITTEE_MEMBER.value, Role.HOD.value]

# Snapshot keys that carry commercial terms when they have a value.
_COMMERCIAL_KEYS = {
    "proposed_total_myr",
    "price",
    "unit_price",
    "total_price",
    "budget",
    "budget_myr",
    "hard_budget_myr",
    "target_total_myr",
    "quantity_tier",
    "quantity_tiers",
    "payment_term",
    "payment_terms",
    "discount",
}
# Free-text keys that are scanned for prices and terms.
_TEXT_KEYS = {"body", "subject"}
_CURRENCY = re.compile(
    r"\b(?:RM|MYR|USD|SGD)\s?\d|\$\s?\d|\d[\d,]*(?:\.\d+)?\s?(?:RM|MYR|ringgit|USD|dollars?)\b",
    re.IGNORECASE,
)
_TERMS = re.compile(
    r"\b(?:budget|payment\s+terms?|deposit|down\s?payment|net\s?\d{1,3}|cash\s+on\s+delivery|"
    r"instal(?:l)?ments?|upfront\s+payment|quantity\s+tiers?|price\s+breaks?|bulk\s+(?:rate|discount|pricing)|"
    r"discounts?|target\s+price|willing\s+to\s+pay|we\s+can\s+pay)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Classification:
    action_type: str  # effective action type, after any safety bump
    requested_action_type: str
    tier: int
    eligible_roles: list[str]
    is_external: bool
    ttl_hours: int
    known: bool
    bumped: bool


# ---------------------------------------------------------------------------
# Hashing and helpers
# ---------------------------------------------------------------------------


def _json_default(value: Any) -> str:
    if isinstance(value, (uuid.UUID, Decimal)):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(getattr(value, "value", value))


def canonical_json(snapshot: Any) -> str:
    """Sorted keys, no spaces. Decimals and UUIDs become strings."""
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_json_default)


def normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """The exact JSON form that is stored and hashed."""
    return json.loads(canonical_json(snapshot))


def content_hash(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(snapshot).encode("utf-8")).hexdigest()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


def _walk(value: Any, key: str | None = None):
    yield key, value
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _walk(v, str(k))
    elif isinstance(value, list):
        for v in value:
            yield from _walk(v, key)


def _has_value(value: Any) -> bool:
    return value not in (None, "", [], {})


def mentions_commercial_terms(snapshot: dict[str, Any] | None) -> bool:
    """True if the snapshot states a price, budget, payment term, quantity tier or currency amount."""
    if not snapshot:
        return False
    for key, value in _walk(snapshot):
        if key in _COMMERCIAL_KEYS and _has_value(value):
            return True
        if key in _TEXT_KEYS and isinstance(value, str) and (_CURRENCY.search(value) or _TERMS.search(value)):
            return True
    return False


def _eligible_for_tier(tier: int, policy_roles: list[str] | None) -> list[str]:
    if tier >= 2:
        return list(HOD_ONLY)  # Tier 2 and 3 always stay with the HOD
    if tier == 1:
        roles = [r for r in (policy_roles or []) if r in TIER1_DEFAULT_ROLES]
        return roles or list(HOD_ONLY)
    return list(policy_roles or ["any"])


def _get_policy(db: Session, action_type: str) -> ApprovalPolicy | None:
    return db.scalars(select(ApprovalPolicy).where(ApprovalPolicy.action_type == action_type)).one_or_none()


def _user_id_from_ref(ref: str | None) -> uuid.UUID | None:
    if ref and ref.startswith("user:"):
        try:
            return uuid.UUID(ref.removeprefix("user:"))
        except ValueError:
            return None
    return None


def requester_user_ids(approval: Approval) -> set[uuid.UUID]:
    ids = {approval.requested_on_behalf_of, _user_id_from_ref(approval.requested_by)}
    return {i for i in ids if i is not None}


def _decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise InvalidInput(f"{field} must be a number") from None
    if not result.is_finite():
        raise InvalidInput(f"{field} must be a finite number")
    return result


# ---------------------------------------------------------------------------
# Classification and permission
# ---------------------------------------------------------------------------


def classify(db: Session, action_type: str, snapshot: dict[str, Any] | None = None) -> Classification:
    policy = _get_policy(db, action_type)
    if policy is None:
        return Classification(
            action_type=action_type,
            requested_action_type=action_type,
            tier=UNKNOWN_TIER,
            eligible_roles=list(HOD_ONLY),
            is_external=True,
            ttl_hours=settings.approval_ttl_hours,
            known=False,
            bumped=False,
        )

    result = Classification(
        action_type=action_type,
        requested_action_type=action_type,
        tier=policy.tier,
        eligible_roles=_eligible_for_tier(policy.tier, policy.eligible_roles),
        is_external=policy.is_external,
        ttl_hours=policy.ttl_hours or settings.approval_ttl_hours,
        known=True,
        bumped=False,
    )
    if result.tier == 1 and mentions_commercial_terms(snapshot):
        terms_policy = _get_policy(db, TERMS_ACTION)
        tier = max(2, terms_policy.tier) if terms_policy else UNKNOWN_TIER
        result = replace(
            result,
            action_type=TERMS_ACTION,
            tier=tier,
            eligible_roles=list(HOD_ONLY),
            is_external=True,
            ttl_hours=(terms_policy.ttl_hours if terms_policy else None) or settings.approval_ttl_hours,
            bumped=True,
        )
    return result


def check_permission(
    db: Session, actor: Actor, action_type: str, mission: Mission | None, snapshot: dict[str, Any] | None = None
) -> dict[str, Any]:
    c = classify(db, action_type, snapshot)
    may_act = actor.is_agent or (actor.is_user and bool(actor.roles))
    mission_closed = mission is not None and mission.status in (
        MissionStatus.COMPLETED.value,
        MissionStatus.CANCELLED.value,
    )
    return {
        "action_type": c.action_type,
        "requested_action_type": c.requested_action_type,
        "tier": c.tier,
        "allowed_to_run_now": c.tier == 0 and may_act and not mission_closed,
        "needs_approval": c.tier > 0,
        "eligible_roles": c.eligible_roles,
        "is_external": c.is_external,
        "known_action_type": c.known,
    }


# ---------------------------------------------------------------------------
# Safety checks shared by request time and execution time
# ---------------------------------------------------------------------------


def _check_hard_budget(mission: Mission, snapshot: dict[str, Any]) -> None:
    proposed = [v for k, v in _walk(snapshot) if k == "proposed_total_myr" and v is not None]
    if not proposed:
        return
    if mission.hard_budget_myr is None:
        raise Refused("The mission has no confirmed hard budget")
    for value in proposed:
        amount = _decimal(value, "proposed_total_myr")
        if amount <= 0:
            raise InvalidInput("proposed_total_myr must be positive")
        if amount > mission.hard_budget_myr:
            raise Refused(
                f"Proposed total RM{amount:,.2f} is above the hard budget RM{mission.hard_budget_myr:,.2f}",
                rule="hard_budget",
            )


def _check_opt_out(db: Session, snapshot: dict[str, Any]) -> None:
    stakeholder_id = snapshot.get("stakeholder_id")
    if stakeholder_id is None:
        return
    try:
        stakeholder = db.get(Stakeholder, uuid.UUID(str(stakeholder_id)))
    except ValueError:
        raise InvalidInput("stakeholder_id is not a valid ID") from None
    if stakeholder is None:
        raise InvalidInput("Unknown stakeholder")
    if stakeholder.opted_out:
        raise Refused(f"{stakeholder.name} has opted out of contact", rule="opted_out")


def refuse_linked_messages(db: Session, approval: Approval) -> None:
    db.execute(
        update(Message)
        .where(Message.approval_id == approval.id, Message.status == MessageStatus.PENDING_APPROVAL.value)
        .values(status=MessageStatus.REFUSED.value)
    )


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------


def request(
    db: Session,
    actor: Actor,
    mission: Mission | None,
    action_type: str,
    snapshot: dict[str, Any],
    minimum_tier: int | None = None,
) -> Approval:
    """Creates a pending approval. Raises Refused/InvalidInput without writing anything,
    so callers record the refusal after rolling back (see audit_service.audited_refusals)."""
    if mission is None:
        raise InvalidInput("Approvals must belong to a mission")
    if not isinstance(snapshot, dict):
        raise InvalidInput("snapshot must be an object")
    if actor.is_user and not actor.roles:
        raise PermissionDenied("Your account has no KawTeam role")

    c = classify(db, action_type, snapshot)
    if c.tier == 0:
        if minimum_tier is None:
            raise InvalidInput(f"{action_type} is Tier 0 and runs without approval")
        # Default deny: an external tool never runs ungated, even if a policy says Tier 0.
        c = replace(c, tier=minimum_tier, eligible_roles=_eligible_for_tier(minimum_tier, TIER1_DEFAULT_ROLES))

    if c.is_external and mission.status != MissionStatus.ACTIVE.value:
        raise Refused("The HOD must confirm this mission's limits before any external action", rule="mission_not_active")
    _check_hard_budget(mission, snapshot)
    _check_opt_out(db, snapshot)

    stored = normalize_snapshot(snapshot)
    approval = Approval(
        mission_id=mission.id,
        action_type=c.action_type,
        tier=c.tier,
        requested_by=actor.ref,
        requested_on_behalf_of=actor.user_id or actor.on_behalf_of,
        eligible_roles=c.eligible_roles,
        status=ApprovalStatus.PENDING.value,
        content_snapshot=stored,
        content_hash=content_hash(stored),
        expires_at=_now() + timedelta(hours=c.ttl_hours),
        hard_budget_at_request=mission.hard_budget_myr,
    )
    db.add(approval)
    db.flush()
    audit_service.record(
        db,
        actor,
        "approval.requested",
        mission_id=mission.id,
        input_ref={"action_type": c.action_type, "requested_action_type": action_type, "snapshot": stored},
        result_ref={
            "approval_id": approval.id,
            "tier": c.tier,
            "eligible_roles": c.eligible_roles,
            "bumped_to_tier_2": c.bumped,
            "expires_at": approval.expires_at,
        },
    )
    return approval


# ---------------------------------------------------------------------------
# Decide
# ---------------------------------------------------------------------------


def _lock(db: Session, approval_id: uuid.UUID) -> Approval:
    approval = db.scalars(select(Approval).where(Approval.id == approval_id).with_for_update()).one_or_none()
    if approval is None:
        raise NotFound("Approval not found")
    return approval


def _expire(db: Session, approval: Approval, actor: Actor = SYSTEM) -> None:
    approval.status = ApprovalStatus.EXPIRED.value
    refuse_linked_messages(db, approval)
    audit_service.record(
        db,
        actor,
        "approval.expired",
        mission_id=approval.mission_id,
        result_ref={"approval_id": approval.id, "expired_at": approval.expires_at},
        status="expired",
    )


def expire_stale(db: Session) -> int:
    """Marks every pending approval past its expiry as expired. Caller commits."""
    stale = db.scalars(
        select(Approval)
        .where(Approval.status == ApprovalStatus.PENDING.value, Approval.expires_at <= _now())
        .with_for_update(skip_locked=True)
    ).all()
    for approval in stale:
        _expire(db, approval)
    return len(stale)


def approver_role_for(actor: Actor, approval: Approval) -> str:
    """The role the actor would approve with. Raises PermissionDenied if not allowed."""
    if not actor.is_user:
        raise PermissionDenied("Agents can never approve anything")
    if approval.tier >= 2:
        if actor.is_hod:
            return Role.HOD.value
        raise PermissionDenied(f"Only the HOD can approve Tier {approval.tier} actions")
    if actor.is_hod:
        return Role.HOD.value
    if actor.is_committee_member and Role.COMMITTEE_MEMBER.value in approval.eligible_roles:
        if actor.user_id in requester_user_ids(approval):
            raise PermissionDenied("You requested this action. Another committee member or the HOD must approve it")
        return Role.COMMITTEE_MEMBER.value
    raise PermissionDenied("Your role cannot approve this action")


def decide(db: Session, actor: Actor, approval_id: uuid.UUID, decision: str, reason: str) -> Approval:
    """Approve or reject exactly one approval. On approval the backend issues a
    single-use token and immediately executes the stored snapshot. Commits."""
    if decision not in (ApprovalStatus.APPROVED.value, ApprovalStatus.REJECTED.value):
        raise InvalidInput("decision must be 'approved' or 'rejected'")
    reason = (reason or "").strip()
    if not reason:
        raise InvalidInput("A reason is required")

    approval = _lock(db, approval_id)
    try:
        if approval.status != ApprovalStatus.PENDING.value:
            raise Conflict(f"This approval is already {approval.status}")
        if _now() >= approval.expires_at:
            _expire(db, approval)
            db.commit()
            raise Conflict("This approval has expired")
        role = approver_role_for(actor, approval)
    except (PermissionDenied, Conflict) as exc:
        audit_service.record(
            db,
            actor,
            "approval.decision_refused",
            mission_id=approval.mission_id,
            input_ref={"approval_id": approval.id, "decision": decision, "tier": approval.tier},
            status="refused",
            error=exc.message,
        )
        db.commit()
        raise

    approval.approver_id = actor.user_id
    approval.approver_role = role
    approval.decision_reason = reason
    approval.decided_at = _now()

    if decision == ApprovalStatus.REJECTED.value:
        approval.status = ApprovalStatus.REJECTED.value
        refuse_linked_messages(db, approval)
        audit_service.record(
            db,
            actor,
            "approval.rejected",
            mission_id=approval.mission_id,
            input_ref={"approval_id": approval.id, "tier": approval.tier, "reason": reason},
        )
        db.commit()
        return approval

    token = secrets.token_urlsafe(32)
    approval.status = ApprovalStatus.APPROVED.value
    approval.token_hash = _token_hash(token)
    audit_service.record(
        db,
        actor,
        "approval.approved",
        mission_id=approval.mission_id,
        input_ref={"approval_id": approval.id, "tier": approval.tier, "reason": reason},
    )
    db.flush()

    from app.tools import executor  # local import: the executor also imports this module

    try:
        executor.run_approved(db, approval.id, token, actor)
    except DomainError:
        pass  # run_approved already marked the approval failed, audited and committed
    db.refresh(approval)
    return approval


# ---------------------------------------------------------------------------
# Verify and consume
# ---------------------------------------------------------------------------


def _mark_failed(db: Session, approval: Approval, reason: str, actor: Actor) -> None:
    approval.status = ApprovalStatus.FAILED.value
    approval.execution_result = {"error": reason}
    refuse_linked_messages(db, approval)
    audit_service.record(
        db,
        actor,
        "approval.execution_refused",
        mission_id=approval.mission_id,
        input_ref={"approval_id": approval.id, "action_type": approval.action_type},
        status="refused",
        error=reason,
    )


def verify_and_consume(
    db: Session, approval_id: uuid.UUID, token: str, snapshot: dict[str, Any], actor: Actor = SYSTEM
) -> Approval:
    """Checks everything again right before execution and burns the token.
    Any failure marks the approval failed, audits, commits and raises Refused."""
    approval = _lock(db, approval_id)

    if approval.status != ApprovalStatus.APPROVED.value or approval.used_at is not None:
        # Already executed, failed or never approved: refuse without touching its status.
        audit_service.record(
            db,
            actor,
            "approval.token_rejected",
            mission_id=approval.mission_id,
            input_ref={"approval_id": approval.id},
            status="refused",
            error=f"Approval is {approval.status}; tokens are single use",
        )
        db.commit()
        raise Refused("This approval token is not valid (already used or not approved)")

    failure: str | None = None
    if _now() >= approval.expires_at:
        failure = "Approval expired before execution"
    elif not approval.token_hash or not secrets.compare_digest(_token_hash(token), approval.token_hash):
        failure = "Approval token does not match"
    elif not secrets.compare_digest(content_hash(normalize_snapshot(snapshot)), approval.content_hash):
        failure = "Content changed after it was submitted for approval"
    else:
        mission = db.get(Mission, approval.mission_id) if approval.mission_id else None
        try:
            if mission is None:
                raise Refused("Mission not found")
            _check_hard_budget(mission, snapshot)
            _check_opt_out(db, snapshot)
        except DomainError as exc:
            failure = exc.message

    if failure:
        _mark_failed(db, approval, failure, actor)
        db.commit()
        raise Refused(f"Execution refused: {failure}")

    approval.used_at = _now()
    approval.status = ApprovalStatus.EXECUTED.value
    db.flush()
    return approval
