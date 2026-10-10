"""docs/PHASE1_DEMO.md, end to end through the HTTP API with a scripted Claude."""

import pytest

from app.agent import claude_orchestrator
from app.api import missions as missions_api
from tests.helpers import (
    FakeAnthropic,
    auth,
    cheapest_within_budget,
    fake_response,
    text_block,
    tool_use_block,
)
from tests.test_missions import MISSION


@pytest.fixture
def scripted_claude(monkeypatch):
    """Lets each test queue the responses the next agent run will get."""
    queue: list = []

    class ScriptedOrchestrator(claude_orchestrator.ClaudeOrchestrator):
        def __init__(self, db, **kwargs):
            super().__init__(db, client=FakeAnthropic(queue.pop(0)), model="test-model")

    monkeypatch.setattr(missions_api, "ClaudeOrchestrator", ScriptedOrchestrator)
    return queue


def enquiry_step(kwargs):
    supplier = cheapest_within_budget(kwargs)
    return fake_response(
        "tool_use",
        tool_use_block(
            "send_approved_message",
            {
                "stakeholder_id": supplier["stakeholder_id"],
                "kind": "enquiry",
                "body": "Hello, could you quote 300 custom tote bags delivered by 25 October?",
            },
        ),
    )


def decide(client, user, approval_id, decision="approved"):
    return client.post(
        f"/approvals/{approval_id}/decision", json={"decision": decision, "reason": "Demo"}, headers=auth(user)
    )


def test_phase1_demo(client, people, scripted_claude):
    a, b, hod = people.cm_a, people.cm_b, people.hod

    # 1. Member A creates the mission.
    mission = client.post("/missions", json=MISSION, headers=auth(a)).json()
    assert mission["status"] == "awaiting_hod_confirmation"

    # 2. The HOD confirms the limits.
    assert client.post(f"/missions/{mission['id']}/confirm-limits", headers=auth(hod)).json()["status"] == "active"

    # 3-4. Member A runs the agent: search (demo data), then an enquiry to the cheapest within budget.
    scripted_claude.append(
        [fake_response("tool_use", tool_use_block("search_suppliers", {"product": "Custom tote bags", "budget": 1500})),
         enquiry_step]
    )
    run = client.post(
        f"/missions/{mission['id']}/agent/run",
        json={"prompt": "Find suppliers and send an enquiry to the cheapest within budget"},
        headers=auth(a),
    ).json()
    assert run["status"] == "approval_required"
    enquiry = run["approvals"][0]
    assert enquiry["tier"] == 1

    # Member B sees it in the inbox; so does A (own mission).
    assert enquiry["approval_id"] in [x["id"] for x in client.get("/approvals", headers=auth(b)).json()]
    assert enquiry["approval_id"] in [x["id"] for x in client.get("/approvals", headers=auth(a)).json()]

    # 5. A is refused, B approves, the message is sent as SIMULATED.
    assert decide(client, a, enquiry["approval_id"]).status_code == 403
    approved = decide(client, b, enquiry["approval_id"])
    assert approved.json()["status"] == "executed"
    detail = client.get(f"/missions/{mission['id']}", headers=auth(a)).json()
    sent = [m for m in detail["messages"] if m["status"] == "sent"]
    assert len(sent) == 1 and sent[0]["is_simulated"] is True and sent[0]["supplier"] == "Supplier B"

    # 6. A asks for a counteroffer at RM1,350: Tier 2, B refused, HOD approves.
    stakeholder_id = sent[0]["stakeholder_id"]
    scripted_claude.append(
        [
            fake_response(
                "tool_use",
                text_block("Sending a counteroffer for HOD approval."),
                tool_use_block(
                    "send_approved_message",
                    {
                        "stakeholder_id": stakeholder_id,
                        "kind": "counteroffer",
                        "body": "Thank you for your quotation of RM1450.00. Would you consider RM1350.00?",
                        "proposed_total_myr": 1350,
                    },
                ),
            )
        ]
    )
    run = client.post(
        f"/missions/{mission['id']}/agent/run", json={"prompt": "Send a counteroffer at RM1,350"}, headers=auth(a)
    ).json()
    counter = run["approvals"][0]
    assert (run["status"], counter["tier"]) == ("approval_required", 2)
    assert decide(client, b, counter["approval_id"]).status_code == 403
    assert decide(client, hod, counter["approval_id"]).json()["status"] == "executed"

    # 7. The audit log shows every step with actor and role.
    events = client.get("/audit", params={"mission_id": mission["id"]}, headers=auth(hod)).json()
    seen = {(e["event_type"], e["actor_role"]) for e in events}
    for expected in [
        ("mission.created", "committee_member"),
        ("mission.limits_confirmed", "hod"),
        ("tool.executed", "agent"),
        ("tool.approval_required", "agent"),
        ("approval.requested", "agent"),
        ("approval.decision_refused", "committee_member"),
        ("approval.approved", "committee_member"),
        ("approval.approved", "hod"),
        ("message.sent_simulated", "committee_member"),
        ("message.sent_simulated", "hod"),
        ("approval.executed", "hod"),
        ("agent.run", "agent"),
    ]:
        assert expected in seen, expected
    agent_rows = [e for e in events if e["actor"] == "agent:claude"]
    assert all(a.email in e["actor_label"] for e in agent_rows)
