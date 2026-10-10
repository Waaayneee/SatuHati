"""First agent loop: Claude API tool use over the KawTeam tool registry.

Every tool call goes through the backend executor as `agent:claude`. The loop stops
on a final answer, as soon as any tool returns `approval_required`, or after
AGENT_MAX_ITERATIONS model calls.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import anthropic
from sqlalchemy.orm import Session

from app.auth.actor import agent_actor
from app.config import settings
from app.models import Mission
from app.services import audit_service
from app.tools import executor, registry

SYSTEM_PROMPT_PATH = Path(__file__).with_name("system_prompt.md")
MAX_TOKENS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AgentConfigError(Exception):
    pass


@dataclass
class ToolCall:
    name: str
    status: str
    approval_id: str | None = None
    tier: int | None = None
    reason: str | None = None


@dataclass
class RunResult:
    status: str  # completed | approval_required | max_iterations | refused | incomplete | error
    final_text: str
    iterations: int
    model: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    approvals: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tool_definitions() -> list[dict[str, Any]]:
    """Claude tool definitions built from the registry (name, description, input schema)."""
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]}
        for t in registry.list_tools()
    ]


def _api_error_message(exc: anthropic.APIError) -> str:
    if isinstance(exc, anthropic.AuthenticationError):
        return "The Claude API key was rejected"
    if isinstance(exc, anthropic.NotFoundError):
        return f"Model {settings.anthropic_model!r} was not found"
    if isinstance(exc, anthropic.RateLimitError):
        return "Claude API rate limit reached. Try again shortly"
    if isinstance(exc, anthropic.APIStatusError):
        return f"Claude API error (HTTP {exc.status_code})"
    if isinstance(exc, anthropic.APIConnectionError):
        return "Could not reach the Claude API"
    return "Claude API error"


class ClaudeOrchestrator:
    def __init__(
        self,
        db: Session,
        client: Any | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
    ) -> None:
        self.db = db
        self.model = model or settings.anthropic_model
        if not self.model:
            raise AgentConfigError("ANTHROPIC_MODEL is not set")
        if client is None:
            if not settings.anthropic_api_key:
                raise AgentConfigError("ANTHROPIC_API_KEY is not set")
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.client = client
        self.max_iterations = max_iterations or settings.agent_max_iterations
        self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.tools = tool_definitions()

    def _create(self, messages: list[dict[str, Any]]) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": MAX_TOKENS,
            "system": self.system_prompt,
            "tools": self.tools,
            "messages": messages,
            "cache_control": {"type": "ephemeral"},
        }
        if settings.anthropic_effort:
            kwargs["output_config"] = {"effort": settings.anthropic_effort}
        if settings.anthropic_fallbacks:
            return self.client.beta.messages.create(
                betas=[FALLBACK_BETA], fallbacks=settings.anthropic_fallbacks, **kwargs
            )
        return self.client.messages.create(**kwargs)

    def run(self, mission: Mission, prompt: str, on_behalf_of: uuid.UUID | None = None) -> RunResult:
        actor = agent_actor("claude", on_behalf_of=on_behalf_of)
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": f"Mission {mission.code}.\n\nRequest:\n{prompt}"}
        ]
        result = RunResult(status="max_iterations", final_text="", iterations=0, model=self.model)

        for iteration in range(1, self.max_iterations + 1):
            result.iterations = iteration
            try:
                response = self._create(messages)
            except anthropic.APIError as exc:
                result.status, result.final_text = "error", _api_error_message(exc)
                break

            texts = [b.text for b in response.content if b.type == "text"]
            if response.stop_reason == "refusal":
                result.status, result.final_text = "refused", "Claude declined this request."
                break
            if response.stop_reason == "max_tokens":
                result.status, result.final_text = "incomplete", "The reply was cut off before it finished."
                break
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if response.stop_reason != "tool_use" or not tool_uses:
                result.status, result.final_text = "completed", "\n".join(texts).strip()
                break

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in tool_uses:
                outcome = executor.execute(self.db, block.name, dict(block.input or {}), actor, mission.id)
                call = ToolCall(
                    name=block.name,
                    status=outcome.get("status", "error"),
                    approval_id=outcome.get("approval_id"),
                    tier=outcome.get("approval_tier"),
                    reason=outcome.get("reason") or outcome.get("error"),
                )
                result.tool_calls.append(call)
                if call.status == "approval_required":
                    result.approvals.append(
                        {
                            "approval_id": call.approval_id,
                            "tier": call.tier,
                            "action_type": outcome.get("action_type"),
                        }
                    )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(outcome, default=str),
                        "is_error": call.status == "error",
                    }
                )
            # All results of one turn go back in a single user message.
            messages.append({"role": "user", "content": tool_results})

            if result.approvals:
                # Enforced in code: an approval request ends the run until a human decides.
                lines = [
                    f"Waiting for approval {a['approval_id']} ({a['action_type']}, Tier {a['tier']})."
                    for a in result.approvals
                ]
                result.status = "approval_required"
                result.final_text = "\n".join([*texts, *lines]).strip()
                break
        else:
            result.final_text = result.final_text or "Stopped after the maximum number of steps."

        audit_service.record(
            self.db,
            actor,
            "agent.run",
            mission_id=mission.id,
            input_ref={"prompt": prompt, "model": self.model},
            result_ref={
                "status": result.status,
                "iterations": result.iterations,
                "tool_calls": [{"name": c.name, "status": c.status} for c in result.tool_calls],
                "approval_ids": [a["approval_id"] for a in result.approvals],
            },
            status="ok" if result.status in ("completed", "approval_required") else result.status,
        )
        self.db.commit()
        return result
