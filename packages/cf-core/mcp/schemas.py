"""
Pydantic Input Schemas for TaskMan-v2 MCP Tools

Defines all input schemas for the 12 MCP tools with proper validation.
Uses Pydantic v2 for JSON schema generation compatible with MCP protocol.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# Task Tool Input Schemas
# =============================================================================

class CreateTaskInput(BaseModel):
    """Input schema for create_task tool."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (required)",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="Detailed task description",
    )
    priority: Literal["p0", "p1", "p2", "p3"] = Field(
        "p2",
        description="Priority level: p0 (Critical) to p3 (Low). Default: p2",
    )
    status: Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"] = Field(
        "new",
        description="Task status: new, ready, in_progress, blocked, review, done, dropped",
    )
    project_id: str | None = Field(
        None,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Parent project ID (format: P-xxx)",
    )
    sprint_id: str | None = Field(
        None,
        pattern=r"^S-[a-zA-Z0-9_-]+$",
        description="Sprint assignment (format: S-xxx)",
    )
    story_points: int | None = Field(
        None,
        ge=1,
        le=21,
        description="Story point estimate (1, 2, 3, 5, 8, 13, 21)",
    )
    tags: list[str] | None = Field(
        None,
        description="List of tags for categorization",
    )
    assignee: str | None = Field(
        None,
        description="Task assignee identifier",
    )
    due_date: datetime | None = Field(
        None,
        description="Task due date (ISO 8601 format)",
    )
    # Phase 2 Fields
    summary: str | None = Field(
        None,
        max_length=200,
        description="Short summary/header (defaults to title if not provided)",
    )
    owner: str | None = Field(
        None,
        description="Task owner",
    )
    observability: dict | None = Field(
        None,
        description="Observability object (status, health_score, evidence)",
    )
    risks: list[dict] | None = Field(
        None,
        description="List of risk objects",
    )
    primary_project: str | None = Field(
        None,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Primary project ID (alias for project_id)",
    )
    primary_sprint: str | None = Field(
        None,
        pattern=r"^S-[a-zA-Z0-9_-]+$",
        description="Primary sprint ID (alias for sprint_id)",
    )


class GetTaskInput(BaseModel):
    """Input schema for get_task tool."""

    task_id: str = Field(
        ...,
        pattern=r"^(T-|TASK-)[a-zA-Z0-9_-]+$",
        description="Task ID to retrieve (format: T-xxx or TASK-xxx)",
    )


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""

    task_id: str = Field(
        ...,
        pattern=r"^(T-|TASK-)[a-zA-Z0-9_-]+$",
        description="Task ID to update (required)",
    )
    title: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="New task title",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="New task description",
    )
    status: (
        Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"] | None
    ) = Field(
        None,
        description="New status",
    )
    priority: Literal["p0", "p1", "p2", "p3"] | None = Field(
        None,
        description="New priority",
    )
    project_id: str | None = Field(
        None,
        description="New project ID assignment",
    )
    sprint_id: str | None = Field(
        None,
        description="New sprint assignment",
    )
    story_points: int | None = Field(
        None,
        ge=1,
        le=21,
        description="New story point estimate",
    )
    actual_hours: float | None = Field(
        None,
        ge=0,
        description="Actual hours spent",
    )
    due_date: datetime | None = Field(
        None,
        description="New due date",
    )
    # Phase 2 Fields
    summary: str | None = Field(
        None,
        description="New summary",
    )
    owner: str | None = Field(
        None,
        description="New owner",
    )
    observability: dict | None = Field(
        None,
        description="New observability data",
    )
    risks: list[dict] | None = Field(
        None,
        description="New risks list",
    )
    primary_project: str | None = Field(
        None,
        description="New primary project assignment",
    )
    primary_sprint: str | None = Field(
        None,
        description="New primary sprint assignment",
    )


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""

    task_id: str = Field(
        ...,
        pattern=r"^(T-|TASK-)[a-zA-Z0-9_-]+$",
        description="Task ID to delete (required)",
    )
    force: bool = Field(
        False,
        description="Force delete without confirmation",
    )


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    status: (
        Literal["new", "ready", "in_progress", "blocked", "review", "done", "dropped"] | None
    ) = Field(
        None,
        description="Filter by status",
    )
    project_id: str | None = Field(
        None,
        description="Filter by project ID",
    )
    sprint_id: str | None = Field(
        None,
        description="Filter by sprint ID",
    )
    priority: Literal["p0", "p1", "p2", "p3"] | None = Field(
        None,
        description="Filter by priority level",
    )
    assignee: str | None = Field(
        None,
        description="Filter by assignee",
    )
    limit: int = Field(
        50,
        ge=1,
        le=100,
        description="Maximum number of results (default: 50)",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of results to skip for pagination",
    )


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""

    task_id: str = Field(
        ...,
        pattern=r"^(T-|TASK-)[a-zA-Z0-9_-]+$",
        description="Task ID to mark as complete (required)",
    )
    actual_hours: float | None = Field(
        None,
        ge=0,
        description="Actual hours spent on the task",
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="Completion notes or summary",
    )


# =============================================================================
# Sprint Tool Input Schemas
# =============================================================================

class CreateSprintInput(BaseModel):
    """Input schema for create_sprint tool."""

    sprint_id: str = Field(
        ...,
        pattern=r"^S-[a-zA-Z0-9_-]+$",
        description="Sprint ID (format: S-xxx, e.g., S-2025-01)",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Sprint title (required)",
    )
    goal: str | None = Field(
        None,
        max_length=1000,
        description="Sprint goal or objective",
    )
    project_id: str | None = Field(
        None,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Associated project ID",
    )
    start_date: datetime | None = Field(
        None,
        description="Sprint start date (ISO 8601)",
    )
    end_date: datetime | None = Field(
        None,
        description="Sprint end date (ISO 8601)",
    )
    status: Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"] = Field(
        "new",
        description="Sprint status: new, pending, assigned, active, in_progress, blocked, completed, cancelled",
    )
    # Phase 2 Fields
    owner: str | None = Field(
        None,
        description="Sprint owner",
    )
    cadence: str | None = Field(
        None,
        description="Sprint cadence (weekly, biweekly, monthly)",
    )
    observability: dict | None = Field(
        None,
        description="Observability data",
    )
    task_ids: list[str] | None = Field(
        None,
        description="List of associated task IDs",
    )
    risks: list[dict] | None = Field(
        None,
        description="List of risk entries",
    )


class GetSprintInput(BaseModel):
    """Input schema for get_sprint tool."""

    sprint_id: str = Field(
        ...,
        pattern=r"^S-[a-zA-Z0-9_-]+$",
        description="Sprint ID to retrieve (required)",
    )


class UpdateSprintInput(BaseModel):
    """Input schema for update_sprint tool."""

    sprint_id: str = Field(
        ...,
        pattern=r"^S-[a-zA-Z0-9_-]+$",
        description="Sprint ID to update (required)",
    )
    title: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="New sprint title",
    )
    goal: str | None = Field(
        None,
        max_length=1000,
        description="New sprint goal",
    )
    status: Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"] | None = Field(
        None,
        description="New status: new, pending, assigned, active, in_progress, blocked, completed, cancelled",
    )
    start_date: datetime | None = Field(
        None,
        description="New start date",
    )
    end_date: datetime | None = Field(
        None,
        description="New end date",
    )
    # Phase 2 Fields
    owner: str | None = Field(
        None,
        description="New owner",
    )
    cadence: str | None = Field(
        None,
        description="New cadence",
    )
    observability: dict | None = Field(
        None,
        description="New observability data",
    )


class ListSprintsInput(BaseModel):
    """Input schema for list_sprints tool."""

    project_id: str | None = Field(
        None,
        description="Filter by project ID",
    )
    status: Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"] | None = Field(
        None,
        description="Filter by status",
    )
    limit: int = Field(
        20,
        ge=1,
        le=50,
        description="Maximum number of results (default: 20)",
    )


# =============================================================================
# Project Tool Input Schemas
# =============================================================================

class CreateProjectInput(BaseModel):
    """Input schema for create_project tool."""

    project_id: str = Field(
        ...,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Project ID (format: P-xxx)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name (required)",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="Project description",
    )
    owner: str | None = Field(
        None,
        description="Project owner/lead identifier",
    )
    status: Literal["discovery", "active", "paused", "closed"] = Field(
        "discovery",
        description="Project status",
    )
    target_end_date: datetime | None = Field(
        None,
        description="Target completion date",
    )
    tags: list[str] | None = Field(
        None,
        description="List of project tags",
    )
    # Phase 2 Fields
    mission: str | None = Field(
        None,
        description="Project mission statement",
    )
    vision: str | None = Field(
        None,
        description="Project vision statement",
    )
    roadmap_url: str | None = Field(
        None,
        description="URL to project roadmap",
    )
    observability: dict | None = Field(
        None,
        description="Observability data",
    )
    team_members: list[str] | None = Field(
        None,
        description="List of team member IDs",
    )


class GetProjectInput(BaseModel):
    """Input schema for get_project tool."""

    project_id: str = Field(
        ...,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Project ID to retrieve (required)",
    )


class UpdateProjectInput(BaseModel):
    """Input schema for update_project tool."""

    project_id: str = Field(
        ...,
        pattern=r"^P-[a-zA-Z0-9_-]+$",
        description="Project ID to update (required)",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="New project name",
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="New project description",
    )
    owner: str | None = Field(
        None,
        description="New project owner",
    )
    status: Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"] | None = Field(
        None,
        description="New project status",
    )
    target_end_date: datetime | None = Field(
        None,
        description="New target completion date",
    )
    tags: list[str] | None = Field(
        None,
        description="New list of project tags",
    )
    # Phase 2 Fields
    mission: str | None = Field(
        None,
        description="New project mission statement",
    )
    vision: str | None = Field(
        None,
        description="New project vision statement",
    )
    roadmap_url: str | None = Field(
        None,
        description="New URL to project roadmap",
    )
    observability: dict | None = Field(
        None,
        description="New observability data",
    )
    team_members: list[str] | None = Field(
        None,
        description="New list of team member IDs",
    )
class ListProjectsInput(BaseModel):
    """Input schema for list_projects tool."""

    status: Literal["new", "active", "completed", "cancelled"] | None = Field(
        None,
        description="Filter by project status",
    )
    owner: str | None = Field(
        None,
        description="Filter by project owner",
    )
    limit: int = Field(
        50,
        ge=1,
        le=100,
        description="Maximum number of results (default: 50)",
    )


# =============================================================================
# Export all schemas
# =============================================================================

__all__ = [
    # Task schemas
    "CreateTaskInput",
    "GetTaskInput",
    "UpdateTaskInput",
    "DeleteTaskInput",
    "ListTasksInput",
    "CompleteTaskInput",
    # Sprint schemas
    "CreateSprintInput",
    "GetSprintInput",
    "UpdateSprintInput",
    "ListSprintsInput",
    # Project schemas
    "CreateProjectInput",
    "GetProjectInput",
    "UpdateProjectInput",
    "ListProjectsInput",
]
