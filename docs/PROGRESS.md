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
