"""
Risk Entry Models

Risk tracking for tasks, sprints, and projects.
"""

from typing import Literal

from pydantic import BaseModel, Field


class RiskEntrySimple(BaseModel):
    """
    Simple risk entry (for tasks and sprints).

    Lightweight risk tracking without owner/ID.
    """

    model_config = {"extra": "forbid"}

    description: str = Field(description="Risk description")
    impact: Literal["low", "med", "high"] = Field(description="Impact if risk occurs")
    likelihood: Literal["low", "med", "high"] = Field(description="Likelihood of occurrence")
    mitigation: str = Field(description="Mitigation strategy")


class RiskEntryExtended(BaseModel):
    """
    Extended risk entry (for projects).

    Full risk tracking with ownership and identification.
    """

    model_config = {"extra": "forbid"}

    id: str = Field(description="Risk ID")
    description: str = Field(description="Risk description")
    impact: Literal["low", "med", "high"] = Field(description="Impact if risk occurs")
    likelihood: Literal["low", "med", "high"] = Field(description="Likelihood of occurrence")
    owner: str = Field(description="Risk owner")
    mitigation: str = Field(description="Mitigation strategy")
