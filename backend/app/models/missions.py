import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import (
    MessageDirection,
    MessageKind,
    MessageStatus,
    MissionStatus,
    NegotiationStatus,
    VerificationState,
    sql_in,
)

MONEY = Numeric(12, 2)

verification_state_enum = Enum(
    VerificationState,
    name="verification_state",
    values_callable=lambda members: [m.value for m in members],
)


class Mission(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint(f"status IN ({sql_in(MissionStatus)})", name="status"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("hard_budget_myr > 0", name="hard_budget_positive"),
        CheckConstraint("target_total_myr >= 0", name="target_non_negative"),
        CheckConstraint("target_total_myr <= hard_budget_myr", name="target_within_budget"),
        CheckConstraint("minimum_quality >= 0 AND minimum_quality <= 5", name="minimum_quality_range"),
        CheckConstraint("max_rounds >= 1 AND max_rounds <= 10", name="max_rounds_range"),
    )

    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    product: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[int | None] = mapped_column(Integer)
    target_total_myr: Mapped[Decimal | None] = mapped_column(MONEY)
    hard_budget_myr: Mapped[Decimal | None] = mapped_column(MONEY)
    minimum_quality: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    delivery_deadline: Mapped[date | None] = mapped_column(Date)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    approval_policy: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default=MissionStatus.DRAFT.value, server_default=MissionStatus.DRAFT.value
    )
    notes: Mapped[str | None] = mapped_column(Text)
    limits_confirmed_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    limits_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EvidenceSource(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "evidence_sources"
    __table_args__ = (CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),)

    url: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    claim: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    caveat: Mapped[str | None] = mapped_column(Text)
    is_simulated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")


class Stakeholder(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "stakeholders"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    org_type: Mapped[str | None] = mapped_column(Text)
    contact_channel: Mapped[str | None] = mapped_column(Text)
    contact_value: Mapped[str | None] = mapped_column(Text)
    contact_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    opted_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("evidence_sources.id"))


class Quotation(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "quotations"

    mission_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("missions.id"), nullable=False, index=True)
    stakeholder_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("stakeholders.id"), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(MONEY)
    total_price: Mapped[Decimal | None] = mapped_column(MONEY)
    currency: Mapped[str] = mapped_column(Text, nullable=False, default="MYR", server_default="MYR")
    delivery_cost: Mapped[Decimal | None] = mapped_column(MONEY)
    tax_fees: Mapped[Decimal | None] = mapped_column(MONEY)
    lead_days: Mapped[int | None] = mapped_column(Integer)
    valid_until: Mapped[date | None] = mapped_column(Date)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("evidence_sources.id"))
    verification_state: Mapped[VerificationState] = mapped_column(
        verification_state_enum,
        nullable=False,
        default=VerificationState.RESEARCH_RESULT,
        server_default=VerificationState.RESEARCH_RESULT.value,
    )


class Negotiation(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "negotiations"
    __table_args__ = (
        CheckConstraint(f"status IN ({sql_in(NegotiationStatus)})", name="status"),
        UniqueConstraint("mission_id", "stakeholder_id", "round_number", name="uq_negotiations_round"),
    )

    mission_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("missions.id"), nullable=False, index=True)
    stakeholder_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("stakeholders.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    offer_total: Mapped[Decimal | None] = mapped_column(MONEY)
    response: Mapped[str | None] = mapped_column(Text)
    conditions: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)


class Message(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(f"direction IN ({sql_in(MessageDirection)})", name="direction"),
        CheckConstraint(f"kind IN ({sql_in(MessageKind)})", name="kind"),
        CheckConstraint(f"status IN ({sql_in(MessageStatus)})", name="status"),
    )

    mission_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("missions.id"), nullable=False, index=True)
    stakeholder_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("stakeholders.id"))
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False, default="email", server_default="email")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_total_myr: Mapped[Decimal | None] = mapped_column(MONEY)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    approval_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("approvals.id"), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Outcome(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "outcomes"

    mission_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("missions.id"), nullable=False, index=True)
    selected_quotation_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("quotations.id"))
    terms_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    approval_status: Mapped[str | None] = mapped_column(Text)
    savings_myr: Mapped[Decimal | None] = mapped_column(MONEY)
    caveats: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
