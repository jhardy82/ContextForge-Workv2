"""
Sprint Repository.

Data access layer for Sprint entities.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.sprint import Sprint
from taskman_api.repositories.base import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    """Repository for Sprint entity operations."""

    model_class = Sprint

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists(self, entity_id: str) -> bool:
        """Check if sprint exists by ID."""
        result = await self.session.execute(
            select(func.count()).select_from(Sprint).where(Sprint.id == entity_id)
        )
        return (result.scalar() or 0) > 0

    async def get_by_status(self, status: str, limit: int = 100) -> list[Sprint]:
        """Get sprints by status."""
        result = await self.session.execute(
            select(Sprint).where(Sprint.status == status).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_project(self, project_id: str, limit: int = 100) -> list[Sprint]:
        """Get sprints by project ID."""
        result = await self.session.execute(
            select(Sprint).where(Sprint.project_id == project_id).limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_sprints(self, limit: int = 100) -> list[Sprint]:
        """Get all active sprints."""
        result = await self.session.execute(
            select(Sprint).where(Sprint.status == "active").limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        status: str | None = None,
        project_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Sprint], int]:
        """
        Search sprints with filters.

        Returns: (sprints, total_count)
        """
        query = select(Sprint)

        if status:
            query = query.where(Sprint.status == status)
        if project_id:
            query = query.where(Sprint.project_id == project_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def create_sprint(
        self,
        sprint_id: str,
        name: str,
        project_id: str | None = None,
        goal: str | None = None,
        status: str = "planning",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Sprint:
        """Create a new sprint."""
        from datetime import datetime

        now = datetime.utcnow().isoformat()
        sprint = Sprint(
            id=sprint_id,
            name=name,
            project_id=project_id,
            goal=goal,
            status=status,
            start_date=start_date,
            end_date=end_date,
            created_at=now,
            updated_at=now,
        )
        return await self.create(sprint)

    async def update_sprint(
        self,
        sprint: Sprint,
        name: str | None = None,
        goal: str | None = None,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Sprint:
        """Update sprint fields (only non-None values)."""
        from datetime import datetime

        if name is not None:
            sprint.name = name
        if goal is not None:
            sprint.goal = goal
        if status is not None:
            sprint.status = status
        if start_date is not None:
            sprint.start_date = start_date
        if end_date is not None:
            sprint.end_date = end_date

        sprint.updated_at = datetime.utcnow().isoformat()
        return await self.update(sprint)

    # find_prefix methods returning Result for Service Layer
    async def find_by_id(self, entity_id: str) -> Result[Sprint, NotFoundError]:
        """Find sprint by ID with Result wrapper."""
        sprint = await self.get_by_id(entity_id)
        if sprint is None:
            return Err(
                NotFoundError(
                    message=f"Sprint not found: {entity_id}",
                    entity_id=entity_id,
                    entity_type="Sprint",
                )
            )
        return Ok(sprint)

    async def find_by_project(
        self, project_id: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Sprint], AppError]:
        """Find sprints by project with Result wrapper."""
        try:
            sprints, _ = await self.search(project_id=project_id, limit=limit, offset=offset)
            return Ok(sprints)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def find_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Sprint], AppError]:
        """Find sprints by status with Result wrapper."""
        try:
            sprints, _ = await self.search(status=status, limit=limit, offset=offset)
            return Ok(sprints)
        except Exception as e:
            return Err(AppError(message=str(e)))
