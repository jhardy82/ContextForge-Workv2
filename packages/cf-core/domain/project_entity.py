"""
Project Domain Entity

Domain entity that wraps the Project model with business logic and validation rules.
Follows domain-driven design principles to encapsulate project-specific behavior.
"""

from datetime import UTC, datetime

from cf_core.models.action_item import ActionItem
from cf_core.models.observability import Observability
from cf_core.models.project import Project, ProjectStatus


class ProjectEntity:
    """
    Domain entity for Project with business logic and state management.

    Wraps the Project Pydantic model to provide domain-specific behavior,
    validation rules, and state transition logic.
    """

    def __init__(self, project: Project):
        """
        Initialize ProjectEntity from a Project model.

        Args:
            project: Project Pydantic model instance
        """
        self._project = project

    @classmethod
    def create(
        cls,
        project_id: str,
        name: str,
        status: ProjectStatus = "new",
        description: str | None = None,
        owner: str | None = None,
        start_date: datetime | None = None,
        target_end_date: datetime | None = None,
        tags: list[str] | None = None,
        team_members: list[str] | None = None,
        mission: str | None = None,
        vision: str | None = None,
        observability: dict | None = None,
    ) -> "ProjectEntity":
        """
        Factory method to create a new ProjectEntity.

        Args:
            project_id: Unique identifier for the project (P- prefix)
            name: Project name
            status: Initial status (default: "new")
            description: Optional project description
            owner: Project owner/lead
            start_date: Project start date
            target_end_date: Target completion date
            tags: List of tags
            team_members: List of team member identifiers
            mission: Project mission
            vision: Project vision
            observability: Observability configuration

        Returns:
            ProjectEntity: New project entity instance
        """
        project = Project(
            id=project_id,
            name=name,
            status=status,
            description=description or "",
            owner=owner,
            start_date=start_date,
            target_end_date=target_end_date,
            tags=tags or [],
            team_members=team_members or [],
            mission=mission,
            vision=vision,
            observability=observability or Observability.create_healthy(),
        )
        return cls(project)

    @property
    def project(self) -> Project:
        """Get the underlying Project model."""
        return self._project

    @property
    def id(self) -> str:
        """Get project ID."""
        return self._project.id

    @property
    def name(self) -> str:
        """Get project name."""
        return self._project.name

    @property
    def status(self) -> ProjectStatus:
        """Get project status."""
        return self._project.status

    @property
    def description(self) -> str | None:
        """Get project description."""
        return self._project.description

    @property
    def owner(self) -> str | None:
        """Get project owner."""
        return self._project.owner

    @property
    def mission(self) -> str | None:
        """Get project mission."""
        return self._project.mission

    @property
    def vision(self) -> str | None:
        """Get project vision."""
        return self._project.vision

    @property
    def observability(self) -> Observability:
        """Get observability configuration."""
        return self._project.observability

    @property
    def start_date(self) -> datetime | None:
        """Get project start date."""
        return self._project.start_date

    @property
    def target_end_date(self) -> datetime | None:
        """Get target end date."""
        return self._project.target_end_date

    @property
    def actual_end_date(self) -> datetime | None:
        """Get actual end date."""
        return self._project.actual_end_date

    @property
    def pending_reason(self) -> str | None:
        """Get pending reason."""
        return self._project.pending_reason

    @property
    def blocked_reason(self) -> str | None:
        """Get blocked reason."""
        return self._project.blocked_reason

    @property
    def sprint_ids(self) -> list[str]:
        """Get list of sprint IDs."""
        return self._project.sprint_ids

    @property
    def task_ids(self) -> list[str]:
        """Get list of task IDs."""
        return self._project.task_ids

    @property
    def action_items(self) -> list[ActionItem]:
        """Get action items."""
        return self._project.action_items

    @property
    def team_members(self) -> list[str]:
        """Get team members."""
        return self._project.team_members

    @property
    def tags(self) -> list[str]:
        """Get project tags."""
        return self._project.tags

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._project.created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._project.updated_at

    def is_active(self) -> bool:
        """Check if project is active or in progress."""
        return self._project.is_active()

    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self._project.is_completed()

    def is_on_hold(self) -> bool:
        """Check if project is on hold (pending or blocked)."""
        return self._project.is_on_hold()

    def can_transition_to(self, new_status: ProjectStatus) -> bool:
        """Check if transition to new_status is valid."""
        return self._project.can_transition_to(new_status)

    def activate(self, owner: str) -> "ProjectEntity":
        """
        Transition project to active status.

        Args:
            owner: Project owner/lead

        Returns:
            ProjectEntity: Updated entity with active status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("active"):
            raise ValueError(f"Cannot transition from {self.status} to active")

        updated = self._project.model_copy(
            update={
                "status": "active",
                "owner": owner,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def start_work(self) -> "ProjectEntity":
        """
        Transition project to in_progress status.

        Returns:
            ProjectEntity: Updated entity with in_progress status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("in_progress"):
            raise ValueError(f"Cannot transition from {self.status} to in_progress")

        updated = self._project.model_copy(
            update={
                "status": "in_progress",
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def complete(self, actual_end_date: datetime | None = None) -> "ProjectEntity":
        """
        Transition project to completed status.

        Args:
            actual_end_date: Actual completion date (defaults to now)

        Returns:
            ProjectEntity: Updated entity with completed status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("completed"):
            raise ValueError(f"Cannot transition from {self.status} to completed")

        end_date = actual_end_date or datetime.now(UTC)
        updated = self._project.model_copy(
            update={
                "status": "completed",
                "actual_end_date": end_date,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def block(self, reason: str) -> "ProjectEntity":
        """
        Transition project to blocked status with reason.

        Args:
            reason: Reason for blocking

        Returns:
            ProjectEntity: Updated entity with blocked status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("blocked"):
            raise ValueError(f"Cannot transition from {self.status} to blocked")

        updated = self._project.model_copy(
            update={
                "status": "blocked",
                "blocked_reason": reason,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def unblock(self) -> "ProjectEntity":
        """
        Transition project from blocked to active status.

        Returns:
            ProjectEntity: Updated entity with active status

        Raises:
            ValueError: If project is not blocked
        """
        if self.status != "blocked":
            raise ValueError("Can only unblock a blocked project")

        updated = self._project.model_copy(
            update={
                "status": "active",
                "blocked_reason": None,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def put_on_hold(self, reason: str) -> "ProjectEntity":
        """
        Transition project to pending status with reason.

        Args:
            reason: Reason for putting on hold

        Returns:
            ProjectEntity: Updated entity with pending status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("pending"):
            raise ValueError(f"Cannot transition from {self.status} to pending")

        updated = self._project.model_copy(
            update={
                "status": "pending",
                "pending_reason": reason,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def resume(self) -> "ProjectEntity":
        """
        Resume project from pending status.

        Returns:
            ProjectEntity: Updated entity with active status

        Raises:
            ValueError: If project is not pending
        """
        if self.status != "pending":
            raise ValueError("Can only resume a pending project")

        updated = self._project.model_copy(
            update={
                "status": "active",
                "pending_reason": None,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def cancel(self) -> "ProjectEntity":
        """
        Cancel the project.

        Returns:
            ProjectEntity: Updated entity with cancelled status

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to("cancelled"):
            raise ValueError(f"Cannot transition from {self.status} to cancelled")

        updated = self._project.model_copy(
            update={
                "status": "cancelled",
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def assign_owner(self, owner: str) -> "ProjectEntity":
        """
        Assign project owner.

        Args:
            owner: Owner identifier

        Returns:
            ProjectEntity: Updated entity with owner
        """
        updated = self._project.model_copy(
            update={
                "owner": owner,
                "updated_at": datetime.now(UTC),
            }
        )
        return ProjectEntity(updated)

    def add_sprint(self, sprint_id: str) -> "ProjectEntity":
        """
        Add a sprint to the project.

        Args:
            sprint_id: Sprint ID to add

        Returns:
            ProjectEntity: Updated entity with sprint added
        """
        if sprint_id not in self.sprint_ids:
            new_sprints = self.sprint_ids + [sprint_id]
            updated = self._project.model_copy(
                update={
                    "sprint_ids": new_sprints,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def remove_sprint(self, sprint_id: str) -> "ProjectEntity":
        """
        Remove a sprint from the project.

        Args:
            sprint_id: Sprint ID to remove

        Returns:
            ProjectEntity: Updated entity with sprint removed
        """
        if sprint_id in self.sprint_ids:
            new_sprints = [s for s in self.sprint_ids if s != sprint_id]
            updated = self._project.model_copy(
                update={
                    "sprint_ids": new_sprints,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def add_task(self, task_id: str) -> "ProjectEntity":
        """
        Add a task to the project.

        Args:
            task_id: Task ID to add

        Returns:
            ProjectEntity: Updated entity with task added
        """
        if task_id not in self.task_ids:
            new_tasks = self.task_ids + [task_id]
            updated = self._project.model_copy(
                update={
                    "task_ids": new_tasks,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def remove_task(self, task_id: str) -> "ProjectEntity":
        """
        Remove a task from the project.

        Args:
            task_id: Task ID to remove

        Returns:
            ProjectEntity: Updated entity with task removed
        """
        if task_id in self.task_ids:
            new_tasks = [t for t in self.task_ids if t != task_id]
            updated = self._project.model_copy(
                update={
                    "task_ids": new_tasks,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def add_team_member(self, member: str) -> "ProjectEntity":
        """
        Add a team member to the project.

        Args:
            member: Team member identifier

        Returns:
            ProjectEntity: Updated entity with team member added
        """
        if member not in self.team_members:
            new_members = self.team_members + [member]
            updated = self._project.model_copy(
                update={
                    "team_members": new_members,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def remove_team_member(self, member: str) -> "ProjectEntity":
        """
        Remove a team member from the project.

        Args:
            member: Team member identifier

        Returns:
            ProjectEntity: Updated entity with team member removed
        """
        if member in self.team_members:
            new_members = [m for m in self.team_members if m != member]
            updated = self._project.model_copy(
                update={
                    "team_members": new_members,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def add_tag(self, tag: str) -> "ProjectEntity":
        """
        Add a tag to the project.

        Args:
            tag: Tag to add

        Returns:
            ProjectEntity: Updated entity with new tag
        """
        if tag not in self.tags:
            new_tags = self.tags + [tag]
            updated = self._project.model_copy(
                update={
                    "tags": new_tags,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def remove_tag(self, tag: str) -> "ProjectEntity":
        """
        Remove a tag from the project.

        Args:
            tag: Tag to remove

        Returns:
            ProjectEntity: Updated entity without the tag
        """
        if tag in self.tags:
            new_tags = [t for t in self.tags if t != tag]
            updated = self._project.model_copy(
                update={
                    "tags": new_tags,
                    "updated_at": datetime.now(UTC),
                }
            )
            return ProjectEntity(updated)
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return self._project.model_dump()

    def update(self, **kwargs) -> "ProjectEntity":
        """
        Update multiple project fields at once.

        Accepts any valid Project model fields as keyword arguments.
        Automatically updates the updated_at timestamp.

        Args:
            **kwargs: Fields to update (name, description, status, owner, etc.)

        Returns:
            ProjectEntity: Updated entity with new field values

        Example:
            updated = project.update(name="New Name", description="New desc")
        """
        if not kwargs:
            return self

        # Always update the timestamp
        kwargs["updated_at"] = datetime.now(UTC)

        updated = self._project.model_copy(update=kwargs)
        return ProjectEntity(updated)

    def __eq__(self, other: object) -> bool:
        """Check equality by project ID."""
        if isinstance(other, ProjectEntity):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Hash by project ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"ProjectEntity(id={self.id}, name='{self.name}', status={self.status})"
