# Flow-Based Orchestration Guide

**Date**: 2025-11-17
**System**: CF_CORE Validation Agent Swarm
**Orchestration Type**: DAG (Directed Acyclic Graph) Flow Execution

---

## Overview

This guide demonstrates how to use the **Flow-Based Orchestrator** to execute the validation agent swarm using workflow-based coordination with dependency management and phase-based execution.

## Architecture

### Flow Execution Model

The Flow Orchestrator implements a **DAG-based execution engine** where:
- **Agents are nodes** in the dependency graph
- **Dependencies are edges** connecting agents
- **Execution follows topological sort** of the DAG
- **Parallel execution** for independent agents
- **Sequential execution** for dependent agents

### Flow Graph Structure

```
                [Data Integrity]
                      ↓
         ┌────────────┼────────────┬────────┐
         ↓            ↓            ↓        ↓
      [CRUD]      [State]      [Rel]    [Audit]
         └────────────┼────────────┴────────┘
                      ↓
                [Performance]
```

**Execution Order**:
1. Data Integrity (Phase 1 - Blocking)
2. CRUD, State, Relationship, Audit (Phase 2 - Parallel)
3. Performance (Phase 3 - Optional)

### Key Features

1. **Dependency Management**: Agents only execute when dependencies are satisfied
2. **Failure Policies**:
   - Integrity failure → Abort flow
   - Other failures → Continue with remaining agents
3. **Phase-Based Execution**: Logical grouping of agents
4. **Real-Time Monitoring**: Progress updates during execution
5. **Comprehensive Reporting**: Flow-level and agent-level reports

---

## Installation

The flow orchestrator is already integrated into the validation module:

```bash
# Already available at:
cf_core/validation/flow_orchestrator.py
```

---

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Full validation with flow orchestration
python -m cf_core.validation.flow_orchestrator --db-path db/trackers.sqlite

# Quick validation (no performance)
python -m cf_core.validation.flow_orchestrator --db-path db/trackers.sqlite --scope quick

# With performance benchmarks
python -m cf_core.validation.flow_orchestrator --db-path db/trackers.sqlite --performance

# Visualize flow graph
python -m cf_core.validation.flow_orchestrator --visualize
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--db-path` | Path to SQLite database | `db/trackers.sqlite` |
| `--scope` | Validation scope (full, quick) | `full` |
| `--performance` | Include performance tests | `false` |
| `--visualize` | Show flow graph visualization | `false` |

### Programmatic Usage

```python
from cf_core.validation.flow_orchestrator import FlowOrchestrator

# Initialize orchestrator
orchestrator = FlowOrchestrator(
    db_path="db/trackers.sqlite",
    config={
        "scope": "full",
        "include_performance": True,
        "emit_evidence": True
    }
)

# Visualize flow
print(orchestrator.visualize_flow())

# Execute flow
result = orchestrator.execute_flow()

if result.is_success:
    report = result.value

    # Access flow summary
    print(f"Flow ID: {report['flow_id']}")
    print(f"Status: {report['overall_status']}")
    print(f"Duration: {report['duration_seconds']:.2f}s")

    # Access flow execution details
    flow_summary = report['flow_summary']
    print(f"Agents: {flow_summary['completed']}/{flow_summary['total_agents']}")

    # Access agent-specific reports
    for agent_id, agent_report in report['agent_reports'].items():
        print(f"\n{agent_id}: {agent_report['summary']['status']}")
        print(f"  Tests: {agent_report['passed']}/{agent_report['total_tests']}")

    # Access validation metrics
    validation_summary = report['validation_summary']
    print(f"\nOverall Success Rate: {validation_summary['success_rate']:.2f}%")
else:
    print(f"Flow failed: {result.error}")
```

---

## Flow Execution Phases

### Phase 1: Foundation (Critical)

**Agent**: Data Integrity Validator

**Purpose**: Validate database integrity before running other validators

**Failure Policy**: **ABORT** - If integrity fails, stop execution

**Checks**:
- Foreign key constraints
- JSON field validity
- Orphaned records
- Timestamp consistency
- Unique constraints
- Soft delete consistency

**Example Output**:
```
▶️  Data Integrity Validator: RUNNING...
✅  Data Integrity Validator: PASSED (2.34s)
```

### Phase 2: Core Validation (Parallel)

**Agents**: CRUD, State, Relationship, Audit

**Purpose**: Comprehensive validation of all aspects

**Failure Policy**: **CONTINUE** - Continue even if individual agents fail

**Execution**: All four agents run in parallel (independent)

**Example Output**:
```
▶️  CRUD Validator: RUNNING...
▶️  State Transition Validator: RUNNING...
▶️  Relationship Validator: RUNNING...
▶️  Audit Trail Validator: RUNNING...
✅  CRUD Validator: PASSED (5.12s)
✅  State Transition Validator: PASSED (3.45s)
⚠️  Relationship Validator: PASSED_WITH_WARNINGS (2.89s)
✅  Audit Trail Validator: PASSED (1.67s)
```

### Phase 3: Performance (Optional)

**Agent**: Performance Validator

**Purpose**: Benchmark system performance

**Failure Policy**: **WARN** - Log warnings but don't fail flow

**Dependencies**: Waits for all Phase 2 agents to complete

**Example Output**:
```
▶️  Performance Validator: RUNNING...
⚠️  Performance Validator: PASSED_WITH_WARNINGS (15.23s)
```

---

## Dependency Management

### How Dependencies Work

1. **Topological Sort**: Agents are executed in dependency order
2. **Dependency Check**: Before executing, verify all dependencies completed successfully
3. **Blocking**: If dependencies fail, dependent agents are marked as BLOCKED
4. **Parallel Execution**: Independent agents run concurrently

### Dependency Graph Example

```python
# Data Integrity has no dependencies
agents["integrity"] = AgentNode(
    id="integrity",
    dependencies=[]  # Runs first
)

# CRUD depends on integrity
agents["crud"] = AgentNode(
    id="crud",
    dependencies=["integrity"]  # Runs after integrity
)

# Performance depends on all core validators
agents["performance"] = AgentNode(
    id="performance",
    dependencies=["crud", "state", "relationship", "audit"]  # Runs last
)
```

### Handling Dependency Failures

```
Scenario 1: Integrity Fails
  [Integrity] → FAILED
      ↓
  [CRUD, State, Rel, Audit] → BLOCKED (not executed)

Scenario 2: CRUD Fails
  [Integrity] → PASSED
      ↓
  [CRUD] → FAILED
  [State] → PASSED
  [Rel] → PASSED
  [Audit] → PASSED
      ↓
  [Performance] → BLOCKED (depends on all, including CRUD)
```

---

## Flow Reports

### Report Structure

```json
{
  "flow_id": "FLOW-20251117-172830-abc123",
  "flow_type": "validation_swarm",
  "started_at": "2025-11-17T17:28:30Z",
  "completed_at": "2025-11-17T17:33:52Z",
  "duration_seconds": 322.45,

  "configuration": {
    "scope": "full",
    "include_performance": true,
    "emit_evidence": true
  },

  "flow_summary": {
    "total_agents": 6,
    "completed": 5,
    "failed": 1,
    "blocked": 0,
    "total_duration": 322.45,
    "agent_durations": {
      "integrity": 2.34,
      "crud": 5.12,
      "state": 3.45,
      "relationship": 2.89,
      "audit": 1.67,
      "performance": 15.23
    }
  },

  "agent_reports": {
    "integrity": { "total_tests": 50, "passed": 48, "failed": 2, ... },
    "crud": { "total_tests": 20, "passed": 18, "failed": 2, ... },
    ...
  },

  "validation_summary": {
    "total_checks": 158,
    "passed": 151,
    "failed": 7,
    "warnings": 12,
    "critical_failures": 0,
    "success_rate": 95.57
  },

  "overall_status": "PASSED_WITH_WARNINGS",

  "recommendations": [
    "Address critical issues in crud validator",
    "Investigate 5 'foreign_key_violation' issues in integrity"
  ]
}
```

### Report Location

```
validation_reports/
├── flow_FLOW-20251117-172830-abc123.json
└── ...
```

---

## Comparison: Flow vs Standard Orchestrator

### Flow Orchestrator

**Pros**:
- ✅ DAG-based dependency management
- ✅ Visual flow representation
- ✅ Phase-based execution
- ✅ Detailed flow metrics (agent durations, execution order)
- ✅ Topological sort for optimal execution
- ✅ Blocking/skipping based on dependencies

**Cons**:
- ❌ Slightly more complex setup
- ❌ Additional abstraction layer

**Best For**:
- Complex workflows with dependencies
- CI/CD pipelines
- Debugging execution flow
- Understanding agent relationships

### Standard Orchestrator

**Pros**:
- ✅ Simpler implementation
- ✅ Direct ThreadPoolExecutor usage
- ✅ Easier to understand

**Cons**:
- ❌ Less sophisticated dependency management
- ❌ No visual representation
- ❌ Less detailed flow metrics

**Best For**:
- Quick validation runs
- Simple parallel execution
- Minimal overhead

---

## Integration with dbcli

Add flow orchestration to `dbcli.py`:

```python
from cf_core.validation.flow_orchestrator import FlowOrchestrator
from rich.console import Console
from rich.panel import Panel
import typer

validate_app = typer.Typer(help="Validation commands")

@validate_app.command("flow")
def validate_flow(
    scope: str = typer.Option("full", help="Validation scope"),
    performance: bool = typer.Option(False, help="Include performance"),
    visualize: bool = typer.Option(False, help="Show flow graph")
):
    """Run flow-based validation"""
    console = Console()

    config = {
        "scope": scope,
        "include_performance": performance,
        "emit_evidence": True
    }

    orchestrator = FlowOrchestrator("db/trackers.sqlite", config)

    if visualize:
        console.print(orchestrator.visualize_flow())
        return

    console.print("[yellow]Executing validation flow...[/yellow]\n")

    result = orchestrator.execute_flow()

    if result.is_success:
        report = result.value

        status_color = {
            "PASSED": "green",
            "PASSED_WITH_WARNINGS": "yellow",
            "DEGRADED": "orange",
            "FAILED": "red"
        }.get(report['overall_status'], "white")

        console.print(Panel(
            f"[{status_color}]{report['overall_status']}[/{status_color}]\n\n"
            f"Flow ID: {report['flow_id']}\n"
            f"Duration: {report['duration_seconds']:.2f}s\n"
            f"Agents: {report['flow_summary']['completed']}/{report['flow_summary']['total_agents']}\n\n"
            f"Success Rate: {report['validation_summary']['success_rate']:.2f}%\n"
            f"Checks: {report['validation_summary']['passed']}/{report['validation_summary']['total_checks']}",
            title="Flow Validation Report"
        ))
    else:
        console.print(f"[red]Flow failed:[/red] {result.error}")

app.add_typer(validate_app, name="validate")
```

### Usage in dbcli

```bash
# Run flow validation
dbcli validate flow --scope full

# With performance
dbcli validate flow --scope full --performance

# Visualize flow
dbcli validate flow --visualize
```

---

## Advanced Features

### Custom Agent Addition

```python
from cf_core.validation.flow_orchestrator import FlowOrchestrator, AgentNode
from cf_core.validation.base_agent import BaseValidationAgent

# Create custom validator
class CustomValidator(BaseValidationAgent):
    def validate(self):
        # Your validation logic
        return Result.success({"custom": "report"})

# Extend orchestrator
class CustomOrchestrator(FlowOrchestrator):
    def _build_flow_graph(self):
        super()._build_flow_graph()

        # Add custom agent
        self.agents["custom"] = AgentNode(
            id="custom",
            name="Custom Validator",
            agent_class=CustomValidator,
            dependencies=["integrity"]  # Run after integrity
        )
```

### Flow Monitoring

```python
# Monitor flow in real-time
orchestrator = FlowOrchestrator("db/trackers.sqlite")

# Execute with callbacks
result = orchestrator.execute_flow()

# Access agent statuses
for agent_id, agent in orchestrator.agents.items():
    print(f"{agent_id}: {agent.status.value} ({agent.duration}s)")
```

---

## Troubleshooting

### Issue: Agent Blocked

**Symptom**: Agent shows `BLOCKED` status

**Cause**: Dependencies failed or didn't complete

**Solution**:
```bash
# Check which dependencies failed
python -m cf_core.validation.flow_orchestrator --db-path db/trackers.sqlite

# Review flow report for dependency chain
cat validation_reports/flow_FLOW-*.json | jq '.flow_summary'
```

### Issue: Circular Dependencies

**Symptom**: `ValueError: Cycle detected in agent dependency graph`

**Cause**: Agent A depends on B, B depends on A

**Solution**: Review and fix dependency definitions in `_build_flow_graph()`

### Issue: Performance Degradation

**Symptom**: Flow takes longer than expected

**Solution**:
```bash
# Check agent durations in report
cat validation_reports/flow_FLOW-*.json | jq '.flow_summary.agent_durations'

# Identify slow agents and optimize
```

---

## Best Practices

1. **Define Clear Dependencies**: Only specify necessary dependencies
2. **Use Phases Logically**: Group related agents in phases
3. **Set Appropriate Failure Policies**: Critical → abort, others → continue
4. **Monitor Flow Execution**: Review flow reports regularly
5. **Optimize Agent Duration**: Keep agents focused and fast
6. **Test Dependency Graph**: Visualize before executing
7. **Handle Failures Gracefully**: Implement proper error handling

---

## Examples

### Example 1: Full Flow Validation

```bash
python -m cf_core.validation.flow_orchestrator \
  --db-path db/trackers.sqlite \
  --scope full \
  --performance
```

**Output**:
```
============================================================
Flow Orchestrator - Validation Swarm
Flow ID: FLOW-20251117-172830-abc123
============================================================

Execution Order: integrity → crud → state → relationship → audit → performance

▶️  Data Integrity Validator: RUNNING...
✅  Data Integrity Validator: PASSED (2.34s)
▶️  CRUD Validator: RUNNING...
▶️  State Transition Validator: RUNNING...
▶️  Relationship Validator: RUNNING...
▶️  Audit Trail Validator: RUNNING...
✅  CRUD Validator: PASSED (5.12s)
✅  State Transition Validator: PASSED (3.45s)
✅  Relationship Validator: PASSED (2.89s)
✅  Audit Trail Validator: PASSED (1.67s)
▶️  Performance Validator: RUNNING...
⚠️  Performance Validator: PASSED_WITH_WARNINGS (15.23s)

============================================================
Flow Execution Complete
Overall Status: PASSED_WITH_WARNINGS
Duration: 30.70s
============================================================

Flow report saved to: validation_reports/flow_FLOW-20251117-172830-abc123.json
```

### Example 2: Quick Validation

```bash
python -m cf_core.validation.flow_orchestrator --scope quick
```

**Output**: Same as above but without performance validator

### Example 3: Visualize Flow

```bash
python -m cf_core.validation.flow_orchestrator --visualize
```

**Output**:
```
Flow Dependency Graph:

  [Data Integrity]
         |
    ┌────┴────┬────────┬────────┐
    |         |        |        |
[CRUD]  [State] [Rel]  [Audit]
    |         |        |        |
    └─────────┴────────┴────────┘
              |
       [Performance]
```

---

## Summary

The Flow-Based Orchestrator provides:

✅ **DAG-based execution** with dependency management
✅ **Phase-based coordination** for logical grouping
✅ **Real-time monitoring** with progress updates
✅ **Comprehensive reporting** at flow and agent levels
✅ **Failure policies** for graceful error handling
✅ **Visual representation** of flow structure
✅ **Topological execution** for optimal ordering
✅ **Parallel & sequential** execution modes

**Use when**: You need sophisticated workflow orchestration with dependency management and detailed flow analytics.

---

**Document Version**: 1.0.0
**Created**: 2025-11-17
**Status**: Production Ready
