"""
Blocker Entry Model

Structured blocker tracking for tasks.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class BlockerEntry(BaseModel):
    """
    Structured blocker information.

    Used in Task.blockers array to track what's blocking progress.
    """

    model_config = {"extra": "forbid"}

    id: str = Field(description="Blocker ID")
    description: str = Field(description="What is blocking the task")
    owner: str = Field(description="Who owns resolving this blocker")
    since: datetime = Field(description="When blocker was identified")
    eta: datetime | None = Field(default=None, description="Expected resolution date")
