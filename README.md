# KawTeam

Your event. Our legwork. Your call.

KawTeam is a chat-first workspace for events and supplier work. The home page is a new chat: ask it to start a project, attach a proposal, find vendors or show what needs approval. Each project has its own conversation, files and optional tasks with separate conversations that share the project files. Supplier shortlists, enquiry drafts, approvals and the final vendor choice appear as cards inside the conversation. Documents, conversations and assistant preferences persist in Supabase. There is no login or procurement intake form.

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

Open **http://localhost:3000**. On a fresh checkout, run `npm ci` in `apps/web` (if npm reports the lockfile is out of sync, `npm install --no-save` installs the same dependencies without rewriting it), then create a Python venv in `apps/api` and install `requirements.txt`. Both servers need their ignored environment files; see **Supabase setup**.

## Supabase setup

Use your own Supabase project. Never reuse another team's database credential.

1. Apply `supabase/migrations/202610100001` to `202610100004` in order, unchanged. Migration 0001 also inserts a template workspace row that only works with its original secret; delete that row from your own database once your workspace exists.
2. Generate locally: a workspace UUID plus `KAWTEAM_DATABASE_SECRET`, `KAWTEAM_SESSION_SECRET` and `KAWTEAM_GATEWAY_SECRET` (at least 32 characters each, for example Python `secrets.token_urlsafe(36)`).
3. Insert your workspace with only the digest of the database secret, never the secret itself: `insert into public.kawteam_workspaces(id,name,credential_digest) values('<uuid>','KawTeam','<sha256 hex of KAWTEAM_DATABASE_SECRET>');`. Keep this out of the migrations folder.
4. Copy `apps/api/.env.example` to `apps/api/.env` with your `SUPABASE_URL`, publishable key, workspace UUID and the three secrets. Create `apps/web/.env.local` with `NEXT_PUBLIC_DATA_MODE=api`, `KAWTEAM_API_URL=http://localhost:8000` and the same `KAWTEAM_GATEWAY_SECRET`. Both files are git-ignored.
5. Seed the labelled sample from `apps/api`: `$env:PYTHONPATH="src"; .venv/Scripts/python.exe -m kawteam.setup_workspace`. It prints `Supabase verified` and never overwrites existing records.

## Using the app

The left sidebar, top to bottom:

- **New chat.** Opens the home chat. Try a suggestion: “Start a new project”, “Find shirt printing vendors for 50 shirts within RM2,000”, “Show what needs my approval” or upload a project file. Requests without a project ask which project to use or offer to create one.
- **Overview.** Expands to **Recent activity** (latest projects, conversations and approval events), **Approvals** (every draft awaiting review) and **Calendar** (dates from project plans and supplier requests).
- **Projects.** **New project** and each project's conversation, with its tasks nested under the selected project. The project header keeps **Files**, **Tasks**, **Approvals**, **Vendors**, **Context**, **Assistant settings** and **New task** close at hand.
- **Connections.** The vendor library, past supplier requests with their outcome reports, and AI provider status on one page.
- **Profile.** Pinned to the bottom: switch between Organiser, Teammate and Observer without a login.

The chatbox sends with Enter and adds a line with Shift+Enter; the paperclip uploads to the current project. Use **New task** only when a separate conversation would help organise the same project. **Assistant settings** offers Automatic, Research first, or Existing vendor, a preferred supplier, a shortlist cap of three and custom instructions. Repeat orders skip discovery and request fresh terms; previous prices, approval and supplier decisions are not copied. Until AI keys are supplied, requests are saved with an honest connection note.

Server-side permissions protect mutations, approvals and selection; buttons a profile cannot use are hidden or disabled, but the server check remains the source of truth. This deliberately shared public demo is not private personal authentication. **Only the organiser approves drafts and chooses a final vendor.** Choosing never buys, pays or signs anything.

Older links still work: `/vendors` opens Connections, `/inbox` opens Approvals, and project, task and supplier request URLs are unchanged.

The interface uses the KawTeam palette (#00545f teal, #d6fb00 lime, #ecffb6 pale lime) with the system font, follows the operating system's light or dark appearance, respects reduced motion and reduced transparency, and is designed for desktop browsers.

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

Deploy the API with its local server environment values, preserving the database credential whose digest is in your workspace row, and set `COOKIE_SECURE=true`. Deploy the web with `NEXT_PUBLIC_DATA_MODE=api`, `KAWTEAM_API_URL=https://your-api.vercel.app`, and the matching server-only `KAWTEAM_GATEWAY_SECRET`. Never expose secrets with a `NEXT_PUBLIC_` prefix. Verify the deployed upload/session/demo flow before submitting.

Database tables deny direct public access. Scoped RPCs require a separate secret-held backend credential. [Checkpoint security notes](docs/PHASE_3_7_CHECKPOINT.md) explain the expected Supabase advisor warnings.

Submission: public GitHub repository, deployed app URL, presentation PDF, group name and campus branch. Aim **11 October 08:45 MYT**, ahead of the supplied 09:00 buffer cutoff.

See the [current project makeover checkpoint](docs/PROJECT_MAKEOVER_CHECKPOINT.md), [makeover plan](docs/plans/2026-10-10-project-makeover.md), [backend checkpoint](docs/PHASE_3_7_CHECKPOINT.md) and [checklist](KAWTEAM_BUILD_CHECKLIST.md). Original blueprint unchanged.
