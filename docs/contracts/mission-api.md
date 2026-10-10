# Phase 1–2 contract

The executable frontend contract is `apps/web/src/lib/demo.ts`. Its `NewBrief`, `ProcurementCase`, `Vendor`, `Activity`, `DemoState` and `Action` types govern the fixture prototype. `CaseRepository` defines the replacement boundary for backend persistence.

- Money uses integer sen. Delivery cost `null` means unknown; never zero.
- Dates are actual ISO calendar dates; display uses Asia/Kuala_Lumpur.
- Offers are fictional and scoped to the seeded 300-tote procurement case.
- Eligibility requires confirmed total cost, budget compliance, specifications and arrival date.
- Editing a draft increments its revision and removes approval.
- Organisers approve/reject messages and explicitly choose the vendor. Teammates create briefs, prepare sample research and edit drafts. Observers read only.
- Research may prepare comparisons but never changes a human's final choice.
- No fixture action contacts a supplier, purchases anything or invokes a live agent.
- Local saved records are validated on restoration. Invalid records reset to the sample workspace.

Phase 3 will expose the backend contract through OpenAPI and replace local fixture storage. Server-side role checks must enforce the same rules; the demo profile switcher alone is not authentication. MCP will never expose a final vendor selection tool.

Implemented routes: `/`, `/demo`, `/workspace`, `/brief/new`, `/cases/:id`, `/cases/:id/vendors`, `/cases/:id/conversations`, `/cases/:id/decision`, `/cases/:id/activity`, `/inbox`, `/vendors`, `/connections`.

The Python package also defines initial validated `NewBrief` and human-only `VendorChoice` contracts in `schemas/domain.py`; no application endpoints are mounted. MCP currently verifies transport only. Its single structured health result contains request ID, product, status, capabilities and phase. Application API endpoints do not exist yet.
