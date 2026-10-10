import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, SmallInteger, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import ApprovalStatus, sql_in
from app.models.missions import MONEY


class ApprovalPolicy(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "approval_policies"
    __table_args__ = (CheckConstraint("tier >= 0 AND tier <= 3", name="tier_range"),)

    action_type: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    eligible_roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    is_external: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ttl_hours: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class Approval(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "approvals"
    __table_args__ = (
        CheckConstraint(f"status IN ({sql_in(ApprovalStatus)})", name="status"),
        CheckConstraint("tier >= 1 AND tier <= 3", name="tier_range"),
    )

    mission_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("missions.id"), index=True)
    action_type: Mapped[str] = mapped_column(Text, nullable=False)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # Actor reference of whoever called the tool, e.g. "agent:claude" or "user:<uuid>".
    requested_by: Mapped[str] = mapped_column(Text, nullable=False)
    # The person who started the agent run (counts as the requester for no-self-approval).
    requested_on_behalf_of: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    eligible_roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default=ApprovalStatus.PENDING.value, server_default=ApprovalStatus.PENDING.value
    )
    approver_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    approver_role: Mapped[str | None] = mapped_column(Text)
    decision_reason: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    token_hash: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hard_budget_at_request: Mapped[Decimal | None] = mapped_column(MONEY)
    execution_result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
