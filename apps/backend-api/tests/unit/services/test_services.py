"""Unit tests for Project, Sprint, and ActionList services.

Consolidated test suite for remaining service layer classes.
"""

import copy
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.enums import ProjectStatus, SprintStatus, TaskStatus
from taskman_api.core.errors import ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.action_list import ActionListAddItemRequest, ReorderItemsRequest
from taskman_api.services.action_list_service import ActionListService
from taskman_api.services.project_service import ProjectService
from taskman_api.services.sprint_service import SprintService


class TestProjectService:
    """Test suite for ProjectService."""

    @pytest.mark.asyncio
    async def test_get_metrics_success(
        self, mocker, mock_project_repository, mock_task_repository, sample_project, sample_task
    ):
        """Test successful metrics calculation."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockProjRepo, \
             patch("taskman_api.services.project_service.TaskRepository") as MockTaskRepo:
            MockProjRepo.return_value = mock_project_repository
            MockTaskRepo.return_value = mock_task_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository
            service.task_repo = mock_task_repository

            # Mock get project
            mock_project_repository.find_by_id = AsyncMock(return_value=Ok(sample_project))

            # Mock get tasks (3 tasks: 1 done, 1 in_progress, 1 blocked)
            import copy
            task1 = copy.deepcopy(sample_task)
            task1.status = TaskStatus.DONE

            task2 = copy.deepcopy(sample_task)
            task2.status = TaskStatus.IN_PROGRESS

            task3 = copy.deepcopy(sample_task)
            task3.status = TaskStatus.BLOCKED

            mock_task_repository.find_by_project = AsyncMock(
                return_value=Ok([task1, task2, task3])
            )

            # Act
            result = await service.get_metrics("P-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            metrics = result.ok()
            assert metrics["total_tasks"] == 3
            assert "done" in metrics["tasks_by_status"]
            assert "health_status" in metrics
            assert "completion_percentage" in metrics

    @pytest.mark.asyncio
    async def test_add_sprint(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test adding sprint to project."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get project
            mock_project_repository.find_by_id = AsyncMock(return_value=Ok(sample_project))

            # Mock update
            updated_project = sample_project
            updated_project.sprints = ["S-TEST-001", "S-2025-01"]
            mock_project_repository.update = AsyncMock(return_value=updated_project)

            # Act
            result = await service.add_sprint("P-TEST-001", "S-2025-01")

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert "S-2025-01" in project.sprints

    @pytest.mark.asyncio
    async def test_remove_sprint(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test removing sprint from project."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get project with 2 sprints
            sample_project.sprints = ["S-TEST-001", "S-TEST-002"]
            mock_project_repository.find_by_id = AsyncMock(return_value=Ok(sample_project))

            # Mock update
            updated_project = sample_project
            updated_project.sprints = ["S-TEST-001"]
            mock_project_repository.update = AsyncMock(return_value=updated_project)

            # Act
            result = await service.remove_sprint("P-TEST-001", "S-TEST-002")

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert "S-TEST-002" not in project.sprints

    @pytest.mark.asyncio
    async def test_change_status(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test changing project status."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Mock get and update - base service uses get_by_id, not find_by_id
            # Repository methods return entities directly, not Ok-wrapped
            mock_project_repository.get_by_id = AsyncMock(return_value=sample_project)
            updated_project = sample_project
            updated_project.status = ProjectStatus.PAUSED
            mock_project_repository.update = AsyncMock(return_value=updated_project)

            # Act
            result = await service.change_status("P-TEST-001", ProjectStatus.PAUSED)

            # Assert
            assert isinstance(result, Ok)
            project = result.ok()
            assert project.status == ProjectStatus.PAUSED

    @pytest.mark.asyncio
    async def test_get_by_status(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test getting projects by status."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Act
            result = await service.get_by_status(ProjectStatus.ACTIVE)

            # Assert
            assert isinstance(result, Ok)
            projects = result.ok()
            assert isinstance(projects, list)
            mock_project_repository.find_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_owner(
        self, mocker, mock_project_repository, sample_project
    ):
        """Test getting projects by owner."""
        # Arrange
        with patch("taskman_api.services.project_service.ProjectRepository") as MockRepo, \
             patch("taskman_api.services.project_service.TaskRepository"):
            MockRepo.return_value = mock_project_repository

            service = ProjectService(mocker.Mock())
            service.repository = mock_project_repository
            service.project_repo = mock_project_repository

            # Act
            result = await service.get_by_owner("project.owner")

            # Assert
            assert isinstance(result, Ok)
            projects = result.ok()
            assert isinstance(projects, list)
            mock_project_repository.find_by_owner.assert_called_once()


class TestSprintService:
    """Test suite for SprintService."""

    @pytest.mark.asyncio
    async def test_calculate_velocity(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test velocity calculation from completed tasks."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            # Mock get sprint
            mock_sprint_repository.find_by_id = AsyncMock(return_value=Ok(sample_sprint))

            # Mock get completed tasks with estimate_points
            import copy
            task1 = copy.deepcopy(sample_task)
            task1.estimate_points = 5.0
            task1.status = TaskStatus.DONE

            task2 = copy.deepcopy(sample_task)
            task2.estimate_points = 3.0
            task2.status = TaskStatus.DONE

            mock_task_repository.find_by_sprint = AsyncMock(
                return_value=Ok([task1, task2])
            )

            # Act
            result = await service.calculate_velocity("S-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            velocity = result.ok()
            assert velocity == 8.0  # 5.0 + 3.0

    @pytest.mark.asyncio
    async def test_get_burndown(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test burndown chart data calculation."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            # Mock get sprint
            mock_sprint_repository.find_by_id = AsyncMock(return_value=Ok(sample_sprint))

            # Mock all tasks (total: 20 points)
            task1 = sample_task
            task1.estimate_points = 10.0
            task2 = sample_task
            task2.estimate_points = 10.0
            mock_task_repository.find_by_sprint = AsyncMock(
                side_effect=[
                    Ok([task1, task2]),  # All tasks
                    Ok([task1]),  # Completed tasks (10 points)
                ]
            )

            # Act
            result = await service.get_burndown("S-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            burndown = result.ok()
            assert burndown["total_points"] == 20.0
            assert burndown["completed_points"] == 10.0
            assert burndown["remaining_points"] == 10.0
            assert "ideal_burndown_rate" in burndown
            assert "actual_burndown_rate" in burndown

    @pytest.mark.asyncio
    async def test_change_status(
        self, mocker, mock_sprint_repository, sample_sprint
    ):
        """Test changing sprint status."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            # Mock get and update - base service uses get_by_id, not find_by_id
            # Repository methods return entities directly, not Ok-wrapped
            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)
            updated_sprint = sample_sprint
            updated_sprint.status = SprintStatus.COMPLETED
            mock_sprint_repository.update = AsyncMock(return_value=updated_sprint)

            # Act
            result = await service.change_status("S-TEST-001", SprintStatus.COMPLETED)

            # Assert
            assert isinstance(result, Ok)
            sprint = result.ok()
            assert sprint.status == SprintStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_current_sprints(
        self, mocker, mock_sprint_repository, sample_sprint
    ):
        """Test getting current sprints."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            # Act
            result = await service.get_current_sprints()

            # Assert
            assert isinstance(result, Ok)
            sprints = result.ok()
            assert isinstance(sprints, list)
            mock_sprint_repository.find_current_sprints.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_project(
        self, mocker, mock_sprint_repository, sample_sprint
    ):
        """Test getting sprints by project."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository"):
            MockRepo.return_value = mock_sprint_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository

            # Act
            result = await service.get_by_project("P-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            sprints = result.ok()
            assert isinstance(sprints, list)
            mock_sprint_repository.find_by_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_metrics(
        self, mocker, mock_sprint_repository, mock_task_repository, sample_sprint, sample_task
    ):
        """Test updating sprint metrics."""
        # Arrange
        with patch("taskman_api.services.sprint_service.SprintRepository") as MockSprintRepo, \
             patch("taskman_api.services.sprint_service.TaskRepository") as MockTaskRepo:
            MockSprintRepo.return_value = mock_sprint_repository
            MockTaskRepo.return_value = mock_task_repository

            service = SprintService(mocker.Mock())
            service.repository = mock_sprint_repository
            service.sprint_repo = mock_sprint_repository
            service.task_repo = mock_task_repository

            # Mock get sprint - base service uses get_by_id
            mock_sprint_repository.get_by_id = AsyncMock(return_value=sample_sprint)

            # Mock completed tasks - get_by_sprint returns entities, not Ok-wrapped
            task1 = sample_task
            task1.estimate_points = 5.0
            mock_task_repository.get_by_sprint = AsyncMock(return_value=[task1])

            # Mock update - returns entity directly
            updated_sprint = sample_sprint
            updated_sprint.actual_points = 5.0
            mock_sprint_repository.update = AsyncMock(return_value=updated_sprint)

            # Act
            result = await service.update_metrics("S-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            sprint = result.ok()
            assert sprint.actual_points == 5.0


class TestActionListService:
    """Test suite for ActionListService."""

    @pytest.mark.asyncio
    async def test_reorder_items_success(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test successful item reordering."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Mock get action list with 3 task IDs
            sample_action_list.task_ids = ["T1", "T2", "T3"]
            sample_action_list.tags = []
            sample_action_list.evidence_refs = []
            sample_action_list.extra_metadata = {}
            sample_action_list.parent_deletion_note = {}
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )  # Mock update
            reordered_list = copy.deepcopy(sample_action_list)
            reordered_list.task_ids = ["T3", "T1", "T2"]
            mock_action_list_repository.update = AsyncMock(return_value=reordered_list)

            # Act - reorder ["T1", "T2", "T3"] → ["T3", "T1", "T2"]
            reorder_request = ReorderItemsRequest(item_ids=["T3", "T1", "T2"])
            result = await service.reorder_items("AL-TEST-001", reorder_request)

            # Assert
            assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_reorder_items_invalid_length(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test reorder with mismatched item count."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Mock get action list with 2 items
            sample_action_list.task_ids = ["T1", "T2"]
            sample_action_list.tags = []
            sample_action_list.evidence_refs = []
            sample_action_list.extra_metadata = {}
            sample_action_list.parent_deletion_note = {}
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )  # Act - try to reorder with 3 IDs (but only 2 exist)
            reorder_request = ReorderItemsRequest(item_ids=["T1", "T2", "T3"])
            result = await service.reorder_items("AL-TEST-001", reorder_request)

            # Assert
            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)

    @pytest.mark.skip(reason="Method mark_complete not implemented - ADR-001 backlog")
    @pytest.mark.asyncio
    async def test_mark_complete(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test marking action list as complete."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Mock get and update
            mock_action_list_repository.find_by_id = AsyncMock(
                return_value=Ok(sample_action_list)
            )
            updated_list = sample_action_list
            updated_list.status = "completed"
            updated_list.completed_at = datetime.utcnow()
            mock_action_list_repository.update = AsyncMock(
                return_value=Ok(updated_list)
            )

            # Act
            result = await service.mark_complete("AL-TEST-001")

            # Assert
            assert isinstance(result, Ok)
            action_list = result.ok()
            assert action_list.status == "completed"
            assert action_list.completed_at is not None

    @pytest.mark.asyncio
    async def test_add_item(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test adding item to action list."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Mock get and update
            sample_action_list.task_ids = ["T1"]
            sample_action_list.tags = []
            sample_action_list.evidence_refs = []
            sample_action_list.extra_metadata = {}
            sample_action_list.parent_deletion_note = {}
            mock_action_list_repository.get_by_id = AsyncMock(return_value=sample_action_list)
            updated_list = copy.deepcopy(sample_action_list)
            updated_list.task_ids = ["T1", "T2"]
            mock_action_list_repository.add_task = AsyncMock(return_value=updated_list)

            # Act
            add_request = ActionListAddItemRequest(text="Item 2", order=1)
            result = await service.add_item("AL-TEST-001", add_request)

            # Assert
            if isinstance(result, Err):
                print(f"\nDEBUG: result={result.err()}")
            assert isinstance(result, Ok)
            action_list = result.ok()
            assert len(action_list.items) == 2

    @pytest.mark.asyncio
    async def test_remove_item(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test removing item from action list."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Mock get and update
            sample_action_list.task_ids = ["T1", "T2"]
            sample_action_list.tags = []
            sample_action_list.evidence_refs = []
            sample_action_list.extra_metadata = {}
            sample_action_list.parent_deletion_note = {}
            mock_action_list_repository.get_by_id = AsyncMock(return_value=sample_action_list)
            updated_list = copy.deepcopy(sample_action_list)
            updated_list.task_ids = ["T1"]
            mock_action_list_repository.remove_task = AsyncMock(return_value=updated_list)

            # Act - remove item "T2"
            result = await service.remove_item("AL-TEST-001", "T2")

            # Assert
            if isinstance(result, Err):
                print(f"\nDEBUG: result={result.err()}")
            assert isinstance(result, Ok)
            action_list = result.ok()
            assert len(action_list.items) == 1

    @pytest.mark.skip(reason="Method get_orphaned not implemented - ADR-001 backlog")
    @pytest.mark.asyncio
    async def test_get_orphaned(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test getting orphaned action lists."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Act
            result = await service.get_orphaned()

            # Assert
            assert isinstance(result, Ok)
            action_lists = result.ok()
            assert isinstance(action_lists, list)
            mock_action_list_repository.find_orphaned.assert_called_once()

    @pytest.mark.skip(reason="Method get_soft_deleted not implemented - ADR-001 backlog")
    @pytest.mark.asyncio
    async def test_get_soft_deleted(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test getting soft-deleted action lists."""
        # Arrange
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            # Act
            result = await service.get_soft_deleted()

            # Assert
            assert isinstance(result, Ok)
            action_lists = result.ok()
            assert isinstance(action_lists, list)
            mock_action_list_repository.find_soft_deleted.assert_called_once()
