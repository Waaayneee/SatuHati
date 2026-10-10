from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NewBrief(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    goal: str = Field(min_length=1, max_length=2000)
    quantity: int = Field(gt=0, strict=True)
    budget_sen: int = Field(alias="budgetSen", gt=0, strict=True)
    target_sen: int = Field(alias="targetSen", gt=0, strict=True)
    deadline: date
    location: str = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def check_boundaries(self) -> Self:
        if self.target_sen > self.budget_sen:
            raise ValueError("Target must be within the hard budget")
        if not all(value.strip() for value in (self.title, self.goal, self.location)):
            raise ValueError("Brief fields must not be blank")
        return self


class VendorChoice(BaseModel):
    """Human API command, deliberately absent from the agent's MCP tools."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    case_id: str = Field(alias="caseId", min_length=1)
    vendor_id: str = Field(alias="vendorId", min_length=1)
    actor: Literal["organiser"]
