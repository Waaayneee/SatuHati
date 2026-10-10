# KawTeam Motion and Polish Claude Code Prompt

Paste everything inside the block below into Claude Code, opened at the root of the `AiDormathon 26` folder. This builds on top of the glass restyle (KAWTEAM_GLASS_RESTYLE_PROMPT.md).

```text
You are a senior frontend engineer and motion designer working on KawTeam (Next.js App Router in apps/web, FastAPI in apps/api, Supabase). The liquid glass restyle is already in place. Your job now is a POLISH pass with four parts. A bigger glass calendar, a background that reacts to navigation, playful hover effects, and light bouncy animations on all elements. Plus a legibility pass. Work in 6 phases. STOP at the end of every phase, print a short summary of what changed, which files were touched and the verification results, and wait for my "continue" before starting the next phase.

<goal>
Make KawTeam feel fun, playful and a little bouncy while staying FAST. Every animation must be LIGHT. The app must never feel slower, laggy or janky because of this work. If an effect cannot hold 60fps on a mid-range laptop with 4x CPU throttling, cut it or simplify it.
</goal>

<context>
- Styling is plain CSS. apps/web/src/app/globals.css imports tailwindcss, legacy.css, project.css, chat.css, theme.css in that order. theme.css loads last and holds the --kt-* tokens, glass tokens (--kt-glass-*), size tokens (--kt-size-*), the aurora and the reduced-motion / reduced-transparency / @supports fallbacks.
- Aurora background. layout.tsx renders <div className="kt-aurora" aria-hidden="true"> with 5 <span> blobs. theme.css animates each span with the kt-drift keyframes (transform based, 47 to 69 second loops) plus a grain ::after.
- Navigation. apps/web/src/components/project-app.tsx reads usePathname() and switches main content between New chat (/), project tabs (/projects/<id>/<tab>, tab defaults to chat), tasks, /activity, /approvals or /inbox, /calendar, /connections or /vendors, and supplier cases.
- Calendar. apps/web/src/components/project-overview.tsx renders Schedule (section.schedule-panel, plus .large-schedule on the /calendar page) with the shadcn Calendar from components/ui/calendar.tsx (react-day-picker v10) using className kt-calendar. Sizes come from --cell-size in project.css (about 2.18rem default, 3rem for .large-schedule, with several media query overrides around lines 213 to 303). theme.css line ~340 strips glass from the day buttons.
- Font is TeX Gyre Heros with ONLY weights 400 and 700 and font-synthesis none. Any "bolder" text means 700. 500 and 600 render as 400 or 700.
- No animation library is installed. Do NOT add framer-motion or any other dependency. Everything is plain CSS plus a few lines of React where needed.
- Profiles are Organiser, Teammate and Observer. Observer is read-only. Keep these rules intact.
- apps/web/AGENTS.md says this Next.js version has breaking changes. Read the relevant guide in apps/web/node_modules/next/dist/docs/ before using any Next API.
- I develop on Windows with PowerShell.
</context>

<hard_rules>
- Only make the changes in this prompt. No new pages, no backend changes, no API, approval, permission or idempotency changes. Do not touch apps/api, supabase or any .env file.
- Stop and ask before adding any npm dependency, downloading any file, or deleting any file.
- Read every file before editing it.
- Do not change copy text.
- PERFORMANCE RULES (non negotiable)
  - Animate ONLY transform and opacity (including the individual translate, scale and rotate properties). Never animate width, height, top, left, margin, padding, box-shadow, filter, backdrop-filter or background-position.
  - For hover glow or shadow changes, put the bigger shadow on a ::after pseudo element and fade its opacity instead of animating box-shadow.
  - No JavaScript animation loops, no requestAnimationFrame loops, no scroll listeners, no mousemove listeners for effects. CSS transitions and keyframes only. The only JS allowed is setting a data attribute or a CSS variable when the route changes.
  - Durations stay short. Hover 160 to 260ms, press 90 to 140ms, entrances 280 to 450ms, route background shift 900 to 1400ms (one shot, not a loop).
  - Entrance stagger is capped at 8 items and 40ms per step. Item 9 onwards uses the step 8 delay.
  - Do not leave will-change on elements permanently, except the existing aurora spans.
  - Keep hover scale small on elements that have backdrop-filter (max scale 1.02), because scaling blurred glass is costly. Prefer translateY lifts.
  - Every new animation is disabled or reduced to a simple opacity fade under prefers-reduced-motion.
  - Hover effects only apply under @media (hover: hover) and (pointer: fine) so touch devices do not get sticky hover states.
- Keep visible focus rings, 44px hit areas, prefers-reduced-transparency, @supports fallbacks and prefers-contrast working.
- Text contrast must meet WCAG AA (4.5 to 1) everywhere, checked against the brightest aurora area. Lime #d6fb00 is a FILL color only, never text on a light surface.
</hard_rules>

<design_spec>
MOTION TOKENS (add to theme.css)
  --kt-ease-bounce: cubic-bezier(.34,1.56,.64,1)   (soft overshoot, used for hover lift and pop ins)
  --kt-ease-spring: cubic-bezier(.22,1.2,.36,1)    (gentler overshoot, used for larger surfaces)
  --kt-ease-out: cubic-bezier(.16,1,.3,1)          (no overshoot, used for fades and the background)
  --kt-dur-press: 120ms, --kt-dur-hover: 220ms, --kt-dur-enter: 380ms, --kt-dur-bg: 1200ms
Bounce must feel LIGHT. One small overshoot, never a wobble that keeps going.

1. BIGGER GLASS CALENDAR
- /calendar page. The schedule panel uses the full content width. On desktop (min-width 900px) lay it out as two columns, a big calendar on the left (about 60 percent) and the agenda list on the right. On smaller screens stack them.
- Calendar cells scale with the space. Use --cell-size: clamp(2.75rem, 5.2vw, 4.5rem) for .large-schedule on desktop, and make sure 7 columns still fit at 390px width with no horizontal scroll. Clean up the old --cell-size overrides in project.css media queries so they do not fight the new value.
- Overview panel calendar (non large) also grows a bit, around 2.6rem cells, while still fitting its panel.
- Day numbers use --kt-size-md on the big calendar. Month caption uses --kt-size-xl at weight 700. Weekday labels use --kt-size-xs uppercase with tracking, darker color for legibility.
- Glass. The whole calendar sits on a glass card (--kt-glass-fill-strong, specular rim, glass shadow, 24px radius). Each day cell is a soft rounded square (14px radius) with a very faint glass fill on hover only. Today gets a teal ring. The selected day is a teal fill with white bold text and a tiny pop in (scale .85 to 1 with --kt-ease-bounce). Days with a scheduled item keep the dot, but the dot becomes a small lime pill with a thin teal edge so it stays visible. Outside month days are lighter. Nav arrows (previous and next month) are round glass buttons, 44px hit area.
- Month change. When the month changes, the grid fades and slides 12px in the direction of travel (opacity plus translateX only, about 260ms).
- Agenda items on the right are glass rows with the same hover effect as cards.

2. REACTIVE BACKGROUND (aurora reacts to navigation)
- Add a small client component (or a few lines in project-app.tsx) that reads usePathname() and sets data-view on the .kt-aurora element (or on <html>). Views are chat (home and project chat), overview (project overview tab), tasks, files or other project tabs, activity, approvals, calendar, connections, cases. Use whatever keys match the real routes.
- Per view, define a small set of CSS variables on .kt-aurora[data-view="..."], one translate and scale per blob, for example --b1-x, --b1-y, --b1-s. Apply them with the INDIVIDUAL translate and scale properties on each span, with transition: translate var(--kt-dur-bg) var(--kt-ease-spring), scale var(--kt-dur-bg) var(--kt-ease-spring), opacity 800ms. The existing kt-drift keyframes keep running on transform, so the drift and the route shift stack without fighting.
- Each view should feel different but on brand. For example chat keeps lime top left, overview pulls the blobs toward the center and slightly bigger, calendar shifts mint and emerald to the right, approvals warms with more lime, connections drifts toward teal. Only change position, scale and opacity per blob. Do not add new blobs and do not animate gradients or colors.
- Add a light "breath" on every route change. A one shot keyframe on the aurora wrapper that scales from 1 to 1.03 and back over about 900ms. Restart it by toggling a data attribute or by keying a tiny element, not by remounting the whole aurora.
- Main content enters on route change with a quick fade and 8px rise (the main element already gets a new key per project tab, reuse that and add the same for other pages if cheap).
- Under prefers-reduced-motion, the background still changes per view but instantly with no transition, and no breath.

3. PLAYFUL HOVER (not just darken)
Replace darken-only hovers with a mix of these. Use them consistently by component type.
- Cards and glass panels (.kt-card, .queue-card, .vendor-record, .connection-card, .project-file-row, .task-tile, agenda items, sidebar project items). Lift translateY(-3px) with --kt-ease-bounce, a soft brighter glow via a ::after shadow layer fading in, and a specular sheen. The sheen is a diagonal white gradient stripe on a pseudo element that sweeps across once (translateX from -120% to 120%, about 600ms) when hover starts. It must not loop.
- Buttons. Hover lifts 2px and scales to 1.03 (non glass) or 1.02 (glass). Press scales to .96 with --kt-dur-press, then springs back. The teal primary button gets a slightly brighter inner highlight on hover.
- Icon buttons and nav icons. The icon inside does a small playful move on hover, chosen per icon type. Arrow icons nudge 3px in their direction. The paperclip tilts -12deg. The send arrow nudges up and right. Plus icons rotate 90deg. Folder and calendar icons do a tiny hop (translateY -2px and back). Sidebar nav icons do a tiny hop.
- Chips and pills. Hover pops to scale 1.04 with bounce, press .95.
- Sidebar nav items. Hover slides the label 3px right and shows a faint teal tint pill behind it that scales in from .9.
- Links with an arrow. Arrow nudges right.
- Calendar days. Hover pops to scale 1.08 with a faint glass fill.
- Tabs. The active tab indicator slides between tabs (transform translateX plus scaleX on a single indicator element) instead of jumping. If that needs measuring in JS, use one ResizeObserver free approach, for example CSS anchor positioning with a plain fallback, or just a fade if it gets complex. Keep it light.
- Keep focus-visible styles at least as visible as hover styles.

4. LIGHT BOUNCY ENTRANCES FOR ALL ELEMENTS
- Add one reusable keyframe, kt-pop-in (opacity 0 to 1, translateY 10px to 0, scale .98 to 1) using --kt-ease-spring and --kt-dur-enter.
- Apply it to cards, panels, list rows, chips, chat messages, the composer, the calendar and dialog content when they first mount. Stagger siblings with a --i index (style={{'--i': index}} where lists are rendered, or :nth-child up to 8 in CSS). Delay is min(var(--i), 8) times 40ms.
- New chat messages pop in from below (user bubble slightly from the right, assistant fade up). Only the newest message animates, not the whole history on load.
- Dialogs and menus. Scale from .96 with --kt-ease-bounce and fade, about 220ms. Toasts slide up 12px with a tiny bounce.
- Badges and counters that change value do a quick scale 1 to 1.15 to 1 bump.
- The empty chat headline lime highlight pill does a single gentle pop on load.
- Nothing animates on every re-render. Entrances run once on mount only. Use animation-fill-mode both so there is no flash.

5. LEGIBILITY PASS
- Bolder text (weight 700, since the font only has 400 and 700). Page titles, section headings, card titles, project names in the sidebar, the selected sidebar item, tab labels (active tab only, inactive stay 400), button labels, chip labels, agenda item project names, calendar month caption and day numbers on the big calendar, table headers, status labels. Body text, chat messages and meta text stay 400.
- Darker text where it is too light. Raise --kt-text-2 and --kt-text-3 contrast so meta text, kickers, weekday labels, timestamps and placeholder text reach at least 4.5 to 1 on glass over the brightest aurora area. Placeholders at least 4.5 to 1 as well.
- Glass backgrounds. Make text heavy surfaces LIGHTER and more opaque so text reads cleanly (cards, panels, the calendar card, the agenda, menus, dialogs, the composer). For example raise --kt-glass-fill to about rgba(255,255,255,.78) to .56 and --kt-glass-fill-strong to about .9 to .74. Keep the blur so it still looks like glass.
- Make some small surfaces DARKER where they sit on bright aurora and look washed out. Inactive chips, status labels, the tab bar track and secondary pills get a slightly deeper fill, for example a faint teal tint like rgba(0,84,95,.08) to .12 over the glass, with dark text. The sidebar can get slightly more opaque so nav text stays crisp over the lime blob.
- Add a very subtle text-shadow only on large headings that sit directly on the aurora (0 1px 0 rgba(255,255,255,.6)) if it helps. Do not add text shadows to body text.
- Report before and after contrast ratios for body text, meta text, kickers, placeholders, button labels and chip labels.
</design_spec>

<phase_0 name="Safety, read and map">
1. Run git status. The glass restyle may still be uncommitted on the glass-restyle branch. If there are uncommitted changes, STOP and ask me whether to commit them first. Then create a new branch named motion-polish from the current branch.
2. Read globals.css, theme.css, project.css, chat.css, legacy.css, layout.tsx, project-app.tsx, project-overview.tsx, components/ui/calendar.tsx, chat-ui.tsx, chat-home.tsx, project-workspace.tsx, and apps/web/AGENTS.md.
3. Start the dev server and take baseline Playwright screenshots (playwright is already a devDependency) of home chat, a project chat with messages, a project overview, /calendar and /approvals, at 1440x900 and 390x844. Save them to docs/design-references/2026-10-11-motion-polish/before/.
4. Record a baseline Chrome performance trace of switching between home, a project overview and /calendar with 4x CPU throttling, and note the frame rate and any long tasks.
5. Output a short map of the selectors for calendar, cards, buttons, chips, tabs, sidebar items, messages, dialogs and the aurora, the list of route keys you will use for data-view, and your plan. No edits in this phase.
</phase_0>

<phase_1 name="Legibility">
Font weights, text colors, glass fill opacity changes (lighter and darker), placeholder contrast, optional heading text-shadow. Report contrast ratios before and after.
</phase_1>

<phase_2 name="Bigger glass calendar">
Calendar size, layout, glass card, day cells, today, selected, scheduled dots, nav buttons, month change slide, agenda rows. Clean the old --cell-size overrides. Check 1440, 1024, 768 and 390 widths with no overflow.
</phase_2>

<phase_3 name="Motion tokens, hovers and press states">
Motion tokens, all hover effects from section 3, press states, the sliding tab indicator, hover only under (hover: hover) and (pointer: fine), reduced-motion fallbacks.
</phase_3>

<phase_4 name="Entrances and reactive background">
kt-pop-in with stagger, message, dialog, menu, toast and badge animations, the data-view route wiring, per view blob variables with individual translate and scale transitions, the one shot breath, and the main content route enter.
</phase_4>

<phase_5 name="Verify and report">
1. In apps/web run npm run typecheck, npm run lint, npm run test and npm run test:e2e. Fix anything this work broke.
2. Take the same Playwright screenshots into docs/design-references/2026-10-11-motion-polish/after/.
3. Record the same performance trace as Phase 0 with 4x CPU throttling. Report frame rate, long tasks and any layout or paint heavy frames compared with the baseline. If anything got noticeably worse, simplify the culprit and measure again.
4. Check prefers-reduced-motion (no bounces, no sheen, background switches instantly), prefers-reduced-transparency, a browser without backdrop-filter, touch emulation (no sticky hovers), and keyboard focus on every animated control.
5. Print a final summary of files changed and anything you chose not to do or cut for performance. Do not commit until I say so.
</phase_5>
```
