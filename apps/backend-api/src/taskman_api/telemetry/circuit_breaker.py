"""Circuit breaker pattern for OpenTelemetry span exports.

Prevents cascading failures when OTLP backend is unreachable:
- Opens circuit after consecutive failures
- Drops spans when circuit is open
- Closes circuit after successful export

Fixes:
- B1: Returns SpanExportResult.FAILURE instead of raising
"""

from collections.abc import Sequence
from datetime import datetime

import structlog
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class CircuitBreakerSpanExporter(SpanExporter):
    """Span exporter with circuit breaker pattern.

    Configuration:
        failure_threshold: Number of consecutive failures before opening (default 3)
        success_threshold: Number of successes needed to close (default 1)

    State transitions:
        closed -> open: After failure_threshold consecutive failures
        open -> closed: After success_threshold consecutive successes
    """

    def __init__(
        self,
        otlp_endpoint: str = "http://localhost:4317",
        failure_threshold: int = 3,
        success_threshold: int = 1,
    ):
        """Initialize circuit breaker exporter."""
        self.otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold

        # Circuit state
        self.state: str = "closed"
        self.consecutive_failures: int = 0
        self.consecutive_successes: int = 0
        self._attempt_count_in_open: int = 0  # Count attempts while open

        # Diagnostic timestamps
        self.last_success_time: datetime | None = None
        self.last_failure_time: datetime | None = None
        self.failure_count: int = 0

        # We need to make sure record_circuit_state is defined before calling it
        # Moved call to after class definition or keep it here if import handles it
        # Actually imports are at bottom of file, which is weird.
        # record_circuit_state(self.state)
        # logger.info("circuit_breaker_initialized", state=self.state)
        # ^ This code relies on imports that were at the bottom.
        # I should check where imports are.

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans with circuit breaker protection.

        Returns:
            SpanExportResult.SUCCESS: Export succeeded
            SpanExportResult.FAILURE: Export failed or circuit open
        """
        if self.state == "open":
            # Probe immediately on first attempt, then periodically
            should_probe = (self._attempt_count_in_open == 0) or (
                self._attempt_count_in_open % 10 == 0
            )
            self._attempt_count_in_open += 1

            if not should_probe:
                logger.warning(
                    "circuit_breaker_drop",
                    dropped_spans=len(spans),
                    consecutive_failures=self.consecutive_failures,
                )
                record_circuit_drop(len(spans))
                return SpanExportResult.FAILURE  # Drop spans when circuit open

        # Attempt export
        start_time = datetime.utcnow()

        try:
            result = self.otlp_exporter.export(spans)

            if result == SpanExportResult.SUCCESS:
                self._handle_success(spans, start_time)
                return SpanExportResult.SUCCESS
            else:
                self._handle_failure(spans)
                return SpanExportResult.FAILURE

        except Exception as e:
            # 🔴 B1 FIX: Return FAILURE instead of raising (SDK contract compliance)
            logger.error(
                "circuit_breaker_export_exception",
                error=str(e),
                error_type=type(e).__name__,
                spans=len(spans),
            )
            self._handle_failure(spans)
            return SpanExportResult.FAILURE  # ✅ SDK-compliant exception handling

    def _handle_success(self, spans: Sequence[ReadableSpan], start_time: datetime) -> None:
        """Handle successful export."""
        latency = (datetime.utcnow() - start_time).total_seconds()

        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.last_success_time = datetime.utcnow()

        record_circuit_success()
        record_span_export(latency, len(spans))

        # Close circuit if it was open
        if self.state == "open" and self.consecutive_successes >= self.success_threshold:
            self.state = "closed"
            self._attempt_count_in_open = 0  # Reset attempt counter
            record_circuit_state("closed")
            logger.info(
                "circuit_breaker_closed",
                consecutive_successes=self.consecutive_successes,
            )

    def _handle_failure(self, _spans: Sequence[ReadableSpan]) -> None:
        """Handle failed export."""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        record_circuit_failure()

        # Open circuit if threshold reached
        if self.state == "closed" and self.consecutive_failures >= self.failure_threshold:
            self.state = "open"
            record_circuit_state("open")
            logger.warning(
                "circuit_breaker_opened",
                consecutive_failures=self.consecutive_failures,
                threshold=self.failure_threshold,
            )

    def get_state(self) -> str:
        """Return current circuit breaker state ('open' or 'closed')."""
        return self.state

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        self.otlp_exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush pending spans."""
        if self.state == "open":
            return False
        return self.otlp_exporter.force_flush(timeout_millis)


from taskman_api.telemetry.metrics import (
    record_circuit_drop,
    record_circuit_failure,
    record_circuit_state,
    record_circuit_success,
    record_span_export,
)

logger = structlog.get_logger(__name__)


# Singleton instance for health check access
circuit_breaker_exporter = CircuitBreakerSpanExporter()
