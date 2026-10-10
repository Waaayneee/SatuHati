import pytest


def test_malformed_provider_briefs_and_citations_cannot_trigger_actions():
    from kawteam.providers import validate_answer

    for brief in ["bad brief", {"budgetSen": "1000"}, {"quantity": -1}]:
        with pytest.raises(ValueError):
            validate_answer({"reply": "Researching", "action": "find_vendors", "brief": brief}, [])
    with pytest.raises(ValueError):
        validate_answer({"reply": "Hello", "action": "none", "citations": "invented"}, [])
    result = validate_answer(
        {"reply": "Hello", "action": "none", "citations": ["real", "fake"]},
        [{"documentId": "real"}],
    )
    assert result["citations"] == ["real"]


def test_explicit_unknown_scope_remains_unknown_instead_of_inheriting_another_quantity():
    from kawteam.providers import validate_answer

    result = validate_answer(
        {
            "reply": "How many catering portions?",
            "action": "find_vendors",
            "brief": {"quantity": None, "budgetSen": 100000},
        },
        [],
    )
    assert "quantity" in result["brief"]
    assert result["brief"]["quantity"] is None
