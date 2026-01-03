"""Database session management and connection handling.

Implements SQLAlchemy 2.0 async patterns with proper lifecycle management:
- Single async engine per application
- Short-lived AsyncSession per request
- Dependency injection for FastAPI routes
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from taskman_api.config import get_settings

# Global engine instance (created once per application)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the global async engine.

    Engine is created once and reused throughout the application lifetime.
    Uses asyncpg driver for PostgreSQL.

    Returns:
        AsyncEngine instance configured from settings
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        # Build database URL from settings
        db_url = (
            f"postgresql+asyncpg://{settings.database.user}:{settings.database.password.get_secret_value()}"
            f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
        )

        # Engine configuration following SQLAlchemy 2.0 best practices
        engine_kwargs: dict[str, Any] = {
            "echo": settings.database.echo_sql,  # SQL logging (disabled in production)
            "pool_pre_ping": True,  # Verify connections before using
            "pool_size": settings.database.pool_size,
            "max_overflow": settings.database.max_overflow,
            "pool_timeout": 30,  # 30 second timeout for getting connection
            "pool_recycle": 3600,  # Recycle connections hourly (mitigates long-lived connection issues)
        }

        # Use NullPool for testing to avoid connection pool issues
        if settings.environment == "testing":
            engine_kwargs["poolclass"] = NullPool

        _engine = create_async_engine(db_url, **engine_kwargs)

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the global session factory.

    Session factory creates short-lived AsyncSession instances per request.
    Uses expire_on_commit=False to keep objects usable after commit.

    Returns:
        async_sessionmaker configured for the application
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Keep objects connected after commit
            autoflush=False,  # Explicit flush control
            autocommit=False,  # Explicit commit control
        )

    return _session_factory


# Convenience accessor for session factory
AsyncSessionLocal = get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Creates a new AsyncSession for each request and ensures proper cleanup.

    Usage:
        @router.get("/tasks/{task_id}")
        async def get_task(
            task_id: str,
            db: AsyncSession = Depends(get_db)
        ):
            # Use db session here
            task = await db.get(Task, task_id)
            return task

    Yields:
        AsyncSession instance that will be automatically closed
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection.

    Call this during application startup to verify database connectivity.
    Does NOT create tables - use Alembic migrations for that.
    """
    engine = get_engine()

    # Test connection
    async with engine.begin() as conn:
        await conn.execute("SELECT 1")  # type: ignore[arg-type]


async def close_db() -> None:
    """Close database connections.

    Call this during application shutdown to gracefully close all connections.
    """
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
