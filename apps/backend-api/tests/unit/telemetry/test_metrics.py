"""Unit tests for Prometheus metrics module.

Tests verify:
- M2 fix: All 5 metric functions wrapped in try/except
- Graceful degradation when Prometheus client fails
- Rate-limited error logging
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from taskman_api.telemetry import metrics


class TestPrometheusMetrics:
    """Test suite for Prometheus metrics functions."""

    def test_record_circuit_state_handles_exceptions(self):
        """AC21: Verify record_circuit_state wraps exceptions (M2 FIX)."""
        with patch.object(
            metrics.circuit_breaker_state,
            "labels",
            side_effect=Exception("Prometheus client error"),
        ):
            # Should not raise, just log warning
            metrics.record_circuit_state("open")  # No exception raised

    def test_record_circuit_drop_handles_exceptions(self):
        """AC21: Verify record_circuit_drop wraps exceptions (M2 FIX)."""
        with patch.object(
            metrics.circuit_breaker_drops,
            "inc",
            side_effect=Exception("Prometheus client error"),
        ):
            metrics.record_circuit_drop(10)  # No exception raised

    def test_record_circuit_success_handles_exceptions(self):
        """AC21: Verify record_circuit_success wraps exceptions (M2 FIX)."""
        with patch.object(
            metrics.circuit_breaker_successes,
            "inc",
            side_effect=Exception("Prometheus client error"),
        ):
            metrics.record_circuit_success()  # No exception raised

    def test_record_circuit_failure_handles_exceptions(self):
        """AC21: Verify record_circuit_failure wraps exceptions (M2 FIX)."""
        with patch.object(
            metrics.circuit_breaker_failures,
            "inc",
            side_effect=Exception("Prometheus client error"),
        ):
            metrics.record_circuit_failure()  # No exception raised

    def test_record_span_export_handles_exceptions(self):
        """AC21: Verify record_span_export wraps exceptions (M2 FIX)."""
        with patch.object(
            metrics.span_export_latency,
            "observe",
            side_effect=Exception("Prometheus client error"),
        ):
            metrics.record_span_export(0.5, 10)  # No exception raised

    def test_rate_limiting_for_error_logging(self):
        """Verify metric failure logging is rate-limited to 1/minute."""
        metrics._last_metric_failure.clear()

        # First call should log
        assert metrics._should_log_failure("test_metric") is True

        # Immediate second call should not log
        assert metrics._should_log_failure("test_metric") is False

        # After 60+ seconds, should log again
        past_time = datetime.utcnow() - timedelta(seconds=61)
        metrics._last_metric_failure["test_metric"] = past_time
        assert metrics._should_log_failure("test_metric") is True
