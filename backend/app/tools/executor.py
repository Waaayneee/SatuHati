"""Every tool call, from any orchestrator, goes through here.

- Tier 0 tools run and are audited.
- Gated (external) tools never run directly. They become a pending approval and the
  call returns `approval_required`.
- `run_approved` is only called by `approval_service.decide` and runs the exact
  approved snapshot after `verify_and_consume`.
"""

import logging
import uuid
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.models import Approval, Mission
from app.services import approval_service, audit_service
from app.services.errors import DomainError, NotFound, Refused
from app.tools import registry
from app.tools.context import ToolContext
from app.tools.registry import PreparedAction, ToolSpec

logger = logging.getLogger(__name__)


def _as_uuid(value: Any) -> uuid.UUID | None:
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def _error(db: Session, actor: Actor, tool_name: str, mission_id: uuid.UUID | None, event: str, message: str,
           input_ref: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    audit_service.record(
        db, actor, event, mission_id=mission_id, tool_name=tool_name, input_ref=input_ref, status="error", error=message
    )
    db.commit()
    return {"status": "error", "tool": tool_name, "error": message, **extra}


def execute(
    db: Session, tool_name: str, args: dict[str, Any] | None, actor: Actor, mission_id: uuid.UUID | str | None
) -> dict[str, Any]:
    """Validates input, checks permission, then runs (Tier 0) or requests approval (gated)."""
    mission_uuid = _as_uuid(mission_id)
    spec = registry.get_tool(tool_name)
    if spec is None:
        return _error(db, actor, tool_name, mission_uuid, "tool.rejected", f"Unknown tool: {tool_name}")

    mission = db.get(Mission, mission_uuid) if mission_uuid else None
    if mission is None:
        return _error(db, actor, tool_name, mission_uuid, "tool.rejected", "Mission not found")

    try:
        parsed = spec.input_model.model_validate(args if args is not None else {})
    except ValidationError as exc:
        details = exc.errors(include_url=False, include_context=False, include_input=False)
        return _error(
            db, actor, tool_name, mission.id, "tool.invalid_input", "Invalid input",
            input_ref={"args": args}, details=details,
        )

    ctx = ToolContext(db=db, actor=actor, mission=mission)
    input_ref = parsed.model_dump(mode="json")
    if spec.gated:
        return _request_approval(spec, ctx, parsed, input_ref)
    return _run_direct(spec, ctx, parsed, input_ref)


def _refused(ctx: ToolContext, spec: ToolSpec, input_ref: dict[str, Any], exc: DomainError,
             tier: int | None = None) -> dict[str, Any]:
    status = audit_service.refusal_status(exc)
    audit_service.record(
        ctx.db, ctx.actor, f"tool.{status}", mission_id=ctx.mission.id, tool_name=spec.name,
        input_ref=input_ref, result_ref=exc.details or None, status=status, error=exc.message,
    )
    ctx.db.commit()
    result: dict[str, Any] = {"status": status, "tool": spec.name, "reason": exc.message, **exc.details}
    if tier is not None:
        result["tier"] = tier
    return result


def _run_direct(spec: ToolSpec, ctx: ToolContext, parsed: BaseModel, input_ref: dict[str, Any]) -> dict[str, Any]:
    db = ctx.db
    tier: int | None = None
    if spec.action_type is not None:
        perm = approval_service.check_permission(db, ctx.actor, spec.action_type, ctx.mission)
        tier = perm["tier"]
        if not perm["allowed_to_run_now"]:
            reason = (
                f"Mission is {ctx.mission.status}" if perm["tier"] == 0
                else f"{spec.action_type} is Tier {perm['tier']} and cannot run without approval"
            )
            return _refused(ctx, spec, input_ref, Refused(reason), tier)

    try:
        with db.begin_nested():
            output = spec.func(ctx, parsed)
            result = spec.output_model.model_validate(output).model_dump(mode="json")
    except DomainError as exc:
        return _refused(ctx, spec, input_ref, exc, tier)
    except Exception:
        logger.exception("Tool %s failed", spec.name)
        return _error(db, ctx.actor, spec.name, ctx.mission.id, "tool.error", "The tool failed unexpectedly",
                      input_ref=input_ref)

    status = "approval_required" if result.get("approval_required") else "ok"
    audit_service.record(
        db, ctx.actor, "tool.executed", mission_id=ctx.mission.id, tool_name=spec.name,
        input_ref=input_ref, result_ref=result, status=status,
    )
    db.commit()
    response: dict[str, Any] = {"status": status, "tool": spec.name, "tier": tier, "result": result}
    if status == "approval_required":
        response["approval_id"] = result.get("approval_id")
        response["approval_tier"] = result.get("approval_tier")
    return response


def _request_approval(spec: ToolSpec, ctx: ToolContext, parsed: BaseModel,
                      input_ref: dict[str, Any]) -> dict[str, Any]:
    db = ctx.db
    try:
        with db.begin_nested():
            prepared: PreparedAction = spec.func(ctx, parsed)
            approval = approval_service.request(
                db, ctx.actor, ctx.mission, prepared.action_type, prepared.snapshot, minimum_tier=spec.minimum_tier
            )
            if prepared.on_approval_created is not None:
                prepared.on_approval_created(approval)
            db.flush()
    except DomainError as exc:
        return _refused(ctx, spec, input_ref, exc)
    except Exception:
        logger.exception("Tool %s failed while requesting approval", spec.name)
        return _error(db, ctx.actor, spec.name, ctx.mission.id, "tool.error", "The tool failed unexpectedly",
                      input_ref=input_ref)

    result = {
        "approval_id": str(approval.id),
        "tier": approval.tier,
        "action_type": approval.action_type,
        "eligible_roles": approval.eligible_roles,
        "expires_at": approval.expires_at.isoformat(),
    }
    audit_service.record(
        db, ctx.actor, "tool.approval_required", mission_id=ctx.mission.id, tool_name=spec.name,
        input_ref=input_ref, result_ref=result, status="approval_required",
    )
    db.commit()
    return {
        "status": "approval_required",
        "tool": spec.name,
        **result,
        "note": "Not executed. A human approver must decide first.",
    }


def run_approved(db: Session, approval_id: uuid.UUID, token: str, actor: Actor) -> dict[str, Any]:
    """Only called by approval_service.decide. Verifies and burns the token, then runs
    the stored snapshot. Commits. Raises Refused if anything fails."""
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise NotFound("Approval not found")
    snapshot = dict(approval.content_snapshot)
    approval_service.verify_and_consume(db, approval_id, token, snapshot, actor)

    mission = db.get(Mission, approval.mission_id)
    handler = registry.get_approved_handler(approval.action_type)
    ctx = ToolContext(db=db, actor=actor, mission=mission)  # type: ignore[arg-type]
    try:
        with db.begin_nested():
            if handler is None:
                result = {
                    "performed": False,
                    "note": f"No executor exists for {approval.action_type} in Phase 1. The approval is recorded only.",
                }
            else:
                result = handler(ctx, approval)
    except Exception as exc:
        reason = exc.message if isinstance(exc, DomainError) else "Execution failed unexpectedly"
        if not isinstance(exc, DomainError):
            logger.exception("Approved action %s failed", approval.action_type)
        approval.status = "failed"
        approval.execution_result = {"error": reason}
        approval_service.refuse_linked_messages(db, approval)
        audit_service.record(
            db, actor, "approval.execution_failed", mission_id=approval.mission_id,
            input_ref={"approval_id": approval.id, "action_type": approval.action_type}, status="error", error=reason,
        )
        db.commit()
        raise Refused(f"Execution failed: {reason}") from exc

    approval.execution_result = result
    audit_service.record(
        db, actor, "approval.executed", mission_id=approval.mission_id,
        input_ref={"approval_id": approval.id, "action_type": approval.action_type, "tier": approval.tier},
        result_ref=result,
    )
    db.commit()
    return result
