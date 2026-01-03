from datetime import datetime
from typing import Any, List, Optional

from mcp.server.fastmcp import Context
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cf_mcp.db import get_db
from cf_mcp.models import Task
from cf_mcp.schemas import TaskCreate, TaskList, TaskResponse, TaskUpdate


async def _get_session(ctx: Context) -> AsyncSession:
    """Helper to get DB session from context or generator."""
    # FastMCP Context integration for dependency injection would be ideal here.
    # For now, we use the get_db generator directly.
    # In a full app, we might check ctx.request_context for an injected session.
    async for session in get_db():
        return session
    raise RuntimeError("Could not aquire database session")


def register_task_tools(mcp):
    """Register all task-related tools with the MCP server."""

    @mcp.tool()
    async def list_tasks(
        status: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> TaskList:
        """
        List tasks with optional filtering.
        """
        async for session in get_db():
            stmt = select(Task)

            # Apply filters
            if status:
                stmt = stmt.where(Task.status == status)
            if project_id:
                stmt = stmt.where(Task.project_id == project_id)
            if sprint_id:
                stmt = stmt.where(Task.sprint_id == sprint_id)
            if assignee:
                stmt = stmt.where(Task.assignee == assignee)

            # Count total (separate query for pagination)
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = (await session.execute(count_stmt)).scalar() or 0

            # Apply pagination
            stmt = stmt.limit(limit).offset(offset).order_by(Task.created_at.desc())

            result = await session.execute(stmt)
            tasks = result.scalars().all()

            return TaskList(
                items=[TaskResponse.model_validate(t) for t in tasks],
                total=total,
                limit=limit,
                offset=offset
            )

    @mcp.tool()
    async def create_task(
        title: str,
        description: str | None = None,
        project_id: str | None = None,
        priority: str = "medium",
        status: str = "new",
        sprint_id: str | None = None,
        story_points: int | None = None,
        assignee: str | None = None
    ) -> TaskResponse:
        """
        Create a new task.
        """
        async for session in get_db():
            # Create Pydantic model first for validation (if we had complex logic)
            # Here we map directly to ORM for speed in tool

            new_task = Task(
                title=title,
                description=description,
                project_id=project_id,
                priority=priority,
                status=status,
                sprint_id=sprint_id,
                story_points=story_points,
                assignee=assignee,
                # Set specific new fields that might need initialization
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            return TaskResponse.model_validate(new_task)

    @mcp.tool()
    async def get_task(task_id: str) -> str:
        """
        Retrieve a task by ID. Returns JSON string of task details.
        """
        async for session in get_db():
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return f"Task with ID {task_id} not found."

            # Return full Pydantic model dump
            return TaskResponse.model_validate(task).model_dump_json()

    @mcp.tool()
    async def update_task(
        task_id: str,
        title: str | None = None,
        status: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None
    ) -> str:
        """
        Update an existing task.
        """
        async for session in get_db():
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return f"Task {task_id} not found."

            # Update fields
            if title is not None: task.title = title
            if status is not None: task.status = status
            if description is not None: task.description = description
            if priority is not None: task.priority = priority
            if project_id is not None: task.project_id = project_id
            if sprint_id is not None: task.sprint_id = sprint_id

            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)
            return TaskResponse.model_validate(task).model_dump_json()

    @mcp.tool()
    async def delete_task(task_id: str) -> str:
        """
        Delete a task permanently.
        """
        async for session in get_db():
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return f"Task {task_id} not found."

            await session.delete(task)
            await session.commit()
            return f"Task {task_id} deleted successfully."
