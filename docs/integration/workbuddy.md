# KawTeam — Phase 0 connection status

The local Python MCP server exposes `kawteam_health` via stdio. An integration test starts a real
MCP process, initialises a client, discovers the tool, and calls it with a correlation ID.

**WorkBuddy account/client connection remains unverified.** No WorkBuddy process was found running
and no usable native application surface is available in this session. Credits do not establish API access.
The frontend is browser-local fixture data and is not yet connected to WorkBuddy.

To connect when the team's client is available:

1. Open WorkBuddy's MCP settings.
2. Use `workbuddy/kawteam/mcp.example.json`, replacing both absolute project paths.
3. Start the connection and ask: “Call kawteam_health with request_id kawteam-workbuddy-check.”
4. Confirm the returned request ID and tool event in the actual client.
5. Record that proof here. Do not substitute the SDK test for proof of WorkBuddy orchestration.

Official reference: https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide
