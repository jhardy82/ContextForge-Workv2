"""Health check infrastructure for Kubernetes probes and monitoring.

Implements three types of health checks following Kubernetes best practices:

1. **Liveness Probe** (/health/live)
   - Checks if the application is running
   - Returns 200 if the process is alive
   - Kubernetes will restart the pod if this fails

2. **Readiness Probe** (/health/ready)
   - Checks if the application can serve traffic
   - Validates database connectivity
   - Returns 200 when ready, 503 when not ready
   - Kubernetes will remove pod from service if this fails

3. **Startup Probe** (/health/startup)
   - Checks if the application has completed initialization
   - Validates all critical dependencies
   - Returns 200 when ready, 503 during startup
   - Kubernetes will not route traffic until this succeeds

Usage:
    from taskman_api.infrastructure.health import HealthChecker

    checker = HealthChecker(db_session_factory)

    # Liveness check
    is_alive = await checker.check_liveness()

    # Readiness check with detailed status
    status = await checker.check_readiness()
"""

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from taskman_api.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Health check result with detailed component status.

    Attributes:
        status: Overall health status (healthy/degraded/unhealthy)
        timestamp: ISO 8601 timestamp of check
        checks: Dict of component check results
        duration_ms: Time taken to perform health checks
    """

    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: str
    checks: dict[str, dict[str, Any]]
    duration_ms: float


class HealthChecker:
    """Health check manager for application dependencies.

    Performs health checks on critical application components:
    - Database connectivity and query performance
    - Application startup state

    Attributes:
        session_factory: SQLAlchemy async session factory for database checks
        startup_time: Application startup timestamp
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        startup_time: datetime | None = None,
    ) -> None:
        """Initialize health checker.

        Args:
            session_factory: Async session factory for database checks
            startup_time: Application startup timestamp (defaults to now)
        """
        self.session_factory = session_factory
        self.startup_time = startup_time or datetime.now(UTC)

    async def check_liveness(self) -> bool:
        """Check if application is alive (liveness probe).

        This is the simplest health check - it just verifies the process
        is running and can execute code.

        Returns:
            True if application is alive

        Example:
            is_alive = await checker.check_liveness()
            # Returns: True (always, unless process is dead)
        """
        return True

    async def check_database(self) -> dict[str, Any]:
        """Check database connectivity and performance.

        Executes a simple SELECT 1 query to verify:
        - Database is reachable
        - Connection pool has available connections
        - Query can be executed successfully

        Returns:
            Dict with status, latency, and optional error details

        Example:
            result = await checker.check_database()
            # Returns: {
            #     "status": "healthy",
            #     "latency_ms": 5.23,
            #     "responsive": True
            # }
        """
        start_time = time.perf_counter()
        check_result: dict[str, Any] = {
            "status": "unhealthy",
            "latency_ms": 0.0,
            "responsive": False,
        }

        try:
            async with self.session_factory() as session:
                # Execute simple query with 5 second timeout
                result = await session.execute(text("SELECT 1"))
                result.scalar()

                # Calculate latency
                latency_ms = (time.perf_counter() - start_time) * 1000
                check_result["latency_ms"] = round(latency_ms, 2)
                check_result["responsive"] = True

                # Determine status based on latency
                if latency_ms < 100:
                    check_result["status"] = "healthy"
                elif latency_ms < 1000:
                    check_result["status"] = "degraded"
                    check_result["warning"] = f"High latency: {latency_ms:.2f}ms"
                else:
                    check_result["status"] = "unhealthy"
                    check_result["error"] = f"Excessive latency: {latency_ms:.2f}ms"

                logger.info(
                    "database_health_check",
                    status=check_result["status"],
                    latency_ms=latency_ms,
                )

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000
            check_result["latency_ms"] = round(latency_ms, 2)
            check_result["error"] = str(exc)
            check_result["error_type"] = type(exc).__name__

            logger.error(
                "database_health_check_failed",
                error_type=type(exc).__name__,
                error_message=str(exc),
                exc_info=True,
            )

        return check_result

    async def check_readiness(self) -> HealthStatus:
        """Check if application is ready to serve traffic (readiness probe).

        Performs comprehensive checks of all critical dependencies:
        - Database connectivity

        Returns:
            HealthStatus with overall status and component details

        Example:
            status = await checker.check_readiness()
            # Returns: HealthStatus(
            #     status="healthy",
            #     timestamp="2025-12-25T10:30:00Z",
            #     checks={"database": {"status": "healthy", ...}},
            #     duration_ms=12.5
            # )
        """
        start_time = time.perf_counter()

        # Run health checks
        db_check = await self.check_database()

        # Determine overall status
        overall_status: Literal["healthy", "degraded", "unhealthy"]
        if db_check["status"] == "healthy":
            overall_status = "healthy"
        elif db_check["status"] == "degraded":
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # Calculate total duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now(UTC).isoformat(),
            checks={
                "database": db_check,
            },
            duration_ms=round(duration_ms, 2),
        )

    async def check_startup(self) -> HealthStatus:
        """Check if application has completed startup (startup probe).

        Validates:
        - Database is accessible
        - Minimum startup time has elapsed (prevents rapid restarts)

        Returns:
            HealthStatus with startup validation results

        Example:
            status = await checker.check_startup()
            # Returns: HealthStatus(
            #     status="healthy",
            #     timestamp="2025-12-25T10:30:00Z",
            #     checks={
            #         "database": {...},
            #         "startup": {"complete": True, "uptime_seconds": 15.3}
            #     },
            #     duration_ms=8.2
            # )
        """
        start_time = time.perf_counter()

        # Check database
        db_check = await self.check_database()

        # Check uptime (must be up for at least 2 seconds)
        uptime_seconds = (datetime.now(UTC) - self.startup_time).total_seconds()
        startup_complete = uptime_seconds >= 2.0 and db_check["responsive"]

        startup_check = {
            "complete": startup_complete,
            "uptime_seconds": round(uptime_seconds, 2),
            "startup_time": self.startup_time.isoformat(),
        }

        # Determine overall status
        if startup_complete and db_check["status"] == "healthy":
            overall_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
        elif startup_complete and db_check["status"] == "degraded":
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        duration_ms = (time.perf_counter() - start_time) * 1000

        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now(UTC).isoformat(),
            checks={
                "database": db_check,
                "startup": startup_check,
            },
            duration_ms=round(duration_ms, 2),
        )
