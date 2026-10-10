import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.api import serializers
from app.auth.actor import Actor
from app.auth.dependencies import get_current_actor, require_user
from app.db import get_db
from app.models import Approval, Mission
from app.models.enums import ApprovalStatus
from app.schemas.approvals import ApprovalDetail, ApprovalSummary, DecisionIn
from app.services import approval_service
from app.services.errors import NotFound

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalSummary])
def inbox(
    status_filter: Literal["pending", "all"] = Query("all", alias="status"),
    actor: Actor = Depends(require_user),
    db: Session = Depends(get_db),
) -> list[ApprovalSummary]:
    """HOD sees everything. Committee Members see Tier 1 items they did not request,
    plus every approval on their own missions."""
    if approval_service.expire_stale(db):
        db.commit()
    query = select(Approval, Mission).outerjoin(Mission, Mission.id == Approval.mission_id)
    if not actor.is_hod:
        me = actor.user_id
        not_mine = and_(
            Approval.tier == 1,
            or_(Approval.requested_on_behalf_of.is_(None), Approval.requested_on_behalf_of != me),
            Approval.requested_by != actor.ref,
        )
        query = query.where(or_(not_mine, Mission.owner_id == me))
    if status_filter == "pending":
        query = query.where(Approval.status == ApprovalStatus.PENDING.value)
    rows = db.execute(query.order_by(Approval.created_at.desc()).limit(200)).all()
    emails = serializers.approval_emails(db, [a for a, _ in rows])
    return [serializers.approval_summary(a, mission, emails) for a, mission in rows]


@router.get("/{approval_id}", response_model=ApprovalDetail)
def detail(
    approval_id: uuid.UUID, actor: Actor = Depends(require_user), db: Session = Depends(get_db)
) -> ApprovalDetail:
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise NotFound("Approval not found")
    return serializers.approval_detail(db, approval, actor)


@router.post("/{approval_id}/decision", response_model=ApprovalDetail)
def decide(
    approval_id: uuid.UUID,
    body: DecisionIn,
    actor: Actor = Depends(get_current_actor),
    db: Session = Depends(get_db),
) -> ApprovalDetail:
    """One approval per call. Agents are refused inside approval_service.decide."""
    approval = approval_service.decide(db, actor, approval_id, body.decision, body.reason)
    return serializers.approval_detail(db, approval, actor)
