"""
Validation Orchestrator

Coordinates execution of validation agent swarm and aggregates results.
"""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.agents.audit_trail_validator import AuditTrailValidatorAgent
from cf_core.validation.agents.crud_validator import CRUDValidatorAgent
from cf_core.validation.agents.data_integrity_validator import DataIntegrityValidatorAgent
from cf_core.validation.agents.performance_validator import PerformanceValidatorAgent
from cf_core.validation.agents.relationship_validator import RelationshipValidatorAgent
from cf_core.validation.agents.state_transition_validator import StateTransitionValidatorAgent


class ValidationOrchestrator:
    """Orchestrates validation swarm execution"""

    def __init__(self, db_path: str, config: dict[str, Any] = None):
        """
        Initialize orchestrator

        Args:
            db_path: Path to SQLite database
            config: Configuration dictionary with options:
                - scope: Validation scope (full, quick, sprint, project)
                - parallel: Run agents in parallel (default: True)
                - include_performance: Include performance tests (default: False)
                - emit_evidence: Emit evidence for audit (default: True)
                - filters: Dict of filters (sprint_id, project_id, etc.)
        """
        self.db_path = db_path
        self.config = config or {}
        self.results = {}
        self.validation_id = self._generate_validation_id()

    def execute_swarm(self) -> Result[dict[str, Any]]:
        """
        Execute validation swarm

        Returns:
            Result containing comprehensive validation report
        """
        started_at = self._utc_now()

        try:
            # Phase 1: Data Integrity (must pass before continuing)
            print("Phase 1: Data Integrity Check...")
            integrity_agent = DataIntegrityValidatorAgent(self.db_path, self.config)
            integrity_result = integrity_agent.validate()

            if integrity_result.is_failure:
                return Result.failure(
                    {
                        "message": "Data integrity check failed - aborting validation",
                        "validation_id": self.validation_id,
                        "integrity_report": integrity_result.error,
                    }
                )

            self.results["integrity"] = integrity_result.value
            print(f"✓ Integrity: {integrity_result.value['summary']['status']}")

            # Phase 2: Core Validators
            print("\nPhase 2: Core Validation...")

            if self.config.get("parallel", True):
                self._execute_parallel_validation()
            else:
                self._execute_sequential_validation()

            # Phase 3: Performance (optional)
            if self.config.get("include_performance", False):
                print("\nPhase 3: Performance Benchmarks...")
                perf_agent = PerformanceValidatorAgent(self.db_path, self.config)
                perf_result = perf_agent.validate()
                self.results["performance"] = (
                    perf_result.value if perf_result.is_success else perf_result.error
                )
                status = (
                    perf_result.value.get("summary", {}).get("status", "UNKNOWN")
                    if perf_result.is_success
                    else "FAILED"
                )
                print(f"✓ Performance: {status}")

            # Phase 4: Aggregate and summarize
            completed_at = self._utc_now()
            final_report = self._generate_final_report(started_at, completed_at)

            # Save report
            self._save_report(final_report)

            print(f"\n{'=' * 60}")
            print(f"Validation Complete: {final_report['overall_status']}")
            print(f"Success Rate: {final_report['summary']['success_rate']:.2f}%")
            print(f"{'=' * 60}")

            return Result.success(final_report)

        except Exception as e:
            return Result.failure(f"Orchestration failed: {e}")

    def _execute_parallel_validation(self):
        """Execute core validators in parallel"""
        agents = {
            "crud": CRUDValidatorAgent(self.db_path, self.config),
            "state": StateTransitionValidatorAgent(self.db_path, self.config),
            "relationship": RelationshipValidatorAgent(self.db_path, self.config),
            "audit": AuditTrailValidatorAgent(self.db_path, self.config),
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(agent.validate): name for name, agent in agents.items()}

            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    result = future.result()
                    self.results[agent_name] = result.value if result.is_success else result.error
                    status = (
                        result.value.get("summary", {}).get("status", "UNKNOWN")
                        if result.is_success
                        else "FAILED"
                    )
                    print(f"✓ {agent_name.capitalize()}: {status}")
                except Exception as e:
                    self.results[agent_name] = {"error": str(e)}
                    print(f"✗ {agent_name.capitalize()}: ERROR - {e}")

    def _execute_sequential_validation(self):
        """Execute core validators sequentially"""
        validators = [
            ("crud", CRUDValidatorAgent),
            ("state", StateTransitionValidatorAgent),
            ("relationship", RelationshipValidatorAgent),
            ("audit", AuditTrailValidatorAgent),
        ]

        for name, AgentClass in validators:
            agent = AgentClass(self.db_path, self.config)
            result = agent.validate()
            self.results[name] = result.value if result.is_success else result.error
            status = (
                result.value.get("summary", {}).get("status", "UNKNOWN")
                if result.is_success
                else "FAILED"
            )
            print(f"✓ {name.capitalize()}: {status}")

    def _generate_final_report(self, started_at: str, completed_at: str) -> dict[str, Any]:
        """Generate comprehensive final report"""
        summary = self._calculate_summary()

        return {
            "validation_id": self.validation_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": self._calculate_duration(started_at, completed_at),
            "scope": self.config.get("scope", "full"),
            "configuration": {
                "parallel": self.config.get("parallel", True),
                "include_performance": self.config.get("include_performance", False),
                "filters": self.config.get("filters", {}),
            },
            "agents_executed": len(self.results),
            "agent_reports": self.results,
            "summary": summary,
            "recommendations": self._generate_recommendations(),
            "overall_status": self._determine_overall_status(summary),
        }

    def _calculate_summary(self) -> dict[str, Any]:
        """Calculate aggregate summary from all agent reports"""
        total_checks = 0
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        critical_failures = 0

        for _agent_name, report in self.results.items():
            if isinstance(report, dict):
                total_checks += report.get("total_tests", report.get("issues_found", 0))
                total_passed += report.get("passed", 0)
                total_failed += report.get("failed", 0)
                total_warnings += report.get("warnings", report.get("warning_count", 0))
                critical_failures += report.get(
                    "critical_failures", report.get("critical_count", 0)
                )

        success_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0

        return {
            "total_checks": total_checks,
            "passed": total_passed,
            "failed": total_failed,
            "warnings": total_warnings,
            "critical_failures": critical_failures,
            "success_rate": success_rate,
        }

    def _determine_overall_status(self, summary: dict[str, Any]) -> str:
        """Determine overall validation status"""
        if summary["critical_failures"] > 0:
            return "FAILED"
        elif summary["failed"] == 0:
            return "PASSED"
        elif summary["success_rate"] >= 90:
            return "PASSED_WITH_WARNINGS"
        elif summary["success_rate"] >= 70:
            return "DEGRADED"
        else:
            return "FAILED"

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        for agent_name, report in self.results.items():
            if isinstance(report, dict):
                failed = report.get("failed", 0)
                critical = report.get("critical_failures", report.get("critical_count", 0))
                issues = report.get("issues", [])

                if critical > 0:
                    recommendations.append(
                        f"[CRITICAL] Address {critical} critical issues in {agent_name} validator"
                    )

                if failed > 0:
                    recommendations.append(f"Fix {failed} failed checks in {agent_name} validator")

                if issues:
                    # Group issues by type
                    issue_types = {}
                    for issue in issues:
                        issue_type = issue.get("type", "unknown")
                        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

                    for issue_type, count in issue_types.items():
                        if count > 5:  # Only recommend if significant
                            recommendations.append(
                                f"Investigate {count} '{issue_type}' issues in {agent_name}"
                            )

        # Add general recommendations
        summary = self._calculate_summary()
        if summary["success_rate"] < 80:
            recommendations.append(
                f"Overall success rate is {summary['success_rate']:.1f}% - comprehensive review recommended"
            )

        return recommendations[:10]  # Limit to top 10 recommendations

    def _save_report(self, report: dict[str, Any]):
        """Save validation report to file"""
        output_dir = Path(self.db_path).parent.parent / "validation_reports"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"validation_{self.validation_id}.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {output_file}")

    def _generate_validation_id(self) -> str:
        """Generate unique validation ID"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"VAL-{timestamp}-{short_uuid}"

    def _utc_now(self) -> str:
        """Get current UTC timestamp"""
        return datetime.now(UTC).isoformat()

    def _calculate_duration(self, started_at: str, completed_at: str) -> float:
        """Calculate duration in seconds"""
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        return (end - start).total_seconds()


def main():
    """CLI entry point for orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="CF_CORE Task Workflow Validation Swarm")
    parser.add_argument("--db-path", default="db/trackers.sqlite", help="Database path")
    parser.add_argument(
        "--scope",
        default="full",
        choices=["full", "quick", "sprint", "project"],
        help="Validation scope",
    )
    parser.add_argument(
        "--parallel", action="store_true", default=True, help="Run agents in parallel"
    )
    parser.add_argument(
        "--no-parallel", action="store_false", dest="parallel", help="Run agents sequentially"
    )
    parser.add_argument("--performance", action="store_true", help="Include performance tests")
    parser.add_argument("--sprint-id", help="Filter by sprint ID")
    parser.add_argument("--project-id", help="Filter by project ID")

    args = parser.parse_args()

    # Build configuration
    config = {
        "scope": args.scope,
        "parallel": args.parallel,
        "include_performance": args.performance,
        "emit_evidence": True,
        "filters": {},
    }

    if args.sprint_id:
        config["filters"]["sprint_id"] = args.sprint_id
    if args.project_id:
        config["filters"]["project_id"] = args.project_id

    # Execute validation
    orchestrator = ValidationOrchestrator(args.db_path, config)
    result = orchestrator.execute_swarm()

    if result.is_failure:
        print(f"\nValidation Failed: {result.error}")
        exit(1)

    report = result.value

    # Display summary
    print(f"\nValidation ID: {report['validation_id']}")
    print(f"Duration: {report['duration_seconds']:.2f}s")
    print(f"\nAgents Executed: {report['agents_executed']}")
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Warnings: {report['summary']['warnings']}")
    print(f"Critical: {report['summary']['critical_failures']}")

    if report["recommendations"]:
        print(f"\nRecommendations ({len(report['recommendations'])}):")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

    exit(0 if report["overall_status"] in ["PASSED", "PASSED_WITH_WARNINGS"] else 1)


if __name__ == "__main__":
    main()
