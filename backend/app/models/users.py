import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import Role, UserStatus, sql_in


class User(Timestamps, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint(f"status IN ({sql_in(UserStatus)})", name="status"),)

    # Equals the Supabase auth user ID (no default: it always comes from Supabase).
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default=UserStatus.ACTIVE.value, server_default=UserStatus.ACTIVE.value
    )


class RoleAssignment(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "role_assignments"
    __table_args__ = (
        CheckConstraint(f"role IN ({sql_in(Role)})", name="role"),
        UniqueConstraint("user_id", "role", "org_scope", name="uq_role_assignments_user_role_scope"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    org_scope: Mapped[str] = mapped_column(Text, nullable=False, default="default", server_default="default")
    # Actor reference, e.g. "system:seed" or "user:<uuid>".
    assigned_by: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
