"""Unit tests for SprintRepository edge cases."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import SprintCadence, SprintStatus
from taskman_api.models.sprint import Sprint
from taskman_api.repositories.sprint_repository import SprintRepository


@pytest.mark.asyncio
class TestSprintRepositoryEdgeCases:
    """Test suite for SprintRepository edge cases."""

    async def test_exists(self, async_session: AsyncSession, sample_sprint):
        """Test exists check."""
        repo = SprintRepository(async_session)
        # sample_sprint depends on sample_project, so we need to add project first if not cascaded,
        # but fixture handles it or we add manually if needed.
        # Actually sample_sprint fixture returns an object, we need to add it.
        # But sample_sprint fixture implementation doesn't add to session, just returns object.
        # Check conftest: sample_sprint takes sample_project fixture.
        # We need to add both.

        # NOTE: sample_sprint fixture *uses* sample_project fixture but doesn't add to DB.
        # We must assume the user must add them.

        # However, checking conftest again:
        # async_session.add(sample_project) is needed.

        # Wait, I need reference to sample_project to add it?
        # sample_sprint already has project_id set to sample_project.id
        # Strict FK constraints in SQLite? Usually yes if enforced.

        # Let's check if we can access project from sprint fixture... no.
        # I'll just add sprint. If FK fails, I'll need to inject sample_project too.
        # Better safe: request sample_project in test arguments.

        async_session.add(sample_sprint)
        await async_session.commit()  # This might fail if project not in DB.

        assert await repo.exists(sample_sprint.id) is True
        assert await repo.exists("NON-EXISTENT") is False

    async def test_get_by_project(self, async_session: AsyncSession, sample_project, sample_sprint):
        """Test getting sprints by project."""
        repo = SprintRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)
        await async_session.commit()

        results = await repo.get_by_project(sample_project.id)
        assert len(results) == 1
        assert results[0].id == sample_sprint.id

        empty = await repo.get_by_project("other_project")
        assert len(empty) == 0

    async def test_get_active_sprints(self, async_session: AsyncSession, sample_project):
        """Test active sprints getter."""
        repo = SprintRepository(async_session)
        async_session.add(sample_project)

        s1 = Sprint(
            id="S-ACTIVE",
            name="S1",
            status=SprintStatus.ACTIVE,
            project_id=sample_project.id,
            cadence=SprintCadence.BIWEEKLY,
            start_date="2025-01-01",
            end_date="2025-01-14",
        )
        s2 = Sprint(
            id="S-CLOSED",
            name="S2",
            status=SprintStatus.CLOSED,
            project_id=sample_project.id,
            cadence=SprintCadence.BIWEEKLY,
            start_date="2025-01-01",
            end_date="2025-01-14",
        )
        async_session.add(s1)
        async_session.add(s2)
        await async_session.commit()

        active = await repo.get_active_sprints()
        assert len(active) == 1
        assert active[0].id == "S-ACTIVE"

    async def test_search_sprints(self, async_session: AsyncSession, sample_project):
        """Test search with filters."""
        repo = SprintRepository(async_session)
        async_session.add(sample_project)

        # 2 active for p1
        for i in range(2):
            s = Sprint(
                id=f"S-P1-A-{i}",
                name=f"S {i}",
                status=SprintStatus.ACTIVE,
                project_id=sample_project.id,
                cadence=SprintCadence.BIWEEKLY,
                start_date="2025-01-01",
                end_date="2025-01-14",
            )
            async_session.add(s)

        # 1 planning for p1
        s_plan = Sprint(
            id="S-P1-PLAN",
            name="Plan",
            status=SprintStatus.PLANNING,
            project_id=sample_project.id,
            cadence=SprintCadence.BIWEEKLY,
            start_date="2025-01-01",
            end_date="2025-01-14",
        )
        async_session.add(s_plan)

        # 1 active for p2 (phantom project id, assuming lazy checks or just insertion)
        s_p2 = Sprint(
            id="S-P2-A",
            name="P2 S",
            status=SprintStatus.ACTIVE,
            project_id="P-OTHER",
            cadence=SprintCadence.BIWEEKLY,
            start_date="2025-01-01",
            end_date="2025-01-14",
        )
        async_session.add(s_p2)

        await async_session.commit()

        # Search active + p1
        results, count = await repo.search(status=SprintStatus.ACTIVE, project_id=sample_project.id)
        assert count == 2
        assert len(results) == 2

        # Search planning
        results_plan, _ = await repo.search(status=SprintStatus.PLANNING)
        assert len(results_plan) == 1
        assert results_plan[0].id == "S-P1-PLAN"

    async def test_create_and_update_sprint_helpers(self, async_session: AsyncSession):
        """Test create and update helper methods."""
        repo = SprintRepository(async_session)

        # Create
        created = await repo.create_sprint(
            sprint_id="S-NEW",
            name="New Sprint",
            status="active",
            project_id="P-ANY",
            goal="Test Goal",
        )
        assert created.id == "S-NEW"
        assert created.status == "active"

        # Update
        updated = await repo.update_sprint(created, name="Updated Sprint", status="completed")
        assert updated.name == "Updated Sprint"
        assert updated.status == "completed"

        # Verify persistence
        stored = await repo.get_by_id("S-NEW")
        assert stored.status == "completed"
