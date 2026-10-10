"""Idempotent seed data: approval policies and the seeded users' roles."""

import uuid
from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth.actor import SYSTEM_SEED
from app.models import ApprovalPolicy, RoleAssignment, User
from app.models.enums import Role
from app.services import audit_service

ANY = ["any"]
TIER1_ROLES = [Role.COMMITTEE_MEMBER.value, Role.HOD.value]
HOD_ONLY = [Role.HOD.value]
NOT_REQUESTER = "committee_member must not be the requester"

# (action_type, tier, eligible_roles, is_external, notes)
APPROVAL_POLICIES: list[tuple[str, int, list[str], bool, str | None]] = [
    ("read_mission_state", 0, ANY, False, None),
    ("update_mission_state", 0, ANY, False, "Non-limit fields only. Limit changes on an active mission use change_mission_limits"),
    ("search_suppliers", 0, ANY, False, None),
    ("prepare_counteroffer", 0, ANY, False, "Draft only, never sent"),
    ("send_enquiry", 1, TIER1_ROLES, True, NOT_REQUESTER),
    ("send_clarification", 1, TIER1_ROLES, True, NOT_REQUESTER),
    ("send_follow_up", 1, TIER1_ROLES, True, NOT_REQUESTER),
    ("send_counteroffer", 2, HOD_ONLY, True, None),
    ("send_terms_message", 2, HOD_ONLY, True, "Also used when a Tier 1 message states a price, budget or terms"),
    ("confirm_mission_limits", 3, HOD_ONLY, False, None),
    ("change_mission_limits", 3, HOD_ONLY, False, "Limits on an active mission"),
    ("confirm_commitment", 3, HOD_ONLY, True, "Policy only. Tool arrives in Phase 6"),
]


def seed_policies(db: Session) -> int:
    """Insert or update every policy row. Returns the number of rows written."""
    existing = {p.action_type: p for p in db.scalars(select(ApprovalPolicy))}
    written = 0
    for action_type, tier, roles, is_external, notes in APPROVAL_POLICIES:
        policy = existing.get(action_type)
        if policy is None:
            db.add(
                ApprovalPolicy(
                    action_type=action_type, tier=tier, eligible_roles=roles, is_external=is_external, notes=notes
                )
            )
            written += 1
        elif (policy.tier, policy.eligible_roles, policy.is_external, policy.notes) != (tier, roles, is_external, notes):
            policy.tier, policy.eligible_roles, policy.is_external, policy.notes = tier, roles, is_external, notes
            written += 1
    db.flush()
    return written


@dataclass
class SeedUser:
    email: str
    role: Role


@dataclass
class SeedResult:
    user_id: uuid.UUID
    email: str
    role: Role
    changed: bool


def lookup_auth_user_ids(db: Session, emails: list[str]) -> dict[str, uuid.UUID]:
    """Reads Supabase `auth.users` through the database connection (no secret key needed)."""
    rows = db.execute(
        text("SELECT id, lower(email) AS email FROM auth.users WHERE lower(email) = ANY(:emails)"),
        {"emails": [e.lower() for e in emails]},
    )
    return {row.email: row.id for row in rows}


def seed_users(db: Session, seed_users: list[SeedUser], auth_ids: dict[str, uuid.UUID]) -> list[SeedResult]:
    """Make each seeded user have exactly the configured role. Every change is audited."""
    results = []
    for entry in seed_users:
        email = entry.email.lower()
        user_id = auth_ids[email]
        changed = False

        user = db.get(User, user_id)
        if user is None:
            user = User(id=user_id, email=email, name=email.split("@")[0])
            db.add(user)
            db.flush()
            changed = True
            audit_service.record(
                db, SYSTEM_SEED, "user.created", input_ref={"user_id": str(user_id), "email": email}
            )

        assignments = list(db.scalars(select(RoleAssignment).where(RoleAssignment.user_id == user_id)))
        for assignment in assignments:
            if assignment.role != entry.role.value:
                db.delete(assignment)
                changed = True
                audit_service.record(
                    db, SYSTEM_SEED, "role.removed", input_ref={"user_id": str(user_id), "role": assignment.role}
                )
        if not any(a.role == entry.role.value for a in assignments):
            db.add(RoleAssignment(user_id=user_id, role=entry.role.value, assigned_by=SYSTEM_SEED.ref))
            changed = True
            audit_service.record(
                db, SYSTEM_SEED, "role.assigned", input_ref={"user_id": str(user_id), "role": entry.role.value}
            )
        db.flush()
        results.append(SeedResult(user_id=user_id, email=email, role=entry.role, changed=changed))
    return results
