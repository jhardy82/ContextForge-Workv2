"""Unit tests for ProjectRepository edge cases."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import ProjectStatus
from taskman_api.models.project import Project
from taskman_api.repositories.project_repository import ProjectRepository


@pytest.mark.asyncio
class TestProjectRepositoryEdgeCases:
    """Test suite for ProjectRepository edge cases."""

    async def test_exists(self, async_session: AsyncSession, sample_project):
        """Test exists check."""
        repo = ProjectRepository(async_session)
        async_session.add(sample_project)
        await async_session.commit()

        assert await repo.exists(sample_project.id) is True
        assert await repo.exists("NON-EXISTENT") is False

    async def test_get_by_owner(self, async_session: AsyncSession, sample_project):
        """Test getting projects by owner."""
        repo = ProjectRepository(async_session)
        sample_project.owner = "unique.owner"
        async_session.add(sample_project)

        # Add another project with different owner
        other_project = Project(
            id="P-OTHER-001",
            name="Other Project",
            status=ProjectStatus.ACTIVE,
            owner="other.owner",
            # Min required fields
            mission="mission",
            start_date="2025-01-01",
        )
        async_session.add(other_project)
        await async_session.commit()

        # Get by unique owner
        results = await repo.get_by_owner("unique.owner")
        assert len(results) == 1
        assert results[0].id == sample_project.id

        # Get by non-existent
        empty = await repo.get_by_owner("nobody")
        assert len(empty) == 0

    async def test_search_filters_and_pagination(self, async_session: AsyncSession):
        """Test search with combined filters and pagination."""
        repo = ProjectRepository(async_session)

        # Create 3 active projects owned by alice
        for i in range(3):
            p = Project(
                id=f"P-SEARCH-{i}",
                name=f"Project {i}",
                status=ProjectStatus.ACTIVE,
                owner="alice",
                mission="mission",
                start_date="2025-01-01",
            )
            await repo.create(p)

        # Create 1 draft project
        p_draft = Project(
            id="P-SEARCH-DRAFT",
            name="Draft Project",
            status=ProjectStatus.NEW,
            owner="alice",
            mission="mission",
            start_date="2025-01-01",
        )
        await repo.create(p_draft)

        # Search active by alice
        result, count = await repo.search(
            owner="alice", status=ProjectStatus.ACTIVE, limit=2, offset=0
        )
        assert len(result) == 2
        assert count == 3
        assert all(p.owner == "alice" for p in result)
        assert all(p.status == ProjectStatus.ACTIVE for p in result)

        # Pagination check
        result_page_2, _ = await repo.search(
            owner="alice", status=ProjectStatus.ACTIVE, limit=2, offset=2
        )
        assert len(result_page_2) == 1
        assert result_page_2[0].id == "P-SEARCH-2"

    async def test_create_project_method(self, async_session: AsyncSession):
        """Test explicit create_project helper."""
        repo = ProjectRepository(async_session)

        project = await repo.create_project(
            project_id="P-NEW-001",
            name="New Project",
            description="Created via helper",
            status="active",
            owner="creator",
        )

        assert project.id == "P-NEW-001"
        assert project.name == "New Project"
        assert project.status == "active"

        stored = await repo.get_by_id("P-NEW-001")
        assert stored is not None
        assert stored.name == "New Project"

    async def test_update_project_method(self, async_session: AsyncSession, sample_project):
        """Test explicit update_project helper."""
        repo = ProjectRepository(async_session)
        async_session.add(sample_project)
        await async_session.commit()

        updated = await repo.update_project(sample_project, name="Renamed Project", status="paused")

        assert updated.name == "Renamed Project"
        assert updated.status == "paused"
        # Ensure other fields untouched
        assert updated.owner == "test.owner"
