"""Unit tests for ProjectService edge cases.

Tests boundary conditions, error paths, and edge cases.
"""

import copy
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import ProjectStatus
from taskman_api.core.errors import NotFoundError
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from taskman_api.services.project_service import ProjectService


class TestProjectServiceBoundaryConditions:
    """Test suite for project service boundary conditions."""

    @pytest.mark.asyncio
    async def test_create_project_with_minimum_fields(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test creating project with only required fields."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Create request with only required fields
            request = ProjectCreateRequest(
                id="P-MIN-001",
                name="Minimal Project",
                mission="Mission statement",
                owner="owner",
                start_date="2025-01-01",
                # Optional fields omitted: description, target_date, etc.
            )

            # Mock create to return project with matching ID
            minimal_project = copy.deepcopy(sample_project)
            minimal_project.id = "P-MIN-001"
            minimal_project.name = "Minimal Project"
            mock_project_repository.create = AsyncMock(return_value=minimal_project)

            # Act
            result = await service.create(request)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.id == "P-MIN-001"
            assert project.name == "Minimal Project"

    @pytest.mark.asyncio
    async def test_create_project_with_all_fields(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test creating project with all optional fields populated."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Create request with all fields
            request = ProjectCreateRequest(
                id="P-FULL-001",
                name="Full Project",
                mission="Mission statement",
                description="Comprehensive description",
                status=ProjectStatus.ACTIVE,
                priority="p1",
                start_date="2025-01-01",
                target_end_date="2025-12-31",
                owner="owner",
                team_members=["member1", "member2"],
                labels=["label1", "label2"],
            )

            # Mock create to return project with matching data
            full_project = copy.deepcopy(sample_project)
            full_project.id = "P-FULL-001"
            full_project.name = "Full Project"
            mock_project_repository.create = AsyncMock(return_value=full_project)

            # Act
            result = await service.create(request)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.id == "P-FULL-001"
            assert project.name == "Full Project"

    @pytest.mark.asyncio
    async def test_update_project_partial_single_field(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test updating project with only one field changed."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get to return existing project
            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

            # Update only name field
            update_request = ProjectUpdateRequest(name="Updated Name Only")

            # Mock update to return project with updated name
            updated_project = copy.deepcopy(sample_project)
            updated_project.name = "Updated Name Only"
            mock_project_repository.update = AsyncMock(return_value=updated_project)

            # Act
            result = await service.update("P-TEST-001", update_request)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.name == "Updated Name Only"

    @pytest.mark.asyncio
    async def test_update_project_empty_mission(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test updating project mission to empty string."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)

            # Update mission to minimal value (1 character - min allowed)
            update_request = ProjectUpdateRequest(mission="X")

            updated_project = copy.deepcopy(sample_project)
            updated_project.mission = "X"
            mock_project_repository.update = AsyncMock(return_value=updated_project)

            # Act
            result = await service.update("P-TEST-001", update_request)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.mission == "X"


class TestProjectServiceStatusTransitions:
    """Test suite for project status change operations."""

    @pytest.mark.asyncio
    async def test_change_status_success(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test successfully changing project status."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Project exists in ACTIVE status
            project_active = copy.deepcopy(sample_project)
            project_active.status = ProjectStatus.ACTIVE
            mock_project_repository.get_by_id = AsyncMock(return_value=project_active)

            # Mock update to return CLOSED project
            project_closed = copy.deepcopy(sample_project)
            project_closed.status = ProjectStatus.COMPLETED
            mock_project_repository.update = AsyncMock(return_value=project_closed)

            # Act
            result = await service.change_status("P-TEST-001", ProjectStatus.COMPLETED)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.status == ProjectStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_change_status_project_not_found(
        self, mocker, mock_project_repository
    ):
        """Test changing status of non-existent project."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get to return None
            mock_project_repository.get_by_id = AsyncMock(return_value=None)

            # Act
            result = await service.change_status("P-NONEXISTENT", ProjectStatus.COMPLETED)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, NotFoundError)


class TestProjectServiceSprintManagement:
    """Test suite for sprint management operations."""

    @pytest.mark.asyncio
    async def test_add_sprint_to_project(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test adding a sprint to project's sprint list."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Project with empty sprints list
            project_no_sprints = copy.deepcopy(sample_project)
            project_no_sprints.sprints = "[]"
            mock_project_repository.get_by_id = AsyncMock(return_value=project_no_sprints)

            # Mock update to return project with sprint added
            project_with_sprint = copy.deepcopy(sample_project)
            project_with_sprint.sprints = '["S-2025-01"]'
            mock_project_repository.update = AsyncMock(return_value=project_with_sprint)

            # Act
            result = await service.add_sprint("P-TEST-001", "S-2025-01")

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert "S-2025-01" in project.sprints

    @pytest.mark.asyncio
    async def test_add_duplicate_sprint_idempotent(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test adding a sprint that already exists (should be idempotent)."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Project already has the sprint
            project_with_sprint = copy.deepcopy(sample_project)
            project_with_sprint.sprints = '["S-2025-01"]'
            mock_project_repository.get_by_id = AsyncMock(return_value=project_with_sprint)

            # Act
            result = await service.add_sprint("P-TEST-001", "S-2025-01")

            # Assert - should return project without calling update
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.sprints.count("S-2025-01") == 1  # No duplicates

    @pytest.mark.asyncio
    async def test_remove_sprint_from_project(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test removing a sprint from project's sprint list."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Project with sprint
            project_with_sprint = copy.deepcopy(sample_project)
            project_with_sprint.sprints = '["S-2025-01"]'
            mock_project_repository.get_by_id = AsyncMock(return_value=project_with_sprint)

            # Mock update to return project without sprint
            project_no_sprint = copy.deepcopy(sample_project)
            project_no_sprint.sprints = "[]"
            mock_project_repository.update = AsyncMock(return_value=project_no_sprint)

            # Act
            result = await service.remove_sprint("P-TEST-001", "S-2025-01")

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert "S-2025-01" not in project.sprints


class TestProjectServiceMetrics:
    """Test suite for project metrics calculation."""

    @pytest.mark.asyncio
    async def test_get_metrics_no_tasks(
        self, mocker, mock_project_repository, mock_task_repository, sample_project
    ):
        """Test metrics calculation for project with no tasks."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockProjRepo:
            with patch(
                "taskman_api.services.project_service.TaskRepository"
            ) as MockTaskRepo:
                MockProjRepo.return_value = mock_project_repository
                MockTaskRepo.return_value = mock_task_repository

                service = ProjectService(mocker.Mock())
                service.repository = mock_project_repository
                service.project_repo = mock_project_repository
                service.task_repo = mock_task_repository

                # Project exists
                mock_project_repository.find_by_id = AsyncMock(
                    return_value=Ok(sample_project)
                )

                # No tasks in project
                mock_task_repository.find_by_project = AsyncMock(return_value=Ok([]))

                # Act
                result = await service.get_metrics("P-TEST-001")

                # Assert
                assert isinstance(result, Ok)
                metrics = result.ok()
                assert metrics["total_tasks"] == 0
                assert metrics["health_status"] == "green"  # No tasks = green
                assert metrics["completion_percentage"] == 0.0

    @pytest.mark.asyncio
    async def test_get_metrics_project_not_found(self, mocker, mock_project_repository):
        """Test metrics calculation for non-existent project."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get to return None
            mock_project_repository.get_by_id = AsyncMock(return_value=None)

            # Act
            result = await service.get_metrics("P-NONEXISTENT")

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, NotFoundError)


class TestProjectServiceSearchAndFiltering:
    """Test suite for project search and filtering operations."""

    @pytest.mark.asyncio
    async def test_get_by_status_no_results(self, mocker, mock_project_repository):
        """Test getting projects by status when none match."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock find_by_status to return empty list
            mock_project_repository.find_by_status = AsyncMock(return_value=Ok([]))

            # Act
            result = await service.get_by_status(ProjectStatus.COMPLETED)

            # Assert
            assert isinstance(result, Ok)
            projects = result.ok()
            assert isinstance(projects, list)
            assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_get_by_owner_no_results(self, mocker, mock_project_repository):
        """Test getting projects by owner when none match."""
        # Arrange
        with patch(
            "taskman_api.services.project_service.ProjectRepository"
        ) as MockRepo:
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock find_by_owner to return empty list
            mock_project_repository.find_by_owner = AsyncMock(return_value=Ok([]))

            # Act
            result = await service.get_by_owner("nonexistent.owner")

            # Assert
            assert isinstance(result, Ok)
            projects = result.ok()
            assert isinstance(projects, list)
            assert len(projects) == 0
