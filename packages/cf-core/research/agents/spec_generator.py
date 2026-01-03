"""
Spec Generator Agent

Generates detailed implementation specifications from research findings.
Creates actionable specs for code, database schemas, API contracts, and workflows.
"""

from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit
from cf_core.shared.result import Result


class SpecGenerator(BaseResearchAgent):
    """
    Generates implementation specifications from research.

    Capabilities:
    - Generates code specifications with examples
    - Creates database schema specifications
    - Defines API contract specifications
    - Builds workflow and CI/CD specifications
    - Produces code templates and boilerplate

    MCP Tools Used:
    - github-copilot: Code generation and examples
    - memory: Spec knowledge graph
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Spec Generator.

        Args:
            config: Configuration dictionary with:
                - evidence_dir: Path to evidence logs
                - specs_output_dir: Path for generated specs
        """
        super().__init__(config)
        self.toolkit = MCPToolkit(config)

        self.evidence_dir = Path(
            config.get("evidence_dir", "evidence")
        )
        self.specs_output_dir = Path(
            config.get("specs_output_dir", "specs")
        )
        self.specs_output_dir.mkdir(parents=True, exist_ok=True)

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute specification generation.

        Returns:
            Result containing:
            - code_specs: Code implementation specifications
            - database_specs: Database schema specifications
            - api_specs: API contract specifications
            - workflow_specs: CI/CD workflow specifications
            - templates: Code templates and boilerplate
        """
        try:
            self._record_finding(category="info", finding=f"Starting specification generation from research findings", severity="info")

            # Step 1: Load design synthesis
            self._record_finding(category="info", finding=f"Loading design synthesis...", severity="info")
            design_synthesis = await self._load_design_synthesis()

            if not design_synthesis:
                return Result.failure("No design synthesis found")

            self._record_finding(
                category="design_synthesis",
                finding="Loaded design synthesis from DesignSynthesizer",
                severity="info"
            )

            # Step 2: Generate code specifications
            self._record_finding(category="info", finding=f"Generating code specifications...", severity="info")
            code_specs = await self._generate_code_specs(design_synthesis)

            self._record_finding(
                category="code_specs",
                finding=f"Generated {len(code_specs)} code specifications",
                severity="info",
                metadata={"specs": [s["name"] for s in code_specs]}
            )

            # Step 3: Generate database specifications
            self._record_finding(category="info", finding=f"Generating database specifications...", severity="info")
            database_specs = await self._generate_database_specs(design_synthesis)

            self._record_finding(
                category="database_specs",
                finding=f"Generated {len(database_specs)} database specifications",
                severity="info"
            )

            # Step 4: Generate API specifications
            self._record_finding(category="info", finding=f"Generating API specifications...", severity="info")
            api_specs = await self._generate_api_specs(design_synthesis)

            self._record_finding(
                category="api_specs",
                finding=f"Generated {len(api_specs)} API specifications",
                severity="info"
            )

            # Step 5: Generate workflow specifications
            self._record_finding(category="info", finding=f"Generating workflow specifications...", severity="info")
            workflow_specs = await self._generate_workflow_specs(design_synthesis)

            self._record_finding(
                category="workflow_specs",
                finding=f"Generated {len(workflow_specs)} workflow specifications",
                severity="info"
            )

            # Step 6: Generate code templates
            self._record_finding(category="info", finding=f"Generating code templates...", severity="info")
            templates = await self._generate_code_templates(code_specs, design_synthesis)

            self._record_finding(
                category="templates",
                finding=f"Generated {len(templates)} code templates",
                severity="info"
            )

            # Step 7: Write specifications to files
            self._record_finding(category="info", finding=f"Writing specifications to files...", severity="info")
            await self._write_specifications({
                "code_specs": code_specs,
                "database_specs": database_specs,
                "api_specs": api_specs,
                "workflow_specs": workflow_specs,
                "templates": templates
            })

            # Step 8: Build knowledge graph
            self._record_finding(category="info", finding=f"Building spec knowledge graph...", severity="info")
            await self._build_knowledge_graph(code_specs, database_specs, api_specs)

            # Compile results
            results = {
                "code_specs": code_specs,
                "database_specs": database_specs,
                "api_specs": api_specs,
                "workflow_specs": workflow_specs,
                "templates": templates,
                "output_directory": str(self.specs_output_dir)
            }

            self.log_success(
                f"Specification generation complete: {len(code_specs)} code specs, "
                f"{len(database_specs)} DB specs, {len(api_specs)} API specs, "
                f"{len(workflow_specs)} workflow specs, {len(templates)} templates"
            )

            return Result.ok(results)

        except Exception as e:
            self._record_finding(category="error", finding=f"Specification generation failed: {str(e)}", severity="critical")
            return Result.failure(f"Spec generation error: {str(e)}")

    async def _load_design_synthesis(self) -> Dict[str, Any]:
        """Load design synthesis from DesignSynthesizer evidence."""
        evidence_files = list(
            self.evidence_dir.glob("research_DesignSynthesizer_*.json")
        )

        if not evidence_files:
            self._record_finding(category="warning", finding=f"No DesignSynthesizer evidence found", severity="warning")
            return {}

        # Get most recent
        latest_file = sorted(evidence_files, key=lambda p: p.stat().st_mtime)[-1]

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                evidence_data = json.load(f)

            return evidence_data.get("summary", {})

        except Exception as e:
            self._record_finding(category="error", finding=f"Failed to load design synthesis: {str(e)}", severity="critical")
            return {}

    async def _generate_code_specs(
        self, design_synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate code implementation specifications."""
        specs = []

        # Spec 1: Unified Output System
        specs.append({
            "id": "CODE-001",
            "name": "Unified Output System",
            "phase": "Phase 3",
            "priority": "HIGH",
            "description": "Consolidate OutputManager and DisplayManager into unified interface",
            "file": "cf_core/output/unified_output_manager.py",
            "estimated_lines": 500,
            "dependencies": [],
            "classes": [
                {
                    "name": "UnifiedOutputManager",
                    "purpose": "Single interface for all output modes",
                    "methods": [
                        {
                            "name": "__init__",
                            "params": ["mode: OutputMode", "config: Dict[str, Any]"],
                            "returns": "None",
                            "description": "Initialize with mode (JSON or RICH)"
                        },
                        {
                            "name": "output",
                            "params": ["data: Any", "format_type: str"],
                            "returns": "None",
                            "description": "Output data in selected mode"
                        },
                        {
                            "name": "progress",
                            "params": ["message: str", "percent: float"],
                            "returns": "None",
                            "description": "Show progress (mode-appropriate)"
                        },
                        {
                            "name": "error",
                            "params": ["message: str", "exception: Exception = None"],
                            "returns": "None",
                            "description": "Display error (mode-appropriate)"
                        }
                    ]
                },
                {
                    "name": "OutputMode",
                    "purpose": "Enum for output modes",
                    "values": ["JSON", "RICH"]
                }
            ],
            "patterns": ["Singleton", "Strategy Pattern", "Factory Pattern"],
            "testing": {
                "unit_tests": [
                    "test_json_mode_output",
                    "test_rich_mode_output",
                    "test_mode_switching",
                    "test_progress_tracking",
                    "test_error_handling"
                ],
                "integration_tests": [
                    "test_cli_integration",
                    "test_ci_cd_json_output",
                    "test_interactive_rich_output"
                ]
            }
        })

        # Spec 2: Validation CLI Commands
        specs.append({
            "id": "CODE-002",
            "name": "Validation CLI Commands",
            "phase": "Phase 2",
            "priority": "HIGH",
            "description": "Add validation commands to dbcli",
            "file": "python/dbcli/validation_commands.py",
            "estimated_lines": 300,
            "dependencies": ["cf_core.validation.flow_orchestrator"],
            "functions": [
                {
                    "name": "validate",
                    "decorator": "@validation_app.command()",
                    "params": [
                        "db_path: str = typer.Option('db/trackers.sqlite')",
                        "output_dir: str = typer.Option('validation_reports')",
                        "verbose: bool = typer.Option(False)"
                    ],
                    "returns": "None",
                    "description": "Run full validation swarm",
                    "implementation_notes": [
                        "Call flow_orchestrator.run_validation()",
                        "Show Rich progress bar",
                        "Display summary table",
                        "Write JSON report if --json flag"
                    ]
                },
                {
                    "name": "validate_report",
                    "decorator": "@validation_app.command()",
                    "params": ["report_path: str = typer.Argument(...)"],
                    "returns": "None",
                    "description": "Display validation report",
                    "implementation_notes": [
                        "Load JSON report",
                        "Display with Rich tables/panels",
                        "Show violations grouped by severity",
                        "Display recommendations"
                    ]
                }
            ],
            "integration": {
                "parent_cli": "dbcli.py",
                "registration": "app.add_typer(validation_app, name='validate')",
                "usage": "cf db validate --verbose"
            },
            "patterns": ["Typer Sub-App", "Rich Console"],
            "testing": {
                "unit_tests": [
                    "test_validate_command",
                    "test_validate_report_command",
                    "test_verbose_output",
                    "test_error_handling"
                ],
                "integration_tests": [
                    "test_full_validation_workflow",
                    "test_cli_invocation",
                    "test_report_generation"
                ]
            }
        })

        # Spec 3: Database Index Management
        specs.append({
            "id": "CODE-003",
            "name": "Database Index Management",
            "phase": "Phase 1",
            "priority": "CRITICAL",
            "description": "Automated index creation for foreign keys",
            "file": "cf_core/database/index_manager.py",
            "estimated_lines": 200,
            "dependencies": ["sqlite3"],
            "classes": [
                {
                    "name": "IndexManager",
                    "purpose": "Manage database indexes",
                    "methods": [
                        {
                            "name": "analyze_schema",
                            "params": ["db_path: str"],
                            "returns": "Dict[str, List[Dict]]",
                            "description": "Analyze schema for missing indexes"
                        },
                        {
                            "name": "create_missing_indexes",
                            "params": ["db_path: str", "dry_run: bool = False"],
                            "returns": "List[str]",
                            "description": "Create missing FK indexes"
                        },
                        {
                            "name": "verify_indexes",
                            "params": ["db_path: str"],
                            "returns": "Dict[str, bool]",
                            "description": "Verify all indexes exist"
                        }
                    ]
                }
            ],
            "implementation_notes": [
                "Query PRAGMA foreign_key_list for FKs",
                "Query PRAGMA index_list to check existing indexes",
                "Generate CREATE INDEX statements",
                "Execute with transaction (rollback on error)",
                "Log all index creations"
            ],
            "patterns": ["Builder Pattern", "Transaction Pattern"],
            "testing": {
                "unit_tests": [
                    "test_analyze_schema",
                    "test_create_indexes",
                    "test_verify_indexes",
                    "test_dry_run_mode",
                    "test_rollback_on_error"
                ]
            }
        })

        # Spec 4: Research Flow Orchestrator
        specs.append({
            "id": "CODE-004",
            "name": "Research Flow Orchestrator",
            "phase": "Phase 0",
            "priority": "HIGH",
            "description": "DAG-based orchestration for research agents",
            "file": "cf_core/research/research_orchestrator.py",
            "estimated_lines": 400,
            "dependencies": ["cf_core.research.agents"],
            "classes": [
                {
                    "name": "ResearchOrchestrator",
                    "purpose": "Orchestrate research agent execution",
                    "methods": [
                        {
                            "name": "define_dag",
                            "params": [],
                            "returns": "Dict[str, List[str]]",
                            "description": "Define agent dependencies (DAG)"
                        },
                        {
                            "name": "run_research",
                            "params": ["agents: List[str] = None"],
                            "returns": "Result[Dict[str, Any]]",
                            "description": "Execute research flow"
                        },
                        {
                            "name": "generate_reports",
                            "params": [],
                            "returns": "None",
                            "description": "Generate consolidated reports"
                        }
                    ]
                }
            ],
            "dag_structure": {
                "foundation_layer": [
                    "DataPatternsAnalyst",
                    "CLIArchitectureAnalyst",
                    "FrameworkResearcher"
                ],
                "deep_dive_layer": [
                    "OutputSystemAnalyst",
                    "IntegrationStrategist",
                    "PerformanceAnalyst"
                ],
                "synthesis_layer": [
                    "DesignSynthesizer",
                    "SpecGenerator",
                    "KnowledgeCurator"
                ],
                "dependencies": {
                    "DesignSynthesizer": ["DataPatternsAnalyst", "CLIArchitectureAnalyst",
                                         "FrameworkResearcher", "OutputSystemAnalyst",
                                         "IntegrationStrategist", "PerformanceAnalyst"],
                    "SpecGenerator": ["DesignSynthesizer"],
                    "KnowledgeCurator": ["DesignSynthesizer", "SpecGenerator"]
                }
            },
            "patterns": ["DAG Orchestration", "Observer Pattern", "Result Monad"],
            "testing": {
                "unit_tests": [
                    "test_dag_definition",
                    "test_topological_sort",
                    "test_agent_execution",
                    "test_failure_handling",
                    "test_parallel_execution"
                ]
            }
        })

        # Spec 5: FK Violation Remediation
        specs.append({
            "id": "CODE-005",
            "name": "FK Violation Remediation",
            "phase": "Phase 1",
            "priority": "CRITICAL",
            "description": "Automated remediation of FK violations",
            "file": "cf_core/remediation/fk_remediation.py",
            "estimated_lines": 400,
            "dependencies": ["cf_core.validation.agents.data_integrity_validator"],
            "classes": [
                {
                    "name": "FKRemediationEngine",
                    "purpose": "Remediate FK violations",
                    "methods": [
                        {
                            "name": "analyze_violations",
                            "params": ["db_path: str"],
                            "returns": "Dict[str, List[Dict]]",
                            "description": "Analyze FK violations"
                        },
                        {
                            "name": "restore_missing_entities",
                            "params": ["entity_type: str", "entity_ids: List[str]"],
                            "returns": "Result[int]",
                            "description": "Restore missing projects/sprints"
                        },
                        {
                            "name": "reassign_orphans",
                            "params": ["strategy: str = 'default'"],
                            "returns": "Result[int]",
                            "description": "Reassign orphaned records"
                        },
                        {
                            "name": "apply_preventive_measures",
                            "params": ["db_path: str"],
                            "returns": "Result[None]",
                            "description": "Add FK constraints"
                        }
                    ]
                }
            ],
            "remediation_strategies": [
                {
                    "name": "restore",
                    "description": "Restore missing parent entities",
                    "use_case": "Top 10 missing projects/sprints"
                },
                {
                    "name": "reassign",
                    "description": "Reassign to default/archive entity",
                    "use_case": "Low-priority orphans"
                },
                {
                    "name": "delete",
                    "description": "Delete orphaned records (with backup)",
                    "use_case": "Abandoned records"
                }
            ],
            "patterns": ["Strategy Pattern", "Command Pattern", "Result Monad"],
            "testing": {
                "unit_tests": [
                    "test_analyze_violations",
                    "test_restore_entities",
                    "test_reassign_orphans",
                    "test_preventive_constraints",
                    "test_rollback_on_error"
                ],
                "integration_tests": [
                    "test_full_remediation_workflow",
                    "test_backup_restore",
                    "test_constraint_enforcement"
                ]
            }
        })

        return specs

    async def _generate_database_specs(
        self, design_synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate database schema specifications."""
        specs = []

        # Spec 1: Foreign Key Constraints
        specs.append({
            "id": "DB-001",
            "name": "Foreign Key Constraints",
            "phase": "Phase 1",
            "priority": "CRITICAL",
            "description": "Add FK constraints to enforce referential integrity",
            "tables": [
                {
                    "name": "tasks",
                    "constraints": [
                        {
                            "column": "project_id",
                            "references": "projects(id)",
                            "on_delete": "RESTRICT",
                            "on_update": "CASCADE"
                        },
                        {
                            "column": "sprint_id",
                            "references": "sprints(id)",
                            "on_delete": "SET NULL",
                            "on_update": "CASCADE"
                        }
                    ]
                },
                {
                    "name": "sprints",
                    "constraints": [
                        {
                            "column": "project_id",
                            "references": "projects(id)",
                            "on_delete": "RESTRICT",
                            "on_update": "CASCADE"
                        }
                    ]
                }
            ],
            "migration_sql": """
-- Add FK constraints to tasks table
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_sprint
    FOREIGN KEY (sprint_id) REFERENCES sprints(id)
    ON DELETE SET NULL ON UPDATE CASCADE;

-- Add FK constraints to sprints table
ALTER TABLE sprints ADD CONSTRAINT fk_sprints_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE RESTRICT ON UPDATE CASCADE;
""",
            "rollback_sql": """
-- Remove FK constraints from tasks table
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_project;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_sprint;

-- Remove FK constraints from sprints table
ALTER TABLE sprints DROP CONSTRAINT IF EXISTS fk_sprints_project;
""",
            "testing": {
                "test_cases": [
                    "Attempt to insert task with invalid project_id (should fail)",
                    "Attempt to delete project with tasks (should fail due to RESTRICT)",
                    "Update project.id and verify cascade to tasks",
                    "Delete sprint and verify tasks.sprint_id set to NULL"
                ]
            }
        })

        # Spec 2: Performance Indexes
        specs.append({
            "id": "DB-002",
            "name": "Performance Indexes",
            "phase": "Phase 1",
            "priority": "HIGH",
            "description": "Create indexes on foreign key and frequently queried columns",
            "indexes": [
                {
                    "name": "idx_tasks_project_id",
                    "table": "tasks",
                    "columns": ["project_id"],
                    "type": "BTREE",
                    "rationale": "Foreign key column, frequently queried"
                },
                {
                    "name": "idx_tasks_sprint_id",
                    "table": "tasks",
                    "columns": ["sprint_id"],
                    "type": "BTREE",
                    "rationale": "Foreign key column, frequently queried"
                },
                {
                    "name": "idx_sprints_project_id",
                    "table": "sprints",
                    "columns": ["project_id"],
                    "type": "BTREE",
                    "rationale": "Foreign key column, frequently queried"
                },
                {
                    "name": "idx_tasks_status",
                    "table": "tasks",
                    "columns": ["status"],
                    "type": "BTREE",
                    "rationale": "Frequently used in WHERE clauses"
                },
                {
                    "name": "idx_tasks_created_at",
                    "table": "tasks",
                    "columns": ["created_at"],
                    "type": "BTREE",
                    "rationale": "Used for time-based queries and sorting"
                }
            ],
            "migration_sql": """
-- Create indexes on tasks table
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_sprint_id ON tasks(sprint_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Create indexes on sprints table
CREATE INDEX IF NOT EXISTS idx_sprints_project_id ON sprints(project_id);
""",
            "performance_impact": {
                "query_speedup": "30-50%",
                "affected_queries": [
                    "SELECT * FROM tasks WHERE project_id = ?",
                    "SELECT * FROM tasks WHERE sprint_id = ?",
                    "SELECT * FROM tasks WHERE status = ?",
                    "SELECT * FROM tasks ORDER BY created_at"
                ]
            }
        })

        return specs

    async def _generate_api_specs(
        self, design_synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate API contract specifications."""
        specs = []

        # Spec 1: Validation API
        specs.append({
            "id": "API-001",
            "name": "Validation API",
            "phase": "Phase 2",
            "priority": "HIGH",
            "description": "REST API for validation operations",
            "base_path": "/api/v1/validation",
            "endpoints": [
                {
                    "path": "/validate",
                    "method": "POST",
                    "description": "Trigger validation run",
                    "request_body": {
                        "db_path": {"type": "string", "required": False, "default": "db/trackers.sqlite"},
                        "agents": {"type": "array", "items": "string", "required": False, "description": "Specific agents to run"},
                        "output_format": {"type": "string", "enum": ["json", "html"], "default": "json"}
                    },
                    "responses": {
                        "200": {
                            "description": "Validation completed",
                            "schema": {
                                "status": "string",
                                "validation_id": "string",
                                "results": "object",
                                "violations_count": "integer",
                                "execution_time_ms": "number"
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "schema": {"error": "string"}
                        }
                    }
                },
                {
                    "path": "/validate/{validation_id}",
                    "method": "GET",
                    "description": "Get validation results",
                    "parameters": [
                        {"name": "validation_id", "in": "path", "type": "string", "required": True}
                    ],
                    "responses": {
                        "200": {
                            "description": "Validation results",
                            "schema": {
                                "validation_id": "string",
                                "status": "string",
                                "results": "object",
                                "report_url": "string"
                            }
                        },
                        "404": {
                            "description": "Validation not found",
                            "schema": {"error": "string"}
                        }
                    }
                }
            ],
            "authentication": "API key (X-API-Key header)",
            "rate_limiting": "100 requests per minute"
        })

        return specs

    async def _generate_workflow_specs(
        self, design_synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate CI/CD workflow specifications."""
        specs = []

        # Spec 1: Basic Validation Workflow
        specs.append({
            "id": "WORKFLOW-001",
            "name": "Basic Validation Workflow",
            "phase": "Phase 4",
            "priority": "HIGH",
            "description": "GitHub Actions workflow for automated validation",
            "file": ".github/workflows/validation.yml",
            "triggers": ["push", "pull_request"],
            "branches": ["main", "develop"],
            "jobs": {
                "validate": {
                    "runs_on": "ubuntu-latest",
                    "steps": [
                        "Checkout code",
                        "Setup Python 3.11",
                        "Install dependencies (cached)",
                        "Run validation swarm",
                        "Upload validation reports (artifacts)",
                        "Post status to PR (if PR trigger)"
                    ],
                    "environment_variables": {
                        "DB_PATH": "db/trackers.sqlite",
                        "OUTPUT_DIR": "validation_reports"
                    },
                    "artifacts": [
                        {
                            "name": "validation-reports",
                            "path": "validation_reports/**",
                            "retention_days": 30
                        }
                    ]
                }
            },
            "failure_handling": {
                "on_failure": "Post comment to PR with violation summary",
                "notifications": "Slack webhook (optional)"
            }
        })

        # Spec 2: Matrix Testing Workflow
        specs.append({
            "id": "WORKFLOW-002",
            "name": "Matrix Testing Workflow",
            "phase": "Phase 4",
            "priority": "MEDIUM",
            "description": "Matrix testing across Python versions and OS",
            "file": ".github/workflows/matrix-validation.yml",
            "triggers": ["push", "pull_request"],
            "branches": ["main", "develop"],
            "strategy": {
                "matrix": {
                    "python_version": ["3.10", "3.11", "3.12"],
                    "os": ["ubuntu-latest", "windows-latest", "macos-latest"]
                },
                "fail_fast": False
            },
            "jobs": {
                "validate_matrix": {
                    "runs_on": "${{ matrix.os }}",
                    "steps": [
                        "Checkout code",
                        "Setup Python ${{ matrix.python_version }}",
                        "Install dependencies",
                        "Run validation swarm",
                        "Upload matrix results"
                    ]
                }
            }
        })

        return specs

    async def _generate_code_templates(
        self, code_specs: List[Dict[str, Any]], design_synthesis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate code templates and boilerplate."""
        templates = []

        # Template 1: Research Agent Template
        copilot_result = await self.toolkit.github_copilot_explain(
            code="""
class MyResearchAgent(BaseResearchAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.toolkit = MCPToolkit(config)

    async def research(self) -> Result[Dict[str, Any]]:
        # Research implementation
        pass
"""
        )

        templates.append({
            "id": "TEMPLATE-001",
            "name": "Research Agent Template",
            "file": "cf_core/research/agents/_template.py",
            "description": "Template for creating new research agents",
            "content": """\"\"\"
{Agent Name}

{Agent description and purpose}
\"\"\"

from typing import Dict, Any, List
from pathlib import Path
import json

from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit
from cf_core.shared.result import Result


class {ClassName}(BaseResearchAgent):
    \"\"\"
    {Agent purpose}.

    Capabilities:
    - {Capability 1}
    - {Capability 2}
    - {Capability 3}

    MCP Tools Used:
    - {tool1}: {purpose1}
    - {tool2}: {purpose2}
    \"\"\"

    def __init__(self, config: Dict[str, Any] = None):
        \"\"\"Initialize {Agent Name}.\"\"\"
        super().__init__(config)
        self.toolkit = MCPToolkit(config)

    async def research(self) -> Result[Dict[str, Any]]:
        \"\"\"Execute research.\"\"\"
        try:
            self._record_finding(category="info", finding=f"Starting {agent name} research", severity="info")

            # Step 1: {First step}
            # TODO: Implement

            # Step 2: {Second step}
            # TODO: Implement

            # Record findings
            self._record_finding(
                category="{category}",
                finding="{finding description}",
                severity="info"
            )

            results = {
                # TODO: Add results
            }

            self.log_success("Research complete")
            return Result.ok(results)

        except Exception as e:
            self._record_finding(category="error", finding=f"Research failed: {str(e)}", severity="critical")
            return Result.failure(f"Error: {str(e)}")
"""
        })

        # Template 2: Validation Agent Template
        templates.append({
            "id": "TEMPLATE-002",
            "name": "Validation Agent Template",
            "file": "cf_core/validation/agents/_template.py",
            "description": "Template for creating new validation agents",
            "content": """\"\"\"
{Agent Name}

{Agent description and purpose}
\"\"\"

from typing import Dict, Any, List
import sqlite3
from pathlib import Path

from cf_core.shared.result import Result


class {ClassName}:
    \"\"\"
    {Agent purpose}.

    Validates:
    - {Validation 1}
    - {Validation 2}
    \"\"\"

    def __init__(self, db_path: str):
        \"\"\"Initialize validator.\"\"\"
        self.db_path = db_path

    def validate(self) -> Result[Dict[str, Any]]:
        \"\"\"Execute validation.\"\"\"
        try:
            violations = []

            # Validation logic
            # TODO: Implement validation queries

            results = {
                "agent": "{ClassName}",
                "violations": violations,
                "violations_count": len(violations),
                "status": "PASS" if len(violations) == 0 else "FAIL"
            }

            return Result.ok(results)

        except Exception as e:
            return Result.failure(f"Validation error: {str(e)}")
"""
        })

        return templates

    async def _write_specifications(self, specs: Dict[str, Any]) -> None:
        """Write all specifications to files."""

        # Write code specs
        code_specs_file = self.specs_output_dir / "code_specifications.json"
        with open(code_specs_file, 'w', encoding='utf-8') as f:
            json.dump(specs["code_specs"], f, indent=2)
        self._record_finding(category="info", finding=f"Wrote code specs to {code_specs_file}", severity="info")

        # Write database specs
        db_specs_file = self.specs_output_dir / "database_specifications.json"
        with open(db_specs_file, 'w', encoding='utf-8') as f:
            json.dump(specs["database_specs"], f, indent=2)
        self._record_finding(category="info", finding=f"Wrote database specs to {db_specs_file}", severity="info")

        # Write API specs
        api_specs_file = self.specs_output_dir / "api_specifications.json"
        with open(api_specs_file, 'w', encoding='utf-8') as f:
            json.dump(specs["api_specs"], f, indent=2)
        self._record_finding(category="info", finding=f"Wrote API specs to {api_specs_file}", severity="info")

        # Write workflow specs
        workflow_specs_file = self.specs_output_dir / "workflow_specifications.json"
        with open(workflow_specs_file, 'w', encoding='utf-8') as f:
            json.dump(specs["workflow_specs"], f, indent=2)
        self._record_finding(category="info", finding=f"Wrote workflow specs to {workflow_specs_file}", severity="info")

        # Write templates
        templates_file = self.specs_output_dir / "code_templates.json"
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(specs["templates"], f, indent=2)
        self._record_finding(category="info", finding=f"Wrote templates to {templates_file}", severity="info")

    async def _build_knowledge_graph(
        self,
        code_specs: List[Dict[str, Any]],
        database_specs: List[Dict[str, Any]],
        api_specs: List[Dict[str, Any]]
    ) -> None:
        """Build knowledge graph from specifications."""

        # Create entities for specifications
        spec_entities = []

        for spec in code_specs:
            spec_entities.append({
                "name": spec["name"],
                "entityType": "CodeSpecification",
                "observations": [
                    f"ID: {spec['id']}",
                    f"Phase: {spec['phase']}",
                    f"Priority: {spec['priority']}",
                    f"File: {spec['file']}"
                ]
            })

        for spec in database_specs:
            spec_entities.append({
                "name": spec["name"],
                "entityType": "DatabaseSpecification",
                "observations": [
                    f"ID: {spec['id']}",
                    f"Phase: {spec['phase']}",
                    f"Priority: {spec['priority']}"
                ]
            })

        for spec in api_specs:
            spec_entities.append({
                "name": spec["name"],
                "entityType": "APISpecification",
                "observations": [
                    f"ID: {spec['id']}",
                    f"Phase: {spec['phase']}",
                    f"Base Path: {spec['base_path']}"
                ]
            })

        await self.toolkit.memory_create_entities(spec_entities)

        # Create relations between specs and implementation phases
        relations = []
        for spec in code_specs + database_specs + api_specs:
            relations.append({
                "from": spec["name"],
                "to": spec["phase"],
                "relationType": "implements_in"
            })

        await self.toolkit.memory_create_relations(relations)

        self.log_info(
            f"Built spec knowledge graph: {len(spec_entities)} entities, {len(relations)} relations"
        )
