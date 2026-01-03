"""Pytest fixtures for repository tests.

Provides async database session and sample entities for testing.
"""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Imports moved inside fixtures to prevent early loading for coverage
# from taskman_api.core.enums ...
# from taskman_api.db.base ...
# from taskman_api.models ...


@pytest.fixture(scope="function")
async def async_session() -> AsyncSession:
    """Create async test database session.

    Uses in-memory SQLite for fast, isolated tests.
    """
    try:
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            poolclass=StaticPool,  # Share single connection for in-memory DB
            connect_args={"check_same_thread": False},  # Required for SQLite with async
            echo=False,
        )

        # Create all tables
        from taskman_api.db.base import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create session factory
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Yield session for tests
        async with session_factory() as session:
            yield session

        # Cleanup
        await engine.dispose()
    except Exception:
        import traceback

        traceback.print_exc()
        raise


@pytest.fixture
def sample_project() -> "Project":
    """Create sample project for testing."""
    from taskman_api.core.enums import ProjectStatus
    from taskman_api.models.project import Project

    return Project(
        id="P-TEST-001",
        name="Test Project",
        mission="Test project mission",
        status=ProjectStatus.ACTIVE,
        start_date="2025-01-01",  # Production uses strings for dates
        owner="test.owner",
        sponsors="[]",
        stakeholders="[]",
        repositories="[]",
        comms_channels='["#test-channel"]',
        okrs="[]",
        kpis="[]",
        roadmap="[]",
        risks="[]",
        assumptions="[]",
        constraints="[]",
        dependencies_external="[]",
        # sprints removed (not in model)
        related_projects="[]",
        shared_components="[]",
        compliance_requirements="[]",
        governance="{}",
        success_metrics="[]",
        mpv_policy="{}",
        # observability removed
    )


@pytest.fixture
def sample_sprint(sample_project: "Project") -> "Sprint":
    """Create sample sprint for testing."""
    from taskman_api.core.enums import SprintCadence, SprintStatus
    from taskman_api.models.sprint import Sprint

    return Sprint(
        id="S-TEST-001",
        name="Test Sprint 1",
        goal="Test sprint goal",
        cadence=SprintCadence.BIWEEKLY,
        start_date="2025-01-01",
        end_date="2025-01-14",
        status=SprintStatus.ACTIVE,
        owner="scrum.master",
        project_id=sample_project.id,
        # tasks removed (not in model)
        # imported_tasks removed
        related_projects="[]",
        # definition_of_done removed (not in model or checked)
        dependencies="{}",
        # scope_changes removed
        risks="[]",
        ceremonies="{}",
        # metrics removed
        # observability removed
    )


@pytest.fixture
def sample_task(sample_project: "Project", sample_sprint: "Sprint") -> "Task":
    """Create sample task for testing."""
    from taskman_api.core.enums import Priority, TaskStatus
    from taskman_api.models.task import Task

    return Task(
        id="T-TEST-001",
        title="Test Task",
        summary="Test task summary",
        description="Test task description",
        status=TaskStatus.NEW,
        owner="task.owner",
        assignees="[]",
        priority=Priority.P1,
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


@pytest.fixture
def sample_action_list() -> "ActionList":
    """Create sample action list for testing.

    ActionList uses 'name' not 'title', and 'task_ids' not 'items'.
    """
    from taskman_api.models.action_list import ActionList

    return ActionList(
        id="AL-TEST-001",
        name="Test Action List",  # 'name' not 'title'
        description="Test description",
        status="active",
        task_ids=[],  # List of task IDs
    )
