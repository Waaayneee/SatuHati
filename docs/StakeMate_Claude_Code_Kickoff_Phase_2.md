# StakeMate AI (KawTeam). Claude Code Kickoff for Phase 2

> Companion to `docs/StakeMate_AI_Complete_Hackathon_Blueprint_1.md` (the blueprint) and the finished `docs/StakeMate_Claude_Code_Kickoff_Phase_0_1.md` (the Phase 0 and 1 kickoff). The blueprint is the source of truth for the product. This file narrows Phase 2 of blueprint Section 23 to exactly what Claude Code should build now, on top of the code that already exists in this repository.

---

## How Wayne uses this file

1. Save this file as `docs/StakeMate_Claude_Code_Kickoff_Phase_2.md` in the `AiDormathon 26` folder.
2. Open the folder in Claude Code and paste this prompt.

```text
Read docs/StakeMate_Claude_Code_Kickoff_Phase_2.md fully, then docs/PROGRESS.md, then the
blueprint sections it references (6, 9 B3, 10 A, 11, 14, 22, and 23 Phase 2).
Follow the working rules in Section 2. Start at Step 2.0. Stop and wait for me at every
step marked HUMAN.
```

Everything below this line is written for Claude Code.

---

## 1. Your mission

Build **Phase 2 (goal understanding and agent orchestration)** of StakeMate AI, as defined in blueprint Section 23.

At the end of Phase 2 the following must be true.

- A Committee Member types the Section 14 demo request into the **New mission** sheet and gets back a structured draft mission with product, quantity, specifications, hard budget, deadline, location, and suggested defaults, each labelled with where it came from.
- The clarification engine asks **only** for information that is missing, invalid, or too uncertain to act on. For the Section 14 request it asks at most one question.
- The user answers inline, reviews the fields, and submits. The mission moves to `awaiting_hod_confirmation` with a stored **task plan** (research, compare, enquire, negotiate, verify, report, commit) that has explicit dependencies.
- The Claude orchestrator reads the plan, works only on tasks whose dependencies are done, updates task status as it goes, and stops cleanly when it is waiting on a human.
- Out-of-order actions (for example an enquiry before any research) are **refused by the backend**, not just discouraged by the prompt.
- Every extraction, question, answer, submission, and task change is in the audit log.

## 2. Working rules

All 13 working rules from the Phase 0 and 1 kickoff (Section 2 of that file) still apply. The most important ones are repeated here, followed by the new Phase 2 rules.

1. Work through the numbered steps in order. After each step run its check, show the result, update `docs/PROGRESS.md`, and commit, for example `phase2: step 2.4 clarification engine`.
2. Stop at every **HUMAN** step and wait for Wayne.
3. Windows and PowerShell. Activate the venv with `.\.venv\Scripts\Activate.ps1` from `backend`.
4. **No WorkBuddy or MCP work.** That is Phase 7.
5. **No real external actions.** Sending still means a simulated message row.
6. The **backend is the only enforcer** of permissions, approvals, and task dependencies. The frontend never decides.
7. No secrets in code, logs, or commits.
8. Nothing under `backend/app/tools/` may import `anthropic`, `fastapi`, or anything WorkBuddy related. `test_tool_isolation.py` must keep passing.
9. Ask Wayne before adding any dependency not listed in Section 4.
10. Check current official docs (Context7 if available) for the Anthropic Python SDK structured output feature before writing Step 2.3.
11. If this file conflicts with the blueprint or with a decision recorded in `docs/PROGRESS.md`, stop and ask Wayne.

**New for Phase 2**

12. **The model proposes, the code decides.** Claude only extracts candidate values. Every value is validated in Python (types, ranges, dates, currency, evidence). Which questions get asked, which fields are required, and when a mission may be submitted are decided by deterministic code, never by the model.
13. **The agent never creates, submits, or confirms a mission.** Intake is a user action (blueprint Section 22.3). The agent identity gets 403 on every intake endpoint, and no registry tool can create or submit a mission.
14. **Claude only, no fallback parser.** If `ANTHROPIC_API_KEY` is not set, intake returns HTTP 503 with a clear message and saves nothing. Tests use a mocked Anthropic client.
15. **Every Phase 1 test must still pass** after every step. Phase 2 may not weaken any approval rule.
16. Product name in the UI and agent prompts stays **KawTeam**. Code and table names keep the StakeMate wording.

## 3. Context you need

### 3.1 What already exists (from `docs/PROGRESS.md`)

| Area | State at the start of Phase 2 |
|---|---|
| Database | 12 tables, migration `0001_phase1_initial.py`, append-only `audit_log`, RLS with no policies on every table |
| Missions | `mission_service.create_mission`, `confirm_limits`, `update_mission`, `apply_limit_changes`. `LIMIT_FIELDS` change on an active mission becomes a Tier 3 approval |
| Approvals | `approval_service` with tiers, safety bump, single-use tokens, `decide` runs `executor.run_approved` |
| Tools | `read_mission_state`, `update_mission_state`, `check_permission`, `request_approval`, `get_approval_status`, `send_approved_message`, `search_suppliers` (demo), `prepare_counteroffer` (demo) |
| Agent | `ClaudeOrchestrator.run(mission, prompt, on_behalf_of)` with a manual tool-use loop and a code-enforced stop on `approval_required` |
| Frontend | Next.js 16.4, Tailwind v4, Apple-style UI, `New mission` bottom sheet in `/missions`, `/missions/[id]`, `/approvals`, `/audit`, `/settings` |
| Tests | 48 tests in `backend/tests/` |

`PROGRESS.md` "Ready for Phase 2" says goal extraction plugs in before the loop in `ClaudeOrchestrator.run`. This kickoff refines that. Extraction is a **separate service called by an intake API**, not a step inside the agent loop, because the agent may not create missions. The orchestrator change in Phase 2 is about reading and following the task plan.

### 3.2 The demo request (blueprint Section 14)

> I'm organising a technology event for 200 students. I need 300 custom tote bags within RM1,500, delivered before 25 October. Find the best suppliers, compare their quality, negotiate for a better price, and present the best available deal for my approval.

Expected extraction on 10 October 2026, with `DEFAULT_DELIVERY_LOCATION` blank.

| Field | Value | Source | Asked? |
|---|---|---|---|
| `product` | custom tote bags | stated | No |
| `quantity` | 300 | stated | No |
| `specifications` | `["custom printed"]` | stated | No |
| `hard_budget_myr` | 1500 | stated ("within RM1,500") | No |
| `delivery_deadline` | 2026-10-25 | inferred (year assumed, next upcoming date) | No |
| `location` | missing | missing | **Yes, the only question** |
| `target_total_myr` | 1350 | default (`DEFAULT_TARGET_RATIO` of the hard budget, rounded down to RM10) | No, shown for review |
| `minimum_quality` | 4.0 | default | No, shown for review |
| `max_rounds` | 3 | default | No, shown for review |
| `event_context` | technology event, 200 students | stated | No (context only, not a limit) |

Note that 200 students is **not** the quantity. The extraction must keep event context separate from the order quantity. Note also that "delivered before 25 October" sets the deadline to 25 October and the evidence quote must contain "25 October".

### 3.3 Field provenance

Every extracted field carries one provenance record.

| Source | Meaning | UI chip |
|---|---|---|
| `stated` | The user wrote it, and the evidence quote appears verbatim in the goal text | Stated |
| `inferred` | Derived from the text with an assumption (for example the year of a date) | Inferred |
| `default` | Filled from a configured default because the text says nothing | Default |
| `answered` | The user gave it in reply to a clarifying question | You answered |
| `edited` | The user changed it by hand in the review form | Edited |
| `missing` | No value | Missing |

### 3.4 What counts as essential (the clarification rule)

A question is asked only when one of these is true for a **required** field.

1. The value is `missing` and there is no configured default.
2. The value fails validation (deadline in the past, quantity not positive, target above hard budget, currency not MYR).
3. The value is `inferred` with confidence below `INTAKE_MIN_CONFIDENCE`.
4. The model flagged a real ambiguity that changes the order (for example two different products, or two different budgets in the same text).

Required fields are `product`, `quantity`, `hard_budget_myr`, `delivery_deadline`, and `location`. Fields with defaults (`target_total_myr`, `minimum_quality`, `max_rounds`) are **never** asked. They are shown for review with a Default chip, and the HOD confirms them along with everything else.

At most `INTAKE_MAX_QUESTIONS` questions are open at once, ordered by the field order above.

## 4. Tech decisions (fixed for this phase)

Everything from Phase 1 Section 4 stays. Phase 2 adds only these.

| Area | Choice |
|---|---|
| New Python dependency | `tzdata` (Windows has no system time zone database, so `zoneinfo` needs it). No other new packages |
| Extraction call | One Claude Messages API call per extraction using **structured outputs** with a JSON Schema built from the Pydantic `GoalExtraction` model. Check the current SDK docs for the exact parameter. Do not use forced `tool_choice` if it conflicts with the model's thinking settings |
| Validation | Pydantic v2 model validation, then the deterministic rules in Step 2.4 |
| Dates | Resolved in `APP_TIMEZONE` (Asia/Kuala_Lumpur). "Today" is passed into the prompt explicitly |
| Planning | A fixed procurement task template in code. The model does not invent the plan in Phase 2 |
| Frontend | No new packages. Reuse the existing `Sheet`, `ui.tsx`, and `.grid-table` styles |

## 5. New and changed files

```text
AiDormathon 26/
├── docs/
│   ├── StakeMate_Claude_Code_Kickoff_Phase_2.md   # this file
│   ├── PROGRESS.md                                # extended
│   └── PHASE2_DEMO.md                             # new
├── backend/
│   ├── .env.example                               # new settings
│   ├── requirements.txt                           # + tzdata
│   ├── alembic/versions/0002_phase2_goals_plan.py # new
│   ├── app/
│   │   ├── config.py                              # new settings
│   │   ├── models/
│   │   │   ├── missions.py                        # new mission columns
│   │   │   └── planning.py                        # GoalExtraction, ClarificationQuestion, MissionTask
│   │   ├── schemas/
│   │   │   ├── intake.py                          # new
│   │   │   └── plan.py                            # new
│   │   ├── services/
│   │   │   ├── goal_manager.py                    # extraction, validation, clarification, submit
│   │   │   ├── workflow_orchestrator.py           # task graph, dependency checks, hooks
│   │   │   └── mission_service.py                 # new limit fields, plan on create
│   │   ├── llm/
│   │   │   ├── extraction_client.py               # the only Phase 2 file that calls anthropic
│   │   │   └── extraction_prompt.md
│   │   ├── tools/
│   │   │   ├── plan_tools.py                      # read_mission_plan, update_task
│   │   │   └── executor.py                        # dependency gate, task hooks
│   │   ├── agent/
│   │   │   ├── claude_orchestrator.py             # plan-aware loop
│   │   │   └── system_prompt.md                   # plan rules
│   │   └── api/
│   │       ├── intake.py                          # new router
│   │       └── missions.py                        # plan endpoint, continue run
│   └── tests/
│       ├── test_goal_extraction.py
│       ├── test_clarification.py
│       ├── test_intake_api.py
│       ├── test_task_plan.py
│       └── test_orchestrator_plan.py
└── frontend/src/
    ├── app/(app)/missions/page.tsx                # sheet steps, draft rows
    ├── app/(app)/missions/[id]/mission-view.tsx   # Plan and Open points sections
    ├── components/intake/                         # describe, questions, review steps
    └── lib/types.ts, lib/api.ts                   # new types and calls
```

`app/llm/` sits outside `app/tools/` on purpose, so the tool isolation rule still holds.

## 6. Environment variables

Add to `backend/.env.example` (and to the `Settings` class).

```dotenv
# Phase 2. Goal intake
APP_TIMEZONE=Asia/Kuala_Lumpur
# Optional. Blank uses ANTHROPIC_MODEL
ANTHROPIC_EXTRACTION_MODEL=
# Optional. Blank means location is asked when the request does not state one
DEFAULT_DELIVERY_LOCATION=
DEFAULT_MIN_QUALITY=4.0
DEFAULT_MAX_ROUNDS=3
# Suggested target = hard budget x ratio, rounded down to RM10
DEFAULT_TARGET_RATIO=0.9
INTAKE_MAX_QUESTIONS=3
INTAKE_MIN_CONFIDENCE=0.6
GOAL_TEXT_MAX_CHARS=2000
```

No frontend environment changes.

---

## 7. Step 2.0. HUMAN gate. Phase 1 must be live first

Phase 2 does not start until Phase 1 is proven on the real database and the real Claude API. Check each item and show Wayne the result. Any failure means stop.

| Check | Command or action | Pass condition |
|---|---|---|
| Network | `python -m scripts.check_db` | Both URLs return `SELECT 1` |
| Migrations | `alembic upgrade head` and `alembic -x target=test upgrade head` | Both succeed |
| Append-only audit | `python -m scripts.check_audit_append_only` | UPDATE and DELETE fail |
| Seed | `python -m scripts.seed` | Three users and 12 policies, safe to re-run |
| Tests | `pytest` | **All 48 pass** |
| Claude | `ANTHROPIC_API_KEY` in `backend/.env`, then `python -m scripts.check_claude` | Model name and first reply line print |
| Live demo | Run `docs/PHASE1_DEMO.md` once with real logins | Every step matches the expected screen |
| Open questions | Wayne answers the two open questions at the end of `PROGRESS.md` | Answers recorded in `PROGRESS.md` |

**HUMAN.** Wayne fixes the network (hotspot or another network that allows port 5432), adds the API key, runs the live demo, and answers the open questions. Record everything in `PROGRESS.md` under "Phase 1 live verification".

Then create branch `phase-2` from the finished Phase 1 branch and ask Wayne whether `phase-0-1` should be merged into `main` first.

---

## 8. Phase 2 steps

### Step 2.1. Settings and dependency

- Add `tzdata` to `requirements.txt` and install it.
- Add the Section 6 settings to `config.py` and `.env.example`. Add a helper `today_local()` that returns today's date in `APP_TIMEZONE`.

**Check.** `python -c "from app.config import today_local; print(today_local())"` prints today's Kuala Lumpur date. All Phase 1 tests pass.

### Step 2.2. Data model and migration `0002`

New columns on `missions`.

| Column | Type | Notes |
|---|---|---|
| `mission_type` | text, default `procurement` | Only `procurement` is supported in Phase 2 |
| `location` | text, nullable | Delivery area, for example "Bandar Sunway, Selangor" |
| `specifications` | jsonb list of strings, default `[]` | Mandatory requirements such as "custom printed" |
| `event_context` | jsonb, default `{}` | Context only (event type, audience size). Never a limit |
| `requirements_provenance` | jsonb, default `{}` | Field name to `{source, evidence, confidence, note}` |
| `submitted_by`, `submitted_at` | uuid, timestamptz, nullable | Set when a draft is submitted |

Add `location` and `specifications` to `LIMIT_FIELDS` and to `REQUIRED_FOR_CONFIRM` (location only), so changing them on an active mission becomes a Tier 3 HOD approval, the same as the other limits. Add both to `MissionCreate`, `MissionUpdate`, and `MissionOut`. Existing rows get `location = NULL`, which means the HOD must fill it before confirming any old unconfirmed mission.

New tables.

| Table | Key columns |
|---|---|
| `goal_extractions` | `id`, `mission_id`, `created_by`, `model`, `goal_text_hash`, `status` (`ok`, `invalid_output`, `api_error`, `unsupported`), `raw_output` (jsonb, the validated model output), `validation_notes` (jsonb), `created_at` |
| `clarification_questions` | `id`, `mission_id`, `extraction_id`, `field`, `reason` (`missing`, `invalid`, `low_confidence`, `ambiguous`), `prompt_text`, `answer_type` (`text`, `number`, `money`, `date`, `choice`), `choices` (jsonb), `status` (`open`, `answered`, `dismissed`), `answer_value` (jsonb), `answered_by`, `answered_at` |
| `mission_tasks` | `id`, `mission_id`, `key` (unique per mission), `title`, `kind` (`human`, `research`, `evaluation`, `communication`, `negotiation`, `verification`, `reporting`), `owner` (`agent`, `hod`, `member`), `depends_on` (jsonb list of keys), `status` (`pending`, `ready`, `in_progress`, `waiting_approval`, `done`, `blocked`, `skipped`, `failed`), `completed_by_tools` (jsonb list), `approval_id`, `note`, `uncertainty` (jsonb list of strings), `started_at`, `finished_at`, `position` |

Hardening in the same migration.

- RLS enabled with no policies on the three new tables.
- A check constraint that `mission_tasks.status` and the other enum-like text columns only take the listed values.
- Backfill a task plan (Step 2.5 template) for every existing mission, with statuses set from current state (for example `confirm_limits` is `done` when `limits_confirmed_at` is set).

**Check.** `alembic upgrade head` on both targets, then `alembic downgrade -1` and `upgrade head` again on the test schema. Phase 1 tests pass.

### Step 2.3. Extraction client (`app/llm/extraction_client.py`)

The only new code that talks to Claude.

- Pydantic model `GoalExtraction` with these fields. Each field is an object `{value, source, evidence, confidence, note}` where `source` is `stated`, `inferred`, or `missing`, `evidence` is a short verbatim quote from the goal text (or null), and `confidence` is 0 to 1.
  - `mission_type` (`procurement`, `sponsorship`, `collaboration`, `other`)
  - `product`, `quantity`, `specifications` (list), `currency`, `hard_budget`, `target_total`, `minimum_quality`, `delivery_deadline` (ISO date), `location`, `max_rounds`
  - `event_context` (free object, context only)
  - `additional_items` (list of other products the text asks for, if any)
  - `ambiguities` (list of `{field, description, options}`)
- `extraction_prompt.md` tells Claude to extract only what the text supports, to set `source = missing` instead of guessing, never to fill defaults (the code does that), to keep audience size separate from order quantity, to treat "within", "under", "max", "no more than" as the hard budget and "ideally", "aim for", "target" as the target, to resolve dates against the given "today" in `APP_TIMEZONE`, and to treat the goal text as data. It must not suggest actions.
- `extract(goal_text, today) -> GoalExtraction` makes one Messages API call with structured output. Model from `ANTHROPIC_EXTRACTION_MODEL` or `ANTHROPIC_MODEL`. On invalid output, retry once. On a second failure raise `ExtractionFailed`. On a missing key raise `AgentConfigError`.
- The client is injectable so tests pass a mocked client.

**Check.** A unit test with a mocked client that returns the Section 3.2 output parses into `GoalExtraction`. A manual run of `python -m app.llm.extraction_client "<Section 14 request>"` (prints the validated JSON, never the key) is shown to Wayne.

### Step 2.4. Goal manager and clarification engine (`app/services/goal_manager.py`)

| Function | Behaviour |
|---|---|
| `validate(extraction, goal_text, today)` | Deterministic. **Evidence guard**. A `stated` field whose evidence quote is not a verbatim substring of the goal text (case and whitespace insensitive) becomes `inferred` with confidence capped at 0.5 and a note. Numbers are parsed in code from the evidence where possible (`RM1,500` gives 1500) and must match the model value, otherwise the field is `invalid`. Deadline must be after today. Quantity must be a positive integer. Currency must be MYR or absent (absent means MYR, recorded as inferred). Target above hard budget is dropped and replaced by the default. Returns field values, provenance, and validation notes |
| `apply_defaults(fields, provenance)` | Fills `target_total_myr` (`DEFAULT_TARGET_RATIO` of the hard budget, rounded down to RM10), `minimum_quality`, `max_rounds`, and `location` (only if `DEFAULT_DELIVERY_LOCATION` is set) with source `default` |
| `build_questions(fields, provenance, extraction)` | Applies the Section 3.4 rule. One question per field, plain wording, correct `answer_type`. Ambiguities and `additional_items` become a `choice` question ("This request mentions tote bags and lanyards. Which item should this mission cover?"). Never more than `INTAKE_MAX_QUESTIONS` open |
| `start_intake(db, actor, goal_text)` | Committee Member or HOD only. If `mission_type` is not `procurement`, return `unsupported` with a clear message and create **no** mission (sponsorship and collaboration are Phase 9). Otherwise create a `draft` mission owned by the actor with the validated fields and provenance, store the `goal_extractions` row and questions, audit `mission.goal_extracted` (model, field sources, question count, never the API key) and `mission.questions_asked` |
| `answer_questions(db, actor, mission, answers)` | Owner or HOD only, draft only. Each answer is validated with the same rules as the field. Valid answers set the field with source `answered` and close the question. Invalid answers return 422 and leave the question open. After applying, rerun `build_questions` so a fixed field can never reopen and a new problem (for example target now above a lowered budget) is caught. Audit `mission.question_answered` |
| `re_extract(db, actor, mission, goal_text)` | Owner or HOD, draft only. Replaces the extraction. Keeps fields whose source is `answered` or `edited` unless the new text clearly states a different value, in which case it opens a question instead of overwriting silently |
| `submit(db, actor, mission, confirm_limits=False)` | Owner or HOD, draft only. Refuses with 409 if any question is open or any required field is missing. Sets `submitted_by`, `submitted_at`, status `awaiting_hod_confirmation`, builds the task plan (Step 2.5), audits `mission.submitted`. The HOD may pass `confirm_limits=True` to submit and confirm in one step (reuses `mission_service._confirm`) |
| `discard(db, actor, mission)` | Owner or HOD, draft only. Sets status `cancelled`. Audited |

Manual edits to a draft go through the existing `PATCH /missions/{id}`. On a draft every field is editable by the owner without approval (limits are not confirmed yet). Each edited field gets source `edited`.

The Phase 1 form path (`POST /missions` with full fields) still works. It creates the mission directly in `awaiting_hod_confirmation` with every provided field marked `edited` and builds the task plan.

**Check.** The goal manager tests in Step 2.9 pass with a mocked extraction client.

### Step 2.5. Task plan and workflow orchestrator (`app/services/workflow_orchestrator.py`)

The procurement template, in code, as a list of dicts. Phase 3 and later phases change `completed_by_tools` as real tools arrive.

| Key | Title | Kind | Owner | Depends on | Completed by (Phase 2) |
|---|---|---|---|---|---|
| `confirm_limits` | HOD confirms mission limits | human | hod | none | `mission.limits_confirmed` event |
| `research_suppliers` | Find candidate suppliers | research | agent | none | `search_suppliers` |
| `compare_rank` | Compare and rank candidates | evaluation | agent | `research_suppliers` | `search_suppliers` (the demo result is already ranked. Phase 3 switches this to `rank_candidates`) |
| `send_enquiries` | Send enquiries to the shortlist | communication | agent | `compare_rank`, `confirm_limits` | an executed `send_enquiry` approval |
| `process_replies` | Read and classify replies | communication | agent | `send_enquiries` | none yet (Phase 4 `process_reply`) |
| `negotiate` | Negotiate within limits | negotiation | agent | `process_replies` | none yet (Phase 4) |
| `verify_terms` | Verify final terms | verification | agent | `negotiate` | none yet (Phase 6) |
| `final_report` | Prepare final report | reporting | agent | `verify_terms` | none yet (Phase 6 `create_final_report`) |
| `hod_commitment` | HOD approves the commitment | human | hod | `final_report` | none yet (Phase 6 `confirm_commitment`) |

Functions.

| Function | Behaviour |
|---|---|
| `build_plan(db, mission)` | Creates the template rows. Idempotent. Tasks with no dependencies start `ready`, the rest `pending` |
| `refresh(db, mission)` | Recomputes `pending` to `ready` when every dependency is `done` or `skipped`. Never moves a task backwards except through `reopen` |
| `ready_tasks(db, mission, owner=None)` | Ready tasks in `position` order |
| `required_task_for(tool_name, args)` | Maps a tool call to the task it belongs to. `send_approved_message` with kind `enquiry` maps to `send_enquiries`. `counteroffer` and `terms` map to `negotiate`. `clarification` and `follow_up` map to `send_enquiries` until Phase 4 adds its own tasks. Tier 0 read tools map to nothing |
| `check_dependencies(db, mission, tool_name, args)` | If the mapped task is `pending` or `blocked`, raise `Refused("dependency_not_met", ...)` naming the unfinished dependencies |
| `on_tool_success(db, mission, tool_name, args, result)` | Marks tasks whose `completed_by_tools` includes the tool as `done`, then `refresh` |
| `on_approval_requested(db, approval)` | Marks the mapped task `waiting_approval` and stores `approval_id` |
| `on_approval_decided(db, approval)` | `executed` marks the task `done`. `rejected`, `expired`, or `failed` reopens it to `ready` with a note giving the reason, and writes audit event `plan.replan_requested` (the Phase 5 replanning hook, a no-op beyond the audit row in Phase 2) |
| `on_limits_confirmed(db, mission)` | Marks `confirm_limits` `done` |
| `set_task(db, actor, mission, key, status, note, uncertainty)` | Used by the agent tool. The agent may only change `agent`-owned tasks and only to `in_progress`, `done`, or `blocked`. It may never touch `human` tasks. Marking `done` a task whose `completed_by_tools` is not empty is refused (those complete only through their tools) |

Wire the hooks in.

- `executor.execute` calls `check_dependencies` before permission checks for every agent actor, `on_tool_success` after a Tier 0 tool succeeds, and `on_approval_requested` after a gated tool creates an approval.
- `approval_service.decide` and `executor.run_approved` call `on_approval_decided` after the final status is set.
- `mission_service._confirm` calls `on_limits_confirmed`.
- Dependency checks apply to the **agent** only. People act through their own endpoints and the approval gate already covers them.

Every task status change writes one audit row `task.status_changed` with old and new status and the reason.

**Check.** `test_task_plan.py` passes.

### Step 2.6. New tools (`app/tools/plan_tools.py`)

| Tool | Action type | What it does |
|---|---|---|
| `read_mission_plan` | `read_mission_state` (Tier 0) | Returns the tasks with status, owner, dependencies, notes, and uncertainty, the ready agent tasks, open questions (normally none after submit), and fields whose provenance is `inferred` or `default` |
| `update_task` | `update_mission_state` (Tier 0) | Wraps `workflow_orchestrator.set_task`. Input `{key, status, note, uncertainty}` |

Also extend `read_mission_state` to return `location`, `specifications`, `event_context`, and `requirements_provenance`.

No new approval policies are needed. Both tools reuse Tier 0 action types already seeded.

**Check.** `list_tools()` now returns 10 tools. `test_tool_isolation.py` passes.

### Step 2.7. Plan-aware orchestrator

Changes to `ClaudeOrchestrator.run`.

- Refuse to run on a `draft` or closed mission (409). Runs on `awaiting_hod_confirmation` are allowed for Tier 0 work only, which the approval gate already guarantees.
- The first user message now contains the mission code, a compact plan summary (each task key, status, owner), the ready agent tasks, and any non-stated fields, followed by the user's prompt. The plan summary is built in code from the database.
- New stop status `waiting_on_humans`. After each turn, if the model has not ended the run and there are **no ready agent tasks**, stop with this status and a message naming what the humans need to do (for example "Waiting for the HOD to confirm limits" or "Waiting for approval APR-..."). This is enforced in code like `approval_required`.
- `RunResult` gains `ready_tasks_before`, `ready_tasks_after`, and `uncertainties` (the `uncertainty` lists of tasks changed during the run). The `agent.run` audit summary includes them.
- New API `POST /missions/{id}/agent/continue` (Committee Member or HOD) runs the loop with the fixed prompt "Continue the mission plan. Work on the ready tasks in order." The existing `POST /missions/{id}/agent/run` with a free prompt stays.

Changes to `system_prompt.md`. Add a "Mission plan" section.

- Call `read_mission_plan` after `read_mission_state`.
- Work only on ready agent tasks, in order. Set a task `in_progress` before working on it.
- A tool refused with `dependency_not_met` means stop and report which tasks must finish first. Do not try another route.
- Record anything uncertain with `update_task` (`uncertainty` list) instead of guessing. Name inferred and default values as such in the final answer.
- Human tasks (`confirm_limits`, `hod_commitment`) are never yours.
- Tasks with no tool yet (replies, negotiation, verification, report in Phase 2) are out of reach. Say they are planned for later and stop.

**Check.** `test_orchestrator_plan.py` passes with a mocked Anthropic client.

### Step 2.8. API endpoints

| Method and path | Who | Purpose |
|---|---|---|
| `POST /missions/intake` | committee_member, hod | Body `{goal_text}`. Runs `start_intake`. Returns the draft mission, field provenance, and open questions. 422 `unsupported_goal` for non-procurement. 503 when Claude is not configured. 502 when extraction fails twice |
| `POST /missions/{id}/intake/answers` | owner, hod | Body `{answers: [{question_id, value}]}` |
| `POST /missions/{id}/intake/re-extract` | owner, hod | Body `{goal_text}` |
| `POST /missions/{id}/submit` | owner, hod | Body `{confirm_limits: bool}` (true allowed for the HOD only) |
| `POST /missions/{id}/discard` | owner, hod | Draft only |
| `GET /missions/{id}/plan` | user | Tasks, ready tasks, open points (non-stated fields, open questions, blocked tasks, uncertainties) |
| `POST /missions/{id}/agent/continue` | committee_member, hod | Plan-driven run |

Changes to existing endpoints.

- `GET /missions` includes drafts **only for their owner** (and all drafts for the HOD), with a `draft` status label.
- `GET /missions/{id}` returns the new fields and provenance.
- The agent token gets 403 on every endpoint in this table except `GET /missions/{id}/plan`, which it does not need either (it uses `read_mission_plan`), so give it 403 too.
- All refusals are audited through `audited_refusals`, as in Phase 1.

### Step 2.9. Tests (write before Step 2.10)

All must pass with `pytest` against the test schema, together with the 48 Phase 1 tests.

**Extraction and validation**

1. The mocked Section 14 output becomes a draft with the Section 3.2 values. Quantity is 300 (not 200). Exactly one open question, for `location`.
2. With `DEFAULT_DELIVERY_LOCATION` set, the same request produces **zero** questions and `location` has source `default`.
3. Evidence guard. A `stated` quantity whose quote is not in the goal text is downgraded to `inferred` with confidence at most 0.5, and because quantity is required a question is opened.
4. Number check. The model says hard budget 1500 but the evidence says `RM1,800`. The field is marked invalid and a question is opened.
5. A deadline in the past opens a `date` question. "25 October" on 10 October 2026 resolves to 2026-10-25 with source `inferred`.
6. A request priced in USD opens a currency question and creates no `money` value until answered.
7. A model target above the hard budget is replaced by the default target and noted.
8. A request for tote bags and lanyards opens one `choice` question listing both.
9. A sponsorship request returns 422 `unsupported_goal` and creates no mission. An audit row records it.
10. Missing `ANTHROPIC_API_KEY` returns 503 and creates no mission. A client that returns invalid JSON twice returns 502 and creates no mission.

**Clarification and submission**

11. A valid answer sets the field with source `answered`, closes the question, and the mission can be submitted.
12. An invalid answer (quantity `-5`, past date, `abc` for money) returns 422 and the question stays open.
13. Submitting with an open question or a missing required field returns 409.
14. Another Committee Member cannot answer, edit, re-extract, submit, or discard someone else's draft (403). The HOD can.
15. The agent token gets 403 on every intake endpoint. No registry tool can create or submit a mission (assert on `list_tools()` names and on the executor refusing an unknown tool).
16. Lowering the hard budget by answer or edit below the default target re-opens nothing but recomputes the default target. Raising the target above the budget by edit returns 422.
17. A Committee Member draft submits to `awaiting_hod_confirmation`. The HOD submit with `confirm_limits=true` goes straight to `active`. A Committee Member sending `confirm_limits=true` gets 403.
18. Changing `location` or `specifications` on an active mission creates a Tier 3 `change_mission_limits` approval and the value does not change until the HOD approves.

**Task plan and orchestration**

19. Submit builds 9 tasks with the template dependencies. `research_suppliers` and `confirm_limits` are `ready`.
20. The agent calling `send_approved_message` (enquiry) before `compare_rank` is done is refused with `dependency_not_met`, audited, and **no approval row** is created.
21. `search_suppliers` success marks `research_suppliers` and `compare_rank` done. With limits confirmed, `send_enquiries` becomes `ready`. The enquiry request marks it `waiting_approval` with the approval ID. Execution after Committee Member B approves marks it `done`.
22. A rejected enquiry approval reopens `send_enquiries` to `ready` with the reason and writes `plan.replan_requested`.
23. `update_task` by the agent cannot change `confirm_limits` or `hod_commitment`, cannot mark `research_suppliers` done directly, and can mark an agent task `blocked` with an uncertainty note.
24. Orchestrator with a mocked client. The first message contains the plan summary. The client calls `read_mission_plan`, then `search_suppliers`, then ends its turn. With limits not confirmed, the run stops with `waiting_on_humans` and names the HOD confirmation.
25. Orchestrator refuses to run on a draft (409).
26. Every task status change and every intake event writes exactly one audit row with the right actor.
27. Migration backfill. A mission created by the Phase 1 code path before `0002` gets a plan with statuses matching its state.

### Step 2.10. Frontend

Keep the Phase 1 look (Apple-style, very little text, full borders on every table cell, light and dark, reduced motion). **No large text box in the middle of the screen.** The goal prompt lives inside the existing New mission bottom sheet.

**New mission sheet (`/missions`)**, three steps inside the same `Sheet`, with a small step indicator at the top.

| Step | Contents |
|---|---|
| Describe | A compact multi-line field at the top of the sheet (about 3 lines, grows to a cap), placeholder "Describe what you need, your budget and deadline", an Extract button, and a quiet "Fill in manually" link that opens the Phase 1 form. While extracting, show a subtle progress state in the button, not a full-screen spinner. 503 shows "Claude is not set up yet" and keeps the text |
| Questions | Shown only when questions are open. Each question is one row with the matching input (number, money with RM prefix, date picker, text, or segmented choice). One Continue button sends all answers. Invalid answers show the backend reason under the input |
| Review | The extracted fields as an editable form. Each field has a provenance chip (Stated, Inferred, Default, You answered, Edited). Tapping a Stated or Inferred chip shows the evidence quote. Default fields have a light highlight so the user and HOD notice them. Event context is shown read-only under the fields. Buttons are Submit to HOD (Committee Member), Submit and confirm (HOD), Save draft, and Discard |

Drafts appear in the missions table with a Draft badge, visible only to their owner and the HOD. Tapping a draft reopens the sheet at the right step.

**Mission detail (`/missions/[id]`)**

- A **Plan** section with a bordered table (step, owner, depends on, status badge, note). Waiting-approval rows link to the approval. Human tasks show who must act.
- An **Open points** list (inferred and default fields, blocked tasks, uncertainty notes) with a count badge. Hidden when empty.
- A **Continue** button next to Run agent that calls `/agent/continue`. After a run, show the status in plain words (Completed, Waiting for approval, Waiting for the HOD, Stopped).
- The fact tiles show `location` and `specifications`.

**Check.** `npm run lint`, `tsc --noEmit`, and `npm run build` pass. Visual check at desktop and 375 px, light and dark, for each sheet step.

### Step 2.11. Phase 2 demo script

Write `docs/PHASE2_DEMO.md`, then run it live.

1. Committee Member A opens New mission and pastes the Section 14 request into Describe.
2. KawTeam extracts the fields. The only question is the delivery location. A answers "Bandar Sunway, Selangor".
3. The Review step shows 300 tote bags, custom printed, hard budget RM1,500, deadline 25 October 2026 (Inferred, year assumed), target RM1,350, minimum quality 4.0, and 3 rounds (Default). A taps the Stated chip on the budget and sees "within RM1,500".
4. A submits. The mission is `awaiting_hod_confirmation` and the Plan shows 9 steps with `research_suppliers` and `confirm_limits` ready.
5. A presses Continue. The agent searches (demo data), marks research and comparison done, and stops with **Waiting for the HOD to confirm limits**.
6. A asks the agent to send an enquiry anyway. The backend refuses with `dependency_not_met` and the answer names the HOD confirmation.
7. The HOD confirms limits. A presses Continue again. The enquiry becomes a Tier 1 approval and `send_enquiries` shows Waiting for approval.
8. Committee Member B rejects it with a reason. The task reopens and the audit log shows `plan.replan_requested`. B then approves a new request and the task is done with a **SIMULATED** message.
9. The audit log shows the extraction, the question and answer, the submission, every task change, and every tool call with actor and role.

Also include the extra checks (sponsorship request refused, USD request asks for currency, two-product request asks which item) and the pytest equivalents.

### Phase 2 exit criteria (from blueprint Section 23)

- The Section 14 demo request produces a structured mission with all constraints (product, quantity, specifications, hard budget, target, minimum quality, deadline, location, max rounds, approval policy), each with provenance.
- The agent asks only essential questions. For the Section 14 request that is at most one question, and zero when a default location is configured.
- The goal is decomposed into a stored task plan with dependencies, and the backend enforces those dependencies for the agent.
- The orchestrator follows the plan, reports uncertainty instead of guessing, and stops cleanly when waiting on people.
- All Phase 1 and Phase 2 tests pass. `npm run build` passes.

---

## 9. Definition of done and handoff

- `pytest` passes (Phase 1 and Phase 2 tests). `npm run build` passes.
- `docs/PHASE2_DEMO.md` has been run live with real logins and the real Claude API, and its run log is filled in.
- `docs/PROGRESS.md` has a Phase 2 section (what was built, how each part was checked, known gaps, open questions) and ends with a short **Ready for Phase 3** note covering these points.
  - Which `completed_by_tools` entries change when `search_stakeholders`, `verify_supplier`, `compare_offers`, and `rank_candidates` arrive.
  - How `location` and `specifications` will feed real supplier search.
  - Where the Phase 5 replanning will hook into `plan.replan_requested`.

## 10. Out of scope for this kickoff

- Real web search, real supplier data, and the Module A handoff object (Phase 3).
- Real email, reply processing, and the negotiation engine (Phase 4).
- Replanning beyond the audit hook, and alternative-supplier switching (Phase 5).
- Final report, `confirm_commitment`, savings, and the nine verified-result states in the UI (Phase 6).
- WorkBuddy, MCP server, StakeMate Skill (Phase 7).
- Sponsorship and collaboration missions, workflow checkpoints, parallel research, user-defined autonomy, multilingual intake (Phase 9).
- A model-generated plan. The plan stays a fixed template in Phase 2.
