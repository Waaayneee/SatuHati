import pytest


def test_event_mentions_select_saved_memory_without_cross_event_leakage():
    from kawteam.memory import resolve_event, retrieve

    events = [{"id": "tech", "name": "Tech Night"}, {"id": "food", "name": "Food Festival"}]
    assert resolve_event("Find vendors for Tech Night", events, None)["id"] == "tech"
    docs = [
        {
            "id": "a",
            "eventId": "tech",
            "name": "proposal.txt",
            "text": "Budget RM1500. Need 300 tote bags.",
        },
        {
            "id": "b",
            "eventId": "food",
            "name": "private.txt",
            "text": "Secret catering budget RM9999.",
        },
    ]
    context = retrieve("tech", "budget", docs)
    assert len(context) == 1
    assert "RM1500" in context[0]["excerpt"]
    assert "RM9999" not in str(context)


def test_upload_parser_extracts_text_and_rejects_unsupported_files():
    from kawteam.memory import extract_text

    assert "RM1000" in extract_text("budget.txt", b"Event budget RM1000")
    with pytest.raises(ValueError):
        extract_text("program.exe", b"fake")
    with pytest.raises(ValueError):
        extract_text("empty.txt", b"")


def test_chat_budget_overrides_memory_and_never_guesses_missing_deadline():
    from kawteam.memory import intake

    event = {
        "id": "tech",
        "name": "Tech Night",
        "facts": {
            "budgetSen": 150000,
            "quantity": 300,
            "deadline": "2026-10-25",
            "location": "Subang Jaya",
        },
    }
    b = intake("Find tote vendors with a budget of RM1000", event)
    assert b["budgetSen"] == 100000
    assert b["quantity"] == 300
    assert b["eventId"] == "tech"
    event["facts"].pop("deadline")
    assert intake("Find vendors for my event", event)["deadline"] is None


def test_memory_prefers_labelled_budget_and_delivery_over_deposit_and_creation_date():
    from kawteam.memory import facts_from_text

    facts = facts_from_text(
        "Proposal created: 2026-10-10\nPrinting deposit RM200\nTotal budget: RM1000\nDelivery deadline: 2026-10-25"
    )
    assert facts["budgetSen"] == 100000
    assert facts["deadline"] == "2026-10-25"
    assert facts_from_text("Deposit RM200. Fee RM300. Created 2026-10-10") == {}


def test_budget_can_be_overridden_in_natural_chat_without_repeating_saved_details():
    from kawteam.memory import facts_from_text

    assert facts_from_text("Find vendors within RM1000")["budgetSen"] == 100000
    assert facts_from_text("I have a budget of 1000rm")["budgetSen"] == 100000


def test_event_names_match_words_and_longest_name_without_wrong_context():
    from kawteam.memory import resolve_event

    events = [{"id": "short", "name": "Tech"}, {"id": "night", "name": "Tech Night"}]
    assert resolve_event("Find vendors for Tech Night", events, "short")["id"] == "night"
    assert resolve_event("A technical question", events, "night")["id"] == "night"
