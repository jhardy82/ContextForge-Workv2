"""Metrics and observability using OpenTelemetry and Prometheus.

Provides instrumentation for:
- HTTP request metrics (count, duration, errors) via Prometheus Instrumentator
- Database query metrics (count, duration, errors)
- Custom business metrics (task creation, completion rates)
- Application metrics (uptime, health status)

Dual metrics system:
- prometheus-fastapi-instrumentator: Prometheus-native HTTP metrics at /metrics
- OpenTelemetry: Custom business metrics with console/Prometheus export

Usage:
    from taskman_api.infrastructure.metrics import (
        configure_metrics,
        get_business_metrics,
    )

    # Configure at application startup
    configure_metrics(app, settings)

    # Get business metrics and track custom events
    metrics = get_business_metrics()
    metrics["tasks_created_total"].add(1, {"project": "P-001", "priority": "high"})
"""

import os
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from prometheus_fastapi_instrumentator import Instrumentator

from taskman_api.config import Settings
from taskman_api.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Prometheus Instrumentator singleton
_prometheus_instrumentator: Instrumentator | None = None

# Global meter instance
_meter: metrics.Meter | None = None
_business_metrics: dict[str, Any] | None = None


def configure_prometheus(app: FastAPI, settings: Settings) -> Instrumentator:
    """Configure Prometheus FastAPI Instrumentator.

    Provides Prometheus-native HTTP metrics at /metrics endpoint:
    - http_requests_total: Counter with method, handler, status labels
    - http_request_duration_seconds: Histogram with latency buckets
    - http_request_size_bytes: Histogram for request body size
    - http_response_size_bytes: Histogram for response body size
    - http_requests_inprogress: Gauge for concurrent requests

    Args:
        app: FastAPI application instance
        settings: Application settings

    Returns:
        Configured Instrumentator instance
    """
    global _prometheus_instrumentator

    # Check if metrics are enabled via environment variable
    enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() in ("true", "1", "yes")

    _prometheus_instrumentator = Instrumentator(
        should_respect_env_var=True,
        env_var_name="ENABLE_METRICS",
        # Exclude non-user endpoints from metrics
        excluded_handlers=["/metrics", "/health", "/ready", "/live", "/docs", "/redoc", "/openapi.json"],
        should_ignore_untemplated=True,
        should_group_status_codes=True,
        should_instrument_requests_inprogress=True,
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    # Instrument the app and expose /metrics endpoint
    _prometheus_instrumentator.instrument(app)

    if enable_metrics:
        _prometheus_instrumentator.expose(
            app,
            endpoint="/metrics",
            include_in_schema=False,  # Don't show in OpenAPI docs
            tags=["Monitoring"],
        )
        logger.info(
            "prometheus_metrics_configured",
            endpoint="/metrics",
            excluded_handlers=["/metrics", "/health", "/ready", "/live", "/docs", "/redoc"],
        )
    else:
        logger.info("prometheus_metrics_disabled", reason="ENABLE_METRICS=false")

    return _prometheus_instrumentator


def configure_metrics(app: FastAPI, settings: Settings, skip_prometheus: bool = False) -> None:
    """Configure OpenTelemetry and Prometheus metrics.

    Sets up:
    - Prometheus FastAPI Instrumentator for HTTP metrics at /metrics (unless skip_prometheus=True)
    - OpenTelemetry MeterProvider with console exporter (development)
    - FastAPI auto-instrumentation for distributed tracing
    - Custom business metrics

    Args:
        app: FastAPI application instance
        settings: Application settings
        skip_prometheus: If True, skip Prometheus configuration (already done in create_app)

    Example:
        app = create_app()
        settings = get_settings()
        configure_metrics(app, settings)
    """
    global _meter, _business_metrics

    # Configure Prometheus metrics (primary HTTP metrics source)
    # Skip if already configured in create_app (for Gunicorn compatibility)
    if not skip_prometheus:
        configure_prometheus(app, settings)

    # Create OpenTelemetry resource with service information
    resource = Resource.create(
        attributes={
            "service.name": settings.app_name,
            "service.version": "1.0.0",
            "deployment.environment": settings.environment,
        }
    )

    # Create metric exporter
    # Development: log metrics to console every 60 seconds
    # Production: metrics are primarily exposed via Prometheus /metrics endpoint
    if settings.environment in ("development", "testing"):
        metric_reader = PeriodicExportingMetricReader(
            exporter=ConsoleMetricExporter(),
            export_interval_millis=60000,  # Export every 60 seconds
        )
    else:
        # Production: suppress console output, rely on Prometheus scraping
        metric_reader = PeriodicExportingMetricReader(
            exporter=ConsoleMetricExporter(),
            export_interval_millis=300000,  # Export every 5 minutes (reduced noise)
        )

    # Create meter provider
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )

    # Set global meter provider
    metrics.set_meter_provider(meter_provider)

    # Get meter for creating custom metrics
    _meter = metrics.get_meter(__name__)

    # Instrument FastAPI application for OpenTelemetry tracing
    FastAPIInstrumentor.instrument_app(app)

    # Create business metrics
    _business_metrics = create_business_metrics()

    logger.info(
        "metrics_configured",
        service_name=settings.app_name,
        environment=settings.environment,
        prometheus_endpoint="/metrics",
        opentelemetry_exporter="console",
    )


def get_meter() -> metrics.Meter:
    """Get the global OpenTelemetry meter instance.

    Returns:
        Meter instance for creating custom metrics

    Raises:
        RuntimeError: If metrics not configured (call configure_metrics first)

    Example:
        meter = get_meter()
        counter = meter.create_counter(
            "tasks_created_total",
            description="Total number of tasks created",
        )
        counter.add(1, {"project": "P-001"})
    """
    if _meter is None:
        raise RuntimeError(
            "Metrics not configured. Call configure_metrics() at application startup."
        )
    return _meter


# Custom business metrics (created lazily after configure_metrics)
def get_business_metrics() -> dict[str, Any]:
    """Get configured business metrics.

    Returns:
        Dict of metric names to metric instances

    Raises:
        RuntimeError: If metrics not configured

    Example:
        metrics = get_business_metrics()
        metrics["tasks_created_total"].add(1, {"priority": "high"})
    """
    if _business_metrics is None:
        raise RuntimeError(
            "Business metrics not initialized. Call configure_metrics() at startup."
        )
    return _business_metrics


def create_business_metrics() -> dict[str, Any]:
    """Create custom business metrics for TaskMan operations.

    Returns:
        Dict of metric names to metric instances

    Metrics created:
    - tasks_created_total: Counter for task creation
    - tasks_completed_total: Counter for task completion
    - task_status_transitions_total: Counter for status changes
    - active_tasks_gauge: Gauge for currently active tasks
    - task_duration_seconds: Histogram for task completion time
    - project_health_score: Gauge for project health (0-100)
    - sprint_velocity: Histogram for sprint velocity

    Example:
        metrics = create_business_metrics()
        metrics["tasks_created_total"].add(1, {"priority": "high"})
    """
    meter = get_meter()

    return {
        "tasks_created_total": meter.create_counter(
            name="tasks_created_total",
            description="Total number of tasks created",
            unit="1",
        ),
        "tasks_completed_total": meter.create_counter(
            name="tasks_completed_total",
            description="Total number of tasks completed",
            unit="1",
        ),
        "task_status_transitions_total": meter.create_counter(
            name="task_status_transitions_total",
            description="Total number of task status transitions",
            unit="1",
        ),
        "active_tasks_gauge": meter.create_up_down_counter(
            name="active_tasks",
            description="Number of currently active tasks",
            unit="1",
        ),
        "task_duration_seconds": meter.create_histogram(
            name="task_duration_seconds",
            description="Task completion duration in seconds",
            unit="s",
        ),
        "project_health_score": meter.create_up_down_counter(
            name="project_health_score",
            description="Project health score (0-100)",
            unit="1",
        ),
        "sprint_velocity": meter.create_histogram(
            name="sprint_velocity",
            description="Sprint velocity (tasks completed per sprint)",
            unit="1",
        ),
    }
