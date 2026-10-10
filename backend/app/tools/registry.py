"""One registry of agent tools, independent of any orchestrator.

The Claude orchestrator (Phase 1) and the WorkBuddy MCP server (Phase 7) both read
`list_tools()` and send every call through `executor.execute`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.models import Approval
from app.tools.context import ToolContext


@dataclass(frozen=True)
class PreparedAction:
    """What a gated (external) tool wants to do, waiting for approval."""

    action_type: str
    snapshot: dict[str, Any]
    on_approval_created: Callable[[Approval], None] | None = None


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    # Policy action type. None for read-only helper tools. For gated tools this is a
    # label, because the real action type comes from the call (see PreparedAction).
    action_type: str | None
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    func: Callable[..., Any]
    # Gated tools never run directly. `func` returns a PreparedAction and the
    # executor turns it into an approval request.
    gated: bool = False
    # For gated tools: lowest tier allowed even if a policy says Tier 0 (default deny).
    minimum_tier: int | None = None


_TOOLS: dict[str, ToolSpec] = {}
_APPROVED_HANDLERS: dict[str, Callable[[ToolContext, Approval], dict[str, Any]]] = {}


def tool(
    name: str,
    description: str,
    action_type: str | None,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    gated: bool = False,
    minimum_tier: int | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Registers a plain function `(ctx: ToolContext, args: input_model) -> output_model`."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if name in _TOOLS:
            raise ValueError(f"Tool {name!r} is already registered")
        _TOOLS[name] = ToolSpec(
            name=name,
            description=description,
            action_type=action_type,
            input_model=input_model,
            output_model=output_model,
            func=func,
            gated=gated,
            minimum_tier=minimum_tier,
        )
        return func

    return decorator


def approved_action(*action_types: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Registers what runs after an approval of one of these action types is granted."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        for action_type in action_types:
            if action_type in _APPROVED_HANDLERS:
                raise ValueError(f"Handler for {action_type!r} is already registered")
            _APPROVED_HANDLERS[action_type] = func
        return func

    return decorator


def get_tool(name: str) -> ToolSpec | None:
    return _TOOLS.get(name)


def get_approved_handler(action_type: str) -> Callable[[ToolContext, Approval], dict[str, Any]] | None:
    return _APPROVED_HANDLERS.get(action_type)


def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": spec.name,
            "description": spec.description,
            "action_type": spec.action_type,
            "input_schema": spec.input_model.model_json_schema(),
        }
        for spec in _TOOLS.values()
    ]
