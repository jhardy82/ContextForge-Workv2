"""
Postgres Sprint Repository.

Specialized repository for PostgreSQL backend using optimized features.
"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.models.sprint import Sprint
from taskman_api.repositories.sprint_repository import SprintRepository


class PostgresSprintRepository(SprintRepository):
    """PostgreSQL implementation of Sprint Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def search_full_text(self, query_text: str, limit: int = 100) -> list[Sprint]:
        """
        Perform a full-text search on name and goal using ILIKE.
        """
        pattern = f"%{query_text}%"
        stmt = select(Sprint).where(
            or_(
                Sprint.name.ilike(pattern),
                Sprint.goal.ilike(pattern)
            )
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
