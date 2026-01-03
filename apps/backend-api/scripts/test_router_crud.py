#!/usr/bin/env python3
"""
CRUD Test Script for SQLAlchemy-Converted Routers

Tests all four main routers (tasks, projects, sprints, action_lists)
with CREATE, READ, UPDATE, DELETE operations.

Usage:
    python scripts/test_router_crud.py [--base-url URL]
    python scripts/test_router_crud.py --router projects
    python scripts/test_router_crud.py --verbose
"""

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

# Configuration
DEFAULT_BASE_URL = "http://127.0.0.1:8002/api/v1"


@dataclass
class TestResult:
    """Result of a single test."""

    name: str
    success: bool
    message: str
    duration_ms: float
    response_data: Any = None


class RouterCRUDTester:
    """Test harness for router CRUD operations."""

    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.results: list[TestResult] = []

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  [DEBUG] {message}")

    def _check_health(self, base_url: str) -> bool:
        """Check API health endpoint."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        name: str,
        json_data: dict | None = None,
        expected_status: int = 200,
    ) -> TestResult:
        """Execute a single API test."""
        url = f"{self.base_url}{endpoint}"
        start = time.perf_counter()

        try:
            self.log(f"{method} {url}")
            if json_data:
                self.log(f"  Payload: {json_data}")

            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json_data,
                )
            duration_ms = (time.perf_counter() - start) * 1000

            if response.status_code == expected_status:
                try:
                    data = response.json()
                except Exception:
                    data = response.text

                result = TestResult(
                    name=name,
                    success=True,
                    message=f"HTTP {response.status_code} ({duration_ms:.0f}ms)",
                    duration_ms=duration_ms,
                    response_data=data,
                )
            else:
                result = TestResult(
                    name=name,
                    success=False,
                    message=f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}",
                    duration_ms=duration_ms,
                )

        except httpx.ConnectError:
            result = TestResult(
                name=name,
                success=False,
                message=f"Connection failed - is the server running at {self.base_url}?",
                duration_ms=0,
            )
        except Exception as e:
            result = TestResult(
                name=name,
                success=False,
                message=f"Error: {e}",
                duration_ms=0,
            )

        self.results.append(result)
        return result

    def print_result(self, result: TestResult) -> None:
        """Print a test result."""
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.name}: {result.message}")

    def test_projects_router(self) -> bool:
        """Test projects router CRUD operations."""
        print("\n📁 Testing Projects Router")
        print("-" * 40)

        # CREATE
        result = self.test_endpoint(
            "POST",
            "/projects/",
            "CREATE project",
            json_data={"name": "Test Project", "description": "CRUD test", "status": "active"},
            expected_status=201,
        )
        self.print_result(result)

        if not result.success or not result.response_data:
            return False

        project_id = result.response_data.get("id")
        if not project_id:
            print("  ❌ No project ID in response")
            return False

        self.log(f"Created project: {project_id}")

        # LIST
        result = self.test_endpoint("GET", "/projects/", "LIST projects")
        self.print_result(result)

        # READ
        result = self.test_endpoint("GET", f"/projects/{project_id}", "READ project")
        self.print_result(result)

        # UPDATE
        result = self.test_endpoint(
            "PUT",
            f"/projects/{project_id}",
            "UPDATE project",
            json_data={"description": "Updated via CRUD test"},
        )
        self.print_result(result)

        # DELETE
        result = self.test_endpoint(
            "DELETE",
            f"/projects/{project_id}",
            "DELETE project",
            expected_status=204,
        )
        self.print_result(result)

        return all(r.success for r in self.results[-5:])

    def test_sprints_router(self) -> bool:
        """Test sprints router CRUD operations."""
        print("\n🏃 Testing Sprints Router")
        print("-" * 40)

        # CREATE
        result = self.test_endpoint(
            "POST",
            "/sprints/",
            "CREATE sprint",
            json_data={
                "name": "Test Sprint",
                "goal": "CRUD test goal",
                "status": "planning",
                "start_date": "2025-01-01",
                "end_date": "2025-01-14",
            },
            expected_status=201,
        )
        self.print_result(result)

        if not result.success or not result.response_data:
            return False

        sprint_id = result.response_data.get("id")
        if not sprint_id:
            print("  ❌ No sprint ID in response")
            return False

        self.log(f"Created sprint: {sprint_id}")

        # LIST
        result = self.test_endpoint("GET", "/sprints/", "LIST sprints")
        self.print_result(result)

        # READ
        result = self.test_endpoint("GET", f"/sprints/{sprint_id}", "READ sprint")
        self.print_result(result)

        # UPDATE
        result = self.test_endpoint(
            "PUT",
            f"/sprints/{sprint_id}",
            "UPDATE sprint",
            json_data={"goal": "Updated goal via CRUD test"},
        )
        self.print_result(result)

        # DELETE
        result = self.test_endpoint(
            "DELETE",
            f"/sprints/{sprint_id}",
            "DELETE sprint",
            expected_status=204,
        )
        self.print_result(result)

        return all(r.success for r in self.results[-5:])

    def test_action_lists_router(self) -> bool:
        """Test action_lists router CRUD operations."""
        print("\n📋 Testing Action Lists Router")
        print("-" * 40)

        # CREATE
        result = self.test_endpoint(
            "POST",
            "/action-lists/",
            "CREATE action list",
            json_data={
                "name": "Test Action List",
                "description": "CRUD test list",
                "status": "active",
                "task_ids": [],
            },
            expected_status=201,
        )
        self.print_result(result)

        if not result.success or not result.response_data:
            return False

        action_list_id = result.response_data.get("id")
        if not action_list_id:
            print("  ❌ No action list ID in response")
            return False

        self.log(f"Created action list: {action_list_id}")

        # LIST
        result = self.test_endpoint("GET", "/action-lists/", "LIST action lists")
        self.print_result(result)

        # READ
        result = self.test_endpoint("GET", f"/action-lists/{action_list_id}", "READ action list")
        self.print_result(result)

        # UPDATE
        result = self.test_endpoint(
            "PUT",
            f"/action-lists/{action_list_id}",
            "UPDATE action list",
            json_data={"description": "Updated via CRUD test"},
        )
        self.print_result(result)

        # DELETE
        result = self.test_endpoint(
            "DELETE",
            f"/action-lists/{action_list_id}",
            "DELETE action list",
            expected_status=204,
        )
        self.print_result(result)

        return all(r.success for r in self.results[-5:])

    def test_tasks_router(self) -> bool:
        """Test tasks router CRUD operations."""
        print("\n✅ Testing Tasks Router")
        print("-" * 40)

        # CREATE
        result = self.test_endpoint(
            "POST",
            "/tasks/",
            "CREATE task",
            json_data={
                "title": "Test Task",
                "description": "CRUD test task",
                "status": "todo",
                "priority": "medium",
            },
            expected_status=201,
        )
        self.print_result(result)

        if not result.success or not result.response_data:
            return False

        task_id = result.response_data.get("id")
        if not task_id:
            print("  ❌ No task ID in response")
            return False

        self.log(f"Created task: {task_id}")

        # LIST
        result = self.test_endpoint("GET", "/tasks/", "LIST tasks")
        self.print_result(result)

        # READ
        result = self.test_endpoint("GET", f"/tasks/{task_id}", "READ task")
        self.print_result(result)

        # UPDATE
        result = self.test_endpoint(
            "PUT",
            f"/tasks/{task_id}",
            "UPDATE task",
            json_data={"description": "Updated via CRUD test"},
        )
        self.print_result(result)

        # DELETE
        result = self.test_endpoint(
            "DELETE",
            f"/tasks/{task_id}",
            "DELETE task",
            expected_status=204,
        )
        self.print_result(result)

        return all(r.success for r in self.results[-5:])

    def run_all_tests(self, routers: list[str] | None = None) -> bool:
        """Run tests for specified routers (or all if None)."""
        all_routers = ["tasks", "projects", "sprints", "action-lists"]
        routers_to_test = routers or all_routers

        print("=" * 50)
        print("🧪 SQLAlchemy Router CRUD Tests")
        print(f"   Base URL: {self.base_url}")
        print(f"   Routers: {', '.join(routers_to_test)}")
        print(f"   Started: {datetime.now().isoformat()}")
        print("=" * 50)

        # Health check first (use root URL, not /api/v1)
        health_url = self.base_url.replace("/api/v1", "")
        health_result = self._check_health(health_url)
        if not health_result:
            print("\n❌ API is not responding. Is the server running?")
            print(f"   Expected URL: {health_url}/health")
            return False
        print("✅ API Health: OK")

        router_results = {}

        if "tasks" in routers_to_test:
            router_results["tasks"] = self.test_tasks_router()

        if "projects" in routers_to_test:
            router_results["projects"] = self.test_projects_router()

        if "sprints" in routers_to_test:
            router_results["sprints"] = self.test_sprints_router()

        if "action-lists" in routers_to_test:
            router_results["action-lists"] = self.test_action_lists_router()

        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)

        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        total_time = sum(r.duration_ms for r in self.results)

        for router, success in router_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {router}: {status}")

        print(f"\n  Total: {passed}/{len(self.results)} tests passed")
        print(f"  Time: {total_time:.0f}ms")

        if failed > 0:
            print(f"\n❌ {failed} test(s) failed")
            return False

        print("\n✅ All tests passed!")
        return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test SQLAlchemy-converted routers with CRUD operations"
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--router",
        choices=["tasks", "projects", "sprints", "action-lists"],
        action="append",
        dest="routers",
        help="Specific router(s) to test (can be repeated)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    tester = RouterCRUDTester(args.base_url, verbose=args.verbose)
    success = tester.run_all_tests(args.routers)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
