import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money


class ApprovalSummary(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID | None
    mission_code: str | None
    action_type: str
    tier: int
    status: str
    requested_by: str
    requester_label: str
    eligible_roles: list[str]
    expires_at: datetime
    created_at: datetime
    decided_at: datetime | None
    approver_role: str | None
    recipient_name: str | None
    kind: str | None
    proposed_total_myr: Money | None
    preview: str | None


class BudgetComparison(BaseModel):
    hard_budget_myr: Money | None
    hard_budget_at_request: Money | None
    target_total_myr: Money | None
    proposed_total_myr: Money | None
    within_budget: bool | None
    difference_from_target_myr: Money | None


class ApprovalDetail(ApprovalSummary):
    content_snapshot: dict[str, Any]
    content_hash: str
    decision_reason: str | None
    approver_email: str | None
    used_at: datetime | None
    execution_result: dict[str, Any] | None
    budget: BudgetComparison
    can_decide: bool
    cannot_decide_reason: str | None


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=1, max_length=1000)
