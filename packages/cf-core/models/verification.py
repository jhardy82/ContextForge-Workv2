"""
Verification Model

MPV (Multi-Point Verification) evidence tracking.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MPVPlanItem(BaseModel):
    """MPV plan entry."""

    model_config = {"extra": "forbid"}

    anchor: str = Field(description="What is being verified")
    method: str = Field(description="How it will be verified")
    success_criteria: str = Field(description="What constitutes success")


class MPVEvidenceItem(BaseModel):
    """MPV evidence entry."""

    model_config = {"extra": "forbid"}

    anchor: str = Field(description="What was verified")
    when: datetime = Field(description="When verification occurred")
    artifact: str = Field(description="Evidence artifact (path/URL)")
    result: Literal["pass", "fail"] = Field(description="Verification result")
    notes: str | None = Field(default=None, description="Additional notes")


class Verification(BaseModel):
    """
    Multi-Point Verification tracking for tasks.

    Provides evidence-based verification plans and results.
    """

    model_config = {"extra": "forbid"}

    mpv_plan: list[MPVPlanItem] = Field(
        default_factory=list,
        description="Verification plan items"
    )
    mpv_evidence: list[MPVEvidenceItem] = Field(
        default_factory=list,
        description="Verification evidence collected"
    )
