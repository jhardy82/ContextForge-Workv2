"""
Base Validation Agent

Abstract base class for all validation agents in the swarm.
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cf_core.shared.result import Result


class BaseValidationAgent(ABC):
    """Base class for validation agents"""

    def __init__(self, db_path: str, config: dict[str, Any] = None):
        """
        Initialize validation agent

        Args:
            db_path: Path to SQLite database
            config: Optional configuration dictionary
        """
        self.db_path = db_path
        self.config = config or {}
        self.results = []
        self.agent_name = self.__class__.__name__.replace("Agent", "")

    @abstractmethod
    def validate(self) -> Result[dict[str, Any]]:
        """
        Execute validation logic

        Returns:
            Result containing validation report
        """
        pass

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _utc_now(self) -> str:
        """Get current UTC timestamp in ISO8601 format"""
        return datetime.now(UTC).isoformat()

    def _record_test_result(
        self,
        test_name: str,
        passed: bool,
        expected: Any = None,
        actual: Any = None,
        severity: str = "normal",
        details: str = None,
    ):
        """
        Record a test result

        Args:
            test_name: Name of the test
            passed: Whether the test passed
            expected: Expected value (optional)
            actual: Actual value (optional)
            severity: Severity level (normal, warning, critical)
            details: Additional details
        """
        result = {
            "test": test_name,
            "passed": passed,
            "severity": severity,
            "timestamp": self._utc_now(),
        }

        if expected is not None:
            result["expected"] = expected
        if actual is not None:
            result["actual"] = actual
        if details:
            result["details"] = details

        self.results.append(result)

    def _emit_evidence(self, payload: dict[str, Any]):
        """
        Emit evidence event for audit trail

        Args:
            payload: Evidence payload
        """
        if not self.config.get("emit_evidence", True):
            return

        evidence_dir = Path(self.db_path).parent.parent / "evidence"
        evidence_dir.mkdir(exist_ok=True)

        evidence_file = (
            evidence_dir / f"validation_{self.agent_name}_{int(datetime.now().timestamp())}.json"
        )

        evidence = {
            "agent": self.agent_name,
            "timestamp": self._utc_now(),
            "action": "validation_executed",
            "payload": payload,
        }

        with open(evidence_file, "w") as f:
            json.dump(evidence, f, indent=2)

    def _generate_report(self) -> dict[str, Any]:
        """
        Generate validation report from test results

        Returns:
            Structured validation report
        """
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total_tests - passed

        critical_failures = [
            r for r in self.results if not r["passed"] and r.get("severity") == "critical"
        ]

        warnings = [r for r in self.results if not r["passed"] and r.get("severity") == "warning"]

        report = {
            "agent": self.agent_name,
            "timestamp": self._utc_now(),
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "critical_failures": len(critical_failures),
            "warnings": len(warnings),
            "test_results": self.results,
            "summary": {
                "status": "PASSED" if failed == 0 else "FAILED",
                "message": self._generate_summary_message(
                    passed, failed, critical_failures, warnings
                ),
            },
        }

        return report

    def _generate_summary_message(
        self, passed: int, failed: int, critical_failures: list, warnings: list
    ) -> str:
        """Generate human-readable summary message"""
        if failed == 0:
            return f"All {passed} tests passed successfully"

        msg_parts = [f"{failed} of {passed + failed} tests failed"]

        if critical_failures:
            msg_parts.append(f"{len(critical_failures)} critical")
        if warnings:
            msg_parts.append(f"{len(warnings)} warnings")

        return ", ".join(msg_parts)

    def _execute_query(self, sql: str, params: tuple = None) -> list[sqlite3.Row]:
        """
        Execute SQL query and return results

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            List of result rows
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    def _get_task_count(self, **filters) -> int:
        """
        Get count of tasks matching filters

        Args:
            **filters: Field filters (status, project_id, sprint_id, etc.)

        Returns:
            Count of matching tasks
        """
        conn = self._get_connection()
        try:
            where_clauses = ["deleted_at IS NULL"]
            params = []

            for field, value in filters.items():
                where_clauses.append(f"{field} = ?")
                params.append(value)

            sql = f"SELECT COUNT(*) as count FROM tasks WHERE {' AND '.join(where_clauses)}"
            cursor = conn.execute(sql, params)
            row = cursor.fetchone()
            return row["count"] if row else 0
        finally:
            conn.close()
