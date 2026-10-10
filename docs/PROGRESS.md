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
