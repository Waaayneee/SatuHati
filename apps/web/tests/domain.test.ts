import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { initialState, applyAction, eligible, fitReason, totalCost, restoreState } from '../src/lib/demo.ts';

describe('KawTeam human decisions and demonstration permissions', () => {
  it('does not choose a vendor when research finishes', () => {
    const state = applyAction(initialState(), 'organiser', { type: 'research', caseId: 'case-totes' });
    assert.equal(state.cases[0].selectedVendorId, null);
    assert.equal(state.cases[0].stage, 'decision');
  });
  it('lets the organiser make an explicit final choice', () => {
    const state = applyAction(initialState(), 'organiser', { type: 'choose', caseId: 'case-totes', vendorId: 'willow' });
    assert.equal(state.cases[0].selectedVendorId, 'willow');
    assert.equal(state.cases[0].stage, 'decided');
  });
  it('blocks teammates from choosing a vendor', () => {
    assert.throws(() => applyAction(initialState(), 'teammate', { type: 'choose', caseId: 'case-totes', vendorId: 'willow' }), /Only the organiser/);
  });
  it('blocks observers from preparing research', () => {
    assert.throws(() => applyAction(initialState(), 'observer', { type: 'research', caseId: 'case-totes' }), /view-only/);
  });
  it('does not allow an over-budget final choice', () => {
    assert.throws(() => applyAction(initialState(), 'organiser', { type: 'choose', caseId: 'case-totes', vendorId: 'campus' }), /requirements/);
  });
  it('keeps unknown delivery costs unknown', () => {
    assert.equal(totalCost({ goodsSen: 134000, deliverySen: null }), null);
    assert.equal(eligible(initialState().cases[0], initialState().cases[0].vendors[1]), false);
  });
  it('prevents teammates approving messages', () => {
    assert.throws(() => applyAction(initialState(), 'teammate', { type: 'approve', caseId: 'case-totes' }), /Only the organiser/);
  });
  it('invalidates an approval when its draft changes', () => {
    const approved = applyAction(initialState(), 'organiser', { type: 'approve', caseId: 'case-totes' });
    const edited = applyAction(approved, 'teammate', { type: 'edit-draft', caseId: 'case-totes', body: 'Changed enquiry' });
    assert.equal(edited.cases[0].draft.status, 'pending');
    assert.equal(edited.cases[0].draft.revision, 2);
  });
  it('preserves an explicit user choice during a research refresh', () => {
    const selected = applyAction(initialState(), 'organiser', { type: 'choose', caseId: 'case-totes', vendorId: 'willow' });
    const refreshed = applyAction(selected, 'teammate', { type: 'research', caseId: 'case-totes' });
    assert.equal(refreshed.cases[0].selectedVendorId, 'willow');
  });
  it('recovers safely from invalid local storage', () => {
    assert.equal(restoreState('{invalid').cases.length, 2);
    assert.equal(restoreState('{"version":1,"cases":[]}').cases.length, 2);
  });
});

it('keeps tote fixtures out of unrelated briefs', () => {
  assert.throws(() => applyAction(initialState(), 'organiser', {type:'research',caseId:'case-workshop'}), /sample/);
});
it('recovers from invalid calendar dates and incomplete saved records', () => {
  const state=initialState(); state.cases[0].deadline='2026-99-99';
  assert.equal(restoreState(JSON.stringify(state)).cases[0].deadline,'2026-10-25');
  const incomplete=initialState(); delete (incomplete.cases[0] as Partial<typeof incomplete.cases[0]>).location;
  assert.equal(restoreState(JSON.stringify(incomplete)).cases[0].location,'Subang Jaya, Selangor');
});

it('explains delivery failure independently of price', () => {
  const c=initialState().cases[0]; const v={...c.vendors[2], arrival:'2026-10-29'};
  assert.equal(fitReason(c,v),'Arrives too late'); assert.equal(eligible(c,v),false);
});
