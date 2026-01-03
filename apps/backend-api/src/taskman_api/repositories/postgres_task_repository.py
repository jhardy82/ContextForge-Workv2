"""
Postgres Task Repository.

Specialized repository for PostgreSQL backend using optimized features.
"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.models.task import Task
from taskman_api.repositories.task_repository import TaskRepository


class PostgresTaskRepository(TaskRepository):
    """PostgreSQL implementation of Task Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def search_full_text(self, query_text: str, limit: int = 100) -> tuple[list[Task], int]:
        """
        Perform a full-text search on title and description using ILIKE.

        This enables case-insensitive search which is not available
        in standard SQL LIKE without lower() functions.
        """
        pattern = f"%{query_text}%"
        stmt = (
            select(Task)
            .where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        tasks = list(result.scalars().all())
        return tasks, len(tasks)
