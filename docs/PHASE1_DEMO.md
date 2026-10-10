# KawTeam Phase 1 demo

Shows the approval gate end to end: a Committee Member creates a mission, the HOD confirms its limits, the Claude agent researches (demo data) and asks to contact a supplier, and nothing leaves until the right person approves. Every "sent" message is **SIMULATED**.

## People

<table border="1" cellspacing="0" cellpadding="6">
  <tr><th>Role in the script</th><th>Account</th><th>KawTeam role</th></tr>
  <tr><td>Committee Member A</td><td>chrispr@sunwaytechclub.com</td><td>Committee Member</td></tr>
  <tr><td>Committee Member B</td><td>zoeypr@sunwaytechclub.com</td><td>Committee Member</td></tr>
  <tr><td>HOD</td><td>waynehopr@sunwaytechclub.com</td><td>HOD</td></tr>
</table>

No passwords: with `DEMO_PROFILE_SWITCH=true` in `backend/.env`, tap the avatar at the top right and pick who you act as. Each browser tab keeps its own person, so you can also open one tab per person.

## Before you start (once)

Run these from the repo root in PowerShell. The network must allow outbound port 5432 (a phone hotspot works if the campus Wi-Fi blocks it), and `ANTHROPIC_API_KEY` must be set in `backend/.env`.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m scripts.check_db
python -m scripts.check_claude
alembic upgrade head
python -m scripts.seed
```

For a clean run where the first mission is `MISSION-001`, reset the **dev** database first. This drops every KawTeam table, including the audit log, so only do it on dev:

```powershell
alembic downgrade base
alembic upgrade head
python -m scripts.seed
```

Start both servers from the project folder in one window (or double-click `start.cmd`):

```powershell
npm run dev
```

Open http://localhost:3000. Ctrl+C stops both. The window says whether the database is reachable.

## Script

1. **Member A creates the mission.** Switch to A (avatar, top right). Missions → **New**. Goal "300 custom tote bags for our tech event", product "Custom tote bags", quantity 300, target 1350, hard budget 1500, min quality 4.0, deadline 25 Oct 2026, max rounds 3 → **Create**. The mission opens as `MISSION-001`, status **Awaiting HOD**.
2. **The HOD confirms the limits.** Switch to the HOD, open `MISSION-001`, press **Confirm limits**. Status becomes **Active**.
3. **Member A runs the agent.** As A, in the Agent box on `MISSION-001`, type "Find suppliers and send an enquiry to the cheapest within budget" → **Run agent**.
4. **Approval required (Tier 1).** The run summary shows `search_suppliers` then `send_approved_message · T1` and status **Approval required**. Quotes list Suppliers A, B and C marked **DEMO DATA**. Under Approvals there is a **T1 Enquiry → Supplier B** card. Messages shows it as **Awaiting approval**.
5. **A is refused, B approves.** As A, press **Approve**, give a reason, confirm: a red toast says you requested this action. As B, open Approvals (the badge shows 1), approve with a reason: toast "Approved · sent (simulated)". On the mission, the message is **Sent** with **SIMULATED**.
6. **Counteroffer goes to the HOD (Tier 2).** As A, run the agent with "Send Supplier B a counteroffer at RM1,350". A **T2 Counteroffer** card appears with the budget bar (RM1,350, target RM1,350, limit RM1,500). As B, open `MISSION-001` and try **Approve**: refused, "Only the HOD can approve Tier 2 actions". As the HOD, approve from Approvals: the counteroffer is **Sent** and **SIMULATED**.
7. **Audit log.** As the HOD, open Audit. Every step is listed with time, actor (the agent shows who it ran for), role, event, tool and status, including A's and B's refused attempts.

Extra checks you can show:

- Ask the agent for a counteroffer at RM1,600: it is refused before any approval is created (hard budget).
- Ask for an enquiry that mentions "RM1,350": it becomes a **T2 Terms message** for the HOD.
- As A, change the hard budget on the active mission (API `PATCH /missions/{id}`): it creates a **T3 Limit change** and the budget does not change until the HOD approves.

## Same script without a browser or API key

`backend/tests/test_demo_flow.py` runs steps 1 to 7 through the real HTTP API with a scripted Claude, against the `kawteam_test` schema:

```powershell
cd backend; .\.venv\Scripts\Activate.ps1; pytest tests/test_demo_flow.py -v
```

## Agent from the command line

```powershell
cd backend; .\.venv\Scripts\Activate.ps1
python -m app.agent.run --mission MISSION-001 --as chrispr@sunwaytechclub.com "Find suppliers for 300 tote bags under RM1,500 and send an enquiry to the cheapest one"
```

## Run log

<table border="1" cellspacing="0" cellpadding="6">
  <tr><th>Date</th><th>How</th><th>Result</th></tr>
  <tr><td>2026-10-10</td><td>Live run</td><td>Not run yet: this network blocks outbound port 5432 and there is no Claude API key yet</td></tr>
  <tr><td>2026-10-10</td><td><code>pytest tests/test_demo_flow.py</code></td><td>Not run yet: same database block</td></tr>
</table>
