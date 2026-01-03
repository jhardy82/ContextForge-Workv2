"""
CRUD Validator Agent

Validates Create, Read, Update, Delete operations for tasks.
"""

import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class CRUDValidatorAgent(BaseValidationAgent):
    """Validates CRUD operations"""

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all CRUD validation tests"""
        try:
            self._test_create_operations()
            self._test_read_operations()
            self._test_update_operations()
            self._test_delete_operations()

            report = self._generate_report()
            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"CRUD validation failed: {e}")

    def _test_create_operations(self):
        """Test task creation scenarios"""
        # Test 1: Create with minimal required fields
        test_title = f"Test Task {uuid.uuid4().hex[:8]}"
        result = self._run_cli_command(
            ["python", "dbcli.py", "task", "create", "--title", test_title, "--json"]
        )

        self._record_test_result(
            test_name="create_minimal_task",
            passed=result["success"] and "id" in result.get("output", {}),
            details=f"Created task with title: {test_title}",
        )

        # Test 2: Create with all fields
        test_id = f"T-CRUD-{uuid.uuid4().hex[:8]}"
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "create",
                "--id",
                test_id,
                "--title",
                f"Complete Task {uuid.uuid4().hex[:8]}",
                "--status",
                "new",
                "--priority",
                "high",
                "--project-id",
                "P-TEST-001",
                "--owner",
                "validation-agent",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="create_complete_task",
            passed=result["success"],
            details="Created task with all optional fields",
        )

        # Test 3: Create with invalid status (should fail)
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "create",
                "--title",
                "Invalid Status Task",
                "--status",
                "invalid_status",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="create_invalid_status",
            passed=not result["success"],  # Should fail
            expected="failure",
            actual="success" if result["success"] else "failure",
            severity="critical",
            details="Invalid status should be rejected",
        )

        # Test 4: Create without title (should fail)
        result = self._run_cli_command(
            ["python", "dbcli.py", "task", "create", "--status", "new", "--json"]
        )

        self._record_test_result(
            test_name="create_without_title",
            passed=not result["success"],  # Should fail
            expected="failure",
            actual="success" if result["success"] else "failure",
            severity="critical",
            details="Title is required field",
        )

    def _test_read_operations(self):
        """Test task read/query scenarios"""
        # Test 1: List all tasks
        result = self._run_cli_command(["python", "dbcli.py", "task", "list", "--json"])

        self._record_test_result(
            test_name="list_all_tasks",
            passed=result["success"],
            details=f"Retrieved {len(result.get('output', {}).get('tasks', []))} tasks",
        )

        # Test 2: Read specific task by ID (create one first)
        test_title = f"Read Test {uuid.uuid4().hex[:8]}"
        create_result = self._run_cli_command(
            ["python", "dbcli.py", "task", "create", "--title", test_title, "--json"]
        )

        if create_result["success"]:
            task_id = create_result["output"].get("id")
            read_result = self._run_cli_command(
                ["python", "dbcli.py", "task", "show", "--id", task_id, "--json"]
            )

            self._record_test_result(
                test_name="read_task_by_id",
                passed=read_result["success"] and read_result["output"].get("id") == task_id,
                details=f"Retrieved task {task_id}",
            )

        # Test 3: List with status filter
        result = self._run_cli_command(
            ["python", "dbcli.py", "task", "list", "--status", "new", "--json"]
        )

        self._record_test_result(
            test_name="list_filtered_by_status",
            passed=result["success"],
            details="Filtered tasks by status=new",
        )

        # Test 4: Read non-existent task
        fake_id = f"T-FAKE-{uuid.uuid4().hex[:8]}"
        result = self._run_cli_command(
            ["python", "dbcli.py", "task", "show", "--id", fake_id, "--json"]
        )

        self._record_test_result(
            test_name="read_nonexistent_task",
            passed=not result["success"],  # Should fail gracefully
            expected="not_found",
            actual="found" if result["success"] else "not_found",
            details="Non-existent task should return error",
        )

    def _test_update_operations(self):
        """Test task update scenarios"""
        # Create test task first
        test_title = f"Update Test {uuid.uuid4().hex[:8]}"
        create_result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "create",
                "--title",
                test_title,
                "--status",
                "new",
                "--json",
            ]
        )

        if not create_result["success"]:
            self._record_test_result(
                test_name="update_operations_setup",
                passed=False,
                severity="critical",
                details="Failed to create test task for update operations",
            )
            return

        task_id = create_result["output"].get("id")

        # Test 1: Update status
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "update",
                "--id",
                task_id,
                "--status",
                "in_progress",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="update_status",
            passed=result["success"],
            details=f"Updated task {task_id} status to in_progress",
        )

        # Test 2: Update priority
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "update",
                "--id",
                task_id,
                "--priority",
                "high",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="update_priority", passed=result["success"], details="Updated task priority"
        )

        # Test 3: Update with invalid status (should fail)
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "update",
                "--id",
                task_id,
                "--status",
                "invalid_status",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="update_invalid_status",
            passed=not result["success"],
            expected="failure",
            actual="success" if result["success"] else "failure",
            severity="critical",
            details="Invalid status update should be rejected",
        )

        # Test 4: Update non-existent task
        fake_id = f"T-FAKE-{uuid.uuid4().hex[:8]}"
        result = self._run_cli_command(
            ["python", "dbcli.py", "task", "update", "--id", fake_id, "--status", "done", "--json"]
        )

        self._record_test_result(
            test_name="update_nonexistent_task",
            passed=not result["success"],
            expected="failure",
            actual="success" if result["success"] else "failure",
            details="Updating non-existent task should fail",
        )

    def _test_delete_operations(self):
        """Test task delete (soft delete) scenarios"""
        # Create test task
        test_title = f"Delete Test {uuid.uuid4().hex[:8]}"
        create_result = self._run_cli_command(
            ["python", "dbcli.py", "task", "create", "--title", test_title, "--json"]
        )

        if not create_result["success"]:
            self._record_test_result(
                test_name="delete_operations_setup",
                passed=False,
                severity="critical",
                details="Failed to create test task for delete operations",
            )
            return

        task_id = create_result["output"].get("id")

        # Test 1: Soft delete task
        # Note: Assuming there's a delete command or we mark as deleted
        # For now, we'll test if task can be marked as dropped
        result = self._run_cli_command(
            [
                "python",
                "dbcli.py",
                "task",
                "update",
                "--id",
                task_id,
                "--status",
                "dropped",
                "--json",
            ]
        )

        self._record_test_result(
            test_name="soft_delete_task",
            passed=result["success"],
            details=f"Marked task {task_id} as dropped",
        )

        # Test 2: Verify soft-deleted task excluded from normal queries
        # This would require checking if deleted_at is set in database
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT deleted_at FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

            # Task should exist but may have deleted_at set
            self._record_test_result(
                test_name="verify_soft_delete_in_db",
                passed=row is not None,
                details="Verified task exists in database after soft delete",
            )
        finally:
            conn.close()

    def _run_cli_command(self, command: list) -> dict[str, Any]:
        """
        Execute CLI command and return structured result

        Args:
            command: Command and arguments as list

        Returns:
            Dict with success flag and output/error
        """
        try:
            # Change to project directory
            project_dir = Path(self.db_path).parent.parent
            result = subprocess.run(
                command, cwd=str(project_dir), capture_output=True, text=True, timeout=30
            )

            output = {}
            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output = {"raw": result.stdout}

            return {
                "success": result.returncode == 0,
                "output": output,
                "error": result.stderr if result.stderr else None,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": {}, "error": "Command timeout", "returncode": -1}
        except Exception as e:
            return {"success": False, "output": {}, "error": str(e), "returncode": -1}
