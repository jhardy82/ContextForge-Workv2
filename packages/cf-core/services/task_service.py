"""Task service for cf_core.

Provides business logic for task operations using cf_core models.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast

from cf_core.models import Task

if TYPE_CHECKING:
    from cf_core.database import DatabaseConnection


class TaskService:
    """Service for task business logic operations.

    Attributes:
        db: Database connection instance
    """

    def __init__(self, db: DatabaseConnection | None = None) -> None:
        """Initialize task service.

        Args:
            db: Optional database connection. If None, operates in-memory.
        """
        self.db = db
        self._tasks: dict[str, Task] = {}

    def create_task(
        self,
        title: str,
        summary: str | None = None,
        description: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        priority: str = "medium",
        assignee: str | None = None,
        estimate_hours: float | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title (required)
            summary: Brief summary (defaults to title if not provided)
            description: Optional description
            project_id: Associated project ID
            sprint_id: Associated sprint ID
            priority: Priority level (low, medium, high, critical)
            assignee: Assigned user
            estimate_hours: Estimated hours to complete
            tags: List of tags

        Returns:
            Created Task instance
        """
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            title=title,
            summary=summary or title,
            description=description,
            project_id=project_id,
            sprint_id=sprint_id,
            priority=priority,  # Now accepts int directly
            assignee=assignee,
            estimated_hours=estimate_hours,
            tags=tags or [],
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def update_task(self, task_id: str, **updates) -> Task | None:
        """Update a task.

        Args:
            task_id: Task identifier
            **updates: Fields to update

        Returns:
            Updated Task if found, None otherwise
        """
        task = self._tasks.get(task_id)
        if not task:
            return None

        # Create updated task with new values
        task_dict = task.model_dump()
        # Map estimate_hours to estimated_hours if present
        if "estimate_hours" in updates:
            updates["estimated_hours"] = updates.pop("estimate_hours")
        task_dict.update(updates)
        task_dict["updated_at"] = datetime.utcnow()

        updated_task = Task(**task_dict)
        self._tasks[task_id] = updated_task
        return updated_task

    def list_tasks(
        self,
        status: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
    ) -> list[Task]:
        """List tasks with optional filtering.

        Args:
            status: Filter by status
            project_id: Filter by project
            sprint_id: Filter by sprint
            assignee: Filter by assignee

        Returns:
            List of matching tasks
        """
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]
        if project_id:
            tasks = [t for t in tasks if t.project_id == project_id]
        if sprint_id:
            tasks = [t for t in tasks if t.sprint_id == sprint_id]
        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]

        return tasks

    def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def complete_task(self, task_id: str, actual_hours: float | None = None) -> Task | None:
        """Mark a task as completed.

        Args:
            task_id: Task identifier
            actual_hours: Actual hours spent

        Returns:
            Updated Task if found, None otherwise
        """
        return self.update_task(
            task_id,
            status="completed",
            completed_at=datetime.utcnow(),
            actual_hours=actual_hours,
        )

    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        import uuid
        return f"T-{uuid.uuid4().hex[:8].upper()}"


__all__ = ["TaskService"]
