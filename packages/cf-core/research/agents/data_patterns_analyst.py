"""
Data Patterns Analyst

Research agent that analyzes validation reports and database patterns
to understand foreign key violations and data integrity issues.

Uses MCP tools:
- database-mcp: Query validation reports and database
- DuckDB: Analytical queries for pattern analysis
- sequential-thinking: Complex multi-step pattern analysis
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class DataPatternsAnalyst(BaseResearchAgent):
    """Analyzes validation reports and database patterns"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.validation_report_path = config.get(
            "validation_report_path",
            "validation_reports/flow_FLOW-20251117-175714-501f5ec7.json"
        )
        self.db_path = config.get("db_path", "db/trackers.sqlite")

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute data patterns analysis

        Returns:
            Result containing analysis findings
        """
        # Load validation report
        report_result = self._load_validation_report()
        if report_result.is_failure:
            return report_result

        report = report_result.value

        # Analyze FK violations
        fk_analysis = self._analyze_fk_violations(report)

        # Record findings
        self._record_findings_from_analysis(fk_analysis)

        # Generate recommendations
        recommendations = self._generate_remediation_recommendations(fk_analysis)

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "validation_report_analyzed": self.validation_report_path,
                "fk_analysis": fk_analysis,
                "recommendations": recommendations,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "data-patterns-analysis"
        )

        return Result.success({
            "analysis": fk_analysis,
            "recommendations": recommendations,
            "findings_count": len(self.findings)
        })

    def _load_validation_report(self) -> Result[Dict[str, Any]]:
        """Load and parse validation report"""
        try:
            report_path = Path(self.validation_report_path)
            if not report_path.exists():
                return Result.failure(f"Validation report not found: {self.validation_report_path}")

            with open(report_path, "r") as f:
                report = json.load(f)

            self._record_finding(
                category="data_loading",
                finding=f"Successfully loaded validation report: {report_path.name}",
                severity="info",
                metadata={
                    "flow_id": report.get("flow_id"),
                    "total_issues": report.get("validation_summary", {}).get("total_checks", 0)
                }
            )

            return Result.success(report)

        except Exception as e:
            return Result.failure(f"Failed to load validation report: {str(e)}")

    def _analyze_fk_violations(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze foreign key violations from report

        Args:
            report: Validation report dictionary

        Returns:
            Analysis results with patterns and statistics
        """
        # Extract test results from recommendations
        test_results = self._extract_test_results(report)

        # Group violations by type
        project_violations = defaultdict(list)
        sprint_violations = defaultdict(list)

        for test in test_results:
            if test.get("test") == "foreign_key_project":
                details = test.get("details", "")
                # Parse: "Task T-XXX references non-existent project P-YYY"
                parts = details.split(" references non-existent project ")
                if len(parts) == 2:
                    task_id = parts[0].replace("Task ", "")
                    project_id = parts[1]
                    project_violations[project_id].append({
                        "task_id": task_id,
                        "severity": test.get("severity"),
                        "timestamp": test.get("timestamp")
                    })

            elif test.get("test") == "foreign_key_sprint":
                details = test.get("details", "")
                # Parse: "Task T-XXX references non-existent sprint S-YYY"
                parts = details.split(" references non-existent sprint ")
                if len(parts) == 2:
                    task_id = parts[0].replace("Task ", "")
                    sprint_id = parts[1]
                    sprint_violations[sprint_id].append({
                        "task_id": task_id,
                        "severity": test.get("severity"),
                        "timestamp": test.get("timestamp")
                    })

        # Sort by impact (number of affected tasks)
        sorted_projects = sorted(
            project_violations.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        sorted_sprints = sorted(
            sprint_violations.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        # Calculate statistics
        analysis = {
            "total_fk_violations": len(test_results),
            "project_violations": {
                "total": len(project_violations),
                "total_tasks_affected": sum(len(tasks) for tasks in project_violations.values()),
                "by_project": dict(sorted_projects),
                "top_impacted": [
                    {
                        "project_id": proj_id,
                        "affected_tasks": len(tasks),
                        "sample_tasks": [t["task_id"] for t in tasks[:5]]
                    }
                    for proj_id, tasks in sorted_projects[:10]
                ]
            },
            "sprint_violations": {
                "total": len(sprint_violations),
                "total_tasks_affected": sum(len(tasks) for tasks in sprint_violations.values()),
                "by_sprint": dict(sorted_sprints),
                "top_impacted": [
                    {
                        "sprint_id": sprint_id,
                        "affected_tasks": len(tasks),
                        "sample_tasks": [t["task_id"] for t in tasks[:5]]
                    }
                    for sprint_id, tasks in sorted_sprints[:10]
                ]
            },
            "patterns": self._identify_patterns(project_violations, sprint_violations)
        }

        return analysis

    def _extract_test_results(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test results from report"""
        test_results = []

        # Check in recommendations (where actual test results are in this report)
        recommendations = report.get("recommendations", [])
        for rec in recommendations:
            if isinstance(rec, str) and "DataIntegrityValidator failed" in rec:
                # Parse embedded test results from recommendation string
                # This is a bit hacky but necessary based on report structure
                try:
                    # Extract the dictionary part after "failed: "
                    dict_str = rec.split("failed: ", 1)[1]
                    data = eval(dict_str)  # Note: In production, use safer parsing
                    if "test_results" in data:
                        test_results = data["test_results"]
                        break
                except:
                    pass

        return test_results

    def _identify_patterns(
        self,
        project_violations: Dict[str, List],
        sprint_violations: Dict[str, List]
    ) -> Dict[str, Any]:
        """Identify patterns in violations"""
        patterns = {
            "common_project_prefixes": self._analyze_project_prefixes(project_violations),
            "temporal_sprint_patterns": self._analyze_sprint_temporal_patterns(sprint_violations),
            "severity_distribution": "All violations are critical (foreign key constraints)",
            "root_causes": [
                "Projects deleted without cascade to tasks",
                "Sprints completed and archived without updating task references",
                "Historical data cleanup removed parent entities",
                "Data migration issues from previous system"
            ]
        }

        return patterns

    def _analyze_project_prefixes(self, violations: Dict[str, List]) -> Dict[str, int]:
        """Analyze project ID prefixes for patterns"""
        prefixes = defaultdict(int)
        for project_id in violations.keys():
            # Extract prefix (e.g., "P-UNIFIED" from "P-UNIFIED-LOG")
            parts = project_id.split("-")
            if len(parts) >= 2:
                prefix = "-".join(parts[:2])
                prefixes[prefix] += len(violations[project_id])

        return dict(sorted(prefixes.items(), key=lambda x: x[1], reverse=True))

    def _analyze_sprint_temporal_patterns(self, violations: Dict[str, List]) -> Dict[str, Any]:
        """Analyze temporal patterns in sprint violations"""
        # Extract dates from sprint IDs (e.g., "S-2025-08-25-...")
        by_month = defaultdict(int)
        for sprint_id in violations.keys():
            parts = sprint_id.split("-")
            if len(parts) >= 3 and parts[0] == "S":
                try:
                    year_month = f"{parts[1]}-{parts[2]}"
                    by_month[year_month] += len(violations[sprint_id])
                except:
                    pass

        return {
            "by_month": dict(sorted(by_month.items())),
            "peak_month": max(by_month.items(), key=lambda x: x[1])[0] if by_month else None,
            "span": f"{min(by_month.keys())} to {max(by_month.keys())}" if by_month else "Unknown"
        }

    def _record_findings_from_analysis(self, analysis: Dict[str, Any]):
        """Record findings from analysis"""
        # Record project violation findings
        self._record_finding(
            category="foreign_key_violations",
            finding=f"Found {analysis['project_violations']['total']} missing projects affecting {analysis['project_violations']['total_tasks_affected']} tasks",
            severity="critical",
            metadata={"top_impacted": analysis['project_violations']['top_impacted'][:5]}
        )

        # Record sprint violation findings
        self._record_finding(
            category="foreign_key_violations",
            finding=f"Found {analysis['sprint_violations']['total']} missing sprints affecting {analysis['sprint_violations']['total_tasks_affected']} tasks",
            severity="critical",
            metadata={"top_impacted": analysis['sprint_violations']['top_impacted'][:5]}
        )

        # Record patterns
        for root_cause in analysis['patterns']['root_causes']:
            self._record_finding(
                category="root_cause_analysis",
                finding=root_cause,
                severity="warning",
                metadata={}
            )

        # Record top impacted projects
        for project_info in analysis['project_violations']['top_impacted'][:5]:
            self._record_finding(
                category="high_impact_projects",
                finding=f"Project {project_info['project_id']} has {project_info['affected_tasks']} orphaned tasks",
                severity="critical",
                metadata=project_info
            )

    def _generate_remediation_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate remediation recommendations"""
        recommendations = []

        # Recommendation 1: Restore high-impact projects
        top_projects = analysis['project_violations']['top_impacted'][:10]
        if top_projects:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "restore_projects",
                "title": "Restore Top 10 Missing Projects",
                "description": "Restore projects with most orphaned tasks",
                "affected_projects": [p["project_id"] for p in top_projects],
                "total_tasks_fixed": sum(p["affected_tasks"] for p in top_projects),
                "estimated_effort": "4 hours",
                "implementation": "Use scripts/restore_missing_projects.py"
            })

        # Recommendation 2: Restore or cleanup sprints
        top_sprints = analysis['sprint_violations']['top_impacted'][:10]
        if top_sprints:
            recommendations.append({
                "priority": "HIGH",
                "action": "restore_or_cleanup_sprints",
                "title": "Handle Top 10 Missing Sprints",
                "description": "Either restore active sprints or cleanup historical sprint references",
                "affected_sprints": [s["sprint_id"] for s in top_sprints],
                "total_tasks_affected": sum(s["affected_tasks"] for s in top_sprints),
                "estimated_effort": "3 hours",
                "implementation": "Review sprint dates and decide restore vs. cleanup"
            })

        # Recommendation 3: Preventive measures
        recommendations.append({
            "priority": "MEDIUM",
            "action": "preventive_measures",
            "title": "Implement Cascade Delete or Validation",
            "description": "Add database triggers or application-level validation to prevent future orphaned tasks",
            "implementation": [
                "Add ON DELETE SET NULL to project_id/sprint_id columns",
                "Or implement soft delete workflow for projects/sprints",
                "Add validation in dbcli to prevent deletion of projects with active tasks"
            ],
            "estimated_effort": "6 hours"
        })

        return recommendations

    def _group_findings_by_category(self) -> Dict[str, List]:
        """Group findings by category"""
        by_category = defaultdict(list)
        for finding in self.findings:
            by_category[finding["category"]].append(finding)
        return dict(by_category)

    def _count_by_severity(self) -> Dict[str, int]:
        """Count findings by severity"""
        counts = {"info": 0, "warning": 0, "critical": 0}
        for finding in self.findings:
            severity = finding.get("severity", "info")
            counts[severity] = counts.get(severity, 0) + 1
        return counts
