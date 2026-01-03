"""Task Domain Entity.

Defines the Task aggregate root for task management following DDD principles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Task:
    """Task domain entity representing a unit of work.

    This is the aggregate root for task management, encapsulating
    all task-related business logic and invariants.

    Attributes:
        id: Unique identifier for the task
        title: Task title/summary
        description: Detailed task description
        status: Current task status (todo, in_progress, done, blocked)
        priority: Task priority level (1-5, where 1 is highest)
        sprint_id: Optional associated sprint
        project_id: Optional associated project
        assignee: Optional person assigned to the task
        estimated_hours: Estimated hours to complete
        actual_hours: Actual hours spent
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        completed_at: Task completion timestamp
        tags: List of tags for categorization
    """

    title: str
    id: str = field(default_factory=lambda: f"TASK-{uuid4().hex[:8].upper()}")
    description: str | None = None
    status: str = "todo"
    priority: int = 3
    sprint_id: str | None = None
    project_id: str | None = None
    assignee: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate task invariants after initialization."""
        self._validate_status()
        self._validate_priority()

    def _validate_status(self) -> None:
        """Validate status is one of allowed values."""
        valid_statuses = {"todo", "in_progress", "done", "blocked", "cancelled"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

    def _validate_priority(self) -> None:
        """Validate priority is within allowed range."""
        if not 1 <= self.priority <= 5:
            raise ValueError(f"Priority must be between 1 and 5, got {self.priority}")

    def start(self) -> None:
        """Transition task to in_progress status."""
        if self.status == "done":
            raise ValueError("Cannot start a completed task")
        self.status = "in_progress"
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Transition task to done status."""
        self.status = "done"
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def block(self, reason: str | None = None) -> None:
        """Block the task.

        Args:
            reason: Optional reason for blocking
        """
        self.status = "blocked"
        if reason and self.description:
            self.description = f"{self.description}\n\nBlocked: {reason}"
        elif reason:
            self.description = f"Blocked: {reason}"
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """Unblock the task, returning to in_progress."""
        if self.status != "blocked":
            raise ValueError("Can only unblock a blocked task")
        self.status = "in_progress"
        self.updated_at = datetime.utcnow()

    def assign_to(self, assignee: str) -> None:
        """Assign task to a person.

        Args:
            assignee: Person to assign the task to
        """
        self.assignee = assignee
        self.updated_at = datetime.utcnow()

    def log_hours(self, hours: float) -> None:
        """Log hours worked on the task.

        Args:
            hours: Hours to add to actual_hours
        """
        if hours < 0:
            raise ValueError("Hours cannot be negative")
        if self.actual_hours is None:
            self.actual_hours = 0.0
        self.actual_hours += hours
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task.

        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "done"

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self.status == "blocked"

    @property
    def is_overdue(self) -> bool:
        """Check if task has exceeded estimated hours."""
        if self.estimated_hours is None or self.actual_hours is None:
            return False
        return self.actual_hours > self.estimated_hours

    def to_dict(self) -> dict:
        """Convert task to dictionary representation.

        Returns:
            Dictionary with all task attributes
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "sprint_id": self.sprint_id,
            "project_id": self.project_id,
            "assignee": self.assignee,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary.

        Args:
            data: Dictionary with task data

        Returns:
            Task instance
        """
        # Handle datetime fields
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.utcnow()

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        return cls(
            id=data.get("id", f"TASK-{uuid4().hex[:8].upper()}"),
            title=data["title"],
            description=data.get("description"),
            status=data.get("status", "todo"),
            priority=data.get("priority", 3),
            sprint_id=data.get("sprint_id"),
            project_id=data.get("project_id"),
            assignee=data.get("assignee"),
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours"),
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            tags=data.get("tags", []),
        )
