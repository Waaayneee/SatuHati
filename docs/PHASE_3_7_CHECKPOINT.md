# KawTeam — chat-first checkpoint

10 October 2026. This supersedes the former form-first Phase 2 prototype. User scope: chat by event name with uploaded proposals/plans/budget, no login, final vendor choice by a human, free hosting, WorkBuddy deferred.

**Flow:** name event → upload documents once → saved event memory → conversation → scoped supplier request → configured discovery → evidence/unknown terms → approved controlled outreach → stored reply → recommendation → organiser decision.

Home `/` is chat; `/events` is event memory; `/casebook` is secondary supplier work; `/brief/new` now opens chat. Supabase is the source of truth. Local storage holds only event/profile preferences in API mode.

| Phase | Delivered | Open |
|---|---|---|
| 3 | Three applied migrations; protected RPCs; signed profile sessions; server permissions; atomic uploads and chat/case commits; revisions/idempotency | Deployment; personal authentication intentionally excluded |
| 4 | Event-scoped retrieval/citations; typed Gemini adapter; capped/deduplicated Tavily adapter; provenance, unknowns and eligibility | Keys, live provider verification, confirmed contacts/direct quotations |
| 5 | Controlled supplier; edit/approve/reject; exact revision/hash; expiry; single-use send; persisted replies; three-round cap | External email/webhooks and autonomous orchestration |
| 6 | Previous health-only feasibility scaffold preserved | WorkBuddy execution explicitly deferred |
| 7 | Ranked outcome report; pending/no-deal states; evidence references; simulated comparable savings; print layout; explicit human choice | Final deployed print/demo QA |

Absent keys produce an honest connection note, not fake AI execution. Public search results are unquoted candidates. Only the sample tote case has simulated offers, replies and savings. Other cases cannot load those quotes. No external email, order, payment or agreement is issued.

## Persistence and access

Tables `kawteam_workspaces`, `kawteam_records`, `kawteam_actions` have RLS enabled and direct anon/authenticated privileges revoked. RPCs check a workspace-specific random backend credential against a stored SHA-256 digest. Publishable key alone gives no data access. SQL is parameterised and function search paths fixed.

Next.js forwards allowlisted routes, a signed HttpOnly role cookie and a separate server gateway secret. FastAPI checks role permissions from the cookie. Production uses secure cookies. Anyone in this intentionally public demo can switch to Organiser; private user accounts are not claimed.

Uploads lock an event and store file plus derived memory together. Content duplicates return sanitised metadata. Chat appends against the current locked thread and commits case/assistant together; deterministic case IDs and request markers prevent duplicate work. Changed message text with the same request ID is rejected. The browser retains an unsuccessful request ID for retry and consumes successful POST state directly.

Uploaded documents are untrusted reference content. The model receives selected-event excerpts, at most six chunks and recent conversation. Explicit labelled budget/deadline values override memory; incidental deposits and proposal creation dates do not. Generic or ambiguous missing terms require clarification rather than guessing.

Supabase advisors report informational no-policy notices for deliberate deny-all direct access, plus executable security-definer RPC warnings. The RPCs are intentionally secret-gated. The live check confirms wrong credentials fail. Review the [advisory guidance](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable) before expanding this security model beyond a shared demo.

## Verification

Python tests cover permissions, conflicts, retries, exact/expired approvals, send consumption, replies, outcomes, memory parsing, invalid AI output and persistent chat. TypeScript tests cover human decisions, role restrictions, scope, unknown shipping and restore/date validation. Live database checks cover concurrent duplicate uploads/user messages/assistant completion, one case, sanitised metadata and invalid credentials.

Production browser checks create an event, upload/preview a proposal, override budget in chat, reload, open saved request/report, switch observer permissions, and check layouts at 390/768/1280/1440px. Desktop/mobile screenshots inspected. Controlled outreach browser checks prepare/approve/send/reply, consumed approval and unchanged human selection; original sample restored afterward. Next.js production build, TypeScript, ESLint and Ruff verified. Live AI/search accounts are not verified without keys.

## Remaining integrations

Configure free-tier AI/search keys and run live smoke tests. Add real email with verified recipients, exact-message approval, send deduplication and validated delivery/reply receipts. When requested, implement WorkBuddy orchestration on these shared services, checkpoint/resume, automatic task planning, bounded negotiations, backup switching and actual tool-call evidence. The track's meaningful WorkBuddy execution requirement is not yet satisfied.
