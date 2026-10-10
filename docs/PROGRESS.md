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
- `GET /health` now returns `{"status": "ok", "database": "ok"}` or `"degraded"` / `"unreachable"`. Connections time out after 10 s per address instead of hanging.
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
