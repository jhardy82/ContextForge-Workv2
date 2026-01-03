"""Regression test fixtures.

Provides test client setup for regression tests using in-memory SQLite.
Pattern follows E2E tests with dependency override for test isolation.
Reference: E2E test fixes commit dde4b943
"""

import uuid
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
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create AsyncClient for regression testing with test database."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def sample_project(async_client: AsyncClient):
    """Create a sample project for tests that need project reference."""
    project_id = f"P-REG-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "id": project_id,
        "name": "Regression Test Project",
        "mission": "Support regression testing",
        "status": "active",
        "start_date": "2025-01-01",
        "owner": "test@example.com",
    }

    response = await async_client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201, f"Failed to create project: {response.text}"

    return response.json()


@pytest_asyncio.fixture
async def sample_sprint(async_client: AsyncClient, sample_project: dict):
    """Create a sample sprint for tests that need sprint reference."""
    sprint_id = f"S-REG-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "id": sprint_id,
        "name": "Regression Test Sprint",
        "goal": "Support regression testing",
        "cadence": "biweekly",
        "start_date": "2025-01-01",
        "end_date": "2025-01-14",
        "status": "planning",
        "owner": "test@example.com",
        "primary_project": sample_project["id"],
    }

    response = await async_client.post("/api/v1/sprints", json=payload)
    assert response.status_code == 201, f"Failed to create sprint: {response.text}"

    return response.json()
