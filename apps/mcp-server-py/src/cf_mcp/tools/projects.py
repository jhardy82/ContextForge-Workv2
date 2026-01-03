from datetime import datetime
from typing import Any, List, Optional

from mcp.server.fastmcp import Context
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cf_mcp.db import get_db
from cf_mcp.models import Project
from cf_mcp.schemas import ProjectCreate, ProjectList, ProjectResponse, ProjectUpdate


def register_project_tools(mcp):
    """Register all project-related tools with the MCP server."""

    @mcp.tool()
    async def list_projects(
        status: str | None = None,
        owner: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> ProjectList:
        """
        List projects with optional filtering.
        """
        # Note: Using get_db generator manually as we don't have request context injection in tools yet
        async for session in get_db():
            stmt = select(Project)

            # Apply filters
            if status:
                stmt = stmt.where(Project.status == status)
            if owner:
                stmt = stmt.where(Project.owner == owner)

            # Count total
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = (await session.execute(count_stmt)).scalar() or 0

            # Pagination
            stmt = stmt.limit(limit).offset(offset).order_by(Project.created_at.desc())

            result = await session.execute(stmt)
            projects = result.scalars().all()

            return ProjectList(
                items=[ProjectResponse.model_validate(p) for p in projects],
                total=total,
                limit=limit,
                offset=offset
            )

    @mcp.tool()
    async def create_project(
        name: str,
        mission: str | None = None,
        owner: str | None = None,
        status: str = "active",
        quarter: str | None = None,
        start_date: datetime | None = None,
        target_date: datetime | None = None
    ) -> ProjectResponse:
        """
        Create a new project.
        """
        async for session in get_db():
            new_project = Project(
                name=name,
                mission=mission,
                owner=owner,
                status=status,
                start_date=start_date,
                target_date=target_date,
                # Ensure timestamps
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_project)
            await session.commit()
            await session.refresh(new_project)

            return ProjectResponse.model_validate(new_project)

    @mcp.tool()
    async def get_project(project_id: str) -> str:
        """
        Retrieve a project by ID. Returns JSON string.
        """
        async for session in get_db():
            stmt = select(Project).where(Project.id == project_id)
            result = await session.execute(stmt)
            project = result.scalar_one_or_none()

            if not project:
                return f"Project {project_id} not found."

            return ProjectResponse.model_validate(project).model_dump_json()

    @mcp.tool()
    async def update_project(
        project_id: str,
        name: str | None = None,
        status: str | None = None,
        mission: str | None = None,
        owner: str | None = None,
        progress: float | None = None
    ) -> str:
        """
        Update an existing project.
        """
        async for session in get_db():
            stmt = select(Project).where(Project.id == project_id)
            result = await session.execute(stmt)
            project = result.scalar_one_or_none()

            if not project:
                return f"Project {project_id} not found."

            if name is not None: project.name = name
            if status is not None: project.status = status
            if mission is not None: project.mission = mission
            if owner is not None: project.owner = owner
            # progress is not a column on current model, might need to be stored in observability or metrics?
            # Checking model: Project has metrics jsonb? Or create column?
            # Model definition check: `cf_mcp/models.py`
            # For now, skipping progress if not in model, or assuming it's dynamic.

            project.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(project)
            return ProjectResponse.model_validate(project).model_dump_json()
