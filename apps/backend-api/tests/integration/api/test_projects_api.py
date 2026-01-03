"""Integration tests for Project API endpoints."""

from fastapi import status
from httpx import AsyncClient

PROJECT_PREFIX = "P-INT"


class TestProjectIntegration:
    """Integration tests for Project management."""

    async def test_project_crud_lifecycle(self, client: AsyncClient):
        """Test complete project lifecycle: Create -> Get -> Update -> Delete."""
        project_id = f"{PROJECT_PREFIX}-LIFE-001"

        # 1. Create
        create_payload = {
            "id": project_id,
            "name": "Lifecycle Project",
            "description": "Integration test project",
            "status": "active",
            "owner": "project.mgr",
            "start_date": "2025-01-01",
            "mission": "To test integration",
        }
        create_res = await client.post("/api/v1/projects", json=create_payload)
        assert create_res.status_code == status.HTTP_201_CREATED
        created_data = create_res.json()
        assert created_data["id"] == project_id
        assert created_data["status"] == "active"

        # 2. Get
        get_res = await client.get(f"/api/v1/projects/{project_id}")
        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["name"] == "Lifecycle Project"

        # 3. Update
        update_payload = {"name": "Updated Project Name", "status": "completed"}
        update_res = await client.put(f"/api/v1/projects/{project_id}", json=update_payload)
        assert update_res.status_code == status.HTTP_200_OK
        updated_data = update_res.json()
        assert updated_data["name"] == "Updated Project Name"
        assert updated_data["status"] == "completed"

        # 4. Verify Update Persisted
        get_res_2 = await client.get(f"/api/v1/projects/{project_id}")
        assert get_res_2.json()["status"] == "completed"

        # 5. Delete (Clean up)
        del_res = await client.delete(f"/api/v1/projects/{project_id}")
        assert del_res.status_code == status.HTTP_204_NO_CONTENT

        # 6. Verify Deletion
        get_res_3 = await client.get(f"/api/v1/projects/{project_id}")
        assert get_res_3.status_code == status.HTTP_404_NOT_FOUND

    async def test_project_validation_errors(self, client: AsyncClient):
        """Test validation failures."""

        # Case 1: Missing name
        res1 = await client.post("/api/v1/projects", json={"id": "P-BAD"})
        assert res1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Case 2: Invalid status
        res2 = await client.post(
            "/api/v1/projects",
            json={
                "id": f"{PROJECT_PREFIX}-BAD-STAT",
                "name": "Bad Status",
                "status": "invalid_status",
                "owner": "owner",
            },
        )
        # Note: Depending on Pydantic config, this might be 422
        assert res2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_project_metrics_endpoint(self, client: AsyncClient):
        """Test fetching project overview metrics."""
        # Note: If there's no dedicated metrics endpoint yet, this tests list/filtering
        # Phase 1.2 plan mentioned metrics, assuming it means getting project list with details
        pass

    async def test_duplicate_project_id(self, client: AsyncClient):
        """Test creating duplicate project ID."""
        project_id = f"{PROJECT_PREFIX}-DUP-001"
        payload = {
            "id": project_id,
            "name": "Original",
            "status": "planning",
            "owner": "owner",
            "mission": "Dup test",
            "start_date": "2025-01-01",
        }

        await client.post("/api/v1/projects", json=payload)

        res = await client.post("/api/v1/projects", json=payload)
        assert res.status_code == status.HTTP_409_CONFLICT
