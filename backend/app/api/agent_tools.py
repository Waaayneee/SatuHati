"""Agent-token endpoints. Phase 7 points the WorkBuddy MCP server here."""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.auth.dependencies import require_agent
from app.db import get_db
from app.schemas.misc import AgentToolCall
from app.tools import executor, registry

router = APIRouter(prefix="/agent/tools", tags=["agent"])


@router.get("")
def list_agent_tools(actor: Actor = Depends(require_agent)) -> list[dict[str, Any]]:
    return registry.list_tools()


@router.post("/{name}")
def call_tool(
    name: str, body: AgentToolCall, actor: Actor = Depends(require_agent), db: Session = Depends(get_db)
) -> JSONResponse:
    result = executor.execute(db, name, body.args, actor, body.mission_id)
    return JSONResponse(status_code=404 if registry.get_tool(name) is None else 200, content=result)
