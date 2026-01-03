"""Unit tests for Tasks Router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.core.errors import NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_db_session, get_task_service
from taskman_api.main import app
from taskman_api.schemas import TaskResponse
from taskman_api.services.task_service import TaskService


@pytest.fixture
def mock_task_service(mocker):
    """Mock TaskService."""
    mock_service = mocker.Mock(spec=TaskService)

    # Needs to be callable for dependency injection
    async def get_service():
        return mock_service

    # The original mock_task_service fixture was overriding TaskService directly.
    # The new client fixture expects to override get_task_service.
    # We'll keep the mock_service object and let the client fixture handle the override.
    return mock_service


@pytest.fixture
def client(mock_task_service):
    """Test client with dependency overrides."""
    app.dependency_overrides[get_task_service] = lambda: mock_task_service
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}


class TestTasksRouter:
    """Test suite for tasks router."""

    def test_list_tasks_success(self, client, mock_task_service):
        """Should list tasks successfully."""
        # Setup
        tasks = [
            TaskResponse(
                id="T-001",
                title="Task 1",
                summary="Summary 1",
                description="Desc 1",
                status=TaskStatus.NEW,
                priority=Priority.P1,
                primary_project="P-1",
                primary_sprint="S-1",
                owner="owner1",
                assignees=[],
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z",
            ),
            TaskResponse(
                id="T-002",
                title="Task 2",
                summary="Summary 2",
                description="Desc 2",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.P2,
                primary_project="P-1",
                primary_sprint="S-1",
                owner="owner2",
                assignees=[],
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z",
            ),
        ]
        mock_task_service.search = AsyncMock(return_value=Ok((tasks, 2)))

        # Execute
        response = client.get("/api/v1/tasks?page=1&per_page=10")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2
        assert data["tasks"][0]["id"] == "T-001"
        assert data["tasks"][1]["id"] == "T-002"

    def test_list_tasks_filtering(self, client, mock_task_service):
        """Should filter tasks correctly."""
        # Setup
        mock_task_service.search = AsyncMock(return_value=Ok(([], 0)))

        # Execute
        client.get("/api/v1/tasks?status=new&priority=p1&project_id=P-1")

        # Verify
        mock_task_service.search.assert_called_once()
        call_kwargs = mock_task_service.search.call_args.kwargs
        assert call_kwargs["status"] == TaskStatus.NEW
        assert call_kwargs["priority"] == Priority.P1
        assert call_kwargs["project_id"] == "P-1"

    def test_create_task_success(self, client, mock_task_service):
        """Should create task successfully."""
        # Setup
        payload = {
            "id": "T-NEW",
            "title": "New Task",
            "summary": "New Summary",
            "description": "Description",
            "primary_project": "P-1",
            "primary_sprint": "S-1",
            "priority": "p1",
            "owner": "me",
        }

        created_task = TaskResponse(
            id="T-NEW",
            title="New Task",
            summary="New Summary",
            description="Description",
            status=TaskStatus.NEW,
            priority=Priority.P1,
            primary_project="P-1",
            primary_sprint="S-1",
            owner="me",
            assignees=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_task_service.create = AsyncMock(return_value=Ok(created_task))

        # Execute
        response = client.post("/api/v1/tasks", json=payload)

        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "T-NEW"
        assert data["title"] == "New Task"

    def test_get_task_success(self, client, mock_task_service):
        """Should get task by ID."""
        # Setup
        task = TaskResponse(
            id="T-001",
            title="Task 1",
            summary="Summary",
            description="Desc",
            status=TaskStatus.NEW,
            priority=Priority.P1,
            primary_project="P-1",
            primary_sprint="S-1",
            owner="owner",
            assignees=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_task_service.get = AsyncMock(return_value=Ok(task))

        # Execute
        response = client.get("/api/v1/tasks/T-001")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == "T-001"

    def test_get_task_not_found(self, client, mock_task_service):
        """Should return 404 for non-existent task."""
        # Setup
        mock_task_service.get = AsyncMock(return_value=Err(NotFoundError("Task not found")))

        # Execute
        response = client.get("/api/v1/tasks/T-999")

        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_success(self, client, mock_task_service):
        """Should update task successfully."""
        # Setup
        payload = {"title": "Updated Title"}

        updated_task = TaskResponse(
            id="T-001",
            title="Updated Title",
            summary="Summary",
            description="Desc",
            status=TaskStatus.NEW,
            priority=Priority.P1,
            primary_project="P-1",
            primary_sprint="S-1",
            owner="owner",
            assignees=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_task_service.update = AsyncMock(return_value=Ok(updated_task))

        # Execute
        response = client.patch("/api/v1/tasks/T-001", json=payload)

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Title"

    def test_delete_task_success(self, client, mock_task_service):
        """Should delete task successfully."""
        # Setup
        mock_task_service.delete = AsyncMock(return_value=Ok(True))

        # Execute
        response = client.delete("/api/v1/tasks/T-001")

        # Verify
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_complete_task_success(self, client, mock_task_service):
        """Should complete task successfully."""
        # Setup
        completed_task = TaskResponse(
            id="T-001",
            title="Task 1",
            summary="Summary",
            description="Desc",
            status=TaskStatus.DONE,
            priority=Priority.P1,
            primary_project="P-1",
            primary_sprint="S-1",
            owner="owner",
            assignees=[],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )
        mock_task_service.change_status = AsyncMock(return_value=Ok(completed_task))

        # Execute
        response = client.post("/api/v1/tasks/T-001/complete")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "done"

    def test_complete_task_validation_error(self, client, mock_task_service):
        """Should return 422 for invalid status transition."""
        # Setup
        mock_task_service.change_status = AsyncMock(
            return_value=Err(ValidationError("Invalid transition"))
        )

        # Execute
        response = client.post("/api/v1/tasks/T-001/complete")

        # Verify
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
