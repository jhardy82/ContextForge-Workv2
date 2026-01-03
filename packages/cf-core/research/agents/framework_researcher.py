"""
Framework Researcher

Research agent that searches for best practices, framework patterns,
and official documentation to inform implementation decisions.

Uses MCP tools:
- microsoft-learn: Search official documentation and code samples
- sequential-thinking: Synthesize findings into recommendations
"""

from typing import Dict, Any, List
from collections import defaultdict

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class FrameworkResearcher(BaseResearchAgent):
    """Researches framework best practices and patterns"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.research_topics = [
            {
                'topic': 'Python Async/Await Patterns',
                'query': 'Python async await best practices 2024',
                'language': 'python',
                'importance': 'HIGH'
            },
            {
                'topic': 'Typer CLI Framework',
                'query': 'Python Typer CLI framework patterns commands',
                'language': 'python',
                'importance': 'HIGH'
            },
            {
                'topic': 'Result Monad Pattern',
                'query': 'Python Result monad error handling pattern',
                'language': 'python',
                'importance': 'MEDIUM'
            },
            {
                'topic': 'Rich Console Library',
                'query': 'Python Rich console formatting tables',
                'language': 'python',
                'importance': 'MEDIUM'
            },
            {
                'topic': 'SQLite Best Practices',
                'query': 'SQLite foreign key constraints best practices',
                'language': 'sql',
                'importance': 'HIGH'
            },
            {
                'topic': 'GitHub Actions Python',
                'query': 'GitHub Actions Python testing validation workflows',
                'language': 'yaml',
                'importance': 'MEDIUM'
            }
        ]

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute framework research

        Returns:
            Result containing research findings
        """
        # Research each topic
        research_results = []
        for topic_config in self.research_topics:
            result = await self._research_topic(topic_config)
            research_results.append(result)

        # Synthesize findings
        synthesis = await self._synthesize_findings(research_results)

        # Record findings
        self._record_findings_from_research(research_results, synthesis)

        # Generate recommendations
        recommendations = self._generate_framework_recommendations(
            research_results,
            synthesis
        )

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "topics_researched": len(research_results),
                "research_results": research_results,
                "synthesis": synthesis,
                "recommendations": recommendations,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "framework-research"
        )

        return Result.success({
            "research_results": research_results,
            "synthesis": synthesis,
            "recommendations": recommendations,
            "findings_count": len(self.findings)
        })

    async def _research_topic(self, topic_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research a specific topic using microsoft-learn MCP

        Args:
            topic_config: Topic configuration

        Returns:
            Research results for topic
        """
        topic = topic_config['topic']
        query = topic_config['query']
        language = topic_config.get('language')

        # Search documentation (simulated)
        # In production: docs_result = await self.toolkit.microsoft_learn.search_docs(query)
        docs_result = self._simulate_docs_search(query)

        # Search code samples (simulated)
        # In production: samples_result = await self.toolkit.microsoft_learn.search_code_samples(query, language)
        samples_result = self._simulate_code_samples_search(query, language)

        # Synthesize with sequential thinking (simulated)
        # In production: synthesis = await self._sequential_thinking_synthesis(docs_result, samples_result)
        synthesis = self._simulate_synthesis(topic, docs_result, samples_result)

        return {
            'topic': topic,
            'query': query,
            'importance': topic_config['importance'],
            'docs_found': len(docs_result),
            'samples_found': len(samples_result),
            'key_findings': synthesis['key_findings'],
            'best_practices': synthesis['best_practices'],
            'code_patterns': synthesis['code_patterns'],
            'docs_summary': docs_result[:3],  # Top 3 docs
            'samples_summary': samples_result[:3]  # Top 3 samples
        }

    def _simulate_docs_search(self, query: str) -> List[Dict[str, Any]]:
        """Simulate documentation search results"""
        # This would be replaced with actual MCP call in production
        simulated_results = []

        if 'async' in query.lower():
            simulated_results = [
                {
                    'title': 'Asynchronous I/O - Python Documentation',
                    'url': 'https://docs.python.org/3/library/asyncio.html',
                    'excerpt': 'asyncio is a library to write concurrent code using the async/await syntax...',
                    'relevance': 0.95
                },
                {
                    'title': 'Async Best Practices - Python Guide',
                    'url': 'https://docs.python-guide.org/scenarios/async/',
                    'excerpt': 'Best practices for async programming in Python including error handling...',
                    'relevance': 0.89
                },
                {
                    'title': 'Modern Python Async Patterns',
                    'url': 'https://realpython.com/async-io-python/',
                    'excerpt': 'Comprehensive guide to async/await patterns in modern Python...',
                    'relevance': 0.87
                }
            ]
        elif 'typer' in query.lower():
            simulated_results = [
                {
                    'title': 'Typer CLI Framework Documentation',
                    'url': 'https://typer.tiangolo.com/',
                    'excerpt': 'Typer is a library for building CLI applications based on Python type hints...',
                    'relevance': 0.98
                },
                {
                    'title': 'Building CLIs with Typer',
                    'url': 'https://typer.tiangolo.com/tutorial/',
                    'excerpt': 'Tutorial on creating command-line interfaces with Typer...',
                    'relevance': 0.92
                },
                {
                    'title': 'Typer Sub-applications',
                    'url': 'https://typer.tiangolo.com/tutorial/subcommands/',
                    'excerpt': 'How to organize commands using sub-applications in Typer...',
                    'relevance': 0.90
                }
            ]
        elif 'rich' in query.lower():
            simulated_results = [
                {
                    'title': 'Rich Console Library',
                    'url': 'https://rich.readthedocs.io/',
                    'excerpt': 'Rich is a Python library for rich text and beautiful formatting...',
                    'relevance': 0.97
                },
                {
                    'title': 'Rich Tables and Formatting',
                    'url': 'https://rich.readthedocs.io/en/latest/tables.html',
                    'excerpt': 'Creating beautiful tables with the Rich library...',
                    'relevance': 0.94
                }
            ]
        elif 'sqlite' in query.lower():
            simulated_results = [
                {
                    'title': 'SQLite Foreign Key Support',
                    'url': 'https://www.sqlite.org/foreignkeys.html',
                    'excerpt': 'SQLite foreign key constraint enforcement and best practices...',
                    'relevance': 0.96
                },
                {
                    'title': 'SQLite Best Practices',
                    'url': 'https://www.sqlite.org/bestpractice.html',
                    'excerpt': 'Recommended practices for SQLite database design...',
                    'relevance': 0.91
                }
            ]
        elif 'github actions' in query.lower():
            simulated_results = [
                {
                    'title': 'GitHub Actions for Python',
                    'url': 'https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-python',
                    'excerpt': 'Setting up continuous integration for Python projects...',
                    'relevance': 0.95
                },
                {
                    'title': 'GitHub Actions Workflow Syntax',
                    'url': 'https://docs.github.com/actions/reference/workflow-syntax-for-github-actions',
                    'excerpt': 'Complete reference for GitHub Actions workflow YAML syntax...',
                    'relevance': 0.88
                }
            ]
        else:
            simulated_results = [
                {
                    'title': f'Documentation for {query}',
                    'url': 'https://example.com/docs',
                    'excerpt': f'General documentation about {query}...',
                    'relevance': 0.70
                }
            ]

        return simulated_results

    def _simulate_code_samples_search(
        self,
        query: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Simulate code sample search results"""
        simulated_samples = []

        if 'async' in query.lower() and language == 'python':
            simulated_samples = [
                {
                    'title': 'Async function example',
                    'language': 'python',
                    'code': '''async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com') as resp:
            return await resp.json()''',
                    'source': 'Python Async Guide',
                    'relevance': 0.92
                },
                {
                    'title': 'Async error handling',
                    'language': 'python',
                    'code': '''async def safe_fetch():
    try:
        result = await fetch_data()
        return Result.success(result)
    except Exception as e:
        return Result.failure(str(e))''',
                    'source': 'Error Handling Patterns',
                    'relevance': 0.88
                }
            ]
        elif 'typer' in query.lower() and language == 'python':
            simulated_samples = [
                {
                    'title': 'Typer sub-app registration',
                    'language': 'python',
                    'code': '''import typer

app = typer.Typer()
validation_app = typer.Typer()

app.add_typer(validation_app, name="validate")

@validation_app.command()
def run(scope: str = "quick"):
    """Run validation"""
    pass''',
                    'source': 'Typer Documentation',
                    'relevance': 0.96
                }
            ]
        elif 'rich' in query.lower() and language == 'python':
            simulated_samples = [
                {
                    'title': 'Rich Table creation',
                    'language': 'python',
                    'code': '''from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Results")
table.add_column("Name", style="cyan")
table.add_column("Status", style="green")
console.print(table)''',
                    'source': 'Rich Documentation',
                    'relevance': 0.94
                }
            ]

        return simulated_samples

    def _simulate_synthesis(
        self,
        topic: str,
        docs: List[Dict[str, Any]],
        samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate synthesis of research findings"""
        # This would use sequential-thinking MCP in production

        synthesis = {
            'key_findings': [],
            'best_practices': [],
            'code_patterns': []
        }

        if 'async' in topic.lower():
            synthesis['key_findings'] = [
                'async/await is the modern standard for concurrent Python code',
                'Error handling in async requires try/except with Result pattern',
                'asyncio library provides core async functionality'
            ]
            synthesis['best_practices'] = [
                'Always use async context managers for resources',
                'Handle exceptions at async boundaries',
                'Use asyncio.gather for concurrent tasks',
                'Wrap async results in Result monad for error propagation'
            ]
            synthesis['code_patterns'] = [
                'async def function_name(): ...',
                'result = await async_call()',
                'async with context_manager(): ...'
            ]
        elif 'typer' in topic.lower():
            synthesis['key_findings'] = [
                'Typer uses Python type hints for automatic CLI generation',
                'Sub-applications organize commands by domain',
                'Decorators define commands and options'
            ]
            synthesis['best_practices'] = [
                'Use sub-apps for command groups (validation, tasks, etc.)',
                'Register sub-apps with descriptive names',
                'Provide help text for all commands and options',
                'Use typer.Option for default values and help'
            ]
            synthesis['code_patterns'] = [
                'app = typer.Typer()',
                '@app.command()',
                'app.add_typer(sub_app, name="command_group")'
            ]
        elif 'rich' in topic.lower():
            synthesis['key_findings'] = [
                'Rich provides beautiful console output',
                'Tables, panels, and progress bars are key components',
                'Supports colors, styles, and markup'
            ]
            synthesis['best_practices'] = [
                'Use Console() for consistent output',
                'Tables for tabular data',
                'Panels for grouped information',
                'Progress bars for long operations'
            ]
            synthesis['code_patterns'] = [
                'console = Console()',
                'table = Table(title="...")',
                'console.print(table)'
            ]
        elif 'sqlite' in topic.lower():
            synthesis['key_findings'] = [
                'Foreign key enforcement must be enabled per connection',
                'CASCADE options control referential integrity',
                'Soft deletes require application-level handling'
            ]
            synthesis['best_practices'] = [
                'Always enable foreign keys: PRAGMA foreign_keys = ON',
                'Use ON DELETE CASCADE or SET NULL for referential integrity',
                'Design schema with soft deletes (deleted_at column)',
                'Validate foreign key constraints in application logic'
            ]
            synthesis['code_patterns'] = [
                'conn.execute("PRAGMA foreign_keys = ON")',
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL'
            ]
        elif 'github actions' in topic.lower():
            synthesis['key_findings'] = [
                'GitHub Actions automates CI/CD workflows',
                'Workflows triggered by events (push, PR, schedule)',
                'Jobs run in parallel by default'
            ]
            synthesis['best_practices'] = [
                'Use caching for dependencies',
                'Schedule nightly validation runs',
                'Upload artifacts for reports',
                'Use continue-on-error for validation steps initially'
            ]
            synthesis['code_patterns'] = [
                'on: schedule: - cron: "0 2 * * *"',
                'uses: actions/setup-python@v4',
                'uses: actions/upload-artifact@v4'
            ]

        return synthesis

    async def _synthesize_findings(
        self,
        research_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize findings across all research topics

        Args:
            research_results: Results from all research topics

        Returns:
            Synthesized findings
        """
        # Group by importance
        high_priority = [r for r in research_results if r['importance'] == 'HIGH']
        medium_priority = [r for r in research_results if r['importance'] == 'MEDIUM']

        # Extract all best practices
        all_best_practices = []
        for result in research_results:
            all_best_practices.extend(result['best_practices'])

        # Extract all code patterns
        all_patterns = []
        for result in research_results:
            all_patterns.extend(result['code_patterns'])

        synthesis = {
            'high_priority_topics': [r['topic'] for r in high_priority],
            'medium_priority_topics': [r['topic'] for r in medium_priority],
            'total_docs_found': sum(r['docs_found'] for r in research_results),
            'total_samples_found': sum(r['samples_found'] for r in research_results),
            'consolidated_best_practices': list(set(all_best_practices)),
            'consolidated_patterns': list(set(all_patterns)),
            'cross_cutting_concerns': self._identify_cross_cutting_concerns(research_results)
        }

        return synthesis

    def _identify_cross_cutting_concerns(
        self,
        research_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns that appear across multiple topics"""
        concerns = [
            {
                'concern': 'Error Handling',
                'topics': ['async', 'result_monad', 'typer'],
                'recommendation': 'Use Result monad pattern consistently across async and CLI code'
            },
            {
                'concern': 'User Experience',
                'topics': ['typer', 'rich'],
                'recommendation': 'Combine Typer CLI with Rich formatting for professional output'
            },
            {
                'concern': 'Data Integrity',
                'topics': ['sqlite', 'validation'],
                'recommendation': 'Enable foreign key enforcement and validate at application level'
            },
            {
                'concern': 'Testing & CI/CD',
                'topics': ['github_actions', 'validation'],
                'recommendation': 'Automate validation runs in CI/CD pipeline'
            }
        ]

        return concerns

    def _generate_framework_recommendations(
        self,
        research_results: List[Dict[str, Any]],
        synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on research"""
        recommendations = []

        # Recommendation 1: Async patterns
        async_research = next(
            (r for r in research_results if 'async' in r['topic'].lower()),
            None
        )
        if async_research:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Async Programming',
                'recommendation': 'Adopt async/await patterns for validation orchestrator',
                'rationale': 'Modern Python standard for concurrent operations',
                'implementation': async_research['best_practices'],
                'code_examples': async_research['code_patterns'],
                'estimated_effort': '2 hours'
            })

        # Recommendation 2: CLI framework
        typer_research = next(
            (r for r in research_results if 'typer' in r['topic'].lower()),
            None
        )
        if typer_research:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'CLI Framework',
                'recommendation': 'Use Typer sub-apps for validation commands',
                'rationale': 'Follows existing dbcli patterns',
                'implementation': typer_research['best_practices'],
                'code_examples': typer_research['code_patterns'],
                'estimated_effort': '4 hours'
            })

        # Recommendation 3: Display
        rich_research = next(
            (r for r in research_results if 'rich' in r['topic'].lower()),
            None
        )
        if rich_research:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Console Output',
                'recommendation': 'Leverage Rich library for validation results display',
                'rationale': 'Already used in dbcli, consistent UX',
                'implementation': rich_research['best_practices'],
                'code_examples': rich_research['code_patterns'],
                'estimated_effort': '3 hours'
            })

        # Recommendation 4: Cross-cutting
        recommendations.append({
            'priority': 'HIGH',
            'area': 'Cross-Cutting Concerns',
            'recommendation': 'Address cross-cutting concerns consistently',
            'rationale': 'Patterns appear across multiple areas',
            'implementation': synthesis['cross_cutting_concerns'],
            'estimated_effort': '6 hours'
        })

        return recommendations

    def _record_findings_from_research(
        self,
        research_results: List[Dict[str, Any]],
        synthesis: Dict[str, Any]
    ):
        """Record findings from research"""
        # Record research coverage
        self._record_finding(
            category="research_coverage",
            finding=f"Researched {len(research_results)} topics, found {synthesis['total_docs_found']} docs and {synthesis['total_samples_found']} code samples",
            severity="info",
            metadata={
                'topics': [r['topic'] for r in research_results],
                'docs_found': synthesis['total_docs_found'],
                'samples_found': synthesis['total_samples_found']
            }
        )

        # Record high priority findings
        for result in research_results:
            if result['importance'] == 'HIGH':
                self._record_finding(
                    category="high_priority_research",
                    finding=f"{result['topic']}: {len(result['best_practices'])} best practices identified",
                    severity="info",
                    metadata=result
                )

        # Record cross-cutting concerns
        for concern in synthesis['cross_cutting_concerns']:
            self._record_finding(
                category="cross_cutting_concerns",
                finding=f"{concern['concern']}: {concern['recommendation']}",
                severity="warning",
                metadata=concern
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
