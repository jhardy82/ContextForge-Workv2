"""Unit tests for BaseService.

Tests generic CRUD operations with mock repositories.
"""


import pytest

from taskman_api.core.enums import Priority
from taskman_api.core.errors import AppError, ConflictError, NotFoundError
from taskman_api.core.result import Err, Ok
from taskman_api.models.task import Task
from taskman_api.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from taskman_api.services.base import BaseService


class TestBaseServiceCreate:
    """Test suite for BaseService.create()."""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_task_repository, sample_task):
        """Test successful entity creation."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)
        request = TaskCreateRequest(
            id="T-TEST-001",
            title="Test Task",
            summary="Summary",
            description="Description",
            owner="test.owner",
            priority=Priority.P1,
            primary_project="P-TEST-001",
            primary_sprint="S-TEST-001",
        )

        # Mock repository to return entity directly
        mock_task_repository.create.return_value = sample_task

        # Act
        result = await service.create(request)

        # Assert
        assert isinstance(result, Ok)
        task_response = result.ok()
        assert isinstance(task_response, TaskResponse)
        assert task_response.id == "T-TEST-001"
        mock_task_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conflict_error(self, mock_task_repository):
        """Test creation with duplicate ID returns AppError (wrapping logic)."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)
        request = TaskCreateRequest(
            id="T-DUPLICATE",
            title="Task",
            summary="Summary",
            description="Description",
            owner="owner",
            priority=Priority.P1,
            primary_project="P-001",
            primary_sprint="S-001",
        )

        # Mock repository to raise ConflictError
        mock_task_repository.create.side_effect = ConflictError(
            message="Entity already exists",
            entity_type="Task",
            entity_id="T-DUPLICATE",
        )

        # Act
        result = await service.create(request)

        # Assert
        assert isinstance(result, Err)
        error = result.err()
        # BaseService wraps exceptions in AppError
        assert isinstance(error, AppError)
        assert "Entity already exists" in error.message


class TestBaseServiceGet:
    """Test suite for BaseService.get()."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_task_repository, sample_task):
        """Test successful entity retrieval."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return entity directly
        mock_task_repository.get_by_id.return_value = sample_task

        # Act
        result = await service.get("T-TEST-001")

        # Assert
        assert isinstance(result, Ok)
        task_response = result.ok()
        assert isinstance(task_response, TaskResponse)
        assert task_response.id == "T-TEST-001"
        mock_task_repository.get_by_id.assert_called_once_with("T-TEST-001")

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_task_repository):
        """Test get with non-existent ID returns NotFoundError."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return None (BaseRepository.get_by_id returns T | None)
        mock_task_repository.get_by_id.return_value = None

        # Act
        result = await service.get("T-NONEXISTENT")

        # Assert
        assert isinstance(result, Err)
        error = result.err()
        assert isinstance(error, NotFoundError)
        assert error.extra.get("entity_id") == "T-NONEXISTENT"


class TestBaseServiceUpdate:
    """Test suite for BaseService.update()."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_task_repository, sample_task):
        """Test successful entity update."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)
        update_request = TaskUpdateRequest(title="Updated Title")

        # Mock get_by_id to return entity for retrieval
        mock_task_repository.get_by_id.return_value = sample_task
        # Mock update to return updated entity
        mock_task_repository.update.return_value = sample_task

        # Act
        result = await service.update("T-TEST-001", update_request)

        # Assert
        assert isinstance(result, Ok)
        task_response = result.ok()
        assert isinstance(task_response, TaskResponse)
        mock_task_repository.get_by_id.assert_called_once_with("T-TEST-001")
        mock_task_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, mock_task_repository):
        """Test update with non-existent ID returns NotFoundError."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)
        update_request = TaskUpdateRequest(title="Updated")

        # Mock repository to return None for get_by_id
        mock_task_repository.get_by_id.return_value = None

        # Act
        result = await service.update("T-NONEXISTENT", update_request)

        # Assert
        assert isinstance(result, Err)
        error = result.err()
        assert isinstance(error, NotFoundError)
        assert error.extra.get("entity_id") == "T-NONEXISTENT"


class TestBaseServiceDelete:
    """Test suite for BaseService.delete()."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_task_repository, sample_task):
        """Test successful entity deletion."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock get_by_id to find it first
        mock_task_repository.get_by_id.return_value = sample_task
        # Mock delete to return None (void)
        mock_task_repository.delete.return_value = None

        # Act
        result = await service.delete("T-TEST-001")

        # Assert
        assert isinstance(result, Ok)
        assert result.ok() is True
        mock_task_repository.delete.assert_called_once_with(sample_task)

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_task_repository):
        """Test delete with non-existent ID returns NotFoundError."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return None for get_by_id
        mock_task_repository.get_by_id.return_value = None

        # Act
        result = await service.delete("T-NONEXISTENT")

        # Assert
        assert isinstance(result, Err)
        error = result.err()
        assert isinstance(error, NotFoundError)


class TestBaseServiceList:
    """Test suite for BaseService.list()."""

    @pytest.mark.asyncio
    async def test_list_success(self, mock_task_repository, sample_task):
        """Test successful entity listing with pagination."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return list of entities
        mock_task_repository.get_all.return_value = [sample_task]

        # Act
        result = await service.list(limit=50, offset=0)

        # Assert
        assert isinstance(result, Ok)
        tasks = result.ok()
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert all(isinstance(task, TaskResponse) for task in tasks)
        mock_task_repository.get_all.assert_called_once_with(limit=50, offset=0)

    @pytest.mark.asyncio
    async def test_list_empty_result(self, mock_task_repository):
        """Test list with no results returns empty list."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return empty list
        mock_task_repository.get_all.return_value = []

        # Act
        result = await service.list()

        # Assert
        assert isinstance(result, Ok)
        tasks = result.ok()
        assert isinstance(tasks, list)
        assert len(tasks) == 0


class TestBaseServiceUtility:
    """Test suite for BaseService utility methods."""

    @pytest.mark.asyncio
    async def test_exists_true(self, mock_task_repository):
        """Test exists returns True for existing entity."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return True
        mock_task_repository.exists.return_value = True

        # Act
        result = await service.exists("T-TEST-001")

        # Assert
        assert isinstance(result, Ok)
        assert result.ok() is True
        mock_task_repository.exists.assert_called_once_with("T-TEST-001")

    @pytest.mark.asyncio
    async def test_exists_false(self, mock_task_repository):
        """Test exists returns False for non-existent entity."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return False
        mock_task_repository.exists.return_value = False

        # Act
        result = await service.exists("T-NONEXISTENT")

        # Assert
        assert isinstance(result, Ok)
        assert result.ok() is False

    @pytest.mark.asyncio
    async def test_count_success(self, mock_task_repository):
        """Test count returns total entity count."""
        # Arrange
        service = BaseService(mock_task_repository, Task, TaskResponse)

        # Mock repository to return count
        mock_task_repository.count.return_value = 42

        # Act
        result = await service.count()

        # Assert
        assert isinstance(result, Ok)
        assert result.ok() == 42
        mock_task_repository.count.assert_called_once()
