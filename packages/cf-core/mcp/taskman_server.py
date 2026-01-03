"""
TaskMan-v2 MCP Server Implementation

FastMCP server exposing TaskMan-v2 operations as MCP tools.
Implements 12 tools for task, sprint, and project management.

Architecture:
- Uses FastMCP for STDIO-first MCP transport
- Injects TaskManService with repository dependencies via lifespan context
- All tools validate input via Pydantic schemas from cf_core.mcp.schemas
- Returns structured Pydantic models for MCP protocol compatibility

Tools:
  Tasks (6):    create_task, get_task, update_task, delete_task, list_tasks, complete_task
  Sprints (4):  create_sprint, get_sprint, update_sprint, list_sprints
  Projects (2): create_project, get_project

Usage:
  mcp dev cf_core/mcp/taskman_server.py
  python -m cf_core.mcp.taskman_server

Environment:
  TASKMAN_DB_PATH: SQLite database path (default: db/taskman.db)
  TRANSPORT: MCP transport type (default: stdio)
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from cf_core.domain.sprint_entity import SprintEntity

# cf_core imports
from cf_core.domain.task_entity import TaskEntity

# Input schemas
from cf_core.mcp.schemas import (
    CompleteTaskInput,
    CreateProjectInput,
    CreateSprintInput,
    CreateTaskInput,
    DeleteTaskInput,
    GetProjectInput,
    GetSprintInput,
    GetTaskInput,
    ListSprintsInput,
    ListTasksInput,
    UpdateProjectInput,
    UpdateSprintInput,
    UpdateTaskInput,
)
from cf_core.repositories.connection import PostgresConnection
from cf_core.repositories.project_repository import (
    IProjectRepository,
    PostgresProjectRepository,
    SqliteProjectRepository,
)
from cf_core.repositories.sprint_repository import (
    ISprintRepository,
    PostgresSprintRepository,
    SqliteSprintRepository,
)
from cf_core.repositories.task_repository import (
    ITaskRepository,
    PostgresTaskRepository,
    SqliteTaskRepository,
)
from cf_core.services.taskman_service import TaskManService

# =============================================================================
# Response Models (Pydantic for structured MCP output)
# =============================================================================

class TaskModel(BaseModel):
    """Task response model for MCP tools."""
    id: str = Field(description="Task identifier (T-xxx or TASK-xxx)")
    title: str = Field(description="Task title")
    status: Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"] = Field(
        description="Task status"
    )
    priority: Literal["p0", "p1", "p2", "p3"] = Field(
        default="p2", description="Priority level (p0-p3)"
    )
    project_id: str | None = Field(default=None, description="Parent project ID")
    sprint_id: str | None = Field(default=None, description="Sprint assignment")
    story_points: int | None = Field(default=None, description="Story point estimate")
    assignee: str | None = Field(default=None, description="Task assignee")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")


class SprintModel(BaseModel):
    """Sprint response model for MCP tools."""
    id: str = Field(description="Sprint identifier (S-xxx)")
    title: str = Field(description="Sprint title")
    goal: str | None = Field(default=None, description="Sprint goal")
    status: str = Field(description="Sprint status")
    project_id: str | None = Field(default=None, description="Associated project")
    start_date: datetime | None = Field(default=None, description="Sprint start")
    end_date: datetime | None = Field(default=None, description="Sprint end")
    task_count: int = Field(default=0, description="Number of tasks in sprint")


class ProjectModel(BaseModel):
    """Project response model for MCP tools."""
    id: str = Field(description="Project identifier (P-xxx)")
    name: str = Field(description="Project name")
    description: str | None = Field(default=None, description="Project description")
    status: str = Field(description="Project status")
    owner: str | None = Field(default=None, description="Project owner")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")


class OperationResult(BaseModel):
    """Generic operation result for success/failure responses."""
    success: bool = Field(description="Whether operation succeeded")
    message: str | None = Field(default=None, description="Result message")
    data: dict[str, Any] | None = Field(default=None, description="Additional data")


# =============================================================================
# Priority Conversion (int 1-5 to string literal)
# =============================================================================

PRIORITY_INT_TO_STR: dict[int, str] = {
    1: "critical",
    2: "high",
    3: "medium",
    4: "low",
    5: "low",
}

PRIORITY_STR_TO_INT: dict[str, int] = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}


def _normalize_priority(priority: int | str) -> str:
    """Convert priority to string literal (p0-p3)."""
    # Map integers 1-5 to p-values
    int_map = {1: "p0", 2: "p1", 3: "p2", 4: "p3", 5: "p3"}
    str_map = {"critical": "p0", "high": "p1", "medium": "p2", "low": "p3"}

    if isinstance(priority, int):
        return int_map.get(priority, "p2")

    if isinstance(priority, str):
        # Already correct format?
        if priority in ["p0", "p1", "p2", "p3"]:
            return priority
        # Legacy string?
        return str_map.get(priority.lower(), "p2")

    return "p2"


# =============================================================================
# Application Context (Dependency Injection via Lifespan)
# =============================================================================

@dataclass
class AppContext:
    """Application context providing injected dependencies."""
    task_service: TaskManService
    task_repository: ITaskRepository
    sprint_repository: ISprintRepository
    project_repository: IProjectRepository


def _create_service() -> tuple[
    TaskManService, ITaskRepository, ISprintRepository, IProjectRepository
]:
    """Create service with repository dependencies."""
    db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    if db_type == "postgres":
        print("DEBUG: Using PostgreSQL backend")
        pg_conn = PostgresConnection.from_env()
        task_repo = PostgresTaskRepository(pg_conn)
        sprint_repo = PostgresSprintRepository(pg_conn)
        project_repo = PostgresProjectRepository(pg_conn)
    else:
        db_path = os.getenv("TASKMAN_DB_PATH", "db/taskman.db")
        print(f"DEBUG: Using SQLite backend. db_path={db_path}")
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        task_repo = SqliteTaskRepository(db_path=db_path)
        sprint_repo = SqliteSprintRepository(db_path=db_path)
        project_repo = SqliteProjectRepository(db_path=db_path)

    # Create service with injected repositories
    service = TaskManService(
        task_repository=task_repo,
        sprint_repository=sprint_repo,
        project_repository=project_repo,
    )

    return service, task_repo, sprint_repo, project_repo


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    """Lifespan context manager for dependency injection."""
    service, task_repo, sprint_repo, project_repo = _create_service()

    app_ctx = AppContext(
        task_service=service,
        task_repository=task_repo,
        sprint_repository=sprint_repo,
        project_repository=project_repo,
    )

    try:
        yield app_ctx
    finally:
        # Cleanup resources if needed
        pass


# =============================================================================
# FastMCP Server Initialization
# =============================================================================

mcp = FastMCP("TaskMan-v2 MCP Server", lifespan=app_lifespan)


# Helper to get service from context
def _get_service(ctx: Context[None, AppContext]) -> TaskManService:
    """Extract TaskManService from request context."""
    return ctx.request_context.lifespan_context.task_service


def _get_sprint_repo(ctx: Context[None, AppContext]) -> ISprintRepository:
    """Extract sprint repository from request context."""
    return ctx.request_context.lifespan_context.sprint_repository


def _get_project_repo(ctx: Context[None, AppContext]) -> IProjectRepository:
    """Extract project repository from request context."""
    return ctx.request_context.lifespan_context.project_repository


def _task_to_model(entity: TaskEntity) -> TaskModel:
    """Convert TaskEntity to TaskModel response."""
    # Note: TaskEntity uses estimate_hours, not story_points
    # Convert estimate_hours to story_points approximation if present
    story_points = None
    if entity.estimate_hours is not None:
        # Rough conversion: 1 hour ≈ 1 story point
        story_points = int(entity.estimate_hours)

    # Convert priority using new normalization
    priority_str = _normalize_priority(entity.priority)

    return TaskModel(
        id=entity.id,
        title=entity.title,
        status=entity.status,  # type: ignore
        priority=priority_str,  # type: ignore
        project_id=entity.project_id,
        sprint_id=entity.sprint_id,
        story_points=story_points,
        assignee=entity.assignee,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _sprint_to_model(entity: SprintEntity) -> SprintModel:
    """Convert SprintEntity to SprintModel response."""
    return SprintModel(
        id=entity.id,
        title=entity.title,
        goal=getattr(entity, 'goal', None),
        status=entity.status,
        project_id=getattr(entity, 'project_id', None),
        start_date=entity.start_date,
        end_date=entity.end_date,
        task_count=len(getattr(entity, 'task_ids', [])),
    )


def _project_to_model(entity: ProjectModel) -> ProjectModel:
    """Convert valid Project entity/model to MCP response model."""
    # Since we are using the same Pydantic model for internal and external representation in this phase
    # (ProjectModel in mcp/taskman_server.py vs model returned by service)
    # we might just return it or cast it.
    # However, service returns cf_core.models.project.Project (domain entity),
    # while MCP uses local ProjectModel (response schema).

    return ProjectModel(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        status=entity.status,
        owner=entity.owner,
        created_at=getattr(entity, "created_at", None) or datetime.now(),
    )


# =============================================================================
# Task Tools (6 tools)
# =============================================================================

@mcp.tool()
def create_task(
    ctx: Context[None, AppContext],
    title: str,
    description: str | None = None,
    priority: Literal["p0", "p1", "p2", "p3"] = "p2",
    status: Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"] = "new",
    project_id: str | None = None,
    sprint_id: str | None = None,
    story_points: int | None = None,
    tags: list[str] | None = None,
    assignee: str | None = None,
    due_date: datetime | None = None,
    # Phase 2 Fields
    summary: str | None = None,
    owner: str | None = None,
    primary_project: str | None = None,
    primary_sprint: str | None = None,
    observability: dict | None = None,
    risks: list[dict] | None = None,
) -> TaskModel | OperationResult:
    """
    Create a new task in TaskMan-v2.

    Args:
        title: Task title (required, max 200 chars)
        description: Detailed task description (optional)
        priority: Priority level (p0-p3, default: p2)
        status: Task status (default: new)
        project_id: Parent project ID (P-xxx format)
        sprint_id: Sprint assignment (S-xxx format)
        story_points: Story point estimate (1, 2, 3, 5, 8, 13, 21)
        tags: List of tags for categorization
        assignee: Task assignee identifier
        due_date: Task due date (ISO 8601)

    Returns:
        Created task or operation result on failure
    """
    # Validate input via Pydantic schema
    validated = CreateTaskInput(
        title=title,
        description=description,
        priority=priority,
        status=status,
        project_id=project_id,
        sprint_id=sprint_id,
        story_points=story_points,
        tags=tags,
        assignee=assignee,
        due_date=due_date,
        summary=summary,
        owner=owner,
        primary_project=primary_project,
        primary_sprint=primary_sprint,
        observability=observability,
        risks=risks,
    )

    service = _get_service(ctx)

    # Check if risks are supported by service (likely not yet in explicit args)
    # If service.create_task doesn't accept risks yet, we might need to handle it separately
    # or just omit it for now if the service signature in previous steps didn't show it.
    # The snippet showed 'observability' but not 'risks'.

    result = service.create_task(
        title=validated.title,
        description=validated.description,
        priority=_normalize_priority(validated.priority),
        status=validated.status,
        project_id=validated.project_id,
        sprint_id=validated.sprint_id,
        story_points=validated.story_points,
        tags=validated.tags,
        assignee=validated.assignee,
        due_date=validated.due_date,
        summary=validated.summary,
        owner=validated.owner,
        primary_project=validated.primary_project,
        primary_sprint=validated.primary_sprint,
        observability=validated.observability,
        risks=validated.risks,
    )

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _task_to_model(result.value)


@mcp.tool()
def get_task(
    ctx: Context[None, AppContext],
    task_id: str,
) -> TaskModel | OperationResult:
    """
    Retrieve a task by ID.

    Args:
        task_id: Task identifier (T-xxx or TASK-xxx format)

    Returns:
        Task details or error result if not found
    """
    # Validate input
    validated = GetTaskInput(task_id=task_id)

    service = _get_service(ctx)
    result = service.get_task(validated.task_id)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _task_to_model(result.value)


@mcp.tool()
def update_task(
    ctx: Context[None, AppContext],
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    status: Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"]
    | None = None,
    priority: Literal["p0", "p1", "p2", "p3"] | None = None,
    project_id: str | None = None,
    sprint_id: str | None = None,
    story_points: int | None = None,
    actual_hours: float | None = None,
    assignee: str | None = None,
    due_date: datetime | None = None,
) -> TaskModel | OperationResult:
    """
    Update an existing task.

    Args:
        task_id: Task ID to update (required)
        title: New task title
        description: New description
        status: New status (todo, in_progress, done, blocked, cancelled)
        priority: New priority (1-5)
        project_id: New project assignment
        sprint_id: New sprint assignment
        story_points: New story point estimate
        actual_hours: Actual hours spent
        assignee: New assignee
        due_date: New due date

    Returns:
        Updated task or error result
    """
    # Validate input
    validated = UpdateTaskInput(
        task_id=task_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        project_id=project_id,
        sprint_id=sprint_id,
        story_points=story_points,
        actual_hours=actual_hours,
        assignee=assignee,
        due_date=due_date,
    )

    service = _get_service(ctx)

    # Build update kwargs (only non-None values)
    update_kwargs: dict[str, Any] = {}
    if validated.title is not None:
        update_kwargs['title'] = validated.title
    if validated.description is not None:
        update_kwargs['description'] = validated.description
    if validated.status is not None:
        update_kwargs['status'] = validated.status
    if validated.priority is not None:
        update_kwargs["priority"] = _normalize_priority(validated.priority)
    if validated.project_id is not None:
        update_kwargs['project_id'] = validated.project_id
    if validated.sprint_id is not None:
        update_kwargs['sprint_id'] = validated.sprint_id
    if validated.story_points is not None:
        update_kwargs['story_points'] = validated.story_points
    if validated.actual_hours is not None:
        update_kwargs['actual_hours'] = validated.actual_hours
    if validated.due_date is not None:
        update_kwargs["due_date"] = validated.due_date
    if validated.assignee is not None:
        update_kwargs['assignee'] = validated.assignee

    result = service.update_task(validated.task_id, **update_kwargs)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _task_to_model(result.value)


@mcp.tool()
def delete_task(
    ctx: Context[None, AppContext],
    task_id: str,
    force: bool = False,
) -> OperationResult:
    """
    Delete a task by ID.

    Args:
        task_id: Task ID to delete (required)
        force: Force delete without confirmation (default: False)

    Returns:
        Operation result indicating success or failure
    """
    # Validate input
    validated = DeleteTaskInput(task_id=task_id, force=force)

    service = _get_service(ctx)
    result = service.delete_task(validated.task_id)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return OperationResult(
        success=True,
        message=f"Task {validated.task_id} deleted successfully",
    )


@mcp.tool()
def list_tasks(
    ctx: Context[None, AppContext],
    status: str | None = None,
    project_id: str | None = None,
    sprint_id: str | None = None,
    priority: Literal["p0", "p1", "p2", "p3"] | None = None,
    assignee: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TaskModel]:
    """
    List tasks with optional filters.

    Args:
        status: Filter by status (todo, in_progress, done, blocked, cancelled)
        project_id: Filter by project ID
        sprint_id: Filter by sprint ID
        priority: Filter by priority level (1-5)
        assignee: Filter by assignee
        limit: Maximum results (1-100, default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        List of matching tasks
    """
    # Validate input
    validated = ListTasksInput(
        status=status,
        project_id=project_id,
        sprint_id=sprint_id,
        priority=priority,
        assignee=assignee,
        limit=limit,
        offset=offset,
    )

    service = _get_service(ctx)
    result = service.list_tasks(
        status=validated.status,
        sprint_id=validated.sprint_id,
        assignee=validated.assignee,
    )

    if result.is_failure:
        return []

    tasks = result.value

    # Apply additional filters not in service layer
    if validated.project_id:
        tasks = [t for t in tasks if t.project_id == validated.project_id]
    if validated.priority:
        tasks = [t for t in tasks if t.priority == validated.priority]

    # Apply pagination
    tasks = tasks[validated.offset:validated.offset + validated.limit]

    return [_task_to_model(t) for t in tasks]


@mcp.tool()
def complete_task(
    ctx: Context[None, AppContext],
    task_id: str,
    actual_hours: float | None = None,
    notes: str | None = None,
) -> TaskModel | OperationResult:
    """
    Mark a task as complete.

    Args:
        task_id: Task ID to complete (required)
        actual_hours: Actual hours spent on the task
        notes: Completion notes or summary

    Returns:
        Completed task or error result
    """
    # Validate input
    validated = CompleteTaskInput(
        task_id=task_id,
        actual_hours=actual_hours,
        notes=notes,
    )

    service = _get_service(ctx)

    # Use complete_task method from service
    result = service.complete_task(validated.task_id)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    # Update actual_hours if provided
    if validated.actual_hours is not None:
        service.update_task(validated.task_id, actual_hours=validated.actual_hours)

    return _task_to_model(result.value)


# =============================================================================
# Sprint Tools (4 tools)
# =============================================================================

@mcp.tool()
def create_sprint(
    ctx: Context[None, AppContext],
    sprint_id: str,
    title: str,
    project_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: str = "new",
    # Phase 2 Fields
    owner: str | None = None,
    cadence: str | None = None,
    observability: dict | None = None,
    task_ids: list[str] | None = None,
    risks: list[dict] | None = None,
) -> SprintModel | OperationResult:
    """
    Create a new sprint.

    Args:
        sprint_id: Sprint ID (S-xxx format, required)
        title: Sprint title (required)
        goal: Sprint goal or objective
        project_id: Associated project ID
        start_date: Sprint start date (ISO 8601)
        end_date: Sprint end date (ISO 8601)
        status: Sprint status (default: planned)

    Returns:
        Created sprint or error result
    """
    # Validate input
    validated = CreateSprintInput(
        sprint_id=sprint_id,
        title=title,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        owner=owner,
        cadence=cadence,
        observability=observability,
        task_ids=task_ids,
        risks=risks,
    )

    # Create sprint via service
    service = _get_service(ctx)
    result = service.create_sprint(
        name=validated.title,
        start_date=validated.start_date or datetime.now(),
        end_date=validated.end_date or datetime.now(),
        project_id=validated.project_id,
        goal=validated.goal,
        # Phase 2 Fields
        owner=validated.owner,
        cadence=validated.cadence,
        observability=validated.observability,
        task_ids=validated.task_ids,
    )

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _sprint_to_model(result.value)

    # Legacy direct repository usage removed in favor of service
    """
    # Create sprint entity
    # Note: SprintEntity.create() uses 'name' parameter, not 'title'
    sprint = SprintEntity.create(
        sprint_id=validated.sprint_id,
        name=validated.title,  # SprintEntity uses 'name', validated input has 'title'
        goal=validated.goal,
        project_id=validated.project_id,
        start_date=validated.start_date or datetime.now(),
        end_date=validated.end_date,
        status=validated.status,
    )

    # Save via repository
    sprint_repo = _get_sprint_repo(ctx)
    try:
        saved = sprint_repo.save(sprint)
        return _sprint_to_model(saved)
    except Exception as e:
        return OperationResult(
            success=False,
            message=f"Failed to create sprint: {e}",
        )
    """


@mcp.tool()
def get_sprint(
    ctx: Context[None, AppContext],
    sprint_id: str,
) -> SprintModel | OperationResult:
    """
    Retrieve a sprint by ID.

    Args:
        sprint_id: Sprint identifier (S-xxx format)

    Returns:
        Sprint details or error result if not found
    """
    # Validate input
    validated = GetSprintInput(sprint_id=sprint_id)

    sprint_repo = _get_sprint_repo(ctx)
    sprint = sprint_repo.get_by_id(validated.sprint_id)

    if sprint is None:
        return OperationResult(
            success=False,
            message=f"Sprint {validated.sprint_id} not found",
        )

    return _sprint_to_model(sprint)


@mcp.tool()
def update_sprint(
    ctx: Context[None, AppContext],
    sprint_id: str,
    title: str | None = None,
    goal: str | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SprintModel | OperationResult:
    """
    Update an existing sprint.

    Args:
        sprint_id: Sprint ID to update (required)
        title: New sprint title
        goal: New sprint goal
        status: New status (planned, active, completed, cancelled)
        start_date: New start date
        end_date: New end date

    Returns:
        Updated sprint or error result
    """
    # Validate input
    validated = UpdateSprintInput(
        sprint_id=sprint_id,
        title=title,
        goal=goal,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )

    sprint_repo = _get_sprint_repo(ctx)
    sprint = sprint_repo.get_by_id(validated.sprint_id)

    if sprint is None:
        return OperationResult(
            success=False,
            message=f"Sprint {validated.sprint_id} not found",
        )

    # Update fields
    if validated.title is not None:
        sprint.title = validated.title
    if validated.goal is not None:
        sprint.goal = validated.goal
    if validated.status is not None:
        # SprintEntity.status has no setter; use update_status() method
        sprint.update_status(validated.status)
    if validated.start_date is not None:
        sprint.start_date = validated.start_date
    if validated.end_date is not None:
        sprint.end_date = validated.end_date

    # Save updated sprint
    try:
        saved = sprint_repo.save(sprint)
        return _sprint_to_model(saved)
    except Exception as e:
        return OperationResult(
            success=False,
            message=f"Failed to update sprint: {e}",
        )


@mcp.tool()
def list_sprints(
    ctx: Context[None, AppContext],
    project_id: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[SprintModel]:
    """
    List sprints with optional filters.

    Args:
        project_id: Filter by project ID
        status: Filter by status (planned, active, completed, cancelled)
        limit: Maximum results (1-50, default: 20)

    Returns:
        List of matching sprints
    """
    # Validate input
    validated = ListSprintsInput(
        project_id=project_id,
        status=status,
        limit=limit,
    )

    service = _get_service(ctx)
    result = service.list_sprints()

    if result.is_failure:
        return []

    sprints = result.value

    # Apply filters
    if validated.project_id:
        sprints = [s for s in sprints if s.project_id == validated.project_id]
    if validated.status:
        sprints = [s for s in sprints if s.status == validated.status]

    # Apply limit
    sprints = sprints[:validated.limit]

    return [_sprint_to_model(s) for s in sprints]


# =============================================================================
# Project Tools (2 tools)
# =============================================================================

@mcp.tool()
def create_project(
    ctx: Context[None, AppContext],
    project_id: str,
    name: str,
    description: str | None = None,
    owner: str | None = None,
    status: Literal["discovery", "active", "paused", "closed"] = "discovery",
    target_end_date: datetime | None = None,
    tags: list[str] | None = None,
    mission: str | None = None,
    vision: str | None = None,
    roadmap_url: str | None = None,
    observability: dict | None = None,
    team_members: list[str] | None = None,
) -> ProjectModel | OperationResult:
    """
    Create a new project.

    Args:
        project_id: Project ID (P-xxx format, required)
        name: Project name (required)
        description: Project description
        owner: Project owner/lead identifier
        status: Project status (default: discovery)
        target_end_date: Target completion date
        tags: List of project tags

    Returns:
        Created project or error result
    """
    # Validate input
    validated = CreateProjectInput(
        project_id=project_id,
        name=name,
        description=description,
        owner=owner,
        status=status,
        target_end_date=target_end_date,
        tags=tags,
        mission=mission,
        vision=vision,
        roadmap_url=roadmap_url,
        observability=observability,
        team_members=team_members,
    )

    service = _get_service(ctx)
    result = service.create_project(
        project_id=validated.project_id,
        name=validated.name,
        description=validated.description,
        owner=validated.owner,
        status=validated.status,
        target_end_date=validated.target_end_date,
        tags=validated.tags,
        mission=validated.mission,
        vision=validated.vision,
        roadmap_url=validated.roadmap_url,
        observability=validated.observability,
        team_members=validated.team_members,
    )

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _project_to_model(result.value)


@mcp.tool()
def get_project(
    ctx: Context[None, AppContext],
    project_id: str,
) -> ProjectModel | OperationResult:
    """
    Retrieve a project by ID.

    Args:
        project_id: Project identifier (P-xxx format)

    Returns:
        Project details or error result if not found
    """
    # Validate input
    validated = GetProjectInput(project_id=project_id)

    service = _get_service(ctx)
    result = service.get_project(validated.project_id)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _project_to_model(result.value)


@mcp.tool()
def update_project(
    ctx: Context[None, AppContext],
    project_id: str,
    name: str | None = None,
    description: str | None = None,
    owner: str | None = None,
    status: Literal["discovery", "active", "paused", "closed"] | None = None,
    target_end_date: datetime | None = None,
    tags: list[str] | None = None,
    mission: str | None = None,
    vision: str | None = None,
    roadmap_url: str | None = None,
    observability: dict | None = None,
    team_members: list[str] | None = None,
) -> ProjectModel | OperationResult:
    """
    Update an existing project.

    Args:
        project_id: Project identifier (required)
        name: New project name
        description: New description
        owner: New owner
        status: New status
        target_end_date: New target end date

    Returns:
        Updated project or error result
    """
    # Validate input
    validated = UpdateProjectInput(
        project_id=project_id,
        name=name,
        description=description,
        owner=owner,
        status=status,
        target_end_date=target_end_date,
        tags=tags,
        mission=mission,
        vision=vision,
        roadmap_url=roadmap_url,
        observability=observability,
        team_members=team_members,
    )

    service = _get_service(ctx)

    # Build updates dict
    updates = {}
    for field in [
        "name",
        "description",
        "owner",
        "status",
        "target_end_date",
        "tags",
        "mission",
        "vision",
        "roadmap_url",
        "observability",
        "team_members",
    ]:
        val = getattr(validated, field)
        if val is not None:
            updates[field] = val

    result = service.update_project(validated.project_id, **updates)

    if result.is_failure:
        return OperationResult(
            success=False,
            message=str(result.error),
        )

    return _project_to_model(result.value)


@mcp.tool()
def list_projects(
    ctx: Context[None, AppContext],
    status: str | None = None,
    owner: str | None = None,
    limit: int = 50,
) -> list[ProjectModel]:
    """
    List projects with optional filters.

    Args:
        status: Filter by status
        owner: Filter by owner
        limit: Maximum results (default: 50)

    Returns:
        List of matching projects
    """
    # Validate input
    validated = ListProjectsInput(
        status=status,
        owner=owner,
        limit=limit,
    )

    service = _get_service(ctx)
    result = service.list_projects(
        status=validated.status,
        owner=validated.owner,
        limit=validated.limit,
    )

    if result.is_failure:
        return []

    return [_project_to_model(p) for p in result.value]


# =============================================================================
# Server Entry Points
# =============================================================================

class TaskManMCPServer:
    """
    Wrapper class for TaskMan MCP server with convenience methods.

    Provides direct access to task, sprint, and project operations
    without requiring MCP protocol overhead. Useful for testing and
    direct Python integration.
    """

    def __init__(self, db_path: str | None = None):
        """
        Initialize server with database path.

        Args:
            db_path: SQLite database path (default: db/taskman.db)
        """
        self._db_path = db_path or os.getenv("TASKMAN_DB_PATH", "db/taskman.db")
        if db_path:
            os.environ["TASKMAN_DB_PATH"] = db_path

        # Initialize repositories and service
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._task_repo = SqliteTaskRepository(self._db_path)
        self._sprint_repo = SqliteSprintRepository(self._db_path)
        self._project_repo = SqliteProjectRepository(self._db_path)
        self._service = TaskManService(task_repository=self._task_repo)

    @property
    def server(self) -> FastMCP:
        """Get the underlying FastMCP server instance."""
        return mcp

    @property
    def server_name(self) -> str:
        """Get the server name."""
        return "taskman-v2"

    @property
    def db_path(self) -> str:
        """Get the database path."""
        return self._db_path

    def run(self, transport: str = "stdio") -> None:
        """Run the MCP server with specified transport."""
        mcp.run(transport=transport)

    # =========================================================================
    # Task Methods
    # =========================================================================

    def create_task(
        self,
        title: str,
        description: str | None = None,
        priority: int | str = "medium",
        status: str = "new",
        project_id: str | None = None,
        sprint_id: str | None = None,
        story_points: int | None = None,
        assignee: str | None = None,
    ) -> TaskModel | OperationResult:
        """
        Create a new task.

        Args:
            title: Task title (required)
            description: Task description
            priority: Priority level (1-5 int or 'low','medium','high','critical' string)
            status: Task status (default: todo)
            project_id: Parent project ID
            sprint_id: Sprint assignment
            story_points: Estimated story points (converted to estimate_hours)
            assignee: Assigned user/team

        Returns:
            TaskModel on success, OperationResult on failure
        """
        try:
            # Convert story_points to estimate_hours if provided (rough 1:1 ratio)
            estimate_hours = float(story_points) if story_points else None

            # Normalize priority (int 1-5 to string literal)
            normalized_priority = _normalize_priority(priority)

            result = self._service.create_task(
                title=title,
                description=description,
                priority=normalized_priority,
                status=status,
                project_id=project_id,
                sprint_id=sprint_id,
                assignee=assignee,
                estimate_hours=estimate_hours,
            )
            if result.is_success:
                return _task_to_model(result.value)
            return OperationResult(success=False, message=str(result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to create task: {e}")

    def get_task(self, task_id: str) -> TaskModel | OperationResult:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task identifier (T-xxx format)

        Returns:
            TaskModel on success, OperationResult on failure
        """
        try:
            result = self._service.get_task(task_id)
            if result.is_success:
                return _task_to_model(result.value)
            return OperationResult(success=False, message=f"Task not found: {task_id}")
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to get task: {e}")

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: int | str | None = None,
        status: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        story_points: int | None = None,
        assignee: str | None = None,
    ) -> TaskModel | OperationResult:
        """
        Update an existing task.

        Args:
            task_id: Task identifier (required)
            title: New title
            description: New description
            priority: New priority
            status: New status
            project_id: New project ID
            sprint_id: New sprint assignment
            story_points: New story points
            assignee: New assignee

        Returns:
            Updated TaskModel on success, OperationResult on failure
        """
        try:
            result = self._service.get_task(task_id)
            if not result.is_success:
                return OperationResult(success=False, message=f"Task not found: {task_id}")

            task = result.value
            updates: dict[str, Any] = {}
            if title is not None:
                updates["title"] = title
            if description is not None:
                updates["description"] = description
            if priority is not None:
                updates["priority"] = priority
            if status is not None:
                updates["status"] = status
            if project_id is not None:
                updates["project_id"] = project_id
            if sprint_id is not None:
                updates["sprint_id"] = sprint_id
            if story_points is not None:
                updates["story_points"] = story_points
            if assignee is not None:
                updates["assignee"] = assignee

            updated_task = task.update(**updates)
            save_result = self._task_repo.save(updated_task)
            if save_result.is_success:
                return _task_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to update task: {e}")

    def delete_task(self, task_id: str) -> OperationResult:
        """
        Delete a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            OperationResult with success/failure status
        """
        try:
            result = self._task_repo.delete(task_id)
            if result.is_success and result.value:
                return OperationResult(success=True, message=f"Task {task_id} deleted")
            return OperationResult(success=False, message=f"Task not found: {task_id}")
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to delete task: {e}")

    def list_tasks(
        self,
        status: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        limit: int = 50,
    ) -> list[TaskModel]:
        """
        List tasks with optional filtering.

        Args:
            status: Filter by status
            project_id: Filter by project
            sprint_id: Filter by sprint
            limit: Maximum results (default: 50)

        Returns:
            List of TaskModel objects
        """
        try:
            # Use service's list_tasks method with optional status filter
            result = self._service.list_tasks(
                status=status,
                sprint_id=sprint_id,
                limit=limit,
            )

            if result.is_success:
                tasks = result.value
                # Apply additional project_id filter (not in service method)
                if project_id:
                    tasks = [t for t in tasks if t.project_id == project_id]
                return [_task_to_model(t) for t in tasks]
            return []
        except Exception:
            return []

    def complete_task(
        self,
        task_id: str,
        actual_hours: float | None = None,
        completion_notes: str | None = None,
    ) -> TaskModel | OperationResult:
        """
        Mark a task as completed.

        Args:
            task_id: Task identifier
            actual_hours: Actual hours spent
            completion_notes: Notes about completion

        Returns:
            Updated TaskModel on success, OperationResult on failure
        """
        try:
            result = self._service.get_task(task_id)
            if not result.is_success:
                return OperationResult(success=False, message=f"Task not found: {task_id}")

            task = result.value
            updates = {"status": "done", "completed_at": datetime.now()}
            if actual_hours is not None:
                updates["actual_hours"] = actual_hours

            updated_task = task.update(**updates)
            save_result = self._task_repo.save(updated_task)
            if save_result.is_success:
                return _task_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to complete task: {e}")

    # =========================================================================
    # Sprint Methods
    # =========================================================================

    def create_sprint(
        self,
        sprint_id: str | None = None,
        title: str | None = None,
        name: str | None = None,
        goal: str | None = None,
        project_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: str = "new",
    ) -> SprintModel | OperationResult:
        """
        Create a new sprint.

        Args:
            sprint_id: Sprint ID (S-xxx format, required)
            title: Sprint title (required)
            goal: Sprint goal/objective
            project_id: Associated project
            start_date: Sprint start date
            end_date: Sprint end date
            status: Sprint status (default: planned)

        Returns:
            SprintModel on success, OperationResult on failure
        """
        try:
            # Handle name as alias for title
            sprint_title = title or name
            if not sprint_title:
                return OperationResult(success=False, message="Sprint title/name is required")

            # Generate sprint_id if not provided
            from cf_core.models.identifiers import generate_sprint_id
            actual_sprint_id = sprint_id or generate_sprint_id()

            sprint = SprintEntity.create(
                sprint_id=actual_sprint_id,
                name=sprint_title,
                start_date=start_date or datetime.now(),
                end_date=end_date,
                goal=goal,
                project_id=project_id,
                status=status,
            )
            save_result = self._sprint_repo.save(sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to create sprint: {e}")

    def get_sprint(self, sprint_id: str) -> SprintModel | OperationResult:
        """
        Retrieve a sprint by ID.

        Args:
            sprint_id: Sprint identifier (S-xxx format)

        Returns:
            SprintModel on success, OperationResult on failure
        """
        try:
            result = self._sprint_repo.get_by_id(sprint_id)
            if result.is_success and result.value:
                return _sprint_to_model(result.value)
            return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to get sprint: {e}")

    def update_sprint(
        self,
        sprint_id: str,
        title: str | None = None,
        goal: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> SprintModel | OperationResult:
        """
        Update an existing sprint.

        Args:
            sprint_id: Sprint identifier (required)
            title: New title
            goal: New goal
            status: New status
            start_date: New start date
            end_date: New end date

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value
            updates: dict[str, Any] = {}
            if title is not None:
                updates["title"] = title
            if status is not None:
                updates["status"] = status
            if start_date is not None:
                updates["start_date"] = start_date
            if end_date is not None:
                updates["end_date"] = end_date

            updated_sprint = sprint.update(**updates)
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to update sprint: {e}")

    def list_sprints(
        self,
        project_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[SprintModel]:
        """
        List sprints with optional filtering.

        Args:
            project_id: Filter by project
            status: Filter by status
            limit: Maximum results (default: 50)

        Returns:
            List of SprintModel objects
        """
        try:
            find_result = self._sprint_repo.find_all()
            if not find_result.is_success:
                return []
            sprints = find_result.value
            # Apply filters before limiting
            if status:
                sprints = [s for s in sprints if s.status == status]
            if project_id:
                sprints = [s for s in sprints if s.project_id == project_id]
            # Apply limit after filtering
            sprints = sprints[:limit]
            return [_sprint_to_model(s) for s in sprints]
        except Exception:
            return []

    def start_sprint(self, sprint_id: str) -> SprintModel | OperationResult:
        """
        Start a sprint (transition to active status).

        Args:
            sprint_id: Sprint identifier (S-xxx format)

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value

            # Check if transition is valid
            if not sprint.can_transition_to("active"):
                return OperationResult(
                    success=False,
                    message=f"Cannot start sprint: invalid transition from '{sprint.status}' to 'active'",
                )

            # Update status to active
            updated_sprint = sprint.update(status="active")
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to start sprint: {e}")

    def complete_sprint(
        self,
        sprint_id: str,
        notes: str | None = None,
    ) -> SprintModel | OperationResult:
        """
        Complete a sprint (transition to completed status).

        Args:
            sprint_id: Sprint identifier (S-xxx format)
            notes: Optional completion notes

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value

            # Check if transition is valid
            if not sprint.can_transition_to("completed"):
                return OperationResult(
                    success=False,
                    message=f"Cannot complete sprint: invalid transition from '{sprint.status}' to 'completed'",
                )

            # Update status to completed with timestamp
            updates: dict[str, Any] = {"status": "completed", "completed_at": datetime.now()}
            updated_sprint = sprint.update(**updates)
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to complete sprint: {e}")

    def cancel_sprint(
        self,
        sprint_id: str,
        reason: str | None = None,
    ) -> SprintModel | OperationResult:
        """
        Cancel a sprint (transition to cancelled status).

        Args:
            sprint_id: Sprint identifier (S-xxx format)
            reason: Optional cancellation reason

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value

            # Check if transition is valid
            if not sprint.can_transition_to("cancelled"):
                return OperationResult(
                    success=False,
                    message=f"Cannot cancel sprint: invalid transition from '{sprint.status}' to 'cancelled'",
                )

            # Update status to cancelled
            updated_sprint = sprint.update(status="cancelled")
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to cancel sprint: {e}")

    def block_sprint(
        self,
        sprint_id: str,
        reason: str | None = None,
    ) -> SprintModel | OperationResult:
        """
        Block a sprint (transition to blocked status).

        Args:
            sprint_id: Sprint identifier (S-xxx format)
            reason: Blocking reason (required by Sprint model validation)

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value

            # Check if transition is valid
            if not sprint.can_transition_to("blocked"):
                return OperationResult(
                    success=False,
                    message=f"Cannot block sprint: invalid transition from '{sprint.status}' to 'blocked'",
                )

            # Update status to blocked with required blocked_reason
            # Sprint model requires blocked_reason when status is "blocked"
            blocked_reason = reason or "Blocked (no reason provided)"
            updated_sprint = sprint.update(status="blocked", blocked_reason=blocked_reason)
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to block sprint: {e}")

    def unblock_sprint(self, sprint_id: str) -> SprintModel | OperationResult:
        """
        Unblock a sprint (transition from blocked to active status).

        Args:
            sprint_id: Sprint identifier (S-xxx format)

        Returns:
            Updated SprintModel on success, OperationResult on failure
        """
        try:
            get_result = self._sprint_repo.get_by_id(sprint_id)
            if not get_result.is_success or not get_result.value:
                return OperationResult(success=False, message=f"Sprint not found: {sprint_id}")

            sprint = get_result.value

            # Must be in blocked status to unblock
            if sprint.status != "blocked":
                return OperationResult(
                    success=False,
                    message=f"Cannot unblock sprint: current status is '{sprint.status}', not 'blocked'",
                )

            # Check if transition is valid
            if not sprint.can_transition_to("active"):
                return OperationResult(
                    success=False,
                    message=f"Cannot unblock sprint: invalid transition from '{sprint.status}' to 'active'",
                )

            # Update status to active and clear blocked_reason
            # Must clear blocked_reason when transitioning out of blocked status
            updated_sprint = sprint.update(status="active", blocked_reason=None)
            save_result = self._sprint_repo.save(updated_sprint)
            if save_result.is_success:
                return _sprint_to_model(save_result.value)
            return OperationResult(success=False, message=str(save_result.error))
        except Exception as e:
            return OperationResult(success=False, message=f"Failed to unblock sprint: {e}")

    # =========================================================================
    # Project Methods
    # =========================================================================

    def _project_to_model(self, entity) -> ProjectModel:
        """Convert ProjectEntity to ProjectModel for MCP response."""
        from cf_core.domain.project_entity import ProjectEntity

        if isinstance(entity, ProjectEntity):
            return ProjectModel(
                id=entity.id,
                name=entity.name,
                description=entity.description,
                status=entity.status,
                owner=entity.owner,
                created_at=entity.created_at,
            )
        # Fallback for Result wrapper
        return entity

    def create_project(
        self,
        name: str,
        description: str | None = None,
        project_id: str | None = None,
        owner: str | None = None,
        status: str = "new",
        target_end_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> ProjectModel | OperationResult:
        """
        Create a new project.

        Args:
            name: Project name (required)
            description: Project description
            project_id: Project ID (P-xxx format, auto-generated if not provided)
            owner: Project owner/lead
            status: Project status (default: new)
            target_end_date: Target completion date
            tags: Project tags

        Returns:
            ProjectModel on success, OperationResult on failure
        """
        import uuid

        from cf_core.domain.project_entity import ProjectEntity

        actual_project_id = project_id or f"P-{uuid.uuid4().hex[:8].upper()}"

        try:
            entity = ProjectEntity.create(
                project_id=actual_project_id,
                name=name,
                description=description or "",  # Project model requires string, not None
                owner=owner,
                status=status,
                target_end_date=target_end_date,
                tags=tags,
            )

            result = self._project_repo.save(entity)
            if result.is_success:
                return self._project_to_model(result.value)
            return OperationResult(success=False, message=result.error)
        except Exception as e:
            return OperationResult(success=False, message=f"Error creating project: {e}")

    def get_project(self, project_id: str) -> ProjectModel | OperationResult:
        """
        Retrieve a project by ID.

        Args:
            project_id: Project identifier (P-xxx format)

        Returns:
            ProjectModel on success, OperationResult on failure
        """
        result = self._project_repo.get_by_id(project_id)
        if result.is_success:
            return self._project_to_model(result.value)
        return OperationResult(success=False, message=f"Project not found: {project_id}")

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        owner: str | None = None,
        status: str | None = None,
    ) -> ProjectModel | OperationResult:
        """
        Update an existing project.

        Args:
            project_id: Project identifier (P-xxx format)
            name: New project name
            description: New description
            owner: New owner
            status: New status

        Returns:
            Updated ProjectModel on success, OperationResult on failure
        """
        result = self._project_repo.get_by_id(project_id)
        if not result.is_success:
            return OperationResult(success=False, message=f"Project not found: {project_id}")

        entity = result.value

        # Build updates dict
        updates = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if owner is not None:
            updates["owner"] = owner
        if status is not None:
            updates["status"] = status

        if updates:
            updated_entity = entity.update(**updates)
            save_result = self._project_repo.save(updated_entity)
            if save_result.is_success:
                return self._project_to_model(save_result.value)
            return OperationResult(success=False, message=save_result.error)

        return self._project_to_model(entity)

    def list_projects(
        self,
        status: str | None = None,
        owner: str | None = None,
        limit: int = 50,
    ) -> list[ProjectModel]:
        """
        List projects with optional filtering.

        Args:
            status: Filter by status
            owner: Filter by owner
            limit: Maximum number of results

        Returns:
            List of ProjectModel objects
        """
        if status:
            result = self._project_repo.find_by_status(status)
        elif owner:
            result = self._project_repo.find_by_owner(owner)
        else:
            result = self._project_repo.find_all()

        if result.is_success:
            projects = result.value[:limit]
            return [self._project_to_model(p) for p in projects]
        return []

    def delete_project(self, project_id: str) -> OperationResult:
        """
        Delete a project by ID.

        Args:
            project_id: Project identifier (P-xxx format)

        Returns:
            OperationResult indicating success or failure
        """
        result = self._project_repo.delete(project_id)
        if result.is_success:
            return OperationResult(success=True, message=f"Project {project_id} deleted")
        return OperationResult(success=False, message=f"Project not found: {project_id}")


def create_taskman_server(db_path: str | None = None) -> TaskManMCPServer:
    """
    Factory function to create TaskMan MCP server instance.

    Args:
        db_path: Optional SQLite database path (default: db/taskman.db)

    Returns:
        Configured TaskManMCPServer instance
    """
    return TaskManMCPServer(db_path=db_path)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    # Default to stdio transport; allow override
    transport = os.getenv("TRANSPORT", "stdio").strip()
    if transport not in {"stdio", "streamable-http"}:
        transport = "stdio"

    print(f"Starting TaskMan-v2 MCP Server (transport: {transport})")
    mcp.run(transport=transport)
