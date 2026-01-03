"""Health check endpoints for Kubernetes probes.

Provides three health check endpoints following Kubernetes best practices:

- GET /health/live - Liveness probe (is the app running?)
- GET /health/ready - Readiness probe (can the app serve traffic?)
- GET /health/startup - Startup probe (has initialization completed?)

These endpoints are designed for:
- Kubernetes liveness/readiness/startup probes
- Load balancer health checks
- Monitoring and alerting systems
- Service mesh health validation
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from taskman_api.db.session import get_session_factory
from taskman_api.infrastructure.health import HealthChecker
from taskman_api.infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global health checker instance (initialized at app startup)
_health_checker: HealthChecker | None = None


def get_health_checker() -> HealthChecker:
    """Get or create health checker instance.

    Returns:
        HealthChecker instance with database session factory

    Raises:
        RuntimeError: If session factory is not initialized
    """
    global _health_checker

    if _health_checker is None:
        session_factory = get_session_factory()
        if session_factory is None:
            raise RuntimeError("Database session factory not initialized")
        _health_checker = HealthChecker(session_factory)

    return _health_checker


@router.get(
    "/health/live",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="""
Kubernetes liveness probe endpoint.

Returns 200 if the application process is alive and responsive.
Kubernetes will restart the pod if this check fails repeatedly.

**Use case**: Detect and recover from application deadlocks or crashes.
""",
)
async def liveness_probe() -> JSONResponse:
    """Check if application is alive.

    This is the simplest health check - it verifies the process
    is running and can handle requests.

    Returns:
        JSONResponse with status "healthy" (always 200 unless process is dead)

    Example response:
        {
            "status": "healthy",
            "service": "taskman-api"
        }
    """
    checker = get_health_checker()
    is_alive = await checker.check_liveness()

    if is_alive:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "healthy", "service": "taskman-api"},
        )

    # This should never happen unless there's a critical error
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "unhealthy", "service": "taskman-api"},
    )


@router.get(
    "/health/ready",
    tags=["Health"],
    summary="Readiness probe",
    description="""
Kubernetes readiness probe endpoint.

Returns 200 if the application is ready to serve traffic.
Checks all critical dependencies (database, external services).

Returns 503 if any dependency is unavailable.
Kubernetes will remove the pod from service if this check fails.

**Use case**: Prevent traffic routing to pods that can't handle requests.
""",
)
async def readiness_probe() -> JSONResponse:
    """Check if application is ready to serve traffic.

    Validates all critical dependencies:
    - Database connectivity
    - Connection pool availability

    Returns:
        JSONResponse with detailed health status and component checks

    Responses:
        200: Application is ready (status: "healthy")
        503: Application is not ready (status: "unhealthy" or "degraded")

    Example response (healthy):
        {
            "status": "healthy",
            "timestamp": "2025-12-25T10:30:00Z",
            "checks": {
                "database": {
                    "status": "healthy",
                    "latency_ms": 5.23,
                    "responsive": true
                }
            },
            "duration_ms": 12.5
        }

    Example response (unhealthy):
        {
            "status": "unhealthy",
            "timestamp": "2025-12-25T10:30:00Z",
            "checks": {
                "database": {
                    "status": "unhealthy",
                    "latency_ms": 0.0,
                    "responsive": false,
                    "error": "Connection refused",
                    "error_type": "OperationalError"
                }
            },
            "duration_ms": 5002.3
        }
    """
    checker = get_health_checker()
    health_status = await checker.check_readiness()

    # Return 503 if unhealthy, 200 if healthy or degraded
    if health_status.status == "unhealthy":
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        http_status = status.HTTP_200_OK

    return JSONResponse(
        status_code=http_status,
        content={
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "checks": health_status.checks,
            "duration_ms": health_status.duration_ms,
        },
    )


@router.get(
    "/health/startup",
    tags=["Health"],
    summary="Startup probe",
    description="""
Kubernetes startup probe endpoint.

Returns 200 if the application has completed initialization.
Validates that all dependencies are ready and minimum uptime has elapsed.

Returns 503 during startup or if critical dependencies fail.
Kubernetes will not route traffic until this check succeeds.

**Use case**: Allow slow-starting applications to initialize before serving traffic.
""",
)
async def startup_probe() -> JSONResponse:
    """Check if application has completed startup.

    Validates:
    - Database is accessible
    - Minimum uptime has elapsed (prevents rapid restart loops)
    - All critical dependencies initialized

    Returns:
        JSONResponse with startup validation results

    Responses:
        200: Application startup complete (status: "healthy")
        503: Application still starting (status: "unhealthy")

    Example response (startup complete):
        {
            "status": "healthy",
            "timestamp": "2025-12-25T10:30:15Z",
            "checks": {
                "database": {
                    "status": "healthy",
                    "latency_ms": 4.12,
                    "responsive": true
                },
                "startup": {
                    "complete": true,
                    "uptime_seconds": 15.3,
                    "startup_time": "2025-12-25T10:30:00Z"
                }
            },
            "duration_ms": 8.2
        }
    """
    checker = get_health_checker()
    health_status = await checker.check_startup()

    # Return 503 if startup not complete or unhealthy
    if health_status.status == "unhealthy":
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        http_status = status.HTTP_200_OK

    return JSONResponse(
        status_code=http_status,
        content={
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "checks": health_status.checks,
            "duration_ms": health_status.duration_ms,
        },
    )


@router.get(
    "/health",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="Basic health check (deprecated)",
    description="""
Basic health check endpoint (legacy).

**Deprecated**: Use /health/live, /health/ready, or /health/startup instead.

This endpoint is maintained for backward compatibility but provides
minimal information. Prefer the specific probe endpoints.
""",
    deprecated=True,
)
async def basic_health_check() -> JSONResponse:
    """Basic health check (legacy endpoint).

    Returns:
        JSONResponse with basic status

    Example response:
        {
            "status": "healthy",
            "service": "taskman-api"
        }
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "service": "taskman-api"},
    )
