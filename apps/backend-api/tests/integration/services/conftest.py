import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from taskman_api.db.base import Base
from taskman_api.models.action_list import ActionList
from taskman_api.models.project import Project
from taskman_api.models.sprint import Sprint
from taskman_api.models.task import Task
from taskman_api.services.project_service import ProjectService
from taskman_api.services.sprint_service import SprintService
from taskman_api.services.task_service import TaskService

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
            await conn.execute(delete(Task))
            await conn.execute(delete(Sprint))
            await conn.execute(delete(Project))
            await conn.execute(delete(ActionList))
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


@pytest_asyncio.fixture(scope="function")
async def db_session(session_factory):
    """Create a database session for testing."""
    async with session_factory() as session:
        yield session
        # No need to commit/rollback here as the engine is disposed/cleared,
        # but explicit rollback is good practice for isolation if we reused the engine differently.
        await session.rollback()


@pytest.fixture(scope="function")
def project_service(db_session):
    return ProjectService(db_session)


@pytest.fixture(scope="function")
def sprint_service(db_session):
    return SprintService(db_session)


@pytest.fixture(scope="function")
def task_service(db_session):
    return TaskService(db_session)
