from kawteam.mcp.server import kawteam_health


def test_health_identifies_a_real_tool_invocation():
    result = kawteam_health("phase-zero-probe")
    assert result["request_id"] == "phase-zero-probe"
    assert result["product"] == "KawTeam"
    assert result["status"] == "ok"
    assert result["capabilities"] == ["health"]
