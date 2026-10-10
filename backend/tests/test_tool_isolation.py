"""Kickoff working rule 8: tools stay framework-agnostic. Needs no database."""

import ast
from pathlib import Path

import app.tools  # noqa: F401  (registers every tool)
from app.tools.registry import list_tools

TOOLS_DIR = Path(__file__).resolve().parent.parent / "app" / "tools"
FORBIDDEN = ("anthropic", "fastapi", "starlette", "mcp", "workbuddy")


def test_tools_import_no_framework_code():
    offenders = []
    for path in TOOLS_DIR.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            offenders += [f"{path.name}: {n}" for n in names if n.split(".")[0].lower() in FORBIDDEN]
    assert offenders == []


def test_registry_lists_every_phase1_tool_with_a_schema():
    tools = {t["name"]: t for t in list_tools()}
    assert set(tools) == {
        "read_mission_state",
        "update_mission_state",
        "check_permission",
        "request_approval",
        "get_approval_status",
        "send_approved_message",
        "search_suppliers",
        "prepare_counteroffer",
    }
    for tool in tools.values():
        assert tool["description"]
        assert tool["input_schema"]["type"] == "object"
