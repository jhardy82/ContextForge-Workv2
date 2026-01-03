"""Health check endpoints for TaskMan-v2 API.

Provides:
- /health/telemetry: OpenTelemetry circuit breaker health check

Fixes:
- M3: Health check endpoint for OTLP backend connectivity
"""


from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from taskman_api.telemetry.circuit_breaker import circuit_breaker_exporter

router = APIRouter(prefix="/health", tags=["health"])


class TelemetryHealthResponse(BaseModel):
    """Response model for telemetry health check."""

    status: str  # "healthy" or "degraded"
    circuit_state: str  # "open" or "closed"
    otlp_backend: str  # "reachable" or "unreachable"
    last_success: str | None = None
    last_failure: str | None = None
    failure_count: int = 0


@router.get("/telemetry")
async def telemetry_health():
    """Health check endpoint for OpenTelemetry backend connectivity.

    Returns:
        200 OK: Circuit closed (healthy)
        503 Service Unavailable: Circuit open (degraded)

    🔴 M3 FIX: Health check endpoint for OTLP connectivity
    """
    state = circuit_breaker_exporter.get_state()

    if state == "closed":
        return TelemetryHealthResponse(
            status="healthy",
            circuit_state="closed",
            otlp_backend="reachable",
            last_success=(
                circuit_breaker_exporter.last_success_time.isoformat()
                if circuit_breaker_exporter.last_success_time
                else None
            ),
            failure_count=circuit_breaker_exporter.failure_count,
        )
    else:
        # Use JSONResponse for consistent serialization
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "circuit_state": "open",
                "otlp_backend": "unreachable",
                "last_failure": (
                    circuit_breaker_exporter.last_failure_time.isoformat()
                    if circuit_breaker_exporter.last_failure_time
                    else None
                ),
                "failure_count": circuit_breaker_exporter.failure_count,
            },
        )
