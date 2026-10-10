import copy
import json
from pathlib import Path

import pytest


def case():
    return json.loads(
        (Path(__file__).parents[1] / "src/kawteam/seed.json").read_text(encoding="utf-8")
    )["cases"][0]


def test_observer_cannot_mutate_and_teammate_cannot_choose():
    from kawteam.workflow import transition

    with pytest.raises(PermissionError):
        transition(case(), "observer", {"type": "research"})
    with pytest.raises(PermissionError):
        transition(case(), "teammate", {"type": "choose", "vendorId": "willow"})


def test_edit_invalidates_exact_payload_approval():
    from kawteam.workflow import transition

    approved = transition(case(), "organiser", {"type": "approve"})
    edited = transition(approved, "teammate", {"type": "edit-draft", "body": "Different terms"})
    assert edited["draft"]["status"] == "pending"
    with pytest.raises(ValueError, match="approval"):
        transition(edited, "organiser", {"type": "send"})


def test_send_is_consumed_once_and_reply_does_not_select_vendor():
    from kawteam.workflow import transition

    approved = transition(case(), "organiser", {"type": "approve"})
    sent = transition(approved, "organiser", {"type": "send"})
    with pytest.raises(ValueError, match="already"):
        transition(sent, "organiser", {"type": "send"})
    replied = transition(sent, "teammate", {"type": "sync"})
    assert replied["selectedVendorId"] is None
    assert replied["messages"][-1]["direction"] == "received"


def test_research_is_scoped_to_fixture_and_does_not_auto_choose():
    from kawteam.workflow import transition

    c = case()
    c["id"] = "new-case"
    with pytest.raises(ValueError, match="Live search"):
        transition(c, "organiser", {"type": "research"})
    assert transition(case(), "teammate", {"type": "research"})["selectedVendorId"] is None


def test_report_suppresses_savings_for_scope_mismatch_and_unknown_shipping():
    from kawteam.workflow import outcome

    c = case()
    report = outcome(c)
    assert report["recommendedVendorId"] == "willow"
    assert report["potentialSavingsSen"] == 35000
    c["quantity"] = 50
    assert outcome(c)["potentialSavingsSen"] is None
    c = case()
    c["vendors"][2]["deliverySen"] = None
    assert outcome(c)["recommendedVendorId"] is None


def test_expired_approval_and_forged_payload_cannot_send():
    from kawteam.workflow import transition

    c = transition(case(), "organiser", {"type": "approve"})
    expired = copy.deepcopy(c)
    expired["draft"]["approvedUntil"] = 0
    with pytest.raises(ValueError, match="approval"):
        transition(expired, "organiser", {"type": "send"})
    c["draft"]["recipient"] = "another vendor"
    with pytest.raises(ValueError, match="approval"):
        transition(c, "organiser", {"type": "send"})


def test_signed_session_rejects_tampering_expiry_and_wrong_workspace():
    from kawteam.auth import issue_session, verify_session

    token = issue_session("organiser", "workspace-a", "secret" * 8, now=100)
    assert verify_session(token, "workspace-a", "secret" * 8, now=101) == "organiser"
    with pytest.raises(ValueError):
        verify_session(token + "x", "workspace-a", "secret" * 8, now=101)
    with pytest.raises(ValueError):
        verify_session(token, "workspace-b", "secret" * 8, now=101)
    with pytest.raises(ValueError):
        verify_session(token, "workspace-a", "secret" * 8, now=100000)
