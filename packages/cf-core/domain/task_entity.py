"""
Task Domain Entity

Domain entity that wraps the Task model with business logic and validation rules.
Follows domain-driven design principles to encapsulate task-specific behavior.
"""

from datetime import UTC, datetime

from cf_core.models.action_item import ActionItem
from cf_core.models.task import Task, TaskStatus


class TaskEntity:
    """
    Domain entity for Task with business logic and state management.

    Wraps the Task Pydantic model to provide domain-specific behavior,
    validation rules, and state transition logic.
    """

    def __init__(self, task: Task):
        """
        Initialize TaskEntity from a Task model.

        Args:
            task: Task Pydantic model instance
        """
        self._task = task

    @classmethod
    def create(
        cls,
        task_id: str,
        title: str,
        status: TaskStatus = "new",
        priority: int | str = 3,
        description: str | None = None,
        # Legacy/Support fields
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        estimate_hours: float | None = None,
        story_points: int | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
        depends_on: list[str] | None = None,
        # New Phase 2 Fields (with defaults for backward compatibility)
        summary: str | None = None,
        owner: str | None = None,
        primary_project: str | None = None,
        primary_sprint: str | None = None,
        observability: dict | None = None,
    ) -> "TaskEntity":
        """
        Factory method to create a new TaskEntity.

        Args:
            task_id: Unique identifier for the task (T- prefix)
            title: Task title
            status: Initial status
            priority: Priority level
            description: Optional task description
            project_id: Legacy project ID (mapped to primary_project if missing)
            sprint_id: Legacy sprint ID (mapped to primary_sprint if missing)
            assignee: Legacy assignee (mapped to owner if missing)
            estimate_hours: Estimated hours
            story_points: Story point estimate
            due_date: Task due date
            tags: List of tags
            depends_on: dependencies
            summary: Brief summary (defaults to title if missing)
            owner: Primary owner (defaults to assignee or 'unassigned')
            primary_project: Primary project ID (defaults to 'P-DEFAULT')
            primary_sprint: Primary sprint ID (defaults to 'S-BACKLOG')
            observability: Observability data (optional)
        """
        # Handle defaults for required schema fields
        final_summary = summary if summary else title
        final_owner = owner if owner else (assignee if assignee else "unassigned")
        final_project = (
            primary_project if primary_project else (project_id if project_id else "P-DEFAULT")
        )
        final_sprint = (
            primary_sprint if primary_sprint else (sprint_id if sprint_id else "S-BACKLOG")
        )

        task = Task(
            id=task_id,
            title=title,
            summary=final_summary,
            description=description or "",
            status=status,
            priority=priority,
            owner=final_owner,
            primary_project=final_project,
            primary_sprint=final_sprint,
            # Legacy mapping handled by Task model sync_legacy_fields or explicit passing
            project_id=project_id,
            sprint_id=sprint_id,
            assignee=assignee,
            estimated_hours=estimate_hours,
            # Schema fields
            estimate_points=story_points,  # Map legacy to new
            due_at=due_date,  # Map legacy to new
            labels=tags or [],
            depends_on=depends_on or [],
            # Pass legacy values too for compatibility during migration validation
            story_points=story_points,
            due_date=due_date,
            tags=tags or [],
        )
        # If observability passed, model handles it (or we accept dict and Pydantic converts)
        if observability:
            # Pydantic v2 allows passing dict to model directly if type is Model
            # But Task model field is Observability type.
            # We might need to construct it if Pydantic doesn't auto-convert in this context?
            # Pydantic usually does coerce dict -> model.
            pass

        return cls(task)

    @property
    def task(self) -> Task:
        """Get the underlying Task model."""
        return self._task

    @property
    def id(self) -> str:
        """Get task ID."""
        return self._task.id

    @property
    def title(self) -> str:
        """Get task title."""
        return self._task.title

    @property
    def status(self) -> TaskStatus:
        """Get task status."""
        return self._task.status

    @property
    def priority(self) -> int:
        """Get task priority (int: 0=P0/highest, 9=lowest)."""
        return self._task.priority

    @property
    def priority_label(self) -> str:
        """Get human-readable priority label."""
        return self._task.priority_label

    @property
    def description(self) -> str | None:
        """Get task description."""
        return self._task.description

    @property
    def project_id(self) -> str | None:
        """Get associated project ID."""
        return self._task.project_id

    @property
    def sprint_id(self) -> str | None:
        """Get associated sprint ID."""
        return self._task.sprint_id

    @property
    def assignee(self) -> str | None:
        """Get assigned user/agent."""
        return self._task.assignee

    @property
    def blocked_reason(self) -> str | None:
        """Get blocked reason."""
        return self._task.blocked_reason

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._task.created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._task.updated_at

    @property
    def completed_at(self) -> datetime | None:
        """Get completion timestamp."""
        return self._task.completed_at

    @property
    def estimate_hours(self) -> float | None:
        """Get estimated hours."""
        return self._task.estimated_hours

    @property
    def actual_hours(self) -> float | None:
        """Get actual hours spent."""
        return self._task.actual_hours

    @property
    def tags(self) -> list[str]:
        """Get task tags."""
        return self._task.tags

    @property
    def depends_on(self) -> list[str]:
        """Get list of task IDs this task depends on."""
        return self._task.depends_on

    @property
    def action_items(self) -> list[ActionItem]:
        """Get action items/subtasks."""
        return self._task.action_items

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self._task.is_completed()

    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self._task.is_blocked()

    def is_active(self) -> bool:
        """Check if task is in progress."""
        return self._task.is_active()

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if transition to new_status is valid."""
        # Prevent transition to same status
        if self.status == new_status:
            return False

        # Define allowed transitions
        valid_transitions = {
            "new": ["ready", "in_progress", "dropped", "cancelled"],
            "ready": ["in_progress", "dropped", "cancelled", "new"],  # new allowed if moved back
            "in_progress": [
                "blocked",
                "review",
                "done",
                "dropped",
                "cancelled",
                "ready",
            ],  # ready/new allowed if stopped
            "blocked": ["in_progress", "dropped", "cancelled"],  # Unblock goes to in_progress
            "review": ["in_progress", "done", "dropped", "cancelled"],
            "done": ["in_progress", "new", "ready"],  # Reopen
            "dropped": ["new", "ready"],  # Restore
            "cancelled": ["new", "ready"],  # Restore
        }

        # If current status not in map, default to allow if strictly not same
        if self.status not in valid_transitions:
            return True

        allowed = valid_transitions.get(self.status, [])
        return new_status in allowed

    def start(self) -> "TaskEntity":
        """
        Transition task to in_progress status.

        Returns:
            TaskEntity: Updated entity with in_progress status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("in_progress"):
            raise ValueError(f"Cannot transition from {self.status} to in_progress")

        updated = self._task.model_copy(
            update={
                "status": "in_progress",
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def complete(self, actual_hours: float | None = None) -> "TaskEntity":
        """
        Transition task to done status.

        Args:
            actual_hours: Optional actual hours spent on task

        Returns:
            TaskEntity: Updated entity with done status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("done"):
            raise ValueError(f"Cannot transition from {self.status} to done")

        now = datetime.now(UTC)
        update_data = {
            "status": "done",
            "updated_at": now,
            "completed_at": now,
        }
        if actual_hours is not None:
            update_data["actual_hours"] = actual_hours

        updated = self._task.model_copy(update=update_data)
        return TaskEntity(updated)

    def block(self, reason: str) -> "TaskEntity":
        """
        Transition task to blocked status with reason.

        Args:
            reason: Reason for blocking

        Returns:
            TaskEntity: Updated entity with blocked status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("blocked"):
            raise ValueError(f"Cannot transition from {self.status} to blocked")

        updated = self._task.model_copy(
            update={
                "status": "blocked",
                "blocked_reason": reason,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def unblock(self) -> "TaskEntity":
        """
        Transition task from blocked to in_progress status.

        Returns:
            TaskEntity: Updated entity with in_progress status

        Raises:
            ValueError: If task is not blocked
        """
        if self.status != "blocked":
            raise ValueError("Can only unblock a blocked task")

        updated = self._task.model_copy(
            update={
                "status": "in_progress",
                "blocked_reason": None,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def cancel(self) -> "TaskEntity":
        """
        Cancel the task.

        Returns:
            TaskEntity: Updated entity with cancelled status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("cancelled"):
            raise ValueError(f"Cannot transition from {self.status} to cancelled")

        updated = self._task.model_copy(
            update={
                "status": "cancelled",
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def assign_to(self, assignee: str) -> "TaskEntity":
        """
        Assign task to a user/agent.

        Args:
            assignee: User/agent to assign

        Returns:
            TaskEntity: Updated entity with assignee
        """
        updated = self._task.model_copy(
            update={
                "assignee": assignee,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def move_to_sprint(self, sprint_id: str) -> "TaskEntity":
        """
        Move task to a sprint.

        Args:
            sprint_id: Sprint ID to move to

        Returns:
            TaskEntity: Updated entity with sprint_id
        """
        updated = self._task.model_copy(
            update={
                "sprint_id": sprint_id,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def update_estimate(self, hours: float) -> "TaskEntity":
        """
        Update estimated hours.

        Args:
            hours: New estimated hours

        Returns:
            TaskEntity: Updated entity with new estimate
        """
        updated = self._task.model_copy(
            update={
                "estimated_hours": hours,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def log_hours(self, hours: float) -> "TaskEntity":
        """
        Add hours to actual_hours.

        Args:
            hours: Hours to add

        Returns:
            TaskEntity: Updated entity with updated actual_hours
        """
        current = self.actual_hours or 0.0
        updated = self._task.model_copy(
            update={
                "actual_hours": current + hours,
                "updated_at": datetime.now(UTC),
            }
        )
        return TaskEntity(updated)

    def update(self, **kwargs) -> "TaskEntity":
        """
        Update multiple task fields at once.

        Accepts any valid Task model fields as keyword arguments.
        Automatically updates the updated_at timestamp.

        Args:
            **kwargs: Fields to update (title, description, priority, status, etc.)

        Returns:
            TaskEntity: Updated entity with new field values

        Example:
            updated = task.update(title="New Title", priority="high", status="in_progress")
        """
        if not kwargs:
            return self

        # Always update the timestamp
        kwargs["updated_at"] = datetime.now(UTC)

        updated = self._task.model_copy(update=kwargs)
        return TaskEntity(updated)

    def add_tag(self, tag: str) -> "TaskEntity":
        """
        Add a tag to the task.

        Args:
            tag: Tag to add

        Returns:
            TaskEntity: Updated entity with new tag
        """
        if tag not in self.tags:
            new_tags = self.tags + [tag]
            updated = self._task.model_copy(
                update={
                    "tags": new_tags,
                    "updated_at": datetime.now(UTC),
                }
            )
            return TaskEntity(updated)
        return self

    def remove_tag(self, tag: str) -> "TaskEntity":
        """
        Remove a tag from the task.

        Args:
            tag: Tag to remove

        Returns:
            TaskEntity: Updated entity without the tag
        """
        if tag in self.tags:
            new_tags = [t for t in self.tags if t != tag]
            updated = self._task.model_copy(
                update={
                    "tags": new_tags,
                    "updated_at": datetime.now(UTC),
                }
            )
            return TaskEntity(updated)
        return self

    def add_dependency(self, task_id: str) -> "TaskEntity":
        """
        Add a dependency on another task.

        Args:
            task_id: Task ID to depend on

        Returns:
            TaskEntity: Updated entity with new dependency
        """
        if task_id not in self.depends_on:
            new_deps = self.depends_on + [task_id]
            updated = self._task.model_copy(
                update={
                    "depends_on": new_deps,
                    "updated_at": datetime.now(UTC),
                }
            )
            return TaskEntity(updated)
        return self

    def remove_dependency(self, task_id: str) -> "TaskEntity":
        """
        Remove a dependency on another task.

        Args:
            task_id: Task ID to remove dependency from

        Returns:
            TaskEntity: Updated entity without the dependency
        """
        if task_id in self.depends_on:
            new_deps = [t for t in self.depends_on if t != task_id]
            updated = self._task.model_copy(
                update={
                    "depends_on": new_deps,
                    "updated_at": datetime.now(UTC),
                }
            )
            return TaskEntity(updated)
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return self._task.model_dump()

    def __eq__(self, other: object) -> bool:
        """Check equality by task ID."""
        if isinstance(other, TaskEntity):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Hash by task ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskEntity(id={self.id}, title='{self.title}', status={self.status})"
