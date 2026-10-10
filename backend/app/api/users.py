from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.auth.dependencies import require_hod
from app.db import get_db
from app.models import RoleAssignment, User
from app.schemas.misc import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(actor: Actor = Depends(require_hod), db: Session = Depends(get_db)) -> list[UserOut]:
    """Read only in Phase 1."""
    roles: dict = defaultdict(list)
    for assignment in db.scalars(select(RoleAssignment)):
        roles[assignment.user_id].append(assignment.role)
    users = db.scalars(select(User).order_by(User.email)).all()
    return [
        UserOut(id=u.id, email=u.email, name=u.name, status=u.status, roles=sorted(roles[u.id]), created_at=u.created_at)
        for u in users
    ]
