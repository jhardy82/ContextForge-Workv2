"""Performance test fixtures.

Provides database setup and utilities for performance tests.
"""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from taskman_api.db.base import Base
from taskman_api.models.action_list import ActionList


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session for performance tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
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
        await session.rollback()

    # Cleanup
    await engine.dispose()


@pytest.fixture
def action_list_factory():
    """Factory for creating ActionList instances."""
    counter = 0

    def _create(**kwargs):
        nonlocal counter
        counter += 1
        defaults = {
            "id": f"AL-PERF-{counter:04d}",
            "name": f"Perf Test List {counter}",
            "description": "Performance test",
            "status": "active",
            "owner": "perf-tester",
            "tags": [],
            "task_ids": [],
            "items": [],
        }
        return ActionList(**{**defaults, **kwargs})

    return _create
