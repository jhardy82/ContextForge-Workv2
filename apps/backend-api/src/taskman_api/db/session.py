"""
Database Session Management
Async SQLAlchemy 2.0 session factory and utilities.
"""

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.config import get_settings
from taskman_api.db.connection_manager import ConnectionManager

logger = structlog.get_logger()

# Load settings from central config
# Load settings from central config
settings = get_settings()
DATABASE_URL = settings.database.async_connection_string
SECONDARY_URL = (
    settings.secondary_database.async_connection_string if settings.secondary_database else None
)
SQLITE_PATH = settings.database.sqlite_path

# Initialize Connection Manager
manager = ConnectionManager(DATABASE_URL, SECONDARY_URL, SQLITE_PATH)

# Compatibility Shims
engine = manager.primary_engine

def AsyncSessionLocal():
    """
    Shim for legacy AsyncSessionLocal usage.
    Returns a session from the active engine (Primary or Fallback).
    Note: calling this bypasses the retry logic of manager.get_session(),
    but ensures basic compatibility for dependency injection.
    """
    if manager._using_fallback:
        return manager.FallbackSession()
    return manager.PrimarySession()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Delegates to ConnectionManager to provide resilient sessions.

    Usage:
        @router.get("/items")
        async def list_items(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async for session in manager.get_session():
        yield session


async def init_db(base_class: type | None = None) -> None:
    """
    Initialize database - create tables if they don't exist.
    Call this during application startup.
    Initializes both Primary and Fallback.
    """
    if base_class is None:
        from taskman_api.db.base import Base

        base_class = Base

    await manager.init_models(base_class)


async def check_db_health() -> dict:
    """
    Check database connectivity and return health status.

    Returns:
        dict with detailed connectivity info for both primary and fallback
    """
    return await manager.check_health()
