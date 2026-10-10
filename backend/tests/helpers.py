"""Shared test helpers: tokens, people, missions, and a fake Claude client."""

import json
import secrets
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.actor import Actor, user_actor
from app.config import settings
from app.models import Approval, AuditLog, Message, Mission, RoleAssignment, Stakeholder, User
from app.models.enums import MessageStatus
from app.services import approval_service, mission_service

TEST_JWT_SECRET = "kawteam-test-secret-0123456789abcdef0123456789abcdef"
TEST_AGENT_TOKEN = "kawteam-test-agent-token-" + "a" * 40
AGENT_HEADERS = {"X-Agent-Token": TEST_AGENT_TOKEN}


@dataclass
class People:
    hod: User
    cm_a: User
    cm_b: User


def make_user(db: Session, role: str | None, label: str) -> User:
    user = User(id=uuid.uuid4(), email=f"{label}-{uuid.uuid4().hex[:8]}@test.kawteam", name=label)
    db.add(user)
    db.flush()
    if role:
        db.add(RoleAssignment(user_id=user.id, role=role, assigned_by="system:test"))
        db.flush()
    return user


def token_for(user_id: uuid.UUID, **overrides: Any) -> str:
    now = int(time.time())
    claims = {
        "sub": str(user_id),
        "aud": "authenticated",
        "iss": settings.supabase_issuer,
        "role": "authenticated",
        "iat": now,
        "exp": now + 3600,
        **overrides,
    }
    return jwt.encode(claims, TEST_JWT_SECRET, algorithm="HS256")


def auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_for(user.id)}"}


def actor_for(db: Session, user: User) -> Actor:
    roles = set(db.scalars(select(RoleAssignment.role).where(RoleAssignment.user_id == user.id)))
    return user_actor(user.id, roles, user.email)


def create_active_mission(db: Session, people: People, **overrides: Any) -> Mission:
    """MISSION like the demo: 300 tote bags, target RM1,350, hard budget RM1,500."""
    data = {
        "goal_text": "300 custom tote bags for a 200-student tech event",
        "product": "Custom tote bags",
        "quantity": 300,
        "target_total_myr": Decimal("1350"),
        "hard_budget_myr": Decimal("1500"),
        "minimum_quality": Decimal("4.0"),
        "delivery_deadline": date(2026, 10, 25),
        "max_rounds": 3,
        **overrides,
    }
    mission = mission_service.create_mission(db, actor_for(db, people.cm_a), data)
    mission_service.confirm_limits(db, actor_for(db, people.hod), mission)
    db.commit()
    return mission


def make_stakeholder(db: Session, name: str = "Supplier B", opted_out: bool = False) -> Stakeholder:
    stakeholder = Stakeholder(
        name=name,
        org_type="supplier",
        contact_channel="email",
        contact_value=f"sales@{name.lower().replace(' ', '-')}.demo.test",
        opted_out=opted_out,
    )
    db.add(stakeholder)
    db.commit()
    return stakeholder


def enquiry_args(stakeholder: Stakeholder, body: str | None = None) -> dict[str, Any]:
    return {
        "stakeholder_id": str(stakeholder.id),
        "kind": "enquiry",
        "body": body
        or "Hello, could you quote 300 custom tote bags delivered by 25 October? "
        "Please include lead time and material options.",
    }


def counteroffer_args(stakeholder: Stakeholder, total: float = 1350) -> dict[str, Any]:
    return {
        "stakeholder_id": str(stakeholder.id),
        "kind": "counteroffer",
        "body": f"Thank you for your quotation of RM1450.00. Would you consider RM{total:.2f}?",
        "proposed_total_myr": total,
    }


def approve_without_running(db: Session, approval: Approval, approver: Actor) -> str:
    """What decide() does before execution, so tests can hold the token."""
    token = secrets.token_urlsafe(32)
    approval.status = "approved"
    approval.token_hash = approval_service._token_hash(token)
    approval.approver_id = approver.user_id
    approval.approver_role = "hod" if approver.is_hod else "committee_member"
    approval.decision_reason = "test"
    db.commit()
    return token


def sent_count(db: Session, mission: Mission) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Message)
        .where(Message.mission_id == mission.id, Message.status == MessageStatus.SENT.value)
    )


def audit_rows(db: Session, mission: Mission | None = None) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.at, AuditLog.id)
    if mission is not None:
        query = query.where(AuditLog.mission_id == mission.id)
    return list(db.scalars(query))


# ---------------------------------------------------------------------------
# Fake Anthropic client
# ---------------------------------------------------------------------------


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def tool_use_block(name: str, tool_input: dict[str, Any], block_id: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=block_id or f"toolu_{uuid.uuid4().hex[:12]}", name=name, input=tool_input)


def fake_response(stop_reason: str, *blocks: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks))


def last_tool_results(kwargs: dict[str, Any]) -> list[dict[str, Any]]:
    """Tool results the orchestrator sent back in its latest user message."""
    return [json.loads(block["content"]) for block in kwargs["messages"][-1]["content"]]


Step = SimpleNamespace | Callable[[dict[str, Any]], SimpleNamespace]


class FakeAnthropic:
    """Replays scripted responses. A step may be a callable that reads the request."""

    def __init__(self, script: list[Step]) -> None:
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        if not self.script:
            raise AssertionError("FakeAnthropic ran out of scripted responses")
        step = self.script.pop(0)
        return step(kwargs) if callable(step) else step


def cheapest_within_budget(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Reads the search_suppliers tool result from the request."""
    search = last_tool_results(kwargs)[0]["result"]
    candidates = [s for s in search["suppliers"] if s["within_budget"]]
    return min(candidates, key=lambda s: s["price"])
