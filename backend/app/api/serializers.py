"""Turns ORM rows into response schemas."""

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.models import Approval, Mission, User
from app.models.enums import ApprovalStatus
from app.schemas.approvals import ApprovalDetail, ApprovalSummary, BudgetComparison
from app.schemas.missions import MissionOut
from app.services import approval_service
from app.services.errors import PermissionDenied


def user_emails(db: Session, ids: Iterable[uuid.UUID | None]) -> dict[uuid.UUID, str]:
    wanted = {i for i in ids if i is not None}
    if not wanted:
        return {}
    return {u.id: u.email for u in db.scalars(select(User).where(User.id.in_(wanted)))}


def actor_label(actor_ref: str, emails: dict[uuid.UUID, str]) -> str:
    kind, _, ident = actor_ref.partition(":")
    if kind == "user":
        try:
            return emails.get(uuid.UUID(ident), actor_ref)
        except ValueError:
            return actor_ref
    if kind == "agent":
        return f"Agent ({ident})"
    return actor_ref


def mission_out(mission: Mission, emails: dict[uuid.UUID, str]) -> MissionOut:
    out = MissionOut.model_validate(mission)
    out.owner_email = emails.get(mission.owner_id)
    return out


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _preview(approval: Approval) -> str | None:
    snapshot = approval.content_snapshot or {}
    body = snapshot.get("body")
    if isinstance(body, str):
        return body if len(body) <= 160 else body[:160] + "..."
    changes = snapshot.get("changes")
    if isinstance(changes, dict):
        return ", ".join(f"{k}: {snapshot.get('previous', {}).get(k)} -> {v}" for k, v in changes.items())
    return None


def requester_label(approval: Approval, emails: dict[uuid.UUID, str]) -> str:
    if approval.requested_by.startswith("agent:"):
        person = emails.get(approval.requested_on_behalf_of) if approval.requested_on_behalf_of else None
        return f"Agent for {person}" if person else "Agent"
    return actor_label(approval.requested_by, emails)


def approval_emails(db: Session, approvals: Iterable[Approval]) -> dict[uuid.UUID, str]:
    ids: set[uuid.UUID | None] = set()
    for a in approvals:
        ids.update({a.requested_on_behalf_of, a.approver_id, approval_service.user_id_from_ref(a.requested_by)})
    return user_emails(db, ids)


def approval_summary(approval: Approval, mission_code: str | None, emails: dict[uuid.UUID, str]) -> ApprovalSummary:
    snapshot = approval.content_snapshot or {}
    return ApprovalSummary(
        id=approval.id,
        mission_id=approval.mission_id,
        mission_code=mission_code,
        action_type=approval.action_type,
        tier=approval.tier,
        status=approval.status,
        requested_by=approval.requested_by,
        requester_label=requester_label(approval, emails),
        eligible_roles=list(approval.eligible_roles or []),
        expires_at=approval.expires_at,
        created_at=approval.created_at,
        decided_at=approval.decided_at,
        approver_role=approval.approver_role,
        recipient_name=snapshot.get("recipient_name"),
        kind=snapshot.get("kind"),
        proposed_total_myr=_decimal(snapshot.get("proposed_total_myr")),
        preview=_preview(approval),
    )


def approval_detail(db: Session, approval: Approval, viewer: Actor) -> ApprovalDetail:
    mission = db.get(Mission, approval.mission_id) if approval.mission_id else None
    emails = approval_emails(db, [approval])
    summary = approval_summary(approval, mission.code if mission else None, emails)

    proposed = summary.proposed_total_myr
    budget = mission.hard_budget_myr if mission else None
    target = mission.target_total_myr if mission else None
    comparison = BudgetComparison(
        hard_budget_myr=budget,
        hard_budget_at_request=approval.hard_budget_at_request,
        target_total_myr=target,
        proposed_total_myr=proposed,
        within_budget=(proposed <= budget) if (proposed is not None and budget is not None) else None,
        difference_from_target_myr=(proposed - target) if (proposed is not None and target is not None) else None,
    )

    can_decide, reason = False, None
    if approval.status != ApprovalStatus.PENDING.value:
        reason = f"Already {approval.status}"
    elif approval.expires_at <= datetime.now(UTC):
        reason = "Expired"
    else:
        try:
            approval_service.approver_role_for(viewer, approval)
            can_decide = True
        except PermissionDenied as exc:
            reason = exc.message

    return ApprovalDetail(
        **summary.model_dump(),
        content_snapshot=approval.content_snapshot,
        content_hash=approval.content_hash,
        decision_reason=approval.decision_reason,
        approver_email=emails.get(approval.approver_id) if approval.approver_id else None,
        used_at=approval.used_at,
        execution_result=approval.execution_result,
        budget=comparison,
        can_decide=can_decide,
        cannot_decide_reason=reason,
    )
