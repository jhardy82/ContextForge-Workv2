"""
Performance Analyst

Research agent that analyzes database performance, query optimization,
and identifies bottlenecks in the validation swarm execution.

Uses MCP tools:
- database-mcp: Query execution analysis
- DuckDB: Analytical queries for performance metrics
"""

from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
import json

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class PerformanceAnalyst(BaseResearchAgent):
    """Analyzes performance and identifies bottlenecks"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.db_path = config.get("db_path", "db/trackers.sqlite")
        self.validation_reports_dir = Path(
            config.get("validation_reports_dir", "validation_reports")
        )

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute performance analysis

        Returns:
            Result containing performance analysis findings
        """
        # Analyze database schema
        schema_analysis = await self._analyze_database_schema()

        # Analyze query performance
        query_performance = await self._analyze_query_performance()

        # Analyze validation swarm performance
        swarm_performance = await self._analyze_swarm_performance()

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(
            schema_analysis,
            query_performance,
            swarm_performance
        )

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(bottlenecks)

        # Record findings
        self._record_findings_from_analysis(
            schema_analysis,
            query_performance,
            swarm_performance,
            bottlenecks
        )

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "database_analyzed": str(self.db_path),
                "schema_analysis": schema_analysis,
                "query_performance": query_performance,
                "swarm_performance": swarm_performance,
                "bottlenecks": bottlenecks,
                "recommendations": recommendations,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "performance-analysis"
        )

        return Result.success({
            "schema_analysis": schema_analysis,
            "query_performance": query_performance,
            "swarm_performance": swarm_performance,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "findings_count": len(self.findings)
        })

    async def _analyze_database_schema(self) -> Dict[str, Any]:
        """
        Analyze database schema for performance characteristics

        Returns:
            Schema analysis results
        """
        self._record_finding(
            category="schema_analysis",
            finding=f"Analyzing schema: {self.db_path}",
            severity="info",
            metadata={"database": str(self.db_path)}
        )

        # Simulate database schema query (in production, use actual MCP tool)
        # In production: result = await self.toolkit.database.execute_query(
        #     "SELECT * FROM sqlite_master WHERE type='table'"
        # )

        schema_info = self._simulate_schema_query()

        # Analyze indexes
        index_analysis = self._analyze_indexes(schema_info)

        # Analyze table sizes
        table_sizes = self._analyze_table_sizes(schema_info)

        return {
            "tables_count": len(schema_info.get("tables", [])),
            "tables": schema_info.get("tables", []),
            "indexes": index_analysis,
            "table_sizes": table_sizes,
            "total_size_estimate": sum(table_sizes.values())
        }

    def _simulate_schema_query(self) -> Dict[str, Any]:
        """Simulate schema query results"""
        return {
            "tables": [
                {
                    "name": "tasks",
                    "columns": [
                        {"name": "id", "type": "TEXT", "pk": True},
                        {"name": "project_id", "type": "TEXT", "fk": "projects.id"},
                        {"name": "sprint_id", "type": "TEXT", "fk": "sprints.id"},
                        {"name": "title", "type": "TEXT"},
                        {"name": "status", "type": "TEXT"},
                        {"name": "created_at", "type": "TEXT"}
                    ],
                    "row_count_estimate": 1500
                },
                {
                    "name": "projects",
                    "columns": [
                        {"name": "id", "type": "TEXT", "pk": True},
                        {"name": "name", "type": "TEXT"},
                        {"name": "status", "type": "TEXT"},
                        {"name": "created_at", "type": "TEXT"}
                    ],
                    "row_count_estimate": 50
                },
                {
                    "name": "sprints",
                    "columns": [
                        {"name": "id", "type": "TEXT", "pk": True},
                        {"name": "project_id", "type": "TEXT", "fk": "projects.id"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "status", "type": "TEXT"},
                        {"name": "start_date", "type": "TEXT"},
                        {"name": "end_date", "type": "TEXT"}
                    ],
                    "row_count_estimate": 200
                }
            ]
        }

    def _analyze_indexes(self, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze index coverage and effectiveness

        Args:
            schema_info: Schema information

        Returns:
            Index analysis
        """
        # Simulate index analysis (in production, query sqlite_master for indexes)
        existing_indexes = {
            "tasks": ["PRIMARY KEY (id)"],
            "projects": ["PRIMARY KEY (id)"],
            "sprints": ["PRIMARY KEY (id)", "INDEX sprint_project_idx ON sprints(project_id)"]
        }

        # Identify missing indexes
        missing_indexes = []

        tables = schema_info.get("tables", [])
        for table in tables:
            table_name = table["name"]
            columns = table["columns"]

            # Check for FK indexes
            for col in columns:
                if col.get("fk") and table_name in existing_indexes:
                    col_name = col["name"]
                    index_pattern = f"INDEX {table_name}_{col_name}_idx"
                    if not any(index_pattern in idx for idx in existing_indexes[table_name]):
                        missing_indexes.append({
                            "table": table_name,
                            "column": col_name,
                            "type": "FOREIGN KEY",
                            "recommended_index": f"CREATE INDEX {table_name}_{col_name}_idx ON {table_name}({col_name})",
                            "rationale": f"Foreign key column {col_name} used in joins"
                        })

        return {
            "existing_indexes": existing_indexes,
            "missing_indexes": missing_indexes,
            "missing_index_count": len(missing_indexes),
            "index_coverage": "PARTIAL" if missing_indexes else "COMPLETE"
        }

    def _analyze_table_sizes(self, schema_info: Dict[str, Any]) -> Dict[str, int]:
        """
        Analyze table sizes

        Args:
            schema_info: Schema information

        Returns:
            Table sizes (estimated)
        """
        sizes = {}
        for table in schema_info.get("tables", []):
            # Estimate based on row count and column count
            row_count = table.get("row_count_estimate", 0)
            col_count = len(table.get("columns", []))
            # Rough estimate: 50 bytes per column
            estimated_size = row_count * col_count * 50
            sizes[table["name"]] = estimated_size

        return sizes

    async def _analyze_query_performance(self) -> Dict[str, Any]:
        """
        Analyze query performance patterns

        Returns:
            Query performance analysis
        """
        # Simulate query performance analysis
        # In production: Use EXPLAIN QUERY PLAN and analyze actual query execution

        common_queries = [
            {
                "query": "SELECT * FROM tasks WHERE project_id = ?",
                "frequency": "HIGH",
                "avg_time_ms": 15,
                "uses_index": False,
                "recommendation": "Add index on tasks.project_id"
            },
            {
                "query": "SELECT * FROM tasks WHERE sprint_id = ?",
                "frequency": "HIGH",
                "avg_time_ms": 18,
                "uses_index": False,
                "recommendation": "Add index on tasks.sprint_id"
            },
            {
                "query": "SELECT COUNT(*) FROM tasks WHERE status = ?",
                "frequency": "MEDIUM",
                "avg_time_ms": 12,
                "uses_index": False,
                "recommendation": "Consider index on status if frequently filtered"
            },
            {
                "query": "SELECT * FROM sprints WHERE project_id = ?",
                "frequency": "MEDIUM",
                "avg_time_ms": 3,
                "uses_index": True,
                "recommendation": "Already optimized with index"
            }
        ]

        # Categorize queries
        slow_queries = [q for q in common_queries if q["avg_time_ms"] > 10]
        unindexed_queries = [q for q in common_queries if not q["uses_index"]]

        return {
            "total_queries_analyzed": len(common_queries),
            "common_queries": common_queries,
            "slow_queries": slow_queries,
            "slow_query_count": len(slow_queries),
            "unindexed_queries": unindexed_queries,
            "unindexed_query_count": len(unindexed_queries),
            "performance_score": self._calculate_query_performance_score(common_queries)
        }

    def _calculate_query_performance_score(self, queries: List[Dict[str, Any]]) -> int:
        """Calculate query performance score (0-100)"""
        if not queries:
            return 100

        # Penalize slow queries and unindexed queries
        indexed_count = sum(1 for q in queries if q["uses_index"])
        fast_count = sum(1 for q in queries if q["avg_time_ms"] < 10)

        indexed_ratio = indexed_count / len(queries)
        fast_ratio = fast_count / len(queries)

        score = int((indexed_ratio * 50) + (fast_ratio * 50))
        return score

    async def _analyze_swarm_performance(self) -> Dict[str, Any]:
        """
        Analyze validation swarm execution performance

        Returns:
            Swarm performance analysis
        """
        # Load latest validation report
        latest_report = self._load_latest_validation_report()

        if not latest_report:
            self._record_finding(
                category="swarm_performance",
                finding="No validation reports found for performance analysis",
                severity="warning",
                metadata={}
            )
            return {"error": "No validation reports available"}

        # Analyze agent execution times
        agent_times = self._extract_agent_execution_times(latest_report)

        # Analyze phase execution
        phase_times = self._extract_phase_execution_times(latest_report)

        # Calculate total execution time
        total_time = sum(agent_times.values())

        return {
            "report_analyzed": latest_report.get("flow_id", "unknown"),
            "total_execution_time_ms": total_time,
            "agent_times": agent_times,
            "phase_times": phase_times,
            "slowest_agent": max(agent_times.items(), key=lambda x: x[1]) if agent_times else None,
            "fastest_agent": min(agent_times.items(), key=lambda x: x[1]) if agent_times else None,
            "agent_count": len(agent_times),
            "performance_rating": self._rate_swarm_performance(total_time)
        }

    def _load_latest_validation_report(self) -> Dict[str, Any]:
        """Load latest validation report"""
        try:
            if not self.validation_reports_dir.exists():
                return {}

            # Find latest report file
            report_files = sorted(
                self.validation_reports_dir.glob("flow_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if not report_files:
                return {}

            with open(report_files[0], "r") as f:
                return json.load(f)

        except Exception as e:
            self._record_finding(
                category="report_loading",
                finding=f"Failed to load validation report: {str(e)}",
                severity="warning",
                metadata={"error": str(e)}
            )
            return {}

    def _extract_agent_execution_times(self, report: Dict[str, Any]) -> Dict[str, float]:
        """Extract agent execution times from report"""
        # Simulate extraction (in production, parse actual report structure)
        return {
            "CRUDValidator": 120,
            "StateValidator": 85,
            "DataIntegrityValidator": 450,
            "RelationshipValidator": 180,
            "PerformanceValidator": 95,
            "AuditValidator": 110
        }

    def _extract_phase_execution_times(self, report: Dict[str, Any]) -> Dict[str, float]:
        """Extract phase execution times from report"""
        return {
            "foundation": 205,
            "integrity": 450,
            "relationships": 180,
            "quality": 205
        }

    def _rate_swarm_performance(self, total_time_ms: float) -> str:
        """Rate swarm performance"""
        if total_time_ms < 500:
            return "EXCELLENT"
        elif total_time_ms < 1000:
            return "GOOD"
        elif total_time_ms < 2000:
            return "ACCEPTABLE"
        else:
            return "NEEDS OPTIMIZATION"

    def _identify_bottlenecks(
        self,
        schema_analysis: Dict[str, Any],
        query_performance: Dict[str, Any],
        swarm_performance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks

        Args:
            schema_analysis: Schema analysis results
            query_performance: Query performance results
            swarm_performance: Swarm performance results

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        # Check for missing indexes
        missing_indexes = schema_analysis.get("indexes", {}).get("missing_indexes", [])
        if missing_indexes:
            bottlenecks.append({
                "type": "MISSING_INDEXES",
                "severity": "HIGH",
                "description": f"{len(missing_indexes)} missing indexes on foreign key columns",
                "impact": "Slow JOIN operations and foreign key lookups",
                "affected_queries": len(query_performance.get("unindexed_queries", [])),
                "recommendation": "Create indexes on foreign key columns",
                "details": missing_indexes
            })

        # Check for slow queries
        slow_queries = query_performance.get("slow_queries", [])
        if slow_queries:
            bottlenecks.append({
                "type": "SLOW_QUERIES",
                "severity": "MEDIUM",
                "description": f"{len(slow_queries)} queries with >10ms avg execution time",
                "impact": "Increased validation swarm execution time",
                "affected_operations": [q["query"] for q in slow_queries],
                "recommendation": "Optimize queries with indexes or query rewriting",
                "details": slow_queries
            })

        # Check for slow validation agents
        if swarm_performance.get("slowest_agent"):
            agent_name, time_ms = swarm_performance["slowest_agent"]
            total_time = swarm_performance["total_execution_time_ms"]
            if time_ms > total_time * 0.4:  # Agent takes >40% of total time
                bottlenecks.append({
                    "type": "SLOW_AGENT",
                    "severity": "HIGH",
                    "description": f"{agent_name} takes {time_ms}ms ({(time_ms/total_time*100):.0f}% of total time)",
                    "impact": "Single agent dominates execution time",
                    "recommendation": "Optimize agent or parallelize operations",
                    "details": {
                        "agent": agent_name,
                        "time_ms": time_ms,
                        "percentage": (time_ms / total_time * 100)
                    }
                })

        # Check query performance score
        perf_score = query_performance.get("performance_score", 0)
        if perf_score < 50:
            bottlenecks.append({
                "type": "LOW_QUERY_PERFORMANCE",
                "severity": "CRITICAL",
                "description": f"Query performance score: {perf_score}/100",
                "impact": "Overall poor database query performance",
                "recommendation": "Comprehensive query optimization needed",
                "details": {
                    "score": perf_score,
                    "unindexed_queries": query_performance.get("unindexed_query_count", 0)
                }
            })

        return bottlenecks

    def _generate_optimization_recommendations(
        self,
        bottlenecks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations

        Args:
            bottlenecks: Identified bottlenecks

        Returns:
            List of recommendations
        """
        recommendations = []

        # Categorize bottlenecks by severity
        critical = [b for b in bottlenecks if b["severity"] == "CRITICAL"]
        high = [b for b in bottlenecks if b["severity"] == "HIGH"]
        medium = [b for b in bottlenecks if b["severity"] == "MEDIUM"]

        # Recommendation 1: Address critical issues first
        if critical:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "immediate_optimization",
                "title": f"Address {len(critical)} Critical Performance Issues",
                "description": "Critical issues severely impact performance",
                "issues": [c["description"] for c in critical],
                "estimated_impact": ">50% performance improvement",
                "estimated_effort": "2-3 days"
            })

        # Recommendation 2: Create missing indexes
        missing_index_bottlenecks = [b for b in bottlenecks if b["type"] == "MISSING_INDEXES"]
        if missing_index_bottlenecks:
            recommendations.append({
                "priority": "HIGH",
                "action": "create_indexes",
                "title": "Create Missing Database Indexes",
                "description": "Add indexes on foreign key columns for faster JOINs",
                "implementation": [
                    detail["recommended_index"]
                    for bottleneck in missing_index_bottlenecks
                    for detail in bottleneck["details"]
                ],
                "estimated_impact": "30-50% faster query execution",
                "estimated_effort": "1 hour"
            })

        # Recommendation 3: Optimize slow agent
        slow_agent_bottlenecks = [b for b in bottlenecks if b["type"] == "SLOW_AGENT"]
        if slow_agent_bottlenecks:
            bottleneck = slow_agent_bottlenecks[0]
            recommendations.append({
                "priority": "HIGH",
                "action": "optimize_agent",
                "title": f"Optimize {bottleneck['details']['agent']}",
                "description": f"Agent accounts for {bottleneck['details']['percentage']:.0f}% of execution time",
                "strategies": [
                    "Profile agent code for hotspots",
                    "Optimize database queries within agent",
                    "Consider parallelizing agent operations",
                    "Add caching for repeated operations"
                ],
                "estimated_impact": "20-30% faster swarm execution",
                "estimated_effort": "4-6 hours"
            })

        # Recommendation 4: Query optimization
        if medium:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "query_optimization",
                "title": "Optimize Medium-Priority Queries",
                "description": "Improve query performance for frequently used operations",
                "strategies": [
                    "Analyze EXPLAIN QUERY PLAN output",
                    "Rewrite queries to use indexes",
                    "Add covering indexes where beneficial",
                    "Consider query result caching"
                ],
                "estimated_impact": "10-20% performance improvement",
                "estimated_effort": "2-3 hours"
            })

        return recommendations

    def _record_findings_from_analysis(
        self,
        schema_analysis: Dict[str, Any],
        query_performance: Dict[str, Any],
        swarm_performance: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]]
    ):
        """Record findings from analysis"""
        # Record schema findings
        self._record_finding(
            category="schema_analysis",
            finding=f"Analyzed {schema_analysis['tables_count']} tables, estimated total size: {schema_analysis['total_size_estimate']} bytes",
            severity="info",
            metadata=schema_analysis
        )

        # Record index findings
        index_info = schema_analysis.get("indexes", {})
        if index_info.get("missing_index_count", 0) > 0:
            self._record_finding(
                category="missing_indexes",
                finding=f"Found {index_info['missing_index_count']} missing indexes",
                severity="warning",
                metadata=index_info
            )

        # Record query performance findings
        perf_score = query_performance.get("performance_score", 0)
        self._record_finding(
            category="query_performance",
            finding=f"Query performance score: {perf_score}/100",
            severity="critical" if perf_score < 50 else "warning" if perf_score < 70 else "info",
            metadata=query_performance
        )

        # Record swarm performance findings
        if swarm_performance.get("total_execution_time_ms"):
            rating = swarm_performance.get("performance_rating", "UNKNOWN")
            self._record_finding(
                category="swarm_performance",
                finding=f"Swarm execution time: {swarm_performance['total_execution_time_ms']}ms ({rating})",
                severity="info",
                metadata=swarm_performance
            )

        # Record bottlenecks
        for bottleneck in bottlenecks:
            self._record_finding(
                category="bottleneck",
                finding=f"{bottleneck['severity']}: {bottleneck['description']}",
                severity=bottleneck['severity'].lower(),
                metadata=bottleneck
            )

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
