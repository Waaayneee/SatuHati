import type { Action, DemoState, ProfileId } from '../demo';
/** API-backed repository can replace the local fixture implementation in Phase 3. */
export interface CaseRepository {
  read(): DemoState;
  mutate(actor: ProfileId, action: Action): DemoState;
}
