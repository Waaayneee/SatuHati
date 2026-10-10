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
