"""Unit tests for Projects Router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from taskman_api.core.enums import ProjectStatus
from taskman_api.core.errors import ConflictError, NotFoundError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_project_service
from taskman_api.main import app
from taskman_api.schemas import ProjectResponse
from taskman_api.services.project_service import ProjectService


@pytest.fixture
def mock_project_service(mocker):
    """Mock ProjectService."""
    mock_service = mocker.Mock(spec=ProjectService)
    return mock_service


@pytest.fixture
def client(mock_project_service, mocker):
    """Test client with dependency overrides."""
    app.dependency_overrides[get_project_service] = lambda: mock_project_service
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


class TestProjectsRouter:
    """Test suite for projects router."""

    def test_list_projects_success(self, client, mock_project_service):
        """Should list projects successfully."""
        # Setup
        projects = [
            ProjectResponse(
                id="P-001",
                name="Project 1",
                mission="Mission 1",
                status=ProjectStatus.ACTIVE,
                owner="owner1",
                sprints=[],
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z",
            ),
            ProjectResponse(
                id="P-002",
                name="Project 2",
                mission=None,  # Draft project
                status=ProjectStatus.NEW,
                owner="owner1",
                sprints=[],
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z",
            ),
        ]
        mock_project_service.search = AsyncMock(return_value=Ok((projects, 2)))

        # Execute
        response = client.get("/api/v1/projects")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["projects"]) == 2
        assert data["projects"][0]["id"] == "P-001"
        assert data["projects"][1]["mission"] is None

    def test_create_project_full_success(self, client, mock_project_service):
        """Should create a project with all fields."""
        # Setup
        payload = {
            "id": "P-NEW",
            "name": "New Project",
            "mission": "To conquer the world",
            "start_date": "2025-01-01",
            "owner": "me",
        }

        created_project = ProjectResponse(
            id="P-NEW",
            name="New Project",
            mission="To conquer the world",
            status=ProjectStatus.NEW,
            owner="me",
            start_date="2025-01-01",
            sprints=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_project_service.create = AsyncMock(return_value=Ok(created_project))

        # Execute
        response = client.post("/api/v1/projects", json=payload)

        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "P-NEW"
        assert data["mission"] == "To conquer the world"

    def test_create_project_draft_success(self, client, mock_project_service):
        """Should create a draft project (missing optional fields)."""
        # Setup
        # Omit mission and start_date
        payload = {"id": "P-DRAFT", "name": "Draft Project", "owner": "me"}

        created_project = ProjectResponse(
            id="P-DRAFT",
            name="Draft Project",
            mission=None,
            status=ProjectStatus.NEW,
            owner="me",
            start_date=None,
            sprints=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_project_service.create = AsyncMock(return_value=Ok(created_project))

        # Execute
        response = client.post("/api/v1/projects", json=payload)

        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "P-DRAFT"
        assert data["mission"] is None

    def test_create_project_duplicate_error(self, client, mock_project_service):
        """Should return 409 for duplicate ID."""
        # Setup
        payload = {"id": "P-DUP", "name": "Dup", "owner": "me"}
        mock_project_service.create = AsyncMock(return_value=Err(ConflictError("Duplicate ID")))

        # Execute
        response = client.post("/api/v1/projects", json=payload)

        # Verify
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_get_project_success(self, client, mock_project_service):
        """Should get project by ID."""
        # Setup
        project = ProjectResponse(
            id="P-001",
            name="Project 1",
            status=ProjectStatus.ACTIVE,
            owner="owner1",
            sprints=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_project_service.get = AsyncMock(return_value=Ok(project))

        # Execute
        response = client.get("/api/v1/projects/P-001")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == "P-001"

    def test_get_project_not_found(self, client, mock_project_service):
        """Should return 404 when not found."""
        # Setup
        mock_project_service.get = AsyncMock(return_value=Err(NotFoundError("Not found")))

        # Execute
        response = client.get("/api/v1/projects/P-999")

        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_project_success(self, client, mock_project_service):
        """Should update project."""
        # Setup
        payload = {"name": "Updated Name"}
        updated = ProjectResponse(
            id="P-001",
            name="Updated Name",
            status=ProjectStatus.ACTIVE,
            owner="owner1",
            sprints=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_project_service.update = AsyncMock(return_value=Ok(updated))

        # Execute
        response = client.put("/api/v1/projects/P-001", json=payload)

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Name"

    def test_delete_project_success(self, client, mock_project_service):
        """Should delete project."""
        # Setup
        mock_project_service.delete = AsyncMock(return_value=Ok(True))

        # Execute
        response = client.delete("/api/v1/projects/P-001")

        # Verify
        assert response.status_code == status.HTTP_204_NO_CONTENT
