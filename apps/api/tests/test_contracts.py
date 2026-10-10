import pytest
from pydantic import ValidationError

from kawteam.schemas.domain import NewBrief, VendorChoice


def test_brief_preserves_integer_sen_and_rejects_unknown_dates():
    values = {
        "title": "Totes",
        "goal": "300 printed totes",
        "quantity": 300,
        "budgetSen": 150000,
        "targetSen": 135000,
        "deadline": "2026-10-25",
        "location": "Subang Jaya",
    }
    assert NewBrief(**values).budget_sen == 150000
    with pytest.raises(ValidationError):
        NewBrief(**(values | {"deadline": "2026-99-99"}))
    with pytest.raises(ValidationError):
        NewBrief(**(values | {"targetSen": 150001}))


def test_final_choice_command_requires_human_organiser():
    with pytest.raises(ValidationError):
        VendorChoice(caseId="case-totes", vendorId="willow", actor="agent")
