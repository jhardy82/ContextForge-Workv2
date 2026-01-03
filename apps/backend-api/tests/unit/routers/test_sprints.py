"""Unit tests for Sprints Router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from taskman_api.core.enums import SprintStatus
from taskman_api.core.result import Ok
from taskman_api.dependencies import get_sprint_service
from taskman_api.main import app
from taskman_api.schemas import SprintProgress, SprintResponse
from taskman_api.services.sprint_service import SprintService


@pytest.fixture
def mock_sprint_service(mocker):
    """Mock SprintService."""
    mock_service = mocker.Mock(spec=SprintService)
    return mock_service


@pytest.fixture
def client(mock_sprint_service, mocker):
    """Test client with dependency overrides."""
    app.dependency_overrides[get_sprint_service] = lambda: mock_sprint_service
    # Mock lifespan DB calls
    mocker.patch("taskman_api.main.init_db", new_callable=AsyncMock)
    mocker.patch(
        "taskman_api.main.check_db_health",
        new_callable=AsyncMock,
        return_value={"connected": True},
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}


class TestSprintsRouter:
    """Test suite for sprints router."""

    def test_list_sprints_success(self, client, mock_sprint_service):
        """Should list sprints successfully."""
        # Setup
        sprints = [
            SprintResponse(
                id="S-1",
                name="Sprint 1",
                goal="Goal 1",
                status=SprintStatus.PLANNING,
                primary_project="P-1",
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z",
            )
        ]
        mock_sprint_service.search = AsyncMock(return_value=Ok((sprints, 1)))

        # Execute
        response = client.get("/api/v1/sprints")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["sprints"][0]["id"] == "S-1"

    def test_create_sprint_draft_success(self, client, mock_sprint_service):
        """Should create a draft sprint (missing optional fields)."""
        # Setup
        # Omit goal, start_date, end_date
        payload = {"id": "S-DRAFT", "name": "Draft Sprint", "primary_project": "P-1", "owner": "me"}

        created = SprintResponse(
            id="S-DRAFT",
            name="Draft Sprint",
            goal=None,
            status=SprintStatus.PLANNING,
            primary_project="P-1",
            start_date=None,
            end_date=None,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_sprint_service.create = AsyncMock(return_value=Ok(created))

        # Execute
        response = client.post("/api/v1/sprints", json=payload)

        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "S-DRAFT"
        assert data["goal"] is None
        assert data["start_date"] is None

    def test_get_sprint_progress_success(self, client, mock_sprint_service):
        """Should get sprint progress."""
        # Setup
        progress = SprintProgress(
            sprint_id="S-1",
            name="Sprint 1",
            status=SprintStatus.ACTIVE,
            task_count=10,
            completed_count=5,
            completion_percentage=50.0,
            total_points=20.0,
            completed_points=10.0,
            days_remaining=5,
        )
        mock_sprint_service.get_progress = AsyncMock(return_value=Ok(progress))

        # Execute
        response = client.get("/api/v1/sprints/S-1/progress")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completion_percentage"] == 50.0

    def test_start_sprint_success(self, client, mock_sprint_service):
        """Should start sprint."""
        # Setup
        started = SprintResponse(
            id="S-1",
            name="Sprint 1",
            status=SprintStatus.ACTIVE,
            primary_project="P-1",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_sprint_service.change_status = AsyncMock(return_value=Ok(started))

        # Execute
        response = client.post("/api/v1/sprints/S-1/start")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "active"
