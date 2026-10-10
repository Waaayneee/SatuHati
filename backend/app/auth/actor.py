"""Who is acting. Framework-agnostic so tools and services can use it."""

import uuid
from dataclasses import dataclass, field
from typing import Literal

from app.models.enums import Role

ActorType = Literal["user", "agent", "system"]


@dataclass(frozen=True)
class Actor:
    type: ActorType
    id: str
    roles: frozenset[str] = field(default_factory=frozenset)
    email: str | None = None
    # For agent actors: the person whose request started the run, if any.
    on_behalf_of: uuid.UUID | None = None

    @property
    def ref(self) -> str:
        """Audit form, e.g. `user:<uuid>` or `agent:claude`."""
        return f"{self.type}:{self.id}"

    @property
    def is_user(self) -> bool:
        return self.type == "user"

    @property
    def is_agent(self) -> bool:
        return self.type == "agent"

    @property
    def user_id(self) -> uuid.UUID | None:
        return uuid.UUID(self.id) if self.is_user else None

    def has_role(self, role: Role) -> bool:
        return role.value in self.roles

    @property
    def is_hod(self) -> bool:
        return self.is_user and self.has_role(Role.HOD)

    @property
    def is_committee_member(self) -> bool:
        return self.is_user and self.has_role(Role.COMMITTEE_MEMBER)

    @property
    def audit_role(self) -> str | None:
        if self.is_agent:
            return "agent"
        if self.is_hod:
            return Role.HOD.value
        if self.is_committee_member:
            return Role.COMMITTEE_MEMBER.value
        return None


def user_actor(user_id: uuid.UUID, roles: set[str] | frozenset[str], email: str | None = None) -> Actor:
    return Actor(type="user", id=str(user_id), roles=frozenset(roles), email=email)


def agent_actor(name: str = "claude", on_behalf_of: uuid.UUID | None = None) -> Actor:
    """Agents never carry roles, so they can never approve anything."""
    return Actor(type="agent", id=name, on_behalf_of=on_behalf_of)


AGENT_CLAUDE = agent_actor("claude")
SYSTEM = Actor(type="system", id="backend")
SYSTEM_SEED = Actor(type="system", id="seed")
