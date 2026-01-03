"""
Audit Trail Validator Agent

Validates evidence logging and audit trail completeness.
"""

import json
import uuid
from pathlib import Path
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class AuditTrailValidatorAgent(BaseValidationAgent):
    """Validates audit trail and evidence logging"""

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all audit trail validation tests"""
        try:
            self._test_evidence_emission()
            self._test_evidence_structure()
            self._test_audit_completeness()

            report = self._generate_report()
            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"Audit trail validation failed: {e}")

    def _test_evidence_emission(self):
        """Test that operations emit evidence"""
        # Create a task and check if evidence is generated
        task_id = f"T-AUDIT-{uuid.uuid4().hex[:8]}"
        conn = self._get_connection()

        try:
            conn.execute(
                """
                INSERT INTO tasks (id, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, "Audit Test", "new", self._utc_now(), self._utc_now()),
            )
            conn.commit()

            # Check if evidence directory exists and has content
            evidence_dir = Path(self.db_path).parent.parent / "evidence"
            has_evidence_dir = evidence_dir.exists()

            self._record_test_result(
                test_name="evidence_directory_exists",
                passed=has_evidence_dir,
                severity="warning" if not has_evidence_dir else "normal",
                details=f"Evidence directory {'exists' if has_evidence_dir else 'missing'}",
            )

            # Check for evidence files
            if has_evidence_dir:
                evidence_files = list(evidence_dir.glob("*.json"))
                self._record_test_result(
                    test_name="evidence_files_present",
                    passed=len(evidence_files) > 0,
                    severity="warning",
                    details=f"Found {len(evidence_files)} evidence files",
                )
        finally:
            conn.close()

    def _test_evidence_structure(self):
        """Validate evidence file structure"""
        evidence_dir = Path(self.db_path).parent.parent / "evidence"

        if not evidence_dir.exists():
            self._record_test_result(
                test_name="evidence_structure_validation",
                passed=False,
                severity="warning",
                details="No evidence directory to validate",
            )
            return

        evidence_files = list(evidence_dir.glob("*.json"))[:10]  # Check first 10 files

        required_fields = ["agent", "timestamp", "action", "payload"]

        for evidence_file in evidence_files:
            try:
                with open(evidence_file) as f:
                    evidence = json.load(f)

                # Check required fields
                missing_fields = [f for f in required_fields if f not in evidence]

                self._record_test_result(
                    test_name=f"evidence_structure_{evidence_file.name}",
                    passed=len(missing_fields) == 0,
                    severity="warning" if missing_fields else "normal",
                    details=f"Missing fields: {missing_fields}"
                    if missing_fields
                    else "All required fields present",
                )
            except json.JSONDecodeError:
                self._record_test_result(
                    test_name=f"evidence_json_valid_{evidence_file.name}",
                    passed=False,
                    severity="warning",
                    details="Invalid JSON in evidence file",
                )
            except Exception as e:
                self._record_test_result(
                    test_name=f"evidence_read_{evidence_file.name}",
                    passed=False,
                    severity="warning",
                    details=f"Failed to read evidence: {e}",
                )

    def _test_audit_completeness(self):
        """Test audit trail completeness"""
        # Check for audit_tag field in tasks
        rows = self._execute_query("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN audit_tag IS NOT NULL AND audit_tag != '' THEN 1 ELSE 0 END) as with_audit_tag
            FROM tasks
            WHERE deleted_at IS NULL
        """)

        if rows:
            total = rows[0]["total"]
            with_audit_tag = rows[0]["with_audit_tag"]
            coverage = (with_audit_tag / total * 100) if total > 0 else 0

            self._record_test_result(
                test_name="audit_tag_coverage",
                passed=coverage >= 80,  # 80% threshold
                expected=">= 80%",
                actual=f"{coverage:.1f}%",
                severity="warning" if coverage < 80 else "normal",
                details=f"{with_audit_tag}/{total} tasks have audit_tag ({coverage:.1f}%)",
            )

        # Check for correlation_hint tracking
        rows = self._execute_query("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN correlation_hint IS NOT NULL AND correlation_hint != '' THEN 1 ELSE 0 END) as with_correlation
            FROM tasks
            WHERE deleted_at IS NULL
        """)

        if rows:
            total = rows[0]["total"]
            with_correlation = rows[0]["with_correlation"]
            coverage = (with_correlation / total * 100) if total > 0 else 0

            self._record_test_result(
                test_name="correlation_hint_coverage",
                passed=True,  # Correlation is optional
                severity="normal",
                details=f"{with_correlation}/{total} tasks have correlation_hint ({coverage:.1f}%)",
            )
