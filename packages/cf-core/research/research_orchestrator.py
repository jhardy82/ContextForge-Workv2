"""
Research Flow Orchestrator

DAG-based orchestration for research agent execution.
Coordinates 9 research agents across 3 layers: Foundation, Deep Dive, and Synthesis.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import time

from cf_core.research.agents import (
    DataPatternsAnalyst,
    CLIArchitectureAnalyst,
    FrameworkResearcher,
    OutputSystemAnalyst,
    IntegrationStrategist,
    PerformanceAnalyst,
    DesignSynthesizer,
    SpecGenerator,
    KnowledgeCurator
)
from cf_core.shared.result import Result
from cf_core.research.config import get_default_config


class ResearchOrchestrator:
    """
    Orchestrates research agent execution with DAG dependencies.

    Architecture:
    - Layer 1 (Foundation): Parallel execution of DataPatterns, CLIArchitecture, Framework
    - Layer 2 (Deep Dive): Parallel execution of OutputSystem, Integration, Performance
    - Layer 3 (Synthesis): Sequential execution of Design → Spec → Knowledge

    Features:
    - DAG-based dependency management
    - Parallel execution within layers
    - Fail-fast error handling
    - Progress tracking
    - Evidence consolidation
    - Report generation
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Research Orchestrator.

        Args:
            config: Configuration dictionary with:
                - db_type: Database type (postgresql or sqlite)
                - db_host: PostgreSQL host (if using postgresql)
                - db_port: PostgreSQL port (if using postgresql)
                - db_name: Database name
                - db_user: Database user (if using postgresql)
                - db_password: Database password (if using postgresql)
                - db_path: Path to database file (if using sqlite)
                - evidence_dir: Path to evidence output
                - research_reports_dir: Path to research reports
                - specs_output_dir: Path to generated specs
                - knowledge_graph_output: Path to knowledge graph
        """
        # Use TaskMan-v2 config by default
        self.config = config or get_default_config()

        # Ensure all required keys are present (for backwards compatibility)
        if "db_type" not in self.config:
            # Legacy SQLite configuration
            self.config.setdefault("db_path", "db/trackers.sqlite")
            self.config.setdefault("evidence_dir", "evidence")
            self.config.setdefault("research_reports_dir", "research")
            self.config.setdefault("specs_output_dir", "specs")
            self.config.setdefault("knowledge_graph_output", "knowledge_graph")
            self.config.setdefault("validation_reports_dir", "validation_reports")

        # Execution state
        self.execution_start_time = None
        self.execution_end_time = None
        self.agent_results = {}
        self.agent_timings = {}

        # DAG definition
        self.dag = self._define_dag()

    def _define_dag(self) -> Dict[str, List[str]]:
        """
        Define agent dependencies as DAG.

        Returns:
            Dictionary mapping agent names to their dependencies
        """
        return {
            # Layer 1: Foundation Research (no dependencies)
            "DataPatternsAnalyst": [],
            "CLIArchitectureAnalyst": [],
            "FrameworkResearcher": [],

            # Layer 2: Deep Dive Research (depends on Layer 1)
            "OutputSystemAnalyst": [
                "DataPatternsAnalyst",
                "CLIArchitectureAnalyst",
                "FrameworkResearcher"
            ],
            "IntegrationStrategist": [
                "DataPatternsAnalyst",
                "CLIArchitectureAnalyst",
                "FrameworkResearcher"
            ],
            "PerformanceAnalyst": [
                "DataPatternsAnalyst",
                "CLIArchitectureAnalyst",
                "FrameworkResearcher"
            ],

            # Layer 3: Synthesis (depends on all previous layers)
            "DesignSynthesizer": [
                "DataPatternsAnalyst",
                "CLIArchitectureAnalyst",
                "FrameworkResearcher",
                "OutputSystemAnalyst",
                "IntegrationStrategist",
                "PerformanceAnalyst"
            ],
            "SpecGenerator": ["DesignSynthesizer"],
            "KnowledgeCurator": ["DesignSynthesizer", "SpecGenerator"]
        }

    def _topological_sort(self, agents: List[str] = None) -> List[List[str]]:
        """
        Perform topological sort to determine execution order.

        Args:
            agents: Optional list of specific agents to run (runs all if None)

        Returns:
            List of layers, where each layer contains agents that can run in parallel
        """
        # Filter DAG if specific agents requested
        if agents:
            dag = {
                agent: [dep for dep in deps if dep in agents]
                for agent, deps in self.dag.items()
                if agent in agents
            }
        else:
            dag = self.dag

        # Calculate in-degree for each agent
        in_degree = {agent: 0 for agent in dag.keys()}
        for agent, deps in dag.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[agent] += 1

        # Build execution layers
        layers = []
        remaining = set(dag.keys())

        while remaining:
            # Find agents with no dependencies in remaining set
            ready = [
                agent for agent in remaining
                if all(dep not in remaining for dep in dag.get(agent, []))
            ]

            if not ready:
                raise ValueError(f"Circular dependency detected in DAG: {remaining}")

            layers.append(ready)
            remaining -= set(ready)

        return layers

    async def run_research(
        self,
        agents: List[str] = None,
        parallel: bool = True
    ) -> Result[Dict[str, Any]]:
        """
        Execute research flow.

        Args:
            agents: Optional list of specific agents to run (runs all if None)
            parallel: Whether to run agents in parallel within layers

        Returns:
            Result containing:
            - agent_results: Results from each agent
            - execution_time_ms: Total execution time
            - layers_executed: Number of layers executed
            - success_count: Number of successful agents
            - failure_count: Number of failed agents
        """
        try:
            print("\n" + "=" * 80)
            print("RESEARCH FLOW ORCHESTRATOR")
            print("=" * 80)
            print(f"Configuration:")
            print(f"  DB Path: {self.config['db_path']}")
            print(f"  Evidence Dir: {self.config['evidence_dir']}")
            print(f"  Reports Dir: {self.config['research_reports_dir']}")
            print(f"  Specs Dir: {self.config['specs_output_dir']}")
            print(f"  Knowledge Graph Dir: {self.config['knowledge_graph_output']}")
            print("=" * 80)

            self.execution_start_time = time.time()

            # Get execution order
            layers = self._topological_sort(agents)

            print(f"\nExecution Plan: {len(layers)} layers")
            for i, layer in enumerate(layers, 1):
                print(f"  Layer {i}: {', '.join(layer)}")

            # Execute layers
            success_count = 0
            failure_count = 0

            for layer_num, layer in enumerate(layers, 1):
                print(f"\n{'=' * 80}")
                print(f"Layer {layer_num}/{len(layers)}: Executing {len(layer)} agent(s)")
                print(f"{'=' * 80}")

                if parallel and len(layer) > 1:
                    # Parallel execution within layer
                    tasks = [
                        self._execute_agent(agent_name)
                        for agent_name in layer
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for agent_name, result in zip(layer, results):
                        if isinstance(result, Exception):
                            print(f"❌ {agent_name} failed: {str(result)}")
                            failure_count += 1
                            self.agent_results[agent_name] = Result.failure(str(result))
                        elif result.is_failure:
                            print(f"❌ {agent_name} failed: {result.error}")
                            failure_count += 1
                            self.agent_results[agent_name] = result
                        else:
                            print(f"✅ {agent_name} completed successfully")
                            success_count += 1
                            self.agent_results[agent_name] = result
                else:
                    # Sequential execution
                    for agent_name in layer:
                        result = await self._execute_agent(agent_name)
                        self.agent_results[agent_name] = result

                        if result.is_failure:
                            print(f"❌ {agent_name} failed: {result.error}")
                            failure_count += 1
                            # Fail-fast: stop execution on error
                            raise Exception(
                                f"Agent {agent_name} failed: {result.error}"
                            )
                        else:
                            print(f"✅ {agent_name} completed successfully")
                            success_count += 1

            self.execution_end_time = time.time()
            execution_time_ms = (
                (self.execution_end_time - self.execution_start_time) * 1000
            )

            # Generate summary
            summary = {
                "agent_results": {
                    name: {
                        "status": "SUCCESS" if result.is_success else "FAILURE",
                        "execution_time_ms": self.agent_timings.get(name, 0),
                        "summary": result.value if result.is_success else None,
                        "error": result.error if result.is_failure else None
                    }
                    for name, result in self.agent_results.items()
                },
                "execution_time_ms": execution_time_ms,
                "layers_executed": len(layers),
                "success_count": success_count,
                "failure_count": failure_count,
                "total_agents": len(self.agent_results)
            }

            print(f"\n{'=' * 80}")
            print("RESEARCH FLOW COMPLETE")
            print(f"{'=' * 80}")
            print(f"Total Time: {execution_time_ms:.2f}ms")
            print(f"Success: {success_count}/{len(self.agent_results)}")
            print(f"Failure: {failure_count}/{len(self.agent_results)}")
            print(f"{'=' * 80}\n")

            # Generate consolidated reports
            await self._generate_consolidated_reports()

            return Result.ok(summary)

        except Exception as e:
            if self.execution_start_time:
                self.execution_end_time = time.time()
                execution_time_ms = (
                    (self.execution_end_time - self.execution_start_time) * 1000
                )
            else:
                execution_time_ms = 0

            print(f"\n{'=' * 80}")
            print("RESEARCH FLOW FAILED")
            print(f"{'=' * 80}")
            print(f"Error: {str(e)}")
            print(f"Time: {execution_time_ms:.2f}ms")
            print(f"{'=' * 80}\n")

            return Result.failure(f"Research flow failed: {str(e)}")

    async def _execute_agent(self, agent_name: str) -> Result[Dict[str, Any]]:
        """Execute a single research agent."""
        print(f"\n🔍 Starting {agent_name}...")
        agent_start_time = time.time()

        try:
            # Instantiate agent
            agent = self._create_agent(agent_name)

            # Execute research
            result = await agent.research()

            agent_end_time = time.time()
            execution_time_ms = (agent_end_time - agent_start_time) * 1000
            self.agent_timings[agent_name] = execution_time_ms

            if result.is_success:
                print(
                    f"✅ {agent_name} completed in {execution_time_ms:.2f}ms"
                )
            else:
                print(
                    f"❌ {agent_name} failed after {execution_time_ms:.2f}ms: "
                    f"{result.error}"
                )

            return result

        except Exception as e:
            agent_end_time = time.time()
            execution_time_ms = (agent_end_time - agent_start_time) * 1000
            self.agent_timings[agent_name] = execution_time_ms

            print(
                f"❌ {agent_name} exception after {execution_time_ms:.2f}ms: "
                f"{str(e)}"
            )
            return Result.failure(f"Agent execution failed: {str(e)}")

    def _create_agent(self, agent_name: str):
        """Create agent instance by name."""
        agent_classes = {
            "DataPatternsAnalyst": DataPatternsAnalyst,
            "CLIArchitectureAnalyst": CLIArchitectureAnalyst,
            "FrameworkResearcher": FrameworkResearcher,
            "OutputSystemAnalyst": OutputSystemAnalyst,
            "IntegrationStrategist": IntegrationStrategist,
            "PerformanceAnalyst": PerformanceAnalyst,
            "DesignSynthesizer": DesignSynthesizer,
            "SpecGenerator": SpecGenerator,
            "KnowledgeCurator": KnowledgeCurator
        }

        if agent_name not in agent_classes:
            raise ValueError(f"Unknown agent: {agent_name}")

        return agent_classes[agent_name](self.config)

    async def _generate_consolidated_reports(self) -> None:
        """Generate consolidated research reports."""
        print("\n📊 Generating consolidated reports...")

        reports_dir = Path(self.config["research_reports_dir"])
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Consolidated summary report
        summary_report = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time_ms": (
                (self.execution_end_time - self.execution_start_time) * 1000
                if self.execution_end_time else 0
            ),
            "agents_executed": len(self.agent_results),
            "agent_timings": self.agent_timings,
            "results": {
                name: {
                    "status": "SUCCESS" if result.is_success else "FAILURE",
                    "execution_time_ms": self.agent_timings.get(name, 0),
                    "error": result.error if result.is_failure else None
                }
                for name, result in self.agent_results.items()
            }
        }

        summary_file = reports_dir / "consolidated_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2)

        print(f"✅ Consolidated summary: {summary_file}")

        # Markdown summary
        md_file = reports_dir / "research_summary.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Research Swarm Execution Summary\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
            f.write(
                f"**Total Execution Time**: "
                f"{summary_report['total_execution_time_ms']:.2f}ms\n\n"
            )

            f.write("## Agent Execution\n\n")
            for name, result in self.agent_results.items():
                status = "✅ SUCCESS" if result.is_success else "❌ FAILURE"
                time_ms = self.agent_timings.get(name, 0)
                f.write(f"- **{name}**: {status} ({time_ms:.2f}ms)\n")

            f.write("\n## Outputs\n\n")
            f.write(
                f"- Evidence logs: `{self.config['evidence_dir']}/`\n"
            )
            f.write(
                f"- Research reports: `{self.config['research_reports_dir']}/`\n"
            )
            f.write(
                f"- Specifications: `{self.config['specs_output_dir']}/`\n"
            )
            f.write(
                f"- Knowledge graph: `{self.config['knowledge_graph_output']}/`\n"
            )

        print(f"✅ Markdown summary: {md_file}")


async def main():
    """Main entry point for research orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Research Flow Orchestrator - Uses TaskMan-v2 PostgreSQL by default"
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Path to SQLite database file (overrides TaskMan-v2 PostgreSQL config)"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        help="Specific agents to run (runs all if not specified)"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run agents sequentially instead of parallel"
    )

    args = parser.parse_args()

    # Use TaskMan-v2 config by default, or legacy SQLite if --db-path provided
    if args.db_path:
        # Legacy SQLite configuration
        config = {
            "db_path": args.db_path,
            "evidence_dir": "evidence",
            "research_reports_dir": "research",
            "specs_output_dir": "specs",
            "knowledge_graph_output": "knowledge_graph",
            "validation_reports_dir": "validation_reports"
        }
    else:
        # Use TaskMan-v2 PostgreSQL configuration
        config = None  # Will use get_default_config()

    orchestrator = ResearchOrchestrator(config)
    result = await orchestrator.run_research(
        agents=args.agents,
        parallel=not args.sequential
    )

    if result.is_failure:
        print(f"\n❌ Research flow failed: {result.error}")
        return 1

    print("\n✅ Research flow completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
