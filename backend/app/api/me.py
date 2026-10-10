from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.auth.dependencies import require_user
from app.db import get_db
from app.models import User
from app.models.enums import Role
from app.schemas.misc import MeOut

router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeOut)
def me(actor: Actor = Depends(require_user), db: Session = Depends(get_db)) -> MeOut:
    user = db.get(User, actor.user_id)
    return MeOut(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=sorted(actor.roles),
        primary_role=Role.HOD.value if actor.is_hod else Role.COMMITTEE_MEMBER.value,
    )
