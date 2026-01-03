# CF_CORE Validation Module

Multi-agent validation swarm for comprehensive testing of task management workflows.

## Overview

The validation module provides a sophisticated agent-based system for validating all aspects of the CF_CORE task management system, including CRUD operations, state transitions, data integrity, relationships, performance, and audit trails.

## Architecture

### Agent Swarm Design

The validation system uses a **multi-agent swarm** architecture where specialized agents work independently or in coordination:

```
Orchestrator
    ├── Phase 1: Data Integrity (blocking)
    ├── Phase 2: Core Validators (parallel)
    │   ├── CRUD Validator
    │   ├── State Transition Validator
    │   ├── Relationship Validator
    │   └── Audit Trail Validator
    └── Phase 3: Performance (optional)
```

### Validation Agents

1. **CRUDValidatorAgent**: Tests Create, Read, Update, Delete operations
2. **StateTransitionValidatorAgent**: Validates task lifecycle state machine
3. **DataIntegrityValidatorAgent**: Checks referential integrity and constraints
4. **RelationshipValidatorAgent**: Validates dependencies and relationships
5. **PerformanceValidatorAgent**: Benchmarks operation performance
6. **AuditTrailValidatorAgent**: Verifies evidence logging completeness

## Quick Start

### Command Line Usage

```bash
# Full validation with all agents
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope full \
  --parallel

# Quick validation (no performance tests)
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope quick

# Sprint-scoped validation
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope sprint \
  --sprint-id S-CF-Work-Sprint1

# With performance benchmarks
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope full \
  --performance
```

### Programmatic Usage

```python
from cf_core.validation.orchestrator import ValidationOrchestrator

# Initialize orchestrator
orchestrator = ValidationOrchestrator(
    db_path="db/trackers.sqlite",
    config={
        "scope": "full",
        "parallel": True,
        "include_performance": True,
        "emit_evidence": True
    }
)

# Execute validation swarm
result = orchestrator.execute_swarm()

if result.is_success:
    report = result.value
    print(f"Status: {report['overall_status']}")
    print(f"Success Rate: {report['summary']['success_rate']:.2f}%")

    # Access agent-specific reports
    crud_report = report['agent_reports']['crud']
    integrity_issues = report['agent_reports']['integrity']['issues']
else:
    print(f"Validation failed: {result.error}")
```

## Configuration Options

### Scope

- **`full`**: All validators, comprehensive testing
- **`quick`**: Core validators only, no performance tests
- **`sprint`**: Validate specific sprint (requires `--sprint-id`)
- **`project`**: Validate specific project (requires `--project-id`)

### Execution Mode

- **`--parallel`**: Run independent agents concurrently (default)
- **`--no-parallel`**: Run agents sequentially

### Optional Features

- **`--performance`**: Include performance benchmarks
- **`--emit-evidence`**: Generate evidence files for audit trail (default: true)

## Validation Reports

### Report Structure

```json
{
  "validation_id": "VAL-20251117-001",
  "started_at": "2025-11-17T10:00:00Z",
  "completed_at": "2025-11-17T10:05:23Z",
  "duration_seconds": 323.45,
  "scope": "full",
  "configuration": {
    "parallel": true,
    "include_performance": true,
    "filters": {}
  },
  "agents_executed": 6,
  "agent_reports": {
    "crud": { "total_tests": 20, "passed": 18, "failed": 2, ... },
    "state": { "total_tests": 15, "passed": 15, "failed": 0, ... },
    "integrity": { "issues_found": 5, "critical_count": 1, ... },
    "relationship": { "issues_found": 0, ... },
    "performance": { "total_tests": 5, "passed": 4, "failed": 1, ... },
    "audit": { "total_tests": 8, "passed": 8, "failed": 0, ... }
  },
  "summary": {
    "total_checks": 73,
    "passed": 69,
    "failed": 4,
    "warnings": 5,
    "critical_failures": 1,
    "success_rate": 94.52
  },
  "recommendations": [
    "[CRITICAL] Address 1 critical issues in integrity validator",
    "Fix 2 failed checks in crud validator",
    "Investigate 5 'foreign_key_violation' issues in integrity"
  ],
  "overall_status": "PASSED_WITH_WARNINGS"
}
```

### Status Levels

- **`PASSED`**: All checks passed, no issues
- **`PASSED_WITH_WARNINGS`**: Success rate ≥90%, only warnings
- **`DEGRADED`**: Success rate 70-90%, significant issues
- **`FAILED`**: Success rate <70% or critical failures

### Report Location

Reports are saved to `validation_reports/` directory:

```
validation_reports/
├── validation_VAL-20251117-001.json
├── validation_VAL-20251117-002.json
└── ...
```

## Individual Agent Usage

### CRUD Validator

```python
from cf_core.validation.agents import CRUDValidatorAgent

agent = CRUDValidatorAgent("db/trackers.sqlite")
result = agent.validate()

if result.is_success:
    report = result.value
    print(f"CRUD Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
```

### State Transition Validator

```python
from cf_core.validation.agents import StateTransitionValidatorAgent

agent = StateTransitionValidatorAgent("db/trackers.sqlite")
result = agent.validate()

if result.is_success:
    report = result.value
    # Check state machine validation results
    for test_result in report['test_results']:
        print(f"{test_result['test']}: {'✓' if test_result['passed'] else '✗'}")
```

### Data Integrity Validator

```python
from cf_core.validation.agents import DataIntegrityValidatorAgent

agent = DataIntegrityValidatorAgent("db/trackers.sqlite")
result = agent.validate()

if result.is_success:
    report = result.value
    issues = report['issues']

    # Filter critical issues
    critical = [i for i in issues if i['severity'] == 'critical']
    print(f"Critical Issues: {len(critical)}")

    for issue in critical:
        print(f"  - {issue['description']}")
```

## Integration with dbcli

Add validation commands to `dbcli.py`:

```python
from cf_core.validation.orchestrator import ValidationOrchestrator
from rich.console import Console
from rich.panel import Panel
import typer

validate_app = typer.Typer(help="Validation commands")

@validate_app.command("run")
def validate_workflows(
    scope: str = typer.Option("full", help="Validation scope"),
    sprint_id: str = typer.Option(None, help="Sprint ID"),
    parallel: bool = typer.Option(True, help="Parallel execution"),
    performance: bool = typer.Option(False, help="Include performance"),
    output: str = typer.Option(None, help="Output file")
):
    """Run validation swarm"""
    console = Console()

    config = {
        "scope": scope,
        "parallel": parallel,
        "include_performance": performance,
        "emit_evidence": True,
        "filters": {"sprint_id": sprint_id} if sprint_id else {}
    }

    console.print("[yellow]Starting validation swarm...[/yellow]")

    orchestrator = ValidationOrchestrator("db/trackers.sqlite", config)
    result = orchestrator.execute_swarm()

    if result.is_success:
        report = result.value

        # Display summary
        status_color = {
            "PASSED": "green",
            "PASSED_WITH_WARNINGS": "yellow",
            "DEGRADED": "orange",
            "FAILED": "red"
        }.get(report['overall_status'], "white")

        console.print(Panel(
            f"[{status_color}]{report['overall_status']}[/{status_color}]\n\n"
            f"Success Rate: {report['summary']['success_rate']:.2f}%\n"
            f"Checks: {report['summary']['total_checks']}\n"
            f"Passed: {report['summary']['passed']}\n"
            f"Failed: {report['summary']['failed']}\n"
            f"Warnings: {report['summary']['warnings']}\n"
            f"Critical: {report['summary']['critical_failures']}",
            title=f"Validation Report - {report['validation_id']}"
        ))

        if report['recommendations']:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in report['recommendations'][:5]:
                console.print(f"  • {rec}")
    else:
        console.print(f"[red]Validation failed:[/red] {result.error}")

# Register with main dbcli app
app.add_typer(validate_app, name="validate")
```

### Usage in dbcli

```bash
# Run full validation
dbcli validate run --scope full

# Quick validation
dbcli validate run --scope quick

# Sprint validation
dbcli validate run --scope sprint --sprint-id S-CF-Work-Sprint1

# With performance tests
dbcli validate run --scope full --performance
```

## Extending the Swarm

### Creating Custom Validators

```python
from cf_core.validation.base_agent import BaseValidationAgent
from cf_core.shared.result import Result
from typing import Dict, Any

class CustomValidatorAgent(BaseValidationAgent):
    """Custom validation logic"""

    def validate(self) -> Result[Dict[str, Any]]:
        """Execute custom validation"""
        try:
            # Your validation logic here
            self._test_custom_rules()

            # Generate report
            report = self._generate_report()
            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"Custom validation failed: {e}")

    def _test_custom_rules(self):
        """Implement your test logic"""
        # Example: Check custom business rules
        rows = self._execute_query("SELECT * FROM tasks WHERE ...")

        for row in rows:
            passed = self._check_business_rule(row)
            self._record_test_result(
                test_name="custom_rule",
                passed=passed,
                details="Custom business rule validation"
            )
```

### Registering Custom Validators

```python
from cf_core.validation.orchestrator import ValidationOrchestrator

# Extend orchestrator
class ExtendedOrchestrator(ValidationOrchestrator):
    def _execute_parallel_validation(self):
        """Override to add custom agents"""
        super()._execute_parallel_validation()

        # Add custom validator
        custom_agent = CustomValidatorAgent(self.db_path, self.config)
        result = custom_agent.validate()
        self.results["custom"] = result.value if result.is_success else result.error
```

## Performance Benchmarks

The Performance Validator establishes baseline performance thresholds:

| Operation | Threshold | Purpose |
|-----------|-----------|---------|
| Create 100 tasks | < 5 seconds | Bulk insertion performance |
| List 1000 tasks | < 1 second | Query performance |
| Update task | < 100ms | Single operation latency |
| Filtered query | < 500ms | Index effectiveness |
| Concurrent creates | < 10 seconds | Concurrency handling |

## Evidence and Audit Trail

All validation runs generate evidence files for audit compliance:

```json
{
  "agent": "CRUDValidator",
  "timestamp": "2025-11-17T10:00:00Z",
  "action": "validation_executed",
  "payload": {
    "total_tests": 20,
    "passed": 18,
    "failed": 2,
    "test_results": [...]
  }
}
```

Evidence files are stored in `evidence/` directory.

## Testing the Validators

### Unit Tests

```python
# tests/validation/test_crud_validator.py
import pytest
from cf_core.validation.agents import CRUDValidatorAgent

@pytest.fixture
def test_db(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test.db"
    # Initialize schema
    return str(db_path)

def test_crud_validator_create_operations(test_db):
    agent = CRUDValidatorAgent(test_db)
    result = agent.validate()

    assert result.is_success
    report = result.value
    assert report['total_tests'] > 0
    assert report['passed'] >= 0
```

### Integration Tests

```python
# tests/validation/test_orchestrator.py
import pytest
from cf_core.validation.orchestrator import ValidationOrchestrator

def test_full_validation_swarm(populated_test_db):
    orchestrator = ValidationOrchestrator(
        populated_test_db,
        {"scope": "full", "parallel": False}
    )

    result = orchestrator.execute_swarm()

    assert result.is_success
    report = result.value
    assert report['validation_id'].startswith('VAL-')
    assert report['agents_executed'] >= 5
    assert 'summary' in report
    assert 'recommendations' in report
```

## Troubleshooting

### Common Issues

**Issue**: Agent timeout or hanging

```bash
# Solution: Run sequentially to isolate issue
python -m cf_core.validation.orchestrator --no-parallel
```

**Issue**: Database locked errors

```bash
# Solution: Ensure no other processes accessing database
# Check for lock files
ls -la db/trackers.sqlite*
```

**Issue**: Missing evidence directory

```bash
# Solution: Create directory manually
mkdir -p evidence validation_reports
```

## Continuous Validation

### Scheduled Validation

```bash
# Cron job (daily at 2 AM)
0 2 * * * cd /path/to/project && python -m cf_core.validation.orchestrator --scope full --performance >> /var/log/cf_validation.log 2>&1
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python -m cf_core.validation.orchestrator --scope quick
if [ $? -ne 0 ]; then
    echo "Validation failed - commit aborted"
    exit 1
fi
```

## Future Enhancements

1. **Self-Healing Agents**: Auto-fix detected issues
2. **ML-Based Anomaly Detection**: Detect performance regressions
3. **Real-Time Validation**: Validate on every operation
4. **Web Dashboard**: Real-time validation status UI
5. **Distributed Execution**: Scale across multiple nodes

## References

- [Agent Swarm Architecture](.github/agents/task-workflow-validation-swarm.agent.md)
- [CF_CORE Architecture](../docs/02-Architecture.md)
- [Database Schema](../docs/05-Database-Design-Implementation.md)
- [Result Monad Pattern](../shared/result.py)

## License

Part of the ContextForge project.

---

**Version**: 1.0.0
**Status**: Active Development
**Last Updated**: 2025-11-17
