"""
Data Integrity Validator Agent

Validates data consistency, referential integrity, and constraint enforcement.
"""

import json
from datetime import datetime
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class DataIntegrityValidatorAgent(BaseValidationAgent):
    """Validates data integrity"""

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all data integrity validation tests"""
        try:
            issues = []

            # Run all integrity checks
            issues.extend(self._check_foreign_keys())
            issues.extend(self._check_json_fields())
            issues.extend(self._check_orphaned_records())
            issues.extend(self._check_timestamps())
            issues.extend(self._check_unique_constraints())
            issues.extend(self._check_soft_deletes())

            # Record results
            for issue in issues:
                self._record_test_result(
                    test_name=issue["check"],
                    passed=False,
                    severity=issue["severity"],
                    details=issue["description"],
                )

            # Add passing tests
            total_checks = 6  # Number of check categories
            passed_checks = total_checks - len(set(i["check"] for i in issues))

            for _ in range(passed_checks):
                self._record_test_result(
                    test_name="integrity_check_passed",
                    passed=True,
                    details="No integrity issues found",
                )

            report = self._generate_report()
            report["issues"] = issues
            report["critical_count"] = sum(1 for i in issues if i["severity"] == "critical")
            report["warning_count"] = sum(1 for i in issues if i["severity"] == "warning")

            self._emit_evidence(report)

            if any(i["severity"] == "critical" for i in issues):
                return Result.failure(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"Data integrity validation failed: {e}")

    def _check_foreign_keys(self) -> list[dict[str, Any]]:
        """Check referential integrity for foreign keys"""
        issues = []

        # Check tasks with invalid project_id
        rows = self._execute_query("""
            SELECT t.id, t.title, t.project_id
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.project_id IS NOT NULL
              AND t.project_id != ''
              AND p.id IS NULL
              AND t.deleted_at IS NULL
        """)

        for row in rows:
            issues.append(
                {
                    "check": "foreign_key_project",
                    "type": "foreign_key_violation",
                    "severity": "critical",
                    "table": "tasks",
                    "field": "project_id",
                    "record_id": row["id"],
                    "record_title": row["title"],
                    "invalid_reference": row["project_id"],
                    "description": f"Task {row['id']} references non-existent project {row['project_id']}",
                }
            )

        # Check tasks with invalid sprint_id
        rows = self._execute_query("""
            SELECT t.id, t.title, t.sprint_id
            FROM tasks t
            LEFT JOIN sprints s ON t.sprint_id = s.id
            WHERE t.sprint_id IS NOT NULL
              AND t.sprint_id != ''
              AND s.id IS NULL
              AND t.deleted_at IS NULL
        """)

        for row in rows:
            issues.append(
                {
                    "check": "foreign_key_sprint",
                    "type": "foreign_key_violation",
                    "severity": "critical",
                    "table": "tasks",
                    "field": "sprint_id",
                    "record_id": row["id"],
                    "record_title": row["title"],
                    "invalid_reference": row["sprint_id"],
                    "description": f"Task {row['id']} references non-existent sprint {row['sprint_id']}",
                }
            )

        # Check sprints with invalid project_id (sprints don't have deleted_at column)
        rows = self._execute_query("""
            SELECT s.id, s.name, s.project_id
            FROM sprints s
            LEFT JOIN projects p ON s.project_id = p.id
            WHERE s.project_id IS NOT NULL
              AND s.project_id != ''
              AND p.id IS NULL
        """)

        for row in rows:
            issues.append(
                {
                    "check": "foreign_key_sprint_project",
                    "type": "foreign_key_violation",
                    "severity": "critical",
                    "table": "sprints",
                    "field": "project_id",
                    "record_id": row["id"],
                    "record_title": row["name"],
                    "invalid_reference": row["project_id"],
                    "description": f"Sprint {row['id']} references non-existent project {row['project_id']}",
                }
            )

        return issues

    def _check_json_fields(self) -> list[dict[str, Any]]:
        """Validate JSON field structure and syntax"""
        issues = []

        # Check tasks.depends_on JSON field
        rows = self._execute_query("""
            SELECT id, title, depends_on
            FROM tasks
            WHERE depends_on IS NOT NULL
              AND depends_on != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                json.loads(row["depends_on"])
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "check": "json_validity_depends_on",
                        "type": "invalid_json",
                        "severity": "critical",
                        "table": "tasks",
                        "field": "depends_on",
                        "record_id": row["id"],
                        "record_title": row["title"],
                        "description": f"Task {row['id']} has invalid JSON in depends_on: {e}",
                    }
                )

        # Check tasks.blocks JSON field
        rows = self._execute_query("""
            SELECT id, title, blocks
            FROM tasks
            WHERE blocks IS NOT NULL
              AND blocks != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                json.loads(row["blocks"])
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "check": "json_validity_blocks",
                        "type": "invalid_json",
                        "severity": "critical",
                        "table": "tasks",
                        "field": "blocks",
                        "record_id": row["id"],
                        "record_title": row["title"],
                        "description": f"Task {row['id']} has invalid JSON in blocks: {e}",
                    }
                )

        # Check tasks.assignees JSON field
        rows = self._execute_query("""
            SELECT id, title, assignees
            FROM tasks
            WHERE assignees IS NOT NULL
              AND assignees != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                json.loads(row["assignees"])
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "check": "json_validity_assignees",
                        "type": "invalid_json",
                        "severity": "warning",
                        "table": "tasks",
                        "field": "assignees",
                        "record_id": row["id"],
                        "record_title": row["title"],
                        "description": f"Task {row['id']} has invalid JSON in assignees: {e}",
                    }
                )

        return issues

    def _check_orphaned_records(self) -> list[dict[str, Any]]:
        """Find orphaned records (references to deleted items)"""
        issues = []

        # Find tasks depending on deleted tasks
        rows = self._execute_query("""
            SELECT t.id, t.title, t.depends_on
            FROM tasks t
            WHERE t.depends_on IS NOT NULL
              AND t.depends_on != ''
              AND t.deleted_at IS NULL
        """)

        for row in rows:
            try:
                depends_on = json.loads(row["depends_on"])
                if isinstance(depends_on, list):
                    for dep_id in depends_on:
                        # Check if referenced task exists and is not deleted
                        dep_rows = self._execute_query(
                            "SELECT id, deleted_at FROM tasks WHERE id = ?", (dep_id,)
                        )

                        if not dep_rows or dep_rows[0]["deleted_at"] is not None:
                            issues.append(
                                {
                                    "check": "orphaned_dependency",
                                    "type": "orphaned_reference",
                                    "severity": "warning",
                                    "table": "tasks",
                                    "field": "depends_on",
                                    "record_id": row["id"],
                                    "record_title": row["title"],
                                    "orphaned_reference": dep_id,
                                    "description": f"Task {row['id']} depends on deleted/non-existent task {dep_id}",
                                }
                            )
            except (json.JSONDecodeError, TypeError):
                pass  # Already caught in JSON validation

        return issues

    def _check_timestamps(self) -> list[dict[str, Any]]:
        """Validate timestamp consistency"""
        issues = []

        # Check created_at <= updated_at
        rows = self._execute_query("""
            SELECT id, title, created_at, updated_at
            FROM tasks
            WHERE created_at IS NOT NULL
              AND updated_at IS NOT NULL
              AND created_at > updated_at
              AND deleted_at IS NULL
        """)

        for row in rows:
            issues.append(
                {
                    "check": "timestamp_consistency",
                    "type": "timestamp_violation",
                    "severity": "critical",
                    "table": "tasks",
                    "field": "created_at, updated_at",
                    "record_id": row["id"],
                    "record_title": row["title"],
                    "description": f"Task {row['id']} has created_at > updated_at",
                }
            )

        # Check done tasks have done_date
        rows = self._execute_query("""
            SELECT id, title, status, done_date
            FROM tasks
            WHERE status = 'done'
              AND (done_date IS NULL OR done_date = '')
              AND deleted_at IS NULL
        """)

        for row in rows:
            issues.append(
                {
                    "check": "done_date_required",
                    "type": "missing_field",
                    "severity": "warning",
                    "table": "tasks",
                    "field": "done_date",
                    "record_id": row["id"],
                    "record_title": row["title"],
                    "description": f"Task {row['id']} has status=done but no done_date",
                }
            )

        # Check timestamp format (should be ISO8601)
        rows = self._execute_query("""
            SELECT id, title, created_at, updated_at
            FROM tasks
            WHERE deleted_at IS NULL
            LIMIT 100
        """)

        for row in rows:
            for field in ["created_at", "updated_at"]:
                timestamp = row[field]
                if timestamp:
                    try:
                        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        issues.append(
                            {
                                "check": "timestamp_format",
                                "type": "invalid_format",
                                "severity": "warning",
                                "table": "tasks",
                                "field": field,
                                "record_id": row["id"],
                                "record_title": row["title"],
                                "description": f"Task {row['id']} has invalid {field} format: {timestamp}",
                            }
                        )

        return issues

    def _check_unique_constraints(self) -> list[dict[str, Any]]:
        """Check for unique constraint violations"""
        issues = []

        # Check for duplicate task IDs (should never happen with PRIMARY KEY)
        rows = self._execute_query("""
            SELECT id, COUNT(*) as count
            FROM tasks
            GROUP BY id
            HAVING count > 1
        """)

        for row in rows:
            issues.append(
                {
                    "check": "unique_constraint_task_id",
                    "type": "duplicate_id",
                    "severity": "critical",
                    "table": "tasks",
                    "field": "id",
                    "record_id": row["id"],
                    "description": f"Duplicate task ID found: {row['id']} ({row['count']} instances)",
                }
            )

        return issues

    def _check_soft_deletes(self) -> list[dict[str, Any]]:
        """Validate soft delete consistency (only tasks table has deleted_at)"""
        issues = []

        # Check that deleted tasks are not in active sprints
        rows = self._execute_query("""
            SELECT t.id, t.title, t.deleted_at, s.id as sprint_id, s.name as sprint_name, s.status as sprint_status
            FROM tasks t
            JOIN sprints s ON t.sprint_id = s.id
            WHERE t.deleted_at IS NOT NULL
              AND s.status = 'active'
        """)

        for row in rows:
            issues.append(
                {
                    "check": "soft_delete_consistency",
                    "type": "deleted_in_active_sprint",
                    "severity": "warning",
                    "table": "tasks",
                    "record_id": row["id"],
                    "record_title": row["title"],
                    "description": f"Deleted task {row['id']} still assigned to active sprint {row['sprint_id']}",
                }
            )

        return issues
