import pytest

from taskman_api.services.qse_service import QSEService


@pytest.mark.asyncio
async def test_evaluate_gate():
    service = QSEService()
    result = await service.evaluate_gate("standard_gate", {})
    assert result["status"] == "PASS"

@pytest.mark.asyncio
async def test_collect_metrics():
    service = QSEService()
    metrics = await service.collect_metrics()
    assert metrics["coverage"] > 0
