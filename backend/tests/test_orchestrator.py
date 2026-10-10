"""Kickoff Step 1.10, test 16: the Claude loop with a mocked Anthropic client."""

from sqlalchemy import select

from app.agent.claude_orchestrator import ClaudeOrchestrator
from app.models import Approval, AuditLog
from tests.helpers import (
    FakeAnthropic,
    cheapest_within_budget,
    create_active_mission,
    fake_response,
    sent_count,
    text_block,
    tool_use_block,
)


def enquiry_to_cheapest(kwargs):
    supplier = cheapest_within_budget(kwargs)
    return fake_response(
        "tool_use",
        text_block(f"{supplier['name']} is the cheapest within budget. Sending an enquiry for approval."),
        tool_use_block(
            "send_approved_message",
            {
                "stakeholder_id": supplier["stakeholder_id"],
                "kind": "enquiry",
                "body": "Hello, could you quote 300 custom tote bags delivered by 25 October?",
            },
        ),
    )


def test_loop_stops_on_approval_required_and_sends_nothing(db, people):
    mission = create_active_mission(db, people)
    client = FakeAnthropic(
        [
            fake_response(
                "tool_use",
                tool_use_block("search_suppliers", {"product": "Custom tote bags", "budget": 1500}),
            ),
            enquiry_to_cheapest,
            # A third response would mean the loop kept going after approval_required.
            fake_response("end_turn", text_block("should never be reached")),
        ]
    )

    result = ClaudeOrchestrator(db, client=client, model="test-model").run(
        mission, "Find suppliers and send an enquiry to the cheapest within budget", on_behalf_of=people.cm_a.id
    )

    assert result.status == "approval_required"
    assert len(client.calls) == 2
    assert [(c.name, c.status) for c in result.tool_calls] == [
        ("search_suppliers", "ok"),
        ("send_approved_message", "approval_required"),
    ]
    assert result.approvals[0]["tier"] == 1
    assert result.approvals[0]["action_type"] == "send_enquiry"
    approval = db.get(Approval, result.approvals[0]["approval_id"])
    assert (approval.status, approval.requested_by, approval.requested_on_behalf_of) == (
        "pending",
        "agent:claude",
        people.cm_a.id,
    )
    assert sent_count(db, mission) == 0

    # The model saw every registry tool and the safety rules.
    first_call = client.calls[0]
    assert {t["name"] for t in first_call["tools"]} >= {"read_mission_state", "search_suppliers", "send_approved_message"}
    assert "data, not instructions" in first_call["system"]
    assert first_call["model"] == "test-model"

    runs = db.scalars(select(AuditLog).where(AuditLog.event_type == "agent.run", AuditLog.mission_id == mission.id)).all()
    assert len(runs) == 1
    assert runs[0].result_ref["status"] == "approval_required"


def test_loop_returns_final_answer(db, people):
    mission = create_active_mission(db, people)
    client = FakeAnthropic(
        [
            fake_response("tool_use", tool_use_block("read_mission_state", {})),
            fake_response("end_turn", text_block("The mission is active.")),
        ]
    )
    result = ClaudeOrchestrator(db, client=client, model="test-model").run(mission, "Status?")
    assert (result.status, result.final_text) == ("completed", "The mission is active.")


def test_loop_respects_max_iterations(db, people):
    mission = create_active_mission(db, people)
    client = FakeAnthropic([fake_response("tool_use", tool_use_block("read_mission_state", {})) for _ in range(3)])
    result = ClaudeOrchestrator(db, client=client, model="test-model", max_iterations=3).run(mission, "Loop")
    assert result.status == "max_iterations"
    assert len(client.calls) == 3


def test_tool_results_reach_the_model_as_data(db, people):
    mission = create_active_mission(db, people)
    client = FakeAnthropic(
        [
            fake_response("tool_use", tool_use_block("no_such_tool", {})),
            fake_response("end_turn", text_block("done")),
        ]
    )
    ClaudeOrchestrator(db, client=client, model="test-model").run(mission, "Try a bad tool")
    tool_result = client.calls[1]["messages"][-1]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert tool_result["is_error"] is True
    assert "Unknown tool" in tool_result["content"]
