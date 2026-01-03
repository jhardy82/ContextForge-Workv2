"""Unit tests for circuit breaker span exporter.

Tests verify:
- B1 fix: export() returns FAILURE instead of raising exceptions
- Circuit state transitions (closed -> open -> closed)
- Span dropping when circuit is open
"""

from unittest.mock import Mock, patch

from opentelemetry.sdk.trace.export import SpanExportResult

from taskman_api.telemetry.circuit_breaker import CircuitBreakerSpanExporter


class TestCircuitBreakerExporter:
    """Test suite for CircuitBreakerSpanExporter."""

    def test_export_returns_failure_on_exception(self):
        """AC20: Verify export() returns FAILURE instead of raising (B1 FIX)."""
        exporter = CircuitBreakerSpanExporter(failure_threshold=3)

        # Mock OTLP exporter to raise exception
        with patch.object(
            exporter.otlp_exporter,
            "export",
            side_effect=ConnectionError("OTLP backend unreachable"),
        ):
            # Should return FAILURE, not raise
            result = exporter.export([])

            assert result == SpanExportResult.FAILURE
            assert exporter.consecutive_failures == 1

    def test_circuit_opens_after_threshold(self):
        """Verify circuit opens after failure_threshold consecutive failures."""
        exporter = CircuitBreakerSpanExporter(failure_threshold=3)

        with patch.object(
            exporter.otlp_exporter,
            "export",
            return_value=SpanExportResult.FAILURE,
        ):
            # Should stay closed for first 2 failures
            exporter.export([])
            exporter.export([])
            assert exporter.state == "closed"

            # Should open on 3rd failure
            exporter.export([])
            assert exporter.state == "open"

    def test_circuit_closes_after_success(self):
        """Verify circuit closes after successful export."""
        exporter = CircuitBreakerSpanExporter()
        exporter.state = "open"

        with patch.object(
            exporter.otlp_exporter,
            "export",
            return_value=SpanExportResult.SUCCESS,
        ):
            exporter.export([])
            assert exporter.state == "closed"

    def test_spans_dropped_when_circuit_open(self):
        """Verify spans are dropped when circuit is open (after first probe attempt)."""
        exporter = CircuitBreakerSpanExporter()
        exporter.state = "open"
        exporter._attempt_count_in_open = 1  # Skip initial probe

        # Should return FAILURE without calling OTLP exporter (until next probe cycle)
        with patch.object(exporter.otlp_exporter, "export") as mock_export:
            result = exporter.export([Mock(), Mock(), Mock()])

            assert result == SpanExportResult.FAILURE
            mock_export.assert_not_called()  # OTLP not called between probes

    def test_get_state_returns_current_state(self):
        """Verify get_state() returns current circuit state."""
        exporter = CircuitBreakerSpanExporter()
        assert exporter.get_state() == "closed"

        exporter.state = "open"
        assert exporter.get_state() == "open"

    def test_probe_cycle_when_circuit_open(self):
        """Verify probe attempts every 10th call when circuit open."""
        exporter = CircuitBreakerSpanExporter(failure_threshold=3)

        # Force circuit open by exceeding threshold
        with patch.object(
            exporter.otlp_exporter,
            "export",
            return_value=SpanExportResult.FAILURE,
        ):
            for _ in range(exporter.failure_threshold):
                exporter.export([Mock()])

        assert exporter.state == "open"
        initial_attempt_count = exporter._attempt_count_in_open
        assert initial_attempt_count == 0, "Attempt counter should reset when circuit opens"

        # Test probe pattern while keeping circuit open (probes fail)
        # Probe happens at attempt 0 (immediate), then every 10th (10, 20, ...)
        # Between probes, spans are dropped without calling backend

        probe_attempts = []
        for i in range(15):  # Test beyond one full cycle
            # Mock the wrapped exporter to track probe attempts
            # Keep returning FAILURE to keep circuit open
            with patch.object(
                exporter.otlp_exporter,
                "export",
                return_value=SpanExportResult.FAILURE,
            ) as mock_export:
                exporter.export([Mock()])

                # Track which attempts actually called the backend (probes)
                if mock_export.called:
                    probe_attempts.append(i)

        # Verify probe pattern: attempt 0 (immediate), then every 10th (10, 20, ...)
        expected_probes = [0, 10]  # Within our 15-attempt test window
        assert probe_attempts == expected_probes, (
            f"Expected probes at {expected_probes}, got {probe_attempts}"
        )
