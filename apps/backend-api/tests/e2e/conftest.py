"""E2E test fixtures.

Provides test client and database setup for end-to-end tests.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Imports moved inside fixtures to prevent early loading for coverage
# from taskman_api.db.base ...
# from taskman_api.dependencies ...
# from taskman_api.main ...
# from taskman_api.models ...

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def async_test_engine():
    """Create async test database engine.

    Uses StaticPool to share connection across test.
    Tables created once and data is cleared BEFORE each test.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create tables
    from taskman_api.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Clear all data before test
    async with engine.begin() as conn:
        try:
            from taskman_api.models.action_list import ActionList
            from taskman_api.models.project import Project
            from taskman_api.models.sprint import Sprint
            from taskman_api.models.task import Task

            await conn.execute(delete(Task))
            await conn.execute(delete(Sprint))
            await conn.execute(delete(Project))
            await conn.execute(delete(ActionList))
        except Exception:
            pass

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
def session_factory(async_test_engine):
    """Create session factory for test database."""
    return async_sessionmaker(
        async_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(scope="function")
def test_app(session_factory):
    """Create test FastAPI application with test database."""
    from taskman_api.dependencies import get_db_session
    from taskman_api.main import app

    app.dependency_overrides = {}

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db
    yield app
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create AsyncClient for E2E testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
