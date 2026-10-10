import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.claude_orchestrator import AgentConfigError, ClaudeOrchestrator
from app.api import serializers
from app.auth.actor import Actor
from app.auth.dependencies import require_hod, require_member, require_user
from app.db import get_db
from app.models import Approval, EvidenceSource, Message, Mission, Quotation, Stakeholder
from app.schemas.missions import (
    AgentRunIn,
    MessageOut,
    MissionCreate,
    MissionDetail,
    MissionOut,
    MissionUpdate,
    MissionUpdateOut,
    QuotationOut,
)
from app.services import audit_service, mission_service

router = APIRouter(prefix="/missions", tags=["missions"])


def _mission_out(db: Session, mission: Mission) -> MissionOut:
    return serializers.mission_out(mission, serializers.user_emails(db, [mission.owner_id]))


@router.post("", response_model=MissionOut, status_code=status.HTTP_201_CREATED)
def create_mission(
    body: MissionCreate, actor: Actor = Depends(require_member), db: Session = Depends(get_db)
) -> MissionOut:
    data = body.model_dump(exclude={"confirm_limits"}, exclude_none=True)
    with audit_service.audited_refusals(db, actor, "mission.create_refused"):
        mission = mission_service.create_mission(db, actor, data, confirm_limits=body.confirm_limits)
    db.commit()
    return _mission_out(db, mission)


@router.get("", response_model=list[MissionOut])
def list_missions(actor: Actor = Depends(require_user), db: Session = Depends(get_db)) -> list[MissionOut]:
    missions = db.scalars(select(Mission).order_by(Mission.created_at.desc()).limit(200)).all()
    emails = serializers.user_emails(db, [m.owner_id for m in missions])
    return [serializers.mission_out(m, emails) for m in missions]


@router.get("/{mission_id}", response_model=MissionDetail)
def get_mission(
    mission_id: uuid.UUID, actor: Actor = Depends(require_user), db: Session = Depends(get_db)
) -> MissionDetail:
    mission = mission_service.get_mission(db, mission_id)
    approvals = db.scalars(
        select(Approval).where(Approval.mission_id == mission.id).order_by(Approval.created_at.desc())
    ).all()
    messages = db.execute(
        select(Message, Stakeholder)
        .outerjoin(Stakeholder, Stakeholder.id == Message.stakeholder_id)
        .where(Message.mission_id == mission.id)
        .order_by(Message.created_at.desc())
    ).all()
    quotations = db.execute(
        select(Quotation, Stakeholder, EvidenceSource)
        .join(Stakeholder, Stakeholder.id == Quotation.stakeholder_id)
        .outerjoin(EvidenceSource, EvidenceSource.id == Quotation.source_id)
        .where(Quotation.mission_id == mission.id)
        .order_by(Quotation.total_price)
    ).all()
    emails = serializers.approval_emails(db, approvals)
    emails.update(serializers.user_emails(db, [mission.owner_id]))
    return MissionDetail(
        mission=serializers.mission_out(mission, emails),
        approvals=[serializers.approval_summary(a, mission, emails) for a in approvals],
        messages=[
            MessageOut(
                id=m.id,
                stakeholder_id=m.stakeholder_id,
                supplier=s.name if s else None,
                recipient=s.contact_value if s else None,
                direction=m.direction,
                kind=m.kind,
                channel=m.channel,
                body=m.body,
                proposed_total_myr=m.proposed_total_myr,
                status=m.status,
                is_simulated=m.is_simulated,
                approval_id=m.approval_id,
                sent_at=m.sent_at,
                created_at=m.created_at,
            )
            for m, s in messages
        ],
        quotations=[
            QuotationOut(
                id=q.id,
                stakeholder_id=q.stakeholder_id,
                supplier=s.name,
                total_price=q.total_price,
                unit_price=q.unit_price,
                currency=q.currency,
                verification_state=q.verification_state.value,
                is_simulated=bool(e.is_simulated) if e else False,
            )
            for q, s, e in quotations
        ],
    )


@router.patch("/{mission_id}", response_model=MissionUpdateOut)
def update_mission(
    mission_id: uuid.UUID,
    body: MissionUpdate,
    actor: Actor = Depends(require_member),
    db: Session = Depends(get_db),
) -> MissionUpdateOut:
    mission = mission_service.get_mission(db, mission_id)
    changes = body.model_dump(exclude_unset=True)
    with audit_service.audited_refusals(
        db, actor, "mission.update_refused", mission_id=mission.id, input_ref={"fields": sorted(changes)}
    ):
        result = mission_service.update_mission(db, actor, mission, changes)
    db.commit()
    emails = serializers.user_emails(db, [mission.owner_id, actor.user_id])
    return MissionUpdateOut(
        mission=serializers.mission_out(result.mission, emails),
        updated_fields=result.updated_fields,
        approval=serializers.approval_summary(result.approval, mission, emails) if result.approval else None,
    )


@router.post("/{mission_id}/confirm-limits", response_model=MissionOut)
def confirm_limits(
    mission_id: uuid.UUID, actor: Actor = Depends(require_hod), db: Session = Depends(get_db)
) -> MissionOut:
    mission = mission_service.get_mission(db, mission_id)
    with audit_service.audited_refusals(db, actor, "mission.confirm_refused", mission_id=mission.id):
        mission_service.confirm_limits(db, actor, mission)
    db.commit()
    return _mission_out(db, mission)


@router.post("/{mission_id}/agent/run")
def run_agent(
    mission_id: uuid.UUID,
    body: AgentRunIn,
    actor: Actor = Depends(require_member),
    db: Session = Depends(get_db),
) -> dict:
    mission = mission_service.get_mission(db, mission_id)
    try:
        orchestrator = ClaudeOrchestrator(db)
    except AgentConfigError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Agent not configured: {exc}") from None
    return orchestrator.run(mission, body.prompt, on_behalf_of=actor.user_id).to_dict()
