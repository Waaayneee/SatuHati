"""Append-only audit trail. Callers own the transaction (record() only adds a row)."""

import json
import re
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.models import AuditLog
from app.services.errors import DomainError, PermissionDenied, Refused

_SENSITIVE_KEY = re.compile(r"token|secret|password|passwd|api[_-]?key|authorization|cookie", re.IGNORECASE)
# Message bodies are stored by reference (message_id), never copied into the log.
_REFERENCE_ONLY_KEYS = {"body", "message", "prompt_text"}
MAX_INLINE_STRING = 500


def _omitted(value: str) -> str:
    return f"[omitted: {len(value)} chars]"


def sanitize(value: Any, _key: str | None = None) -> Any:
    """Redact secrets and drop long text so the log never stores sensitive values."""
    if _key is not None and _SENSITIVE_KEY.search(_key):
        return "[redacted]"
    if isinstance(value, dict):
        return {str(k): sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        if (_key in _REFERENCE_ONLY_KEYS) or len(value) > MAX_INLINE_STRING:
            return _omitted(value)
        return value
    if value is None or isinstance(value, (bool, int, float)):
        return value
    # UUID, Decimal, date, datetime, enums...
    return str(getattr(value, "value", value))


def _to_json(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return json.loads(json.dumps(sanitize(value), default=str))


def record(
    db: Session,
    actor: Actor,
    event_type: str,
    mission_id: uuid.UUID | None = None,
    tool_name: str | None = None,
    input_ref: dict[str, Any] | None = None,
    result_ref: dict[str, Any] | None = None,
    status: str = "ok",
    error: str | None = None,
    retry_count: int = 0,
) -> AuditLog:
    """Inserts one audit row in the caller's transaction."""
    if actor.is_agent and actor.on_behalf_of is not None:
        input_ref = {**(input_ref or {}), "on_behalf_of": str(actor.on_behalf_of)}
    row = AuditLog(
        actor=actor.ref,
        actor_role=actor.audit_role,
        mission_id=mission_id,
        event_type=event_type,
        tool_name=tool_name,
        input_ref=_to_json(input_ref),
        result_ref=_to_json(result_ref),
        status=status,
        error=(error[:MAX_INLINE_STRING] if error else None),
        retry_count=retry_count,
    )
    db.add(row)
    db.flush()
    return row


def refusal_status(exc: DomainError) -> str:
    return "refused" if isinstance(exc, (Refused, PermissionDenied)) else "error"


@contextmanager
def audited_refusals(
    db: Session,
    actor: Actor,
    event_type: str,
    mission_id: uuid.UUID | None = None,
    input_ref: dict[str, Any] | None = None,
) -> Iterator[None]:
    """If the block raises a DomainError: roll back its partial work, record the
    refusal, commit that audit row, then re-raise."""
    try:
        yield
    except DomainError as exc:
        db.rollback()
        record(
            db,
            actor,
            event_type,
            mission_id=mission_id,
            input_ref=input_ref,
            result_ref=exc.details or None,
            status=refusal_status(exc),
            error=exc.message,
        )
        db.commit()
        raise
