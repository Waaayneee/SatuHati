"""FastAPI dependencies that turn a request into an Actor."""

import secrets
import uuid
from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.actor import AGENT_CLAUDE, Actor, user_actor
from app.auth.tokens import TokenError, verify_access_token
from app.config import settings
from app.db import get_db
from app.models import RoleAssignment, User
from app.models.enums import Role, UserStatus

_bearer = HTTPBearer(auto_error=False)

PROFILE_HEADER = "X-Profile-Id"


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _registered_user(db: Session, user_id: uuid.UUID) -> Actor:
    user = db.get(User, user_id)
    if user is None or user.status != UserStatus.ACTIVE.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account is not registered in KawTeam")
    roles = set(db.scalars(select(RoleAssignment.role).where(RoleAssignment.user_id == user_id)))
    if not roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account has no KawTeam role")
    return user_actor(user.id, roles, user.email)


def get_current_actor(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    x_agent_token: str | None = Header(default=None, alias="X-Agent-Token"),
    x_profile_id: str | None = Header(default=None, alias=PROFILE_HEADER),
) -> Actor:
    if x_agent_token is not None:
        expected = settings.agent_service_token
        # An empty configured token must never authenticate anything.
        if not expected or not secrets.compare_digest(x_agent_token.encode(), expected.encode()):
            raise _unauthorized("Invalid agent token")
        return AGENT_CLAUDE

    if credentials is not None:
        try:
            claims = verify_access_token(credentials.credentials)
            user_id = uuid.UUID(str(claims["sub"]))
        except (TokenError, ValueError):
            raise _unauthorized("Invalid or expired token") from None
        return _registered_user(db, user_id)

    if x_profile_id is not None:
        # Demo profile switching: the header names the person, no password.
        if not settings.demo_profile_switch:
            raise _unauthorized("Profile switching is turned off")
        try:
            user_id = uuid.UUID(x_profile_id)
        except ValueError:
            raise _unauthorized("Unknown profile") from None
        return _registered_user(db, user_id)

    raise _unauthorized("Missing bearer token")


def require_user(actor: Actor = Depends(get_current_actor)) -> Actor:
    if not actor.is_user:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="A signed-in person is required")
    return actor


def require_roles(*roles: Role) -> Callable[..., Actor]:
    wanted = {r.value for r in roles}

    def dependency(actor: Actor = Depends(require_user)) -> Actor:
        if not (actor.roles & wanted):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Your role cannot do this")
        return actor

    return dependency


def require_agent(actor: Actor = Depends(get_current_actor)) -> Actor:
    if not actor.is_agent:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Agent token required")
    return actor


require_member = require_roles(Role.COMMITTEE_MEMBER, Role.HOD)
require_hod = require_roles(Role.HOD)
