"""Unit tests for TaskRepository.

Tests task-specific query methods.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.core.errors import NotFoundError
from taskman_api.core.result import Err, Ok
from taskman_api.models.task import Task
from taskman_api.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
class TestTaskRepository:
    """Test suite for TaskRepository specialized queries."""

    async def test_find_by_status(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by status."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with different statuses
        for i, status in enumerate([TaskStatus.NEW, TaskStatus.IN_PROGRESS, TaskStatus.NEW]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=status,
                owner="owner",
                assignees="[]",
                priority=Priority.P2,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        result = await repo.get_by_status(TaskStatus.NEW)

        # Assert
        # Repository returns list[Task], not Result[list[Task]]
        tasks = result
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.NEW for task in tasks)

    async def test_find_by_priority(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by priority."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with different priorities
        for i, priority in enumerate([Priority.P0, Priority.P1, Priority.P0]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=TaskStatus.NEW,
                owner="owner",
                assignees="[]",
                priority=priority,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act - Use search for priority
        tasks, count = await repo.search(priority=Priority.P0)

        # Assert
        assert count == 2
        assert len(tasks) == 2
        assert all(task.priority == Priority.P0 for task in tasks)

    async def test_find_by_owner(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by owner."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with different owners
        for i, owner in enumerate(["alice", "bob", "alice"]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=TaskStatus.NEW,
                owner=owner,
                assignees="[]",
                priority=Priority.P2,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act - Use search for owner
        tasks, count = await repo.search(owner="alice")

        # Assert
        assert count == 2
        assert len(tasks) == 2
        assert all(task.owner == "alice" for task in tasks)

    async def test_find_by_project(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by project."""
        # Arrange
        repo = TaskRepository(async_session)

        # Create second project

        from taskman_api.core.enums import ProjectStatus
        from taskman_api.models.project import Project

        project2 = Project(
            id="P-TEST-002",
            name="Project 2",
            mission="Mission 2",
            status=ProjectStatus.ACTIVE,
            start_date="2025-01-01",
            owner="owner",
            sponsors="[]",
            stakeholders="[]",
            repositories="[]",
            comms_channels="[]",
            okrs="[]",
            kpis="[]",
            roadmap="[]",
            risks="[]",
            assumptions="[]",
            constraints="[]",
            dependencies_external="[]",
            # sprints removed
            related_projects="[]",
            shared_components="[]",
            compliance_requirements="[]",
            governance="{}",
            success_metrics="[]",
            mpv_policy="{}",
            # observability removed
        )

        async_session.add(sample_project)
        async_session.add(project2)
        async_session.add(sample_sprint)

        # Create tasks for different projects
        for i, project_id in enumerate([sample_project.id, project2.id, sample_project.id]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=TaskStatus.NEW,
                owner="owner",
                assignees="[]",
                priority=Priority.P2,
                primary_project=project_id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        tasks = await repo.get_by_project(sample_project.id)

        # Assert
        assert len(tasks) == 2
        assert all(task.primary_project == sample_project.id for task in tasks)

    async def test_find_by_project_with_status_filter(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by project with status filter."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with different statuses
        for i, status in enumerate([TaskStatus.NEW, TaskStatus.IN_PROGRESS, TaskStatus.NEW]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=status,
                owner="owner",
                assignees="[]",
                priority=Priority.P2,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        # search supports project_id AND status
        tasks, count = await repo.search(project_id=sample_project.id, status=TaskStatus.NEW)

        # Assert
        assert count == 2
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.NEW for task in tasks)

    async def test_find_by_sprint(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by sprint."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks
        for i in range(3):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=TaskStatus.NEW,
                owner="owner",
                assignees="[]",
                priority=Priority.P2,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        tasks = await repo.get_by_sprint(sample_sprint.id)

        # Assert
        assert len(tasks) == 3

    async def test_find_by_status_and_priority(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding tasks by status and priority (composite index)."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with various combinations
        combos = [
            (TaskStatus.NEW, Priority.P0),
            (TaskStatus.NEW, Priority.P1),
            (TaskStatus.IN_PROGRESS, Priority.P0),
            (TaskStatus.NEW, Priority.P0),
        ]

        for i, (status, priority) in enumerate(combos):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=status,
                owner="owner",
                assignees="[]",
                priority=priority,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        tasks, count = await repo.search(status=TaskStatus.NEW, priority=Priority.P0)

        # Assert
        assert count == 2
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.NEW and task.priority == Priority.P0 for task in tasks)

    # test_find_blocked_tasks can be tested via search(status=BLOCKED) if BLOCKED is a status
    async def test_find_blocked_tasks(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding all blocked tasks."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks
        for i, status in enumerate([TaskStatus.BLOCKED, TaskStatus.NEW, TaskStatus.BLOCKED]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=status,
                owner="owner",
                assignees="[]",
                priority=Priority.P2,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act - using search
        tasks, count = await repo.search(status=TaskStatus.BLOCKED)

        # Assert
        assert count == 2
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.BLOCKED for task in tasks)

    # find_high_priority_tasks removed/skipped as it requires OR logic not in simple search
    async def test_find_high_priority_tasks(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test finding P0 and P1 (critical/high priority) tasks."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        # Create tasks with different priorities
        for i, priority in enumerate([Priority.P0, Priority.P1, Priority.P2, Priority.P0]):
            task = Task(
                id=f"T-TEST-{i:03d}",
                title=f"Task {i}",
                summary=f"Summary {i}",
                description=f"Description {i}",
                status=TaskStatus.NEW,
                owner="owner",
                assignees="[]",
                priority=priority,
                primary_project=sample_project.id,
                primary_sprint=sample_sprint.id,
                related_projects="[]",
                related_sprints="[]",
                parents="[]",
                depends_on="[]",
                blocks="[]",
                blockers="[]",
                acceptance_criteria="[]",
                definition_of_done="[]",
                quality_gates="{}",
                verification="{}",
                actions_taken="[]",
                labels="[]",
                related_links="[]",
                risks="[]",
                # observability removed
            )
            async_session.add(task)

        await async_session.commit()

        # Act
        tasks = await repo.find_high_priority_tasks()

        # Assert
        assert len(tasks) == 3
        assert all(task.priority in [Priority.P0, Priority.P1] for task in tasks)

    async def test_create_task_method(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test create_task method with convenient arguments."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)
        await async_session.commit()

        # Act
        task = await repo.create_task(
            id="T-CREATE-001",
            title="Created via Method",
            summary="Summary",
            description="Description",
            owner="creator",
            primary_project=sample_project.id,
            primary_sprint=sample_sprint.id,
            priority=Priority.P1,
            estimate_points=5.0,
        )

        # Assert
        assert task.id == "T-CREATE-001"
        assert task.title == "Created via Method"
        assert task.priority == Priority.P1
        assert task.estimate_points == 5.0

        # Verify persistence
        saved = await repo.get_by_id("T-CREATE-001")
        assert saved is not None
        assert saved.title == "Created via Method"

    async def test_update_task_method(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test update_task method with partial updates."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        task = Task(
            id="T-UPDATE-001",
            title="Original Title",
            summary="Original Summary",
            description="Desc",
            owner="owner",
            primary_project=sample_project.id,
            primary_sprint=sample_sprint.id,
            priority=Priority.P2,
        )
        async_session.add(task)
        await async_session.commit()

        # Act
        updated = await repo.update_task(
            task, title="New Title", priority=Priority.P0, estimate_points=8.0
        )

        # Assert
        assert updated.title == "New Title"
        assert updated.priority == Priority.P0
        assert updated.estimate_points == 8.0
        assert updated.summary == "Original Summary"  # Unchanged

    async def test_find_by_id_result_wrapper(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test find_by_id returning Result (Ok/Err)."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        task = Task(
            id="T-RESULT-001",
            title="Result Task",
            summary="Sum",
            description="Desc",
            owner="owner",
            primary_project=sample_project.id,
            primary_sprint=sample_sprint.id,
        )
        async_session.add(task)
        await async_session.commit()

        # Act - Success
        result_ok = await repo.find_by_id("T-RESULT-001")

        # Act - Failure
        result_err = await repo.find_by_id("NON-EXISTENT")

        # Assert
        assert isinstance(result_ok, Ok)
        assert result_ok.ok().id == "T-RESULT-001"

        assert isinstance(result_err, Err)
        assert isinstance(result_err.err(), NotFoundError)

    async def test_exists(
        self,
        async_session: AsyncSession,
        sample_project,
        sample_sprint,
    ):
        """Test exists method."""
        # Arrange
        repo = TaskRepository(async_session)
        async_session.add(sample_project)
        async_session.add(sample_sprint)

        task = Task(
            id="T-EXISTS-001",
            title="Exists Task",
            summary="Sum",
            description="Desc",
            owner="owner",
            primary_project=sample_project.id,
            primary_sprint=sample_sprint.id,
        )
        async_session.add(task)
        await async_session.commit()

        # Act & Assert
        assert await repo.exists("T-EXISTS-001") is True
        assert await repo.exists("NON-EXISTENT") is False
