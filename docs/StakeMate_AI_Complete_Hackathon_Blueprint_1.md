# StakeMate AI — Complete Hackathon Blueprint

> **Track:** WorkBuddy Track 2 — Agentic Solutions  
> **Product tagline:** *From First Contact to Final Agreement.*  
> **Core idea:** An AI stakeholder liaison agent powered by Tencent WorkBuddy that discovers, evaluates, engages, negotiates, coordinates, and verifies outcomes with external stakeholders.

---

## Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution and Value Proposition](#3-solution-and-value-proposition)
4. [Primary Use Cases](#4-primary-use-cases)
5. [How Module A and Module B Integrate](#5-how-module-a-and-module-b-integrate)
6. [End-to-End Workflow Example](#6-end-to-end-workflow-example)
7. [Technical Architecture](#7-technical-architecture)
8. [Module A — Discovery, Sourcing, and Evaluation](#8-module-a--discovery-sourcing-and-evaluation)
9. [Module B — Communication and Negotiation](#9-module-b--communication-and-negotiation)
10. [Complete Feature Catalogue and Priorities](#10-complete-feature-catalogue-and-priorities)
11. [Trust, Safety, and Verification](#11-trust-safety-and-verification)
12. [Dashboard, Reporting, and Analytics](#12-dashboard-reporting-and-analytics)
13. [MVP Scope and Build Order](#13-mvp-scope-and-build-order)
14. [Hackathon Demo Scenario](#14-hackathon-demo-scenario)
15. [Judging Strategy](#15-judging-strategy)
16. [Beginner Guide: Integrating Tencent WorkBuddy](#16-beginner-guide-integrating-tencent-workbuddy)
17. [Starter MCP Server Code](#17-starter-mcp-server-code)
18. [Supplier Handoff Data Contract](#18-supplier-handoff-data-contract)
19. [Suggested Technology Stack and Code Components](#19-suggested-technology-stack-and-code-components)
20. [Product Decisions and Important Limitations](#20-product-decisions-and-important-limitations)
21. [Closing Pitch](#21-closing-pitch)
22. [Access Control and Approval Governance](#22-access-control-and-approval-governance)
23. [Build Phases](#23-build-phases)
24. [Phase Coverage Map](#24-phase-coverage-map)
25. [Official References](#25-official-references)

---

## 1. Executive Summary

**StakeMate AI** is an autonomous stakeholder management and negotiation platform for student clubs and societies, small businesses, procurement teams, event organisers, and business development teams. It tackles the time-consuming work involved in locating suitable external stakeholders, evaluating them, communicating, following up, negotiating terms, coordinating meetings, and confirming commitments.

Rather than stopping at recommendations or drafting emails, StakeMate aims to take a user-defined goal through a controlled, tool-enabled workflow and deliver a measurable, verifiable result.

**Central principle:** Finding the right stakeholder is difficult; getting them to respond, agree, and deliver is even harder.

### Core value proposition

One prompt → one goal → end-to-end execution:

1. **Discover** the right people or suppliers.
2. **Engage** them through appropriate channels.
3. **Negotiate** price and terms within user-defined limits.
4. **Coordinate** meetings, messages, and next steps.
5. **Execute** approved actions.
6. **Verify** the outcome and report the result.

### Recommended hackathon direction

Build one shared stakeholder-management engine, demonstrated primarily through **supplier procurement and negotiation**. Add sponsorship acquisition as a second workflow only if time permits. Procurement is especially effective for a demo because judges can observe supplier comparisons, target-price decisions, negotiation responses, and final terms.

---

## 2. Problem Statement

### Pitch-ready problem statement

Students, organisations, and businesses face significant challenges when engaging external stakeholders, including suppliers, sponsors, vendors, and potential collaborators. The process is fragmented, time-consuming, and highly manual, requiring individuals to independently source contacts, evaluate options, initiate communication, negotiate terms, coordinate schedules, and manage follow-ups across multiple platforms.

These inefficiencies often result in missed opportunities, delayed decisions, poor negotiation outcomes, and unnecessary administrative workloads. The challenge is particularly significant for student-led organisations and small businesses that lack dedicated procurement, business development, or stakeholder-management teams.

**How might we leverage agentic AI to autonomously discover, engage, negotiate, and coordinate with external stakeholders, transforming fragmented communication into seamless, goal-driven, end-to-end collaboration?**

### Problem in one sentence

**Finding the right stakeholder is difficult. Getting them to agree, respond, and deliver is even harder.**

### Pain points discovered

- Hard to source suitable external stakeholders.
- Hard to find the right contact person or official contact channel.
- Hard to initiate and sustain communication.
- Hard to liaise across multiple platforms and conversations.
- Hard to follow up consistently.
- Hard to persuade a stakeholder or explain mutual value.
- Hard to find a middle ground that benefits both parties.
- Hard to negotiate a price or package that meets the user's target.
- Hard to coordinate a suitable meeting time.
- Hard to compare quality, price, reliability, reviews, and delivery conditions.
- Hard to manage commitments, action items, and deadlines after meetings.
- Hard to keep the full history and avoid repeating work.
- Student clubs and societies often lack dedicated procurement or partnership teams; small businesses may also lack dedicated staff for these tasks.

---

## 3. Solution and Value Proposition

### What StakeMate does

StakeMate AI is an AI-powered stakeholder engagement platform built on Tencent WorkBuddy. It manages the collaboration lifecycle: from discovering suitable stakeholders to contacting them, negotiating within defined constraints, coordinating next steps, and recording verified outcomes.

### Product positioning

> An autonomous AI stakeholder liaison agent powered by Tencent WorkBuddy that helps organisations discover, engage, negotiate, and collaborate with external partners—turning complex stakeholder management into goal-driven, end-to-end execution.

### Key distinction

A basic chatbot can write a sponsorship email or suggest a counteroffer. StakeMate is intended to go further: find candidates, use tools to compare them, send approved communications through connected services, process replies, replan after a rejection, and return an evidence-backed result.

### Core principles

- User goal and measurable outcome first.
- Research and communication should share a persistent mission state.
- Use structured data for handoffs between modules, not just free-form text.
- Autonomy operates inside user-defined boundaries.
- Every consequential result should be supported by evidence.
- Clearly distinguish live information, estimates, and simulated data.

---

## 4. Primary Use Cases

### Use Case A — Sponsorship Acquisition Agent

A student club needs RM5,000 of sponsorship for a technology event. StakeMate finds relevant companies, scores sponsor fit, prepares personalised proposals, sends approved outreach, tracks replies, negotiates benefits or contributions, and arranges meetings.

**Why it matters:** Relevant for student clubs, societies, conferences, and campus events.

### Use Case B — Autonomous Procurement Agent

An SME needs 300 custom-printed tote bags within a target budget. StakeMate researches suppliers, compares quotations and quality indicators, calculates total costs, negotiates within approved limits, and presents the best verified offer.

**Why it matters:** The result is measurable through price, total cost, delivery terms, quality, and savings against comparable initial quotations.

### Use Case C — Collaboration and Partnership Agent

A business wants a university partner for a workshop. StakeMate identifies potential collaborators, proposes mutual benefits, manages correspondence, schedules meetings, and tracks commitments.

**Recommendation:** Make Use Case B the main demo; use Use Case A as an optional additional workflow.

---

## 5. How Module A and Module B Integrate

### Main distinction

- **Module A — Discovery & Evaluation:** Finds, verifies, compares, filters, and ranks potential stakeholders.
- **Module B — Engagement & Negotiation:** Contacts the shortlist, requests information, follows up, negotiates terms, and coordinates next steps.

They should not be two disconnected tools or two independent agents that do not share information. They are specialised capabilities within a single WorkBuddy-orchestrated workflow.

### Module A → Module B handoff

Module A passes a structured, evidence-backed shortlist to Module B. The handoff should include:

- Stakeholder identity and official contact channel.
- Product/service or partnership fit.
- Quoted or advertised price, if available.
- Delivery cost, taxes, setup fees, and other known costs.
- Quality indicators, reviews, and source links.
- Lead time and deadline compatibility.
- Missing or uncertain information.
- User target price, hard budget, minimum quality, and deadline.
- Negotiation rules, communication approval policy, and purchase-approval requirements.

Module B should not need to research everything from scratch or ask the user to repeat the requirements.

### Return loop: Module B → Module A

The integration must be bidirectional:

1. Module A finds and ranks suppliers.
2. Module B contacts approved candidates and tracks their responses.
3. A supplier may reject a price, change delivery terms, or fail to respond.
4. Module B records the new information in the shared mission database.
5. The evaluation engine reranks candidates based on updated prices, terms, and availability.
6. If necessary, Module A searches for additional alternatives.
7. Module B continues with a suitable alternative.
8. StakeMate presents the best verified result and outstanding conditions.

**Key design requirement:** Shared state and controlled feedback loops—not just text passing between separate chatbots.

### Example sequence

1. User asks for 300 tote bags, delivered by 25 October, within RM1,500.
2. WorkBuddy extracts goals, constraints, and missing information.
3. Module A finds candidates through accessible web search, directories, marketplace APIs, and existing records.
4. The evaluation engine calculates total cost and ranks suppliers against price, quality, reliability, and lead-time criteria.
5. The shortlist is saved in the database and passed to Module B.
6. Module B drafts enquiries or counteroffers.
7. The user approves messages where required; communication tools send them.
8. Supplier replies are retrieved and classified.
9. The negotiation engine decides whether to counteroffer, clarify, wait, stop, or switch suppliers.
10. Module A updates rankings using new information.
11. StakeMate outputs final quotations, costs, evidence, delivery terms, savings calculations, risks, and required approvals.

---

## 6. End-to-End Workflow Example

### User request

> “I’m organising a technology event for 200 students. I need 300 custom tote bags within RM1,500, delivered before 25 October. Find the best suppliers, compare their quality, negotiate for a better price, and present the best available deal for my approval.”

### Workflow

1. **Goal analysis:** Extract budget, quantity, specifications, quality requirements, and delivery date. Ask only for essential missing details.
2. **Autonomous research:** Search accessible supplier sources and return candidates with evidence-backed prices, quality signals, delivery terms, and official contacts.
3. **Multi-criteria evaluation:** Compare total costs, delivery charges, quality, ratings, reliability evidence, and deadline compatibility.
4. **Negotiation handoff:** Pass the shortlist and negotiation limits into Module B.
5. **Approved outreach:** Draft and, after required approval, send enquiries or counteroffers through connected email/messaging services.
6. **Reply processing:** Classify replies as accepted, rejected, conditional, requesting information, or pending.
7. **Dynamic replanning:** If one supplier refuses the target, try an alternative or negotiate non-price terms such as simpler printing, bulk quantity, packaging, delivery, or a repeat-order opportunity.
8. **Verification:** Compare the latest offers against constraints, confirm what is actually agreed, flag unresolved conditions, and request user approval before a financial commitment.
9. **Final report:** Present the best available option, total landed cost, quality evidence, delivery terms, communication history, estimated savings against a comparable starting quote, and remaining risks.

### Negotiation example

- Initial quote: RM1,800.
- User's hard budget: RM1,500.
- Potential final offer: RM1,450.
- Difference: RM350, or about 19.4% of RM1,800.

These numbers are illustrative demo values, not real supplier quotes. Savings should only be described as realised when comparable terms and a final agreement are verified. If an offer excludes delivery or changes specifications, compare total equivalent cost before claiming savings.

---

## 7. Technical Architecture

### High-level architecture

```text
User
  ↓
StakeMate Dashboard
(goal, budget, deadline, requirements, approval settings)
  ↓
Agent Orchestrator
(understand goal → plan → invoke tools → inspect results → replan)
  Phases 1 to 6: Claude API orchestrator (kept as fallback)
  Phase 7 onward: WorkBuddy Agent + StakeMate Skill
  ↕
StakeMate Tool Registry + Tool Executor
(exposed to WorkBuddy as an MCP server from Phase 7)
  ├── Module A tools
  │     ├── search_stakeholders
  │     ├── verify_supplier
  │     ├── compare_offers
  │     └── rank_candidates
  ├── Module B tools
  │     ├── draft_outreach
  │     ├── send_approved_message
  │     ├── prepare_counteroffer
  │     └── process_reply
  └── Common workflow tools
        ├── read_mission_state
        ├── update_mission_state
        ├── request_approval
        ├── check_permission        (Section 22)
        ├── get_approval_status     (Section 22)
        ├── confirm_commitment      (Section 22, HOD only)
        └── create_final_report
  ↕
Approval Gate / Access Control
(roles: Committee Member, HOD · risk tiers 0 to 3 · default deny)
  ↕
Shared Backend + Database
(goals, contacts, sources, quotations, offers, messages, approvals, task states, audit log)
  ↕
External services
(web search, supplier APIs, email, calendar, documents)
```

### The parts in plain language

- **WorkBuddy = brain/orchestrator:** Understands goals, plans tasks, chooses tools, interprets outputs, and decides the next step.
- **Claude orchestrator = first brain and fallback:** Does the same job using the Claude API with tool use during Phases 1 to 6, before WorkBuddy is added. It stays available as a fallback (Section 23.0).
- **Tool registry and executor = single source of tools:** Every tool is defined once in the backend, and every call passes the approval gate and audit log, whichever orchestrator makes it.
- **MCP server = bridge/tool interface:** Exposes functions you implement so WorkBuddy can call them. Added in Phase 7 as a thin wrapper over the tool registry.
- **External APIs = hands:** Search websites, send/read messages, retrieve availability, or create calendar events, according to their permissions.
- **Database = persistent memory:** Stores missions, suppliers, quotations, negotiations, responses, approvals, and outcomes across steps or sessions.
- **Frontend = control centre:** Displays requirements, activity, comparisons, approval requests, status, and reports.
- **Approval/verification layer = safety gate:** Enforces budget, permission, and commitment rules.
- **Access control = who may approve what:** Committee Members approve routine enquiries, the HOD approves counteroffers, orders, payments, and commitments and also manages users and integrations. See Section 22.

### Important WorkBuddy integration idea

Use **MCP + Skill**: the MCP server exposes the actual tools; the Skill describes their purpose, ordering, constraints, and workflow. Avoid merely adding WorkBuddy branding to a conventional chatbot. WorkBuddy should genuinely call the tools and coordinate execution.

This integration is built in Phase 7, after the full workflow already runs on the Claude orchestrator. Because the tools live in a framework-agnostic registry, adding WorkBuddy does not change business logic or safety rules (Section 23.0).

### One agent or multiple agents?

For the first hackathon version, use **one WorkBuddy-orchestrated agent** with specialised tools and a shared database. Add specialised agents later only if they provide a measurable improvement. Logical modules do not have to be separate AI models or separate servers.

---

## 8. Module A — Discovery, Sourcing, and Evaluation

### A1. Search and discovery

- Internet-wide search across accessible/indexed websites.
- Multi-source search across suitable public sources and supported directories.
- Product-specific vendor search.
- Geographic and delivery-area filtering.
- Budget filtering.
- Sponsor discovery by industry, target audience, and partnership fit.
- Collaborator discovery for universities, NGOs, startups, speakers, and industry partners.
- Public contact discovery from legitimate, official sources.
- Existing database search to reuse previously known stakeholders.
- Search expansion if the first search returns too few candidates.

### A2. Quality and suitability assessment

- Price comparison across advertised prices and quotations.
- Total-cost calculation including delivery, customisation/printing, setup fees, taxes where applicable, and other known fees.
- Quality assessment using specifications, certifications, samples, and evidence.
- Review analysis summarising recurring positive and negative themes.
- Review credibility flags for suspicious patterns or low review volume.
- Delivery assessment and deadline feasibility.
- Supplier reliability assessment using available fulfilment history, references, and other evidence.
- Capability matching for required quantity, customisation, or services.
- Risk and suitability checks for missing company details, unclear terms, and unusual payment requests.
- AI comparison report explaining trade-offs and linking to sources.

### A3. Ranking and selection

- Configurable compatibility score with adjustable weights.
- Cheapest qualifying option among candidates meeting all mandatory criteria.
- Best-value recommendation that may differ from the cheapest offer.
- Explainable ranking that states why candidates ranked as they did.
- User-managed shortlist.
- Backup suppliers for failed negotiations.
- Live reranking when new quotes, terms, or availability arrive.
- Price history for repeat suppliers (advanced).
- Target-price estimation from verified comparable offers (advanced).

### Example compatibility score

A transparent weighted score can combine normalised measures of price, quality, reliability, delivery, and fit. Let users adjust the weights. The ranking should show each subscore and supporting evidence rather than presenting an unexplained number.

Example supplier records (simulated only):

| Supplier | Price | Quality score | Delivery | Total score |
|---|---:|---:|---:|---:|
| Supplier A | RM1,650 | 82/100 | 7 days | 84/100 |
| Supplier B | RM1,420 | 75/100 | 12 days | 79/100 |
| Supplier C | RM1,750 | 94/100 | 5 days | 91/100 |

Supplier C has the best illustrative overall score, while Supplier B has the lowest price. The system should explain the trade-off. These values are simulated, not market research.

### Limitation to communicate honestly

A search engine cannot guarantee it has found the cheapest vendor anywhere on the internet. Recommendations should say they are based on accessible sources and terms that could be verified, and should note gaps in coverage or missing quotation details.

---

## 9. Module B — Communication and Negotiation

### B1. Outreach and communication

- Personalised emails based on the recipient's business and the user's goal.
- Enquiry generation to request quotes, specifications, delivery, and missing details.
- Sponsorship proposal generation and personalisation.
- Attach approved decks, quotation requests, and supporting documents.
- Multiple authorised communication channels where APIs/integrations are available.
- Reply monitoring using connected email/messaging accounts.
- Reply classification (accepted, declined, conditional, clarification required, pending).
- Intent and objection analysis (price concerns, delivery concerns, interest, questions).
- Context-aware responses using prior messages and offers.
- Follow-up scheduling after a defined time without a reply.
- Escalation for urgent, ambiguous, or sensitive messages.
- Full communication history.
- Multilingual messages in English, Bahasa Malaysia, and Chinese.

### B2. Negotiation intelligence

- User-set target price and hard budget.
- Counteroffer generation with rationale.
- Sending approved counteroffers through connected services.
- Offer tracking for every round and changed term.
- Negotiation-round limits.
- Conditional negotiation that changes strategy based on responses.
- Walk-away conditions when the budget is exceeded or mandatory requirements fail.
- Multi-variable bargaining across price, quantity, delivery, payment terms, packaging, and customisation.
- Win-win optimisation (e.g., bulk order or repeat business in exchange for a discount).
- Bulk and quantity price-break comparison.
- Best-and-final offer strategy where appropriate.
- Alternative-supplier switching after failure.
- Cross-supplier benchmarking using legitimate comparable quotations; do not share confidential competing offers improperly.
- Agreement comparison against the original target.
- Negotiation debrief explaining what worked, what failed, and why.

### B3. User-defined negotiation boundaries

Let the user set:

- **Target price:** ideal outcome.
- **Hard budget:** maximum permitted total spend.
- **Minimum quality:** minimum acceptable specifications or quality.
- **Deadline:** latest acceptable delivery date.
- **Negotiation limit:** maximum counteroffer rounds or stopping point.
- **Approval policy:** which messages or commitments require a human.

Example: ask for RM1,350; consider RM1,420 if all terms meet requirements; reject RM1,520 if the hard budget is RM1,500. The target is not permission for binding commitments. Never invent competing quotations or misrepresent another supplier to gain leverage.

---

## 10. Complete Feature Catalogue and Priorities

### Priority definitions

- **P0 — Core hackathon demo:** Essential for the first coherent end-to-end workflow.
- **P1 — Strong extension:** Valuable after the core flow works.
- **P2 — Advanced roadmap:** Longer-term or more complex feature.

### A. Agent orchestration and goal understanding

| Feature | What it does | Priority |
|---|---|---|
| Natural-language goal input | Accepts requests such as “find a sponsor for our event” | P0 |
| Goal decomposition | Breaks a goal into research, communication, and negotiation tasks | P0 |
| Requirement extraction | Extracts product, quantity, budget, location, and deadline | P0 |
| Clarification engine | Asks only for missing information needed to act | P0 |
| Dynamic task planning | Changes the plan when a supplier rejects an offer | P0 |
| Agent execution loop | Observes results, selects next actions, and repeats | P0 |
| Task dependency management | Ensures prerequisite actions happen in the right order | P0 |
| Workflow checkpoints | Saves and resumes interrupted missions | P1 |
| Parallel research | Searches different supplier categories simultaneously | P1 |
| Multi-agent collaboration | Specialises research, negotiation, and risk review | P2 |
| Failure recovery | Retries recoverable errors and chooses alternative tools | P1 |
| Confidence/uncertainty reporting | Flags incomplete evidence instead of guessing | P0 |
| User-defined autonomy | Lets users choose which steps can run independently | P1 |

### B. Module A features

| Feature | What it does | Priority |
|---|---|---|
| Internet-wide sourcing | Searches accessible indexed websites and sources | P0 |
| Multi-source search | Uses several accessible sources | P1 |
| Product-specific search | Finds vendors selling a specified product/service | P0 |
| Geographic filtering | Filters by country, state, city, or delivery area | P1 |
| Budget filtering | Identifies potentially affordable options | P0 |
| Sponsor discovery | Finds businesses with relevant audience/industry fit | P1 |
| Collaborator discovery | Finds universities, NGOs, startups, speakers, and partners | P1 |
| Public contact discovery | Retrieves official public contact channels | P0 |
| Existing database search | Reuses saved stakeholders and vendors | P0 |
| Search expansion | Finds alternatives if too few candidates emerge | P1 |
| Price comparison | Compares advertised prices and quotations | P0 |
| Total-cost calculation | Includes known delivery, setup, tax, printing and other costs | P0 |
| Quality assessment | Compares specifications, certifications, and evidence | P0 |
| Review analysis | Summarises available positive/negative review themes | P1 |
| Review credibility flags | Flags suspicious patterns or sparse evidence | P1 |
| Delivery assessment | Evaluates lead time and deadline compatibility | P0 |
| Reliability assessment | Uses available track records and references | P1 |
| Capability matching | Checks quantity, customisation and service fit | P0 |
| Risk/suitability checks | Flags missing details, unclear terms, unusual payment requests | P1 |
| Comparison report | Explains candidate trade-offs and cites sources | P0 |
| Configurable compatibility score | Weights price, quality, reliability, and delivery | P0 |
| Cheapest qualifying option | Finds the lowest-priced candidate meeting mandatory criteria | P0 |
| Best-value recommendation | Recommends the best trade-off rather than cheapest by default | P0 |
| Explainable ranking | Explains ranking and its evidence | P0 |
| Shortlist management | Approve/remove candidates | P0 |
| Alternative recommendations | Keeps backup suppliers | P0 |
| Live reranking | Recalculates ranking when new offers arrive | P0 |
| Price history | Tracks previous quotes | P2 |
| Target-price estimation | Estimates targets from verified comparable offers | P1 |

### C. Module B features

| Feature | What it does | Priority |
|---|---|---|
| Personalised email generation | Tailors emails to recipient and objective | P0 |
| Enquiry generation | Requests quotes and missing terms | P0 |
| Sponsorship proposals | Creates sponsor-specific proposals | P1 |
| Document attachments | Attaches approved decks and supporting documents | P1 |
| Multiple communication channels | Uses authorised email/messaging integrations | P1 |
| Reply monitoring | Retrieves replies from connected accounts | P1 |
| Reply classification | Categorises replies by outcome/intent | P0 |
| Intent/objection detection | Identifies concerns, objections, or interest | P1 |
| Context-aware responses | Uses prior messages/offers | P0 |
| Follow-up scheduling | Prepares follow-ups after a defined interval | P1 |
| Escalation rules | Flags ambiguous, urgent or sensitive messages | P0 |
| Communication history | Stores the interaction trail | P0 |
| Multilingual messaging | Supports English, Bahasa Malaysia, and Chinese | P1 |
| Target-price setting | Defines desired price and hard budget | P0 |
| Counteroffer generation | Suggests a price and reasoning | P0 |
| Counteroffer execution | Sends approved proposals via connected services | P0 |
| Offer tracking | Records offers, counteroffers, and changed terms | P0 |
| Negotiation-round management | Limits and records rounds | P0 |
| Conditional negotiation | Adjusts strategy based on reply | P0 |
| Walk-away conditions | Stops when limits/requirements fail | P0 |
| Multi-variable bargaining | Trades price against quantity, delivery, terms, packaging, etc. | P1 |
| Win-win optimiser | Proposes reciprocal value for concessions | P1 |
| Bulk discounts | Compares quantity/price tiers | P1 |
| Best-and-final offer | Requests final quote when sensible | P1 |
| Alternative switching | Returns to Module A when negotiation fails | P0 |
| Cross-supplier benchmarking | Uses legitimate comparable quotes where appropriate | P1 |
| Agreement comparison | Compares latest deal with original target | P0 |
| Negotiation debrief | Explains outcomes and lessons | P1 |

### D. Meeting, collaboration and relationships

| Feature | What it does | Priority |
|---|---|---|
| Meeting-slot discovery | Finds possible times | P1 |
| Calendar integration | Reads authorised availability and creates approved invites | P1 |
| Agenda generation | Creates agendas from goals and prior messages | P1 |
| Meeting notes | Summarises notes or authorised transcripts | P1 |
| Action-item extraction | Finds owners, deadlines and next steps | P1 |
| Meeting follow-up emails | Drafts minutes and follow-ups | P1 |
| Commitment tracker | Tracks promises, deliverables and overdue actions | P1 |
| Stakeholder CRM | Stores contact and interaction history | P0 |
| Relationship history | Records previous partnerships and outcomes | P1 |
| Team collaboration | Lets multiple club/business members work on one mission | P1 |
| Role-based access | Controls viewing, editing, and approvals (Committee Member, HOD; see Section 22) | P0 (moved up from P1) |
| Duplicate contact detection | Prevents repeated approaches to same company | P1 |
| Relationship health monitoring | Flags unresponsive threads and unresolved commitments | P2 |
| Reusable templates | Reuses successful workflows and communications | P1 |

### E. Sponsorship and partnership features

| Feature | What it does | Priority |
|---|---|---|
| Event brief builder | Captures audience size, date, venue and goals | P1 |
| Sponsor matching | Ranks companies by industry, audience and fit | P1 |
| Sponsorship tier generator | Creates Gold/Silver/Bronze packages | P1 |
| Benefit matching | Matches sponsor needs to exposure, booths, talks, recruitment, etc. | P1 |
| Proposal personalisation | Tailors each deck/email | P1 |
| Sponsorship pipeline | Tracks prospects, outreach, replies, meetings and decisions | P1 |
| Sponsorship negotiation | Handles cash, in-kind support and deliverables | P1 |
| Sponsorship value tracking | Separates confirmed cash from estimated in-kind value | P1 |
| Sponsor deliverable tracker | Tracks logos and promised benefits | P2 |
| Post-event reporting | Generates reports and thank-you messages | P2 |
| Future-partner recommendations | Finds returning sponsors based on past outcomes | P2 |
| In-kind sponsorship optimisation | Compares non-cash support against actual event needs | P1 |

### F. Trust, safety, and verification features

| Feature | What it does | Priority |
|---|---|---|
| Source attribution | Stores evidence URLs and timestamps | P0 |
| Verified vs estimated labels | Separates confirmed quotes from estimates | P0 |
| Approval before sending | Lets users review consequential outgoing messages | P0 |
| Purchase approval | Requires explicit authorisation for financial commitments | P0 |
| Tiered approval gate | Classifies every action into risk tiers 0 to 3 and routes it to the Committee Member or HOD before execution (Section 22) | P0 |
| Budget enforcement | Prevents actions beyond permitted limits | P0 |
| Contact/outreach controls | Respects opt-outs and avoids inappropriate bulk outreach | P0 |
| Credential protection | Stores API keys and account tokens securely | P0 |
| Least-privilege access | Requests only necessary permissions | P0 |
| Audit logs | Records tools, actions, results, approvals, and timestamps | P0 |
| Prompt-injection defences | Treats webpage/email instructions as untrusted data | P1 |
| Error/contradiction handling | Detects missing or conflicting prices and terms | P0 |
| Personal-data protection | Minimises stored personal/contact information | P0 |
| Human escalation | Requests assistance for risky or ambiguous terms | P0 |
| Supplier fraud warnings | Flags suspicious payment requests/inconsistent identities | P1 |

### G. Dashboard, reporting and analytics

| Feature | What it does | Priority |
|---|---|---|
| Mission dashboard | Shows goals, active tasks, and statuses | P0 |
| Live agent activity | Shows searches, tool calls, and next action | P0 |
| Supplier comparison table | Shows cost, quality, delivery and evidence | P0 |
| Negotiation timeline | Displays offers and counteroffers | P0 |
| Approval inbox | Centralises pending actions | P0 |
| Budget tracker | Tracks target, quotes, and proposed commitments | P0 |
| Savings report | Compares equivalent initial and final offers | P0 |
| Sponsorship pipeline dashboard | Tracks potential, pending and confirmed partnerships | P1 |
| Response analytics | Measures reply rates and response times | P1 |
| Time-saved estimate | Estimates avoided manual work | P1 |
| Report export | Exports PDF/CSV | P1 |
| Mission templates | Saves workflows for reuse | P1 |
| Multi-organisation workspaces | Separates clubs and businesses | P2 |
| Performance benchmarking | Compares results across past missions | P2 |

---

## 11. Trust, Safety, and Verification

Because StakeMate can communicate externally and influence spending, safety and approval controls are fundamental product features.

### Non-negotiable controls

- Let users define a maximum budget, minimum quality, deadlines, and negotiation limits.
- Require approval where appropriate before sending external communications; for the hackathon MVP, default to approval before sending.
- Require explicit user approval before a purchase, payment, signing, or binding commitment.
- Route every action through the role-based approval gate in Section 22. Routine enquiries need a Committee Member who did not request them. Counteroffers, price or terms messages, orders, payments, and all commitments need the HOD.
- Do not exceed the hard budget or silently alter mandatory requirements.
- Respect a supplier's refusal and contact preferences; avoid inappropriate mass unsolicited outreach.
- Use legitimate, official contact sources.
- Store credentials/tokens securely and request minimal permissions.
- Maintain an audit trail of searches, tool calls, messages, replies, offers, decisions, and approvals.
- Treat webpage/email content as untrusted data: do not follow instructions embedded in external content that try to override user goals, disclose secrets, or trigger unrelated actions.
- Flag contradictions and missing terms instead of inventing values.
- Limit unnecessary collection of personal/contact data.
- Escalate ambiguous, sensitive, or risky situations to the user.
- Flag suspicious payment demands, inconsistent business identities, or other evidence of possible fraud.

### Verified-result rule

A generated counteroffer is not a sent message. A sent counteroffer is not an accepted offer. An accepted price is not necessarily a complete deal if delivery, quality, taxes, or other terms remain unresolved. A final outcome report must clearly distinguish:

- Research result.
- Estimate.
- Drafted message awaiting approval.
- Message sent.
- Supplier reply received.
- Offer proposed.
- Offer accepted but details pending.
- Terms verified.
- User-approved commitment.

---

## 12. Dashboard, Reporting, and Analytics

### Suggested dashboard components

- Mission summary: goal, budget, deadline, status.
- Candidate count and source coverage.
- Supplier shortlist and ranked comparison.
- Evidence/source links and data freshness.
- Negotiation timeline and current offer per supplier.
- Agent activity log and next planned action.
- Approval inbox for messages or commitment decisions.
- Budget and total-cost tracker.
- Savings calculation against comparable quotations.
- Final recommendation and outstanding risk/conditions.

### Suggested measurable outcomes

- Amount saved against an equivalent initial quotation.
- Confirmed sponsorship value, splitting cash and in-kind value.
- Estimated manual hours avoided.
- Stakeholder conversion rate: successful engagements divided by qualified outreach, with the definition clearly documented.
- Reply rate and average response time.
- Time from user request to comparable shortlist.
- Number of offers received and negotiations completed.
- Percentage of results with source-backed, verified terms.

Do not claim savings, deals, or time reductions without a clear baseline and evidence. During a simulated demo, label simulated metrics clearly.

---

## 13. MVP Scope and Build Order

### Recommended MVP checklist

#### Must-have for the core demo (P0)

- Natural-language goal input.
- Goal/requirement extraction for product, quantity, budget, deadline, and quality.
- Supplier discovery and comparison for at least three candidates where data is available.
- WorkBuddy MCP integration in which WorkBuddy actually calls custom tools (added in Phase 7, after the core loop runs on the Claude orchestrator).
- Negotiation logic with a target price, hard budget, maximum rounds, and stopping rules.
- Approved email outreach or a clearly labelled controlled demo simulation.
- Reply classification and negotiation state updates.
- Live mission/activity dashboard.
- Shared persistent mission state.
- Budget/quality constraints, approval gates, audit history, and final report.
- Role-based access control (Committee Member, HOD) with risk-tiered approvals (Section 22).

#### Strong extensions (P1)

- Automated follow-up.
- Calendar/meeting scheduling.
- Sponsorship deck generation.
- Meeting summary and action-item extraction.
- Multilingual support.
- Parallel research and workflow checkpoints.
- Sponsorship pipeline, relationship CRM, and report exports.

#### Longer-term/stretch (P2)

- Multi-agent negotiation war room.
- Relationship intelligence graph.
- Price history and cross-mission benchmarking.
- Advanced relationship health monitoring.
- Multi-organisation management and advanced analytics.

### Recommended build order

1. **Foundation:** Frontend goal form, mission database, basic dashboard, tool registry, and a working Claude API agent loop.
2. **Module A:** Search suppliers, collect evidence, calculate total cost, and rank candidates.
3. **Module B:** Draft messages, simulate or retrieve responses, prepare counteroffers, and manage negotiation rounds.
4. **Integration:** Pass supplier results into negotiation; feed failed negotiations back into discovery and reranking.
5. **Verification:** Enforce budget limits, approvals, audit logs, and a final report.
6. **WorkBuddy integration:** Expose the same tools to WorkBuddy through an MCP server and Skill, and run the demo on WorkBuddy.
7. **Expansion:** Add sponsorship, calendars, meeting notes, and team collaboration only after the main loop works.

Section 23 expands this build order into detailed phases, with access control built in Phase 1 before any external tool and WorkBuddy added in Phase 7. Section 24 maps every item in this document to a phase.

### Suggested development checklist

- [ ] Natural-language goal input.
- [ ] Supplier discovery/comparison.
- [ ] WorkBuddy MCP integration.
- [ ] Negotiation agent.
- [ ] Email communication or controlled simulation.
- [ ] Live agent activity dashboard.
- [ ] Automated follow-up.
- [ ] Calendar scheduling.
- [ ] Sponsorship deck generation.
- [ ] Meeting summarisation.

---

## 14. Hackathon Demo Scenario

### Demo request

> “I’m organising a technology event for 200 students. I need 300 custom tote bags within RM1,500, delivered before 25 October. Find the best suppliers, compare their quality, negotiate for a better price, and present the best available deal for my approval.”

### What judges should see

1. **Goal analysis:** The agent extracts requirements, budget, quantity, and deadline.
2. **Autonomous research:** Searches suppliers and presents at least three plausible candidates with sources.
3. **Comparison:** Displays price, total costs, quality signals, delivery, and uncertainties.
4. **Negotiation:** Prepares and, with approval, sends a counteroffer.
5. **Reply handling:** Receives a controlled demo reply or a real authorised reply and classifies it.
6. **Dynamic replanning:** If the supplier rejects the target, proposes revised terms or moves to the next-ranked supplier.
7. **Verified outcome:** Shows offer history, final terms, comparable savings, outstanding conditions, and user approval status.
8. **Approval gate:** A Committee Member approves the enquiry, the HOD approves the counteroffer and the final deal, and a Committee Member login shows it cannot approve the counteroffer.

### Dashboard mock data

| Metric | Illustrative value |
|---|---:|
| Initial quote | RM1,800 |
| Final offer | RM1,450 |
| Difference | RM350 |
| Difference as % of initial quote | 19.4% |

Illustrative activity timeline:

- Requirements analysed: budget RM1,500, quantity 300.
- Three suppliers evaluated: price, quality, delivery compared.
- Counteroffer accepted: simulated supplier agreed to RM1,450.
- Final deal awaiting HOD approval: no purchase order issued.

**Clearly label mock data and simulated suppliers/negotiations.** A controlled mock supplier-email service can guarantee a reply during the presentation; a separate live search integration can demonstrate real sourcing. Do not present simulated acceptance as a real transaction or realised savings.

---

## 15. Judging Strategy

| Judging criterion | How StakeMate should demonstrate it |
|---|---|
| Real problem and user value | Saves time in procurement, sponsorship, and stakeholder coordination for student clubs and small businesses. |
| Agentic workflow | Plans, searches, compares, communicates, negotiates, interprets replies, and replans. |
| Meaningful use of WorkBuddy | WorkBuddy genuinely invokes custom MCP tools and orchestrates the workflow. |
| End-to-end execution | Advances one user goal from requirements to an evidence-backed recommendation or verified agreement. |
| Usable and verifiable results | Shows quotations, evidence links, communication logs, approvals, and measurable outcomes. |

### Strong closing statement

> “Today, AI can write an email asking for sponsorship or a discount. But it is still up to us to find the right person, send the email, follow up, negotiate, and close the deal. StakeMate changes that. We don’t just help you communicate with stakeholders. We help you achieve outcomes.”

### Product closing line

**StakeMate AI — From First Contact to Final Agreement.**

---

## 16. Beginner Guide: Integrating Tencent WorkBuddy

> **When to use this guide.** Following Section 23, these steps are done in **Phase 7**, after the full workflow already runs on the Claude orchestrator. The project folder and virtual environment from Step 2 already exist from Phase 0, so only the `mcp[cli]` install is new. The Step 6 table also lists the integrations used from Phase 3 onward.

> This section is a practical starting point. WorkBuddy screens, connector schemas, account eligibility, and Enterprise/API access can change; verify exact details against the current official documentation before relying on them during the hackathon.

### Step 1 — Install and explore WorkBuddy

1. Visit the official WorkBuddy website: <https://www.workbuddy.ai/>.
2. Follow its current installation/sign-in instructions.
3. Learn how to give WorkBuddy a goal and ask it to plan a workflow.
4. Try this prompt:

   “You are StakeMate, an AI procurement assistant. Help me plan a workflow for finding three qualified tote bag suppliers within RM1,500. Break down the tasks and explain what tools you need.”

At this point WorkBuddy can plan the workflow, but it will not yet have access to StakeMate's custom database or negotiation functions.

### Step 2 — Create a project and Python environment

```bash
mkdir stakemate-ai
cd stakemate-ai
python -m venv .venv
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\activate
```

Install the Python MCP SDK:

```bash
pip install "mcp[cli]"
```

Create `server.py` in the project folder.

### Step 3 — Implement custom MCP tools

The starter code is in [Section 17](#17-starter-mcp-server-code). It defines:

- `search_suppliers`: searches a small, simulated supplier list and marks whether prices are within budget.
- `prepare_counteroffer`: constructs a message for approval without sending it.

The data is deliberately simulated so that the first milestone is to prove that WorkBuddy can call the Python functions successfully.

### Step 4 — Connect the server to WorkBuddy

The earlier documented route is **Settings → MCP → Add MCP Server**, though the current screen may differ by version. Use the current WorkBuddy MCP/connector guide to verify the exact configuration method.

For a local stdio server, an example configuration shape is:

```json
{
  "mcpServers": {
    "stakemate": {
      "type": "stdio",
      "command": "C:\\path\\to\\stakemate-ai\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\stakemate-ai\\server.py"
      ]
    }
  }
}
```

Replace the example paths with the actual absolute paths on your machine. The format/entry point may differ by WorkBuddy version, so confirm it in the official connector docs. Keep the local server running/available as required by the configured transport.

### Step 5 — Test the integration

Try asking WorkBuddy:

> “Use the StakeMate tools to compare suppliers for 300 tote bags with a budget of RM1,500. Select the best budget-compatible supplier and prepare a counteroffer for another supplier. Do not send any messages.”

**First integration milestone:** WorkBuddy calls the Python tools and returns their results. This proves the essential connection between WorkBuddy and custom functionality.

### Step 6 — Replace demo tools with real integrations

| Capability | Suggested approach |
|---|---|
| Supplier discovery | A search API such as Brave Search or Tavily, subject to access, terms, and availability |
| Email sending/reading | Gmail API or Microsoft Graph with scoped authorisation |
| Meeting scheduling | Google Calendar API or Microsoft Graph |
| Persistent storage | Supabase PostgreSQL |
| Document generation | Python PDF generation |
| Frontend | Next.js + Tailwind CSS |
| Backend | FastAPI where a separate application API is useful |
| WorkBuddy connection | Custom MCP server; investigate Enterprise Managed Agents APIs if the dashboard must initiate WorkBuddy sessions directly |

A recommended stack is **Next.js + FastAPI + Supabase + WorkBuddy MCP**. The frontend manages the workflow, WorkBuddy orchestrates reasoning and tool calls, the backend enforces business logic/permissions, and the database preserves state.

WorkBuddy Enterprise Managed Agents APIs may provide ways to create agents and sessions, but access requirements and availability must be verified before making the hackathon architecture depend on them.

---

## 17. Starter MCP Server Code

This minimal demo uses simulated data. It does not perform internet search, send emails, or make real supplier contact.

> **Build note.** In Phase 1 the same `search_suppliers` and `prepare_counteroffer` behaviour is built as plain functions in the backend tool registry and called by the Claude orchestrator. In Phase 7 the MCP server below becomes a thin wrapper that forwards each tool call to the backend tool executor, so approvals and audit logging stay in the backend.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("StakeMate")

# Demo data. Replace with live supplier APIs later.
suppliers = [
    {"name": "Supplier A", "price": 1800, "rating": 4.6},
    {"name": "Supplier B", "price": 1450, "rating": 4.2},
    {"name": "Supplier C", "price": 1600, "rating": 4.8},
]

@mcp.tool()
def search_suppliers(product: str, budget: float) -> dict:
    """Compare demo suppliers against a budget."""
    ranked = sorted(suppliers, key=lambda x: x["price"])
    return {
        "product": product,
        "budget": budget,
        "suppliers": [
            {**s, "within_budget": s["price"] <= budget}
            for s in ranked
        ],
        "data_source": "demo"
    }

@mcp.tool()
def prepare_counteroffer(
    supplier_name: str,
    quoted_price: float,
    target_price: float
) -> dict:
    """Prepare a negotiation proposal for approval."""
    if target_price <= 0 or quoted_price <= 0:
        return {"error": "Prices must be positive"}

    return {
        "supplier": supplier_name,
        "proposed_price": target_price,
        "message": (
            f"Thank you for your quotation of RM{quoted_price:.2f}. "
            f"Would you consider RM{target_price:.2f}? "
            "We would be happy to discuss mutually "
            "beneficial terms."
        ),
        "status": "awaiting_user_approval",
        "sent": False
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### What this code demonstrates

- Registers `StakeMate` as an MCP server.
- Exposes `search_suppliers` as a callable tool.
- Exposes `prepare_counteroffer` as a callable tool.
- Sorts demo supplier data by price and marks suppliers within budget.
- Drafts a counteroffer but explicitly returns `sent: False` and `awaiting_user_approval`.

Before using this in production, add robust input validation, typed schemas where appropriate, error handling, logging, authentication for real user data, persistent storage, and approval enforcement in the backend—not just in the model prompt.

---

## 18. Supplier Handoff Data Contract

Use structured data so that Module A and Module B share the same mission and supplier facts.

```json
{
  "mission_id": "MISSION-001",
  "product": "Custom tote bags",
  "quantity": 300,
  "budget_myr": 1500,
  "delivery_deadline": "2026-10-25",
  "minimum_quality": 4.0,
  "supplier": {
    "id": "SUP-001",
    "name": "Example Supplier A",
    "quoted_unit_price": null,
    "total_quoted_price": null,
    "delivery_cost": null,
    "estimated_lead_days": null,
    "contact_channel": "email",
    "contact_verified": false
  },
  "negotiation_rules": {
    "target_total_myr": 1350,
    "hard_budget_myr": 1500,
    "max_rounds": 3,
    "require_approval_before_sending": true,
    "require_approval_before_purchase": true
  },
  "status": "shortlisted"
}
```

The prices and rules are examples, not verified market data. Backend logic should populate supplier fields with sourced values or preserve unknowns explicitly instead of inventing quotes. The approval flags in `negotiation_rules` are resolved to specific roles by the tier rules in Section 22.

### Suggested shared database entities

- **Mission:** mission ID, user goal, constraints, status, deadlines, owner.
- **Stakeholder/Supplier:** ID, organisation, official contact channel, source, verification status.
- **Evidence/Source:** URL, retrieval timestamp, claim supported, confidence or caveat.
- **Quotation:** supplier ID, unit/total prices, currency, delivery, tax/fees, validity period, source.
- **Negotiation:** supplier ID, round number, offer, response, conditions, status.
- **Message:** channel, draft/sent/received status, timestamp, body/reference, approval record.
- **Approval:** action, approver, decision, timestamp, limits (extended with tier, approver role, content hash, token, and expiry in Section 22.6).
- **User and RoleAssignment:** user identity and role (Committee Member, HOD) with organisation scope (Section 22.6).
- **ApprovalPolicy:** which action types fall in which tier and which roles may approve them (Section 22.6).
- **Task/Event log:** tool call, input/output reference, result, failure, retry count, timestamp.
- **Outcome:** selected option, terms verified, approval status, calculated savings and caveats.

---

## 19. Suggested Technology Stack and Code Components

### Suggested technologies

- **Frontend:** Next.js + Tailwind CSS.
- **Application backend:** FastAPI (Python).
- **Agent tool bridge:** Custom MCP server using the Python MCP SDK/FastMCP.
- **Orchestration:** Claude API (Anthropic Python SDK) tool-use loop during Phases 1 to 6, then Tencent WorkBuddy + a StakeMate Skill from Phase 7, with the Claude loop kept as fallback.
- **Database:** Supabase PostgreSQL.
- **Search:** Search provider API such as Brave Search or Tavily, subject to access/terms.
- **Email:** Gmail API or Microsoft Graph, with scoped permission and approval controls.
- **Calendar:** Google Calendar API or Microsoft Graph.
- **Documents:** Python-based PDF/document generation.

These are recommendations, not requirements. Choose the smallest set that the team can implement and test within the hackathon time limit.

### Recommended logical components

| Component | Responsibility |
|---|---|
| `goal_manager` | Understands the request and creates a mission |
| `discovery_service` | Searches for stakeholders and supplier candidates |
| `evaluation_engine` | Scores, filters, and compares candidates |
| `negotiation_engine` | Prepares counteroffers, enforces limits, and decides next steps |
| `communication_service` | Sends approved messages and retrieves replies |
| `workflow_orchestrator` | Coordinates Module A/B, manages retries and feedback loops |
| `approval_service` | Enforces role-based, risk-tiered approvals for messages and commitments (Section 22) |
| `stakeholder_database` | Stores contacts, quotes, conversations, and mission state |
| `reporting_service` | Generates comparisons, audit logs, and final reports |
| `tool_registry` | Defines every agent tool once, with typed input and output schemas, independent of any orchestrator |
| `tool_executor` | Runs every tool call through permission checks, the approval gate, and the audit log |
| `claude_orchestrator` | Runs the agent loop with Claude API tool use (Phases 1 to 6) and stays as a fallback |
| `workbuddy_mcp_server` | Exposes the tool registry to WorkBuddy as MCP tools (Phase 7) |

Avoid duplication of responsibilities: the negotiation engine should call the discovery/evaluation services for alternatives instead of implementing a second web-search system.

---

## 20. Product Decisions and Important Limitations

1. **Build one coherent workflow first.** Do not attempt the entire feature catalogue during the hackathon.
2. **Use one orchestrator initially.** WorkBuddy can call different specialised tools; separate autonomous agents are a later optimisation.
3. **Make the Module A–B link bidirectional.** Updated negotiations must change ranking and can trigger additional discovery.
4. **Prioritise actual tool calls.** The strongest demo shows WorkBuddy invoking MCP tools rather than merely describing actions.
5. **Avoid pretending simulated operations are real.** Mark demo suppliers, prices, messages, replies, and savings as simulated.
6. **Do not claim universal cheapest-vendor coverage.** Search coverage is finite and terms may be incomplete.
7. **Use equivalent cost comparisons.** Consider quantity, specifications, delivery, fees, taxes where applicable, lead time, and quote validity.
8. **Keep autonomy bounded.** The user sets budgets, minimum requirements, negotiation limits, and approvals.
9. **Separate offer acceptance from purchasing.** Final financial or binding commitments require explicit approval.
10. **Design for failure.** A supplier may not reply, search may fail, an API may rate-limit, or terms may be inconsistent. Retry safely, record failures, switch tools/candidates where appropriate, and escalate when necessary.
11. **Protect external communications.** Use authorised accounts, legitimate contacts, rate limits, opt-out controls, secure tokens, and an audit trail.
12. **Verify WorkBuddy access and API options early.** Do not assume Enterprise Managed Agents APIs or a particular setup interface is available to the hackathon account.

---

## 21. Closing Pitch

> “Today, AI can write an email asking for sponsorship or a discount. But it is still up to us to find the right person, send the email, follow up, negotiate, and close the deal. StakeMate changes that. We don’t just help you communicate with stakeholders. We help you achieve outcomes.”

**StakeMate AI — From First Contact to Final Agreement.**

An agentic stakeholder liaison system that connects discovery, evaluation, communication, negotiation, coordination, and verification into one goal-driven workflow.

---

## 22. Access Control and Approval Governance

StakeMate acts on behalf of a club, society, department, or business, so no external action may happen without a check. Access control uses two human roles plus one non-human agent identity, and a risk-tiered approval gate. The rule is **default deny**. Every action passes through the gate before it executes, and the gate is enforced in the backend, not in the AI prompt.

### 22.1 Roles

| Role | Typical person | What the role is for |
|---|---|---|
| **Committee Member** | Club or society committee member, procurement or business development staff | Creates missions, runs research, manages the shortlist, drafts messages, and approves routine (Tier 1) actions requested by someone else |
| **HOD (Head of Department)** | Faculty advisor, department head, or business owner who carries final accountability | Approves all high-risk (Tier 2) and commitment (Tier 3) actions, sets or changes the hard budget and mandatory requirements, handles escalations, and manages users, role assignments, integrations, API credentials, and policy configuration |
| **StakeMate Agent** (`agent:claude` from Phase 1, plus `agent:workbuddy` from Phase 7) | Non-human | Calls tools and creates approval requests. Holds no approval rights and can never approve, create, or edit its own approval tokens |

Because the HOD also manages users and integrations, every role assignment, integration change, and policy change is written to the audit log.

### 22.2 Risk tiers

Every action is classified into a tier before it runs. If the classification is unclear, the higher tier is used.

| Tier | Risk level | Example actions | Who can approve | Execution rule |
|---|---|---|---|---|
| **Tier 0** | Internal, no external effect | Search, verify, compare, rank, draft messages, prepare counteroffers (not send), read or update mission state, generate internal reports, suggest shortlist changes | No approval needed. Run by a Committee Member, the HOD, or the Agent | Logged in the audit trail |
| **Tier 1** | Routine external | First enquiry or quotation request that states no price, budget, or terms. Clarification questions. Follow-ups that repeat already approved content. Meeting-slot requests or calendar invites with no commercial commitment | A Committee Member who is **not** the requester, or the HOD | Executes only with a valid single-use approval token |
| **Tier 2** | High-risk external | Counteroffers. Any message that states a price, budget, quantity tier, payment term, or delivery term. Best-and-final requests. Sponsorship proposals and benefit offers. Attaching decks, quotations, or documents. Any message flagged by escalation rules (ambiguous, urgent, sensitive). First contact with a supplier carrying a risk or fraud flag | **HOD only** | Executes only with a valid HOD approval token |
| **Tier 3** | Commitment and financial | Accepting an offer. Placing an order or purchase order. Any payment or deposit. Signing or entering a binding agreement. Confirming a sponsorship deal. Changing the hard budget, minimum quality, deadline, negotiation limits, or approval policy of an active mission. Overriding a walk-away decision | **HOD only**, with explicit confirmation of the final verified terms | Executes only after HOD approval **and** a passing verified-terms check |

### 22.3 Permission matrix

| Action | Committee Member | HOD | StakeMate Agent |
|---|---|---|---|
| Create a mission and enter a goal | Yes | Yes | No |
| Set target price and scoring weights | Yes | Yes | Suggest only |
| Set hard budget, minimum quality, deadline, max rounds, approval policy at mission creation | Propose | Yes (confirms) | No |
| Change those limits on an active mission | Request (Tier 3) | Yes | No |
| Run search, verification, comparison, ranking | Yes | Yes | Yes (via tools) |
| Add or remove shortlist candidates | Yes | Yes | Suggest only |
| Draft messages and counteroffers | Yes | Yes | Yes |
| Approve Tier 1 actions | Yes (not own requests) | Yes | No |
| Approve Tier 2 actions | No | Yes | No |
| Approve Tier 3 actions (orders, payments, commitments) | No | Yes | No |
| View approval inbox | Own missions and Tier 1 queue | All | No |
| Respond to escalations | View only | Yes | No |
| View audit log | Own missions | All | No |
| Export reports | Yes | Yes | No |
| Manage users and role assignments | No | Yes | No |
| Manage integrations, API keys, tokens | No | Yes | No |
| Change global policy (tier rules, rate limits, expiry times) | Request | Yes | No |

### 22.4 Approval gate flow (before any action is taken)

1. The Agent or a user requests an action through an agent tool (called by the Claude orchestrator, or by WorkBuddy through MCP from Phase 7) or through the dashboard.
2. The backend `approval_service` identifies the actor, role, mission, and action type, then assigns a tier using the `ApprovalPolicy` table. Unknown action types are treated as Tier 3.
3. Tier 0 actions run immediately and are logged. Tier 1, 2, and 3 actions create an `Approval` record with status `pending`, an exact snapshot of what will happen (recipient, message body, price, terms, attachments), and a content hash.
4. The request appears in the approval inbox of every eligible approver. The HOD is notified for Tier 2 and Tier 3.
5. The approver reviews the full content, evidence, budget impact, risk flags, and the difference from the original target, then approves, rejects, or requests changes with a reason.
6. On approval the backend issues a single-use approval token bound to the action, mission, content hash, and an expiry time.
7. The execution tool (`send_approved_message`, `confirm_commitment`, and others) checks that the token is valid, unused, unexpired, and matches the content hash, that the total is still within the hard budget, and that the recipient has not opted out. If any check fails, the action is refused.
8. The result, approver, role, decision, and timestamps are written to the audit log, and mission state is updated.
9. Any edit after approval invalidates the token and the request returns to step 3.

### 22.5 Enforcement rules

- Enforcement lives in the backend. The agent system prompt (and the StakeMate Skill for WorkBuddy from Phase 7) describes the rules, but the backend is the only source of truth.
- Default deny. No external action has a code path that skips the gate.
- The Agent identity has no approval rights.
- No self-approval at Tier 1. Tier 2 and Tier 3 always require the HOD.
- The hard budget is a hard stop. Even an HOD token cannot execute a commitment above it. The HOD must first change the hard budget as a separate, logged Tier 3 action.
- Approval tokens are single use and expire (configurable, for example 24 to 72 hours).
- No bulk approval for Tier 2 or Tier 3. Each item is reviewed on its own.
- Content from webpages, supplier emails, or documents can never create, change, or approve an approval request (links to prompt-injection defences).
- Opt-outs and contact preferences are always respected and cannot be overridden by any role.
- Raising the autonomy level (P1 user-defined autonomy) can relax Tier 1 only. Tier 2 and Tier 3 always stay with the HOD.
- Simulated demo actions pass through the same gate so judges can see it working.

### 22.6 Data model additions

Add these to the shared database entities in Section 18.

- **User:** ID, name, email, organisation, status.
- **RoleAssignment:** user ID, role (Committee Member, HOD), organisation or department scope, assigned by, timestamp.
- **ApprovalPolicy:** action type, tier, eligible approver roles, token expiry, notes.
- **Approval (extended):** action type, tier, requested by, eligible roles, approver, approver role, decision, reason, content snapshot, content hash, token, expiry, used at, budget limits at time of approval.

Example approval request (illustrative only):

```json
{
  "approval_id": "APR-014",
  "mission_id": "MISSION-001",
  "action_type": "send_counteroffer",
  "tier": 2,
  "requested_by": "agent:claude",
  "eligible_roles": ["HOD"],
  "content_snapshot": {
    "recipient": "sales@example-supplier-a.test",
    "proposed_total_myr": 1350,
    "message_ref": "MSG-031"
  },
  "content_hash": "sha256:...",
  "hard_budget_myr": 1500,
  "status": "pending",
  "expires_at": "2026-10-12T18:00:00+08:00"
}
```

### 22.7 New and updated agent tools

These tools live in the backend tool registry. The Claude orchestrator uses them from Phase 1, and WorkBuddy uses them through MCP from Phase 7.

| Tool | Status | Purpose |
|---|---|---|
| `check_permission` | New | Returns the tier and whether the actor may run or must request approval |
| `request_approval` | Updated | Takes action type and content snapshot, returns approval ID, tier, eligible roles |
| `get_approval_status` | New | Lets the Agent wait for or read a decision without guessing |
| `send_approved_message` | Updated | Requires a valid approval token that matches the content hash |
| `confirm_commitment` | New | Tier 3 only. Records an accepted offer, order, or sponsorship confirmation after HOD approval. In the hackathon it records the commitment and makes no real payment |

### 22.8 Dashboard additions

- Login with a visible role badge.
- Approval inbox filtered by role, with tier labels and expiry countdown.
- HOD queue for Tier 2 and Tier 3 with budget impact, evidence links, and a comparison against the original target.
- HOD settings page for users, roles, integrations, and policy settings.
- Audit log viewer with requester, approver, role, and decision columns.

---

## 23. Build Phases

These phases expand the build order in Section 13 so that every item in this document has a place. Phases 0 to 8 form the hackathon MVP (P0). Phase 9 holds the P1 extensions. Phase 10 holds the P2 roadmap.

### 23.0 Build approach. Own orchestrator first, WorkBuddy later

StakeMate is **not** built around WorkBuddy from the start. Phases 1 to 6 build a complete, working product that runs its own agent loop using the **Claude API (Anthropic) with tool use**. WorkBuddy is added in **Phase 7** as a second orchestrator that calls the exact same tools.

This works because of three design rules that apply from Phase 1.

- **One tool registry.** Every agent tool (search, compare, draft, request approval, and so on) is a plain Python function with typed input and output schemas, registered in one place in the backend. Tools never depend on Claude, MCP, or WorkBuddy.
- **One tool executor.** Every tool call, whichever orchestrator makes it, goes through the same backend executor that checks permissions, applies the approval gate (Section 22), and writes the audit log.
- **Thin adapters.** The Claude orchestrator (Phase 1 onward) turns registry schemas into Claude tool definitions. The WorkBuddy MCP server (Phase 7) turns the same schemas into MCP tools that forward to the backend. Swapping or adding an orchestrator does not touch business logic or safety rules.

The Claude orchestrator stays in the product after Phase 7 as a fallback, and a setting chooses which orchestrator runs a mission.

### Phase 0. Setup and access verification

**Goal.** Get the development environment and every non-WorkBuddy account working.

- Pick the stack from Section 19 (Next.js + Tailwind CSS, FastAPI, Supabase PostgreSQL, Claude API through the Anthropic Python SDK).
- Create the repository, project folders, Python virtual environment, and Next.js app (Windows PowerShell commands).
- Create the Supabase project and get the database connection string and auth keys.
- Get an Anthropic API key and confirm a test call works.
- Request or test access for the search API (Brave Search or Tavily), email (Gmail API or Microsoft Graph), calendar (Google Calendar API or Microsoft Graph), and a Python PDF library. Record the status of each.
- Set up secure secret storage (`.env` files ignored by git) and request least-privilege scopes only.
- Decide test accounts for the two roles (Committee Member and HOD), with at least two Committee Member accounts so the no-self-approval rule can be tested.
- WorkBuddy is **not** built against in this phase. At most, one team member signs in once to confirm the hackathon account exists (Section 20, item 12), so there are no surprises in Phase 7.

**Exit criteria.** Backend and frontend both start locally, the database connection works, a Claude API test call succeeds, access status for each external API is recorded, and no secrets live in code.

### Phase 1. Foundation, access control, tool registry, and first agent loop

**Goal.** Build the shared mission state and the approval gate, then prove an AI orchestrator can call StakeMate tools safely.

- Create the database schema for all entities in Section 18 (Mission, Stakeholder/Supplier, Evidence/Source, Quotation, Negotiation, Message, Approval, Task/Event log, Outcome) plus the Section 22.6 additions (User, RoleAssignment, ApprovalPolicy, extended Approval).
- Add authentication and role-based access for Committee Member and HOD, plus the Agent service identity.
- Build `approval_service` with risk tiers, the gate flow, single-use tokens, expiry, and no self-approval (Sections 22.2 to 22.5).
- Write every tool call, decision, and approval to the audit log.
- Build the FastAPI backend skeleton with mission create, read, and update, and the `stakeholder_database` component.
- Build the `tool_registry` and `tool_executor` (Section 23.0).
- Register the first tools. The common workflow tools `read_mission_state`, `update_mission_state`, `request_approval`, `check_permission`, `get_approval_status`, the demo tools `search_suppliers` and `prepare_counteroffer` (same behaviour as the Section 17 starter code, on simulated data), and a simulated `send_approved_message` that writes to a mock outbox so the gate can be tested.
- Build the `claude_orchestrator` with a minimal tool-use loop and a hard iteration limit.
- Build the Next.js goal form (goal, budget, deadline, requirements, approval settings), a basic mission dashboard, login with role badge, the approval inbox, and an audit log view.
- Write the first agent system prompt describing tool purpose, order, constraints, and the approval rules. It becomes the basis of the WorkBuddy Skill in Phase 7.

**Exit criteria.** The Claude orchestrator calls the demo tools through the tool executor and returns their results (this replaces the old WorkBuddy first integration milestone). A Committee Member can create a mission. A simulated external action is blocked until the correct role approves it, and the audit log records every step.

### Phase 2. Goal understanding and agent orchestration

**Goal.** Turn one natural-language request into a structured, constrained mission, using the Claude orchestrator.

- Natural-language goal input.
- Goal decomposition into research, communication, and negotiation tasks.
- Requirement extraction for product, quantity, budget, location, deadline, and quality.
- Clarification engine that asks only for missing information needed to act.
- Task dependency management and the agent execution loop (observe, choose next action, repeat).
- Dynamic task planning hooks for later replanning.
- Confidence and uncertainty reporting that flags incomplete evidence instead of guessing.
- Store the negotiation boundaries from Section 9 B3 (target price, hard budget, minimum quality, deadline, negotiation limit, approval policy). Once the mission is active, changes to these become Tier 3 HOD actions.
- Build the `goal_manager` and `workflow_orchestrator` components.

**Exit criteria.** The Section 14 demo request produces a structured mission with all constraints, and the agent asks only essential questions.

### Phase 3. Module A, discovery and evaluation (P0)

**Goal.** Find, verify, compare, and rank at least three candidates with evidence.

- Agent tools `search_stakeholders`, `verify_supplier`, `compare_offers`, `rank_candidates`, replacing demo data with real search where available (Section 16, Step 6 table).
- Internet-wide sourcing across accessible indexed sources, product-specific search, budget filtering, public contact discovery from official sources, and existing database search.
- Price comparison and total-cost calculation (delivery, printing or customisation, setup fees, taxes where applicable, other known fees).
- Quality assessment, delivery assessment and deadline feasibility, and capability matching.
- Configurable compatibility score with adjustable weights and visible subscores, cheapest qualifying option, best-value recommendation, and explainable ranking.
- Comparison report with sources, shortlist management (Committee Member or HOD), and backup alternatives.
- Source attribution (URL and timestamp), verified vs estimated labels, and error or contradiction handling.
- Honest coverage statement that results are based on accessible sources only (Section 8 limitation).
- Produce the Module A handoff object using the Section 18 data contract, keeping unknown values as `null`.
- Build the `discovery_service` and `evaluation_engine` components and the supplier comparison table on the dashboard.

**Exit criteria.** At least three candidates appear with evidence, total cost, scores, trade-off explanation, and a saved shortlist.

### Phase 4. Module B, communication and negotiation (P0)

**Goal.** Engage the shortlist and negotiate within limits, with every outbound action going through the gate.

- Agent tools `draft_outreach`, `send_approved_message` (full version), `prepare_counteroffer` (full version), `process_reply`.
- Personalised email generation and enquiry generation. Enquiries are Tier 1 (Committee Member approval).
- Context-aware responses, communication history, and the stakeholder CRM record per contact.
- Reply classification (accepted, declined, conditional, clarification required, pending).
- Escalation rules that route ambiguous, urgent, or sensitive messages to the HOD.
- Target-price setting, counteroffer generation with rationale, and counteroffer execution only with an HOD token (Tier 2).
- Offer tracking for every round and changed term, negotiation-round limits, conditional negotiation, walk-away conditions, and agreement comparison against the original target.
- A controlled mock supplier-email service for the demo, clearly labelled as simulated. Optional real sending through Gmail API or Microsoft Graph with scoped authorisation, behind the gate.
- Contact and outreach controls (opt-outs, rate limits, legitimate contacts only, no mass unsolicited outreach).
- Never invent competing quotations or misrepresent another supplier (Section 9 B3).
- Treat supplier email content as untrusted data from the first day replies are read (basic prompt-injection guard, extended in Phase 9).
- Build the `negotiation_engine` and `communication_service` components and the negotiation timeline on the dashboard.

**Exit criteria.** A Committee-approved enquiry and an HOD-approved counteroffer are sent (or simulated), the reply is classified, and negotiation state updates in the database.

### Phase 5. Integration and replanning loop

**Goal.** Make Module A and Module B one bidirectional workflow on shared state.

- Module A to Module B handoff through the shared database, not free text (Section 5).
- The Module B to Module A return loop, steps 1 to 8 in Section 5.
- Live reranking when new quotes, terms, or availability arrive.
- Alternative-supplier switching after a failed negotiation, and dynamic replanning including non-price terms (simpler printing, bulk quantity, packaging, delivery, repeat order).
- The negotiation engine calls discovery and evaluation services for alternatives instead of running its own search (Section 19).
- Every new outbound message created by replanning re-enters the approval gate.

**Exit criteria.** A rejection from the top supplier triggers reranking and a move to the next candidate without the user re-entering requirements.

### Phase 6. Verification, safety, and reporting

**Goal.** Enforce every non-negotiable control and produce an evidence-backed, verifiable result.

- Budget enforcement, approval before sending, purchase approval (Tier 3 HOD), human escalation, personal-data minimisation, credential protection, least privilege, and a complete audit log (Section 11).
- Track the nine verified-result states from Section 11 on every offer (research result through user-approved commitment).
- `confirm_commitment` tool for Tier 3 actions. In the hackathon it records the HOD-approved commitment and issues no real payment.
- Dashboard components from Section 12 (mission summary, candidate count and source coverage, shortlist and ranked comparison, evidence links and data freshness, negotiation timeline and current offer per supplier, live agent activity and next action, approval inbox, budget and total-cost tracker, savings calculation, final recommendation and outstanding risks).
- `create_final_report` tool and `reporting_service` component (best option, total landed cost, quality evidence, delivery terms, communication history, savings against a comparable quote, remaining risks, approval status).
- Measurable outcomes from Section 12 with documented definitions. Claim savings only on equivalent cost and verified terms. Label simulated metrics.

**Exit criteria.** The full Section 14 scenario runs end to end on the Claude orchestrator. The final report is produced, the best deal shows "awaiting HOD approval", and nothing is committed without the HOD.

### Phase 7. WorkBuddy integration

**Goal.** Add WorkBuddy as the orchestrator on top of the finished product, without changing business logic or safety rules.

- Install WorkBuddy, sign in, and run the planning prompt from Section 16, Step 1.
- Verify the current MCP setup route (Settings → MCP → Add MCP Server, or the newer screen) using the official MCP and connector guides in Section 25.
- Check whether WorkBuddy Enterprise Managed Agents APIs are available (Section 20, item 12). Only use them if the dashboard must start WorkBuddy sessions directly.
- Install `mcp[cli]` (Section 16, Step 2) and build the `workbuddy_mcp_server` using FastMCP, following the Section 17 starter pattern. It registers every tool in the tool registry and forwards each call to the backend tool executor with a WorkBuddy agent service token, so the approval gate and audit log stay in the backend.
- Connect it to WorkBuddy using the stdio configuration in Section 16, Step 4 (absolute Windows paths).
- Turn the Phase 1 agent system prompt into the StakeMate Skill (tool purpose, ordering, constraints, approval rules, untrusted-content rule), following the MCP + Skill pattern in Section 7.
- Run the Section 16, Step 5 test prompt. **First WorkBuddy integration milestone.** WorkBuddy calls the StakeMate tools and returns their results.
- Run the full Section 14 scenario with WorkBuddy as the orchestrator. A Committee Member creates the mission in the dashboard, WorkBuddy runs it by mission ID, and the dashboard shows progress from shared state.
- Add an orchestrator setting (Claude or WorkBuddy) per mission, record which orchestrator acted in the audit log (`agent:claude` or `agent:workbuddy`), and keep the Claude orchestrator as the fallback.
- Leave buffer time. If WorkBuddy access or MCP configuration fails, the product still works on the Claude orchestrator while the issue is fixed.

**Exit criteria.** WorkBuddy runs the Section 14 scenario end to end through the MCP tools, every external action is still blocked until the right role approves it, and the audit log shows `agent:workbuddy` as the requester.

### Phase 8. Demo readiness and pitch

**Goal.** Deliver the Section 14 scenario cleanly on WorkBuddy and map it to the judging criteria.

- Run the demo with WorkBuddy as the orchestrator, since the track judges meaningful use of WorkBuddy (Section 15). Keep the Claude orchestrator ready as a backup only.
- Seed the Section 14 mock dashboard data and activity timeline, clearly labelled as simulated. Keep the live search integration separate.
- Rehearse with Committee Member and HOD logins so judges see the gate (Committee Member approves the enquiry but cannot approve the counteroffer, HOD approves the counteroffer and the final deal).
- Map each demo moment to the Section 15 judging table.
- Run failure drills from Section 20, item 10 (no reply, failed search, API rate limit, inconsistent terms), plus a WorkBuddy connection failure that falls back to the Claude orchestrator.
- Tick off the Section 13 MVP checklist and the P0 items in the development checklist.
- Prepare the closing statement and product line from Sections 15 and 21.

**Exit criteria.** One uninterrupted WorkBuddy run from user request to HOD approval screen with all mock data labelled.

### Phase 9. P1 extensions (only after the core loop works)

**9a. Orchestration.** Workflow checkpoints, parallel research, failure recovery, user-defined autonomy (Tier 1 only, Section 22.5).

**9b. Module A.** Multi-source search, geographic filtering, sponsor discovery, collaborator discovery, search expansion, review analysis, review credibility flags, reliability assessment, risk and suitability checks, target-price estimation.

**9c. Module B.** Sponsorship proposals (Tier 2), document attachments (Tier 2), multiple communication channels, reply monitoring, intent and objection detection, automated follow-up scheduling (Tier 1 when repeating approved content), multilingual messages in English, Bahasa Malaysia, and Chinese (approver sees an English version), multi-variable bargaining, win-win optimiser, bulk discounts, best-and-final offer (Tier 2), cross-supplier benchmarking using legitimate comparable quotes, negotiation debrief.

**9d. Meetings, collaboration, and relationships (Use Case C).** Meeting-slot discovery, calendar integration (external invites Tier 1), agenda generation, meeting notes and summarisation, action-item extraction, meeting follow-up emails, commitment tracker, relationship history, team collaboration on one mission, duplicate contact detection, reusable templates.

**9e. Sponsorship workflow (Use Case A).** Event brief builder, sponsor matching, sponsorship tier generator (Gold, Silver, Bronze), benefit matching, proposal personalisation, sponsorship deck generation, sponsorship pipeline, sponsorship negotiation (Tier 2, deal confirmation Tier 3), sponsorship value tracking (cash vs in-kind), in-kind sponsorship optimisation.

**9f. Trust.** Full prompt-injection defences, supplier fraud warnings.

**9g. Dashboard.** Sponsorship pipeline dashboard, response analytics, time-saved estimate, report export (PDF and CSV), mission templates.

Every new tool added in Phase 9 goes into the tool registry, so it is available to both the Claude orchestrator and WorkBuddy automatically.

### Phase 10. P2 advanced roadmap

- Multi-agent collaboration and the multi-agent negotiation war room.
- Price history and cross-mission benchmarking (performance benchmarking).
- Relationship intelligence graph and relationship health monitoring.
- Sponsor deliverable tracker, post-event reporting and thank-you messages, future-partner recommendations.
- Multi-organisation workspaces with roles scoped per organisation, and advanced analytics.
- Enterprise Managed Agents APIs if the dashboard must start WorkBuddy sessions directly (only once access is verified).

---

## 24. Phase Coverage Map

This map confirms that every section and feature in this document is assigned to a phase.

### 24.1 Sections to phases

| Section | Covered in |
|---|---|
| 1. Executive Summary (Discover, Engage, Negotiate, Coordinate, Execute, Verify) | Discover P3, Engage P4, Negotiate P4, Coordinate P4 and P9d, Execute P4 and P6, Verify P6 |
| 2. Problem Statement | P8 pitch, pain points in 24.2 |
| 3. Solution and core principles | 24.3 |
| 4. Use Case B Procurement (main demo) | P2 to P8 |
| 4. Use Case A Sponsorship | P9e |
| 4. Use Case C Collaboration | P9d, P9b collaborator discovery |
| 5. Module A and B integration | P3 handoff, P5 loop |
| 6. End-to-end workflow | P2 (step 1), P3 (2 to 3), P4 (4 to 6), P5 (7), P6 (8 to 9) |
| 7. Architecture | P1 (backend, database, tool registry, Claude orchestrator), P7 (WorkBuddy, MCP + Skill), tools in 24.4 |
| 8. Module A | P3 (P0), P9b (P1), P10 (P2) |
| 9. Module B and B3 boundaries | P2 (boundaries), P4 (P0), P9c (P1) |
| 10. Feature tables A to G | 24.5 |
| 11. Trust, Safety, Verification | P1, P4, P6, P9f |
| 12. Dashboard and measurable outcomes | P1 (basic), P3, P4, P6, P9g |
| 13. MVP scope, build order, checklists | P0 to P10 |
| 14. Demo scenario and mock data | P6 (Claude run), P7 (WorkBuddy run), P8 (demo) |
| 15. Judging strategy | P8 |
| 16. WorkBuddy beginner guide, Steps 1 to 6 | Steps 1 to 5 in P7, Step 6 integrations in P3, P4, P9d |
| 17. Starter MCP server code | Tool behaviour in P1, MCP wrapper in P7 |
| 18. Data contract and database entities | P1 schema, P3 handoff |
| 19. Tech stack and logical components | P0 stack, components in 24.4 |
| 20. Product decisions 1 to 12 | 1 P9 gating, 2 P1 and P7, 3 P5, 4 P1 and P7, 5 P4 and P8, 6 P3, 7 P3 and P6, 8 P1 and P2, 9 P6, 10 P5 and P8, 11 P4, 12 P0 (account check) and P7 |
| 21. Closing pitch | P8 |
| 22. Access Control and Approval Governance | Built P1, enforced P4, P5, P6, P7, shown P8 |
| 25. Official references | P7 |

### 24.2 Pain points to phases

| Pain point (Section 2) | Addressed in |
|---|---|
| Hard to source suitable stakeholders | P3, P9b |
| Hard to find the right contact or official channel | P3 public contact discovery |
| Hard to initiate and sustain communication | P4, P9c follow-up |
| Hard to liaise across multiple platforms | P9c multiple channels and reply monitoring |
| Hard to follow up consistently | P9c follow-up scheduling |
| Hard to persuade or explain mutual value | P9c win-win optimiser, P9e proposals |
| Hard to find a middle ground | P4 conditional negotiation, P9c multi-variable bargaining |
| Hard to negotiate to the target price | P4 |
| Hard to coordinate a meeting time | P9d |
| Hard to compare quality, price, reliability, reviews, delivery | P3, P9b |
| Hard to manage commitments and deadlines after meetings | P9d commitment tracker |
| Hard to keep full history and avoid repeat work | P1 audit log, P3 database search, P4 history, P9d duplicate detection |
| Clubs and small businesses lack dedicated teams | P1 roles, P9d team collaboration |

### 24.3 Core principles to phases

| Principle (Section 3) | Enforced in |
|---|---|
| User goal and measurable outcome first | P2, P6 |
| Shared persistent mission state | P1, P5 |
| Structured data handoffs | P3, P5 |
| Autonomy inside user-defined boundaries | P1 (Section 22), P2 |
| Consequential results supported by evidence | P3, P6 |
| Live vs estimated vs simulated labels | P3, P6, P8 |

### 24.4 Tools and components to phases

| Item | Phase |
|---|---|
| `tool_registry`, `tool_executor`, `claude_orchestrator` | P1 |
| `search_suppliers`, `prepare_counteroffer` (demo), `send_approved_message` (simulated) | P1 |
| `read_mission_state`, `update_mission_state`, `request_approval`, `check_permission`, `get_approval_status` | P1 |
| `search_stakeholders`, `verify_supplier`, `compare_offers`, `rank_candidates` | P3 |
| `draft_outreach`, `send_approved_message` (full), `prepare_counteroffer` (full), `process_reply` | P4 |
| `confirm_commitment`, `create_final_report` | P6 |
| `stakeholder_database`, `approval_service` | P1 |
| `goal_manager`, `workflow_orchestrator` | P2 (loop completed in P5) |
| `discovery_service`, `evaluation_engine` | P3 |
| `negotiation_engine`, `communication_service` | P4 |
| `reporting_service` | P6 |
| `workbuddy_mcp_server`, StakeMate Skill | P7 |

### 24.5 Feature tables to phases

| Table in Section 10 | P0 features | P1 features | P2 features |
|---|---|---|---|
| A. Orchestration | P2 | P9a | P10 |
| B. Module A | P3 | P9b | P10 (price history) |
| C. Module B | P4 (alternative switching P5) | P9c | none |
| D. Meetings and relationships | Stakeholder CRM P4 | Role-based access moved to P1 (now P0), rest P9d | P10 |
| E. Sponsorship | none | P9e | P10 |
| F. Trust and verification | P1, P4, P6 | P9f (basic injection guard in P4) | none |
| G. Dashboard and reporting | P1, P3, P4, P6 | P9g | P10 |

---

## 25. Official References

Verify the current version and access requirements before implementing against these sources:

- WorkBuddy website: <https://www.workbuddy.ai/>
- WorkBuddy MCP Guide: <https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide>
- WorkBuddy Connector Development Guide: <https://open.workbuddy.cn/en/docs/connector>
- Model Context Protocol: <https://modelcontextprotocol.io/>

**Documentation caveat:** Product UIs, schemas, APIs, account permissions, and feature availability can change. Confirm the exact MCP configuration and any managed-agent API access from the current official documentation before the hackathon demo.
