"""Prometheus metrics endpoint for TaskMan-v2 API.

Provides:
- /metrics: Prometheus metrics in text format

Fixes:
- M1: Rate limiting (10/minute) to prevent DoS attacks
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Import limiter for decorator pattern
from taskman_api.rate_limiter import limiter

router = APIRouter(tags=["metrics"])


@router.get("/metrics", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def metrics_endpoint(request: Request):  # noqa: ARG001
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    Rate limited to 10 requests per minute per IP.

    🔴 M1 FIX: Rate limiting prevents resource exhaustion attacks

    NOTE: Rate limiting is applied via @limiter.limit("10/minute") decorator.
    The Request parameter is required by slowapi for extracting client IP address.
    """

    return Response(
        content=generate_latest(),
        media_type=f"{CONTENT_TYPE_LATEST}; charset=utf-8",
    )
