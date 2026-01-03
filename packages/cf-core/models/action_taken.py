"""
Action Taken Model

Audit trail entry for tasks.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ActionTaken(BaseModel):
    """
    Record of an action taken on a task.

    Provides audit trail of who did what and when.
    """

    model_config = {"extra": "forbid"}

    when: datetime = Field(description="When action occurred")
    actor: str = Field(description="Who performed the action")
    action: str = Field(description="What was done")
    artifacts: list[str] = Field(
        default_factory=list,
        description="Related artifacts (paths/URLs)"
    )
