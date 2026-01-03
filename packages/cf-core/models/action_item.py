"""ActionItem domain model for cf_core.

Provides a rich Pydantic v2 model for ActionItem entities with:
- Status lifecycle (pending, in_progress, completed, skipped)
- Priority levels (low, medium, high, critical)
- Parent hierarchy tracking (project, sprint, or task)
- Ownership and assignment
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ActionItemStatus = Literal["pending", "in_progress", "completed", "skipped", "blocked"]
ActionItemPriority = Literal["low", "medium", "high", "critical"]


class ActionItem(BaseModel):
    """Domain model for ActionItem entities.

    ActionItems are discrete, actionable items within a parent context
    (Project, Sprint, or Task). They represent specific work items,
    checklist entries, or sub-tasks.

    Attributes:
        id: Unique action item identifier (A- prefix, hierarchical)
        title: Action item title/description
        status: Current action item status
        priority: Action item priority level
        parent_type: Type of parent entity ('project', 'sprint', 'task')
        parent_id: ID of the parent entity
        assignee: Assigned user/agent
        due_date: Optional due date
        notes: Additional notes or context
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
        order: Sort order within parent (for display)
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., pattern=r"^A-[a-zA-Z0-9_-]+$")
    title: str = Field(..., min_length=1, max_length=500)
    status: ActionItemStatus = Field(default="pending")
    priority: ActionItemPriority = Field(default="medium")
    parent_type: Literal["project", "sprint", "task"] = Field(...)
    parent_id: str = Field(...)
    assignee: str | None = Field(default=None)
    due_date: datetime | None = Field(default=None)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
    order: int = Field(default=0, ge=0)

    def is_completed(self) -> bool:
        """Check if action item is completed."""
        return self.status == "completed"

    def is_pending(self) -> bool:
        """Check if action item is pending."""
        return self.status == "pending"

    def is_active(self) -> bool:
        """Check if action item is in progress."""
        return self.status == "in_progress"

    def is_blocked(self) -> bool:
        """Check if action item is blocked."""
        return self.status == "blocked"

    def complete(self) -> ActionItem:
        """Mark action item as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return self

    def skip(self) -> ActionItem:
        """Mark action item as skipped."""
        self.status = "skipped"
        self.updated_at = datetime.utcnow()
        return self


__all__ = ["ActionItem", "ActionItemStatus", "ActionItemPriority"]
