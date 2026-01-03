"""cf_core database module.

Provides database connection and session management.
Wraps existing database implementations for unified access.
"""

from __future__ import annotations

from typing import Any

# Try to import from canonical locations
try:
    from python.cf_core.database import (
        get_db_connection,
        get_db_session,
    )
    HAS_DB_CONNECTION = True
except ImportError:
    HAS_DB_CONNECTION = False

    def get_db_connection() -> None:  # type: ignore[misc]
        """Stub for missing database connection."""
        return None

    def get_db_session() -> None:  # type: ignore[misc]
        """Stub for missing database session."""
        return None

try:
    from python.api.database import (
        SessionLocal as ApiSessionLocal,
        engine as api_engine,
    )
    HAS_API_DB = True
except ImportError:
    HAS_API_DB = False
    api_engine: Any = None
    ApiSessionLocal: Any = None


class DatabaseConnection:
    """Unified database connection manager.

    Provides a clean interface for database operations,
    abstracting the underlying connection implementation.

    Attributes:
        connection_string: Database connection URL
        engine: SQLAlchemy engine (if available)
    """

    def __init__(
        self,
        connection_string: str | None = None,
        use_api_db: bool = False,
    ) -> None:
        """Initialize database connection.

        Args:
            connection_string: Optional database URL
            use_api_db: Use the API database engine if available
        """
        self.connection_string = connection_string
        self._engine = None
        self._session_factory = None

        if use_api_db and HAS_API_DB:
            self._engine = api_engine
            self._session_factory = ApiSessionLocal

    @property
    def is_connected(self) -> bool:
        """Check if database connection is available."""
        return self._engine is not None

    def get_session(self):
        """Get a database session.

        Returns:
            Database session or None if not connected
        """
        if self._session_factory:
            return self._session_factory()
        return None

    def execute(self, query: str, params: dict | None = None) -> Any:
        """Execute a raw SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result
        """
        if not self.is_connected:
            raise ConnectionError("Database not connected")

        with self._engine.connect() as conn:
            result = conn.execute(query, params or {})
            return result


# Default connection instance
_default_connection: DatabaseConnection | None = None


def get_connection(
    connection_string: str | None = None,
    use_api_db: bool = True,
) -> DatabaseConnection:
    """Get or create a database connection.

    Args:
        connection_string: Optional connection URL
        use_api_db: Use API database if available

    Returns:
        DatabaseConnection instance
    """
    global _default_connection

    if connection_string:
        return DatabaseConnection(connection_string)

    if _default_connection is None:
        _default_connection = DatabaseConnection(use_api_db=use_api_db)

    return _default_connection


__all__ = [
    "DatabaseConnection",
    "get_connection",
    "HAS_DB_CONNECTION",
    "HAS_API_DB",
]
