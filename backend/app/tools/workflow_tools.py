"""Common workflow tools. Plain functions: no Claude, FastAPI or WorkBuddy imports."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select

from app.models import Approval, EvidenceSource, Message, Negotiation, Quotation, Stakeholder
from app.models.enums import ApprovalStatus, MessageDirection, MessageKind, MessageStatus, NegotiationStatus
from app.services import approval_service, audit_service, mission_service
from app.services.errors import InvalidInput, NotFound, Refused
from app.tools.context import ToolContext
from app.tools.registry import PreparedAction, approved_action, tool

ACTION_FOR_KIND = {
    MessageKind.ENQUIRY.value: "send_enquiry",
    MessageKind.CLARIFICATION.value: "send_clarification",
    MessageKind.FOLLOW_UP.value: "send_follow_up",
    MessageKind.COUNTEROFFER.value: "send_counteroffer",
    MessageKind.TERMS.value: "send_terms_message",
}
SEND_ACTIONS = (*ACTION_FOR_KIND.values(),)
# Action types that must go through their own tool, not request_approval.
DEDICATED_TOOL = {
    **{action: "send_approved_message" for action in SEND_ACTIONS},
    "change_mission_limits": "update_mission_state",
    "confirm_mission_limits": "the HOD's Confirm limits button (people only)",
}
ACTION_TYPE_PATTERN = r"^[a-z][a-z0-9_]{2,63}$"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _money(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _preview(text: str, limit: int = 300) -> str:
    return text if len(text) <= limit else text[:limit] + "..."


# ---------------------------------------------------------------------------
# read_mission_state
# ---------------------------------------------------------------------------


class ReadMissionStateIn(StrictModel):
    pass


class ReadMissionStateOut(BaseModel):
    mission: dict[str, Any]
    quotations: list[dict[str, Any]]
    pending_approvals: list[dict[str, Any]]
    recent_messages: list[dict[str, Any]]


@tool(
    name="read_mission_state",
    description=(
        "Read the current mission: goal, product, quantity, target price, hard budget, minimum quality, "
        "deadline, max negotiation rounds, status, known quotations, pending approvals and recent messages. "
        "Call this first in every run, and again whenever you need fresh state."
    ),
    action_type="read_mission_state",
    input_model=ReadMissionStateIn,
    output_model=ReadMissionStateOut,
)
def read_mission_state(ctx: ToolContext, args: ReadMissionStateIn) -> ReadMissionStateOut:
    db, mission = ctx.db, ctx.mission
    quotations = db.execute(
        select(Quotation, Stakeholder, EvidenceSource)
        .join(Stakeholder, Stakeholder.id == Quotation.stakeholder_id)
        .outerjoin(EvidenceSource, EvidenceSource.id == Quotation.source_id)
        .where(Quotation.mission_id == mission.id)
        .order_by(Quotation.total_price)
    ).all()
    pending = db.scalars(
        select(Approval)
        .where(Approval.mission_id == mission.id, Approval.status == ApprovalStatus.PENDING.value)
        .order_by(Approval.created_at)
    ).all()
    messages = db.execute(
        select(Message, Stakeholder)
        .outerjoin(Stakeholder, Stakeholder.id == Message.stakeholder_id)
        .where(Message.mission_id == mission.id)
        .order_by(Message.created_at.desc())
        .limit(10)
    ).all()
    return ReadMissionStateOut(
        mission=mission_service.mission_to_dict(mission),
        quotations=[
            {
                "stakeholder_id": str(s.id),
                "supplier": s.name,
                "total_price_myr": _money(q.total_price),
                "unit_price_myr": _money(q.unit_price),
                "verification_state": q.verification_state.value,
                "simulated": bool(e.is_simulated) if e else False,
                "opted_out": s.opted_out,
            }
            for q, s, e in quotations
        ],
        pending_approvals=[
            {
                "approval_id": str(a.id),
                "action_type": a.action_type,
                "tier": a.tier,
                "expires_at": a.expires_at.isoformat(),
            }
            for a in pending
        ],
        recent_messages=[
            {
                "message_id": str(m.id),
                "supplier": s.name if s else None,
                "kind": m.kind,
                "status": m.status,
                "is_simulated": m.is_simulated,
                "proposed_total_myr": _money(m.proposed_total_myr),
                "body_preview": _preview(m.body),
                "created_at": m.created_at.isoformat(),
            }
            for m, s in messages
        ],
    )


# ---------------------------------------------------------------------------
# update_mission_state
# ---------------------------------------------------------------------------


class UpdateMissionStateIn(StrictModel):
    notes: str | None = Field(None, max_length=4000, description="Internal notes to save on the mission.")
    hard_budget_myr: float | None = Field(None, gt=0, description="Limit change. Needs HOD approval.")
    minimum_quality: float | None = Field(None, ge=0, le=5, description="Limit change. Needs HOD approval.")
    delivery_deadline: str | None = Field(None, description="Limit change (YYYY-MM-DD). Needs HOD approval.")
    max_rounds: int | None = Field(None, ge=1, le=10, description="Limit change. Needs HOD approval.")
    quantity: int | None = Field(None, gt=0, description="Limit change. Needs HOD approval.")
    product: str | None = Field(None, max_length=200, description="Limit change. Needs HOD approval.")


class UpdateMissionStateOut(BaseModel):
    updated_fields: list[str]
    approval_required: bool = False
    approval_id: str | None = None
    approval_tier: int | None = None
    approval_action_type: str | None = None
    note: str


@tool(
    name="update_mission_state",
    description=(
        "Save internal notes on the mission (for example research findings or a suggested target price). "
        "You may also propose a change to a mission limit (hard budget, minimum quality, deadline, max rounds, "
        "quantity, product). Limit changes are never applied directly: they create a Tier 3 approval for the HOD."
    ),
    action_type="update_mission_state",
    input_model=UpdateMissionStateIn,
    output_model=UpdateMissionStateOut,
)
def update_mission_state(ctx: ToolContext, args: UpdateMissionStateIn) -> UpdateMissionStateOut:
    changes = args.model_dump(exclude_none=True)
    if not changes:
        raise InvalidInput("Nothing to update")
    result = mission_service.update_mission(ctx.db, ctx.actor, ctx.mission, changes)
    approval = result.approval
    if approval is not None:
        note = "Limit changes are waiting for HOD approval. Nothing changed yet."
    elif result.updated_fields:
        note = "Saved."
    else:
        note = "No changes were needed."
    return UpdateMissionStateOut(
        updated_fields=result.updated_fields,
        approval_required=approval is not None,
        approval_id=str(approval.id) if approval else None,
        approval_tier=approval.tier if approval else None,
        approval_action_type=approval.action_type if approval else None,
        note=note,
    )


# ---------------------------------------------------------------------------
# check_permission
# ---------------------------------------------------------------------------


class CheckPermissionIn(StrictModel):
    action_type: str = Field(pattern=ACTION_TYPE_PATTERN, description="For example send_enquiry or send_counteroffer.")
    snapshot: dict[str, Any] | None = Field(
        None, description="Optional draft content (for example a message body) to classify more precisely."
    )


class CheckPermissionOut(BaseModel):
    action_type: str
    requested_action_type: str
    tier: int
    allowed_to_run_now: bool
    needs_approval: bool
    eligible_roles: list[str]
    is_external: bool
    known_action_type: bool


@tool(
    name="check_permission",
    description=(
        "Check the risk tier of an action and whether it can run now or needs a human approval. "
        "Use it when you are unsure how an action will be treated. It never performs the action."
    ),
    action_type=None,
    input_model=CheckPermissionIn,
    output_model=CheckPermissionOut,
)
def check_permission(ctx: ToolContext, args: CheckPermissionIn) -> CheckPermissionOut:
    return CheckPermissionOut(
        **approval_service.check_permission(ctx.db, ctx.actor, args.action_type, ctx.mission, args.snapshot)
    )


# ---------------------------------------------------------------------------
# request_approval
# ---------------------------------------------------------------------------


class RequestApprovalIn(StrictModel):
    action_type: str = Field(pattern=ACTION_TYPE_PATTERN, description="The action that needs approval.")
    snapshot: dict[str, Any] = Field(description="Exactly what would happen if approved.")


class ApprovalRequiredOut(BaseModel):
    approval_id: str
    tier: int
    action_type: str
    eligible_roles: list[str]
    expires_at: str


def _request_approval(ctx: ToolContext, args: RequestApprovalIn) -> PreparedAction:
    if args.action_type in DEDICATED_TOOL:
        raise InvalidInput(f"Use {DEDICATED_TOOL[args.action_type]} for {args.action_type}")
    return PreparedAction(action_type=args.action_type, snapshot=args.snapshot)


tool(
    name="request_approval",
    description=(
        "Ask a human to approve an action that has no dedicated tool. Returns approval_required with an "
        "approval ID. Do not use it for messages (use send_approved_message) or mission limits "
        "(use update_mission_state). Unknown action types are Tier 3 and need the HOD."
    ),
    action_type="caller_supplied",
    input_model=RequestApprovalIn,
    output_model=ApprovalRequiredOut,
    gated=True,
)(_request_approval)


# ---------------------------------------------------------------------------
# get_approval_status
# ---------------------------------------------------------------------------


class GetApprovalStatusIn(StrictModel):
    approval_id: uuid.UUID


class GetApprovalStatusOut(BaseModel):
    approval_id: str
    action_type: str
    tier: int
    status: str
    is_expired: bool
    decision: Literal["approved", "rejected"] | None
    decision_reason: str | None
    approver_role: str | None
    decided_at: str | None
    expires_at: str
    execution_result: dict[str, Any] | None


@tool(
    name="get_approval_status",
    description=(
        "Read the status of an approval you requested on this mission: pending, approved, rejected, expired, "
        "executed or failed, with the reason and the execution result. Use it instead of guessing."
    ),
    action_type=None,
    input_model=GetApprovalStatusIn,
    output_model=GetApprovalStatusOut,
)
def get_approval_status(ctx: ToolContext, args: GetApprovalStatusIn) -> GetApprovalStatusOut:
    approval = ctx.db.get(Approval, args.approval_id)
    if approval is None or approval.mission_id != ctx.mission.id:
        raise NotFound("No such approval on this mission")
    decided = approval.approver_id is not None and approval.decided_at is not None
    decision: Literal["approved", "rejected"] | None = None
    if decided:
        decision = "rejected" if approval.status == ApprovalStatus.REJECTED.value else "approved"
    return GetApprovalStatusOut(
        approval_id=str(approval.id),
        action_type=approval.action_type,
        tier=approval.tier,
        status=approval.status,
        is_expired=approval.status == ApprovalStatus.EXPIRED.value
        or (approval.status == ApprovalStatus.PENDING.value and approval.expires_at <= datetime.now(UTC)),
        decision=decision,
        decision_reason=approval.decision_reason,
        approver_role=approval.approver_role,
        decided_at=approval.decided_at.isoformat() if approval.decided_at else None,
        expires_at=approval.expires_at.isoformat(),
        execution_result=approval.execution_result,
    )


# ---------------------------------------------------------------------------
# send_approved_message
# ---------------------------------------------------------------------------


class SendApprovedMessageIn(StrictModel):
    stakeholder_id: uuid.UUID = Field(description="Recipient, from search_suppliers or read_mission_state.")
    kind: Literal["enquiry", "clarification", "follow_up", "counteroffer", "terms"] = Field(
        description=(
            "enquiry: first quotation request with no price, budget or terms (Tier 1). "
            "clarification / follow_up: no new commercial content (Tier 1). "
            "counteroffer / terms: any price, budget, payment or delivery terms (Tier 2, HOD)."
        )
    )
    body: str = Field(min_length=1, max_length=5000, description="The full message text the supplier would receive.")
    proposed_total_myr: float | None = Field(
        None, gt=0, description="Required for counteroffer and terms. Must not exceed the hard budget."
    )


@tool(
    name="send_approved_message",
    description=(
        "Submit a message to a supplier for human approval. It is never sent directly: it returns "
        "approval_required and the message is sent (simulated, no real email) only after the right person approves. "
        "Enquiries are Tier 1 (another committee member or the HOD). Counteroffers, terms, or any message that "
        "states a price, budget or payment term are Tier 2 (HOD only)."
    ),
    action_type="send_<kind>",
    input_model=SendApprovedMessageIn,
    output_model=ApprovalRequiredOut,
    gated=True,
    minimum_tier=1,
)
def send_approved_message(ctx: ToolContext, args: SendApprovedMessageIn) -> PreparedAction:
    db, mission = ctx.db, ctx.mission
    stakeholder = db.get(Stakeholder, args.stakeholder_id)
    if stakeholder is None:
        raise InvalidInput("Unknown stakeholder. Use a stakeholder_id from search_suppliers")
    proposed = Decimal(str(args.proposed_total_myr)) if args.proposed_total_myr is not None else None
    if args.kind in (MessageKind.COUNTEROFFER.value, MessageKind.TERMS.value) and proposed is None:
        raise InvalidInput("Counteroffers and terms messages must include proposed_total_myr")
    if args.kind == MessageKind.COUNTEROFFER.value:
        rounds = db.scalar(
            select(func.count())
            .select_from(Negotiation)
            .where(Negotiation.mission_id == mission.id, Negotiation.stakeholder_id == stakeholder.id)
        )
        if rounds >= mission.max_rounds:
            raise Refused(
                f"All {mission.max_rounds} negotiation rounds with {stakeholder.name} are used", rule="max_rounds"
            )

    message = Message(
        mission_id=mission.id,
        stakeholder_id=stakeholder.id,
        direction=MessageDirection.OUTBOUND.value,
        kind=args.kind,
        channel=stakeholder.contact_channel or "email",
        body=args.body,
        proposed_total_myr=proposed,
        status=MessageStatus.PENDING_APPROVAL.value,
        is_simulated=True,
    )
    db.add(message)
    db.flush()
    snapshot = {
        "message_id": str(message.id),
        "mission_id": str(mission.id),
        "stakeholder_id": str(stakeholder.id),
        "recipient_name": stakeholder.name,
        "recipient": stakeholder.contact_value,
        "channel": message.channel,
        "kind": args.kind,
        "body": args.body,
        "proposed_total_myr": mission_service.json_value(proposed) if proposed is not None else None,
    }

    def link(approval: Approval) -> None:
        message.approval_id = approval.id

    return PreparedAction(action_type=ACTION_FOR_KIND[args.kind], snapshot=snapshot, on_approval_created=link)


@approved_action(*SEND_ACTIONS)
def perform_send_message(ctx: ToolContext, approval: Approval) -> dict[str, Any]:
    """Runs after approval. Simulated only: marks the message sent, never contacts anyone."""
    db = ctx.db
    snapshot = approval.content_snapshot
    message = db.get(Message, uuid.UUID(snapshot["message_id"]), with_for_update=True)
    if (
        message is None
        or message.approval_id != approval.id
        or message.status != MessageStatus.PENDING_APPROVAL.value
        or message.body != snapshot["body"]
        or str(message.stakeholder_id) != snapshot["stakeholder_id"]
        or message.mission_id != approval.mission_id
    ):
        raise Refused("The message no longer matches what was approved")

    now = datetime.now(UTC)
    message.status = MessageStatus.SENT.value
    message.is_simulated = True
    message.sent_at = now
    if message.kind == MessageKind.COUNTEROFFER.value or (
        message.kind == MessageKind.TERMS.value and message.proposed_total_myr is not None
    ):
        rounds = db.scalar(
            select(func.count())
            .select_from(Negotiation)
            .where(Negotiation.mission_id == message.mission_id, Negotiation.stakeholder_id == message.stakeholder_id)
        )
        db.add(
            Negotiation(
                mission_id=message.mission_id,
                stakeholder_id=message.stakeholder_id,
                round_number=rounds + 1,
                offer_total=message.proposed_total_myr,
                status=NegotiationStatus.SENT.value,
                conditions={"message_id": str(message.id)},
            )
        )
    db.flush()
    result = {
        "message_id": str(message.id),
        "kind": message.kind,
        "status": message.status,
        "is_simulated": True,
        "sent_at": now.isoformat(),
    }
    audit_service.record(db, ctx.actor, "message.sent_simulated", mission_id=message.mission_id, result_ref=result)
    return result


@approved_action("change_mission_limits")
def perform_change_limits(ctx: ToolContext, approval: Approval) -> dict[str, Any]:
    if ctx.mission is None:
        raise Refused("Mission not found")
    return mission_service.apply_limit_changes(ctx.db, ctx.actor, ctx.mission, approval.content_snapshot)
