import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MeOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    roles: list[str]
    primary_role: str


class ProfileOut(MeOut):
    pass


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    status: str
    roles: list[str]
    created_at: datetime


class AuditOut(BaseModel):
    id: uuid.UUID
    at: datetime
    actor: str
    actor_label: str
    actor_role: str | None
    mission_id: uuid.UUID | None
    mission_code: str | None
    event_type: str
    tool_name: str | None
    status: str
    error: str | None
    input_ref: dict[str, Any] | None
    result_ref: dict[str, Any] | None


class AgentToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission_id: uuid.UUID
    args: dict[str, Any] = Field(default_factory=dict)
