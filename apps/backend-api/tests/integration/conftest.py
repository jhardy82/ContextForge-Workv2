"""Integration test fixtures.

Provides database session and factories for integration tests.
"""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Imports moved inside fixtures to prevent early loading for coverage
# from taskman_api.core.enums ...
# from taskman_api.db.base ...
# from taskman_api.models ...


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session with transaction rollback.

    Uses in-memory SQLite for fast, isolated tests.
    Each test gets a fresh database.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
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
        await session.rollback()  # Rollback any changes

    # Cleanup
    await engine.dispose()


@pytest.fixture
def action_list_factory():
    """Factory for creating ActionList instances.

    Returns:
        Callable that creates ActionList with custom attributes
    """
    counter = 0
    from taskman_api.models.action_list import ActionList

    def _create(**kwargs):
        nonlocal counter
        counter += 1
        defaults = {
            "id": f"AL-TEST-{counter:04d}",
            "name": f"Test Action List {counter}",
            "description": "Test description",
            "status": "active",
            "owner": "test-owner",
            "tags": [],
            "task_ids": [],
            "items": [],
        }
        return ActionList(**{**defaults, **kwargs})

    return _create


@pytest.fixture
def task_factory():
    """Factory for creating Task instances.

    Returns:
        Callable that creates Task with custom attributes
    """
    counter = 0
    from taskman_api.core.enums import Priority, TaskStatus
    from taskman_api.models.task import Task

    def _create(**kwargs):
        nonlocal counter
        counter += 1
        defaults = {
            "id": f"T-TEST-{counter:04d}",
            "title": f"Test Task {counter}",
            "summary": "Test summary",
            "description": "Test description",
            "status": TaskStatus.NEW,
            "owner": "test-owner",
            "assignees": "[]",
            "priority": Priority.P2,
            "primary_project": None,
            "primary_sprint": None,
            "related_projects": "[]",
            "related_sprints": "[]",
            "parents": "[]",
            "depends_on": "[]",
            "blocks": "[]",
            "blockers": "[]",
            "acceptance_criteria": "[]",
            "definition_of_done": "[]",
            "quality_gates": "{}",
            "verification": "{}",
            "actions_taken": "[]",
            "labels": "[]",
            "related_links": "[]",
            "risks": "[]",
        }
        return Task(**{**defaults, **kwargs})

    return _create
