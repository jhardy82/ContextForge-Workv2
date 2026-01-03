"""
Relationship Validator Agent

Validates task dependencies and relationship integrity.
"""

import json
from collections import defaultdict
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class RelationshipValidatorAgent(BaseValidationAgent):
    """Validates task relationships and dependencies"""

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all relationship validation tests"""
        try:
            issues = []

            # Build dependency graph
            graph = self._build_dependency_graph()

            # Run relationship checks
            issues.extend(self._detect_circular_dependencies(graph))
            issues.extend(self._check_bidirectional_consistency())
            issues.extend(self._check_dependency_states())
            issues.extend(self._check_orphaned_dependencies())

            # Record results
            for issue in issues:
                self._record_test_result(
                    test_name=issue["check"],
                    passed=False,
                    severity=issue["severity"],
                    details=issue["description"],
                )

            # Add passing status if no issues
            if not issues:
                self._record_test_result(
                    test_name="relationship_validation",
                    passed=True,
                    details="All relationship checks passed",
                )

            report = self._generate_report()
            report["issues"] = issues
            report["dependency_graph_size"] = len(graph)

            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"Relationship validation failed: {e}")

    def _build_dependency_graph(self) -> dict[str, list[str]]:
        """Build dependency graph from database"""
        graph = defaultdict(list)

        rows = self._execute_query("""
            SELECT id, depends_on
            FROM tasks
            WHERE depends_on IS NOT NULL
              AND depends_on != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                depends_on = json.loads(row["depends_on"])
                if isinstance(depends_on, list):
                    graph[row["id"]] = depends_on
            except (json.JSONDecodeError, TypeError):
                pass  # Invalid JSON handled by integrity validator

        return dict(graph)

    def _detect_circular_dependencies(self, graph: dict[str, list[str]]) -> list[dict[str, Any]]:
        """Detect cycles in dependency graph using DFS"""
        issues = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> list[list[str]]:
            """DFS to detect cycles"""
            cycles = []
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, path.copy()))
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)
            return cycles

        all_cycles = []
        for node in graph:
            if node not in visited:
                cycles = dfs(node, [])
                all_cycles.extend(cycles)

        for cycle in all_cycles:
            issues.append(
                {
                    "check": "circular_dependency",
                    "type": "cycle_detected",
                    "severity": "critical",
                    "cycle": " → ".join(cycle),
                    "cycle_length": len(cycle) - 1,
                    "description": f"Circular dependency detected: {' → '.join(cycle)}",
                }
            )

        return issues

    def _check_bidirectional_consistency(self) -> list[dict[str, Any]]:
        """Check that depends_on and blocks are bidirectional"""
        issues = []

        # Get all tasks with dependencies
        rows = self._execute_query("""
            SELECT id, title, depends_on, blocks
            FROM tasks
            WHERE (depends_on IS NOT NULL OR blocks IS NOT NULL)
              AND deleted_at IS NULL
        """)

        task_data = {}
        for row in rows:
            depends_on = []
            blocks = []

            try:
                if row["depends_on"]:
                    depends_on = json.loads(row["depends_on"])
            except json.JSONDecodeError:
                pass

            try:
                if row["blocks"]:
                    blocks = json.loads(row["blocks"])
            except json.JSONDecodeError:
                pass

            task_data[row["id"]] = {
                "title": row["title"],
                "depends_on": depends_on if isinstance(depends_on, list) else [],
                "blocks": blocks if isinstance(blocks, list) else [],
            }

        # Check bidirectional consistency
        for task_id, data in task_data.items():
            # For each dependency, check if blocker has reciprocal relationship
            for dep_id in data["depends_on"]:
                if dep_id in task_data:
                    if task_id not in task_data[dep_id]["blocks"]:
                        issues.append(
                            {
                                "check": "bidirectional_consistency",
                                "type": "missing_reciprocal",
                                "severity": "warning",
                                "task_id": task_id,
                                "task_title": data["title"],
                                "dependency_id": dep_id,
                                "description": f"Task {task_id} depends on {dep_id}, but {dep_id} does not list {task_id} in blocks",
                            }
                        )

        return issues

    def _check_dependency_states(self) -> list[dict[str, Any]]:
        """Check dependency state logic"""
        issues = []

        # Check for done tasks depending on non-done tasks
        rows = self._execute_query("""
            SELECT id, title, status, depends_on
            FROM tasks
            WHERE status = 'done'
              AND depends_on IS NOT NULL
              AND depends_on != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                depends_on = json.loads(row["depends_on"])
                if isinstance(depends_on, list):
                    for dep_id in depends_on:
                        dep_rows = self._execute_query(
                            "SELECT status FROM tasks WHERE id = ? AND deleted_at IS NULL",
                            (dep_id,),
                        )

                        if dep_rows and dep_rows[0]["status"] != "done":
                            issues.append(
                                {
                                    "check": "dependency_state_logic",
                                    "type": "done_before_dependency",
                                    "severity": "warning",
                                    "task_id": row["id"],
                                    "task_title": row["title"],
                                    "dependency_id": dep_id,
                                    "dependency_status": dep_rows[0]["status"],
                                    "description": f"Task {row['id']} is done but depends on incomplete task {dep_id} (status: {dep_rows[0]['status']})",
                                }
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        return issues

    def _check_orphaned_dependencies(self) -> list[dict[str, Any]]:
        """Check for dependencies referencing deleted tasks"""
        issues = []

        rows = self._execute_query("""
            SELECT id, title, depends_on
            FROM tasks
            WHERE depends_on IS NOT NULL
              AND depends_on != ''
              AND deleted_at IS NULL
        """)

        for row in rows:
            try:
                depends_on = json.loads(row["depends_on"])
                if isinstance(depends_on, list):
                    for dep_id in depends_on:
                        dep_rows = self._execute_query(
                            "SELECT id, deleted_at FROM tasks WHERE id = ?", (dep_id,)
                        )

                        if not dep_rows or dep_rows[0]["deleted_at"]:
                            issues.append(
                                {
                                    "check": "orphaned_dependency",
                                    "type": "dependency_deleted",
                                    "severity": "warning",
                                    "task_id": row["id"],
                                    "task_title": row["title"],
                                    "dependency_id": dep_id,
                                    "description": f"Task {row['id']} depends on deleted/non-existent task {dep_id}",
                                }
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        return issues
