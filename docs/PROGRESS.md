# KawTeam (StakeMate AI) build progress

Kickoff: `docs/StakeMate_Claude_Code_Kickoff_Phase_0_1.md`. Blueprint: `docs/StakeMate_AI_Complete_Hackathon_Blueprint_1.md`.

## Decisions from Wayne (2026-10-10)

| Topic | Decision |
|---|---|
| Product name in UI and agent prompt | KawTeam (code and table names keep the kickoff wording) |
| HOD | waynehopr@sunwaytechclub.com |
| Committee Members | chrispr@sunwaytechclub.com, zoeypr@sunwaytechclub.com |
| Test database | Isolated `kawteam_test` schema in the same Supabase project, rolled back after every test |
| Claude model | `claude-sonnet-5-5` (from `ANTHROPIC_MODEL`) |
| JWT verification | `jwks` (project signs tokens with an ES256 key) |

## Phase 0

### Step 0.1. Prerequisites

- Python 3.12 (via `py -3.12`; 3.14 is also installed but not used), Node v24.18.0, npm 11.16.0, git 2.55.0. All meet the kickoff minimums.

### Step 0.2. Repository

- Git repo already existed (`main`). Work happens on branch `phase-0-1`.
- `.gitignore` covers `.venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`, `.next/`, `.env`, `.env.local`, `*.local`. Only `.env.example` and `.env.local.example` can be committed.

### Step 0.3. Backend scaffold

- `backend/.venv` on Python 3.12.6. Packages from kickoff Section 4 installed and pinned in `backend/requirements.txt`.
- Note: `anthropic` 1.x uses `httpx2` internally. The `httpx` package stays for FastAPI's test client.
- Check: `uvicorn app.main:app --port 8000`, then `GET /health` returned `{"status":"ok"}`.

### Step 0.4. Frontend scaffold

- `npx create-next-app@16.4.0 frontend` with TypeScript, Tailwind CSS v4, ESLint, App Router, `src/` dir. Next 16.4 ships with Cache Components and Partial Prefetching on.
- Added `@supabase/supabase-js@2.117.3` and `@supabase/ssr@0.12.7`.
- `frontend/.gitignore` now allows `.env.local.example`.
- Check: `npm run dev`, then `GET /` returned 200.

### Steps 0.5 and 0.6. Supabase and Claude settings (HUMAN)

- `backend/.env` and `frontend/.env.local` written from the values Wayne gave (both gitignored, checked with `git check-ignore`).
- Frontend uses the publishable key (`sb_publishable_...`) as `NEXT_PUBLIC_SUPABASE_ANON_KEY`. No secret key anywhere in the frontend.
- `SUPABASE_JWT_MODE=jwks`: the project's JWKS endpoint serves one ES256 key with kid `1d3a1dd0-...`.
- `AGENT_SERVICE_TOKEN` generated with `secrets.token_urlsafe(48)` and written straight into `backend/.env` (never printed).
- Extra optional settings: `TEST_DATABASE_SCHEMA=kawteam_test`, `ANTHROPIC_EFFORT=medium`, `ANTHROPIC_FALLBACKS=default` (server-side refusal fallback for Sonnet 5.5).
- Open: `ANTHROPIC_API_KEY` is still empty. Wayne has no key yet.

### Step 0.7. Smoke checks

- `python -m scripts.check_db` runs `SELECT 1` on both URLs. `python -m scripts.check_claude` prints only the model and first reply line.
- `GET /health` now returns `{"status": "ok", "database": "ok"}` or `"degraded"` / `"unreachable"`. Connections time out after 5 s per address instead of hanging (was 10 s, lowered on 2026-10-10).
- Result on 2026-10-10: **both DB checks fail** because this network blocks outbound TCP 5432 and 6543 (`portquiz.net:5432` times out, `portquiz.net:443` works, also outside the sandbox). Claude check: key not set.

### Step 0.8. Access status

- `docs/ACCESS_STATUS.md` created with a fully bordered table. HUMAN rows: Claude key, search, email, calendar, WorkBuddy sign-in.

### Phase 0 exit status

| Criterion | Status |
|---|---|
| `/health` and Next.js home page load | Done |
| Both DB connections pass | Blocked by network firewall on port 5432 |
| Claude test call passes | Waiting for API key |
| `ACCESS_STATUS.md` filled | Done, HUMAN rows open |
| One commit per step, no `.env` tracked | Done |

## Phase 1

### Step 1.1. Data model and migrations

- SQLAlchemy models in `backend/app/models/` for all 12 tables in the kickoff, UUID keys, `created_at`/`updated_at`, `jsonb` for flexible fields. `audit_log` uses a single `at` timestamp because it is never updated.
- `quotations.verification_state` uses the Postgres enum `verification_state` with the nine Section 11 states.
- Extra columns needed by the flows: `missions.notes`, `missions.limits_confirmed_by/at`, `messages.proposed_total_myr`, `messages.sent_at`, `approvals.requested_on_behalf_of` (the person who ran the agent, so they cannot approve its Tier 1 request), `approvals.decided_at`, `approvals.execution_result`.
- `audit_log.mission_id` has no foreign key on purpose, so an audit row can always be written.
- Migration `alembic/versions/0001_phase1_initial.py` (create-table code rendered from the models, so they match). Hardening: append-only trigger on `audit_log` (blocks UPDATE, DELETE and TRUNCATE), RLS enabled with no policies on every table including `alembic_version`. Mission codes come from sequence `mission_code_seq`.
- `alembic -x target=test upgrade head` migrates the `kawteam_test` schema.
- Checks: `alembic upgrade head --sql` renders cleanly offline (12 tables, enum, sequence, triggers, RLS). Live `alembic upgrade head` on both targets and `python -m scripts.check_audit_append_only` are **pending the network fix**.

### Step 1.2. Seed data

- `app/services/seed_service.py` holds the 12 approval policies from the kickoff table (Tier 0 roles stored as `["any"]`, Tier 1 as `["committee_member", "hod"]` with the not-requester note, Tier 2/3 as `["hod"]`).
- `python -m scripts.seed` looks the three users up in Supabase `auth.users` through the database connection (no secret key needed), makes each seeded user hold exactly its configured role, writes `user.created` / `role.assigned` / `role.removed` audit rows, and upserts the policies. Safe to re-run.
- Check: imports compile. Live run is **pending the network fix**.

### Step 1.3. Authentication and actors

- `app/auth/actor.py`: framework-agnostic `Actor` (`type`, `id`, `roles`, plus `on_behalf_of` for agent runs started by a person). Agents never carry roles.
- `app/auth/tokens.py`: verifies Supabase access tokens via JWKS (ES256/RS256/EdDSA only) or the legacy secret (HS256), audience `authenticated`, issuer `<SUPABASE_URL>/auth/v1`, `role = authenticated`, 30 s leeway.
- `app/auth/dependencies.py`: `get_current_actor` maps a Bearer token to a `users` row and its roles (no role or unknown user gives 403). `X-Agent-Token` equal to `AGENT_SERVICE_TOKEN` (compared with `secrets.compare_digest`) becomes `agent:claude` with no roles. An empty configured token never authenticates.
- CORS allows only `FRONTEND_ORIGIN`. Domain errors map to 404/403/409/422.
- Check: local ES256 key test. Valid token accepted; wrong audience, wrong issuer, expired, anon role and forged signature all rejected. Full HTTP tests come in Step 1.10.

### Step 1.4. Audit service

- `audit_service.record(...)` inserts one row in the caller's transaction. `sanitize()` redacts any key that looks like a token, secret, password, API key, authorization or cookie, and replaces message bodies and any string over 500 chars with `[omitted: N chars]` (bodies are referenced by `message_id`).
- `audited_refusals(...)` context manager: on a refusal it rolls back the partial work, records the refusal, commits the audit row, then re-raises.
- Check: sanitizer output verified by hand (`api_key`, `access_token` redacted; `body` and a 600-char string omitted).

### Step 1.5. Approval service

- `app/services/approval_service.py`: `classify`, `check_permission`, `request`, `decide`, `verify_and_consume`, plus `expire_stale`.
- Unknown action types are Tier 3 (HOD). Tier 2 and 3 eligible roles are forced to `["hod"]` in code even if a policy row says otherwise.
- Safety bump: a Tier 1 snapshot with a commercial key (`proposed_total_myr`, `price`, `budget`, `payment_terms`, `quantity_tier`...) or a body containing a currency amount (`RM1,350`, `RM 1,350`, `$300`, `300 MYR`) or budget / payment-term / deposit / discount / quantity-tier wording becomes `send_terms_message` at Tier 2. "100% cotton" and plain quantities do not trigger it.
- `request`: external actions need an `active` mission (HOD-confirmed limits); any `proposed_total_myr` above the hard budget is refused; opted-out stakeholders are refused; `content_hash` = SHA-256 of canonical JSON (sorted keys, no spaces); stored snapshot is exactly the hashed form; `expires_at = now + APPROVAL_TTL_HOURS`; audited.
- `decide`: agents always refused; reason required; one approval per call with a row lock; expired approvals become `expired`; Tier 1 needs a committee member who is not the requester (the person who started the agent run counts as the requester) or the HOD; Tier 2/3 need the HOD. Refusals are audited. On approval it issues `secrets.token_urlsafe(32)`, stores only the SHA-256, and immediately runs the snapshot through `executor.run_approved`. The token never leaves the function.
- `verify_and_consume`: re-checks status, expiry, token hash, content hash, hard budget and opt-out against current data. Failures mark the approval `failed`, refuse the linked message, audit and commit. A second use of a token is refused without changing the `executed` status.
- `app/services/mission_service.py`: create (Committee -> `awaiting_hod_confirmation`; HOD may create and confirm), confirm limits (HOD), edit. Limit fields (`product`, `quantity`, `hard_budget_myr`, `minimum_quality`, `delivery_deadline`, `max_rounds`, `approval_policy`) on an active mission become a Tier 3 `change_mission_limits` approval and do not change until the HOD approves; the approval also re-checks that nothing changed in between. The agent may only write `notes`.
- Check: classifier spot checks (see above) and canonical hash order-independence. Behaviour tests in Step 1.10.

### Step 1.6. Tool registry and tool executor

- `app/tools/registry.py`: `@tool(name, description, action_type, input_model, output_model)` and `list_tools()` (name, description, action type, input JSON Schema with `additionalProperties: false`). `@approved_action(...)` registers what runs after approval.
- `app/tools/executor.py`: `execute(db, tool_name, args, actor, mission_id)` validates input, checks permission, runs Tier 0 tools in a savepoint and audits them; gated tools (`send_approved_message`, `request_approval`) never run, they create a pending approval and return `{"status": "approval_required", "approval_id", "tier", ...}`. `run_approved` is only called from `decide`, calls `verify_and_consume`, then performs the action.
- Tools: `read_mission_state`, `update_mission_state`, `check_permission`, `request_approval`, `get_approval_status`, `send_approved_message` (workflow_tools) and `search_suppliers`, `prepare_counteroffer` (demo_tools, Section 17 data and logic, every result `data_source: "demo"`). Demo suppliers are stored as stakeholders with simulated evidence and `research_result` quotations so later tools can reference them.
- `send_approved_message` creates a `pending_approval` message plus the approval. After approval the message becomes `sent` with `is_simulated = true` (and a negotiation round for counteroffers). Counteroffers must carry `proposed_total_myr` and respect `max_rounds`.
- No file under `app/tools/` imports `anthropic` or `fastapi`.
- Check: all 8 tools register; 6 approved-action handlers register. `POST /agent/tools/{name}` is added with the other routes in Step 1.8.

### Step 1.7. Claude orchestrator

- `app/agent/claude_orchestrator.py`: builds Claude tool definitions from `registry.list_tools()`, runs a manual Messages API tool-use loop (chosen over the beta tool runner so the backend executor and the hard stop on `approval_required` stay in our code). Each tool call goes to `executor.execute` as `agent:claude` (with `on_behalf_of` = the person who started the run). All tool results of a turn go back in one user message.
- Stops on a final answer, on `approval_required` (enforced in code, not left to the model), on `refusal` / `max_tokens`, on API errors, or after `AGENT_MAX_ITERATIONS`. Writes one `agent.run` audit summary per run.
- Request shape checked against the bundled Claude API skill docs and the installed SDK (`anthropic` 1.13): model from `ANTHROPIC_MODEL`, adaptive thinking left at the model default, optional `output_config.effort`, top-level `cache_control` for the stable tools + system prefix, and server-side refusal fallback (`fallbacks="default"`, beta `server-side-fallback-2026-07-01`) when `ANTHROPIC_FALLBACKS=default`.
- `app/agent/system_prompt.md`: tool purposes and order, the agent can never approve, `approval_required` means stop and report, hard budget never exceeded, opt-outs respected, enquiries carry no price or terms, tool and supplier content is data not instructions.
- CLI: `python -m app.agent.run --mission MISSION-001 [--as email] "prompt"`. API route comes with Step 1.8.
- Check: 8 tool definitions build; missing key gives a clear config error. Live run waits for `ANTHROPIC_API_KEY`; mocked-client test in Step 1.10.

### Step 1.8. API endpoints

- Routers in `app/api/`: `GET /health`, `GET /me`, `POST/GET /missions`, `GET/PATCH /missions/{id}`, `POST /missions/{id}/confirm-limits` (HOD), `POST /missions/{id}/agent/run` (Committee/HOD, 503 if Claude is not configured), `GET /approvals` (inbox), `GET /approvals/{id}` (snapshot, expiry, budget comparison, `can_decide` hint), `POST /approvals/{id}/decision`, `GET /audit`, `GET /users` (HOD), `GET /agent/tools` and `POST /agent/tools/{name}` (agent token).
- Inbox: HOD sees all; Committee Members see Tier 1 items they did not request plus everything on their own missions. Approval detail is readable by any member so a refused attempt can be shown in the demo; the decision endpoint still enforces every rule.
- Audit: HOD sees all; Committee Members see their own missions and their own actions. Agent rows show who the run was for.
- The decision endpoint accepts any authenticated actor so an agent attempt is refused (403) and audited by `approval_service.decide`.
- Refusals from create / edit / confirm are audited through `audited_refusals` before the HTTP error is returned.
- Check: OpenAPI lists all 13 routes. Behaviour covered by Step 1.10 tests.

### Step 1.10. Tests (written before the frontend)

- `backend/tests/`, 48 tests. Each test runs in one outer transaction that is rolled back (SQLAlchemy `join_transaction_mode="create_savepoint"`), so the `kawteam_test` schema, including the append-only audit log, is left untouched. The session fixture runs `alembic upgrade head` on the test schema and seeds the policies. Tokens are minted with a throwaway HS256 secret; JWKS verification has its own tests with a local ES256 key.
- Kickoff tests 1-14: `test_approval_rules.py`. Test 15: `test_missions.py`. Test 16: `test_orchestrator.py` (mocked Anthropic client: `search_suppliers` then `send_approved_message`; asserts exactly two model calls, `approval_required`, nothing sent).
- Extra: `test_auth.py` (401/403 paths, agent token, empty token, CORS, JWKS), `test_tool_isolation.py` (no `anthropic`/`fastapi`/`mcp` imports under `app/tools/`), `test_demo_flow.py` (the whole PHASE1_DEMO script through HTTP with a scripted Claude).
- Fix found while writing tests: `audit_log.at` now defaults to `clock_timestamp()` instead of `now()`, so rows written in one transaction keep their real order.
- Check: 9 database-free tests pass. The 39 database tests are **pending the network fix** (port 5432 blocked).

### Step 1.9. Frontend pages

- Next.js 16.4 App Router, Tailwind v4, Apple-style design (system font with size-specific tracking, translucent sticky nav, press feedback on pointer-down, bottom sheet that enters and leaves the same way, light and dark themes, reduced-motion / reduced-transparency / more-contrast support). Very little text on screen.
- `/login` (Supabase email + password), shared shell with role badge (HOD / Committee) and nav with a pending-approvals count, `/missions` (bordered table + New mission sheet; HOD can confirm on create), `/missions/[id]` (fact tiles, Confirm limits for the HOD, agent prompt + Run agent with the run summary, this mission's approvals, messages with a **SIMULATED** label, demo quotes, activity from the audit log), `/approvals` (Pending / All; tier badge, requester, live expiry countdown, snapshot preview, budget bar vs target and hard budget, approve or reject with a required reason), `/audit`, `/settings` (HOD only, read-only users and roles).
- Every table has a visible border on every cell (`.grid-table`).
- Every request sends the Supabase access token as a Bearer header. The frontend never writes to the database and never decides who may approve: Approve / Reject show on every pending item and the backend's 403 reason is shown when someone is not allowed (needed for the demo's "Member A is refused" step).
- `/missions/[id]` reads its param inside a `<Suspense>` boundary (required by Cache Components). Time-dependent values (countdowns) come from a shared client clock that returns null during server render.
- Backend tweak: approval summaries now include the mission's current hard budget and target for the budget bar.
- `.claude/launch.json` added with `frontend` and `backend` dev-server entries.
- Checks: `npm run lint` clean, `tsc --noEmit` clean, `npm run build` passes. Visual check in the browser at desktop and 375 px, light and dark, using a temporary fixture page (deleted). Signed-out visits redirect to `/login`. A live signed-in check needs the database (network) and the users' passwords.

### Step 1.11. Phase 1 demo script

- `docs/PHASE1_DEMO.md`: setup commands, optional dev reset for a clean `MISSION-001`, the 7 demo steps with what each screen should show, extra checks (hard budget refusal, RM bump to Tier 2, Tier 3 limit change), the scripted-Claude pytest equivalent, and the CLI.
- Self-review of the database code paths while the tests cannot run: tests now look rows up by `uuid.UUID`, and only pass bind parameters to statements that use them.
- Not run yet (database blocked, no Claude key). Run log in the demo file.

## Phase 1 exit status

<table border="1" cellspacing="0" cellpadding="6">
  <tr><th>Criterion</th><th>Status</th></tr>
  <tr><td>Claude orchestrator calls the demo tools through the executor</td><td>Built; covered by mocked-client tests. Live run needs the API key</td></tr>
  <tr><td>A Committee Member can create a mission</td><td>Built (API + UI); test 15 written</td></tr>
  <tr><td>Simulated external action blocked until the correct role approves</td><td>Built; tests 2-13 written</td></tr>
  <tr><td>Audit log records every step</td><td>Built; append-only trigger; demo-flow test checks the events</td></tr>
  <tr><td>All Step 1.10 tests pass</td><td>9 database-free tests pass; 39 database tests waiting for port 5432</td></tr>
  <tr><td><code>npm run build</code> passes</td><td>Done</td></tr>
</table>

## Still to do once the network allows Postgres (Wayne's laptop on a hotspot)

```powershell
cd backend; .\.venv\Scripts\Activate.ps1
python -m scripts.check_db
alembic upgrade head
alembic -x target=test upgrade head
python -m scripts.check_audit_append_only
python -m scripts.seed
pytest
```

Then, with `ANTHROPIC_API_KEY` in `backend/.env`: `python -m scripts.check_claude` and the live demo in `docs/PHASE1_DEMO.md`.

## Known gaps

- Live database checks, seed, and the 39 database tests have not run (network). The Claude live call has not run (no key).
- No UI form for editing mission fields or limits yet; `PATCH /missions/{id}` exists and is tested.
- Expired approvals are marked lazily (when the inbox loads or someone decides), not by a scheduler.
- `POST /missions/{id}/agent/run` is synchronous and can take tens of seconds.
- The HOD confirms limits directly (audited as `confirm_mission_limits`, Tier 3) rather than through an approval record, since the HOD is the approver.
- A `request_approval` snapshot containing exponent-style floats (e.g. `1e100`) changes form in JSONB and would fail its hash check at execution. This fails closed (refused), never open.

## Open questions for Wayne

- Committee Members can list and open every mission; the audit log shows them only their own missions and actions. Keep it this way?
- The kickoff lets the HOD approve any Tier 1 item, including one the HOD requested. Keep it?

## Ready for Phase 2

- Goal extraction plugs in before the loop in `ClaudeOrchestrator.run` (`backend/app/agent/claude_orchestrator.py`): add a `goal_manager` service plus a Tier 0 tool (for example `extract_goal`) that turns the user's request into mission fields through `mission_service.create_mission` / `update_mission`, and a clarification result when required fields are missing. Limits it proposes still need HOD confirmation; the gate does not change.
- Phase 3 replaces `demo_tools.search_suppliers` with real search (Brave or Tavily) that writes `evidence_sources` with `is_simulated = false`, and adds `verify_supplier`, `compare_offers`, `rank_candidates` to the same registry. `prepare_counteroffer` moves to a negotiation engine.
- Phase 4 swaps the body of `perform_send_message` (`backend/app/tools/workflow_tools.py`) for real email. The approval, token and audit path stays exactly as is.
- Phase 7 (WorkBuddy MCP) points at `GET /agent/tools` and `POST /agent/tools/{name}`, which are already built and tested.

## UI update (2026-10-10): profile switching, palette, light by default

Wayne asked for no login page, a profile switcher, light mode by default, and the teal and lime palette.

- **No sign-in.** `/login` and the Supabase browser client are gone (`@supabase/ssr` and `@supabase/supabase-js` uninstalled). The avatar at the top right opens a menu that lists every seeded person (HOD first) and switches between them with no password. Each tab keeps its own person in memory; localStorage only remembers the last choice. A switch remounts the app so every page reloads its data as the new person.
- **Backend.** New setting `DEMO_PROFILE_SWITCH` (default `false`, set to `true` in Wayne's local `backend/.env`). When on, `GET /profiles` (no auth) lists active people with a role, and an `X-Profile-Id` header acts as that person through the same user and role checks as a token (`_registered_user` in `app/auth/dependencies.py`). Bearer tokens and the agent token still work and take priority. When off, `/profiles` is 404 and the header is 401. CORS allows the header.
- **Trade-off.** With switching on, anyone who can reach the backend can act as any person, including approving as someone else. Approval rules still apply to the person chosen, but they no longer prove who is at the keyboard. Keep it off for anything other people can reach.
- **Look.** Palette from Wayne's brief: deep teal `#00545f`, lime `#d6fb00`, pale lime `#ecffb6`. Light is the default whatever the system setting. Dark is a choice in the profile menu, applied before first paint by an inline script (`lib/theme.ts`). Primary buttons and the active nav item are teal with pale-lime text (lime with teal text in dark mode). HOD avatars are teal and Committee avatars are lime.
- **Next.js.** `experimental.instantInsights.validationLevel = "manual-warning"`. Pages wait for the chosen profile in the browser, so the default check flagged every page as a dev-only "Insight".
- **Checks.** `npm run lint`, `tsc --noEmit` and `npm run build` pass. The 9 database-free tests pass. New `tests/test_profiles.py` (6 tests) still needs port 5432; its logic was checked with a stubbed database session. Browser check against a temporary mock API (deleted) at desktop and 375 px, light and dark: switching HOD to Committee, a reload keeping the profile and theme, outside click and Escape closing the menu, the "server unreachable" screen and its Try again.

### One-window start and database errors (2026-10-10)

- `npm run dev` in the project folder (root `package.json`, no packages) or double-clicking `start.cmd` runs `scripts/dev.mjs`. It starts the backend (uvicorn `--reload`, port 8000) and the frontend (Next.js, port 3000) in one window with `[api]` and `[web]` labels, then says whether the database is reachable. Ctrl+C, or either server exiting, stops both (`taskkill /T` on Windows, so no worker is left on the port). It refuses to start while 3000 or 8000 is in use.
- A database that can't be reached is now a 503 "Can't reach the database" with CORS headers (handler for `sqlalchemy.exc.OperationalError` in `app/main.py`). Before, the 500 had no CORS headers, so the browser showed only "Failed to fetch". The app shows that message with a hotspot hint and Try again. A "Connecting…" line appears if loading takes over 3 s.
- Checked: the launcher refuses busy ports. A copy on spare ports started both servers and reported the unreachable database. Both crash and abrupt-kill paths left no process behind. The full start on 3000 was not run while Wayne's own frontend still held the port.
- Follow-up: running `npm run dev` inside `frontend/` started only Next.js, so every API call failed. A browser extension that wraps `fetch` then re-threw each failure as an unhandled rejection in the Next overlay. `frontend`'s `dev` script now runs the same launcher (`dev:web` is plain `next dev`, used by `.claude/launch.json`). The launcher starts the frontend only after the backend accepts connections on port 8000. Checked live: backend then frontend start in order, the page shows the database message, and the dev log has no "Failed to fetch".
