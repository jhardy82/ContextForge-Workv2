"""OpenTelemetry instrumentation for TaskMan-v2 backend API.

Provides:
- Circuit breaker pattern for OTLP exports
- Prometheus metrics for circuit breaker state
- Health check endpoint integration
"""

from .circuit_breaker import (
    CircuitBreakerSpanExporter,
    circuit_breaker_exporter,
)
from .metrics import (
    record_circuit_drop,
    record_circuit_failure,
    record_circuit_state,
    record_circuit_success,
    record_span_export,
)

__all__ = [
    "CircuitBreakerSpanExporter",
    "circuit_breaker_exporter",
    "record_circuit_drop",
    "record_circuit_failure",
    "record_circuit_state",
    "record_circuit_success",
    "record_span_export",
]
