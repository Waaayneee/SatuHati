import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api import serializers
from app.auth.actor import Actor
from app.auth.dependencies import require_user
from app.db import get_db
from app.models import AuditLog, Mission
from app.schemas.misc import AuditOut
from app.services import approval_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut])
def audit_log(
    mission_id: uuid.UUID | None = None,
    limit: int = Query(200, ge=1, le=500),
    actor: Actor = Depends(require_user),
    db: Session = Depends(get_db),
) -> list[AuditOut]:
    """HOD sees all. Committee Members see their own missions and their own actions."""
    query = select(AuditLog, Mission.code).outerjoin(Mission, Mission.id == AuditLog.mission_id)
    if not actor.is_hod:
        query = query.where(or_(Mission.owner_id == actor.user_id, AuditLog.actor == actor.ref))
    if mission_id is not None:
        query = query.where(AuditLog.mission_id == mission_id)
    rows = db.execute(query.order_by(AuditLog.at.desc()).limit(limit)).all()

    ids: set[uuid.UUID | None] = set()
    for row, _ in rows:
        ids.add(approval_service.user_id_from_ref(row.actor))
        on_behalf = (row.input_ref or {}).get("on_behalf_of")
        if on_behalf:
            try:
                ids.add(uuid.UUID(on_behalf))
            except ValueError:
                pass
    emails = serializers.user_emails(db, ids)

    def label(row: AuditLog) -> str:
        text = serializers.actor_label(row.actor, emails)
        on_behalf = (row.input_ref or {}).get("on_behalf_of")
        if row.actor.startswith("agent:") and on_behalf:
            try:
                person = emails.get(uuid.UUID(on_behalf))
            except ValueError:
                person = None
            if person:
                text = f"{text} for {person}"
        return text

    return [
        AuditOut(
            id=row.id,
            at=row.at,
            actor=row.actor,
            actor_label=label(row),
            actor_role=row.actor_role,
            mission_id=row.mission_id,
            mission_code=code,
            event_type=row.event_type,
            tool_name=row.tool_name,
            status=row.status,
            error=row.error,
            input_ref=row.input_ref,
            result_ref=row.result_ref,
        )
        for row, code in rows
    ]
