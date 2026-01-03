"""Integration tests for /metrics endpoint.

Tests verify:
- M1 fix: Rate limiting (10/minute) on metrics endpoint
"""

import pytest
from fastapi.testclient import TestClient

from taskman_api.main import app
from taskman_api.rate_limiter import limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test.

    Ensures test isolation - prevents rate limit state from
    one test affecting subsequent tests.
    """
    yield
    # Clear rate limit storage after each test
    limiter.reset()


class TestMetricsEndpoint:
    """Test suite for /metrics endpoint."""

    def test_metrics_returns_prometheus_text_format(self):
        """Verify /metrics returns Prometheus text format."""
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "circuit_breaker_state" in response.text

    @pytest.mark.slow
    def test_metrics_rate_limiting(self):
        """AC22: Verify 429 after 10 requests/minute (M1 FIX).

        This test is marked 'slow' because it makes 11 sequential requests.
        Rate limiting is enforced by slowapi per remote address.
        """
        # Make 10 requests (should succeed)
        for i in range(10):
            response = client.get("/metrics")
            assert response.status_code == 200, f"Request {i+1} failed"

        # 11th request should be rate-limited
        response = client.get("/metrics")
        assert response.status_code == 429  # Too Many Requests

    def test_metrics_includes_circuit_breaker_metrics(self):
        """Verify metrics include circuit breaker counters and gauges."""
        response = client.get("/metrics")

        assert response.status_code == 200
        content = response.text

        # Check for circuit breaker metrics
        assert "circuit_breaker_state" in content
        assert "circuit_breaker_drops_total" in content
        assert "circuit_breaker_successes_total" in content
        assert "circuit_breaker_failures_total" in content
        assert "span_export_latency_seconds" in content
        assert "span_export_batch_size" in content
