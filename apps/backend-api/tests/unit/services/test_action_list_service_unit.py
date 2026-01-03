"""Unit tests for ActionListService."""

import copy
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from taskman_api.core.errors import ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.services.action_list_service import ActionListService


class TestActionListServiceReorder:
    """Tests for action list item reordering."""

    @pytest.mark.asyncio
    async def test_reorder_items_success(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test successful item reordering."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            sample_action_list.items = [
                {"task": "Item 1", "done": False},
                {"task": "Item 2", "done": False},
                {"task": "Item 3", "done": False},
            ]
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )

            reordered_list = sample_action_list
            reordered_list.items = [
                {"task": "Item 3", "done": False},
                {"task": "Item 1", "done": False},
                {"task": "Item 2", "done": False},
            ]
            mock_action_list_repository.update = AsyncMock(
                return_value=reordered_list
            )

            result = await service.reorder_items("AL-TEST-001", [2, 0, 1])

            assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_reorder_items_invalid_length(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test reorder with mismatched item count returns error."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            sample_action_list.items = [
                {"task": "Item 1", "done": False},
                {"task": "Item 2", "done": False},
            ]
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )

            # Try to reorder with 3 indices but only 2 items exist
            result = await service.reorder_items("AL-TEST-001", [0, 1, 2])

            assert isinstance(result, Err)
            error = result.err()
            assert isinstance(error, ValidationError)


class TestActionListServiceItems:
    """Tests for action list item management."""

    @pytest.mark.asyncio
    async def test_add_item(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test adding item to action list."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            sample_action_list.items = [{"task": "Item 1", "done": False}]
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )

            updated_list = copy.deepcopy(sample_action_list)
            updated_list.items = [
                {"task": "Item 1", "done": False},
                {"task": "Item 2", "done": False},
            ]
            mock_action_list_repository.update = AsyncMock(
                return_value=updated_list
            )

            new_item = {"task": "Item 2", "done": False}
            result = await service.add_item("AL-TEST-001", new_item)

            assert isinstance(result, Ok)
            action_list = result.ok()
            assert len(action_list.items) == 2

    @pytest.mark.asyncio
    async def test_remove_item(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test removing item from action list."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            sample_action_list.items = [
                {"task": "Item 1", "done": False},
                {"task": "Item 2", "done": False},
            ]
            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )

            updated_list = copy.deepcopy(sample_action_list)
            updated_list.items = [{"task": "Item 1", "done": False}]
            mock_action_list_repository.update = AsyncMock(
                return_value=updated_list
            )

            result = await service.remove_item("AL-TEST-001", 1)

            assert isinstance(result, Ok)
            action_list = result.ok()
            assert len(action_list.items) == 1


class TestActionListServiceStatus:
    """Tests for action list status operations."""

    @pytest.mark.asyncio
    async def test_mark_complete(
        self, mocker, mock_action_list_repository, sample_action_list
    ):
        """Test marking action list as complete."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            mock_action_list_repository.get_by_id = AsyncMock(
                return_value=sample_action_list
            )
            updated_list = sample_action_list
            updated_list.status = "completed"
            updated_list.completed_at = datetime.utcnow()
            mock_action_list_repository.update = AsyncMock(
                return_value=Ok(updated_list)
            )

            result = await service.mark_complete("AL-TEST-001")

            assert isinstance(result, Ok)
            action_list = result.ok()
            assert action_list.status == "completed"
            assert action_list.completed_at is not None


class TestActionListServiceQueries:
    """Tests for action list query operations."""

    @pytest.mark.asyncio
    async def test_get_orphaned(self, mocker, mock_action_list_repository):
        """Test getting orphaned action lists."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            result = await service.get_orphaned()

            assert isinstance(result, Ok)
            action_lists = result.ok()
            assert isinstance(action_lists, list)
            mock_action_list_repository.find_orphaned.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_soft_deleted(self, mocker, mock_action_list_repository):
        """Test getting soft-deleted action lists."""
        with patch("taskman_api.services.action_list_service.ActionListRepository") as MockRepo:
            MockRepo.return_value = mock_action_list_repository

            service = ActionListService(mocker.Mock())
            service.repository = mock_action_list_repository
            service.action_list_repo = mock_action_list_repository

            result = await service.get_soft_deleted()

            assert isinstance(result, Ok)
            action_lists = result.ok()
            assert isinstance(action_lists, list)
            mock_action_list_repository.find_soft_deleted.assert_called_once()
