"""Core logging functionality for cf_core.logging.

Implements the primary logging API including get_logger(), ulog(), and
configure_logging() functions. Provides backward compatibility with
existing unified_logger.py interface while adding new capabilities.

Key Features:
- Structured logging via structlog
- Correlation ID integration
- Configurable output formats (JSON, text)
- Legacy ulog() API compatibility
- LOG-001..009 baseline event support

Authority: docs/prd/PRD-CFCORE-LOGGING.md (FR-001, FR-002, FR-008)
"""

import logging
import os
import sys
from typing import Any

try:
    import structlog
    _STRUCTLOG_AVAILABLE = True
except ImportError:
    _STRUCTLOG_AVAILABLE = False

from .correlation import get_correlation_id

# Global logger instance
_logger: structlog.stdlib.BoundLogger | logging.Logger | None = None
_configured = False


def _add_correlation_processor(logger, method_name, event_dict):
    """Structlog processor to add correlation ID to all log entries."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def configure_logging(
    level: str = "INFO",
    format: str = "json",
    output: str = "console",
    **kwargs: Any
) -> None:
    """Configure the logging system (FR-008).

    Sets up structured logging with correlation ID support and configurable
    output formats. Should be called once at application startup.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Output format ("json" or "text")
        output: Output destination ("console", "file", or file path)
        **kwargs: Additional configuration options

    Raises:
        ValueError: If invalid level or format specified
        ImportError: If structlog not available and format="json"

    Example:
        # Configure JSON logging to console
        configure_logging(level="INFO", format="json", output="console")

        # Configure text logging to file
        configure_logging(level="DEBUG", format="text", output="/var/log/app.log")
    """
    global _logger, _configured

    # Validate parameters
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")

    valid_formats = {"json", "text"}
    if format.lower() not in valid_formats:
        raise ValueError(f"Invalid format: {format}. Must be one of {valid_formats}")

    # Check structlog availability for JSON format
    if format.lower() == "json" and not _STRUCTLOG_AVAILABLE:
        raise ImportError(
            "structlog is required for JSON format. Install with: pip install structlog"
        )

    # Configure based on format
    if format.lower() == "json" and _STRUCTLOG_AVAILABLE:
        _configure_structlog(level, output, **kwargs)
    else:
        _configure_stdlib(level, format, output, **kwargs)

    _configured = True


def _configure_structlog(level: str, output: str, **kwargs: Any) -> None:
    """Configure structlog for JSON output."""
    global _logger

    # Configure structlog processors
    processors = [
        # Add correlation ID to all log entries
        _add_correlation_processor,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    # Add JSON formatter for machine-readable output
    processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging as backend
    if output == "console":
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, level.upper())
        )
    else:
        logging.basicConfig(
            format="%(message)s",
            filename=output,
            level=getattr(logging, level.upper())
        )

    _logger = structlog.get_logger()


def _configure_stdlib(level: str, format: str, output: str, **kwargs: Any) -> None:
    """Configure stdlib logging for text output."""
    global _logger

    # Create formatter
    if format.lower() == "text":
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Fallback to simple format
        formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Create handler
    if output == "console":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(output)

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    _logger = logging.getLogger("cf_core")





def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger | logging.Logger:
    """Get a logger instance (FR-001).

    Returns a structured logger (structlog) if available and configured,
    otherwise returns a stdlib logger. Automatically includes correlation ID.

    Args:
        name: Logger name (defaults to "cf_core")

    Returns:
        Logger instance with correlation ID support

    Example:
        logger = get_logger("my_module")
        logger.info("Task started", task_id="T-001")
    """
    global _logger

    # Auto-configure if not already done
    if not _configured:
        configure_logging()

    if _STRUCTLOG_AVAILABLE and isinstance(_logger, structlog.stdlib.BoundLogger):
        # Return bound structlog logger with name
        return _logger.bind(logger_name=name or "cf_core")
    else:
        # Return stdlib logger
        return logging.getLogger(name or "cf_core")


def ulog(
    action: str,
    target: str | None = None,
    result: str = "success",
    severity: str = "INFO",
    **kwargs: Any,
) -> None:
    """Legacy unified logging function (FR-002).

    Provides backward compatibility with existing ulog() calls throughout
    the codebase. Automatically includes correlation ID in log entries.

    Args:
        action: The action being performed
        target: The target of the action (optional)
        result: The result of the action (default: "success")
        severity: Log level (DEBUG, INFO, WARN, ERROR)
        **kwargs: Additional fields to log

    Example:
        ulog("task_start", "T-001", "success", task_id="T-001", priority=3)
        ulog("api_call", "/tasks", "error", status_code=404, error="Not found")
    """
    # Normalize severity level
    level = severity.upper()
    if level == "WARN":
        level = "WARNING"

    # Get logger
    logger = get_logger("ulog")

    # Prepare log data
    log_data = {
        "action": action,
        "result": result,
        **kwargs
    }

    # Add target if provided
    if target is not None:
        log_data["target"] = target

    # Log based on severity
    if hasattr(logger, 'info') and hasattr(logger, 'error'):
        # structlog or stdlib logger
        log_method = getattr(logger, level.lower(), logger.info)

        if _STRUCTLOG_AVAILABLE and isinstance(logger, structlog.stdlib.BoundLogger):
            # structlog - pass data as kwargs
            log_method(action, **log_data)
        else:
            # stdlib logger - format message
            message = f"{action}"
            if target:
                message += f" -> {target}"
            message += f" ({result})"

            # Add correlation ID for stdlib logging
            correlation_id = get_correlation_id()
            extra_data = {"correlation_id": correlation_id, **log_data}

            log_method(message, extra=extra_data)


def log_baseline_event(
    event_type: str,
    **event_data: Any
) -> None:
    """Log a baseline event (LOG-001..009) with evidence capture.

    Logs one of the required baseline events with automatic evidence
    bundle generation and correlation ID inclusion.

    Baseline Events:
    - session_start, task_start, decision
    - artifact_touch_batch, artifact_emit
    - warning, error, task_end, session_summary

    Args:
        event_type: One of the LOG-001..009 baseline event types
        **event_data: Event-specific data fields

    Example:
        log_baseline_event("task_start", task_id="T-001", estimated_hours=2.5)
        log_baseline_event("artifact_emit", path="config.yaml", hash="abc123", size_bytes=1024)
    """
    # Import here to avoid circular imports
    from .evidence import capture_evidence

    # Valid baseline event types per LOG-001..009
    baseline_events = {
        "session_start", "task_start", "decision", "artifact_touch_batch",
        "artifact_emit", "warning", "error", "task_end", "session_summary"
    }

    if event_type not in baseline_events:
        # Log but don't fail - allows extensibility
        ulog("log_baseline_event", event_type, "warning",
             message=f"Non-baseline event type: {event_type}")

    # Capture evidence bundle
    evidence = capture_evidence(event_type, **event_data)

    # Log the event with evidence
    logger = get_logger("baseline")

    if _STRUCTLOG_AVAILABLE and isinstance(logger, structlog.stdlib.BoundLogger):
        logger.info(event_type, **evidence)
    else:
        logger.info(f"Baseline event: {event_type}", extra=evidence)


# Convenience functions for common baseline events

def log_session_start(session_id: str, **context: Any) -> None:
    """Log session_start baseline event (LOG-001)."""
    log_baseline_event("session_start", session_id=session_id, **context)


def log_task_start(task_id: str, **context: Any) -> None:
    """Log task_start baseline event (LOG-002)."""
    log_baseline_event("task_start", task_id=task_id, **context)


def log_task_end(task_id: str, status: str, **context: Any) -> None:
    """Log task_end baseline event (LOG-007)."""
    log_baseline_event("task_end", task_id=task_id, status=status, **context)


def log_artifact_emit(path: str, hash: str, size_bytes: int, **context: Any) -> None:
    """Log artifact_emit baseline event (LOG-005)."""
    log_baseline_event("artifact_emit", path=path, hash=hash, size_bytes=size_bytes, **context)
