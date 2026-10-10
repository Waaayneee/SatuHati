# KawTeam project workspace makeover

User has explicitly authorised autonomous design recommendations and implementation without clarification while away.

## Design

Recommend a project hub with focused workspaces. A pure chat list hides approvals and dates; a generic metrics dashboard obscures work. The project hub provides calendar, project rows, relevant updates and approval queue. Projects cover events and other work without assuming everything is an event. Optional Tasks organise independent conversations without requiring a task before chatting.

Visual direction: minimal operational software, warm white surfaces, deep teal #00545f navigation, lime #d6fb00 accents and pale lime #ecffb6 selection. Compact sans typography, clean lines, modest radii, no decorative serif slogans, oversized hero or fake progress metrics. Use shadcn accessible primitives with custom styling.

Projects have Overview/Chat, Tasks, Files, Approvals, Vendors and assistant settings. Sidebar persists project names with expandable task conversations. General is the default assistant workflow; allow Automatic, Research first and Use existing vendor routes. Settings contain instructions and shortlist cap up to three. Existing vendor reuse must preserve identity/history while clearing price, quantity fit, arrival and approval so a new request needs a new quote. Never pretend an old 50-shirt price is valid for 20 shirts. Unknown or ambiguous vendor references prompt clarification. Human selects final supplier and approves exact outgoing messages.

## Implementation plan

1. Backend: add validated project settings/tasks, separate task thread scope, correct general/research/direct-liaison routing and plans. Add behavior tests first. Use additive scoped-chat RPC; retain existing records and approval boundaries. Apply migration and test existing and task conversations. No live email or WorkBuddy integration.
2. shadcn: connect configured stdio MCP, inspect/install Dialog, DropdownMenu, Tabs, Calendar, Button. Preserve credentials/config. Style own product shell instead of using a dashboard template.
3. Frontend: replace shell/home and chat. Project creation, sidebar list, global approval queue, live derived calendar/update agenda; project/task chat, upload/files, settings and known-vendor reuse. Preserve secondary supplier evidence and approval views in new styling.
4. Verify: backend role/scope/repeat-quote tests, TypeScript/lint/build, production browser creation/tasks/settings/upload/chat isolation/reuse/approvals/calendar/responsive layouts, visual screenshot inspection. Independent code review and fix important findings.

No questions or approval gate is needed: the user's explicit instruction authorises making these design choices and proceeding. Existing repository is unborn, so no worktree/commit is created solely for this revision. Plan and checkpoints remain reviewable files.
