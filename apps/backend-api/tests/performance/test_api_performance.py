"""Performance tests for TaskMan API.

These tests establish baseline response times and verify the API
can handle concurrent requests without degradation.

Test Categories:
1. Response time baselines (p50, p95, p99)
2. Concurrent request handling
3. Bulk operation performance
4. Database query efficiency

Run with: pytest tests/performance/ -v --tb=short
"""

import asyncio
import statistics
import time
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from taskman_api.db.base import Base
from taskman_api.dependencies import get_db_session
from taskman_api.main import app

# Performance thresholds (milliseconds)
THRESHOLDS = {
    "list_endpoint_p95": 200,  # List operations should complete < 200ms
    "get_endpoint_p95": 100,  # Single item retrieval < 100ms
    "create_endpoint_p95": 300,  # Create operations < 300ms
    "bulk_create_p95": 500,  # Bulk operations < 500ms per item
}


@pytest.fixture(scope="function")
async def perf_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session for performance tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
async def perf_client(perf_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with performance database."""

    async def override_get_db():
        yield perf_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_data(perf_client: AsyncClient) -> dict:
    """Create seed data for performance tests."""
    # Create project
    project_response = await perf_client.post(
        "/api/v1/projects",
        json={
            "id": "P-PERF-001",
            "name": "Performance Test Project",
            "mission": "Performance testing",
            "status": "active",
            "start_date": "2025-01-01",
            "owner": "perf@test.com",
        },
    )
    assert project_response.status_code == 201
    project = project_response.json()

    # Create sprint
    sprint_response = await perf_client.post(
        "/api/v1/sprints",
        json={
            "id": "S-PERF-001",
            "name": "Performance Test Sprint",
            "goal": "Performance testing",
            "cadence": "biweekly",
            "start_date": "2025-01-01",
            "end_date": "2025-01-14",
            "status": "planning",
            "owner": "perf@test.com",
            "primary_project": project["id"],
        },
    )
    assert sprint_response.status_code == 201
    sprint = sprint_response.json()

    return {"project": project, "sprint": sprint}


class TestResponseTimeBaselines:
    """Establish and verify response time baselines for API endpoints."""

    @pytest.mark.asyncio
    async def test_list_projects_response_time(self, perf_client: AsyncClient, seeded_data: dict):
        """Measure list projects endpoint response time.

        Target: p95 < 200ms
        """
        times = []

        for _ in range(20):
            start = time.perf_counter()
            response = await perf_client.get("/api/v1/projects")
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert response.status_code == 200

        p95 = sorted(times)[int(len(times) * 0.95)]

        # Log metrics
        print(
            f"\n  Projects List - p50: {statistics.median(times):.1f}ms, "
            f"p95: {p95:.1f}ms, max: {max(times):.1f}ms"
        )

        assert p95 < THRESHOLDS["list_endpoint_p95"], (
            f"p95 response time {p95:.1f}ms exceeds threshold "
            f"{THRESHOLDS['list_endpoint_p95']}ms"
        )

    @pytest.mark.asyncio
    async def test_list_tasks_response_time(self, perf_client: AsyncClient, seeded_data: dict):
        """Measure list tasks endpoint response time.

        Target: p95 < 200ms
        """
        times = []

        for _ in range(20):
            start = time.perf_counter()
            response = await perf_client.get("/api/v1/tasks")
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert response.status_code == 200

        p95 = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\n  Tasks List - p50: {statistics.median(times):.1f}ms, "
            f"p95: {p95:.1f}ms, max: {max(times):.1f}ms"
        )

        assert p95 < THRESHOLDS["list_endpoint_p95"]

    @pytest.mark.asyncio
    async def test_get_project_response_time(self, perf_client: AsyncClient, seeded_data: dict):
        """Measure single project retrieval response time.

        Target: p95 < 100ms
        """
        project_id = seeded_data["project"]["id"]
        times = []

        for _ in range(20):
            start = time.perf_counter()
            response = await perf_client.get(f"/api/v1/projects/{project_id}")
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert response.status_code == 200

        p95 = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\n  Get Project - p50: {statistics.median(times):.1f}ms, "
            f"p95: {p95:.1f}ms, max: {max(times):.1f}ms"
        )

        assert p95 < THRESHOLDS["get_endpoint_p95"]

    @pytest.mark.asyncio
    async def test_create_task_response_time(self, perf_client: AsyncClient, seeded_data: dict):
        """Measure task creation response time.

        Target: p95 < 300ms
        """
        times = []

        for i in range(10):
            task_data = {
                "id": f"T-PERF-TIME-{i:03d}",
                "title": f"Performance test task {i}",
                "summary": "Measuring creation time",
                "description": "Performance test task for timing measurements",
                "status": "new",
                "owner": "perf@test.com",
                "priority": "p2",
                "primary_project": seeded_data["project"]["id"],
                "primary_sprint": seeded_data["sprint"]["id"],
            }

            start = time.perf_counter()
            response = await perf_client.post("/api/v1/tasks", json=task_data)
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert response.status_code == 201

        p95 = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\n  Create Task - p50: {statistics.median(times):.1f}ms, "
            f"p95: {p95:.1f}ms, max: {max(times):.1f}ms"
        )

        assert p95 < THRESHOLDS["create_endpoint_p95"]


class TestConcurrentRequests:
    """Verify API handles concurrent requests without degradation."""

    @pytest.mark.asyncio
    async def test_concurrent_list_requests(self, perf_client: AsyncClient, seeded_data: dict):
        """Test 10 concurrent list requests complete successfully.

        Verifies no request failures under concurrent load.
        """

        async def make_request():
            start = time.perf_counter()
            response = await perf_client.get("/api/v1/projects")
            elapsed_ms = (time.perf_counter() - start) * 1000
            return response.status_code, elapsed_ms

        # Execute 10 concurrent requests
        results = await asyncio.gather(*[make_request() for _ in range(10)])

        status_codes = [r[0] for r in results]
        times = [r[1] for r in results]

        # All should succeed
        assert all(code == 200 for code in status_codes), f"Some requests failed: {status_codes}"

        # Log concurrent performance
        print(
            f"\n  Concurrent (10 requests) - avg: {statistics.mean(times):.1f}ms, "
            f"max: {max(times):.1f}ms"
        )

    @pytest.mark.asyncio
    async def test_sequential_create_requests(self, perf_client: AsyncClient, seeded_data: dict):
        """Test 5 sequential create requests to measure write performance.

        Note: True concurrent write tests require PostgreSQL due to SQLite
        in-memory database limitations with async concurrent writes.
        This test measures sequential write latency instead.
        """
        times = []
        status_codes = []

        for i in range(5):
            task_data = {
                "id": f"T-PERF-SEQ-{i:03d}",
                "title": f"Sequential task {i}",
                "summary": "Sequential creation test",
                "description": "Testing sequential task creation",
                "status": "new",
                "owner": "perf@test.com",
                "priority": "p2",
                "primary_project": seeded_data["project"]["id"],
                "primary_sprint": seeded_data["sprint"]["id"],
            }

            start = time.perf_counter()
            response = await perf_client.post("/api/v1/tasks", json=task_data)
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            status_codes.append(response.status_code)

        # All should succeed
        assert all(code == 201 for code in status_codes), f"Some creates failed: {status_codes}"

        # Each create should be under threshold
        assert max(times) < 300, f"Slowest create: {max(times):.1f}ms > 300ms"

        print(
            f"\n  Sequential Creates (5) - avg: {statistics.mean(times):.1f}ms, "
            f"p95: {sorted(times)[int(len(times) * 0.95)]:.1f}ms"
        )


class TestBulkOperations:
    """Test performance of bulk data operations."""

    @pytest.mark.asyncio
    async def test_bulk_task_creation(self, perf_client: AsyncClient, seeded_data: dict):
        """Create 20 tasks and measure total time.

        Target: Average < 500ms per task
        """
        start_total = time.perf_counter()
        task_count = 20

        for i in range(task_count):
            task_data = {
                "id": f"T-PERF-BULK-{i:03d}",
                "title": f"Bulk task {i}",
                "summary": "Bulk creation test",
                "description": "Testing bulk task creation performance",
                "status": "new",
                "owner": "perf@test.com",
                "priority": "p2",
                "primary_project": seeded_data["project"]["id"],
                "primary_sprint": seeded_data["sprint"]["id"],
            }
            response = await perf_client.post("/api/v1/tasks", json=task_data)
            assert response.status_code == 201

        total_ms = (time.perf_counter() - start_total) * 1000
        avg_per_task = total_ms / task_count

        print(
            f"\n  Bulk Create ({task_count} tasks) - "
            f"total: {total_ms:.0f}ms, avg: {avg_per_task:.1f}ms/task"
        )

        assert (
            avg_per_task < THRESHOLDS["bulk_create_p95"]
        ), f"Average creation time {avg_per_task:.1f}ms exceeds threshold"

    @pytest.mark.asyncio
    async def test_list_with_many_items(self, perf_client: AsyncClient, seeded_data: dict):
        """Create many items then measure list performance.

        Verifies list endpoint scales reasonably.
        """
        # Create 15 action lists
        for i in range(15):
            response = await perf_client.post(
                "/api/v1/action-lists",
                json={
                    "id": f"AL-PERF-{i:03d}",
                    "title": f"Performance test list {i}",
                    "description": "Testing list scaling",
                },
            )
            assert response.status_code == 201

        # Measure list retrieval time
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = await perf_client.get("/api/v1/action-lists")
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert response.status_code == 200

        data = response.json()
        p95 = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\n  List {len(data)} items - p50: {statistics.median(times):.1f}ms, "
            f"p95: {p95:.1f}ms"
        )

        # Should still be fast with 15+ items
        assert p95 < THRESHOLDS["list_endpoint_p95"]


class TestActionListPerformance:
    """Performance tests specific to action list operations."""

    @pytest.mark.asyncio
    async def test_action_list_crud_cycle(self, perf_client: AsyncClient):
        """Measure complete CRUD cycle for action lists.

        Tests: Create → Read → Update → Delete timing
        """
        times = {}

        # Create
        start = time.perf_counter()
        create_response = await perf_client.post(
            "/api/v1/action-lists",
            json={
                "id": "AL-PERF-CRUD",
                "title": "CRUD Performance Test",
                "description": "Measuring CRUD cycle",
            },
        )
        times["create"] = (time.perf_counter() - start) * 1000
        assert create_response.status_code == 201
        list_id = create_response.json()["id"]

        # Read
        start = time.perf_counter()
        read_response = await perf_client.get(f"/api/v1/action-lists/{list_id}")
        times["read"] = (time.perf_counter() - start) * 1000
        assert read_response.status_code == 200

        # Update
        start = time.perf_counter()
        update_response = await perf_client.put(
            f"/api/v1/action-lists/{list_id}",
            json={
                "id": list_id,
                "title": "Updated CRUD Test",
                "description": "Updated description",
            },
        )
        times["update"] = (time.perf_counter() - start) * 1000
        assert update_response.status_code == 200

        # Delete
        start = time.perf_counter()
        delete_response = await perf_client.delete(f"/api/v1/action-lists/{list_id}")
        times["delete"] = (time.perf_counter() - start) * 1000
        assert delete_response.status_code == 204

        print(
            f"\n  CRUD Cycle - Create: {times['create']:.1f}ms, "
            f"Read: {times['read']:.1f}ms, Update: {times['update']:.1f}ms, "
            f"Delete: {times['delete']:.1f}ms"
        )

        # All operations should be reasonably fast
        assert max(times.values()) < THRESHOLDS["create_endpoint_p95"]

    @pytest.mark.asyncio
    async def test_action_list_with_tasks(self, perf_client: AsyncClient, seeded_data: dict):
        """Measure action list task association performance."""
        # Create action list
        al_response = await perf_client.post(
            "/api/v1/action-lists",
            json={
                "id": "AL-PERF-TASKS",
                "title": "Task Association Performance",
                "description": "Testing task associations",
            },
        )
        assert al_response.status_code == 201
        list_id = al_response.json()["id"]

        # Create and associate 5 tasks
        times = []
        for i in range(5):
            # Create task
            task_data = {
                "id": f"T-PERF-AL-{i:03d}",
                "title": f"Action list task {i}",
                "summary": "Association test",
                "description": "Testing task association performance",
                "status": "new",
                "owner": "perf@test.com",
                "priority": "p2",
                "primary_project": seeded_data["project"]["id"],
                "primary_sprint": seeded_data["sprint"]["id"],
            }
            await perf_client.post("/api/v1/tasks", json=task_data)

            # Time the association
            start = time.perf_counter()
            assoc_response = await perf_client.post(
                f"/api/v1/action-lists/{list_id}/tasks",
                params={"task_id": f"T-PERF-AL-{i:03d}"},
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            assert assoc_response.status_code == 200

        # Time task list retrieval
        start = time.perf_counter()
        tasks_response = await perf_client.get(f"/api/v1/action-lists/{list_id}/tasks")
        get_tasks_time = (time.perf_counter() - start) * 1000
        assert tasks_response.status_code == 200

        print(
            f"\n  Task Association - avg: {statistics.mean(times):.1f}ms, "
            f"get tasks (5 items): {get_tasks_time:.1f}ms"
        )

        assert get_tasks_time < THRESHOLDS["get_endpoint_p95"]
