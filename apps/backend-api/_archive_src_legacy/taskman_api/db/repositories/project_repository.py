"""Project repository with project-specific queries.

Provides specialized queries for project management and filtering.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import ProjectStatus
from taskman_api.core.errors import DatabaseError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.project import Project

from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = ProjectRepository(session)
            projects = await repo.find_by_status(ProjectStatus.ACTIVE)
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize project repository.

        Args:
            session: Async database session
        """
        super().__init__(Project, session)

    async def find_by_status(
        self,
        status: ProjectStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Project], DatabaseError]:
        """Find projects by status.

        Args:
            status: Project status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of projects or error
        """
        try:
            stmt = (
                select(Project)
                .where(Project.status == status)
                .order_by(Project.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            projects = result.scalars().all()
            return Ok(projects)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find projects by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_by_owner(
        self,
        owner: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Project], DatabaseError]:
        """Find projects by owner.

        Args:
            owner: Owner username to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of projects or error
        """
        try:
            stmt = (
                select(Project)
                .where(Project.owner == owner)
                .order_by(Project.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            projects = result.scalars().all()
            return Ok(projects)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find projects by owner {owner}",
                    operation="find_by_owner",
                    details=str(e),
                )
            )

    async def find_active_projects(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Project], DatabaseError]:
        """Find all active projects.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of active projects or error
        """
        return await self.find_by_status(ProjectStatus.ACTIVE, limit, offset)

    async def find_by_date_range(
        self,
        start_after: date | None = None,
        start_before: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Project], DatabaseError]:
        """Find projects by start date range.

        Args:
            start_after: Filter for projects starting after this date
            start_before: Filter for projects starting before this date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of projects or error
        """
        try:
            stmt = select(Project)

            if start_after is not None:
                stmt = stmt.where(Project.start_date >= start_after)

            if start_before is not None:
                stmt = stmt.where(Project.start_date <= start_before)

            stmt = stmt.order_by(Project.start_date.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            projects = result.scalars().all()
            return Ok(projects)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find projects by date range",
                    operation="find_by_date_range",
                    details=str(e),
                )
            )

    async def find_by_sponsor(
        self,
        sponsor: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Project], DatabaseError]:
        """Find projects with specific sponsor.

        Args:
            sponsor: Sponsor name to filter by (searches sponsors JSON array)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of projects or error
        """
        try:
            # Note: This uses PostgreSQL JSON containment operator @>
            # For other databases, may need different syntax
            stmt = (
                select(Project)
                .where(Project.sponsors.contains([sponsor]))
                .order_by(Project.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            projects = result.scalars().all()
            return Ok(projects)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find projects by sponsor {sponsor}",
                    operation="find_by_sponsor",
                    details=str(e),
                )
            )

    async def find_with_sprints(
        self,
        project_id: str,
    ) -> Result[Project, NotFoundError | DatabaseError]:
        """Find project with eager-loaded sprints.

        Args:
            project_id: Project ID to find

        Returns:
            Result with project and loaded relationships or error
        """
        try:
            # Use the existing find_by_id from base, relationships are already configured
            return await self.find_by_id(project_id)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find project {project_id} with sprints",
                    operation="find_with_sprints",
                    details=str(e),
                )
            )
