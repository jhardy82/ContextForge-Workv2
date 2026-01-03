"""
Project Repository.

Data access layer for Project entities.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.project import Project
from taskman_api.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entity operations."""

    model_class = Project

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists(self, entity_id: str) -> bool:
        """Check if project exists by ID."""
        result = await self.session.execute(
            select(func.count()).select_from(Project).where(Project.id == entity_id)
        )
        return (result.scalar() or 0) > 0

    async def get_by_status(self, status: str, limit: int = 100) -> list[Project]:
        """Get projects by status."""
        result = await self.session.execute(
            select(Project).where(Project.status == status).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_owner(self, owner: str, limit: int = 100) -> list[Project]:
        """Get projects by owner."""
        result = await self.session.execute(
            select(Project).where(Project.owner == owner).limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        status: str | None = None,
        owner: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Project], int]:
        """
        Search projects with filters.

        Returns: (projects, total_count)
        """
        query = select(Project)

        if status:
            query = query.where(Project.status == status)
        if owner:
            query = query.where(Project.owner == owner)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def create_project(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        status: str = "active",
        owner: str | None = None,
    ) -> Project:
        """Create a new project."""
        from datetime import datetime

        now = datetime.utcnow().isoformat()
        project = Project(
            id=project_id,
            name=name,
            description=description,
            status=status,
            owner=owner,
            created_at=now,
            updated_at=now,
        )
        return await self.create(project)

    async def update_project(
        self,
        project: Project,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        owner: str | None = None,
    ) -> Project:
        """Update project fields (only non-None values)."""
        from datetime import datetime

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if status is not None:
            project.status = status
        if owner is not None:
            project.owner = owner

        project.updated_at = datetime.utcnow().isoformat()
        return await self.update(project)

    # find_prefix methods returning Result for Service Layer
    async def find_by_id(self, entity_id: str) -> Result[Project, NotFoundError]:
        """Find project by ID with Result wrapper."""
        project = await self.get_by_id(entity_id)
        if project is None:
            return Err(
                NotFoundError(
                    message=f"Project not found: {entity_id}",
                    entity_id=entity_id,
                    entity_type="Project",
                )
            )
        return Ok(project)

    async def find_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Project], AppError]:
        """Find projects by status with Result wrapper."""
        try:
            projects, _ = await self.search(status=status, limit=limit, offset=offset)
            return Ok(projects)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def find_by_owner(
        self, owner: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Project], AppError]:
        """Find projects by owner with Result wrapper."""
        try:
            projects, _ = await self.search(owner=owner, limit=limit, offset=offset)
            return Ok(projects)
        except Exception as e:
            return Err(AppError(message=str(e)))
