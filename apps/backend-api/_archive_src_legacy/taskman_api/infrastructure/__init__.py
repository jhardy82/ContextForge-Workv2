"""Infrastructure components for TaskMan API.

This package provides cross-cutting infrastructure concerns:
- Structured logging with JSONL output
- Health checks (liveness, readiness, startup)
- Metrics and observability (Prometheus, OpenTelemetry)
- Middleware for security, rate limiting, and monitoring
"""

from taskman_api.infrastructure.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
