"""Unit tests for ProjectRepository, SprintRepository, and ActionListRepository.

Consolidated test suite for remaining repository specialized queries.
Updated to use correct method names and direct return values (not Result monads).
Model fields verified against actual SQLAlchemy model definitions on 2025-12-28.
"""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import ProjectStatus, SprintStatus
from taskman_api.repositories.action_list_repository import ActionListRepository
from taskman_api.repositories.project_repository import ProjectRepository
from taskman_api.repositories.sprint_repository import SprintRepository


@pytest.mark.asyncio
class TestProjectRepository:
    """Test suite for ProjectRepository."""

    async def test_get_by_status(self, async_session: AsyncSession):
        """Test finding projects by status."""
        from taskman_api.models.project import Project

        repo = ProjectRepository(async_session)

        # Create projects with different statuses
        # Using only fields that exist in Project model
        for i, status in enumerate([ProjectStatus.ACTIVE, ProjectStatus.PAUSED, ProjectStatus.ACTIVE]):
            project = Project(
                id=f"P-TEST-{i:03d}",
                name=f"Project {i}",
                status=status,
                owner="owner",
                start_date=str(date(2025, 1, 1)),
            )
            async_session.add(project)

        await async_session.commit()

        # Use correct method name: get_by_status returns list directly
        projects = await repo.get_by_status(ProjectStatus.ACTIVE)
        assert isinstance(projects, list)
        assert len(projects) == 2

    async def test_get_active_projects(self, async_session: AsyncSession):
        """Test finding all active projects via get_by_status."""
        from taskman_api.models.project import Project

        repo = ProjectRepository(async_session)

        project = Project(
            id="P-ACTIVE-001",
            name="Active Project",
            status=ProjectStatus.ACTIVE,
            owner="owner",
            start_date=str(date(2025, 1, 1)),
        )
        async_session.add(project)
        await async_session.commit()

        # Use get_by_status with ACTIVE status
        projects = await repo.get_by_status(ProjectStatus.ACTIVE)
        assert isinstance(projects, list)
        assert len(projects) == 1
        assert projects[0].status == ProjectStatus.ACTIVE


@pytest.mark.asyncio
class TestSprintRepository:
    """Test suite for SprintRepository."""

    async def test_get_by_status(self, async_session: AsyncSession, sample_project):
        """Test finding sprints by status."""
        from taskman_api.models.sprint import Sprint

        async_session.add(sample_project)
        await async_session.commit()

        repo = SprintRepository(async_session)

        # Create sprints with different statuses
        # Using only fields that exist in Sprint model
        for i, status in enumerate(
            [SprintStatus.ACTIVE, SprintStatus.PLANNING, SprintStatus.ACTIVE]
        ):
            sprint = Sprint(
                id=f"S-TEST-{i:03d}",
                name=f"Sprint {i}",
                goal=f"Goal {i}",
                status=status,
                owner="owner",
                cadence="biweekly",
                project_id=sample_project.id,
                start_date=str(date(2025, 1, 1)),
                end_date=str(date(2025, 1, 14)),
            )
            async_session.add(sprint)

        await async_session.commit()

        # Use correct method name: get_by_status returns list directly
        sprints = await repo.get_by_status(SprintStatus.ACTIVE)
        assert isinstance(sprints, list)
        assert len(sprints) == 2

    async def test_get_active_sprints(self, async_session: AsyncSession, sample_project):
        """Test finding all active sprints."""
        from taskman_api.models.sprint import Sprint

        async_session.add(sample_project)
        await async_session.commit()

        repo = SprintRepository(async_session)

        sprint = Sprint(
            id="S-ACTIVE-001",
            name="Active Sprint",
            goal="Goal",
            status=SprintStatus.ACTIVE,
            owner="owner",
            cadence="biweekly",
            project_id=sample_project.id,
            start_date=str(date(2025, 1, 1)),
            end_date=str(date(2025, 1, 14)),
        )
        async_session.add(sprint)
        await async_session.commit()

        # Use correct method name: get_active_sprints returns list directly
        sprints = await repo.get_active_sprints()
        assert isinstance(sprints, list)
        assert len(sprints) == 1


@pytest.mark.asyncio
class TestActionListRepository:
    """Test suite for ActionListRepository."""

    async def test_get_active(self, async_session: AsyncSession):
        """Test finding active action lists."""
        from taskman_api.models.action_list import ActionList

        repo = ActionListRepository(async_session)

        # Create action lists with different statuses
        # Using only fields that exist in ActionList model: name (not title!)
        for i, status in enumerate(["active", "archived", "active"]):
            action_list = ActionList(
                id=f"AL-TEST-{i:03d}",
                name=f"List {i}",  # ActionList uses 'name', not 'title'
                status=status,
                task_ids=[],
            )
            async_session.add(action_list)

        await async_session.commit()

        # Use correct method name: get_active returns list directly
        lists = await repo.get_active()
        assert isinstance(lists, list)
        assert len(lists) == 2

    async def test_search_action_lists(self, async_session: AsyncSession):
        """Test searching action lists with filters."""
        from taskman_api.models.action_list import ActionList

        repo = ActionListRepository(async_session)

        # Create action list
        action_list = ActionList(
            id="AL-SEARCH-001",
            name="Search Test List",  # ActionList uses 'name', not 'title'
            status="active",
            task_ids=[],
        )
        async_session.add(action_list)
        await async_session.commit()

        # Use search method (returns tuple of list, count)
        lists, total = await repo.search(status="active")
        assert isinstance(lists, list)
        assert len(lists) == 1
        assert total == 1
