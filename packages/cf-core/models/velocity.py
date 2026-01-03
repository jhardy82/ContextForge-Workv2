"""Velocity domain model for cf_core.

Provides a Pydantic v2 model for Velocity tracking with:
- Story points and hours tracking
- Sprint/task associations
- Velocity calculations
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VelocityMetric(BaseModel):
    """Domain model for Velocity metrics.

    Attributes:
        id: Unique velocity record identifier
        sprint_id: Associated sprint ID
        task_id: Associated task ID (if task-level)
        story_points: Story points completed
        actual_hours: Actual hours spent
        estimated_hours: Estimated hours
        recorded_at: When the metric was recorded
        notes: Optional notes
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., min_length=1)
    sprint_id: str | None = Field(default=None)
    task_id: str | None = Field(default=None)
    story_points: float = Field(default=0.0, ge=0)
    actual_hours: float = Field(default=0.0, ge=0)
    estimated_hours: float = Field(default=0.0, ge=0)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = Field(default="")

    def hours_per_point(self) -> float | None:
        """Calculate hours per story point."""
        if self.story_points == 0:
            return None
        return self.actual_hours / self.story_points

    def estimation_accuracy(self) -> float | None:
        """Calculate estimation accuracy percentage."""
        if self.estimated_hours == 0:
            return None
        return (self.actual_hours / self.estimated_hours) * 100


__all__ = ["VelocityMetric"]
