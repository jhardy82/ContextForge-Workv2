"""
Output System Analyst

Research agent that analyzes OutputManager and DisplayManager to identify
consolidation opportunities and design a unified output system.

Uses MCP tools:
- github-copilot: Code analysis and refactoring suggestions
- memory: Knowledge graph building for output system relationships
"""

from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class OutputSystemAnalyst(BaseResearchAgent):
    """Analyzes output systems for consolidation"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.output_files = [
            "src/output_manager.py",
            "python/monitoring/display_manager.py",
            "output_monitor.py"
        ]

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute output system analysis

        Returns:
            Result containing consolidation analysis findings
        """
        # Analyze output system files
        file_analysis = await self._analyze_output_files()

        # Identify commonalities and differences
        comparison = self._compare_output_systems(file_analysis)

        # Identify consolidation opportunities
        consolidation_opportunities = self._identify_consolidation_opportunities(
            file_analysis,
            comparison
        )

        # Build knowledge graph entities
        await self._build_knowledge_graph(file_analysis, consolidation_opportunities)

        # Generate recommendations
        recommendations = self._generate_consolidation_recommendations(
            consolidation_opportunities
        )

        # Record findings
        self._record_findings_from_analysis(
            file_analysis,
            comparison,
            consolidation_opportunities
        )

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "files_analyzed": len(file_analysis),
                "file_analysis": file_analysis,
                "comparison": comparison,
                "consolidation_opportunities": consolidation_opportunities,
                "recommendations": recommendations,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "output-system-analysis"
        )

        return Result.success({
            "analysis": file_analysis,
            "comparison": comparison,
            "consolidation_opportunities": consolidation_opportunities,
            "recommendations": recommendations,
            "findings_count": len(self.findings)
        })

    async def _analyze_output_files(self) -> Dict[str, Any]:
        """
        Analyze output system files

        Returns:
            Analysis results for each output file
        """
        analysis = {}

        for output_file in self.output_files:
            try:
                file_path = Path(output_file)
                if not file_path.exists():
                    self._record_finding(
                        category="file_not_found",
                        finding=f"Output file not found: {output_file}",
                        severity="warning",
                        metadata={"file": output_file}
                    )
                    continue

                # Read file content
                content = self._read_file(output_file)

                # Analyze file structure
                file_analysis = self._analyze_file_content(output_file, content)

                # Use Copilot to explain patterns (simulated for now)
                file_analysis["copilot_insights"] = await self._get_copilot_insights(
                    output_file,
                    content
                )

                analysis[output_file] = file_analysis

                self._record_finding(
                    category="output_analysis",
                    finding=f"Analyzed {output_file}: {file_analysis['lines']} lines, {len(file_analysis['classes'])} classes",
                    severity="info",
                    metadata=file_analysis
                )

            except Exception as e:
                self._record_finding(
                    category="analysis_error",
                    finding=f"Failed to analyze {output_file}: {str(e)}",
                    severity="warning",
                    metadata={"file": output_file, "error": str(e)}
                )

        return analysis

    def _analyze_file_content(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Analyze file content for classes, methods, patterns

        Args:
            filename: Name of the file
            content: File content

        Returns:
            Analysis results
        """
        lines = content.split('\n')

        # Extract classes
        classes = []
        current_class = None
        for i, line in enumerate(lines):
            if line.strip().startswith('class '):
                class_name = line.strip().split('class ')[1].split('(')[0].split(':')[0].strip()
                current_class = {
                    'name': class_name,
                    'line_number': i + 1,
                    'methods': [],
                    'docstring': None
                }
                classes.append(current_class)
            elif current_class and line.strip().startswith('def '):
                method_name = line.strip().split('def ')[1].split('(')[0]
                current_class['methods'].append({
                    'name': method_name,
                    'line_number': i + 1,
                    'is_public': not method_name.startswith('_')
                })

        # Extract imports
        imports = []
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())

        # Identify patterns
        patterns = {
            'uses_rich': 'from rich' in content or 'import rich' in content,
            'uses_json': 'import json' in content or 'json.' in content,
            'uses_threading': 'import threading' in content or 'threading.' in content,
            'uses_console': 'Console' in content,
            'uses_live': 'Live' in content,
            'uses_singleton': 'singleton' in content.lower() or '_instance' in content,
            'uses_envelopes': 'envelope' in content.lower(),
            'uses_display_modes': 'DisplayMode' in content or 'display_mode' in content,
            'uses_progress': 'Progress' in content
        }

        # Count public vs private methods
        public_methods = []
        private_methods = []
        for cls in classes:
            for method in cls['methods']:
                if method['is_public']:
                    public_methods.append(f"{cls['name']}.{method['name']}")
                else:
                    private_methods.append(f"{cls['name']}.{method['name']}")

        return {
            'filename': filename,
            'lines': len(lines),
            'classes': classes,
            'class_count': len(classes),
            'imports': imports[:15],  # First 15 imports
            'import_count': len(imports),
            'patterns': patterns,
            'public_methods': public_methods,
            'public_method_count': len(public_methods),
            'private_methods': private_methods[:10],  # First 10 private methods
            'private_method_count': len(private_methods),
            'purpose': self._infer_purpose(filename, patterns, classes)
        }

    def _infer_purpose(
        self,
        filename: str,
        patterns: Dict[str, bool],
        classes: List[Dict[str, Any]]
    ) -> str:
        """Infer the purpose of the file based on patterns"""
        if 'output_manager' in filename:
            if patterns['uses_envelopes'] and patterns['uses_json']:
                return "CLI JSON envelope builder for machine-readable output"
        elif 'display_manager' in filename:
            if patterns['uses_rich'] and patterns['uses_live']:
                return "Rich console TUI manager for human-readable display"
        elif 'monitor' in filename:
            return "Output monitoring and coordination"
        return "Unknown purpose"

    async def _get_copilot_insights(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Get insights from GitHub Copilot (simulated)

        Args:
            filename: Name of file
            content: File content

        Returns:
            Copilot insights
        """
        # Simulate Copilot analysis
        # In production: result = await self.toolkit.github_copilot.explain(content[:3000])

        insights = {}

        if 'output_manager' in filename:
            insights = {
                "purpose": "Thread-safe JSON output for CLI",
                "pattern": "Singleton with envelope builders",
                "strengths": [
                    "Deterministic JSON encoding",
                    "Thread-safe singleton",
                    "Clear envelope contract (ok/error/partial)"
                ],
                "weaknesses": [
                    "Limited to JSON stdout",
                    "No human-readable formatting",
                    "No progress indicators"
                ]
            }
        elif 'display_manager' in filename:
            insights = {
                "purpose": "Rich TUI display for monitoring",
                "pattern": "Threaded live display with layouts",
                "strengths": [
                    "Multiple display modes",
                    "Real-time updates",
                    "Progress tracking",
                    "Rich formatting"
                ],
                "weaknesses": [
                    "Complex threading model",
                    "No machine-readable output",
                    "Tight coupling to Rich library"
                ]
            }

        return insights

    def _compare_output_systems(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare output systems to identify commonalities and differences

        Args:
            file_analysis: File analysis results

        Returns:
            Comparison results
        """
        output_manager_file = "src/output_manager.py"
        display_manager_file = "python/monitoring/display_manager.py"

        output_manager = file_analysis.get(output_manager_file, {})
        display_manager = file_analysis.get(display_manager_file, {})

        # Compare patterns
        output_patterns = output_manager.get('patterns', {})
        display_patterns = display_manager.get('patterns', {})

        common_patterns = {
            pattern: (output_patterns.get(pattern, False), display_patterns.get(pattern, False))
            for pattern in set(output_patterns.keys()) | set(display_patterns.keys())
        }

        # Identify overlap
        overlap = {
            'threading': output_patterns.get('uses_threading') and display_patterns.get('uses_threading'),
            'singleton': output_patterns.get('uses_singleton') or display_patterns.get('uses_singleton'),
            'console_output': True  # Both output to console
        }

        # Identify differences
        differences = {
            'output_format': {
                'OutputManager': 'JSON (machine-readable)',
                'DisplayManager': 'Rich formatting (human-readable)'
            },
            'threading_model': {
                'OutputManager': 'Thread-safe singleton with locks',
                'DisplayManager': 'Dedicated display thread with live updates'
            },
            'primary_use_case': {
                'OutputManager': 'CLI command output',
                'DisplayManager': 'Real-time monitoring and progress'
            },
            'dependencies': {
                'OutputManager': ['json', 'threading'],
                'DisplayManager': ['rich', 'threading']
            }
        }

        # Calculate overlap score
        overlap_count = sum(1 for v in overlap.values() if v)
        overlap_score = (overlap_count / len(overlap)) * 100

        return {
            'systems_compared': 2,
            'common_patterns': common_patterns,
            'overlap': overlap,
            'overlap_score': overlap_score,
            'differences': differences,
            'output_manager': {
                'lines': output_manager.get('lines', 0),
                'classes': output_manager.get('class_count', 0),
                'public_methods': output_manager.get('public_method_count', 0),
                'purpose': output_manager.get('purpose', 'Unknown')
            },
            'display_manager': {
                'lines': display_manager.get('lines', 0),
                'classes': display_manager.get('class_count', 0),
                'public_methods': display_manager.get('public_method_count', 0),
                'purpose': display_manager.get('purpose', 'Unknown')
            }
        }

    def _identify_consolidation_opportunities(
        self,
        file_analysis: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify opportunities to consolidate output systems

        Args:
            file_analysis: File analysis results
            comparison: Comparison results

        Returns:
            List of consolidation opportunities
        """
        opportunities = []

        # Opportunity 1: Unified output interface
        opportunities.append({
            'priority': 'HIGH',
            'type': 'abstraction',
            'title': 'Create Unified Output Interface',
            'description': 'Abstract base class for all output types (JSON, Rich, plain text)',
            'rationale': 'Both systems output to console but with different formats',
            'benefits': [
                'Single output abstraction',
                'Easy to add new output formats',
                'Consistent API across codebase'
            ],
            'implementation': {
                'create': 'cf_core/output/base_output.py',
                'inherit': ['OutputManager', 'DisplayManager'],
                'interface': [
                    'output(data: Any, format: OutputFormat)',
                    'start_live_display()',
                    'stop_live_display()',
                    'emit(envelope: Dict)'
                ]
            },
            'estimated_effort': '6 hours'
        })

        # Opportunity 2: Shared threading model
        if comparison['overlap']['threading']:
            opportunities.append({
                'priority': 'MEDIUM',
                'type': 'consolidation',
                'title': 'Consolidate Threading Model',
                'description': 'Use single threading model for both JSON and Rich output',
                'rationale': 'Both use threading but with different approaches',
                'benefits': [
                    'Simpler threading model',
                    'Reduced code duplication',
                    'Easier to debug'
                ],
                'implementation': {
                    'create': 'cf_core/output/output_thread.py',
                    'pattern': 'Producer-consumer with queue',
                    'features': [
                        'Thread-safe message queue',
                        'Pluggable formatters (JSON, Rich)',
                        'Graceful shutdown'
                    ]
                },
                'estimated_effort': '8 hours'
            })

        # Opportunity 3: Mode-based output selection
        opportunities.append({
            'priority': 'HIGH',
            'type': 'enhancement',
            'title': 'Mode-Based Output Selection',
            'description': 'Allow runtime selection of output mode (JSON, Rich, Plain)',
            'rationale': 'Different use cases need different output formats',
            'benefits': [
                'CLI can output JSON for piping',
                'Interactive mode can use Rich',
                'Tests can use plain text'
            ],
            'implementation': {
                'create': 'cf_core/output/output_mode.py',
                'enum': ['JSON', 'RICH', 'PLAIN', 'QUIET'],
                'detection': [
                    'Check if stdout is TTY',
                    'Check environment variable OUTPUT_MODE',
                    'Check CLI flag --output-mode'
                ]
            },
            'estimated_effort': '4 hours'
        })

        # Opportunity 4: Unified progress tracking
        opportunities.append({
            'priority': 'MEDIUM',
            'type': 'enhancement',
            'title': 'Unified Progress Tracking',
            'description': 'Single progress tracking system that works with both JSON and Rich',
            'rationale': 'DisplayManager has progress, OutputManager does not',
            'benefits': [
                'Progress in JSON mode (for CI/CD)',
                'Progress in Rich mode (for interactive)',
                'Consistent progress API'
            ],
            'implementation': {
                'create': 'cf_core/output/progress_tracker.py',
                'api': [
                    'start_task(name: str) -> TaskID',
                    'update_task(task_id: TaskID, progress: float)',
                    'complete_task(task_id: TaskID)',
                    'emit_progress(format: OutputFormat)'
                ]
            },
            'estimated_effort': '5 hours'
        })

        return opportunities

    async def _build_knowledge_graph(
        self,
        file_analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ):
        """
        Build knowledge graph of output system architecture

        Args:
            file_analysis: File analysis results
            opportunities: Consolidation opportunities
        """
        entities = []
        relations = []

        # Create entities for output files
        for filename, analysis in file_analysis.items():
            entities.append({
                'name': filename,
                'entityType': 'Output_File',
                'observations': [
                    f"{analysis['lines']} lines of code",
                    f"{analysis['class_count']} classes defined",
                    f"Purpose: {analysis['purpose']}",
                    f"Uses patterns: {', '.join([k for k, v in analysis['patterns'].items() if v])}"
                ]
            })

            # Create entities for classes
            for cls in analysis.get('classes', [])[:3]:  # First 3 classes
                class_entity_name = f"{filename}::{cls['name']}"
                entities.append({
                    'name': class_entity_name,
                    'entityType': 'Output_Class',
                    'observations': [
                        f"Defined in {filename}",
                        f"{len(cls['methods'])} methods",
                        f"Line {cls['line_number']}"
                    ]
                })

                # Create relation
                relations.append({
                    'from': filename,
                    'to': class_entity_name,
                    'relationType': 'defines_class'
                })

        # Create entities for consolidation opportunities
        for i, opp in enumerate(opportunities[:3]):  # Top 3 opportunities
            opp_name = f"Opportunity_{i+1}_{opp['type']}"
            entities.append({
                'name': opp_name,
                'entityType': 'Consolidation_Opportunity',
                'observations': [
                    f"Type: {opp['type']}",
                    f"Priority: {opp['priority']}",
                    f"Title: {opp['title']}",
                    f"Description: {opp['description']}"
                ]
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

    def _generate_consolidation_recommendations(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for output system consolidation

        Args:
            opportunities: Consolidation opportunities

        Returns:
            List of recommendations
        """
        recommendations = []

        # Prioritize opportunities
        high_priority = [o for o in opportunities if o['priority'] == 'HIGH']
        medium_priority = [o for o in opportunities if o['priority'] == 'MEDIUM']

        # Recommendation 1: Phased consolidation approach
        recommendations.append({
            'priority': 'CRITICAL',
            'action': 'phased_consolidation',
            'title': 'Implement Phased Consolidation Strategy',
            'description': 'Consolidate output systems in phases to minimize disruption',
            'phases': [
                {
                    'phase': 1,
                    'name': 'Create Abstraction Layer',
                    'duration': '1 week',
                    'tasks': [
                        'Create cf_core/output/base_output.py',
                        'Define OutputFormat enum',
                        'Create unified output interface'
                    ],
                    'deliverables': ['BaseOutput abstract class', 'OutputMode enum']
                },
                {
                    'phase': 2,
                    'name': 'Adapt Existing Systems',
                    'duration': '1 week',
                    'tasks': [
                        'Wrap OutputManager with BaseOutput',
                        'Wrap DisplayManager with BaseOutput',
                        'Add mode detection'
                    ],
                    'deliverables': ['JSONOutput adapter', 'RichOutput adapter']
                },
                {
                    'phase': 3,
                    'name': 'Migrate Consumers',
                    'duration': '2 weeks',
                    'tasks': [
                        'Update dbcli to use new API',
                        'Update validation agents',
                        'Update tests'
                    ],
                    'deliverables': ['Migrated CLI commands', 'Updated documentation']
                }
            ],
            'total_effort': '4 weeks',
            'risk': 'LOW - Phased approach minimizes disruption'
        })

        # Recommendation 2: Immediate high-priority opportunities
        if high_priority:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'implement_high_priority',
                'title': f'Implement {len(high_priority)} High-Priority Opportunities',
                'description': 'Focus on high-impact consolidation opportunities first',
                'opportunities': [
                    {
                        'title': opp['title'],
                        'effort': opp['estimated_effort'],
                        'benefits': opp['benefits']
                    }
                    for opp in high_priority
                ],
                'total_effort': f"{sum(int(opp['estimated_effort'].split()[0]) for opp in high_priority)} hours",
                'expected_impact': 'Significant reduction in code duplication'
            })

        # Recommendation 3: Testing strategy
        recommendations.append({
            'priority': 'HIGH',
            'action': 'testing_strategy',
            'title': 'Comprehensive Testing for Consolidation',
            'description': 'Ensure consolidation does not break existing functionality',
            'test_strategy': {
                'unit_tests': [
                    'Test BaseOutput interface',
                    'Test JSON output adapter',
                    'Test Rich output adapter',
                    'Test mode detection'
                ],
                'integration_tests': [
                    'Test CLI with JSON mode',
                    'Test CLI with Rich mode',
                    'Test validation agents with new output'
                ],
                'compatibility_tests': [
                    'Test stdout redirection',
                    'Test TTY detection',
                    'Test environment variable overrides'
                ]
            },
            'estimated_effort': '1 week'
        })

        return recommendations

    def _record_findings_from_analysis(
        self,
        file_analysis: Dict[str, Any],
        comparison: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ):
        """Record findings from analysis"""
        # Record file analysis findings
        total_lines = sum(
            a.get('lines', 0) for a in file_analysis.values()
        )
        self._record_finding(
            category="output_system_size",
            finding=f"Analyzed {len(file_analysis)} output files with {total_lines} total lines",
            severity="info",
            metadata={
                'files': list(file_analysis.keys()),
                'total_lines': total_lines
            }
        )

        # Record overlap findings
        self._record_finding(
            category="system_overlap",
            finding=f"Found {comparison['overlap_score']:.0f}% overlap between output systems",
            severity="warning" if comparison['overlap_score'] > 30 else "info",
            metadata=comparison['overlap']
        )

        # Record consolidation opportunities
        for opp in opportunities:
            self._record_finding(
                category="consolidation_opportunity",
                finding=f"{opp['priority']} priority: {opp['title']}",
                severity="warning" if opp['priority'] == 'HIGH' else "info",
                metadata=opp
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
