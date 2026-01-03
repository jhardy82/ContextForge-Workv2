"""
Database Connection Manager.

Implements the Dual-Database Architecture pattern (Primary: PostgreSQL, Fallback: SQLite).
Provides resilient session management and health checking.
"""

import os
from collections.abc import AsyncGenerator

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

logger = structlog.get_logger()


class ConnectionManager:
    """
    Manages connections to Primary (Postgres), Secondary (Cloud Postgres), and Fallback (SQLite).
    Implements a 3-Tier Circuit Breaker pattern for maximum resilience.
    """

    def __init__(
        self, primary_url: str, secondary_url: str | None, sqlite_path: str = "taskman.db"
    ):
        self.primary_url = self._fix_async_url(primary_url)
        self.secondary_url = self._fix_async_url(secondary_url) if secondary_url else None
        self.sqlite_url = f"sqlite+aiosqlite:///{sqlite_path}"
        self.sqlite_path = sqlite_path

        # 1. Initialize Primary Engine
        self.primary_engine = self._create_postgres_engine(self.primary_url)

        # 2. Initialize Secondary Engine (if configured)
        self.secondary_engine = None
        if self.secondary_url:
            self.secondary_engine = self._create_postgres_engine(self.secondary_url)

        # 3. Initialize Fallback Engine
        self.fallback_engine = create_async_engine(
            self.sqlite_url,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            connect_args={"check_same_thread": False, "timeout": 60},
            poolclass=NullPool,
        )

        # Enable WAL mode for SQLite
        from sqlalchemy import event

        @event.listens_for(self.fallback_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        # Session Factories
        self.PrimarySession = async_sessionmaker(
            self.primary_engine, expire_on_commit=False, autoflush=False
        )
        self.SecondarySession = None
        if self.secondary_engine:
            self.SecondarySession = async_sessionmaker(
                self.secondary_engine, expire_on_commit=False, autoflush=False
            )
        self.FallbackSession = async_sessionmaker(
            self.fallback_engine, expire_on_commit=False, autoflush=False
        )

        # State tracking: "primary", "secondary", "fallback"
        self._active_tier = "primary"

    def _create_postgres_engine(self, url: str):
        """Helper to create configured Postgres engine."""
        connect_args = {}
        # Add SSL if not local
        if "localhost" not in url and "127.0.0.1" not in url:
            import ssl

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ctx

        return create_async_engine(
            url,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=connect_args,
        )

    @staticmethod
    def _fix_async_url(url: str) -> str:
        """Ensure URL uses an async driver."""
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    async def check_health(self) -> dict:
        """Check health of all databases and update active tier."""
        import time

        status = {
            "mode": self._active_tier,
            "primary": {"connected": False, "latency_ms": None, "error": None},
            "secondary": {"connected": False, "latency_ms": None, "error": None},
            "fallback": {"connected": False, "latency_ms": None, "error": None},
        }

        # Check Primary
        try:
            start = time.perf_counter()
            async with self.PrimarySession() as session:
                await session.execute(text("SELECT 1"))
                status["primary"]["connected"] = True
                status["primary"]["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        except Exception as e:
            status["primary"]["error"] = str(e)
            logger.error("primary_health_check_failed", error=str(e))

        # Check Secondary
        if self.SecondarySession:
            try:
                start = time.perf_counter()
                async with self.SecondarySession() as session:
                    await session.execute(text("SELECT 1"))
                    status["secondary"]["connected"] = True
                    status["secondary"]["latency_ms"] = round(
                        (time.perf_counter() - start) * 1000, 2
                    )
            except Exception as e:
                status["secondary"]["error"] = str(e)
                logger.error("secondary_health_check_failed", error=str(e))
        else:
            status["secondary"]["error"] = "Not Configured"

        # Check Fallback
        try:
            start = time.perf_counter()
            async with self.FallbackSession() as session:
                await session.execute(text("SELECT 1"))
                status["fallback"]["connected"] = True
                status["fallback"]["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        except Exception as e:
            status["fallback"]["error"] = str(e)
            logger.error("fallback_health_check_failed", error=str(e))

        # Determine Active Tier
        if status["primary"]["connected"]:
            self._active_tier = "primary"
        elif status["secondary"]["connected"]:
            if self._active_tier != "secondary":
                logger.warning("failed_over_to_secondary")
            self._active_tier = "secondary"
        elif status["fallback"]["connected"]:
            if self._active_tier != "fallback":
                logger.warning("failed_over_to_fallback")
            self._active_tier = "fallback"
        else:
            self._active_tier = "none"
            logger.critical("all_databases_down")

        status["mode"] = self._active_tier
        return status

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yields a database session from the active tier."""

        # Determine session factory based on current state optimization
        session_factory = self.PrimarySession
        if self._active_tier == "secondary" and self.SecondarySession:
            session_factory = self.SecondarySession
        elif self._active_tier == "fallback":
            session_factory = self.FallbackSession

        try:
            async with session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
        except Exception as e:
            # If current tier failed, try to adapt
            if session_factory == self.PrimarySession:
                logger.warning("primary_failed_trying_secondary", error=str(e))
                # Try Secondary
                if self.SecondarySession:
                    try:
                        async with self.SecondarySession() as session:
                            self._active_tier = "secondary"
                            yield session
                            await session.commit()
                            return
                    except Exception as sec_e:
                        logger.warning("secondary_failed_trying_fallback", error=str(sec_e))

                # Try Fallback
                self._active_tier = "fallback"
                async with self.FallbackSession() as session:
                    yield session
                    await session.commit()

            elif session_factory == self.SecondarySession:
                logger.warning("secondary_failed_trying_fallback", error=str(e))
                self._active_tier = "fallback"
                async with self.FallbackSession() as session:
                    yield session
                    await session.commit()

            else:
                logger.error("all_tiers_failed", error=str(e))
                raise e

    async def init_models(self, base_class):
        """Initialize tables in all databases."""
        # Primary
        try:
            async with self.primary_engine.begin() as conn:
                await conn.run_sync(base_class.metadata.create_all)
            logger.info("primary_db_initialized")
        except Exception as e:
            logger.warning("primary_db_init_failed", error=str(e))

        # Secondary
        if self.secondary_engine:
            try:
                async with self.secondary_engine.begin() as conn:
                    await conn.run_sync(base_class.metadata.create_all)
                logger.info("secondary_db_initialized")
            except Exception as e:
                logger.warning("secondary_db_init_failed", error=str(e))

        # Fallback
        try:
            async with self.fallback_engine.begin() as conn:
                await conn.run_sync(base_class.metadata.create_all)
            logger.info("fallback_db_initialized")
        except Exception as e:
            logger.error("fallback_db_init_failed", error=str(e))

    @property
    def _using_fallback(self):
        """Legacy property for compatibility."""
        return self._active_tier == "fallback"
