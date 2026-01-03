"""Unit tests for TaskService edge cases.

Tests status transition validation, boundary conditions, and error paths.
"""

import copy
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import TaskStatus
from taskman_api.core.errors import NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.services.task_service import TaskService


class TestTaskServiceStatusTransitionEdgeCases:
    """Test suite for status transition edge cases and validation."""

    @pytest.mark.asyncio
    async def test_valid_transition_new_to_ready(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test valid transition from NEW to READY."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Create task in NEW status
            task_new = copy.deepcopy(sample_task)
            task_new.status = TaskStatus.NEW
            # Base service uses get_by_id, returns entity directly
            mock_task_repository.get_by_id = AsyncMock(return_value=task_new)

            # Mock update to return task in READY status
            task_ready = copy.deepcopy(sample_task)
            task_ready.status = TaskStatus.READY
            mock_task_repository.update = AsyncMock(return_value=task_ready)

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.READY)

            # Assert
            assert isinstance(result, Ok)
            task_response = result.ok()
            assert task_response.status == TaskStatus.READY

    @pytest.mark.asyncio
    async def test_valid_transition_in_progress_to_blocked(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test valid transition from IN_PROGRESS to BLOCKED."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in IN_PROGRESS status
            task_in_progress = copy.deepcopy(sample_task)
            task_in_progress.status = TaskStatus.IN_PROGRESS
            # Base service uses get_by_id, returns entity directly
            mock_task_repository.get_by_id = AsyncMock(return_value=task_in_progress)

            # Mock update to return BLOCKED task
            task_blocked = copy.deepcopy(sample_task)
            task_blocked.status = TaskStatus.BLOCKED
            mock_task_repository.update = AsyncMock(return_value=task_blocked)

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.BLOCKED)

            # Assert
            assert isinstance(result, Ok)
            task_response = result.ok()
            assert task_response.status == TaskStatus.BLOCKED

    @pytest.mark.asyncio
    async def test_valid_transition_in_progress_to_done(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test valid transition from IN_PROGRESS to DONE."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in IN_PROGRESS status
            task_in_progress = copy.deepcopy(sample_task)
            task_in_progress.status = TaskStatus.IN_PROGRESS
            # Base service uses get_by_id, returns entity directly
            mock_task_repository.get_by_id = AsyncMock(return_value=task_in_progress)

            # Mock update to return DONE task
            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            mock_task_repository.update = AsyncMock(return_value=task_done)

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.DONE)

            # Assert
            assert isinstance(result, Ok)
            task_response = result.ok()
            assert task_response.status == TaskStatus.DONE

    @pytest.mark.asyncio
    async def test_invalid_transition_done_to_new(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test invalid transition from DONE (terminal state) to NEW.

        DONE is a terminal state - no transitions allowed.
        """
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in DONE status (terminal state)
            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            # Base service uses get_by_id, returns entity directly
            mock_task_repository.get_by_id = AsyncMock(return_value=task_done)

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.NEW)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message
            assert "done -> new" in error.message.lower()

    @pytest.mark.asyncio
    async def test_invalid_transition_done_to_in_progress(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test invalid transition from DONE (terminal state) to IN_PROGRESS."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in DONE status (terminal state)
            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            mock_task_repository.find_by_id = AsyncMock(return_value=Ok(task_done))

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.IN_PROGRESS)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message

    @pytest.mark.asyncio
    async def test_invalid_transition_dropped_to_ready(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test invalid transition from DROPPED (terminal state) to READY."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in DROPPED status (terminal state)
            task_dropped = copy.deepcopy(sample_task)
            task_dropped.status = TaskStatus.DROPPED
            mock_task_repository.get_by_id = AsyncMock(return_value=task_dropped)

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.READY)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message

    @pytest.mark.asyncio
    async def test_invalid_transition_new_to_done(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test invalid transition from NEW to DONE (skip intermediate states)."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in NEW status
            task_new = copy.deepcopy(sample_task)
            task_new.status = TaskStatus.NEW
            mock_task_repository.find_by_id = AsyncMock(return_value=Ok(task_new))

            # Act - attempt to jump directly to DONE
            result = await service.change_status("T-TEST-001", TaskStatus.DONE)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message

    @pytest.mark.asyncio
    async def test_invalid_transition_ready_to_blocked(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test invalid transition from READY to BLOCKED (must be IN_PROGRESS first)."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Task in READY status
            task_ready = copy.deepcopy(sample_task)
            task_ready.status = TaskStatus.READY
            mock_task_repository.find_by_id = AsyncMock(return_value=Ok(task_ready))

            # Act
            result = await service.change_status("T-TEST-001", TaskStatus.BLOCKED)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message


class TestTaskServiceBulkOperationEdgeCases:
    """Test suite for bulk operation edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_bulk_update_partial_failure_fails_fast(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test bulk update fails on first error and doesn't continue.

        Ensures fail-fast behavior: if task 2 fails, task 3 should not be processed.
        """
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # First task succeeds, second task fails (not found)
            mock_task_repository.get_by_id = AsyncMock(
                side_effect=[
                    sample_task,  # Task 1 found
                    None,  # Task 2 not found
                ]
            )
            mock_task_repository.update = AsyncMock(return_value=sample_task)

            updates = [
                {"id": "T-001", "status": "in_progress"},
                {"id": "T-NONEXISTENT", "status": "done"},  # This will fail
                {"id": "T-003", "status": "blocked"},  # This should not be processed
            ]

            # Act
            result = await service.bulk_update(updates)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, NotFoundError)
            # Verify only 2 calls - fail-fast behavior
            assert mock_task_repository.get_by_id.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_update_empty_list(self, mocker, mock_task_repository):
        """Test bulk update with empty list returns empty result."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Act
            result = await service.bulk_update([])

            # Assert
            assert isinstance(result, Ok)
            tasks = result.ok()
            assert isinstance(tasks, list)
            assert len(tasks) == 0


class TestTaskServiceAssignmentEdgeCases:
    """Test suite for task assignment edge cases."""

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_sprint(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test assigning task to non-existent sprint propagates error."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock dependencies
            mock_sprint_repo = mocker.Mock()
            mock_sprint_repo.get_by_id = AsyncMock(return_value=None)
            service.sprint_repo = mock_sprint_repo

            # Task exists
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
            # Use real update logic but it won't be reached because of sprint check
            mock_task_repository.update = AsyncMock()

            # Act
            result = await service.assign_to_sprint("T-TEST-001", "S-NONEXISTENT")

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, NotFoundError)

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_project(
        self, mocker, mock_task_repository, sample_task
    ):
        """Test assigning task to non-existent project propagates error."""
        # Arrange
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock dependencies
            mock_project_repo = mocker.Mock()
            mock_project_repo.get_by_id = AsyncMock(return_value=None)
            service.project_repo = mock_project_repo

            # Task exists
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
            # Use real update logic but it won't be reached
            mock_task_repository.update = AsyncMock()

            # Act
            result = await service.assign_to_project("T-TEST-001", "P-NONEXISTENT")

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, NotFoundError)
