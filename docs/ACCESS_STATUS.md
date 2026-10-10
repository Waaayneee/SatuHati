# Access status

Last checked 2026-10-10. Rows marked **HUMAN** need Wayne to confirm.

<table border="1" cellspacing="0" cellpadding="6">
  <thead>
    <tr><th>Service</th><th>Purpose</th><th>Needed in</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr><td>Supabase Auth (project KawTeam)</td><td>Login, JWT signing</td><td>Phase 1</td><td>Working. JWKS endpoint serves an ES256 key. 3 confirmed users exist (1 HOD, 2 Committee)</td></tr>
    <tr><td>Supabase Postgres, dev (<code>public</code> schema)</td><td>Database</td><td>Phase 1</td><td>Credentials set. <b>Blocked on the current network</b>: outbound TCP 5432/6543 is firewalled. Works from a network that allows Postgres (e.g. phone hotspot)</td></tr>
    <tr><td>Supabase Postgres, test (<code>kawteam_test</code> schema, same project)</td><td>pytest</td><td>Phase 1</td><td>Same as dev</td></tr>
    <tr><td>Anthropic Claude API</td><td>Agent orchestrator</td><td>Phase 1</td><td><b>HUMAN</b>. No API key yet. Model chosen: <code>claude-sonnet-5-5</code></td></tr>
    <tr><td>Brave Search or Tavily</td><td>Supplier discovery</td><td>Phase 3</td><td><b>HUMAN</b>. Not requested yet</td></tr>
    <tr><td>Gmail API or Microsoft Graph</td><td>Email</td><td>Phase 4</td><td><b>HUMAN</b>. Not requested yet</td></tr>
    <tr><td>Google Calendar API or Microsoft Graph</td><td>Meetings</td><td>Phase 9</td><td><b>HUMAN</b>. Not requested yet</td></tr>
    <tr><td>Python PDF library</td><td>Reports</td><td>Phase 6</td><td>Not installed yet (open-source, no account needed; pick in Phase 6)</td></tr>
    <tr><td>WorkBuddy account (sign-in check only)</td><td>Orchestrator</td><td>Phase 7</td><td><b>HUMAN</b>. One sign-in to confirm the hackathon account exists</td></tr>
  </tbody>
</table>
