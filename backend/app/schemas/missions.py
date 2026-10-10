import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.approvals import ApprovalSummary
from app.schemas.common import Money, MoneyIn, Rating


class MissionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_text: str = Field(min_length=1, max_length=2000)
    product: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0, le=1_000_000)
    target_total_myr: MoneyIn = Field(ge=0)
    hard_budget_myr: MoneyIn = Field(gt=0)
    minimum_quality: Decimal = Field(ge=0, le=5, max_digits=2, decimal_places=1)
    delivery_deadline: date
    max_rounds: int = Field(default=3, ge=1, le=10)
    notes: str | None = Field(default=None, max_length=4000)
    confirm_limits: bool = Field(default=False, description="HOD only: create and confirm in one step")

    @model_validator(mode="after")
    def _target_within_budget(self) -> "MissionCreate":
        if self.target_total_myr > self.hard_budget_myr:
            raise ValueError("Target price cannot exceed the hard budget")
        return self


class MissionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_text: str | None = Field(default=None, min_length=1, max_length=2000)
    target_total_myr: MoneyIn | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=4000)
    product: str | None = Field(default=None, min_length=1, max_length=200)
    quantity: int | None = Field(default=None, gt=0, le=1_000_000)
    hard_budget_myr: MoneyIn | None = Field(default=None, gt=0)
    minimum_quality: Decimal | None = Field(default=None, ge=0, le=5, max_digits=2, decimal_places=1)
    delivery_deadline: date | None = None
    max_rounds: int | None = Field(default=None, ge=1, le=10)


class MissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    owner_id: uuid.UUID
    owner_email: str | None = None
    goal_text: str
    product: str | None
    quantity: int | None
    target_total_myr: Money | None
    hard_budget_myr: Money | None
    minimum_quality: Rating | None
    delivery_deadline: date | None
    max_rounds: int
    approval_policy: dict[str, Any]
    status: str
    notes: str | None
    limits_confirmed_by: uuid.UUID | None
    limits_confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: uuid.UUID
    stakeholder_id: uuid.UUID | None
    supplier: str | None
    recipient: str | None
    direction: str
    kind: str
    channel: str
    body: str
    proposed_total_myr: Money | None
    status: str
    is_simulated: bool
    approval_id: uuid.UUID | None
    sent_at: datetime | None
    created_at: datetime


class QuotationOut(BaseModel):
    id: uuid.UUID
    stakeholder_id: uuid.UUID
    supplier: str
    total_price: Money | None
    unit_price: Money | None
    currency: str
    verification_state: str
    is_simulated: bool


class MissionDetail(BaseModel):
    mission: MissionOut
    approvals: list[ApprovalSummary]
    messages: list[MessageOut]
    quotations: list[QuotationOut]


class MissionUpdateOut(BaseModel):
    mission: MissionOut
    updated_fields: list[str]
    approval: ApprovalSummary | None


class AgentRunIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=4000)
