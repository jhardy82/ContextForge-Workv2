"""Structured logging configuration using structlog.

Provides JSON-formatted logs for production with human-readable console logs
for development. Integrates with Python's standard logging module.

Features:
- JSONL output format for production log aggregation
- Human-readable colored console output for development
- Request ID propagation for distributed tracing
- Automatic exception formatting with stack traces
- Sensitive data sanitization (passwords, tokens, API keys)
- Context binding for structured metadata

Usage:
    from taskman_api.infrastructure.logging import configure_logging, get_logger

    # Configure at application startup
    configure_logging()

    # Get logger instance
    logger = get_logger(__name__)

    # Log with structured context
    logger.info("user_created", user_id="U-12345", email="user@example.com")

    # Bind context for multiple log entries
    log = logger.bind(request_id="req-abc123")
    log.info("processing_request")
    log.info("request_completed", duration_ms=125)
"""

import logging
import sys
from typing import Any, cast

import structlog
from structlog.types import EventDict, Processor

from taskman_api.config import get_settings

# Sensitive field patterns to sanitize in logs
SENSITIVE_PATTERNS = {
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
    "private_key",
    "access_key",
}


def sanitize_sensitive_data(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Sanitize sensitive data from log entries.

    Replaces values for keys matching sensitive patterns with '***REDACTED***'.

    Args:
        _logger: Logger instance (unused, required by structlog processor signature)
        _method_name: Log method name (unused, required by structlog processor signature)
        event_dict: Log event dictionary to sanitize

    Returns:
        EventDict with sensitive values redacted
    """
    for key in event_dict:
        key_lower = str(key).lower()
        if any(pattern in key_lower for pattern in SENSITIVE_PATTERNS):
            event_dict[key] = "***REDACTED***"

    return event_dict


def add_app_context(
    _logger: logging.Logger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Add application-wide context to all log entries.

    Args:
        _logger: Logger instance (unused, required by structlog processor signature)
        _method_name: Log method name (unused, required by structlog processor signature)
        event_dict: Log event dictionary to enhance

    Returns:
        EventDict with application context added
    """
    settings = get_settings()

    event_dict["app_name"] = settings.app_name
    event_dict["environment"] = settings.environment

    return event_dict


def configure_logging(log_level: str | None = None) -> None:
    """Configure structured logging for the application.

    Sets up structlog with appropriate processors for the environment:
    - Development: Human-readable colored console output
    - Production: JSON Lines (JSONL) format for log aggregation

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, uses DEBUG for dev/test, INFO for staging/prod.

    Example:
        # Configure with default settings
        configure_logging()

        # Override log level
        configure_logging(log_level="DEBUG")
    """
    settings = get_settings()

    # Determine log level
    if log_level is None:
        log_level = (
            "DEBUG"
            if settings.environment in ("development", "testing")
            else "INFO"
        )

    # Convert string to logging level constant
    numeric_level = getattr(logging, log_level.upper())

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Common processors for all environments
    common_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,  # Add context variables
        structlog.stdlib.add_log_level,  # Add log level
        structlog.stdlib.add_logger_name,  # Add logger name
        structlog.processors.TimeStamper(fmt="iso", utc=True),  # ISO 8601 timestamps
        structlog.processors.StackInfoRenderer(),  # Render stack info
        add_app_context,  # Add app name and environment
        sanitize_sensitive_data,  # Redact sensitive values
    ]

    # Environment-specific processors
    if settings.environment in ("development", "testing"):
        # Development: human-readable colored console output (no format_exc_info to avoid conflict)
        processors: list[Processor] = common_processors + [
            structlog.dev.ConsoleRenderer(colors=True),  # Colored console output with exception rendering
        ]
    else:
        # Production: JSON Lines format for log aggregation
        processors = common_processors + [
            structlog.processors.format_exc_info,  # Format exceptions as strings
            structlog.processors.JSONRenderer(),  # JSON output
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module.
              If None, uses the root logger.

    Returns:
        BoundLogger instance with configured processors

    Example:
        logger = get_logger(__name__)
        logger.info("operation_started", operation_id="OP-123")

        # Bind context for multiple log entries
        log = logger.bind(request_id="req-abc")
        log.info("processing")
        log.info("completed", duration_ms=250)
    """
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


def bind_request_context(request_id: str, **kwargs: Any) -> None:
    """Bind request context to all subsequent log entries in current context.

    Uses structlog's contextvars support to add metadata to all logs
    within the current async context (e.g., request handler).

    Args:
        request_id: Unique request identifier
        **kwargs: Additional context key-value pairs

    Example:
        # In FastAPI middleware
        bind_request_context(
            request_id="req-123",
            user_id="U-456",
            endpoint="/api/v1/tasks"
        )

        # All subsequent logs will include this context
        logger.info("task_created")  # Includes request_id, user_id, endpoint
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, **kwargs)


def clear_request_context() -> None:
    """Clear request context variables.

    Should be called after request processing to avoid context leakage
    between requests.

    Example:
        try:
            bind_request_context(request_id="req-123")
            # Process request...
        finally:
            clear_request_context()
    """
    structlog.contextvars.clear_contextvars()
