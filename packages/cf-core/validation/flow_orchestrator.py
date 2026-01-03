"""
Flow-Based Orchestrator

Flow-based orchestration system for agent swarm using workflow DAG execution.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.agents.audit_trail_validator import AuditTrailValidatorAgent
from cf_core.validation.agents.crud_validator import CRUDValidatorAgent
from cf_core.validation.agents.data_integrity_validator import DataIntegrityValidatorAgent
from cf_core.validation.agents.performance_validator import PerformanceValidatorAgent
from cf_core.validation.agents.relationship_validator import RelationshipValidatorAgent
from cf_core.validation.agents.state_transition_validator import StateTransitionValidatorAgent


class AgentStatus(Enum):
    """Agent execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


@dataclass
class AgentNode:
    """Represents an agent in the flow"""

    id: str
    name: str
    agent_class: type
    dependencies: list[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    start_time: float | None = None
    end_time: float | None = None

    @property
    def duration(self) -> float | None:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class FlowOrchestrator:
    """
    Flow-based orchestration for validation agent swarm.

    Implements a DAG (Directed Acyclic Graph) execution engine where agents
    are nodes and dependencies are edges. Supports parallel execution of
    independent agents and sequential execution of dependent agents.
    """

    def __init__(self, db_path: str, config: dict[str, Any] = None):
        """
        Initialize flow orchestrator

        Args:
            db_path: Path to SQLite database
            config: Configuration dictionary
        """
        self.db_path = db_path
        self.config = config or {}
        self.agents: dict[str, AgentNode] = {}
        self.flow_id = self._generate_flow_id()
        self._build_flow_graph()

    def _build_flow_graph(self):
        """Build the agent flow graph with dependencies"""
        # Phase 1: Data Integrity (must run first, no dependencies)
        self.agents["integrity"] = AgentNode(
            id="integrity",
            name="Data Integrity Validator",
            agent_class=DataIntegrityValidatorAgent,
            dependencies=[],  # No dependencies - runs first
        )

        # Phase 2: Core validators (depend on integrity passing)
        self.agents["crud"] = AgentNode(
            id="crud",
            name="CRUD Validator",
            agent_class=CRUDValidatorAgent,
            dependencies=["integrity"],
        )

        self.agents["state"] = AgentNode(
            id="state",
            name="State Transition Validator",
            agent_class=StateTransitionValidatorAgent,
            dependencies=["integrity"],
        )

        self.agents["relationship"] = AgentNode(
            id="relationship",
            name="Relationship Validator",
            agent_class=RelationshipValidatorAgent,
            dependencies=["integrity"],
        )

        self.agents["audit"] = AgentNode(
            id="audit",
            name="Audit Trail Validator",
            agent_class=AuditTrailValidatorAgent,
            dependencies=["integrity"],
        )

        # Phase 3: Performance (optional, depends on all core validators)
        if self.config.get("include_performance", False):
            self.agents["performance"] = AgentNode(
                id="performance",
                name="Performance Validator",
                agent_class=PerformanceValidatorAgent,
                dependencies=["crud", "state", "relationship", "audit"],
            )

    def execute_flow(self) -> Result[dict[str, Any]]:
        """
        Execute the validation flow

        Returns:
            Result containing flow execution report
        """
        flow_start = time.time()
        print(f"\n{'=' * 60}")
        print("Flow Orchestrator - Validation Swarm")
        print(f"Flow ID: {self.flow_id}")
        print(f"{'=' * 60}\n")

        try:
            # Execute flow using topological sort
            execution_order = self._topological_sort()

            print(f"Execution Order: {' → '.join(execution_order)}\n")

            # Execute agents in order
            for agent_id in execution_order:
                agent_node = self.agents[agent_id]

                # Check if dependencies are satisfied
                if not self._check_dependencies(agent_node):
                    agent_node.status = AgentStatus.BLOCKED
                    agent_node.error = "Dependencies failed - execution blocked"
                    print(f"⏸️  {agent_node.name}: BLOCKED (dependencies failed)")
                    continue

                # Execute agent
                self._execute_agent(agent_node)

                # Check for critical failures
                if agent_node.status == AgentStatus.FAILED:
                    if agent_node.id == "integrity":
                        # Integrity failure is critical - stop execution
                        print(f"\n❌ Critical failure in {agent_node.name} - aborting flow")
                        break

            # Generate flow report
            flow_end = time.time()
            flow_report = self._generate_flow_report(flow_start, flow_end)

            # Save flow report
            self._save_flow_report(flow_report)

            print(f"\n{'=' * 60}")
            print("Flow Execution Complete")
            print(f"Overall Status: {flow_report['overall_status']}")
            print(f"Duration: {flow_report['duration_seconds']:.2f}s")
            print(f"{'=' * 60}\n")

            return Result.success(flow_report)

        except Exception as e:
            return Result.failure(f"Flow execution failed: {e}")

    def _check_dependencies(self, agent_node: AgentNode) -> bool:
        """
        Check if all dependencies are satisfied

        Args:
            agent_node: Agent to check

        Returns:
            True if all dependencies completed successfully
        """
        for dep_id in agent_node.dependencies:
            dep_node = self.agents.get(dep_id)
            if not dep_node or dep_node.status != AgentStatus.COMPLETED:
                return False

            # Check if dependency has critical failures
            if dep_node.result and isinstance(dep_node.result, dict):
                if dep_node.result.get("summary", {}).get("status") == "FAILED":
                    return False

        return True

    def _execute_agent(self, agent_node: AgentNode):
        """
        Execute a single agent

        Args:
            agent_node: Agent to execute
        """
        print(f"▶️  {agent_node.name}: RUNNING...")

        agent_node.status = AgentStatus.RUNNING
        agent_node.start_time = time.time()

        try:
            # Instantiate and execute agent
            agent = agent_node.agent_class(self.db_path, self.config)
            result = agent.validate()

            agent_node.end_time = time.time()

            if result.is_success:
                agent_node.status = AgentStatus.COMPLETED
                agent_node.result = result.value

                # Extract summary status
                summary = result.value.get("summary", {})
                status_emoji = "✅" if summary.get("status") == "PASSED" else "⚠️"

                print(
                    f"{status_emoji}  {agent_node.name}: {summary.get('status', 'UNKNOWN')} "
                    f"({agent_node.duration:.2f}s)"
                )
            else:
                agent_node.status = AgentStatus.FAILED
                agent_node.error = str(result.error)
                print(f"❌  {agent_node.name}: FAILED - {result.error}")

        except Exception as e:
            agent_node.status = AgentStatus.FAILED
            agent_node.error = str(e)
            agent_node.end_time = time.time()
            print(f"❌  {agent_node.name}: ERROR - {e}")

    def _topological_sort(self) -> list[str]:
        """
        Perform topological sort of agent DAG

        Returns:
            List of agent IDs in execution order
        """
        # Build adjacency list
        in_degree = {agent_id: 0 for agent_id in self.agents}
        adj_list = {agent_id: [] for agent_id in self.agents}

        for agent_id, agent_node in self.agents.items():
            for dep_id in agent_node.dependencies:
                adj_list[dep_id].append(agent_id)
                in_degree[agent_id] += 1

        # Kahn's algorithm
        queue = [agent_id for agent_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort queue for deterministic execution
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.agents):
            raise ValueError("Cycle detected in agent dependency graph")

        return result

    def _generate_flow_report(self, start_time: float, end_time: float) -> dict[str, Any]:
        """
        Generate comprehensive flow report

        Args:
            start_time: Flow start timestamp
            end_time: Flow end timestamp

        Returns:
            Flow report dictionary
        """
        # Aggregate agent results
        agent_reports = {}
        total_checks = 0
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        critical_failures = 0

        for agent_id, agent_node in self.agents.items():
            if agent_node.result:
                agent_reports[agent_id] = agent_node.result

                # Aggregate metrics
                result = agent_node.result
                total_checks += result.get("total_tests", result.get("issues_found", 0))
                total_passed += result.get("passed", 0)
                total_failed += result.get("failed", 0)
                total_warnings += result.get("warnings", result.get("warning_count", 0))
                critical_failures += result.get(
                    "critical_failures", result.get("critical_count", 0)
                )

        success_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0

        # Determine overall status
        if critical_failures > 0:
            overall_status = "FAILED"
        elif total_failed == 0:
            overall_status = "PASSED"
        elif success_rate >= 90:
            overall_status = "PASSED_WITH_WARNINGS"
        elif success_rate >= 70:
            overall_status = "DEGRADED"
        else:
            overall_status = "FAILED"

        # Generate flow execution summary
        flow_summary = {
            "total_agents": len(self.agents),
            "completed": sum(1 for a in self.agents.values() if a.status == AgentStatus.COMPLETED),
            "failed": sum(1 for a in self.agents.values() if a.status == AgentStatus.FAILED),
            "blocked": sum(1 for a in self.agents.values() if a.status == AgentStatus.BLOCKED),
            "total_duration": end_time - start_time,
            "agent_durations": {
                agent_id: agent.duration
                for agent_id, agent in self.agents.items()
                if agent.duration is not None
            },
        }

        return {
            "flow_id": self.flow_id,
            "flow_type": "validation_swarm",
            "started_at": self._format_timestamp(start_time),
            "completed_at": self._format_timestamp(end_time),
            "duration_seconds": end_time - start_time,
            "configuration": self.config,
            "flow_summary": flow_summary,
            "agent_reports": agent_reports,
            "validation_summary": {
                "total_checks": total_checks,
                "passed": total_passed,
                "failed": total_failed,
                "warnings": total_warnings,
                "critical_failures": critical_failures,
                "success_rate": success_rate,
            },
            "overall_status": overall_status,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        for _agent_id, agent_node in self.agents.items():
            if agent_node.status == AgentStatus.FAILED:
                recommendations.append(f"[CRITICAL] {agent_node.name} failed: {agent_node.error}")
            elif agent_node.status == AgentStatus.BLOCKED:
                recommendations.append(
                    f"[BLOCKED] {agent_node.name} was blocked due to dependency failures"
                )
            elif agent_node.result:
                result = agent_node.result
                if result.get("critical_failures", result.get("critical_count", 0)) > 0:
                    recommendations.append(f"Address critical issues in {agent_node.name}")

        return recommendations[:10]

    def _save_flow_report(self, report: dict[str, Any]):
        """Save flow report to file"""
        output_dir = Path(self.db_path).parent.parent / "validation_reports"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"flow_{self.flow_id}.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nFlow report saved to: {output_file}")

    def visualize_flow(self) -> str:
        """
        Generate ASCII visualization of flow graph

        Returns:
            ASCII art representation of the flow
        """
        lines = ["", "Flow Dependency Graph:", ""]

        # Level 0: Integrity
        lines.append("  [Data Integrity]")
        lines.append("         |")
        lines.append("    ┌────┴────┬────────┬────────┐")
        lines.append("    |         |        |        |")

        # Level 1: Core validators
        lines.append("[CRUD]  [State] [Rel]  [Audit]")

        # Level 2: Performance (if enabled)
        if "performance" in self.agents:
            lines.append("    |         |        |        |")
            lines.append("    └─────────┴────────┴────────┘")
            lines.append("              |")
            lines.append("       [Performance]")

        lines.append("")
        return "\n".join(lines)

    def _generate_flow_id(self) -> str:
        """Generate unique flow ID"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        import uuid

        short_uuid = uuid.uuid4().hex[:8]
        return f"FLOW-{timestamp}-{short_uuid}"

    def _format_timestamp(self, ts: float) -> str:
        """Format timestamp as ISO8601"""
        return datetime.fromtimestamp(ts, tz=UTC).isoformat()


def main():
    """CLI entry point for flow orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="CF_CORE Flow-Based Validation Orchestrator")
    parser.add_argument("--db-path", default="db/trackers.sqlite", help="Database path")
    parser.add_argument(
        "--scope", default="full", choices=["full", "quick"], help="Validation scope"
    )
    parser.add_argument("--performance", action="store_true", help="Include performance tests")
    parser.add_argument("--visualize", action="store_true", help="Show flow graph")

    args = parser.parse_args()

    # Build configuration
    config = {"scope": args.scope, "include_performance": args.performance, "emit_evidence": True}

    # Create orchestrator
    orchestrator = FlowOrchestrator(args.db_path, config)

    # Show visualization if requested
    if args.visualize:
        print(orchestrator.visualize_flow())
        return

    # Execute flow
    result = orchestrator.execute_flow()

    if result.is_failure:
        print(f"\nFlow execution failed: {result.error}")
        exit(1)

    report = result.value

    # Display summary
    print("\nFlow Summary:")
    print(
        f"  Agents: {report['flow_summary']['completed']}/{report['flow_summary']['total_agents']} completed"
    )
    print(
        f"  Checks: {report['validation_summary']['passed']}/{report['validation_summary']['total_checks']} passed"
    )
    print(f"  Success Rate: {report['validation_summary']['success_rate']:.2f}%")

    if report["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

    exit(0 if report["overall_status"] in ["PASSED", "PASSED_WITH_WARNINGS"] else 1)


if __name__ == "__main__":
    main()
