"""Unit tests for Action Lists router endpoints.

Tests router layer logic: request parsing, response formatting, error handling.
Service layer is mocked to test router behavior in isolation.

Coverage Targets:
- All 12 endpoints tested
- Success paths (happy path)
- Failure paths (service returns failure)
- Edge cases (empty results, optional params)
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from taskman_api.core.result import Err, Ok
from taskman_api.main import app

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_action_list_dict():
    """Create a sample action list dict for testing.

    Uses dict instead of SQLAlchemy model to avoid ORM initialization issues.
    The dict structure matches what the service returns after model_dump().
    """
    return {
        "id": f"AL-{uuid4().hex[:8]}",
        "name": "Test Action List",  # Model uses 'name', schema maps to 'title'
        "description": "Test description",
        "status": "active",
        "owner": "test-owner",
        "tags": ["tag1", "tag2"],
        "project_id": "PROJ-001",
        "sprint_id": "SPRINT-001",
        "items": [
            {"id": "item-1", "text": "First item", "completed": False, "order": 0},
            {"id": "item-2", "text": "Second item", "completed": True, "order": 1},
        ],
        "priority": "high",
        "due_date": datetime(2025, 12, 31, 23, 59, 59),
        "evidence_refs": ["EVD-001"],
        "extra_metadata": {"velocity": 5},
        "notes": "Test notes",
        "geometry_shape": "rectangle",
        "created_at": datetime(2025, 1, 1, 10, 0, 0),
        "updated_at": datetime(2025, 1, 1, 12, 0, 0),
        "completed_at": None,
        "parent_deleted_at": None,
        "parent_deletion_note": {},
    }


@pytest.fixture
def sample_action_list_entity(sample_action_list_dict):
    """Create a mock entity that behaves like an SQLAlchemy model.

    Returns a MagicMock with model_dump() method that returns the dict.
    This simulates what the service layer returns without SQLAlchemy complexity.
    """
    entity = MagicMock()
    entity.model_dump = MagicMock(return_value=sample_action_list_dict)

    # Also expose dict values as attributes for direct access
    for key, value in sample_action_list_dict.items():
        setattr(entity, key, value)

    return entity


@pytest.fixture
def mock_action_list_service(sample_action_list_entity):
    """Create a mock ActionListService."""
    service = AsyncMock()

    # Default successful responses using Ok()
    service.create_action_list = AsyncMock(return_value=Ok(sample_action_list_entity))
    service.list_action_lists = AsyncMock(
        return_value=Ok(([sample_action_list_entity], 1))
    )
    service.get_action_list = AsyncMock(return_value=Ok(sample_action_list_entity))
    service.update_action_list = AsyncMock(return_value=Ok(sample_action_list_entity))
    service.delete_action_list = AsyncMock(return_value=Ok(True))
    service.get_tasks_for_action_list = AsyncMock(
        return_value=Ok(["task-1", "task-2"])
    )
    service.add_task_to_action_list = AsyncMock(
        return_value=Ok(sample_action_list_entity)
    )
    service.remove_task_from_action_list = AsyncMock(
        return_value=Ok(sample_action_list_entity)
    )
    service.add_item = AsyncMock(return_value=Ok(sample_action_list_entity))
    service.remove_item = AsyncMock(return_value=Ok(True))
    service.reorder_items = AsyncMock(return_value=Ok(sample_action_list_entity))

    return service


@pytest.fixture
async def client_with_mock_service(mock_action_list_service):
    """Create test client with mocked service dependency."""
    from taskman_api.dependencies import get_action_list_service

    # Override dependency
    app.dependency_overrides[get_action_list_service] = lambda: mock_action_list_service

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Cleanup
    app.dependency_overrides.clear()


# ============================================================================
# Test: POST / - Create Action List
# ============================================================================


class TestCreateActionList:
    """Tests for create action list endpoint."""

    @pytest.mark.asyncio
    async def test_create_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful action list creation."""
        payload = {
            "id": "AL-new-test-001",  # Required field with AL- prefix
            "title": "New Action List",
            "description": "Description",
            "owner": "test-owner",
            "status": "active",
        }

        response = await client_with_mock_service.post(
            "/api/v1/action-lists", json=payload
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Action List"
        mock_action_list_service.create_action_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_all_fields(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test creation with all optional fields populated."""
        payload = {
            "id": "AL-complete-test-001",  # Required field with AL- prefix
            "title": "Complete Action List",
            "description": "Full description",
            "owner": "full-owner",
            "status": "active",
            "tags": ["urgent", "sprint-1"],
            "project_id": "PROJ-999",
            "sprint_id": "SPRINT-999",
            "items": [{"text": "Item 1", "completed": False}],
            "priority": "critical",
            "due_date": "2025-12-31T23:59:59Z",
        }

        response = await client_with_mock_service.post(
            "/api/v1/action-lists", json=payload
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_action_list_service.create_action_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test creation failure from service layer."""
        mock_action_list_service.create_action_list = AsyncMock(
            return_value=Err("Validation error: title too long")
        )

        payload = {
            "id": "AL-failing-test",  # Required field
            "title": "x" * 200,  # Within limit, error from service
            "status": "active",
        }

        response = await client_with_mock_service.post(
            "/api/v1/action-lists", json=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Validation error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_missing_required_field(self, client_with_mock_service):
        """Test creation with missing required id field."""
        payload = {"title": "No ID", "description": "Missing required id"}

        response = await client_with_mock_service.post(
            "/api/v1/action-lists", json=payload
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Test: GET / - List Action Lists
# ============================================================================


class TestListActionLists:
    """Tests for list action lists endpoint."""

    @pytest.mark.asyncio
    async def test_list_default_pagination(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test list with default pagination."""
        response = await client_with_mock_service.get("/api/v1/action-lists")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "action_lists" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["per_page"] == 20

    @pytest.mark.asyncio
    async def test_list_with_filters(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test list with status, owner, project, sprint filters."""
        response = await client_with_mock_service.get(
            "/api/v1/action-lists",
            params={
                "status": "active",
                "owner": "test-owner",
                "project_id": "PROJ-001",
                "sprint_id": "SPRINT-001",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify service was called with filters
        call_args = mock_action_list_service.list_action_lists.call_args
        assert call_args.kwargs["status"] == "active"
        assert call_args.kwargs["owner"] == "test-owner"

    @pytest.mark.asyncio
    async def test_list_custom_pagination(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test list with custom page and per_page."""
        response = await client_with_mock_service.get(
            "/api/v1/action-lists", params={"page": 3, "per_page": 50}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 3
        assert data["per_page"] == 50

    @pytest.mark.asyncio
    async def test_list_empty_results(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test list when no results found."""
        mock_action_list_service.list_action_lists = AsyncMock(return_value=Ok(([], 0)))

        response = await client_with_mock_service.get("/api/v1/action-lists")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["action_lists"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    @pytest.mark.asyncio
    async def test_list_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test list failure from service layer."""
        mock_action_list_service.list_action_lists = AsyncMock(
            return_value=Err("Database connection error")
        )

        response = await client_with_mock_service.get("/api/v1/action-lists")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: GET /{list_id} - Get Action List
# ============================================================================


class TestGetActionList:
    """Tests for get action list by ID endpoint."""

    @pytest.mark.asyncio
    async def test_get_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful get by ID."""
        response = await client_with_mock_service.get(
            "/api/v1/action-lists/AL-test-001"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Action List"

    @pytest.mark.asyncio
    async def test_get_not_found(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test get for non-existent ID."""
        mock_action_list_service.get_action_list = AsyncMock(return_value=Err("Not found"))

        response = await client_with_mock_service.get(
            "/api/v1/action-lists/AL-nonexistent"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_none_value(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test get when service returns None (soft deleted)."""
        mock_action_list_service.get_action_list = AsyncMock(return_value=Ok(None))

        response = await client_with_mock_service.get("/api/v1/action-lists/AL-deleted")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: PUT/PATCH /{list_id} - Update Action List
# ============================================================================


class TestUpdateActionList:
    """Tests for update action list endpoints."""

    @pytest.mark.asyncio
    async def test_put_update_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful full update with PUT."""
        # ActionListStatus enum only has: active, archived (no "completed")
        payload = {"title": "Updated Title", "status": "archived"}

        response = await client_with_mock_service.put(
            "/api/v1/action-lists/AL-test-001", json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        mock_action_list_service.update_action_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_patch_update_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful partial update with PATCH."""
        payload = {"description": "Updated description only"}

        response = await client_with_mock_service.patch(
            "/api/v1/action-lists/AL-test-001", json=payload
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_update_not_found(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test update for non-existent ID."""
        mock_action_list_service.update_action_list = AsyncMock(
            return_value=Err("ActionList not found: AL-ghost")
        )

        response = await client_with_mock_service.put(
            "/api/v1/action-lists/AL-ghost", json={"title": "Ghost"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_update_title_maps_to_name(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test that 'title' in request maps to 'name' in service call."""
        payload = {"title": "New Title Value"}

        await client_with_mock_service.put(
            "/api/v1/action-lists/AL-test-001", json=payload
        )

        call_args = mock_action_list_service.update_action_list.call_args
        # title should be mapped to name in the router
        assert call_args.kwargs.get("name") == "New Title Value"


# ============================================================================
# Test: DELETE /{list_id} - Delete Action List
# ============================================================================


class TestDeleteActionList:
    """Tests for delete action list endpoint."""

    @pytest.mark.asyncio
    async def test_delete_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful deletion."""
        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-test-001"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_action_list_service.delete_action_list.assert_called_once_with(
            "AL-test-001"
        )

    @pytest.mark.asyncio
    async def test_delete_not_found(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test delete for non-existent ID."""
        mock_action_list_service.delete_action_list = AsyncMock(
            return_value=Err("ActionList not found")
        )

        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-nonexistent"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: GET /{list_id}/tasks - Get Tasks
# ============================================================================


class TestGetActionListTasks:
    """Tests for get action list tasks endpoint."""

    @pytest.mark.asyncio
    async def test_get_tasks_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful task retrieval."""
        response = await client_with_mock_service.get(
            "/api/v1/action-lists/AL-test-001/tasks"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert "task-1" in data
        assert "task-2" in data

    @pytest.mark.asyncio
    async def test_get_tasks_empty(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test get tasks when action list has no tasks."""
        mock_action_list_service.get_tasks_for_action_list = AsyncMock(
            return_value=Ok([])
        )

        response = await client_with_mock_service.get(
            "/api/v1/action-lists/AL-empty/tasks"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tasks_not_found(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test get tasks for non-existent action list."""
        mock_action_list_service.get_tasks_for_action_list = AsyncMock(
            return_value=Err("ActionList not found")
        )

        response = await client_with_mock_service.get(
            "/api/v1/action-lists/AL-ghost/tasks"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Test: POST /{list_id}/tasks - Add Task
# ============================================================================


class TestAddTaskToActionList:
    """Tests for add task to action list endpoint."""

    @pytest.mark.asyncio
    async def test_add_task_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful task addition."""
        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-test-001/tasks", params={"task_id": "TASK-new"}
        )

        assert response.status_code == status.HTTP_200_OK
        mock_action_list_service.add_task_to_action_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_task_missing_param(self, client_with_mock_service):
        """Test add task without required task_id parameter."""
        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-test-001/tasks"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_add_task_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test add task when service fails (invalid task ID)."""
        mock_action_list_service.add_task_to_action_list = AsyncMock(
            return_value=Err("Task not found: TASK-invalid")
        )

        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-test-001/tasks", params={"task_id": "TASK-invalid"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: DELETE /{list_id}/tasks/{task_id} - Remove Task
# ============================================================================


class TestRemoveTaskFromActionList:
    """Tests for remove task from action list endpoint."""

    @pytest.mark.asyncio
    async def test_remove_task_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful task removal."""
        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-test-001/tasks/TASK-001"
        )

        assert response.status_code == status.HTTP_200_OK
        mock_action_list_service.remove_task_from_action_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_task_not_in_list(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test remove task that's not in the list (idempotent)."""
        # Service should still succeed (idempotent)
        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-test-001/tasks/TASK-not-in-list"
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_remove_task_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test remove task when service fails."""
        mock_action_list_service.remove_task_from_action_list = AsyncMock(
            return_value=Err("ActionList not found")
        )

        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-ghost/tasks/TASK-001"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: POST /{list_id}/items - Add Item
# ============================================================================


class TestAddItemToActionList:
    """Tests for add item to action list endpoint."""

    @pytest.mark.asyncio
    async def test_add_item_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful item addition."""
        payload = {"text": "New checklist item", "order": 0}

        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-test-001/items", json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        mock_action_list_service.add_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_item_minimal(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test adding item with minimal data."""
        payload = {"text": "Just text"}

        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-test-001/items", json=payload
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_add_item_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test add item when service fails."""
        mock_action_list_service.add_item = AsyncMock(
            return_value=Err("ActionList not found")
        )

        response = await client_with_mock_service.post(
            "/api/v1/action-lists/AL-ghost/items", json={"text": "Item"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: DELETE /{list_id}/items/{item_id} - Remove Item
# ============================================================================


class TestRemoveItemFromActionList:
    """Tests for remove item from action list endpoint."""

    @pytest.mark.asyncio
    async def test_remove_item_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful item removal."""
        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-test-001/items/item-1"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_action_list_service.remove_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_item_by_text(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test remove item using text identifier."""
        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-test-001/items/First%20item"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_remove_item_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test remove item when service fails."""
        mock_action_list_service.remove_item = AsyncMock(
            return_value=Err("ActionList not found")
        )

        response = await client_with_mock_service.delete(
            "/api/v1/action-lists/AL-ghost/items/item-1"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Test: PATCH /{list_id}/items/reorder - Reorder Items
# ============================================================================


class TestReorderActionListItems:
    """Tests for reorder action list items endpoint."""

    @pytest.mark.asyncio
    async def test_reorder_success(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test successful item reordering."""
        payload = {"item_ids": ["item-2", "item-1"]}

        response = await client_with_mock_service.patch(
            "/api/v1/action-lists/AL-test-001/items/reorder", json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        mock_action_list_service.reorder_items.assert_called_once()

    @pytest.mark.asyncio
    async def test_reorder_empty_list(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test reorder with empty item list."""
        payload = {"item_ids": []}

        response = await client_with_mock_service.patch(
            "/api/v1/action-lists/AL-test-001/items/reorder", json=payload
        )

        # Empty reorder should still be valid
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_reorder_service_failure(
        self, client_with_mock_service, mock_action_list_service
    ):
        """Test reorder when service fails (invalid item IDs)."""
        mock_action_list_service.reorder_items = AsyncMock(
            return_value=Err("Invalid item IDs provided")
        )

        payload = {"item_ids": ["nonexistent-1", "nonexistent-2"]}

        response = await client_with_mock_service.patch(
            "/api/v1/action-lists/AL-test-001/items/reorder", json=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_reorder_missing_body(self, client_with_mock_service):
        """Test reorder without request body."""
        response = await client_with_mock_service.patch(
            "/api/v1/action-lists/AL-test-001/items/reorder"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
