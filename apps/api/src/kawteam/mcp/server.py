from typing import TypedDict

from mcp.server import MCPServer

mcp = MCPServer("KawTeam")


class HealthResult(TypedDict):
    request_id: str
    product: str
    status: str
    capabilities: list[str]
    phase: str


@mcp.tool(structured_output=True)
def kawteam_health(request_id: str) -> HealthResult:
    """Verify a KawTeam tool invocation. Does not research, send messages, or select vendors."""
    return {
        "request_id": request_id,
        "product": "KawTeam",
        "status": "ok",
        "capabilities": ["health"],
        "phase": "frontend-prototype",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
