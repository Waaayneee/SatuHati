"""Kickoff Step 1.10, test 15: mission lifecycle and Tier 3 limit changes."""

from decimal import Decimal

from app.models import Mission
from tests.helpers import auth

MISSION = {
    "goal_text": "300 custom tote bags for a 200-student tech event",
    "product": "Custom tote bags",
    "quantity": 300,
    "target_total_myr": 1350,
    "hard_budget_myr": 1500,
    "minimum_quality": 4.0,
    "delivery_deadline": "2026-10-25",
    "max_rounds": 3,
}


def test_mission_confirm_and_tier3_limit_change(client, db, people):
    created = client.post("/missions", json=MISSION, headers=auth(people.cm_a))
    assert created.status_code == 201, created.text
    mission = created.json()
    assert mission["status"] == "awaiting_hod_confirmation"
    assert mission["code"].startswith("MISSION-")

    # Only the HOD confirms limits.
    assert client.post(f"/missions/{mission['id']}/confirm-limits", headers=auth(people.cm_a)).status_code == 403
    confirmed = client.post(f"/missions/{mission['id']}/confirm-limits", headers=auth(people.hod))
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "active"

    # Non-limit fields change directly.
    notes = client.patch(f"/missions/{mission['id']}", json={"notes": "Prefer canvas"}, headers=auth(people.cm_a))
    assert notes.status_code == 200
    assert notes.json()["updated_fields"] == ["notes"]
    assert notes.json()["approval"] is None

    # A limit change on an active mission becomes a Tier 3 approval and changes nothing yet.
    change = client.patch(f"/missions/{mission['id']}", json={"hard_budget_myr": 1700}, headers=auth(people.cm_a))
    assert change.status_code == 200, change.text
    approval = change.json()["approval"]
    assert (approval["action_type"], approval["tier"], approval["status"]) == ("change_mission_limits", 3, "pending")
    assert change.json()["updated_fields"] == []
    assert db.get(Mission, mission["id"]).hard_budget_myr == Decimal("1500.00")

    for member in (people.cm_a, people.cm_b):
        refused = client.post(
            f"/approvals/{approval['id']}/decision",
            json={"decision": "approved", "reason": "ok"},
            headers=auth(member),
        )
        assert refused.status_code == 403
    assert db.get(Mission, mission["id"]).hard_budget_myr == Decimal("1500.00")

    approved = client.post(
        f"/approvals/{approval['id']}/decision",
        json={"decision": "approved", "reason": "Sponsor added budget"},
        headers=auth(people.hod),
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "executed"
    mission_row = db.get(Mission, mission["id"])
    db.refresh(mission_row)
    assert mission_row.hard_budget_myr == Decimal("1700.00")


def test_hod_can_create_and_confirm_in_one_step(client, people):
    response = client.post("/missions", json={**MISSION, "confirm_limits": True}, headers=auth(people.hod))
    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_member_cannot_self_confirm_on_create(client, people):
    response = client.post("/missions", json={**MISSION, "confirm_limits": True}, headers=auth(people.cm_a))
    assert response.status_code == 403


def test_target_above_hard_budget_is_rejected(client, people):
    response = client.post("/missions", json={**MISSION, "target_total_myr": 1600}, headers=auth(people.cm_a))
    assert response.status_code == 422


def test_limit_edits_before_confirmation_apply_directly(client, people):
    created = client.post("/missions", json=MISSION, headers=auth(people.cm_a)).json()
    response = client.patch(f"/missions/{created['id']}", json={"hard_budget_myr": 1600}, headers=auth(people.cm_a))
    assert response.status_code == 200
    assert response.json()["approval"] is None
    assert response.json()["mission"]["hard_budget_myr"] == 1600


def test_external_action_refused_before_hod_confirms(client, db, people):
    from tests.helpers import AGENT_HEADERS, enquiry_args, make_stakeholder

    created = client.post("/missions", json=MISSION, headers=auth(people.cm_a)).json()
    supplier = make_stakeholder(db)
    result = client.post(
        "/agent/tools/send_approved_message",
        json={"mission_id": created["id"], "args": enquiry_args(supplier)},
        headers=AGENT_HEADERS,
    ).json()
    assert result["status"] == "refused"
    assert "confirm" in result["reason"]
