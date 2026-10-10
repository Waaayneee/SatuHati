"""Kickoff Step 1.10, tests 1 to 14: the approval gate."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError

from app.auth.actor import AGENT_CLAUDE, agent_actor
from app.models import Approval, AuditLog, Message, Negotiation
from app.services import approval_service, audit_service
from app.services.errors import Refused
from app.tools import executor
from tests.helpers import (
    AGENT_HEADERS,
    actor_for,
    approve_without_running,
    audit_rows,
    auth,
    counteroffer_args,
    create_active_mission,
    enquiry_args,
    make_stakeholder,
    sent_count,
)


def call_tool(client, mission, name, args):
    response = client.post(f"/agent/tools/{name}", json={"mission_id": str(mission.id), "args": args}, headers=AGENT_HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def decide(client, user, approval_id, decision="approved", reason="Looks right"):
    return client.post(f"/approvals/{approval_id}/decision", json={"decision": decision, "reason": reason}, headers=auth(user))


# 1 -----------------------------------------------------------------------------
def test_tier0_tool_runs_without_approval_and_writes_one_audit_row(client, db, people):
    mission = create_active_mission(db, people)
    before = {row.id for row in audit_rows(db, mission)}

    result = call_tool(client, mission, "search_suppliers", {"product": "Custom tote bags", "budget": 1500})

    assert result["status"] == "ok"
    assert result["tier"] == 0
    assert [s["data_source"] for s in result["result"]["suppliers"]] == ["demo", "demo", "demo"]
    assert db.scalar(select(func.count()).select_from(Approval).where(Approval.mission_id == mission.id)) == 0
    new_rows = [row for row in audit_rows(db, mission) if row.id not in before]
    assert len(new_rows) == 1
    assert (new_rows[0].event_type, new_rows[0].tool_name, new_rows[0].actor) == (
        "tool.executed",
        "search_suppliers",
        "agent:claude",
    )


# 2 -----------------------------------------------------------------------------
def test_agent_enquiry_creates_pending_tier1_approval_and_sends_nothing(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)

    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))

    assert result["status"] == "approval_required"
    assert result["tier"] == 1
    assert result["action_type"] == "send_enquiry"
    approval = db.get(Approval, result["approval_id"])
    assert approval.status == "pending"
    assert approval.requested_by == "agent:claude"
    assert approval.eligible_roles == ["committee_member", "hod"]
    message = db.scalars(select(Message).where(Message.approval_id == approval.id)).one()
    assert message.status == "pending_approval"
    assert sent_count(db, mission) == 0


# 3 -----------------------------------------------------------------------------
def test_requesting_member_cannot_approve_own_tier1_request(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    # Member A ran the agent, so A counts as the requester.
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier),
                              agent_actor(on_behalf_of=people.cm_a.id), mission.id)

    response = decide(client, people.cm_a, result["approval_id"])

    assert response.status_code == 403
    assert "requested this action" in response.json()["detail"]
    assert db.get(Approval, result["approval_id"]).status == "pending"
    assert sent_count(db, mission) == 0


def test_member_who_requested_directly_cannot_approve(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier), actor_for(db, people.cm_b), mission.id)

    assert decide(client, people.cm_b, result["approval_id"]).status_code == 403


# 4 -----------------------------------------------------------------------------
def test_other_member_approves_tier1_and_message_is_sent_simulated(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier),
                              agent_actor(on_behalf_of=people.cm_a.id), mission.id)

    response = decide(client, people.cm_b, result["approval_id"])

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "executed"
    assert body["approver_role"] == "committee_member"
    approval = db.get(Approval, result["approval_id"])
    db.refresh(approval)
    assert approval.used_at is not None and approval.token_hash
    message = db.scalars(select(Message).where(Message.approval_id == approval.id)).one()
    db.refresh(message)
    assert (message.status, message.is_simulated) == ("sent", True)
    assert message.sent_at is not None


# 5 -----------------------------------------------------------------------------
def test_counteroffer_is_tier2_member_refused_hod_approves(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = call_tool(client, mission, "send_approved_message", counteroffer_args(supplier, 1350))
    assert (result["status"], result["tier"], result["action_type"]) == ("approval_required", 2, "send_counteroffer")

    refused = decide(client, people.cm_b, result["approval_id"])
    assert refused.status_code == 403
    assert "Only the HOD" in refused.json()["detail"]

    approved = decide(client, people.hod, result["approval_id"])
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "executed"
    assert sent_count(db, mission) == 1
    rounds = db.scalars(select(Negotiation).where(Negotiation.mission_id == mission.id)).all()
    assert [(r.round_number, float(r.offer_total), r.status) for r in rounds] == [(1, 1350.0, "sent")]


# 6 -----------------------------------------------------------------------------
def test_agent_cannot_call_decision_endpoint(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))

    response = client.post(
        f"/approvals/{result['approval_id']}/decision",
        json={"decision": "approved", "reason": "agent tries"},
        headers=AGENT_HEADERS,
    )

    assert response.status_code == 403
    assert db.get(Approval, result["approval_id"]).status == "pending"
    refusal = db.scalars(select(AuditLog).where(AuditLog.event_type == "approval.decision_refused")).all()
    assert any(r.actor == "agent:claude" for r in refusal)


# 7 -----------------------------------------------------------------------------
def test_token_cannot_be_consumed_twice(db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier), AGENT_CLAUDE, mission.id)
    approval = db.get(Approval, result["approval_id"])
    hod = actor_for(db, people.hod)
    token = approve_without_running(db, approval, hod)

    executor.run_approved(db, approval.id, token, hod)
    assert db.get(Approval, approval.id).status == "executed"

    with pytest.raises(Refused):
        executor.run_approved(db, approval.id, token, hod)
    db.refresh(approval)
    assert approval.status == "executed"  # the second attempt does not change the result
    assert sent_count(db, mission) == 1


# 8 -----------------------------------------------------------------------------
def test_expired_approval_cannot_be_approved(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))
    approval = db.get(Approval, result["approval_id"])
    approval.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db.commit()

    response = decide(client, people.cm_b, approval.id)

    assert response.status_code == 409
    db.refresh(approval)
    assert approval.status == "expired"
    assert db.scalars(select(Message.status).where(Message.approval_id == approval.id)).one() == "refused"
    assert sent_count(db, mission) == 0


def test_expired_approval_cannot_be_executed(db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier), AGENT_CLAUDE, mission.id)
    approval = db.get(Approval, result["approval_id"])
    hod = actor_for(db, people.hod)
    token = approve_without_running(db, approval, hod)
    approval.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()

    with pytest.raises(Refused):
        executor.run_approved(db, approval.id, token, hod)
    db.refresh(approval)
    assert approval.status == "failed"
    assert sent_count(db, mission) == 0


# 9 -----------------------------------------------------------------------------
def test_changed_snapshot_is_refused_and_approval_fails(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))
    approval = db.get(Approval, result["approval_id"])
    # Someone edits the stored content after it was submitted (hash stays the old one).
    approval.content_snapshot = {**approval.content_snapshot, "body": "Edited after submission"}
    db.commit()

    response = decide(client, people.cm_b, approval.id)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert "Content changed" in body["execution_result"]["error"]
    assert sent_count(db, mission) == 0


def test_verify_and_consume_rejects_a_different_snapshot(db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = executor.execute(db, "send_approved_message", enquiry_args(supplier), AGENT_CLAUDE, mission.id)
    approval = db.get(Approval, result["approval_id"])
    hod = actor_for(db, people.hod)
    token = approve_without_running(db, approval, hod)
    tampered = {**approval.content_snapshot, "recipient": "someone-else@example.test"}

    with pytest.raises(Refused):
        approval_service.verify_and_consume(db, approval.id, token, tampered, hod)
    db.refresh(approval)
    assert approval.status == "failed"


# 10 ----------------------------------------------------------------------------
def test_unknown_action_type_is_tier3_and_hod_only(client, db, people):
    mission = create_active_mission(db, people)
    result = call_tool(client, mission, "request_approval",
                       {"action_type": "wire_transfer", "snapshot": {"amount_note": "deposit to a supplier"}})

    assert (result["status"], result["tier"], result["eligible_roles"]) == ("approval_required", 3, ["hod"])
    assert decide(client, people.cm_b, result["approval_id"]).status_code == 403
    assert decide(client, people.cm_a, result["approval_id"]).status_code == 403
    response = decide(client, people.hod, result["approval_id"])
    assert response.status_code == 200
    assert response.json()["status"] == "executed"
    assert response.json()["execution_result"]["performed"] is False


def test_classify_unknown_action_type_directly(db, people):
    assert approval_service.classify(db, "something_new").tier == 3


# 11 ----------------------------------------------------------------------------
def test_counteroffer_above_hard_budget_is_refused_at_request(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)

    result = call_tool(client, mission, "send_approved_message", counteroffer_args(supplier, 1600))

    assert result["status"] == "refused"
    assert "hard budget" in result["reason"]
    assert db.scalar(select(func.count()).select_from(Approval).where(Approval.mission_id == mission.id)) == 0
    assert db.scalar(select(func.count()).select_from(Message).where(Message.mission_id == mission.id)) == 0
    assert any(
        (r.event_type, r.tool_name) == ("tool.refused", "send_approved_message") for r in audit_rows(db, mission)
    )


# 12 ----------------------------------------------------------------------------
def test_enquiry_mentioning_rm1350_is_bumped_to_tier2(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)

    result = call_tool(client, mission, "send_approved_message",
                       enquiry_args(supplier, "Could you supply 300 tote bags for RM1,350 in total?"))

    assert (result["tier"], result["action_type"], result["eligible_roles"]) == (2, "send_terms_message", ["hod"])


# 13 ----------------------------------------------------------------------------
def test_opted_out_stakeholder_is_refused_at_request(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db, opted_out=True)

    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))

    assert result["status"] == "refused"
    assert "opted out" in result["reason"]
    assert db.scalar(select(func.count()).select_from(Approval).where(Approval.mission_id == mission.id)) == 0


def test_opted_out_stakeholder_is_refused_at_execution(client, db, people):
    mission = create_active_mission(db, people)
    supplier = make_stakeholder(db)
    result = call_tool(client, mission, "send_approved_message", enquiry_args(supplier))
    supplier.opted_out = True
    db.commit()

    response = decide(client, people.cm_b, result["approval_id"])

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert "opted out" in response.json()["execution_result"]["error"]
    assert sent_count(db, mission) == 0


# 14 ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE audit_log SET status = 'tampered' WHERE id = :id",
        "DELETE FROM audit_log WHERE id = :id",
        "TRUNCATE audit_log",
    ],
)
def test_audit_log_is_append_only(db, statement):
    row = audit_service.record(db, AGENT_CLAUDE, "test.append_only_probe")
    db.commit()

    with pytest.raises(DBAPIError, match="append-only"):
        with db.begin_nested():
            db.execute(text(statement), {"id": row.id})

    assert db.get(AuditLog, row.id).status == "ok"
