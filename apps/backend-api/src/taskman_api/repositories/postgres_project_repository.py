"""
Postgres Project Repository.

Specialized repository for PostgreSQL backend using optimized features.
"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.models.project import Project
from taskman_api.repositories.project_repository import ProjectRepository


class PostgresProjectRepository(ProjectRepository):
    """PostgreSQL implementation of Project Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def search_full_text(self, query_text: str, limit: int = 100) -> list[Project]:
        """
        Perform a full-text search on name and description using ILIKE.
        """
        pattern = f"%{query_text}%"
        stmt = select(Project).where(
            or_(
                Project.name.ilike(pattern),
                Project.description.ilike(pattern)
            )
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
