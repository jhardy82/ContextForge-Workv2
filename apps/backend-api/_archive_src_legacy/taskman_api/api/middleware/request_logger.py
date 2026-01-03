"""Request logging middleware for FastAPI.

Logs all incoming HTTP requests and responses with structured metadata:
- Request ID generation and propagation
- Request method, path, query parameters
- Response status code and duration
- Client IP address
- User agent
- Request/response body sizes

Request IDs are generated for each request and added to response headers
for distributed tracing support.
"""

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from taskman_api.infrastructure.logging import (
    bind_request_context,
    clear_request_context,
    get_logger,
)

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses.

    Generates unique request IDs and logs request/response metadata
    in structured format for observability.

    Features:
    - Automatic request ID generation
    - Request/response logging with duration tracking
    - Context binding for all logs within request scope
    - Request ID propagation via X-Request-ID header
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize request logging middleware.

        Args:
            app: ASGI application instance
        """
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response from handler
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Get client information
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        # Bind request context for all logs in this request scope
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_host,
        )

        # Log incoming request
        logger.info(
            "request_started",
            query_params=dict(request.query_params),
            user_agent=user_agent,
        )

        # Track request processing time
        start_time = time.perf_counter()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers for client-side tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            logger.error(
                "request_failed",
                error_type=type(exc).__name__,
                error_message=str(exc),
                duration_ms=round(duration_ms, 2),
                exc_info=True,  # Include stack trace
            )

            # Re-raise to let error middleware handle it
            raise

        finally:
            # Clear request context to prevent leakage between requests
            clear_request_context()
