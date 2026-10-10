# KawTeam Glass Restyle Claude Code Prompt

Paste everything inside the block below into Claude Code, opened at the root of the `AiDormathon 26` folder. Reference images live in `docs/design-references/2026-10-11-glass-restyle/`.

```text
You are a senior frontend engineer and visual designer working on KawTeam (Next.js App Router in apps/web, FastAPI in apps/api, Supabase). Your job is a VISUAL RESTYLE of the web app plus ONE small chatbox feature. Work in 6 phases. STOP at the end of every phase, print a short summary of what changed, which files were touched and the verification results, and wait for my "continue" before starting the next phase.

<goal>
Make KawTeam look premium, light mode, with soft aurora gradients and an iPhone style liquid glass material, inspired by the reference images. Make the chatbox taller and glass. Add a "Projects" button inside the chatbox, bottom left, that links the chat message to a chosen project. Switch every piece of text to a self-hosted Helvetica clone at a larger, display-style scale so the UI has less dead space.
</goal>

<references>
- Folder docs/design-references/2026-10-11-glass-restyle/ holds 8 PNG references and a README.md. Read the README first, then open and look at every image before designing anything.
- 07-azinsy-landing.png is the primary light mode reference. 04-aurora-forest-palette.png is the reference for the glass material. 03 and 06 are the reference for the aurora glow and film grain, but on a LIGHT base.
- These are mood references. Do not copy logos, wordmarks, illustrations or layouts. The app stays LIGHT MODE even where references are dark.
</references>

<context>
- Styling is plain CSS, no CSS modules. apps/web/src/app/globals.css imports, in order, tailwindcss, legacy.css, project.css, chat.css, theme.css. theme.css loads last and holds the KawTeam tokens (--kt-*), the sidebar, menus, composer, cards, buttons, focus, reduced-motion and reduced-transparency fallbacks. Older variable names (--canvas, --paper, --ink, --serif, --sans and so on) alias the --kt-* tokens at the top of theme.css.
- Font is set once in --kt-font. legacy.css and project.css use var(--serif) and var(--sans), which both resolve to --kt-font. There are roughly 370 hard-coded font-size declarations across legacy.css, project.css, chat.css and theme.css.
- Shell. apps/web/src/components/project-app.tsx renders the sidebar (.kt-sidebar, currently dark translucent teal), top bar and main area.
- Chat. apps/web/src/components/chat-ui.tsx exports the shared Composer (attach button, auto-growing textarea capped at 200px, send button). It is used by chat-home.tsx (NewChat, the home / new chat screen) and project-workspace.tsx (ProjectWorkspace, the chat inside a project or task).
- In chat-home.tsx, handle(text) checks createIntent and approvalIntent, then routes a message to a project with send(text, projectId) if exactly one project name is mentioned, otherwise shows a "Which project is this for?" pick card. attach(files) shows the same pick card and then calls upload(files, projectId). Projects are state.events from useDemo().
- apps/web/src/components/ui/dropdown-menu.tsx is an existing Radix dropdown wrapper. Use it for the project menu.
- Profiles are Organiser, Teammate and Observer. Observer is read-only. These rules must stay intact.
- apps/web/AGENTS.md says this Next.js version has breaking changes. Read the relevant guide in apps/web/node_modules/next/dist/docs/ before using next/font or any Next API.
- The working tree may have uncommitted changes on the current branch.
- I develop on Windows with PowerShell.
</context>

<hard_rules>
- Only make the changes in this prompt. No new pages, no backend changes, no API route or response shape changes, no changes to approval, permission or idempotency logic.
- Do not touch apps/api, supabase, or any .env file.
- Stop and ask before adding any npm dependency, downloading any file, or deleting any file.
- Read every file before editing it.
- Keep the dark palette block (:root[data-theme="dark"]) untouched. The app stays light.
- Keep and extend the existing accessibility work. Visible focus rings, 44px hit areas, prefers-reduced-motion, prefers-reduced-transparency, @supports fallbacks for backdrop-filter, prefers-contrast.
- Body text and labels must meet WCAG AA contrast (4.5 to 1) on top of the glass, checked against the brightest part of the aurora behind it. Lime #d6fb00 is a FILL color only, never text on a light surface.
- No SVG displacement or refraction filters for the glass. They are Chrome only and expensive. Glass is built from backdrop-filter, gradients, borders and shadows.
- Animate only transform and opacity. Never animate backdrop-filter, filter blur or box-shadow in loops.
</hard_rules>

<design_spec>
PALETTE (blend). Keep the existing brand tokens. Teal #00545f is the primary action color (buttons, send, links, focus). Lime #d6fb00 and pale lime #ecffb6 stay as highlight, selection and the New chat button. Add background-only tokens for the aurora, for example --kt-aurora-lime #d6fb00, --kt-aurora-mint #b9f0d0, --kt-aurora-emerald #1f9a6a, --kt-aurora-forest #1f5f3a, --kt-aurora-teal #00545f. Forest green, emerald and mint appear ONLY inside the aurora, never on controls. New base background is a warm off-white around #f5f9ef.

AURORA BACKGROUND. A fixed, full-viewport layer behind the whole app (body::before and body::after, or one aria-hidden div in layout.tsx, whichever is cleaner). 4 or 5 large, very soft radial-gradient blobs (lime near the top left, mint and emerald on the right, a faint teal and forest wash at the bottom), each at low opacity so the page still reads as light. Blobs drift very slowly (40 to 70 second alternate loops, translate and scale only). Add a film grain overlay using an inline SVG feTurbulence data URI at about 5 to 8 percent opacity. Under prefers-reduced-motion the aurora is static. Every page background that is currently solid (.kt-main, .kt-topbar, .workspace-page, .project-workspace, the composer dock fade) becomes transparent so the aurora shows through.

LIQUID GLASS MATERIAL. Define reusable tokens and one or two utility classes in theme.css, for example
  --kt-glass-fill: linear-gradient(135deg, rgba(255,255,255,.66), rgba(255,255,255,.38))
  --kt-glass-fill-strong: same idea at about .82 / .6 for menus, dialogs and the composer
  --kt-glass-blur: blur(28px) saturate(180%)
  --kt-glass-edge: 1px solid rgba(255,255,255,.75)
  --kt-glass-highlight: inset 0 1px 0 rgba(255,255,255,.95), inset 0 -1px 0 rgba(255,255,255,.3), inset 0 0 24px rgba(255,255,255,.25)
  --kt-glass-shadow: 0 24px 60px rgba(0,84,95,.12), 0 4px 12px rgba(0,84,95,.06)
Add a specular rim with a ::before pseudo element using a gradient border (mask-composite exclude) that is brighter at the top left, like iOS liquid glass. Radius scale goes up for the premium feel. Cards 24px, composer 28px, menus and dialogs 22px, pills 999px. Apply glass to the sidebar, top bar, composer, cards (.kt-card, .queue-card, .vendor-record, .connection-card, .activity-list, .request-list, .schedule-panel, .project-context-panel, .project-file-row, .task-tile), chips, tabs, menus and dialogs. Keep the existing solid fallbacks working for no blur support and reduced transparency.

SIDEBAR. Light frosted glass, NOT dark teal. Dark text (--kt-text, --kt-text-2), icons in --kt-text-3, hover is a faint teal tint, selected item is pale lime fill with teal text. The New chat button stays lime with teal text. Brand mark stays lime square with teal letter. Retune all --kt-sidebar-* tokens for the light material and remove any leftover white-on-teal assumptions.

TYPOGRAPHY.
- Font. Self-host TeX Gyre Heros (free Helvetica clone, GUST Font License) from the official GUST e-foundry page or CTAN. It ships Regular, Italic, Bold and Bold Italic only (weights 400 and 700). Ask me before downloading. Place the files in apps/web/src/app/fonts/ (or public/fonts if next/font/local needs it) together with the licence text, and load them with next/font/local in layout.tsx exposing a CSS variable. If .woff2 is not available, use the .otf files as they are. Do not add a converter dependency.
- Set --kt-font to the next/font variable followed by "Helvetica Neue", Helvetica, Arial, sans-serif. Make sure button, input, textarea and select inherit the font. Add font-synthesis: none so no fake bold or italic appears. Weights 500 resolve to 400 and 600 or 650 resolve to 700. Review headings and buttons afterwards so nothing looks too heavy.
- Large display-style scale. Introduce size tokens in theme.css and use them instead of raw numbers in the most visible places.
  --kt-size-xs 13px (kickers, eyebrows, badges), --kt-size-sm 15px (meta text, chips, small buttons), --kt-size-md 18px (body, inputs, nav), --kt-size-msg 17.5px (chat messages), --kt-size-lg 21px (card titles), --kt-size-xl 26px (section headings), --kt-size-2xl 40px (page titles), --kt-size-display 52px (chat empty-state headline).
  Body line-height 1.5, chat messages 1.6, headings 1.05 to 1.15 with tracking from -0.01em (h3) to -0.035em (display). Kickers 13px uppercase with +0.06em tracking.
  Mobile (max-width 650px) display 34px and page titles 30px.
- Then sweep legacy.css, project.css and chat.css. Raise every remaining font-size of 10 to 13px to at least 13px, and scale the rest roughly in line with the new tokens, so no screen keeps the old small text. Keep layouts from breaking. Widen or rewrap where text now overflows.
- Use the reference trick of inline highlight pills in key headings sparingly, for example the word "KawTeam" in the empty chat headline sitting in a pale lime capsule.

CHATBOX (two-row glass card). Restructure the Composer in chat-ui.tsx.
- Row 1 is the textarea, full width, min-height about 96px (three lines at 18px), grows with content up to 280px (raise the existing 200px cap), then scrolls.
- Row 2 is a toolbar. Left side has the Projects button then the attach (paperclip) button. Right side has the round send button (teal fill, white arrow, 44px).
- Whole card uses --kt-glass-fill-strong, 28px radius, specular rim and glass shadow. On focus-within the rim brightens and a soft teal focus ring appears.
- Composer max-width about 960px. The docked composer in a thread floats over the messages with no solid fade band. Increase .kt-chat-scroll bottom padding so the last message is never hidden behind the taller card.
- Keep Enter to send, Shift+Enter for a new line, IME composition handling and all existing disabled states.

PROJECTS BUTTON (inside the chatbox, bottom left).
- Composer gets new optional props, for example projects (list of {id,name}), selectedProjectId, onSelectProject(id or null), lockedProjectName. If neither projects nor lockedProjectName is passed, the button is not rendered.
- New chat (chat-home.tsx). Unselected, it is a glass pill with a folder icon and the label "Projects". Clicking opens the existing dropdown menu listing state.events by name, with a check on the selected one and a short "No projects yet" disabled row when the list is empty. When a project is chosen the pill turns pale lime with teal text showing the project name (truncate long names with an ellipsis) and a small x button that clears the selection.
- Wiring in chat-home.tsx. Keep selectedProjectId in state. In handle(text), keep the createIntent and approvalIntent branches first and unchanged. After those, if a project is selected, call send(text, selectedProjectId) directly and skip the mention matching and the "Which project is this for?" card. In attach(files), if a project is selected, call upload(list, selectedProjectId) directly. Observer still gets the read-only message exactly as today. Clicking a starter chip does not clear the selection.
- Project chat (project-workspace.tsx). Pass lockedProjectName (project name, plus " · task name" when inside a task). It renders as the same pale lime pill but not clickable, with aria-disabled and a tooltip or title like "This chat belongs to <project>". No x button.
- Accessibility. The button has an aria-label that states the current selection, the menu is keyboard navigable (Radix handles it), and the hit area stays at least 44px.

OTHER SURFACES.
- Buttons. Default stays teal with white text but gets a subtle top-to-bottom gradient and inner highlight. Outline and ghost buttons become glass. Pills where the references use pills.
- Chips under the empty chat become glass pills at 15px.
- User message bubbles use pale lime with a faint glass edge. Assistant messages stay unboxed on the aurora, with text in --kt-text for contrast.
- Project tabs, status labels, toasts, the profile menu and dialogs follow the glass and radius scale.
- Do not change copy text except the headline highlight pill.
</design_spec>

<phase_0 name="Safety, read and map">
1. Run git status. If there are uncommitted changes, STOP and ask me whether to commit them first. Then create a new branch named glass-restyle from the current branch.
2. Read docs/design-references/2026-10-11-glass-restyle/README.md and view all 8 images. Read globals.css, theme.css, chat.css, project.css, legacy.css, layout.tsx, project-app.tsx, chat-ui.tsx, chat-home.tsx, project-workspace.tsx, components/ui/dropdown-menu.tsx and apps/web/AGENTS.md, plus the next/font docs inside node_modules/next/dist/docs/.
3. Start the dev server and take baseline Playwright screenshots (the playwright package is already a devDependency) of the home chat, a project chat with messages, the overview page and one card-heavy page, at 1440x900 and 390x844. Save them to docs/design-references/2026-10-11-glass-restyle/before/.
4. Output a short map of which selectors style the shell, composer, cards, tabs, menus and dialogs, and your plan for the font download. No style edits in this phase.
</phase_0>

<phase_1 name="Foundations">
Font (after my OK to download), --kt-font, font inheritance and font-synthesis, the size tokens, palette and aurora tokens, glass tokens and utility classes, the aurora background with grain, and transparent page backgrounds. Verify the font actually loads (computed font-family in the browser) on the home page.
</phase_1>

<phase_2 name="Shell">
Light frosted glass sidebar with retuned --kt-sidebar-* tokens, glass top bar, transparent main area, glass profile menu and dialogs, mobile drawer still working.
</phase_2>

<phase_3 name="Chatbox and Projects button">
Two-row glass Composer, the Projects button with menu, chip and locked states, the chat-home.tsx and project-workspace.tsx wiring, dock and scroll padding changes. Test by hand in the browser. Pick a project then send a message that names no project and confirm it goes straight to that project's chat without the pick card. Attach a file with a project selected and confirm it uploads to that project. Clear the selection and confirm the old pick card flow still works. Confirm the locked pill inside a project chat. Confirm Observer is still read-only.
</phase_3>

<phase_4 name="Surfaces and type sweep">
Glass cards, chips, tabs, buttons, status labels, toasts, message bubbles, the headline highlight pill, and the font-size sweep across legacy.css, project.css and chat.css. Check every route renders without overflow at 1440 and 390 widths.
</phase_4>

<phase_5 name="Verify and report">
1. In apps/web run npm run typecheck, npm run lint, npm run test and npm run test:e2e. Fix anything this work broke.
2. Take the same Playwright screenshots as Phase 0 into docs/design-references/2026-10-11-glass-restyle/after/ and compare them with the references. List what matches and what still differs.
3. Check contrast of body text, meta text and button labels on glass against the brightest aurora area and report the ratios.
4. Check reduced motion (aurora static), reduced transparency (solid surfaces), and a browser without backdrop-filter (solid fallback).
5. Print a final summary of files changed and anything you chose not to do. Do not commit until I say so.
</phase_5>
```
