"""Integration tests for /health/telemetry endpoint.

Tests verify:
- M3 fix: Health endpoint returns 200 when circuit closed, 503 when open
"""

from fastapi.testclient import TestClient

from taskman_api.main import app
from taskman_api.telemetry.circuit_breaker import circuit_breaker_exporter

client = TestClient(app)


class TestTelemetryHealthEndpoint:
    """Test suite for /health/telemetry endpoint."""

    def test_health_returns_200_when_circuit_closed(self):
        """AC23: Verify 200 when circuit is closed (M3 FIX)."""
        # Force circuit closed
        circuit_breaker_exporter.state = "closed"

        response = client.get("/health/telemetry")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["circuit_state"] == "closed"
        assert data["otlp_backend"] == "reachable"

    def test_health_returns_503_when_circuit_open(self):
        """AC23: Verify 503 when circuit is open (M3 FIX)."""
        # Force circuit open
        circuit_breaker_exporter.state = "open"

        response = client.get("/health/telemetry")

        assert response.status_code == 503
        # Response content is dict (not JSON parsed)
        # FastAPI's Response() with content dict returns it as-is

    def test_health_includes_diagnostic_timestamps(self):
        """Verify health endpoint includes last success/failure timestamps."""
        circuit_breaker_exporter.state = "closed"
        circuit_breaker_exporter.last_success_time = None

        response = client.get("/health/telemetry")

        assert response.status_code == 200
        data = response.json()
        assert "last_success" in data
        assert "failure_count" in data
