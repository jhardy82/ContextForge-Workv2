import contextlib
import logging
import os
import sqlite3
from collections.abc import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import psycopg2


class SQLiteConnection:
    """
    Context manager for SQLite connections.
    Ensures connections are properly closed and errors are handled.
    Applies standard PRAGMAs for performance and reliability.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextlib.contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Yields a managed SQLite connection.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=60.0)
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Use WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")
            # Use synchronous = NORMAL for better performance (with WAL)
            conn.execute("PRAGMA synchronous = NORMAL")

            conn.row_factory = sqlite3.Row # Access columns by name
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    pass
            raise e
        finally:
            if conn:
                conn.close()


logger = logging.getLogger(__name__)


class PostgresConnection:
    """
    Context manager for PostgreSQL connections.
    Ensures connections are properly closed and handles transactions.

    Supports two usage patterns:
    1. Context manager (preferred): with self.connect() as conn: ...
    2. Direct access (legacy): self.get_cursor(), self.commit(), self.rollback()
    """

    def __init__(
        self,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
    ) -> None:
        self.host = host or os.getenv("APP_DATABASE__HOST", "localhost")
        self.port = int(port or os.getenv("APP_DATABASE__PORT", "5434"))
        self.dbname = dbname or os.getenv("APP_DATABASE__DATABASE", "taskman_v2")
        self.user = user or os.getenv("APP_DATABASE__USER", "contextforge")
        self.password = password or os.getenv("APP_DATABASE__PASSWORD", "contextforge")
        self._direct_conn: psycopg2.connection | None = None

    @classmethod
    def from_env(cls) -> "PostgresConnection":
        """Create connection from environment variables."""
        return cls(
            host=os.getenv("APP_DATABASE__HOST", "localhost"),
            port=int(os.getenv("APP_DATABASE__PORT", "5434")),
            dbname=os.getenv("APP_DATABASE__DATABASE", "taskman_v2"),
            user=os.getenv("APP_DATABASE__USER", "contextforge"),
            password=os.getenv("APP_DATABASE__PASSWORD", "contextforge"),
        )

    @contextlib.contextmanager
    def connect(self) -> Generator["psycopg2.connection", None, None]:
        """
        Yields a managed PostgreSQL connection.
        """
        import psycopg2

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )
            yield conn
            conn.commit()
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.exception("PostgreSQL connection error: %s", e)
            raise
        finally:
            if conn:
                conn.close()

    # Legacy methods for compatibility with older repository implementations
    @contextlib.contextmanager
    def get_cursor(self):
        """
        Get a cursor from the direct connection (legacy support).
        Creates a persistent connection if one doesn't exist.
        """
        import psycopg2
        from psycopg2.extras import RealDictCursor

        if self._direct_conn is None or self._direct_conn.closed:
            self._direct_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )

        cursor = self._direct_conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

    def commit(self):
        """Commit the current transaction (legacy support)."""
        if self._direct_conn and not self._direct_conn.closed:
            self._direct_conn.commit()

    def rollback(self):
        """Rollback the current transaction (legacy support)."""
        if self._direct_conn and not self._direct_conn.closed:
            self._direct_conn.rollback()

    def close(self):
        """Close the direct connection (legacy support)."""
        if self._direct_conn and not self._direct_conn.closed:
            self._direct_conn.close()
            self._direct_conn = None
