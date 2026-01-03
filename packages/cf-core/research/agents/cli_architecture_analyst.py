"""
CLI Architecture Analyst

Research agent that analyzes CLI architecture and structure to identify
integration points for validation commands and understand command patterns.

Uses MCP tools:
- github-copilot: Code explanation and pattern analysis
- memory: Knowledge graph building for CLI relationships
- sequential-thinking: Complex architecture analysis
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class CLIArchitectureAnalyst(BaseResearchAgent):
    """Analyzes CLI architecture and integration patterns"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.cli_files = [
            "dbcli.py",
            "python/dbcli/app.py",
            "python/dbcli/tasks_commands.py",
            "cf_cli.py",
            "tasks_cli.py",
            "sprints_cli.py",
            "projects_cli.py"
        ]

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute CLI architecture analysis

        Returns:
            Result containing architecture analysis findings
        """
        # Analyze CLI file structure
        cli_analysis = await self._analyze_cli_files()

        # Identify integration points
        integration_points = self._identify_integration_points(cli_analysis)

        # Build knowledge graph entities
        await self._build_knowledge_graph(cli_analysis, integration_points)

        # Generate recommendations
        recommendations = self._generate_integration_recommendations(
            cli_analysis,
            integration_points
        )

        # Record findings
        self._record_findings_from_analysis(cli_analysis, integration_points)

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "cli_files_analyzed": len(cli_analysis),
                "cli_analysis": cli_analysis,
                "integration_points": integration_points,
                "recommendations": recommendations,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "cli-architecture-analysis"
        )

        return Result.success({
            "analysis": cli_analysis,
            "integration_points": integration_points,
            "recommendations": recommendations,
            "findings_count": len(self.findings)
        })

    async def _analyze_cli_files(self) -> Dict[str, Any]:
        """
        Analyze CLI files to understand structure and patterns

        Returns:
            Analysis results for each CLI file
        """
        analysis = {}

        for cli_file in self.cli_files:
            try:
                file_path = Path(cli_file)
                if not file_path.exists():
                    self._record_finding(
                        category="file_not_found",
                        finding=f"CLI file not found: {cli_file}",
                        severity="warning",
                        metadata={"file": cli_file}
                    )
                    continue

                # Read file content
                content = self._read_file(cli_file)

                # Analyze file structure
                file_analysis = self._analyze_file_structure(cli_file, content)

                # Use Copilot to explain patterns (simulated for now)
                # In production, this would call actual MCP tool
                file_analysis["copilot_insights"] = await self._get_copilot_insights(
                    cli_file,
                    content
                )

                analysis[cli_file] = file_analysis

                self._record_finding(
                    category="cli_analysis",
                    finding=f"Analyzed {cli_file}: {file_analysis['lines']} lines, {len(file_analysis['commands'])} commands",
                    severity="info",
                    metadata=file_analysis
                )

            except Exception as e:
                self._record_finding(
                    category="analysis_error",
                    finding=f"Failed to analyze {cli_file}: {str(e)}",
                    severity="warning",
                    metadata={"file": cli_file, "error": str(e)}
                )

        return analysis

    def _analyze_file_structure(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Analyze file structure to extract commands, imports, patterns

        Args:
            filename: Name of the file
            content: File content

        Returns:
            Analysis results
        """
        lines = content.split('\n')

        # Extract imports
        imports = []
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())

        # Extract Typer app creation
        typer_apps = []
        for i, line in enumerate(lines):
            if 'typer.Typer' in line:
                typer_apps.append({
                    'line_number': i + 1,
                    'code': line.strip()
                })

        # Extract command decorators
        commands = []
        for i, line in enumerate(lines):
            if '@' in line and ('command' in line or 'app.command' in line):
                # Get function name from next non-empty line
                func_name = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip().startswith('def '):
                        func_name = lines[j].strip().split('(')[0].replace('def ', '')
                        break

                commands.append({
                    'line_number': i + 1,
                    'decorator': line.strip(),
                    'function': func_name,
                    'context_lines': lines[max(0, i-2):min(len(lines), i+5)]
                })

        # Identify sub-app registrations
        sub_apps = []
        for i, line in enumerate(lines):
            if 'add_typer' in line:
                sub_apps.append({
                    'line_number': i + 1,
                    'code': line.strip()
                })

        # Framework detection
        frameworks = {
            'typer': 'import typer' in content,
            'click': 'import click' in content,
            'argparse': 'import argparse' in content,
            'rich': 'from rich' in content or 'import rich' in content
        }

        return {
            'filename': filename,
            'lines': len(lines),
            'imports': imports[:10],  # First 10 imports
            'import_count': len(imports),
            'typer_apps': typer_apps,
            'commands': commands,
            'command_count': len(commands),
            'sub_apps': sub_apps,
            'sub_app_count': len(sub_apps),
            'frameworks': frameworks,
            'has_validation_command': 'validate' in content.lower()
        }

    async def _get_copilot_insights(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Get insights from GitHub Copilot (simulated)

        In production, this would use actual MCP tool

        Args:
            filename: Name of file
            content: File content

        Returns:
            Copilot insights
        """
        # Simulate Copilot analysis
        # In production: result = await self.toolkit.github_copilot.explain(content[:2000])

        insights = {
            "architecture_pattern": "Typer CLI with sub-apps",
            "command_organization": "Commands organized by domain (tasks, sprints, projects)",
            "integration_readiness": "High - sub-app pattern supports new command groups",
            "recommended_location": f"{filename} - add validation_app sub-app"
        }

        return insights

    def _identify_integration_points(self, cli_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify optimal integration points for validation commands

        Args:
            cli_analysis: CLI analysis results

        Returns:
            List of integration points with recommendations
        """
        integration_points = []

        # Look for primary CLI files with sub-app support
        for filename, analysis in cli_analysis.items():
            if analysis.get('sub_app_count', 0) > 0:
                integration_points.append({
                    'file': filename,
                    'type': 'sub_app_registration',
                    'priority': 'HIGH',
                    'location': 'After existing sub-app registrations',
                    'pattern': 'app.add_typer(validation_app, name="validate")',
                    'reasoning': f"File has {analysis['sub_app_count']} existing sub-apps, follows established pattern",
                    'estimated_lines': 1,
                    'dependencies': ['cf_core.validation.flow_orchestrator']
                })

            if analysis.get('command_count', 0) > 0 and not analysis.get('has_validation_command'):
                integration_points.append({
                    'file': filename,
                    'type': 'new_command_group',
                    'priority': 'MEDIUM',
                    'location': 'Create python/dbcli/validation_commands.py',
                    'pattern': 'New validation_app with @validation_app.command() decorators',
                    'reasoning': f"File has {analysis['command_count']} commands, needs validation command group",
                    'estimated_lines': 300,
                    'dependencies': [
                        'cf_core.validation.flow_orchestrator',
                        'rich.console',
                        'typer'
                    ]
                })

        # Rank by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        integration_points.sort(key=lambda x: priority_order.get(x['priority'], 999))

        return integration_points

    async def _build_knowledge_graph(
        self,
        cli_analysis: Dict[str, Any],
        integration_points: List[Dict[str, Any]]
    ):
        """
        Build knowledge graph of CLI architecture

        Args:
            cli_analysis: CLI analysis results
            integration_points: Integration points
        """
        entities = []
        relations = []

        # Create entities for CLI files
        for filename, analysis in cli_analysis.items():
            entities.append({
                'name': filename,
                'entityType': 'CLI_File',
                'observations': [
                    f"{analysis['lines']} lines of code",
                    f"{analysis['command_count']} commands defined",
                    f"Uses frameworks: {', '.join([f for f, used in analysis['frameworks'].items() if used])}",
                    f"Has {analysis['sub_app_count']} sub-apps"
                ]
            })

            # Create entities for commands
            for cmd in analysis.get('commands', [])[:5]:  # First 5 commands
                if cmd['function']:
                    cmd_entity_name = f"{filename}::{cmd['function']}"
                    entities.append({
                        'name': cmd_entity_name,
                        'entityType': 'CLI_Command',
                        'observations': [
                            f"Defined in {filename}",
                            f"Decorator: {cmd['decorator']}",
                            f"Line {cmd['line_number']}"
                        ]
                    })

                    # Create relation
                    relations.append({
                        'from': filename,
                        'to': cmd_entity_name,
                        'relationType': 'defines_command'
                    })

        # Create entities for integration points
        for i, point in enumerate(integration_points[:3]):  # Top 3 integration points
            point_name = f"Integration_Point_{i+1}_{point['type']}"
            entities.append({
                'name': point_name,
                'entityType': 'Integration_Point',
                'observations': [
                    f"Type: {point['type']}",
                    f"Priority: {point['priority']}",
                    f"File: {point['file']}",
                    f"Pattern: {point['pattern']}",
                    f"Reasoning: {point['reasoning']}"
                ]
            })

            # Create relation to file
            relations.append({
                'from': point['file'],
                'to': point_name,
                'relationType': 'has_integration_point'
            })

        # Store in knowledge graph (simulated)
        # In production: await self.toolkit.memory.create_entities(entities)
        # In production: await self.toolkit.memory.create_relations(relations)

        self._record_finding(
            category="knowledge_graph",
            finding=f"Built knowledge graph with {len(entities)} entities and {len(relations)} relations",
            severity="info",
            metadata={
                'entity_count': len(entities),
                'relation_count': len(relations),
                'entity_types': list(set(e['entityType'] for e in entities))
            }
        )

    def _generate_integration_recommendations(
        self,
        cli_analysis: Dict[str, Any],
        integration_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for CLI integration

        Args:
            cli_analysis: CLI analysis results
            integration_points: Integration points

        Returns:
            List of recommendations
        """
        recommendations = []

        # Recommendation 1: Primary integration point
        if integration_points:
            primary_point = integration_points[0]
            recommendations.append({
                'priority': 'HIGH',
                'action': 'integrate_validation_commands',
                'title': f"Add Validation Commands to {primary_point['file']}",
                'description': f"Integrate validation agent swarm via {primary_point['type']}",
                'implementation': {
                    'file': primary_point['file'],
                    'pattern': primary_point['pattern'],
                    'location': primary_point['location'],
                    'dependencies': primary_point.get('dependencies', [])
                },
                'code_example': self._generate_code_example(primary_point),
                'estimated_effort': '4 hours',
                'impact': 'Enables dbcli validate commands'
            })

        # Recommendation 2: Command module structure
        recommendations.append({
            'priority': 'HIGH',
            'action': 'create_validation_commands_module',
            'title': 'Create python/dbcli/validation_commands.py',
            'description': 'Create dedicated module for validation commands following dbcli patterns',
            'implementation': {
                'file': 'python/dbcli/validation_commands.py',
                'structure': [
                    'validation_app = typer.Typer()',
                    '@validation_app.command("run")',
                    '@validation_app.command("report")',
                    '@validation_app.command("history")'
                ],
                'dependencies': [
                    'cf_core.validation.flow_orchestrator',
                    'rich.console',
                    'rich.table',
                    'typer'
                ]
            },
            'estimated_effort': '6 hours',
            'impact': '4 new validation commands available'
        })

        # Recommendation 3: Display integration
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'integrate_display_patterns',
            'title': 'Reuse Existing Display Patterns',
            'description': 'Leverage existing Rich console patterns from dbcli',
            'implementation': {
                'files_to_reference': [
                    'python/dbcli/tasks_commands.py',
                    'python/monitoring/display_manager.py'
                ],
                'patterns_to_reuse': [
                    'Rich Table formatting',
                    'Panel creation',
                    'Progress indicators',
                    'Console output styling'
                ],
                'example_functions': [
                    'format_task_table()',
                    'display_sprint_summary()'
                ]
            },
            'estimated_effort': '3 hours',
            'impact': 'Consistent UX across dbcli'
        })

        return recommendations

    def _generate_code_example(self, integration_point: Dict[str, Any]) -> str:
        """Generate code example for integration"""
        if integration_point['type'] == 'sub_app_registration':
            return f"""
# In {integration_point['file']}
from python.dbcli.validation_commands import validation_app

# Add validation sub-app
app.add_typer(validation_app, name="validate")
"""
        elif integration_point['type'] == 'new_command_group':
            return """
# python/dbcli/validation_commands.py
import typer
from rich.console import Console
from cf_core.validation.flow_orchestrator import FlowOrchestrator

validation_app = typer.Typer(help="Database validation operations")
console = Console()

@validation_app.command("run")
def validate_database(
    scope: str = typer.Option("quick", help="Validation scope"),
    performance: bool = typer.Option(False, help="Include performance tests")
):
    \"\"\"Run validation agent swarm\"\"\"
    orchestrator = FlowOrchestrator("db/trackers.sqlite", {"scope": scope})
    result = orchestrator.execute_flow()
    # Display results...
"""
        return ""

    def _record_findings_from_analysis(
        self,
        cli_analysis: Dict[str, Any],
        integration_points: List[Dict[str, Any]]
    ):
        """Record findings from analysis"""
        # Record CLI file findings
        total_commands = sum(
            a.get('command_count', 0) for a in cli_analysis.values()
        )
        self._record_finding(
            category="cli_structure",
            finding=f"Analyzed {len(cli_analysis)} CLI files with {total_commands} total commands",
            severity="info",
            metadata={
                'files': list(cli_analysis.keys()),
                'total_commands': total_commands
            }
        )

        # Record framework findings
        frameworks_used = set()
        for analysis in cli_analysis.values():
            frameworks_used.update(
                f for f, used in analysis.get('frameworks', {}).items() if used
            )

        self._record_finding(
            category="frameworks",
            finding=f"CLI uses frameworks: {', '.join(frameworks_used)}",
            severity="info",
            metadata={'frameworks': list(frameworks_used)}
        )

        # Record integration point findings
        for point in integration_points[:3]:
            self._record_finding(
                category="integration_points",
                finding=f"Found {point['priority']} priority integration point in {point['file']}",
                severity="info" if point['priority'] == 'HIGH' else "warning",
                metadata=point
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
