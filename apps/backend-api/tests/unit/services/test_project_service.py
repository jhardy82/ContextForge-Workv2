"""Unit tests for ProjectService.

Consolidated tests covering metrics, sprint management, status operations,
CRUD operations, and edge cases.
"""

import copy
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import ProjectStatus, TaskStatus
from taskman_api.core.errors import NotFoundError
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from taskman_api.services.project_service import ProjectService


class TestProjectServiceMetrics:
    """Tests for project metrics calculation."""

    @pytest.mark.asyncio
    async def test_get_metrics_success(
        self, mocker, mock_project_repository, mock_task_repository, sample_project, sample_task
    ):
        """Test successful metrics calculation with mixed task statuses."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockProjRepo, \
             patch("taskman_api.services.project_service.TaskRepository") as MockTaskRepo:
            MockProjRepo.return_value = mock_project_repository
            MockTaskRepo.return_value = mock_task_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository
            service.task_repo = mock_task_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

            task1 = copy.deepcopy(sample_task)
            task1.status = TaskStatus.DONE
            task2 = copy.deepcopy(sample_task)
            task2.status = TaskStatus.IN_PROGRESS
            task3 = copy.deepcopy(sample_task)
            task3.status = TaskStatus.BLOCKED

            mock_task_repository.find_by_project = AsyncMock(
                return_value=Ok([task1, task2, task3])
            )

            result = await service.get_metrics("P-TEST-001")

            assert isinstance(result, Ok)
            metrics = result.ok()
            assert metrics["total_tasks"] == 3
            assert "done" in metrics["tasks_by_status"]
            assert "health_status" in metrics
            assert "completion_percentage" in metrics

    @pytest.mark.asyncio
    async def test_get_metrics_no_tasks(
        self, mocker, mock_project_repository, mock_task_repository, sample_project
    ):
        """Test metrics calculation for project with no tasks."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockProjRepo, \
             patch("taskman_api.services.project_service.TaskRepository") as MockTaskRepo:
            MockProjRepo.return_value = mock_project_repository
            MockTaskRepo.return_value = mock_task_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository
            service.task_repo = mock_task_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
            mock_task_repository.find_by_project = AsyncMock(return_value=Ok([]))

            result = await service.get_metrics("P-TEST-001")

            assert isinstance(result, Ok)
            metrics = result.ok()
            assert metrics["total_tasks"] == 0
            assert metrics["health_status"] == "green"
            assert metrics["completion_percentage"] == 0.0

    @pytest.mark.asyncio
    async def test_get_metrics_project_not_found(self, mocker, mock_project_repository):
        """Test metrics calculation for non-existent project."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=None)

            result = await service.get_metrics("P-NONEXISTENT")

            assert isinstance(result, Err)
            assert isinstance(result.err(), NotFoundError)


class TestProjectServiceSprints:
    """Tests for project sprint management."""

    @pytest.mark.asyncio
    async def test_add_sprint(self, mocker, mock_project_repository, sample_project):
        """Test adding sprint to project."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            project_no_sprints = copy.deepcopy(sample_project)
            project_no_sprints.sprints = []
            mock_project_repository.get_by_id = AsyncMock(return_value=project_no_sprints)

            project_with_sprint = copy.deepcopy(sample_project)
            project_with_sprint.sprints = ["S-2025-01"]
            mock_project_repository.update = AsyncMock(return_value=project_with_sprint)

            result = await service.add_sprint("P-TEST-001", "S-2025-01")

            assert isinstance(result, Ok)
            assert "S-2025-01" in result.ok().sprints

    @pytest.mark.asyncio
    async def test_add_duplicate_sprint_idempotent(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test adding duplicate sprint is idempotent (no duplicates created)."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            project_with_sprint = copy.deepcopy(sample_project)
            project_with_sprint.sprints = ["S-2025-01"]
            mock_project_repository.get_by_id = AsyncMock(return_value=project_with_sprint)

            result = await service.add_sprint("P-TEST-001", "S-2025-01")

            assert isinstance(result, Ok)
            assert result.ok().sprints.count("S-2025-01") == 1

    @pytest.mark.asyncio
    async def test_remove_sprint(self, mocker, mock_project_repository, sample_project):
        """Test removing sprint from project."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            sample_project.sprints = ["S-TEST-001", "S-TEST-002"]
            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

            updated = copy.deepcopy(sample_project)
            updated.sprints = ["S-TEST-001"]
            mock_project_repository.update = AsyncMock(return_value=updated)

            result = await service.remove_sprint("P-TEST-001", "S-TEST-002")

            assert isinstance(result, Ok)
            assert "S-TEST-002" not in result.ok().sprints


class TestProjectServiceStatus:
    """Tests for project status operations."""

    @pytest.mark.asyncio
    async def test_change_status(self, mocker, mock_project_repository, sample_project):
        """Test changing project status."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
            updated = copy.deepcopy(sample_project)
            updated.status = ProjectStatus.PAUSED
            mock_project_repository.update = AsyncMock(return_value=updated)

            result = await service.change_status("P-TEST-001", ProjectStatus.PAUSED)

            assert isinstance(result, Ok)
            assert result.ok().status == ProjectStatus.PAUSED

    @pytest.mark.asyncio
    async def test_change_status_not_found(self, mocker, mock_project_repository):
        """Test changing status of non-existent project."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=None)

            result = await service.change_status("P-NONEXISTENT", ProjectStatus.CLOSED)

            assert isinstance(result, Err)
            assert isinstance(result.err(), NotFoundError)

    @pytest.mark.asyncio
    async def test_get_by_status(self, mocker, mock_project_repository):
        """Test getting projects by status."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            result = await service.get_by_status(ProjectStatus.ACTIVE)

            assert isinstance(result, Ok)
            assert isinstance(result.ok(), list)
            mock_project_repository.find_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_status_no_results(self, mocker, mock_project_repository):
        """Test getting projects by status when none match."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.find_by_status = AsyncMock(return_value=Ok([]))

            result = await service.get_by_status(ProjectStatus.CLOSED)

            assert isinstance(result, Ok)
            assert len(result.ok()) == 0


class TestProjectServiceQueries:
    """Tests for project query operations."""

    @pytest.mark.asyncio
    async def test_get_by_owner(self, mocker, mock_project_repository):
        """Test getting projects by owner."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            result = await service.get_by_owner("project.owner")

            assert isinstance(result, Ok)
            assert isinstance(result.ok(), list)
            mock_project_repository.find_by_owner.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_owner_no_results(self, mocker, mock_project_repository):
        """Test getting projects by owner when none match."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.find_by_owner = AsyncMock(return_value=Ok([]))

            result = await service.get_by_owner("nonexistent.owner")

            assert isinstance(result, Ok)
            assert len(result.ok()) == 0


class TestProjectServiceCRUD:
    """Tests for project CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_with_minimum_fields(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test creating project with only required fields."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            request = ProjectCreateRequest(
                id="P-MIN-001",
                name="Minimal Project",
                mission="Mission statement",
                owner="owner",
                start_date="2025-01-01",
            )

            minimal = copy.deepcopy(sample_project)
            minimal.id = "P-MIN-001"
            minimal.name = "Minimal Project"
            mock_project_repository.create = AsyncMock(return_value=minimal)

            result = await service.create(request)

            assert isinstance(result, Ok)
            assert result.ok().id == "P-MIN-001"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test creating project with all optional fields populated."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            request = ProjectCreateRequest(
                id="P-FULL-001",
                name="Full Project",
                mission="Mission statement",
                description="Description",
                status=ProjectStatus.ACTIVE,
                priority="p1",
                start_date="2025-01-01",
                target_end_date="2025-12-31",
                owner="owner",
                team_members=["m1", "m2"],
                labels=["l1", "l2"],
            )

            full = copy.deepcopy(sample_project)
            full.id = "P-FULL-001"
            full.name = "Full Project"
            mock_project_repository.create = AsyncMock(return_value=full)

            result = await service.create(request)

            assert isinstance(result, Ok)
            assert result.ok().id == "P-FULL-001"

    @pytest.mark.asyncio
    async def test_update_partial_single_field(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test updating project with only one field changed."""
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

            updated = copy.deepcopy(sample_project)
            updated.name = "Updated Name"
            mock_project_repository.update = AsyncMock(return_value=updated)

            request = ProjectUpdateRequest(name="Updated Name")
            result = await service.update("P-TEST-001", request)

            assert isinstance(result, Ok)
            assert result.ok().name == "Updated Name"
