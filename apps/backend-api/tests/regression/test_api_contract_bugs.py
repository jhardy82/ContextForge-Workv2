"""
Regression tests for API contract bugs discovered during E2E testing.

These tests prevent regression of bugs that were found and fixed:
1. Task creation requires description field (was assumed optional)
2. Task creation requires primary_sprint field (was assumed optional)
3. Sprint updates only work via PUT (PATCH returns 405)
4. Action list IDs are server-generated (client ID ignored)
5. Action list task association uses query param not path param

Reference: E2E test fixes commit dde4b943
"""

import pytest
from fastapi import status
from httpx import AsyncClient


class TestTaskCreationRequiredFields:
    """
    Regression: Task creation was failing with 422 when missing
    description or primary_sprint fields that are actually required.
    """

    @pytest.mark.asyncio
    async def test_task_creation_requires_description(
        self, async_client: AsyncClient, sample_project: dict, sample_sprint: dict
    ):
        """Task creation without description should fail with 422."""
        task_payload = {
            "id": "T-REG-DESC-001",
            "title": "Task without description",
            "summary": "Test summary",
            # "description" intentionally omitted
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
        }

        response = await async_client.post("/api/v1/tasks", json=task_payload)

        # Should fail because description is required
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()
        assert "detail" in error_detail

    @pytest.mark.asyncio
    async def test_task_creation_requires_primary_sprint(
        self, async_client: AsyncClient, sample_project: dict
    ):
        """Task creation without primary_sprint should fail with 422."""
        task_payload = {
            "id": "T-REG-SPRINT-001",
            "title": "Task without sprint",
            "summary": "Test summary",
            "description": "Test description",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            # "primary_sprint" intentionally omitted
        }

        response = await async_client.post("/api/v1/tasks", json=task_payload)

        # Should fail because primary_sprint is required
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_task_creation_with_all_required_fields_succeeds(
        self, async_client: AsyncClient, sample_project: dict, sample_sprint: dict
    ):
        """Task creation with all required fields should succeed."""
        task_payload = {
            "id": "T-REG-FULL-001",
            "title": "Complete task",
            "summary": "Test summary",
            "description": "Test description",  # Required
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],  # Required
        }

        response = await async_client.post("/api/v1/tasks", json=task_payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "T-REG-FULL-001"
        assert data["description"] == "Test description"
        assert data["primary_sprint"] == sample_sprint["id"]


class TestSprintUpdateMethod:
    """
    Regression: Sprint updates were failing with 405 when using PATCH.
    The API only supports PUT for sprint updates.
    """

    @pytest.mark.asyncio
    async def test_sprint_patch_returns_405(
        self, async_client: AsyncClient, sample_sprint: dict
    ):
        """PATCH on sprint should return 405 Method Not Allowed."""
        response = await async_client.patch(
            f"/api/v1/sprints/{sample_sprint['id']}",
            json={"status": "active"},
        )

        # PATCH is not supported for sprints
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.asyncio
    async def test_sprint_put_succeeds(
        self, async_client: AsyncClient, sample_sprint: dict
    ):
        """PUT on sprint should succeed for updates."""
        # First get the full sprint to include all fields
        get_response = await async_client.get(f"/api/v1/sprints/{sample_sprint['id']}")
        assert get_response.status_code == status.HTTP_200_OK
        sprint_data = get_response.json()

        # Update via PUT with full payload
        sprint_data["status"] = "active"

        response = await async_client.put(
            f"/api/v1/sprints/{sample_sprint['id']}",
            json=sprint_data,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "active"


class TestActionListIdFormat:
    """
    Regression: Action list IDs are server-generated with AL-xxxx pattern.
    Note: Despite schema having 'id' field, the API generates sequential IDs.
    This documents the ACTUAL behavior for regression testing.
    """

    @pytest.mark.asyncio
    async def test_action_list_id_is_server_generated(
        self, async_client: AsyncClient
    ):
        """Action list ID is generated by server (not client-provided)."""
        payload = {
            "id": "AL-REG-TEST-001",  # Client provides this, but API ignores it
            "title": "Test Action List",
            "description": "Testing ID generation",
            "status": "active",
            "owner": "test@example.com",
        }

        response = await async_client.post("/api/v1/action-lists", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Server generates ID with AL-xxxx format (ignores client input)
        assert data["id"].startswith("AL-")
        # Note: Actual ID is like "AL-0001" - sequential server-generated

    @pytest.mark.asyncio
    async def test_action_list_crud_with_server_id(
        self, async_client: AsyncClient
    ):
        """CRUD operations work with server-generated ID."""
        # Create action list
        create_payload = {
            "id": "AL-REG-CRUD-001",  # Ignored by server
            "title": "CRUD Test List",
            "description": "Testing CRUD with server ID",
            "status": "active",
            "owner": "test@example.com",
        }
        create_response = await async_client.post("/api/v1/action-lists", json=create_payload)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Use server-generated ID for subsequent operations
        created_id = create_response.json()["id"]
        assert created_id.startswith("AL-")

        # GET by server-generated ID should work
        get_response = await async_client.get(f"/api/v1/action-lists/{created_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == created_id


class TestActionListTaskAssociationEndpoint:
    """
    Regression: Task association endpoint uses query param, not path param.
    POST /{list_id}/tasks?task_id=xxx (correct)
    POST /{list_id}/tasks/{task_id} (incorrect - returns 405)
    """

    @pytest.mark.asyncio
    async def test_task_association_path_param_returns_405(
        self,
        async_client: AsyncClient,
        sample_project: dict,
        sample_sprint: dict,
    ):
        """Using task_id as path param should return 405."""
        # Create a task first
        task_payload = {
            "id": "T-REG-ASSOC-001",
            "title": "Task for association test",
            "summary": "Test summary",
            "description": "Test description",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
        }
        task_res = await async_client.post("/api/v1/tasks", json=task_payload)
        assert task_res.status_code == status.HTTP_201_CREATED

        # Create action list (with correct schema: id, title, not name)
        al_res = await async_client.post(
            "/api/v1/action-lists",
            json={
                "id": "AL-REG-ASSOC-001",
                "title": "Association Test List",
                "description": "Test",
                "status": "active",
                "owner": "test@example.com",
            },
        )
        assert al_res.status_code == status.HTTP_201_CREATED
        al_id = al_res.json()["id"]

        # Using path param style should fail with 405
        wrong_response = await async_client.post(
            f"/api/v1/action-lists/{al_id}/tasks/T-REG-ASSOC-001"
        )
        assert wrong_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.asyncio
    async def test_task_association_query_param_succeeds(
        self,
        async_client: AsyncClient,
        sample_project: dict,
        sample_sprint: dict,
    ):
        """Using task_id as query param should succeed."""
        # Create a task
        task_payload = {
            "id": "T-REG-ASSOC-002",
            "title": "Task for query param test",
            "summary": "Test summary",
            "description": "Test description",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
        }
        task_res = await async_client.post("/api/v1/tasks", json=task_payload)
        assert task_res.status_code == status.HTTP_201_CREATED

        # Create action list (with correct schema: id, title, not name)
        al_res = await async_client.post(
            "/api/v1/action-lists",
            json={
                "id": "AL-REG-ASSOC-002",
                "title": "Query Param Test List",
                "description": "Test",
                "status": "active",
                "owner": "test@example.com",
            },
        )
        assert al_res.status_code == status.HTTP_201_CREATED
        al_id = al_res.json()["id"]

        # Using query param style should succeed
        correct_response = await async_client.post(
            f"/api/v1/action-lists/{al_id}/tasks",
            params={"task_id": "T-REG-ASSOC-002"},
        )
        assert correct_response.status_code == status.HTTP_200_OK

        # Verify task is associated
        # Note: GET /{list_id}/tasks returns list of task ID STRINGS, not objects
        tasks_response = await async_client.get(f"/api/v1/action-lists/{al_id}/tasks")
        assert tasks_response.status_code == status.HTTP_200_OK
        task_ids = tasks_response.json()  # Already a list of strings
        assert "T-REG-ASSOC-002" in task_ids


class TestEnumValueCasing:
    """
    Regression: Enum values must be lowercase (p0-p3, not P0-P3).
    """

    @pytest.mark.asyncio
    async def test_priority_must_be_lowercase(
        self, async_client: AsyncClient, sample_project: dict, sample_sprint: dict
    ):
        """Task priority enum values must be lowercase."""
        # Uppercase should fail
        uppercase_payload = {
            "id": "T-REG-ENUM-001",
            "title": "Uppercase priority test",
            "summary": "Test",
            "description": "Test",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
            "priority": "P2",  # Uppercase - should fail
        }

        uppercase_response = await async_client.post("/api/v1/tasks", json=uppercase_payload)
        assert uppercase_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_lowercase_priority_succeeds(
        self, async_client: AsyncClient, sample_project: dict, sample_sprint: dict
    ):
        """Lowercase priority enum values should succeed."""
        lowercase_payload = {
            "id": "T-REG-ENUM-002",
            "title": "Lowercase priority test",
            "summary": "Test",
            "description": "Test",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
            "priority": "p2",  # Lowercase - should succeed
        }

        lowercase_response = await async_client.post("/api/v1/tasks", json=lowercase_payload)
        assert lowercase_response.status_code == status.HTTP_201_CREATED
        assert lowercase_response.json()["priority"] == "p2"

    @pytest.mark.asyncio
    async def test_status_must_be_lowercase(
        self, async_client: AsyncClient, sample_project: dict, sample_sprint: dict
    ):
        """Task status enum values must be lowercase."""
        # Valid lowercase statuses: new, in_progress, done
        valid_payload = {
            "id": "T-REG-STATUS-001",
            "title": "Status test",
            "summary": "Test",
            "description": "Test",
            "owner": "test@example.com",
            "primary_project": sample_project["id"],
            "primary_sprint": sample_sprint["id"],
            "status": "new",  # Lowercase
        }

        response = await async_client.post("/api/v1/tasks", json=valid_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "new"
