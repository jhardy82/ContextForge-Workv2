"""CLI State Container.

Holds shared state (Settings, Service, Output) for the CLI.
"""

from __future__ import annotations

import os
from pathlib import Path

from cf_core.cli.output import Output, get_output
from cf_core.config.settings import ContextForgeSettings, get_fresh_settings
from cf_core.services.taskman_service import TaskManService

# =============================================================================
# Service Factory
# =============================================================================


def _get_db_path(settings: ContextForgeSettings) -> str:
    """Get database path from settings or environment."""
    # Priority: env var > settings > default
    db_path = os.getenv("TASKMAN_DB_PATH")
    if db_path:
        return db_path

    if settings.database.url.get_secret_value():
        # Handle sqlite:/// URLs
        url = settings.database.url.get_secret_value()
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "")
        return url

    # Default path
    return "db/taskman.db"


def _create_service(settings: ContextForgeSettings) -> TaskManService:
    """Create TaskManService with repository dependencies.

    Supports both SQLite and PostgreSQL backends based on database URL.
    PostgreSQL URL format: postgresql://user:password@host:port/database
    SQLite URL format: sqlite:///path/to/database.db (or plain path)
    """
    db_url = settings.database.url.get_secret_value()

    # Determine if PostgreSQL or SQLite based on URL
    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        # Use PostgreSQL repositories
        from urllib.parse import urlparse

        from cf_core.repositories.connection import PostgresConnection
        from cf_core.repositories.project_repository import PostgresProjectRepository
        from cf_core.repositories.sprint_repository import PostgresSprintRepository
        from cf_core.repositories.task_repository import PostgresTaskRepository

        # Parse PostgreSQL connection string
        parsed = urlparse(db_url)
        connection = PostgresConnection(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            dbname=parsed.path.lstrip("/") if parsed.path else "contextforge",
            user=parsed.username or "contextforge",
            password=parsed.password or "",
        )

        # Create PostgreSQL repositories
        task_repo = PostgresTaskRepository(connection)
        sprint_repo = PostgresSprintRepository(connection)
        project_repo = PostgresProjectRepository(connection)
    else:
        # Use SQLite repositories (legacy/fallback)
        from cf_core.repositories.project_repository import SqliteProjectRepository
        from cf_core.repositories.sprint_repository import SqliteSprintRepository
        from cf_core.repositories.task_repository import SqliteTaskRepository

        db_path = _get_db_path(settings)

        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create repositories (they auto-create tables)
        task_repo = SqliteTaskRepository(db_path=db_path)
        sprint_repo = SqliteSprintRepository(db_path=db_path)
        project_repo = SqliteProjectRepository(db_path=db_path)

    # Create service with injected repositories
    return TaskManService(
        task_repository=task_repo,
        sprint_repository=sprint_repo,
        project_repository=project_repo,
    )


# =============================================================================
# State Container
# =============================================================================


class CLIState:
    """Container for CLI state shared across commands."""

    def __init__(self) -> None:
        self.settings: ContextForgeSettings = get_fresh_settings()
        self._service: TaskManService | None = None
        self._db_initialized: bool = False
        self._output: Output | None = None
        self._action_list_session_maker = None

    @property
    def service(self) -> TaskManService:
        """Lazy-initialize and return the TaskMan service."""
        if self._service is None:
            self._service = _create_service(self.settings)
        return self._service

    @property
    def output(self) -> Output:
        """Lazy-initialize and return the Output adapter."""
        if self._output is None:
            self._output = get_output(machine_mode=self.settings.machine_mode)
        return self._output

    def ensure_database(self) -> None:
        """Ensure database is initialized (triggers lazy service creation)."""
        if not self._db_initialized:
            _ = self.service  # Trigger lazy init
            self._db_initialized = True

    @property
    def action_list_session_maker(self):
        """Lazy-initialize and return the async session maker for ActionListService."""
        if self._action_list_session_maker is None:
            self._action_list_session_maker = _create_action_list_service(self.settings)
        return self._action_list_session_maker

    async def get_db_session(self):
        """Get a managed AsyncSession."""
        if not hasattr(self, "_session_maker") or self._session_maker is None:
            # Create engine and maker
            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            db_url = self.settings.database.url.get_secret_value()
            if "sqlite" in db_url:
                if "aiosqlite" not in db_url:
                    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
            else:
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

            self._db_engine = create_async_engine(db_url)
            self._session_maker = async_sessionmaker(self._db_engine, expire_on_commit=False)

        return self._session_maker()

    async def close(self):
        """Close all managed resources."""
        if hasattr(self, "_db_engine") and self._db_engine:
            await self._db_engine.dispose()
            self._db_engine = None


# Global state instance
state = CLIState()


# =============================================================================
# Async Support (Action List Service)
# =============================================================================


def _get_async_db_url(settings: ContextForgeSettings) -> str:
    """Get async database URL."""
    db_url = settings.database.url.get_secret_value()
    if db_url.startswith("sqlite:///"):
        # Convert sqlite:///path/to/db to sqlite+aiosqlite:///path/to/db
        return db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://")
    return db_url


def _create_action_list_service(settings: ContextForgeSettings):
    """Create ActionListService with async repository."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from cf_core.repositories.action_list_repository import ActionListRepository
    from cf_core.services.action_list_service import ActionListService

    db_url = _get_async_db_url(settings)
    engine = create_async_engine(db_url)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # We need a way to pass the session to the repository.
    # Since the repository takes a session in __init__, we normally would
    # create a session per request. For the CLI, we can create a single
    # service instance that creates sessions as needed, OR we can
    # instantiate the repository with a session per command.
    #
    # However, ActionListRepository takes `session` in __init__.
    # So we should probably handle the session lifecycle in the CLI command
    # or create a wrapper.
    #
    # For simplicity in this migration, we will expose the session_maker
    # on the state, and let the CLI commands create the service context.
    # But to match the synchronous `state.service` pattern, we might want
    # a ready-to-go service.
    #
    # Let's verify ActionListService dependencies.
    # It takes an ActionListRepository.
    # ActionListRepository takes an AsyncSession.
    #
    # We will attach the session_maker to the state, and the commands
    # will be responsible for creating the session and service,
    # OR we can make `state.action_list_service` property return a FACTORY
    # or simple context manager.

    return session_maker
