"""Unit tests for TaskService.

Comprehensive test suite covering:
- Status transitions and validation
- Task assignments (sprint, project)
- Bulk operations
- Search functionality
"""

import copy
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.core.errors import NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.task import TaskResponse
from taskman_api.services.task_service import TaskService


class TestTaskServiceStatusTransitions:
    """Test suite for task status transitions."""

    @pytest.mark.asyncio
    async def test_new_to_ready(self, mocker, mock_task_repository, sample_task):
        """NEW -> READY is a valid transition."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Create independent copies to avoid fixture mutation
            task_with_new_status = copy.deepcopy(sample_task)
            task_with_new_status.status = TaskStatus.NEW
            # Base service uses get_by_id, returns entity directly
            mock_task_repository.get_by_id = AsyncMock(return_value=task_with_new_status)

            # Mock update with independent task copy - returns entity directly
            task_with_ready_status = copy.deepcopy(sample_task)
            task_with_ready_status.status = TaskStatus.READY
            mock_task_repository.update = AsyncMock(return_value=task_with_ready_status)

            result = await service.change_status("T-TEST-001", TaskStatus.READY)

            assert isinstance(result, Ok)
            assert result.ok().status == TaskStatus.READY

    @pytest.mark.asyncio
    async def test_in_progress_to_blocked(self, mocker, mock_task_repository, sample_task):
        """IN_PROGRESS -> BLOCKED is a valid transition."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock get() to return task with IN_PROGRESS status
            # Base service uses get_by_id, returns entity directly
            sample_task.status = TaskStatus.IN_PROGRESS
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)

            task_blocked = copy.deepcopy(sample_task)
            task_blocked.status = TaskStatus.BLOCKED
            mock_task_repository.update = AsyncMock(return_value=task_blocked)

            result = await service.change_status("T-TEST-001", TaskStatus.BLOCKED)

            if isinstance(result, Err):
                print(f"DEBUG_TEST_FAIL: {result.err()}")
            assert isinstance(result, Ok)
            assert result.ok().status == TaskStatus.BLOCKED

    @pytest.mark.asyncio
    async def test_in_progress_to_done(self, mocker, mock_task_repository, sample_task):
        """IN_PROGRESS -> DONE is a valid transition."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_in_progress = copy.deepcopy(sample_task)
            task_in_progress.status = TaskStatus.IN_PROGRESS
            mock_task_repository.get_by_id = AsyncMock(return_value=task_in_progress)

            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            mock_task_repository.update = AsyncMock(return_value=task_done)

            result = await service.change_status("T-TEST-001", TaskStatus.DONE)

            assert isinstance(result, Ok)
            assert result.ok().status == TaskStatus.DONE

    @pytest.mark.asyncio
    async def test_task_not_found(self, mocker, mock_task_repository):
        """Status change on non-existent task returns NotFoundError."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock get_by_id to return None (not found)
            # Base service checks for None and returns NotFoundError
            mock_task_repository.get_by_id = AsyncMock(return_value=None)

            result = await service.change_status("T-NONEXISTENT", TaskStatus.READY)

            assert isinstance(result, Err)
            assert isinstance(result.err(), NotFoundError)


class TestTaskServiceInvalidTransitions:
    """Test invalid status transitions (terminal states, skipped states)."""

    @pytest.mark.asyncio
    async def test_done_to_new_invalid(self, mocker, mock_task_repository, sample_task):
        """DONE -> NEW is invalid (terminal state)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            mock_task_repository.get_by_id = AsyncMock(return_value=task_done)

            result = await service.change_status("T-TEST-001", TaskStatus.NEW)

            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)
            assert "Invalid status transition" in error.message

    @pytest.mark.asyncio
    async def test_done_to_in_progress_invalid(self, mocker, mock_task_repository, sample_task):
        """DONE -> IN_PROGRESS is invalid (terminal state)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_done = copy.deepcopy(sample_task)
            task_done.status = TaskStatus.DONE
            mock_task_repository.get_by_id = AsyncMock(return_value=task_done)

            result = await service.change_status("T-TEST-001", TaskStatus.IN_PROGRESS)

            assert isinstance(result, Err)
            assert isinstance(result.err(), ValidationError)

    @pytest.mark.asyncio
    async def test_dropped_to_ready_invalid(self, mocker, mock_task_repository, sample_task):
        """DROPPED -> READY is invalid (terminal state)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_dropped = copy.deepcopy(sample_task)
            task_dropped.status = TaskStatus.DROPPED
            mock_task_repository.get_by_id = AsyncMock(return_value=task_dropped)

            result = await service.change_status("T-TEST-001", TaskStatus.READY)

            assert isinstance(result, Err)
            assert isinstance(result.err(), ValidationError)

    @pytest.mark.asyncio
    async def test_new_to_done_invalid(self, mocker, mock_task_repository, sample_task):
        """NEW -> DONE is invalid (skips intermediate states)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_new = copy.deepcopy(sample_task)
            task_new.status = TaskStatus.NEW
            mock_task_repository.get_by_id = AsyncMock(return_value=task_new)

            result = await service.change_status("T-TEST-001", TaskStatus.DONE)

            assert isinstance(result, Err)
            assert isinstance(result.err(), ValidationError)

    @pytest.mark.asyncio
    async def test_ready_to_blocked_invalid(self, mocker, mock_task_repository, sample_task):
        """READY -> BLOCKED is invalid (must be IN_PROGRESS first)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            task_ready = copy.deepcopy(sample_task)
            task_ready.status = TaskStatus.READY
            mock_task_repository.get_by_id = AsyncMock(return_value=task_ready)

            result = await service.change_status("T-TEST-001", TaskStatus.BLOCKED)

            assert isinstance(result, Err)
            assert isinstance(result.err(), ValidationError)


class TestTaskServiceStatusValidation:
    """Test internal status transition validation logic."""

    def test_new_to_ready_valid(self, mocker):
        """_is_valid_transition returns True for NEW -> READY."""
        with patch("taskman_api.services.task_service.TaskRepository"):
            service = TaskService(mocker.Mock())
            assert service._is_valid_transition(TaskStatus.NEW, TaskStatus.READY) is True

    def test_ready_to_in_progress_valid(self, mocker):
        """_is_valid_transition returns True for READY -> IN_PROGRESS."""
        with patch("taskman_api.services.task_service.TaskRepository"):
            service = TaskService(mocker.Mock())
            assert (
                service._is_valid_transition(TaskStatus.READY, TaskStatus.IN_PROGRESS) is True
            )

    def test_done_to_any_invalid(self, mocker):
        """_is_valid_transition returns False for DONE -> any state."""
        with patch("taskman_api.services.task_service.TaskRepository"):
            service = TaskService(mocker.Mock())
            assert service._is_valid_transition(TaskStatus.DONE, TaskStatus.NEW) is False
            assert service._is_valid_transition(TaskStatus.DONE, TaskStatus.IN_PROGRESS) is False
            assert service._is_valid_transition(TaskStatus.DONE, TaskStatus.DROPPED) is False


class TestTaskServiceAssignment:
    """Test task assignment operations."""

    @pytest.mark.asyncio
    async def test_assign_to_sprint(self, mocker, mock_task_repository, sample_task):
        """Successfully assign task to sprint."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock get and update
            service.task_repo = mock_task_repository
            # Mock sprint repository for validation
            mock_sprint_repo = mocker.Mock()
            mock_sprint_repo.get_by_id = AsyncMock(return_value=mocker.Mock(id="S-2025-01"))
            service.sprint_repo = mock_sprint_repo

            # Mock get and update
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
            updated_task = copy.deepcopy(sample_task)
            updated_task.primary_sprint = "S-2025-01"
            mock_task_repository.update = AsyncMock(return_value=updated_task)

            result = await service.assign_to_sprint("T-TEST-001", "S-2025-01")

            assert isinstance(result, Ok)
            assert result.ok().primary_sprint == "S-2025-01"

    @pytest.mark.asyncio
    async def test_assign_to_project(self, mocker, mock_task_repository, sample_task):
        """Successfully assign task to project."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock get and update
            service.task_repo = mock_task_repository
            # Mock project repository for validation
            mock_project_repo = mocker.Mock()
            mock_project_repo.get_by_id = AsyncMock(return_value=mocker.Mock(id="P-TASKMAN"))
            service.project_repo = mock_project_repo

            # Mock get and update
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
            updated_task = copy.deepcopy(sample_task)
            updated_task.primary_project = "P-TASKMAN"
            mock_task_repository.update = AsyncMock(return_value=updated_task)

            result = await service.assign_to_project("T-TEST-001", "P-TASKMAN")

            assert isinstance(result, Ok)
            assert result.ok().primary_project == "P-TASKMAN"

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_sprint(self, mocker, mock_task_repository, sample_task):
        """Assignment to non-existent sprint returns error."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository
            service.sprint_repo = mocker.Mock()
            service.sprint_repo.get_by_id = AsyncMock(return_value=None)

            mock_task_repository.find_by_id = AsyncMock(return_value=sample_task)
            mock_task_repository.update = AsyncMock(
                return_value=Err(
                    ValidationError(
                        message="Sprint not found",
                        field="primary_sprint",
                        value="S-NONEXISTENT",
                    )
                )
            )

            result = await service.assign_to_sprint("T-TEST-001", "S-NONEXISTENT")

            assert isinstance(result, Err)
            # Expect NotFoundError because sprint doesn't exist (get_by_id returned None)
            assert isinstance(result.err(), NotFoundError)

    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_project(self, mocker, mock_task_repository, sample_task):
        """Assignment to non-existent project returns error."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository
            service.project_repo = mocker.Mock()
            service.project_repo.get_by_id = AsyncMock(return_value=None)

            mock_task_repository.find_by_id = AsyncMock(return_value=sample_task)
            mock_task_repository.update = AsyncMock(
                return_value=Err(
                    ValidationError(
                        message="Project not found",
                        field="primary_project",
                        value="P-NONEXISTENT",
                    )
                )
            )

            result = await service.assign_to_project("T-TEST-001", "P-NONEXISTENT")

            assert isinstance(result, Err)
            # Expect NotFoundError because project doesn't exist (get_by_id returned None)
            assert isinstance(result.err(), NotFoundError)


class TestTaskServiceBulkOperations:
    """Test bulk update operations."""

    @pytest.mark.asyncio
    async def test_bulk_update_success(self, mocker, mock_task_repository, sample_task):
        """Successfully update multiple tasks."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock get and update for each task
            mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
            mock_task_repository.update = AsyncMock(return_value=sample_task)

            updates = [
                {"id": "T-001", "status": "in_progress"},
                {"id": "T-002", "priority": "p1"},
            ]

            result = await service.bulk_update(updates)

            assert isinstance(result, Ok)
            tasks = result.ok()
            assert len(tasks) == 2
            assert all(isinstance(task, TaskResponse) for task in tasks)

    @pytest.mark.asyncio
    async def test_bulk_update_fails_fast(self, mocker, mock_task_repository, sample_task):
        """Bulk update stops on first error (fail-fast behavior)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # First task succeeds, second task fails
            mock_task_repository.get_by_id = AsyncMock(
                side_effect=[
                    sample_task,  # First call succeeds
                    None,  # Second call fails
                ]
            )
            mock_task_repository.update = AsyncMock(return_value=sample_task)

            updates = [
                {"id": "T-001", "status": "in_progress"},
                {"id": "T-002", "status": "done"},
                {"id": "T-003", "status": "blocked"},  # Should not be processed
            ]

            result = await service.bulk_update(updates)

            assert isinstance(result, Err)
            assert isinstance(result.err(), NotFoundError)
            assert mock_task_repository.get_by_id.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_update_empty_list(self, mocker, mock_task_repository):
        """Bulk update with empty list returns empty result."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            result = await service.bulk_update([])

            assert isinstance(result, Ok)
            assert result.ok() == []


class TestTaskServiceSearch:
    """Test task search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_status(self, mocker, mock_task_repository, sample_task):
        """Search tasks by status."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock search
            tasks = [sample_task, sample_task]
            mock_task_repository.search = AsyncMock(return_value=(tasks, 2))

            # Act
            result = await service.search(status=TaskStatus.IN_PROGRESS, limit=50)

            assert isinstance(result, Ok)
            responses, total = result.ok()
            assert isinstance(responses, list)
            assert total == 2
            mock_task_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_status_and_priority(self, mocker, mock_task_repository, sample_task):
        """Search tasks by status and priority."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            # Mock search
            tasks = [sample_task, sample_task]
            mock_task_repository.find_by_status_and_priority = AsyncMock(return_value=tasks)

            # Mock search
            tasks = [sample_task, sample_task]
            mock_task_repository.search = AsyncMock(return_value=(tasks, 2))

            # Act
            result = await service.search(
                status=TaskStatus.IN_PROGRESS, priority=Priority.P1
            )

            assert isinstance(result, Ok)
            responses, total = result.ok()
            assert isinstance(responses, list)
            assert total == 2
            mock_task_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_high_priority_tasks(self, mocker, mock_task_repository, sample_task):
        """Get high priority tasks (P0, P1)."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository
            # Mock find_high_priority_tasks
            tasks = [sample_task, sample_task]
            mock_task_repository.find_high_priority_tasks = AsyncMock(return_value=tasks)

            result = await service.get_high_priority_tasks(limit=20)

            assert isinstance(result, Ok)
            mock_task_repository.find_high_priority_tasks.assert_called_once_with(20, 0)

    @pytest.mark.asyncio
    async def test_get_blocked_tasks(self, mocker, mock_task_repository, sample_task):
        """Get blocked tasks."""
        with patch("taskman_api.services.task_service.TaskRepository") as MockRepo:
            MockRepo.return_value = mock_task_repository

            service = TaskService(mocker.Mock())
            service.repository = mock_task_repository
            service.task_repo = mock_task_repository

            result = await service.get_blocked_tasks()

            assert isinstance(result, Ok)
            mock_task_repository.find_by_status.assert_called_once_with(
                TaskStatus.BLOCKED, 100, 0
            )
