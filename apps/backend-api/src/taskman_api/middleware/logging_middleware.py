"""
HTTP Request/Response Logging Middleware.

Provides structured JSON logging for all HTTP requests with:
- Request timing (X-Response-Time header)
- Correlation ID tracking (X-Request-ID header)
- Sensitive parameter redaction
- Configurable health endpoint exclusion

Environment Variables:
    TASKMAN_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    TASKMAN_LOG_HEALTH_ENDPOINTS: Set to "true" to include health checks in logs

Usage:
    from taskman_api.middleware import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)
"""

from __future__ import annotations

import os
import time
import uuid
from typing import TYPE_CHECKING

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint

# Configure module logger
logger = structlog.get_logger(__name__)

# Paths to exclude from verbose logging (health checks, metrics, etc.)
EXCLUDED_PATHS: frozenset[str] = frozenset({
    "/health",
    "/api/health",
    "/metrics",
    "/ready",
    "/live",
    "/",
})

# Query parameter keys to redact (case-insensitive matching)
SENSITIVE_QUERY_PARAMS: frozenset[str] = frozenset({
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "credential",
    "access_token",
    "refresh_token",
    "bearer",
})


def _should_log_path(path: str) -> bool:
    """Check if the path should be logged verbosely.

    Args:
        path: Request URL path

    Returns:
        True if path should be logged, False for excluded health endpoints
    """
    log_health = os.environ.get("TASKMAN_LOG_HEALTH_ENDPOINTS", "false").lower() == "true"
    if log_health:
        return True
    return path not in EXCLUDED_PATHS


def _redact_query_params(query_string: str) -> str:
    """Redact sensitive query parameters from the query string.

    Args:
        query_string: Raw query string from the URL

    Returns:
        Query string with sensitive values replaced by ***REDACTED***
    """
    if not query_string:
        return ""

    redacted_params = []
    for param in query_string.split("&"):
        if "=" in param:
            key, _value = param.split("=", 1)
            if key.lower() in SENSITIVE_QUERY_PARAMS:
                redacted_params.append(f"{key}=***REDACTED***")
            else:
                redacted_params.append(param)
        else:
            redacted_params.append(param)

    return "&".join(redacted_params)


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies.

    Checks X-Forwarded-For and X-Real-IP headers for proxied requests.

    Args:
        request: Starlette request object

    Returns:
        Client IP address string
    """
    # Check for proxy headers first (most proxies set these)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs: client, proxy1, proxy2
        # The first one is the original client
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct client connection
    if request.client:
        return request.client.host

    return "unknown"


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware for structured HTTP request/response logging.

    Features:
        - Generates or propagates X-Request-ID for correlation
        - Logs request start with method, path, query, client IP
        - Logs response with status code and duration in milliseconds
        - Adds X-Response-Time header to all responses
        - Redacts sensitive query parameters
        - Excludes health check endpoints from verbose logs (configurable)
        - Optional metrics callback for session tracking

    Environment Configuration:
        TASKMAN_LOG_LEVEL: Controls log verbosity
        TASKMAN_LOG_HEALTH_ENDPOINTS: "true" to log health checks

    Example Output:
        {"timestamp": "2025-12-27T12:00:00Z", "level": "info", "event": "http_request", ...}
        {"timestamp": "2025-12-27T12:00:00.150Z", "level": "info", "event": "http_response", ...}
    """

    # Class-level metrics callback - can be set by the application
    _metrics_callback: dict[str, int | float | None] | None = None

    @classmethod
    def set_metrics(cls, metrics: dict[str, int | float | None]) -> None:
        """Set the metrics dictionary to update on each request.

        Args:
            metrics: Dictionary with 'requests_processed' and 'errors_logged' keys
        """
        cls._metrics_callback = metrics

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the logging middleware.

        Args:
            app: The ASGI application to wrap
        """
        super().__init__(app)
        self._log_level = os.environ.get("TASKMAN_LOG_LEVEL", "INFO").upper()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and log timing information.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in the chain

        Returns:
            Response from the application with timing headers added
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Request-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Extract request metadata
        method = request.method
        path = request.url.path
        query_string = str(request.url.query) if request.url.query else ""
        redacted_query = _redact_query_params(query_string)
        client_ip = _get_client_ip(request)

        # Bind correlation ID to structlog context for this request
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Start timing
        start_time = time.perf_counter()

        # Log request start (if path is not excluded)
        should_log = _should_log_path(path)
        if should_log:
            logger.info(
                "http_request",
                method=method,
                path=path,
                query=redacted_query if redacted_query else None,
                correlation_id=correlation_id,
                client_ip=client_ip,
            )

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            logger.error(
                "http_request_error",
                method=method,
                path=path,
                correlation_id=correlation_id,
                duration_ms=round(duration_ms, 2),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add timing and correlation headers to response
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        response.headers["X-Request-ID"] = correlation_id

        # Update session metrics if callback is set
        if self._metrics_callback is not None:
            requests = self._metrics_callback.get("requests_processed")
            if isinstance(requests, int):
                self._metrics_callback["requests_processed"] = requests + 1
            if response.status_code >= 400:
                errors = self._metrics_callback.get("errors_logged")
                if isinstance(errors, int):
                    self._metrics_callback["errors_logged"] = errors + 1

        # Log response (if path is not excluded)
        if should_log:
            log_method = logger.info if response.status_code < 400 else logger.warning
            if response.status_code >= 500:
                log_method = logger.error

            log_method(
                "http_response",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                correlation_id=correlation_id,
            )

        return response
