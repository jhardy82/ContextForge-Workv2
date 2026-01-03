"""
Integration Strategist

Research agent that researches CI/CD integration patterns and provides
recommendations for integrating validation swarm into automated pipelines.

Uses MCP tools:
- microsoft-learn: Research CI/CD best practices
- sequential-thinking: Multi-step integration strategy synthesis
"""

from typing import Dict, Any, List
from collections import defaultdict

from cf_core.shared.result import Result
from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit


class IntegrationStrategist(BaseResearchAgent):
    """Researches CI/CD integration patterns"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)
        self.research_topics = [
            {
                "topic": "GitHub Actions for Python Projects",
                "query": "github actions python testing CI/CD best practices",
                "importance": "HIGH",
                "language": "yaml"
            },
            {
                "topic": "Database Testing in CI/CD",
                "query": "database integration testing CI/CD SQLite fixtures",
                "importance": "HIGH",
                "language": "python"
            },
            {
                "topic": "Validation Gates in CI/CD",
                "query": "quality gates validation checks CI/CD pipelines",
                "importance": "HIGH",
                "language": "yaml"
            },
            {
                "topic": "Matrix Testing Strategies",
                "query": "github actions matrix strategy python versions",
                "importance": "MEDIUM",
                "language": "yaml"
            }
        ]

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute CI/CD integration research

        Returns:
            Result containing integration strategy findings
        """
        # Research each topic
        research_results = []
        for topic_config in self.research_topics:
            result = await self._research_topic(topic_config)
            research_results.append(result)

        # Synthesize findings
        synthesis = await self._synthesize_findings(research_results)

        # Generate integration strategy
        strategy = self._generate_integration_strategy(synthesis)

        # Create workflow examples
        workflow_examples = self._create_workflow_examples(strategy)

        # Record findings
        self._record_findings_from_research(research_results, synthesis, strategy)

        # Save research report
        self._save_research_report(
            {
                "agent_name": self.agent_name,
                "timestamp": self._utc_now(),
                "topics_researched": len(research_results),
                "research_results": research_results,
                "synthesis": synthesis,
                "integration_strategy": strategy,
                "workflow_examples": workflow_examples,
                "total_findings": len(self.findings),
                "findings_by_category": self._group_findings_by_category(),
                "findings_by_severity": self._count_by_severity()
            },
            "integration-strategy"
        )

        return Result.success({
            "research_results": research_results,
            "synthesis": synthesis,
            "strategy": strategy,
            "workflow_examples": workflow_examples,
            "findings_count": len(self.findings)
        })

    async def _research_topic(self, topic_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research a specific CI/CD integration topic

        Args:
            topic_config: Topic configuration

        Returns:
            Research findings
        """
        topic = topic_config["topic"]
        query = topic_config["query"]
        importance = topic_config["importance"]
        language = topic_config.get("language")

        self._record_finding(
            category="topic_research",
            finding=f"Researching: {topic}",
            severity="info",
            metadata={"query": query, "importance": importance}
        )

        # Simulate documentation search (in production, use actual MCP tool)
        # docs_result = await self.toolkit.microsoft_learn.search_docs(query)
        docs_result = self._simulate_docs_search(query)

        # Simulate code samples search
        # samples_result = await self.toolkit.microsoft_learn.search_code_samples(query, language)
        samples_result = self._simulate_code_samples_search(query, language)

        # Synthesize with sequential thinking (simulated)
        synthesis = self._simulate_synthesis(topic, docs_result, samples_result)

        return {
            "topic": topic,
            "importance": importance,
            "documentation_findings": docs_result,
            "code_samples": samples_result,
            "synthesis": synthesis
        }

    def _simulate_docs_search(self, query: str) -> Dict[str, Any]:
        """Simulate documentation search results"""
        if "github actions" in query.lower():
            return {
                "key_findings": [
                    "GitHub Actions supports matrix strategies for testing multiple Python versions",
                    "Workflow files should be in .github/workflows/ directory",
                    "Caching dependencies speeds up CI runs significantly",
                    "Artifacts can persist test results between jobs",
                    "Secrets management through GitHub repository settings"
                ],
                "best_practices": [
                    "Use setup-python action for Python environments",
                    "Pin action versions with @v3 or commit SHA",
                    "Split long workflows into multiple jobs",
                    "Use concurrency controls to cancel outdated runs",
                    "Store test artifacts for debugging failures"
                ]
            }
        elif "database testing" in query.lower():
            return {
                "key_findings": [
                    "SQLite works well for CI testing without external dependencies",
                    "Database fixtures should be version-controlled",
                    "Test isolation critical for parallel test execution",
                    "Migration testing should run in CI pipeline",
                    "Seed data management using fixtures or factories"
                ],
                "best_practices": [
                    "Use in-memory SQLite for fastest tests",
                    "Reset database state between test runs",
                    "Test both schema and data migrations",
                    "Use pytest fixtures for database setup/teardown",
                    "Validate foreign key constraints in tests"
                ]
            }
        elif "validation gates" in query.lower():
            return {
                "key_findings": [
                    "Quality gates prevent merging code that doesn't meet standards",
                    "Branch protection rules enforce validation checks",
                    "Status checks can be required before merge",
                    "Validation should include tests, linting, type checking",
                    "Fail-fast approach saves CI time"
                ],
                "best_practices": [
                    "Run fast checks (linting, type checking) first",
                    "Parallel execution of independent validations",
                    "Clear failure messages for debugging",
                    "Store validation reports as artifacts",
                    "Use status badges to show validation status"
                ]
            }
        elif "matrix strategy" in query.lower():
            return {
                "key_findings": [
                    "Matrix builds test across multiple configurations",
                    "Common dimensions: Python version, OS, dependencies",
                    "Fast-fail option stops all jobs on first failure",
                    "Max-parallel limits concurrent jobs",
                    "Include/exclude specific combinations"
                ],
                "best_practices": [
                    "Test minimum and maximum supported Python versions",
                    "Include at least one Windows build for compatibility",
                    "Use fail-fast for early problem detection",
                    "Cache dependencies per matrix combination",
                    "Limit matrix size to essential combinations"
                ]
            }
        return {"key_findings": [], "best_practices": []}

    def _simulate_code_samples_search(
        self,
        query: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Simulate code samples search results"""
        if "github actions" in query.lower() and language == "yaml":
            return {
                "sample_count": 3,
                "samples": [
                    {
                        "title": "Python CI Workflow",
                        "language": "yaml",
                        "code": """name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    - run: pip install -r requirements.txt
    - run: pytest --cov --cov-report=xml
    - uses: codecov/codecov-action@v3"""
                    },
                    {
                        "title": "Database Validation Workflow",
                        "language": "yaml",
                        "code": """name: Database Validation

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -e .
    - name: Run validation swarm
      run: python -m cf_core.validation.flow_orchestrator
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: validation-reports
        path: validation_reports/"""
                    }
                ]
            }
        elif "database testing" in query.lower() and language == "python":
            return {
                "sample_count": 2,
                "samples": [
                    {
                        "title": "SQLite Test Fixture",
                        "language": "python",
                        "code": """import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    # Setup database schema
    setup_schema(db_path)

    yield str(db_path)

    # Cleanup
    db_path.unlink(missing_ok=True)"""
                    }
                ]
            }
        return {"sample_count": 0, "samples": []}

    def _simulate_synthesis(
        self,
        topic: str,
        docs_result: Dict[str, Any],
        samples_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate synthesis of research findings"""
        return {
            "summary": f"Comprehensive research on {topic} reveals modern best practices and implementation patterns",
            "key_takeaways": docs_result.get("key_findings", [])[:3],
            "recommended_patterns": docs_result.get("best_practices", [])[:3],
            "implementation_notes": [
                "Follow industry-standard patterns",
                "Prioritize developer experience",
                "Optimize for CI execution time"
            ]
        }

    async def _synthesize_findings(
        self,
        research_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize findings across all research topics

        Args:
            research_results: Research results

        Returns:
            Synthesized findings
        """
        # Collect all best practices
        all_best_practices = []
        for result in research_results:
            docs = result.get("documentation_findings", {})
            practices = docs.get("best_practices", [])
            all_best_practices.extend(practices)

        # Identify cross-cutting concerns
        cross_cutting = {
            "performance": [
                "Cache dependencies",
                "Parallel execution",
                "Fail-fast approach"
            ],
            "reliability": [
                "Database fixtures",
                "Test isolation",
                "Artifact storage"
            ],
            "maintainability": [
                "Pin action versions",
                "Clear failure messages",
                "Version-controlled configs"
            ],
            "security": [
                "Secrets management",
                "Branch protection",
                "Status checks enforcement"
            ]
        }

        # Prioritize recommendations
        prioritized_recommendations = [
            {
                "priority": "HIGH",
                "category": "CI Configuration",
                "recommendation": "Implement GitHub Actions workflow with matrix strategy",
                "rationale": "Essential for testing across Python versions",
                "effort": "2 hours"
            },
            {
                "priority": "HIGH",
                "category": "Validation Integration",
                "recommendation": "Add validation swarm as required status check",
                "rationale": "Prevents merging code with data integrity issues",
                "effort": "3 hours"
            },
            {
                "priority": "MEDIUM",
                "category": "Database Testing",
                "recommendation": "Create SQLite test fixtures for CI",
                "rationale": "Ensures consistent test environment",
                "effort": "4 hours"
            },
            {
                "priority": "MEDIUM",
                "category": "Artifact Management",
                "recommendation": "Store validation reports as GitHub artifacts",
                "rationale": "Enables debugging failed CI runs",
                "effort": "1 hour"
            }
        ]

        return {
            "topics_synthesized": len(research_results),
            "total_best_practices": len(all_best_practices),
            "cross_cutting_concerns": cross_cutting,
            "prioritized_recommendations": prioritized_recommendations
        }

    def _generate_integration_strategy(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate CI/CD integration strategy

        Args:
            synthesis: Synthesized findings

        Returns:
            Integration strategy
        """
        return {
            "approach": "Progressive Integration",
            "phases": [
                {
                    "phase": 1,
                    "name": "Basic CI Workflow",
                    "duration": "1 day",
                    "objectives": [
                        "Create .github/workflows/validation.yml",
                        "Run validation swarm on push/PR",
                        "Report status to GitHub checks"
                    ],
                    "deliverables": [
                        "GitHub Actions workflow file",
                        "CI documentation"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Matrix Testing",
                    "duration": "1 day",
                    "objectives": [
                        "Test across Python 3.10, 3.11, 3.12",
                        "Add Linux and Windows runners",
                        "Implement dependency caching"
                    ],
                    "deliverables": [
                        "Matrix strategy configuration",
                        "Cached workflow execution"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Quality Gates",
                    "duration": "2 days",
                    "objectives": [
                        "Enable branch protection rules",
                        "Require validation checks before merge",
                        "Add status badges to README"
                    ],
                    "deliverables": [
                        "Branch protection configuration",
                        "Status badges"
                    ]
                },
                {
                    "phase": 4,
                    "name": "Advanced Integration",
                    "duration": "2 days",
                    "objectives": [
                        "Store validation reports as artifacts",
                        "Add performance benchmarking",
                        "Implement failure notifications"
                    ],
                    "deliverables": [
                        "Artifact storage",
                        "Performance tracking",
                        "Notification system"
                    ]
                }
            ],
            "total_duration": "6 days",
            "recommended_tools": [
                "GitHub Actions",
                "pytest with coverage",
                "SQLite for test database",
                "GitHub artifacts for reports"
            ],
            "success_metrics": [
                "All PRs pass validation before merge",
                "< 5 minute CI execution time",
                "100% validation coverage",
                "Zero false positives in 30 days"
            ]
        }

    def _create_workflow_examples(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create workflow examples based on integration strategy

        Args:
            strategy: Integration strategy

        Returns:
            Workflow examples
        """
        return {
            "basic_workflow": {
                "filename": ".github/workflows/validation.yml",
                "content": """name: Database Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .

    - name: Run validation swarm
      run: |
        python -m cf_core.validation.flow_orchestrator

    - name: Upload validation reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: validation-reports
        path: validation_reports/

    - name: Check validation status
      run: |
        python -c "import json; r=json.load(open('validation_reports/latest.json')); exit(0 if r['validation_summary']['passed'] else 1)"
"""
            },
            "matrix_workflow": {
                "filename": ".github/workflows/validation-matrix.yml",
                "content": """name: Database Validation (Matrix)

on: [push, pull_request]

jobs:
  validate:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .

    - name: Run validation swarm
      run: python -m cf_core.validation.flow_orchestrator

    - name: Upload reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: validation-${{ matrix.os }}-py${{ matrix.python-version }}
        path: validation_reports/
"""
            },
            "scheduled_workflow": {
                "filename": ".github/workflows/nightly-validation.yml",
                "content": """name: Nightly Validation

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  full-validation:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .

    - name: Run comprehensive validation
      run: |
        python -m cf_core.validation.flow_orchestrator --scope comprehensive

    - name: Generate validation report
      if: always()
      run: |
        python scripts/generate_validation_report.py

    - name: Upload comprehensive report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: nightly-validation-report
        path: |
          validation_reports/
          reports/

    - name: Notify on failure
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: 'Nightly validation failed',
            body: 'The nightly validation run failed. Check the workflow logs for details.',
            labels: ['validation', 'automated']
          })
"""
            }
        }

    def _record_findings_from_research(
        self,
        research_results: List[Dict[str, Any]],
        synthesis: Dict[str, Any],
        strategy: Dict[str, Any]
    ):
        """Record findings from research"""
        # Record research count
        self._record_finding(
            category="research_completed",
            finding=f"Researched {len(research_results)} CI/CD integration topics",
            severity="info",
            metadata={
                'topics': [r['topic'] for r in research_results],
                'total_best_practices': synthesis.get('total_best_practices', 0)
            }
        )

        # Record cross-cutting concerns
        for concern, items in synthesis.get('cross_cutting_concerns', {}).items():
            self._record_finding(
                category="cross_cutting_concern",
                finding=f"Identified {concern} concerns in CI/CD integration",
                severity="info",
                metadata={'concern': concern, 'items': items}
            )

        # Record recommendations
        for rec in synthesis.get('prioritized_recommendations', []):
            self._record_finding(
                category="integration_recommendation",
                finding=f"{rec['priority']} priority: {rec['recommendation']}",
                severity="warning" if rec['priority'] == 'HIGH' else "info",
                metadata=rec
            )

        # Record strategy phases
        self._record_finding(
            category="integration_strategy",
            finding=f"Generated {len(strategy['phases'])}-phase integration strategy ({strategy['total_duration']})",
            severity="info",
            metadata={
                'phases': [p['name'] for p in strategy['phases']],
                'total_duration': strategy['total_duration']
            }
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
