from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import RoleAssignment, User
from app.models.enums import Role, UserStatus
from app.schemas.misc import ProfileOut

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileOut])
def list_profiles(db: Session = Depends(get_db)) -> list[ProfileOut]:
    """Demo profile switching: the people the UI may act as. HOD first."""
    if not settings.demo_profile_switch:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Profile switching is turned off")
    roles: dict = defaultdict(set)
    for assignment in db.scalars(select(RoleAssignment)):
        roles[assignment.user_id].add(assignment.role)
    users = db.scalars(select(User).where(User.status == UserStatus.ACTIVE.value)).all()
    profiles = [
        ProfileOut(
            id=u.id,
            email=u.email,
            name=u.name,
            roles=sorted(roles[u.id]),
            primary_role=Role.HOD.value if Role.HOD.value in roles[u.id] else Role.COMMITTEE_MEMBER.value,
        )
        for u in users
        if roles[u.id]
    ]
    return sorted(profiles, key=lambda p: (p.primary_role != Role.HOD.value, (p.name or p.email).lower()))
