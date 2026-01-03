"""Prometheus metrics for OpenTelemetry circuit breaker.

Provides:
- Circuit breaker state gauge
- Circuit breaker event counters
- Span export metrics

Fixes:
- M2: All metric functions wrapped in try/except
"""

from datetime import datetime

import structlog
from prometheus_client import Counter, Gauge, Histogram

logger = structlog.get_logger(__name__)

# Circuit breaker state gauge
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (1=open, 0=closed)",
    ["state"],
)

# Circuit breaker event counters
circuit_breaker_drops = Counter(
    "circuit_breaker_drops_total",
    "Total spans dropped due to open circuit",
)

circuit_breaker_successes = Counter(
    "circuit_breaker_successes_total",
    "Total successful span exports",
)

circuit_breaker_failures = Counter(
    "circuit_breaker_failures_total",
    "Total failed span exports",
)

# Span export metrics
span_export_latency = Histogram(
    "span_export_latency_seconds",
    "Span export latency in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

span_export_batch_size = Histogram(
    "span_export_batch_size",
    "Number of spans in each export batch",
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000],
)

# Rate limiting for metric failure logging
_last_metric_failure: dict[str, datetime] = {}
_METRIC_FAILURE_LOG_INTERVAL_SECONDS = 60


def _should_log_failure(metric_name: str) -> bool:
    """Rate limit metric failure logging to 1 per minute per metric."""
    now = datetime.utcnow()
    last_failure = _last_metric_failure.get(metric_name)

    if (
        last_failure is None
        or (now - last_failure).total_seconds() >= _METRIC_FAILURE_LOG_INTERVAL_SECONDS
    ):
        _last_metric_failure[metric_name] = now
        return True
    return False


def record_circuit_state(state: str) -> None:
    """Record circuit breaker state change.

    🔴 M2 FIX: Wrapped in try/except for graceful degradation
    """
    try:
        # Set gauge: 1 for open, 0 for closed
        circuit_breaker_state.labels(state="open").set(1 if state == "open" else 0)
        circuit_breaker_state.labels(state="closed").set(0 if state == "open" else 1)
    except Exception as e:
        if _should_log_failure("record_circuit_state"):
            logger.warning("metric_recording_failed", metric="circuit_state", error=str(e))


def record_circuit_drop(dropped_spans: int) -> None:
    """Record spans dropped due to open circuit.

    🔴 M2 FIX: Wrapped in try/except for graceful degradation
    """
    try:
        circuit_breaker_drops.inc(dropped_spans)
    except Exception as e:
        if _should_log_failure("record_circuit_drop"):
            logger.warning("metric_recording_failed", metric="circuit_drop", error=str(e))


def record_circuit_success() -> None:
    """Record successful OTLP export.

    🔴 M2 FIX: Wrapped in try/except for graceful degradation
    """
    try:
        circuit_breaker_successes.inc()
    except Exception as e:
        if _should_log_failure("record_circuit_success"):
            logger.warning("metric_recording_failed", metric="circuit_success", error=str(e))


def record_circuit_failure() -> None:
    """Record failed OTLP export.

    🔴 M2 FIX: Wrapped in try/except for graceful degradation
    """
    try:
        circuit_breaker_failures.inc()
    except Exception as e:
        if _should_log_failure("record_circuit_failure"):
            logger.warning("metric_recording_failed", metric="circuit_failure", error=str(e))


def record_span_export(latency_seconds: float, batch_size: int) -> None:
    """Record span export latency and batch size.

    🔴 M2 FIX: Wrapped in try/except for graceful degradation
    """
    try:
        span_export_latency.observe(latency_seconds)
        span_export_batch_size.observe(batch_size)
    except Exception as e:
        if _should_log_failure("record_span_export"):
            logger.warning("metric_recording_failed", metric="span_export", error=str(e))
