"""Integration tests for Task API endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient

# Constants for test data
TASK_PREFIX = "T-INT"
PROJECT_PREFIX = "P-INT"
SPRINT_PREFIX = "S-INT"


class TestTaskIntegration:
    """Integration tests for Task management."""

    @pytest.fixture(autouse=True)
    async def setup_dependencies(self, client: AsyncClient):
        """Setup required project and sprint for tasks."""
        # Create Project
        p_res = await client.post(
            "/api/v1/projects",
            json={
                "id": f"{PROJECT_PREFIX}-001",
                "name": "Integration Project",
                "mission": "Test Mission",
                "start_date": "2025-01-01",
                "status": "active",
                "owner": "test.owner",
            },
        )
        assert p_res.status_code == status.HTTP_201_CREATED
        self.project_id = p_res.json()["id"]

        # Create Sprint
        s_res = await client.post(
            "/api/v1/sprints",
            json={
                "id": f"{SPRINT_PREFIX}-001",
                "name": "Integration Sprint",
                "goal": "Test Goal",
                "status": "active",
                "primary_project": self.project_id,
                "owner": "test.owner",
                "start_date": "2025-01-01",
                "end_date": "2025-01-14",
                "cadence": "biweekly",
            },
        )
        assert s_res.status_code == status.HTTP_201_CREATED
        self.sprint_id = s_res.json()["id"]

    async def test_create_task_full_lifecycle(self, client: AsyncClient):
        """Test complete task lifecycle: Create -> Get -> Update -> Delete."""
        task_id = f"{TASK_PREFIX}-LIFE-001"

        # 1. Create
        create_payload = {
            "id": task_id,
            "title": "Lifecycle Task",
            "summary": "Testing full lifecycle",
            "description": "Detailed description",
            "owner": "test.user",
            "priority": "p1",
            "status": "new",
            "primary_project": self.project_id,
            "primary_sprint": self.sprint_id,
            "assignees": ["dev.one", "dev.two"],
            "estimate_points": 5,
            "labels": ["integration", "test"],
        }
        create_res = await client.post("/api/v1/tasks", json=create_payload)
        assert create_res.status_code == status.HTTP_201_CREATED, (
            f"Failed to create task: {create_res.text}"
        )
        created_data = create_res.json()
        assert created_data["id"] == task_id
        assert created_data["status"] == "new"

        # 2. Get
        get_res = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["title"] == "Lifecycle Task"

        # 3. Update
        update_payload = {
            "status": "in_progress",
            "actual_time_hours": 2.5,
            "summary": "Updated summary",
        }
        update_res = await client.patch(f"/api/v1/tasks/{task_id}", json=update_payload)
        assert update_res.status_code == status.HTTP_200_OK
        updated_data = update_res.json()
        assert updated_data["status"] == "in_progress"
        assert updated_data["actual_time_hours"] == 2.5
        assert updated_data["summary"] == "Updated summary"

        # 4. Verify Update Persisted
        get_res_2 = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_res_2.json()["status"] == "in_progress"

        # 5. Delete
        del_res = await client.delete(f"/api/v1/tasks/{task_id}")
        assert del_res.status_code == status.HTTP_204_NO_CONTENT

        # 6. Verify Deletion
        get_res_3 = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_res_3.status_code == status.HTTP_404_NOT_FOUND, (
            f"Expected 404 after delete, got {get_res_3.status_code}. Body: {get_res_3.text}"
        )

    async def test_task_validation_errors(self, client: AsyncClient):
        """Test various validation failure scenarios."""

        # Case 1: Missing required fields
        res1 = await client.post("/api/v1/tasks", json={"title": "Incomplete"})
        assert res1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Case 2: Invalid Enum (Priority)
        res2 = await client.post(
            "/api/v1/tasks",
            json={
                "id": f"{TASK_PREFIX}-BAD-ENUM",
                "title": "Bad Enum",
                "summary": "Test",
                "description": "Test",
                "status": "new",
                "priority": "invalid_priority",  # <--- Invalid
                "owner": "owner",
                "primary_project": self.project_id,
                "primary_sprint": self.sprint_id,
            },
        )
        assert res2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Case 3: Invalid Points (Negative)
        res3 = await client.post(
            "/api/v1/tasks",
            json={
                "id": f"{TASK_PREFIX}-BAD-POINTS",
                "title": "Bad Points",
                "summary": "Test",
                "description": "Test",
                "status": "new",
                "priority": "p1",
                "owner": "owner",
                "primary_project": self.project_id,
                "primary_sprint": self.sprint_id,
                "estimate_points": -1,  # <--- Invalid
            },
        )
        assert res3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_list_tasks_pagination_and_filtering(self, client: AsyncClient):
        """Test listing tasks with various filters and pagination."""

        # Seed Data
        base_id = f"{TASK_PREFIX}-LIST"
        for i in range(5):
            await client.post(
                "/api/v1/tasks",
                json={
                    "id": f"{base_id}-{i}",
                    "title": f"Task {i}",
                    "summary": f"Summary {i}",
                    "description": "Desc",
                    "status": "new" if i < 3 else "done",
                    "priority": "p1" if i % 2 == 0 else "p2",
                    "owner": "owner.1" if i < 2 else "owner.2",
                    "primary_project": self.project_id,
                    "primary_sprint": self.sprint_id,
                },
            )

        # 1. Basic Pagination
        res_page = await client.get(
            "/api/v1/tasks?per_page=2&page=1"
        )  # Using correct params per schema
        assert res_page.status_code == status.HTTP_200_OK, f"List tasks failed: {res_page.text}"
        data = res_page.json()
        tasks = data["tasks"]
        assert len(tasks) == 2
        assert tasks[0]["id"] == f"{base_id}-0"
        assert data["total"] == 5

        # 2. Filter by Status
        res_status = await client.get("/api/v1/tasks?status=done")
        data_status = res_status.json()
        tasks_status = data_status["tasks"]
        assert len(tasks_status) == 2  # Tasks 3 and 4
        assert all(t["status"] == "done" for t in tasks_status)

        # 3. Filter by Priority
        res_prio = await client.get("/api/v1/tasks?priority=p2")
        data_prio = res_prio.json()
        tasks_prio = data_prio["tasks"]
        assert len(tasks_prio) == 2  # Tasks 1 and 3 (indices)
        assert all(t["priority"] == "p2" for t in tasks_prio)

        # 4. Filter by Owner
        res_owner = await client.get("/api/v1/tasks?owner=owner.1")
        data_owner = res_owner.json()
        tasks_owner = data_owner["tasks"]
        assert len(tasks_owner) == 2  # Tasks 0 and 1

    async def test_duplicate_task_id(self, client: AsyncClient):
        """Test creating a task with an existing ID returns 409 Conflict."""
        task_id = f"{TASK_PREFIX}-DUP-001"
        payload = {
            "id": task_id,
            "title": "Original",
            "summary": "Summary",
            "description": "Desc",
            "status": "new",
            "priority": "p1",
            "owner": "owner",
            "primary_project": self.project_id,
            "primary_sprint": self.sprint_id,
        }

        # First creation
        await client.post("/api/v1/tasks", json=payload)

        # Second creation (Duplicate)
        res = await client.post("/api/v1/tasks", json=payload)
        if res.status_code != status.HTTP_409_CONFLICT:
            print(f"Duplicate check failed. Status: {res.status_code}, Body: {res.text}")
        assert res.status_code == status.HTTP_409_CONFLICT
