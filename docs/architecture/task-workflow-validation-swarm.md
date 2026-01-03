---
Description: This document defines a multi-agent swarm architecture for comprehensive validation of task management workflows in the CF_CORE system. The swarm consists of specialized agents working in coordination to validate CRUD operations, state transitions, data integrity, performance, and audit compliance.
---

## Swarm Architecture

### Design Principles

1. **Separation of Concerns**: Each agent specializes in one validation domain
2. **Result Monad Pattern**: All agents return Result[ValidationReport] for consistent error handling
3. **Evidence-Based**: All validations emit evidence events for audit trails
4. **Parallel Execution**: Independent validators run concurrently
5. **Orchestrated Coordination**: Orchestrator manages dependencies and aggregates results

### Swarm Topology

```
                    ┌─────────────────────────┐
                    │  Orchestrator Agent     │
                    │  (Coordination & Agg)   │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
    ┌───────────────────┐ ┌──────────────┐ ┌─────────────┐
    │ CRUD Validator    │ │ State Trans. │ │ Performance │
    │ Agent             │ │ Validator    │ │ Validator   │
    └───────────────────┘ └──────────────┘ └─────────────┘
                │                │                │
                ▼                ▼                ▼
    ┌───────────────────┐ ┌──────────────┐ ┌─────────────┐
    │ Integrity Check   │ │ Relationship │ │ Audit Trail │
    │ Agent             │ │ Validator    │ │ Validator   │
    └───────────────────┘ └──────────────┘ └─────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Report Aggregator      │
                    │  (Synthesis & Summary)  │
                    └─────────────────────────┘
```

---

## Agent Definitions

### 1. Orchestrator Agent

**Role**: Coordinates validation workflow and aggregates results

**Responsibilities**:
- Initialize swarm with validation parameters
- Dispatch work to specialized agents
- Manage execution order and dependencies
- Aggregate validation reports
- Generate comprehensive summary
- Emit orchestration evidence

**Inputs**:
```python
{
    "db_path": "db/trackers.sqlite",
    "scope": "full",  # or "quick", "sprint", "project"
    "filters": {
        "project_id": "P-CF-SPECTRE-001",
        "sprint_id": "S-CF-Work-Sprint1",
        "status": ["new", "in_progress"]
    },
    "parallel": True,
    "emit_evidence": True
}
```

**Outputs**:
```python
Result[SwarmValidationReport] {
    "validation_id": "VAL-20251117-001",
    "started_at": "2025-11-17T10:00:00Z",
    "completed_at": "2025-11-17T10:05:23Z",
    "scope": "full",
    "agents_executed": 6,
    "total_checks": 247,
    "passed": 245,
    "failed": 2,
    "warnings": 5,
    "agent_reports": [...],
    "summary": {...},
    "recommendations": [...]
}
```

---

### 2. CRUD Validator Agent

**Role**: Validate Create, Read, Update, Delete operations

**Responsibilities**:
- Test task creation with valid/invalid inputs
- Verify read operations return correct data
- Validate update operations and field changes
- Test soft delete functionality
- Verify SQL injection protection
- Test edge cases (empty strings, null values, special characters)

**Test Cases**:

1. **Create Operations**:
   - ✓ Create task with minimal required fields
   - ✓ Create task with all optional fields
   - ✗ Create task with missing required field (title)
   - ✗ Create task with invalid status value
   - ✓ Create task with dependencies
   - ✓ Verify created_at and updated_at timestamps

2. **Read Operations**:
   - ✓ Read task by ID
   - ✓ List tasks with filters (status, project, sprint)
   - ✓ Read non-existent task (should fail gracefully)
   - ✓ Verify soft-deleted tasks excluded from list
   - ✓ Test pagination (limit, offset)

3. **Update Operations**:
   - ✓ Update single field (status)
   - ✓ Update multiple fields
   - ✓ Update with invalid data (should fail)
   - ✓ Verify updated_at timestamp changes
   - ✓ Update with concurrent modifications

4. **Delete Operations**:
   - ✓ Soft delete task (deleted_at set)
   - ✓ Verify task excluded from queries
   - ✓ Verify cascade behavior with relationships

**Implementation Pattern**:
```python
from cf_core.shared.result import Result
from typing import List, Dict, Any
import sqlite3

class CRUDValidatorAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.results = []

    def validate(self) -> Result[Dict[str, Any]]:
        """Run all CRUD validation tests"""
        try:
            self._test_create_operations()
            self._test_read_operations()
            self._test_update_operations()
            self._test_delete_operations()

            report = {
                "agent": "CRUDValidator",
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r["passed"]),
                "failed": sum(1 for r in self.results if not r["passed"]),
                "test_results": self.results
            }
            return Result.success(report)
        except Exception as e:
            return Result.failure(f"CRUD validation failed: {e}")

    def _test_create_operations(self):
        """Test task creation"""
        # Test 1: Create with minimal fields
        self._run_test(
            name="create_minimal_task",
            command=["dbcli", "task", "create", "--title", "Test Task"],
            expected_status=0,
            validation=lambda r: "id" in r
        )
        # ... more tests

    def _run_test(self, name: str, command: List[str], expected_status: int, validation: callable):
        """Execute test and record result"""
        # Execute command via subprocess
        # Validate result
        # Record in self.results
```

---

### 3. State Transition Validator Agent

**Role**: Validate task lifecycle state transitions

**Responsibilities**:
- Test valid state transitions
- Reject invalid state transitions
- Verify state-specific field requirements
- Test concurrent state changes
- Validate state history tracking

**Valid Transitions**:
```python
STATE_MACHINE = {
    "new": ["in_progress", "dropped"],
    "in_progress": ["blocked", "review", "dropped"],
    "blocked": ["in_progress", "dropped"],
    "review": ["in_progress", "done", "dropped"],
    "done": [],  # Terminal state
    "dropped": []  # Terminal state
}
```

**Test Cases**:

1. **Valid Transitions**:
   - ✓ new → in_progress
   - ✓ in_progress → blocked
   - ✓ blocked → in_progress
   - ✓ in_progress → review
   - ✓ review → done
   - ✓ new → dropped
   - ✓ in_progress → dropped

2. **Invalid Transitions**:
   - ✗ new → review (skip in_progress)
   - ✗ new → done (skip workflow)
   - ✗ done → in_progress (terminal state)
   - ✗ dropped → in_progress (terminal state)

3. **State Requirements**:
   - ✓ status=done requires done_date
   - ✓ status=blocked requires risk_notes
   - ✓ status=in_progress requires owner

**Implementation**:
```python
class StateTransitionValidatorAgent:
    STATE_MACHINE = {
        "new": ["in_progress", "dropped"],
        "in_progress": ["blocked", "review", "dropped"],
        "blocked": ["in_progress", "dropped"],
        "review": ["in_progress", "done", "dropped"],
        "done": [],
        "dropped": []
    }

    def validate_transition(self, task_id: str, from_state: str, to_state: str) -> Result[bool]:
        """Validate state transition is allowed"""
        if to_state not in self.STATE_MACHINE.get(from_state, []):
            return Result.failure(f"Invalid transition: {from_state} → {to_state}")
        return Result.success(True)

    def validate(self) -> Result[Dict[str, Any]]:
        """Run all state transition tests"""
        # Create test task
        # Test each valid transition
        # Test each invalid transition
        # Aggregate results
```

---

### 4. Data Integrity Validator Agent

**Role**: Validate data consistency and referential integrity

**Responsibilities**:
- Verify foreign key constraints (project_id, sprint_id)
- Test cascade operations
- Validate JSON field structure (depends_on, blocks, assignees)
- Check for orphaned records
- Verify unique constraints
- Test timestamp consistency

**Test Cases**:

1. **Foreign Keys**:
   - ✗ Create task with non-existent project_id (should fail)
   - ✗ Create task with non-existent sprint_id (should fail)
   - ✓ Create task with valid project_id and sprint_id
   - ✓ Verify CASCADE on project delete (if configured)

2. **JSON Fields**:
   - ✓ Valid JSON array for depends_on
   - ✓ Valid JSON array for assignees
   - ✗ Invalid JSON syntax (should fail or sanitize)
   - ✓ Empty JSON arrays handled correctly

3. **Orphaned Records**:
   - Find tasks referencing deleted projects
   - Find tasks referencing deleted sprints
   - Find tasks with circular dependencies

4. **Timestamp Consistency**:
   - ✓ created_at <= updated_at
   - ✓ updated_at changes on every update
   - ✓ done_date set when status=done
   - ✓ All timestamps in UTC ISO8601 format

**Implementation**:
```python
class DataIntegrityValidatorAgent:
    def validate(self) -> Result[Dict[str, Any]]:
        """Run data integrity checks"""
        issues = []

        # Check foreign keys
        issues.extend(self._check_foreign_keys())

        # Check JSON validity
        issues.extend(self._check_json_fields())

        # Check orphaned records
        issues.extend(self._check_orphans())

        # Check timestamps
        issues.extend(self._check_timestamps())

        report = {
            "agent": "DataIntegrityValidator",
            "issues_found": len(issues),
            "critical": sum(1 for i in issues if i["severity"] == "critical"),
            "warnings": sum(1 for i in issues if i["severity"] == "warning"),
            "issues": issues
        }

        if any(i["severity"] == "critical" for i in issues):
            return Result.failure(report)
        return Result.success(report)

    def _check_foreign_keys(self) -> List[Dict]:
        """Check referential integrity"""
        conn = sqlite3.connect(self.db_path)
        issues = []

        # Find tasks with invalid project_id
        cursor = conn.execute("""
            SELECT t.id, t.project_id
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.project_id IS NOT NULL
              AND p.id IS NULL
              AND t.deleted_at IS NULL
        """)

        for row in cursor:
            issues.append({
                "type": "foreign_key_violation",
                "severity": "critical",
                "table": "tasks",
                "field": "project_id",
                "task_id": row[0],
                "invalid_ref": row[1]
            })

        return issues
```

---

### 5. Relationship Validator Agent

**Role**: Validate task dependencies and relationships

**Responsibilities**:
- Test depends_on relationships
- Test blocks relationships
- Detect circular dependencies
- Verify bidirectional consistency
- Validate dependency state logic
- Test cascade effects

**Test Cases**:

1. **Dependency Creation**:
   - ✓ Task A depends_on Task B
   - ✓ Task B blocks Task A (reciprocal)
   - ✓ Multiple dependencies
   - ✓ Dependency chain (A→B→C)

2. **Circular Dependencies**:
   - ✗ Detect A→B→A cycle
   - ✗ Detect A→B→C→A cycle
   - ✓ No cycles in dependency graph

3. **State Logic**:
   - ✓ Task cannot be done if dependencies not done
   - ✓ Blocked task has blocker in depends_on
   - ✓ Done task doesn't block in_progress tasks

4. **Orphaned Dependencies**:
   - Find tasks depending on deleted tasks
   - Find tasks blocking deleted tasks

**Implementation**:
```python
class RelationshipValidatorAgent:
    def validate(self) -> Result[Dict[str, Any]]:
        """Validate task relationships"""
        issues = []

        # Build dependency graph
        graph = self._build_dependency_graph()

        # Check for cycles
        cycles = self._detect_cycles(graph)
        if cycles:
            issues.extend([
                {"type": "circular_dependency", "cycle": cycle}
                for cycle in cycles
            ])

        # Check bidirectional consistency
        issues.extend(self._check_bidirectional())

        # Check state logic
        issues.extend(self._check_dependency_states())

        return Result.success({
            "agent": "RelationshipValidator",
            "issues_found": len(issues),
            "issues": issues
        })

    def _detect_cycles(self, graph: Dict) -> List[List[str]]:
        """Use DFS to detect cycles in dependency graph"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles
```

---

### 6. Performance Validator Agent

**Role**: Validate performance and scalability

**Responsibilities**:
- Benchmark CRUD operations
- Test query performance with large datasets
- Validate indexing effectiveness
- Test concurrent operations
- Monitor memory usage
- Check for N+1 query problems

**Test Cases**:

1. **Baseline Performance**:
   - ✓ Create 100 tasks < 5 seconds
   - ✓ List 1000 tasks < 1 second
   - ✓ Update task < 100ms
   - ✓ Query with filters < 500ms

2. **Scalability**:
   - ✓ Create 10,000 tasks
   - ✓ Query performance with 10,000 tasks
   - ✓ Index effectiveness on status/priority

3. **Concurrency**:
   - ✓ 10 concurrent creates
   - ✓ 10 concurrent updates to same task
   - ✓ No data corruption with concurrent access

**Implementation**:
```python
import time
import concurrent.futures

class PerformanceValidatorAgent:
    BENCHMARKS = {
        "create_100_tasks": {"threshold": 5.0, "unit": "seconds"},
        "list_1000_tasks": {"threshold": 1.0, "unit": "seconds"},
        "update_task": {"threshold": 0.1, "unit": "seconds"},
        "query_filtered": {"threshold": 0.5, "unit": "seconds"}
    }

    def validate(self) -> Result[Dict[str, Any]]:
        """Run performance tests"""
        results = []

        # Benchmark create operations
        start = time.time()
        for i in range(100):
            self._create_task(f"Task {i}")
        create_time = time.time() - start

        results.append({
            "test": "create_100_tasks",
            "duration": create_time,
            "threshold": self.BENCHMARKS["create_100_tasks"]["threshold"],
            "passed": create_time < self.BENCHMARKS["create_100_tasks"]["threshold"]
        })

        # More benchmarks...

        return Result.success({
            "agent": "PerformanceValidator",
            "results": results,
            "all_passed": all(r["passed"] for r in results)
        })
```

---

### 7. Audit Trail Validator Agent

**Role**: Validate evidence logging and audit compliance

**Responsibilities**:
- Verify evidence events emitted for all operations
- Validate evidence structure and completeness
- Check audit_tag consistency
- Test evidence replay capability
- Verify correlation_hint tracking

**Test Cases**:

1. **Evidence Emission**:
   - ✓ Create operation emits evidence
   - ✓ Update operation emits evidence with diff
   - ✓ Delete operation emits evidence
   - ✓ Evidence includes timestamp, agent_id, correlation_hint

2. **Evidence Structure**:
   - ✓ Valid JSON structure
   - ✓ Required fields present (action, target, timestamp)
   - ✓ Diff includes before/after values

3. **Audit Trail**:
   - ✓ Can reconstruct task history from evidence
   - ✓ No gaps in evidence log
   - ✓ Evidence timestamps monotonically increasing

**Implementation**:
```python
class AuditTrailValidatorAgent:
    def validate(self) -> Result[Dict[str, Any]]:
        """Validate audit trail"""
        issues = []

        # Check evidence emission
        task_id = self._create_test_task()
        evidence = self._get_evidence_for_task(task_id)

        if not evidence:
            issues.append({
                "type": "missing_evidence",
                "severity": "critical",
                "task_id": task_id
            })

        # Validate evidence structure
        for ev in evidence:
            issues.extend(self._validate_evidence_structure(ev))

        # Test replay
        try:
            reconstructed = self._replay_evidence(evidence)
            if not self._compare_states(reconstructed, self._get_task(task_id)):
                issues.append({
                    "type": "replay_mismatch",
                    "severity": "critical",
                    "task_id": task_id
                })
        except Exception as e:
            issues.append({
                "type": "replay_failed",
                "severity": "critical",
                "error": str(e)
            })

        return Result.success({
            "agent": "AuditTrailValidator",
            "issues_found": len(issues),
            "issues": issues
        })
```

---

## Orchestration Workflow

### Sequential Execution Plan

```python
class ValidationOrchestrator:
    def __init__(self, db_path: str, config: Dict[str, Any]):
        self.db_path = db_path
        self.config = config
        self.agents = self._initialize_agents()
        self.results = {}

    def _initialize_agents(self) -> List:
        """Initialize all validation agents"""
        return [
            CRUDValidatorAgent(self.db_path),
            StateTransitionValidatorAgent(self.db_path),
            DataIntegrityValidatorAgent(self.db_path),
            RelationshipValidatorAgent(self.db_path),
            PerformanceValidatorAgent(self.db_path),
            AuditTrailValidatorAgent(self.db_path)
        ]

    def execute_swarm(self) -> Result[Dict[str, Any]]:
        """Execute validation swarm"""
        validation_id = self._generate_validation_id()
        started_at = self._utc_now()

        # Phase 1: Data Integrity (must pass before continuing)
        integrity_result = self.agents[2].validate()
        if integrity_result.is_failure:
            return Result.failure({
                "message": "Data integrity check failed - aborting validation",
                "integrity_report": integrity_result.error
            })
        self.results["integrity"] = integrity_result.value

        # Phase 2: Parallel execution of independent validators
        if self.config.get("parallel", True):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.agents[0].validate): "crud",
                    executor.submit(self.agents[1].validate): "state",
                    executor.submit(self.agents[3].validate): "relationship",
                    executor.submit(self.agents[5].validate): "audit"
                }

                for future in concurrent.futures.as_completed(futures):
                    agent_name = futures[future]
                    try:
                        result = future.result()
                        self.results[agent_name] = result.value if result.is_success else result.error
                    except Exception as e:
                        self.results[agent_name] = {"error": str(e)}
        else:
            # Sequential execution
            for agent, name in zip(self.agents, ["crud", "state", "integrity", "relationship", "performance", "audit"]):
                if name != "integrity":  # Already executed
                    result = agent.validate()
                    self.results[name] = result.value if result.is_success else result.error

        # Phase 3: Performance validation (optional, can be slow)
        if self.config.get("include_performance", False):
            perf_result = self.agents[4].validate()
            self.results["performance"] = perf_result.value if perf_result.is_success else perf_result.error

        # Phase 4: Aggregate results
        completed_at = self._utc_now()
        summary = self._generate_summary()

        final_report = {
            "validation_id": validation_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "scope": self.config.get("scope", "full"),
            "agents_executed": len(self.results),
            "agent_reports": self.results,
            "summary": summary,
            "recommendations": self._generate_recommendations(),
            "overall_status": self._determine_status()
        }

        # Emit orchestration evidence
        if self.config.get("emit_evidence", True):
            self._emit_evidence(final_report)

        return Result.success(final_report)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary from all agent reports"""
        total_checks = sum(
            r.get("total_tests", r.get("issues_found", 0))
            for r in self.results.values()
            if isinstance(r, dict)
        )

        total_passed = sum(
            r.get("passed", 0)
            for r in self.results.values()
            if isinstance(r, dict)
        )

        total_failed = sum(
            r.get("failed", r.get("critical", 0))
            for r in self.results.values()
            if isinstance(r, dict)
        )

        total_warnings = sum(
            r.get("warnings", 0)
            for r in self.results.values()
            if isinstance(r, dict)
        )

        return {
            "total_checks": total_checks,
            "passed": total_passed,
            "failed": total_failed,
            "warnings": total_warnings,
            "success_rate": (total_passed / total_checks * 100) if total_checks > 0 else 0
        }

    def _determine_status(self) -> str:
        """Determine overall validation status"""
        summary = self._generate_summary()

        if summary["failed"] == 0:
            return "PASSED"
        elif summary["failed"] > 0 and summary["success_rate"] >= 90:
            return "PASSED_WITH_WARNINGS"
        elif summary["success_rate"] >= 70:
            return "DEGRADED"
        else:
            return "FAILED"

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        for agent_name, report in self.results.items():
            if isinstance(report, dict):
                if report.get("failed", 0) > 0:
                    recommendations.append(
                        f"Address {report['failed']} failed checks in {agent_name}"
                    )
                if report.get("issues_found", 0) > 0:
                    recommendations.append(
                        f"Investigate {report['issues_found']} issues found by {agent_name}"
                    )

        return recommendations
```

---

## Usage Examples

### Example 1: Full Validation

```bash
# Run complete validation swarm
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope full \
  --parallel \
  --include-performance \
  --emit-evidence \
  --output validation-report.json
```

### Example 2: Sprint-Scoped Validation

```bash
# Validate specific sprint
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope sprint \
  --sprint-id S-CF-Work-Sprint1 \
  --parallel \
  --output sprint-validation.json
```

### Example 3: Quick Validation (No Performance)

```bash
# Quick validation without performance tests
python -m cf_core.validation.orchestrator \
  --db-path db/trackers.sqlite \
  --scope quick \
  --parallel \
  --no-performance \
  --output quick-validation.json
```

### Example 4: Programmatic Usage

```python
from cf_core.validation.orchestrator import ValidationOrchestrator

# Initialize orchestrator
orchestrator = ValidationOrchestrator(
    db_path="db/trackers.sqlite",
    config={
        "scope": "full",
        "parallel": True,
        "include_performance": True,
        "emit_evidence": True,
        "filters": {
            "project_id": "P-CF-SPECTRE-001"
        }
    }
)

# Execute swarm
result = orchestrator.execute_swarm()

if result.is_success:
    report = result.value
    print(f"Validation Status: {report['overall_status']}")
    print(f"Success Rate: {report['summary']['success_rate']:.2f}%")
    print(f"Recommendations: {len(report['recommendations'])}")
else:
    print(f"Validation failed: {result.error}")
```

---

## Integration with CF_CORE

### CLI Integration

Add validation commands to `dbcli.py`:

```python
# dbcli.py
from cf_core.validation.orchestrator import ValidationOrchestrator

@app.command("validate")
def validate_workflows(
    scope: str = typer.Option("full", help="Validation scope"),
    sprint_id: str = typer.Option(None, help="Sprint ID to validate"),
    parallel: bool = typer.Option(True, help="Run agents in parallel"),
    performance: bool = typer.Option(False, help="Include performance tests"),
    output: str = typer.Option("validation-report.json", help="Output file")
):
    """Run validation swarm on task workflows"""
    config = {
        "scope": scope,
        "parallel": parallel,
        "include_performance": performance,
        "emit_evidence": True,
        "filters": {"sprint_id": sprint_id} if sprint_id else {}
    }

    orchestrator = ValidationOrchestrator("db/trackers.sqlite", config)
    result = orchestrator.execute_swarm()

    if result.is_success:
        report = result.value

        # Save report
        with open(output, "w") as f:
            json.dump(report, f, indent=2)

        # Display summary
        console = Console()
        console.print(Panel(
            f"[green]Validation Complete[/green]\n\n"
            f"Status: {report['overall_status']}\n"
            f"Success Rate: {report['summary']['success_rate']:.2f}%\n"
            f"Checks: {report['summary']['total_checks']}\n"
            f"Passed: {report['summary']['passed']}\n"
            f"Failed: {report['summary']['failed']}\n"
            f"Warnings: {report['summary']['warnings']}",
            title="Validation Report"
        ))

        if report['recommendations']:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in report['recommendations']:
                console.print(f"  • {rec}")
    else:
        console.print(f"[red]Validation failed:[/red] {result.error}")
```

---

## Evidence Schema

All agents emit structured evidence:

```json
{
  "validation_id": "VAL-20251117-001",
  "agent": "CRUDValidator",
  "timestamp": "2025-11-17T10:00:00Z",
  "action": "validation_executed",
  "scope": "full",
  "results": {
    "total_tests": 50,
    "passed": 48,
    "failed": 2,
    "warnings": 3
  },
  "failures": [
    {
      "test": "create_with_invalid_status",
      "expected": "failure",
      "actual": "success",
      "severity": "critical"
    }
  ],
  "metadata": {
    "db_path": "db/trackers.sqlite",
    "execution_time_ms": 1234,
    "correlation_id": "CORR-001"
  }
}
```

---

## Testing the Swarm

### Unit Tests for Individual Agents

```python
# tests/validation/test_crud_validator.py
import pytest
from cf_core.validation.agents import CRUDValidatorAgent

def test_crud_validator_create_operations(tmp_db_path):
    agent = CRUDValidatorAgent(tmp_db_path)
    result = agent._test_create_operations()
    assert result.is_success
    assert result.value["passed"] > 0

def test_crud_validator_handles_invalid_input(tmp_db_path):
    agent = CRUDValidatorAgent(tmp_db_path)
    result = agent.validate()
    assert result.is_success
    # Should have some failures for invalid inputs
    assert result.value["failed"] > 0
```

### Integration Tests for Orchestrator

```python
# tests/validation/test_orchestrator.py
import pytest
from cf_core.validation.orchestrator import ValidationOrchestrator

def test_orchestrator_full_validation(test_db_with_data):
    orchestrator = ValidationOrchestrator(
        test_db_with_data,
        {"scope": "full", "parallel": False}
    )
    result = orchestrator.execute_swarm()

    assert result.is_success
    report = result.value
    assert "validation_id" in report
    assert report["agents_executed"] >= 5
    assert report["summary"]["total_checks"] > 0

def test_orchestrator_parallel_execution(test_db_with_data):
    orchestrator = ValidationOrchestrator(
        test_db_with_data,
        {"scope": "quick", "parallel": True}
    )
    result = orchestrator.execute_swarm()
    assert result.is_success
```

---

## Monitoring and Observability

### Metrics to Track

1. **Validation Execution**:
   - Total validations run
   - Average execution time
   - Success rate trends
   - Agent-specific performance

2. **Issue Detection**:
   - Critical issues found
   - Warnings issued
   - Issue categories (integrity, performance, audit)
   - Time to resolution

3. **System Health**:
   - Database size growth
   - Query performance trends
   - Evidence storage utilization

### Dashboards

Create monitoring dashboards in analytics:

```python
# python/analytics/validation_dashboard.py
def generate_validation_dashboard(validation_results: List[Dict]) -> Dict:
    """Generate validation metrics dashboard"""
    return {
        "total_validations": len(validation_results),
        "success_rate": sum(1 for r in validation_results if r["status"] == "PASSED") / len(validation_results),
        "avg_execution_time": statistics.mean(r["duration"] for r in validation_results),
        "issues_by_category": categorize_issues(validation_results),
        "trends": calculate_trends(validation_results)
    }
```

---

## Future Enhancements

1. **Self-Healing Agents**: Agents that can automatically fix detected issues
2. **Machine Learning**: Anomaly detection for performance regressions
3. **Continuous Validation**: Real-time validation on every operation
4. **Custom Validators**: Plugin architecture for domain-specific validators
5. **Distributed Execution**: Run swarm across multiple nodes
6. **Web UI**: Real-time dashboard for validation status

---

## References

- CF_CORE Architecture: `docs/02-Architecture.md`
- Database Schema: `docs/05-Database-Design-Implementation.md`
- CLI Reference: `docs/10-API-Reference.md`
- Testing Guidelines: `docs/13-Testing-Validation.md`
- Result Monad Pattern: `cf_core/shared/result.py`
- Repository Pattern: `cf_core/repositories/sprint_repository.py`

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-17
**Status**: Active Development
**Next Review**: 2025-12-01
