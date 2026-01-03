"""Integration tests for ActionList Service (bypassing broken router).

These tests validate the service layer directly until router is fixed.
See AAR-T11-Integration-Testing-CRITICAL-FINDINGS.md for details.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.schemas.action_list import ActionListCreate, ActionListUpdate
from taskman_api.services.action_list_service import ActionListService


class TestActionListServiceDirect:
    """Test ActionListService methods directly (bypassing router)."""

    @pytest.fixture
    async def service(self, db_session: AsyncSession):
        """Create ActionListService instance."""
        return ActionListService(session=db_session)

    @pytest.mark.asyncio
    async def test_create_returns_ok_result(self, service: ActionListService):
        """Should create action list and return Ok result."""
        # Arrange
        create_data = ActionListCreate(
            id="AL-test-001",
            title="Test List",
            description="Test description",
        )

        # Act
        result = await service.create(create_data)

        # Assert
        assert (
            result.is_ok()
        ), f"Expected Ok, got Err: {result.unwrap_err() if result.is_err() else 'N/A'}"
        response = result.unwrap()
        assert response.title == "Test List"
        assert response.description == "Test description"

    @pytest.mark.asyncio
    async def test_get_existing_returns_ok(self, service: ActionListService):
        """Should retrieve existing action list."""
        # Arrange - create first
        create_result = await service.create(ActionListCreate(id="AL-get-001", title="Get Test"))
        assert create_result.is_ok()
        created = create_result.unwrap()

        # Act
        get_result = await service.get(created.id)

        # Assert
        assert get_result.is_ok()
        retrieved = get_result.unwrap()
        assert retrieved.id == created.id
        assert retrieved.title == "Get Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_err(self, service: ActionListService):
        """Should return Err for nonexistent list."""
        # Act
        result = await service.get("AL-nonexistent")

        # Assert
        assert result.is_err()

    @pytest.mark.asyncio
    async def test_update_returns_ok(self, service: ActionListService):
        """Should update action list."""
        # Arrange
        create_result = await service.create(ActionListCreate(id="AL-update-001", title="Original"))
        assert create_result.is_ok()
        created = create_result.unwrap()

        # Act
        update_result = await service.update(created.id, ActionListUpdate(title="Updated"))

        # Assert
        assert update_result.is_ok()
        updated = update_result.unwrap()
        assert updated.title == "Updated"

    @pytest.mark.asyncio
    async def test_delete_returns_ok(self, service: ActionListService):
        """Should delete action list."""
        # Arrange
        create_result = await service.create(
            ActionListCreate(id="AL-delete-001", title="To Delete")
        )
        assert create_result.is_ok()
        created = create_result.unwrap()

        # Act
        delete_result = await service.delete(created.id)

        # Assert
        assert delete_result.is_ok()

        # Verify deleted
        get_result = await service.get(created.id)
        assert get_result.is_err()

    @pytest.mark.asyncio
    async def test_list_returns_ok(self, service: ActionListService):
        """Should list action lists."""
        # Arrange - create a few lists
        for i in range(3):
            result = await service.create(
                ActionListCreate(id=f"AL-list-{i:03d}", title=f"List {i}")
            )
            assert result.is_ok()

        # Act
        list_result = await service.list(limit=10, offset=0)

        # Assert
        assert list_result.is_ok()
        items = list_result.unwrap()
        assert len(items) >= 3

    @pytest.mark.asyncio
    async def test_search_with_status_filter(self, service: ActionListService):
        """Should search with status filter."""
        # Arrange
        await service.create(
            ActionListCreate(id="AL-search-active", title="Active", status="active")
        )
        await service.create(
            ActionListCreate(id="AL-search-archived", title="Archived", status="archived")
        )

        # Act
        result = await service.search(status="active")

        # Assert
        assert result.is_ok()
        items, total = result.unwrap()
        assert all(item.status == "active" for item in items)
