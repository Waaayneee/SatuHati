# KawTeam

Your event. Our legwork. Your call.

KawTeam is a project workspace for events and supplier work. Start from the overview: projects, approvals, updates and a calendar of saved dates. Create a project by name, upload its proposal, plans and budget once, then talk naturally in its general conversation. Optional tasks provide separate conversations with shared project files. Documents, conversations and assistant preferences persist in Supabase. There is no login or procurement intake form.

## Run locally

Open this folder in VS Code. Use **two terminals**, starting from the project folder.

Terminal 1:

```powershell
cd apps/api
.venv/Scripts/python.exe -m uvicorn kawteam.main:app --app-dir src --reload --port 8000
```

Terminal 2:

```powershell
cd apps/web
npm run dev
```

Open **http://localhost:3000**. Local ignored environment files already connect this workspace to KawTeam Supabase. On a fresh checkout, run `npm ci` in `apps/web`; create a Python venv and install `requirements.txt` in `apps/api`. Configure both `.env.example` templates first.

Start with the labelled sample **Tech Night**, or click **New project**. Use **Files** or the chat paperclip to upload a proposal, then ask “Find shirt printing vendors for 50 shirts within RM2,000.” Use **New task** only when a separate conversation would help organise the same project. **Assistant settings** offers Automatic, Research first, or Existing vendor, a preferred supplier, a shortlist cap of three and custom instructions. Repeat orders skip discovery and request fresh terms; previous prices, approval and supplier decisions are not copied. Until AI keys are supplied, requests are saved with an honest connection note.

Switch Organiser, Teammate and Observer using the profile button. Server-side permissions protect mutations, approvals and selection, but this deliberately shared public demo is not private personal authentication. **Only the organiser chooses a final vendor.** Choosing never buys, pays or signs anything.

## Current implementation

- Supabase projects, optional tasks, assistant settings, files, extracted memory, scoped conversations, requests, drafts and human decisions. Atomic uploads/chat completion, conflict detection and retry protection.
- Event-scoped document retrieval/citations. PDF, DOCX, XLSX, TXT, Markdown and CSV up to 3 MB; 80,000 extracted characters/file, 20 files/event. Text PDFs up to 40 pages; scanned PDFs need a text version. The hackathon version stores originals in database records; object storage/vector retrieval can follow.
- Optional Gemini conversation and Tavily source discovery adapters. **Neither key is configured yet.** Public-source candidates remain unquoted; unknown terms and contacts are never invented.
- Controlled tote scenario: **Prepare enquiry → Approve draft → Send in demo → Check demo reply**. Exact-message hash/revision, 30-minute approval expiry, single-use send and three-round cap. Replies are fictional and saved; no external email is sent.
- Outcome report with constraints, evidence references, pending/no-deal outcomes and explicitly simulated potential savings for the sample scope.

**WorkBuddy remains deferred at your request.** The existing health-only scaffold is preserved; autonomous execution and real external email need their future integrations. Phases 3–5 and 7 have a working hackathon implementation; live Phase 4 needs keys, Phase 6 remains deferred. No public deployment has been created.

## Optional provider keys

Add to `apps/api/.env`, never frontend code or Git, then restart FastAPI:

```dotenv
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
TAVILY_API_KEY=your_key
```

Use the providers' available free tiers and avoid enabling paid billing. Account quotas/availability vary. The Connections page reports configuration. Email remains controlled even with these keys.

## Verify

In `apps/api`: `.venv/Scripts/python.exe -m pytest -q` and `.venv/Scripts/python.exe -m ruff check src tests`.

In `apps/web`: `npm run test`, `npm run lint`, `npm run typecheck`, `npm run build`. Stop the dev server before building the same directory. With both servers running and Playwright Chromium installed, run `npm run test:e2e`.

Browser tests create labelled QA events in the connected workspace. Screenshots: ignored `apps/web/test-results/`. Separate opt-in scripts `tests/live_database.py` and `tests/live_outreach_browser.py` test concurrency and controlled outreach; the latter restores the sample case.

## Free deployment preparation

Use two projects in one Vercel Hobby account: Next.js root **apps/web**, FastAPI root **apps/api**. The API exports `app` from `index.py`, a supported [FastAPI entrypoint](https://vercel.com/docs/frameworks/backend/fastapi). No paid backend host is required. Stay within [function limits](https://vercel.com/docs/functions/limitations); this version uses bounded calls and saved state.

Deploy the API with its local server environment values, preserving the database credential matching the applied migration, and set `COOKIE_SECURE=true`. Deploy the web with `NEXT_PUBLIC_DATA_MODE=api`, `KAWTEAM_API_URL=https://your-api.vercel.app`, and the matching server-only `KAWTEAM_GATEWAY_SECRET`. Never expose secrets with a `NEXT_PUBLIC_` prefix. Verify the deployed upload/session/demo flow before submitting.

Database tables deny direct public access. Scoped RPCs require a separate secret-held backend credential. [Checkpoint security notes](docs/PHASE_3_7_CHECKPOINT.md) explain the expected Supabase advisor warnings.

Submission: public GitHub repository, deployed app URL, presentation PDF, group name and campus branch. Aim **11 October 08:45 MYT**, ahead of the supplied 09:00 buffer cutoff.

See the [current project makeover checkpoint](docs/PROJECT_MAKEOVER_CHECKPOINT.md), [makeover plan](docs/plans/2026-10-10-project-makeover.md), [backend checkpoint](docs/PHASE_3_7_CHECKPOINT.md) and [checklist](KAWTEAM_BUILD_CHECKLIST.md). Original blueprint unchanged.
