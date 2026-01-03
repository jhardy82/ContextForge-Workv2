"""
Task entity - Domain model for tasks with validation.

Follows DDD patterns with immutable value objects and entity lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class TaskId:
    """Value object for Task identifier."""

    value: str

    def __post_init__(self) -> None:
        """Validate task ID format."""
        if not self.value:
            raise ValueError("TaskId cannot be empty")

    @classmethod
    def generate(cls) -> TaskId:
        """Generate a new unique TaskId."""
        return cls(value=f"T-{uuid4().hex[:8].upper()}")

    def __str__(self) -> str:
        return self.value


@dataclass
class Task:
    """
    Task domain entity.

    Represents a unit of work within a sprint or project.
    Follows ContextForge Work Codex principles.
    """

    id: TaskId
    title: str
    description: str = ""
    status: str = "todo"
    priority: int = 3  # 1=highest, 5=lowest
    estimated_hours: float | None = None
    actual_hours: float | None = None
    sprint_id: str | None = None
    project_id: str | None = None
    assignee: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    # Valid status transitions
    VALID_STATUSES = ("todo", "in_progress", "blocked", "completed", "cancelled")
    VALID_TRANSITIONS = {
        "todo": ("in_progress", "cancelled"),
        "in_progress": ("blocked", "completed", "todo", "cancelled"),
        "blocked": ("in_progress", "cancelled"),
        "completed": ("todo",),  # Allow reopening
        "cancelled": ("todo",),  # Allow resurrection
    }

    def __post_init__(self) -> None:
        """Validate task state."""
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")
        if not 1 <= self.priority <= 5:
            raise ValueError(f"Priority must be 1-5, got {self.priority}")

    @classmethod
    def create(
        cls,
        title: str,
        description: str = "",
        priority: int = 3,
        sprint_id: str | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Factory method to create a new task."""
        return cls(
            id=TaskId.generate(),
            title=title,
            description=description,
            priority=priority,
            sprint_id=sprint_id,
            project_id=project_id,
            tags=tags or [],
        )

    def start(self) -> Task:
        """Transition task to in_progress status."""
        return self._transition_to("in_progress")

    def complete(self, actual_hours: float | None = None) -> Task:
        """Mark task as completed."""
        task = self._transition_to("completed")
        task.completed_at = datetime.utcnow()
        if actual_hours is not None:
            task.actual_hours = actual_hours
        return task

    def block(self) -> Task:
        """Mark task as blocked."""
        return self._transition_to("blocked")

    def cancel(self) -> Task:
        """Cancel the task."""
        return self._transition_to("cancelled")

    def reopen(self) -> Task:
        """Reopen a completed or cancelled task."""
        task = self._transition_to("todo")
        task.completed_at = None
        return task

    def _transition_to(self, new_status: str) -> Task:
        """Validate and perform status transition."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        valid_next = self.VALID_TRANSITIONS.get(self.status, ())
        if new_status not in valid_next:
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'. "
                f"Valid transitions: {valid_next}"
            )

        self.status = new_status
        self.updated_at = datetime.utcnow()
        return self

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: int | None = None,
        estimated_hours: float | None = None,
        assignee: str | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Update task fields (immutable update pattern)."""
        if title is not None:
            if not title:
                raise ValueError("Task title cannot be empty")
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            if not 1 <= priority <= 5:
                raise ValueError(f"Priority must be 1-5, got {priority}")
            self.priority = priority
        if estimated_hours is not None:
            self.estimated_hours = estimated_hours
        if assignee is not None:
            self.assignee = assignee
        if tags is not None:
            self.tags = tags

        self.updated_at = datetime.utcnow()
        return self

    def log_hours(self, hours: float) -> Task:
        """Add actual hours worked."""
        if hours <= 0:
            raise ValueError("Hours must be positive")
        self.actual_hours = (self.actual_hours or 0) + hours
        self.updated_at = datetime.utcnow()
        return self

    @property
    def is_complete(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"

    @property
    def is_active(self) -> bool:
        """Check if task is in an active state."""
        return self.status in ("todo", "in_progress", "blocked")

    @property
    def velocity_ratio(self) -> float | None:
        """Calculate hours per estimated (for velocity tracking)."""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours / self.estimated_hours
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "sprint_id": self.sprint_id,
            "project_id": self.project_id,
            "assignee": self.assignee,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Create Task from dictionary."""
        task_id = TaskId(value=data["id"]) if isinstance(data.get("id"), str) else data.get("id")

        return cls(
            id=task_id,
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            priority=data.get("priority", 3),
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours"),
            sprint_id=data.get("sprint_id"),
            project_id=data.get("project_id"),
            assignee=data.get("assignee"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else datetime.utcnow(),
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
        )
