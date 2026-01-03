"""Pytest fixtures for API integration tests.

Provides TestClient and database fixtures for E2E endpoint testing.
"""

import os

# Set environment variables BEFORE importing main module
# This is required because main.py calls get_settings() at module load time
os.environ.setdefault("APP_ENVIRONMENT", "testing")
os.environ.setdefault("APP_DATABASE__HOST", "localhost")
os.environ.setdefault("APP_DATABASE__PORT", "5433")
os.environ.setdefault("APP_DATABASE__USER", "taskman_test")
os.environ.setdefault("APP_DATABASE__PASSWORD", "test_password")
os.environ.setdefault("APP_DATABASE__DATABASE", "taskman_test")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-min-32-characters-for-testing")
os.environ.setdefault("APP_JWT_SECRET", "test-jwt-secret-min-32-characters-for-testing")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from taskman_api.db.base import Base
from taskman_api.dependencies import get_db_session
from taskman_api.main import app
from taskman_api.models.action_list import ActionList
from taskman_api.models.project import Project
from taskman_api.models.sprint import Sprint
from taskman_api.models.task import Task

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
        poolclass=StaticPool,  # Share single connection for in-memory DB
        connect_args={"check_same_thread": False},  # Required for SQLite with async
        echo=False,
    )

    # Create tables once if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Clear all data from tables BEFORE test runs (delete in reverse dependency order)
    async with engine.begin() as conn:
        try:
            # Core entities
            await conn.execute(delete(Task))
            await conn.execute(delete(Sprint))
            await conn.execute(delete(Project))
            await conn.execute(delete(ActionList))
            # State Store entities
            await conn.execute(delete(ConversationTurn))
            await conn.execute(delete(ConversationSession))
            await conn.execute(delete(Plan))
            await conn.execute(delete(Checklist))
        except Exception:
            # Tables might not exist on first run, ignore
            pass

    yield engine

    # Cleanup: dispose engine
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
    # Use global app instance (main.py does not have factory)
    app.dependency_overrides = {}

    # Override get_db_session dependency to use test session factory with commit
    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()  # Commit changes after successful request
            except Exception:
                await session.rollback()  # Rollback on error
                raise

    app.dependency_overrides[get_db_session] = override_get_db

    yield app

    # Cleanup overrides
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def client(test_app):
    """Create AsyncClient for API testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
