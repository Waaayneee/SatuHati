# KawTeam Claude Code Prompt

Paste everything inside the block below into Claude Code, opened at the root of the `AiDormathon 26` folder.

```text
You are a senior full-stack engineer working on KawTeam, a hackathon app (Next.js in apps/web, FastAPI in apps/api, Supabase via RPC functions). The project is already named KawTeam in the code. Work in 5 phases. STOP at the end of every phase, print a short summary of what changed and which files were touched, and wait for my "continue" before starting the next phase.

<context>
- Stack. Next.js App Router (apps/web), FastAPI (apps/api/src/kawteam), Supabase Postgres with RPC functions in supabase/migrations (4 files, 202610100001 to 202610100004). Developed on Windows with PowerShell.
- Data flow. The browser calls the Next.js gateway route apps/web/src/app/api/kawteam/[...path]/route.ts, which forwards to FastAPI using KAWTEAM_API_URL and KAWTEAM_GATEWAY_SECRET. FastAPI calls Supabase RPCs using SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, KAWTEAM_WORKSPACE_ID and KAWTEAM_DATABASE_SECRET (see apps/api/src/kawteam/config.py).
- The database authorises each RPC by comparing sha256(KAWTEAM_DATABASE_SECRET) with kawteam_workspaces.credential_digest. Migration 202610100001 hardcodes my friend's workspace row (id a86971a9-7f0a-4169-9f29-d31a7ca719b1) with a digest of THEIR secret, which I do not have.
- No .env files exist locally. Only .env.example and apps/api/.env.example.
- Profiles (Organiser, Teammate, Observer) switch without login. Server-side permission checks protect mutations, approvals and vendor selection. Only the organiser chooses a final vendor. These rules MUST stay intact.
- Current UI. apps/web/src/components/project-app.tsx renders a sidebar (Overview, Approvals, Calendar, project list with tasks, New project, Vendor library, Connections) plus a top bar with the profile dropdown, and a dashboard (WorkspaceOverview in project-overview.tsx) as the landing page. Chat lives in chat-workspace.tsx and project-workspace.tsx. State lives in workspace-context.tsx.
- I have the Supabase MCP connected to MY OWN Supabase project and the apple-design skill installed.
</context>

<hard_rules>
- NEVER read from, write to, or connect to my friend's Supabase project. Only use the project exposed by my Supabase MCP. Before Phase 1 work, call the MCP to print my project URL and ref and ask me to confirm it is mine.
- NEVER commit secrets. .env files stay git-ignored. NEVER put secrets in any NEXT_PUBLIC_ variable or frontend code. NEVER send KAWTEAM_DATABASE_SECRET through the MCP. Compute its sha256 digest locally and send only the digest.
- Only make changes I requested. Do not add features, new pages, auth, abstractions or refactors beyond this prompt.
- Keep the backend workflow, API contracts, approval rules, idempotency and permission checks unchanged. The new UI reuses existing endpoints and context functions.
- Stop and ask before. Applying any SQL or migration, deleting any file, adding any npm or pip dependency, changing any API route or response shape.
- Read every file you plan to edit before editing it.
</hard_rules>

<phase_0 name="Read and map">
Read README.md, KAWTEAM_BUILD_CHECKLIST.md, docs/PROJECT_MAKEOVER_CHECKPOINT.md, docs/plans/2026-10-10-project-makeover.md, all 4 migrations, apps/api/src/kawteam/config.py, setup_workspace.py, and every file in apps/web/src/components and apps/web/src/app. Output a short map of. Which component renders each current sidebar item and page, which context functions handle create project, upload, chat send, vendor discovery, draft approval and vendor selection, and which CSS files style the shell. No edits in this phase.
</phase_0>

<phase_1 name="Move to my Supabase">
1. Via the Supabase MCP, confirm my project URL and ref with me.
2. List existing tables. If kawteam tables already exist, stop and ask me.
3. Apply migrations 202610100001 to 202610100004 in order, unchanged (ask first).
4. Generate locally with Python `secrets`. A new workspace UUID, KAWTEAM_DATABASE_SECRET, KAWTEAM_SESSION_SECRET and KAWTEAM_GATEWAY_SECRET (48 characters each). Compute sha256 hex of the database secret locally.
5. Via the MCP, run one SQL statement (ask first) that inserts my workspace row into public.kawteam_workspaces with the new UUID, name 'KawTeam' and the new digest. Then ask me whether to delete the friend's workspace row from MY database. Do not commit this insert as a migration.
6. Create apps/api/.env from apps/api/.env.example with SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY fetched from the MCP, the new workspace ID and secrets, COOKIE_SECURE=false, and empty GEMINI_API_KEY and TAVILY_API_KEY.
7. Create apps/web/.env.local with NEXT_PUBLIC_DATA_MODE=api, KAWTEAM_API_URL=http://localhost:8000 and the SAME KAWTEAM_GATEWAY_SECRET.
8. Confirm both .env files are git-ignored. Run `python -m kawteam.setup_workspace` from apps/api using the venv (create the venv and install requirements.txt if missing) to seed Tech Night. Report the seed output.
Done when. Seed prints "Supabase verified" against MY project URL and git status shows no .env files.
</phase_1>

<phase_2 name="Chat-first app, no dashboard">
Replace the dashboard landing with a ChatGPT-style experience.
- Route "/" becomes a new chat. Empty state shows a centred greeting ("What are we working on?"), the chatbox below it, and 3 to 4 suggestion chips (for example "Start a new project", "Find shirt printing vendors for 50 shirts within RM2,000", "Show what needs my approval").
- Chatbox is a single rounded composer pinned to the bottom once messages exist, with a paperclip for uploads, auto-growing textarea, Enter to send, Shift+Enter for newline, and a send button.
- Messages render as a centred column (max width about 760px). User messages right aligned in a soft bubble, assistant messages full width without a bubble.
- The chat MUST support these actions by calling the existing context functions and endpoints.
  1. Create project. A message like "Start a project called Tech Night" creates it and navigates to that project's chat. If intent detection needs the AI provider and no key is set, show an inline "Create project 'X'" confirm card instead of guessing.
  2. Upload files. Paperclip uploads to the current project with the existing limits and error messages. On the "/" chat, ask which project or offer to create one first.
  3. Find vendors and draft enquiry. Reuse the existing supplier request flow and show vendor shortlists and enquiry drafts as cards inside the conversation.
  4. Approve and choose inline. Draft approval and final vendor choice appear as buttons inside the relevant message card. Buttons are hidden or disabled for profiles without permission, and the server check stays the source of truth.
- Remove the top bar dashboard elements and the WorkspaceOverview landing. Keep a minimal top bar with only the mobile menu button and the current chat or project title.
- Remove dead dashboard code only after listing the files and getting my approval.
Done when. "/" shows the chat, all 4 actions work for the Organiser against my Supabase, and an Observer cannot approve or choose.
</phase_2>

<phase_3 name="Sidebar">
Rebuild the left sidebar in this exact order.
1. KawTeam wordmark and a "New chat" button.
2. Overview (expandable). Sub-items Recent activity, Approvals, Calendar. Each opens a clean panel in the main area. Recent activity lists the latest project, chat and approval events. Approvals reuses ApprovalQueue. Calendar reuses Schedule.
3. Projects. List of projects with their tasks nested under the selected project, and a "New project" button (disabled for Observer). Clicking a project opens that project's chat. Keep the project Files and Assistant settings reachable from the project chat header.
4. Connections. One page combining the Vendor library (all past vendor info), past supplier requests with their outcome reports, and AI provider status (the existing Connections component).
5. Profile switcher pinned to the bottom of the sidebar, ChatGPT style. Avatar, name, role, and a menu to switch between Organiser, Teammate and Observer with no login. Remove the profile dropdown from the top bar.
- Keep existing routes working or redirect old ones (/approvals, /calendar, /vendors, /connections, /projects/[id], /projects/[id]/tasks/[taskId]) to the new locations. No 404s.
- Mobile. Sidebar becomes a slide-in drawer with a backdrop, as now.
Done when. Every sidebar item opens the right view, old URLs still resolve, and the profile switch updates permissions immediately.
</phase_3>

<phase_4 name="Apple design polish">
Invoke the apple-design skill and apply it to the whole web app.
- System font stack (-apple-system, SF Pro, Inter fallback) with correct tracking and leading per size. Clear type scale.
- Restrained neutral palette with one accent colour, generous spacing, 12 to 16px radii, hairline separators.
- Translucent sidebar and composer using backdrop blur with a solid fallback.
- Spring-based transitions for sidebar expand, drawer open, message appear and card actions. Interruptible, short, never blocking input.
- Respect prefers-reduced-motion and prefers-color-scheme (light and dark).
- Visible focus rings, 44px minimum touch targets, WCAG AA contrast.
- Use CSS and existing libraries only. Ask before adding any animation dependency.
Done when. The app looks consistent in light and dark at 375px and 1440px widths.
</phase_4>

<phase_5 name="Verify">
Run and report pass or fail for each. In apps/api `.venv/Scripts/python.exe -m pytest -q` and `.venv/Scripts/python.exe -m ruff check src tests`. In apps/web `npm run test`, `npm run lint`, `npm run typecheck`, `npm run build` (stop the dev server first). Fix only failures caused by your changes. Update existing tests that referenced the removed dashboard instead of deleting them. Then update README.md sections that describe the dashboard, the sidebar and Supabase setup so they match the new app. Do not change the original blueprint file.
Final output. A checklist table of every requirement in this prompt with Done or Not done, plus the exact commands I run to start both servers.
</phase_5>

<stop_conditions>
- Stop and ask if any requirement conflicts with the existing permission or approval logic.
- Stop and ask if a fix attempt for the same failing test or build error fails 3 times.
- Stop at the end of every phase and wait for "continue".
</stop_conditions>
```

Setup before pasting. Connect the Supabase MCP in Claude Code to your own project and sign in with your own Supabase account first.

This prompt is for an agentic tool with real system access. Review the scope locks, forbidden actions and stop conditions before pasting. Confirm file paths, directories and permissions match the actual project.
