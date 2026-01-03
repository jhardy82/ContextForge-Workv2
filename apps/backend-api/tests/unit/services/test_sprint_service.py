"""Unit tests for SprintService."""

import copy
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import SprintStatus, TaskStatus
from taskman_api.core.result import Ok
from taskman_api.services.sprint_service import SprintService


class TestSprintServiceVelocity:
    """Tests for sprint velocity calculation."""

    @pytest.mark.asyncio
    async def test_calculate_velocity(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test velocity calculation from completed tasks."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)

            # 2 completed tasks with estimate points
            task1 = copy.deepcopy(sample_task)
            task1.estimate_points = 5.0
            task1.status = TaskStatus.DONE
            task2 = copy.deepcopy(sample_task)
            task2.estimate_points = 3.0
            task2.status = TaskStatus.DONE

            mock_task_repository.find_by_sprint = AsyncMock(
                return_value=Ok([task1, task2])
            )

            result = await service.calculate_velocity("S-TEST-001")

            assert isinstance(result, Ok)
            velocity = result.ok()
            assert velocity == 8.0  # 5.0 + 3.0


class TestSprintServiceBurndown:
    """Tests for sprint burndown chart data."""

    @pytest.mark.asyncio
    async def test_get_burndown(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test burndown chart data calculation."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)

            # Total: 20 points, Completed: 10 points
            task1 = sample_task
            task1.estimate_points = 10.0
            task2 = sample_task
            task2.estimate_points = 10.0
            mock_task_repository.find_by_sprint = AsyncMock(
                side_effect=[
                    Ok([task1, task2]),  # All tasks
                    Ok([task1]),  # Completed tasks
                ]
            )

            result = await service.get_burndown("S-TEST-001")

            assert isinstance(result, Ok)
            burndown = result.ok()
            assert burndown["total_points"] == 20.0
            assert burndown["completed_points"] == 10.0
            assert burndown["remaining_points"] == 10.0
            assert "ideal_burndown_rate" in burndown
            assert "actual_burndown_rate" in burndown


class TestSprintServiceStatus:
    """Tests for sprint status operations."""

    @pytest.mark.asyncio
    async def test_change_status(self, mocker, mock_sprint_repository, sample_sprint):
        """Test changing sprint status."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)
            updated_sprint = sample_sprint
            updated_sprint.status = SprintStatus.CLOSED
            mock_sprint_repository.update = AsyncMock(return_value=updated_sprint)

            result = await service.change_status("S-TEST-001", SprintStatus.CLOSED)

            assert isinstance(result, Ok)
            sprint = result.ok()
            assert sprint.status == SprintStatus.CLOSED


class TestSprintServiceQueries:
    """Tests for sprint query operations."""

    @pytest.mark.asyncio
    async def test_get_current_sprints(self, mocker, mock_sprint_repository):
        """Test getting current sprints."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            result = await service.get_current_sprints()

            assert isinstance(result, Ok)
            sprints = result.ok()
            assert isinstance(sprints, list)
            mock_sprint_repository.find_current_sprints.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_project(self, mocker, mock_sprint_repository):
        """Test getting sprints by project."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            result = await service.get_by_project("P-TEST-001")

            assert isinstance(result, Ok)
            sprints = result.ok()
            assert isinstance(sprints, list)
            mock_sprint_repository.find_by_project.assert_called_once()


class TestSprintServiceMetrics:
    """Tests for sprint metrics updates."""

    @pytest.mark.asyncio
    async def test_update_metrics(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test updating sprint metrics."""
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)

            task1 = sample_task
            task1.estimate_points = 5.0
            mock_task_repository.find_by_sprint = AsyncMock(return_value=Ok([task1]))

            updated_sprint = sample_sprint
            updated_sprint.actual_points = 5.0
            mock_sprint_repository.update = AsyncMock(return_value=updated_sprint)

            result = await service.update_metrics("S-TEST-001")

            assert isinstance(result, Ok)
            sprint = result.ok()
            assert sprint.actual_points == 5.0
