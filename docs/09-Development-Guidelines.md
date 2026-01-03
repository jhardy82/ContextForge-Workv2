# 09 – Development Guidelines

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [13-Testing-Validation](13-Testing-Validation.md) | [Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md)

---

## Purpose

Establish **concise, enforceable engineering standards** aligned with the ContextForge Universal Methodology and [ContextForge Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md). This document is implementation-layer guidance (Doc 09) mapping high-level principles to day-to-day practice.

---

## Core Philosophies (Codex)

From [ContextForge Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

1. **Trust Nothing, Verify Everything** — Evidence is the closing loop of trust. Logs and tests ground belief.
2. **Workspace First** — Begin with what exists; build outward only when necessary.
3. **Logs First** — Truth lives in records, not assumptions.
4. **Leave Things Better** — Every action should enrich the system for those who follow.
5. **Fix the Root, Not the Symptom** — Problems repeat until addressed at the source.
6. **Best Tool for the Context** — Every task has its proper tool; discernment is the engineer's art.
7. **Balance Order and Flow** — Rigid order calcifies; unchecked flow dissolves. The right path blends both.
8. **Iteration is Sacred** — Progress spirals, not straight lines.
9. **Context Before Action** — To act without context is to cut against the grain.
10. **Resonance is Proof** — Solutions that harmonize across business, user, and technical needs endure.
11. **Diversity, Equity, and Inclusion** — Teams and systems thrive when perspectives are varied, access is fair, and participation is open.

---

## Engineering Pillars

### 1. Logging First (LOG-001..009)

**Principle**: Emit baseline event set every non-trivial run.

**Required Events** (non-trivial run):
- `session_start` - Begin work session
- `task_start` - Each atomic unit of work
- `decision` - Reuse vs generate / branch logic
- `artifact_touch_batch` - Multi-file reads
- `artifact_emit` - Every created/modified artifact (with hash + size)
- `warning` / `error` - All exceptional conditions
- `task_end` - Complete work unit
- `session_summary` - Session metrics

**Missing any → emit `logging_gap_detected`; repeat → `logging_deficit`**

**Logging Coverage Target**: ≥90% of execution paths produce structured logs (Codex Addendum C)

**Implementation** (Python):
```python
from python.services.unified_logger import logger

def process_task(task_id: str):
    """Process task with comprehensive logging."""
    logger.info("task_start", task_id=task_id)

    try:
        # Read artifacts
        files = ["config.yaml", "schema.json"]
        logger.info("artifact_touch_batch", files=files)

        # Make decision
        if should_reuse_existing():
            logger.info("decision", choice="reuse", rationale="valid_existing_schema")
        else:
            logger.info("decision", choice="generate", rationale="missing_contract")

        # Generate artifact
        result = generate_artifact()
        logger.info("artifact_emit",
                   path="output.json",
                   hash=compute_hash(result),
                   size_bytes=len(result))

        logger.info("task_end", task_id=task_id, status="success")

    except Exception as e:
        logger.error("task_failed",
                    task_id=task_id,
                    error_type=type(e).__name__,
                    message=str(e),
                    remediation=["Check input validity", "Retry with valid data"])
        raise
```

### 2. Python-First Orchestration

**Principle**: Governance & analytics scripted in Python 3.11+ with direct invocation.

**Prohibited**:
```powershell
# ❌ DON'T DO THIS
pwsh -Command "python script.py"
```

**Allowed**:
```powershell
# ✅ Direct invocation
python script.py

# ✅ With activated venv
.\.venv\Scripts\python script.py
```

**Exception**: `pwsh -Command` only when irreducible pre-flight documented with `# HostFallbackReason: wrapper_required`

### 3. Authority & Idempotency

**Database Authority Principle** (Codex Addendum A):
- PostgreSQL (`172.25.14.122:5432/taskman_v2`) is **primary task management authority** for TaskMan-v2
- SQLite (`db/trackers.sqlite`) maintains legacy tracker data and supplementary context
- Runtime CSV mutation **blocked** (`direct_csv_access_blocked`)
- Legacy CSV constants only for migration

**Idempotency**: All operations must be safe on re-run.

**Implementation**:
```python
# cf_core/repositories/authority_check.py
import os

SENTINEL_PATH = "db/.cf_migration_complete"

def check_database_authority() -> bool:
    """Check if database is authoritative source."""
    if os.path.exists(SENTINEL_PATH):
        return True
    else:
        logger.warn("direct_csv_access_blocked",
                   message="Database authority not established")
        return False

def ensure_idempotent_operation(operation_name: str):
    """Decorator to ensure operation is idempotent."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if already done
            if is_operation_completed(operation_name):
                logger.info("operation_skipped",
                           operation=operation_name,
                           reason="already_completed")
                return

            # Execute
            result = func(*args, **kwargs)

            # Mark complete
            mark_operation_completed(operation_name)
            return result
        return wrapper
    return decorator
```

### 4. Quality Gates

**Matrix**:

| Domain | Tool | Threshold | Enforcement |
|--------|------|-----------|-------------|
| Python Lint | ruff | 0 errors (warn allowed) | Blocking |
| Python Types | mypy | no errors new strict modules | Advisory |
| Python Tests | pytest | pass; coverage ≥85% (target) | Blocking |
| PowerShell Lint | PSScriptAnalyzer | 0 Errors | Blocking |
| PowerShell Tests | Pester | pass; coverage ≥70% | Blocking |
| Security | pip-audit | no HIGH/CRITICAL vulns | Blocking |
| Config | JSON Schema | valid config + context schema | Blocking |

**Coverage Policy** (Codex Addendum C):
- Unit: ≥70%
- Integration: ≥40%
- System: ≥25%
- Acceptance: ≥15%
- Logging: ≥90%

### 5. JSON Serialization Standards

**Principle**: All JSON output MUST use canonical serialization for reproducibility and hash stability.

**Authoritative Reference**: [Output Manager Serialization Spec](output-manager/serialization-spec.md)

**Requirements** (RFC 8785 - JSON Canonicalization Scheme):
- Lexicographic key ordering (Unicode code point order)
- No whitespace between tokens
- Minimal number representation (no trailing zeros, convert `-0` to `0`)
- I-JSON range compliance for integers (±2^53-1)
- UTF-8 encoding with minimal escaping

**Implementation** (Python):
```python
from python.output_manager import OutputManager

# Canonical serialization for evidence bundles
canonical_json = OutputManager.canonicalize(data)
evidence_hash = OutputManager.hash_evidence(data)  # SHA-256 of canonical form

# Rich console output with consistent styling
OutputManager.print_json(data)  # Uses configured theme
```

**Anti-Pattern** (Deprecated):
```python
# ❌ DON'T DO THIS - Non-canonical, hash-unstable
json.dumps(data, sort_keys=True, indent=2)

# ✅ DO THIS - RFC 8785 compliant
from python.output_manager import OutputManager
OutputManager.canonicalize(data)
```

**Migration**: All `json.dumps()` calls in CLI tools and evidence generation MUST migrate to Output Manager by Sprint 3.

---

### 6. Evidence On Trigger

**Activation Triggers**:
- `high_risk` refactor label
- Public API shape changes (OpenAPI diff)
- `evidence:true` marker in task
- Security vulnerability fixes

**Else**: Rely on baseline logging + quality gates

**Evidence Bundle**:
```python
from python.output_manager import OutputManager

def create_evidence_bundle(event: dict) -> str:
    """Generate SHA-256 evidence hash using canonical serialization."""
    return OutputManager.hash_evidence(event)

# Usage
event = {"event_type": "task_complete", "task_id": "TASK-123"}
evidence_hash = create_evidence_bundle(event)
logger.info("task_complete", evidence_bundle_hash=evidence_hash, **event)
```

---

## Sacred Geometry Patterns

From [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md):

### Triangle (Stability)

**Three-layer architecture**: CLI → Domain → Storage

**Triple-Check Protocol**:
1. Initial build → tests pass
2. Logs-first diagnostics → all events emitted
3. Reproducibility/DoD compliance → evidence bundles valid

**Implementation**:
```python
def triple_check_protocol():
    """Execute triple-check validation."""
    # 1. Build
    if not run_tests():
        raise ValidationError("Tests failed")

    # 2. Logs
    if not validate_logging_coverage():
        raise ValidationError("Logging coverage < 90%")

    # 3. Evidence
    if not validate_evidence_bundles():
        raise ValidationError("Evidence bundles invalid")

    logger.info("triple_check_complete", status="passed")
```

### Circle (Completeness)

**COF 13-dimensional analysis** for all contexts:

```python
# cf_core/models/cof_dimensions.py
from pydantic import BaseModel

class COFDimensions(BaseModel):
    """13-dimensional Context Ontology Framework analysis."""
    motivational: str          # Why this work matters
    relational: str            # Dependencies & connections
    situational: str           # Environment & constraints
    resource: str              # Time, skill, tools
    narrative: str             # User/stakeholder journey
    recursive: str             # Meta-patterns & processes
    computational: str         # Algorithmic efficiency
    emergent: str              # Unexpected interactions
    temporal: str              # Timing & sequencing
    spatial: str               # Topology & layout
    holistic: str              # System-wide integration
    validation: str            # Evidence & requirements
    integration: str           # Fits back into whole
```

### Spiral (Iteration)

**DuckDB velocity tracking**: 0.23 hrs/point baseline

**Retrospectives**: Every 2 weeks (3/6/9 cadence)

**Implementation**:
```python
def record_velocity(task_id: str, hours: float, story_points: int):
    """Record task velocity in DuckDB."""
    import duckdb

    conn = duckdb.connect("db/velocity.duckdb")
    conn.execute("""
        INSERT INTO velocity_metrics (task_id, hours, story_points, timestamp)
        VALUES (?, ?, ?, NOW())
    """, [task_id, hours, story_points])

    logger.info("velocity_recorded",
               task_id=task_id,
               hours=hours,
               story_points=story_points)
```

### Golden Ratio (Balance)

**Right-sized solutions**:
- 35% focused test coverage (not 100%)
- Coverage targets reflect reality (70% unit, not 100%)
- "Best tool for the context" (Codex)

### Fractal (Modularity)

**Repository pattern** at all layers:

```python
# cf_core/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository pattern for all domain entities."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Retrieve entity by ID."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist entity."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        pass
```

---

## Host Policy Tags

**Every reusable script** must declare HostPolicy within first 20 lines:

```powershell
# HostPolicy: ModernPS7 | LegacyPS51 | DualHost | PythonHelper
# HostFallbackReason: <reason>  (only when LegacyPS51 or wrapper_required)
```

**Example**:
```powershell
# HostPolicy: ModernPS7
# Description: Generate PowerShell coverage report
# Requires: PowerShell 7.0+, Pester 5.0+

function Generate-PowerShellCoverage {
    # Implementation
}
```

---

## Virtual Environment Enforcement

**All Python invocations** occur after `.venv` activation.

**Enforcement**:
```powershell
# build/Ensure-VirtualEnv.ps1
if (-not $env:CF_VENV_ACTIVE) {
    Write-Error "Virtual environment not activated. Run: .\.venv\Scripts\Activate.ps1"
    exit 1
}
```

**CI/CD**:
```yaml
# .github/workflows/quality.yml
- name: Create venv
  run: python -m venv .venv

- name: Install deps
  run: .\.venv\Scripts\python -m pip install -r requirements.txt
```

---

## Tracker Operations

**Always mutate** tasks/projects/sprints via `dbcli`:

```bash
# Create task
python dbcli.py task create "Implement JWT auth" --priority high

# Update task
python dbcli.py task update TASK-001 --status in_progress

# Complete task
python dbcli.py task complete TASK-001

# Reference document in context
python dbcli.py context upsert-object \
  --kind document \
  --id docs/09-Development-Guidelines.md \
  --status complete
```

**Never edit CSV directly post-sentinel.**

---

## Document Lifecycle

**Status Flow**: `placeholder` → `draft` → `complete`

**Promotion to complete requires**:
1. Quality gates green (lint, tests, coverage)
2. Cross-references added (README, API ref)
3. Context object updated
4. Evidence bundle generated

**Implementation**:
```python
def promote_document_to_complete(doc_path: str):
    """Promote document from draft to complete."""
    # 1. Validate quality gates
    if not validate_quality_gates(doc_path):
        raise ValidationError("Quality gates not satisfied")

    # 2. Check cross-references
    if not validate_cross_references(doc_path):
        raise ValidationError("Missing cross-references")

    # 3. Update context
    update_context_status(doc_path, "complete")

    # 4. Generate evidence
    evidence_hash = generate_evidence_bundle(doc_path)

    logger.info("document_promoted",
               path=doc_path,
               status="complete",
               evidence_bundle_hash=evidence_hash)
```

---

## Code Style & Formatting

### Python

**Tool**: `ruff` (replaces black, isort, flake8, pyupgrade)

**Configuration** (pyproject.toml):
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
```

**Usage**:
```bash
# Check
ruff check .

# Fix
ruff check . --fix

# Format
ruff format .
```

### PowerShell

**Tool**: PSScriptAnalyzer

**Configuration** (PSScriptAnalyzerSettings.psd1):
```powershell
@{
    Rules = @{
        PSUseApprovedVerbs = @{
            Enable = $true
        }
        PSAvoidUsingWriteHost = @{
            Enable = $false  # Allowed for CLI output
        }
    }
}
```

**Usage**:
```powershell
# Check
Invoke-ScriptAnalyzer -Path . -Recurse

# Fix
Invoke-ScriptAnalyzer -Path . -Recurse -Fix
```

---

## Testing Standards

### Python Tests (pytest)

**Structure**:
```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Multi-component tests
├── system/            # End-to-end tests
└── conftest.py        # Shared fixtures
```

**Markers** (pytest.ini):
```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests
    system: System tests (slow)
    slow: Slow tests (skip in quick mode)
    evidence: Tests requiring evidence bundles
```

**Usage**:
```bash
# Run all tests
pytest

# Run fast tests only
pytest -m "not slow"

# Run with coverage
pytest --cov=cf_core --cov-report=html
```

### PowerShell Tests (Pester)

**Structure**:
```
tests/
├── ContextForge.Spectre.Tests.ps1
├── ContextForge.Spectre.Helpers.Tests.ps1
└── fixtures/
```

**Usage**:
```powershell
# Run all tests
Invoke-Pester

# Run with coverage
Invoke-Pester -CodeCoverage 'modules/**/*.ps1'
```

---

## ContextForge.Spectre Standards

**Sacred Geometry Glyphs**:

```powershell
# modules/ContextForge.Spectre/Public/Write-ContextForgeSacredGeometry.ps1

function Write-ContextForgeSacredGeometry {
    param([ValidateSet('Triangle', 'Circle', 'Spiral', 'GoldenRatio', 'Fractal')]
          [string]$Pattern)

    switch ($Pattern) {
        'Triangle' {
            Write-SpectreHost "    △" -Color Blue
            Write-SpectreHost "   △ △" -Color Blue
            Write-SpectreHost "  △   △" -Color Blue
        }
        'Circle' {
            Write-SpectreHost "   ◯" -Color Green
            Write-SpectreHost "  ◯ ◯" -Color Green
            Write-SpectreHost "   ◯" -Color Green
        }
        'Spiral' {
            Write-SpectreHost "  ⟲" -Color Yellow
            Write-SpectreHost " ⟲  ⟲" -Color Yellow
        }
        'GoldenRatio' {
            Write-SpectreHost "  φ = 1.618" -Color Magenta
        }
        'Fractal' {
            Write-SpectreHost "  ❋" -Color Cyan
            Write-SpectreHost " ❋ ❋" -Color Cyan
        }
    }
}
```

**Progress Tracking**:

```powershell
function Start-CFProgress {
    param(
        [string]$Activity,
        [int]$TotalSteps
    )

    $script:CFProgress = @{
        Activity = $Activity
        TotalSteps = $TotalSteps
        CurrentStep = 0
        StartTime = Get-Date
    }

    Write-SpectreHost "Starting: $Activity" -Color Green
    logger.info("progress_started", activity=$Activity, total_steps=$TotalSteps)
}

function Update-CFProgress {
    param([string]$Status)

    $script:CFProgress.CurrentStep++
    $pct = ($script:CFProgress.CurrentStep / $script:CFProgress.TotalSteps) * 100

    Write-SpectreHost "[$($script:CFProgress.CurrentStep)/$($script:CFProgress.TotalSteps)] $Status" -Color Yellow
    logger.info("progress_updated", step=$script:CFProgress.CurrentStep, status=$Status)
}

function Complete-CFProgress {
    $duration = (Get-Date) - $script:CFProgress.StartTime
    Write-SpectreHost "Completed: $($script:CFProgress.Activity) in $($duration.TotalSeconds)s" -Color Green
    logger.info("progress_completed", activity=$script:CFProgress.Activity, duration_seconds=$duration.TotalSeconds)
}
```

---

## Error Handling Patterns

### External Boundary Pattern

**Principle**: Wrap all external calls (filesystem, DB, subprocess, network)

**Implementation**:
```python
def safe_external_call(operation: str, timeout: int = 45):
    """Decorator for safe external calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation}_success")
                return result

            except TimeoutError as e:
                logger.error(f"{operation}_timeout",
                            timeout_seconds=timeout,
                            remediation=["Increase timeout", "Check network/resource availability"])
                raise

            except Exception as e:
                logger.error(f"{operation}_failed",
                            error_type=type(e).__name__,
                            message=str(e),
                            stack_frame=traceback.format_exc().split('\n')[-3],
                            remediation=["Check input validity", "Verify permissions", "Retry operation"])
                raise
        return wrapper
    return decorator

# Usage
@safe_external_call("database_query", timeout=30)
def query_database(sql: str):
    return db.execute(sql)
```

---

## Performance Considerations

### Incremental Testing

**Fast feedback loop**:
```bash
# Quick checks (< 5 seconds)
pytest -m "not slow" --exitfirst

# Incremental lint
ruff check --diff

# Pester incremental
Invoke-Pester -Path tests/ -Tag "Unit"
```

### Full Suite

**Pre-merge / governance**:
```bash
# Full test suite
pytest --cov=cf_core --cov-report=html

# Full lint
ruff check . --output-format=github

# Full Pester
Invoke-Pester -CodeCoverage 'modules/**/*.ps1'
```

---

## Pre-commit Hooks (Planned)

**Configuration** (.pre-commit-config.yaml):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key
      - id: check-yaml
      - id: check-json

  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest -m "not slow"
        language: system
        pass_filenames: false

      - id: pip-audit
        name: pip-audit
        entry: pip-audit
        language: system
        pass_filenames: false
```

---

## Config & Contracts

### Pydantic Models

```python
# models/context.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TaskContext(BaseModel):
    """Task context model."""
    id: str
    task_id: str
    title: str
    description: Optional[str] = None
    status: str = "new"
    priority: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # COF dimensions
    cof_motivational: Optional[str] = None
    cof_relational: Optional[str] = None
    cof_situational: Optional[str] = None
    cof_resource: Optional[str] = None
    cof_narrative: Optional[str] = None
    cof_recursive: Optional[str] = None
    cof_computational: Optional[str] = None
    cof_emergent: Optional[str] = None
    cof_temporal: Optional[str] = None
    cof_spatial: Optional[str] = None
    cof_holistic: Optional[str] = None
```

### Configuration Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContextForge Configuration",
  "type": "object",
  "properties": {
    "database_url": {
      "type": "string",
      "description": "PostgreSQL connection string"
    },
    "log_level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
      "default": "INFO"
    },
    "coverage_thresholds": {
      "type": "object",
      "properties": {
        "unit": {"type": "number", "minimum": 0, "maximum": 100},
        "integration": {"type": "number", "minimum": 0, "maximum": 100}
      }
    }
  },
  "required": ["database_url"]
}
```

---

## Reuse vs Generate

**Decision Flow**:

1. **Search repo** for existing artifact
2. If exists and valid:
   - Log `decision` event with `choice: reuse`
   - Return existing artifact
3. If missing or invalid:
   - Log `decision` event with `choice: generate`, `rationale: missing_contract`
   - Generate new artifact
   - Log `artifact_emit` with hash

**Implementation**:
```python
def get_or_generate_schema(name: str):
    """Get existing schema or generate new one."""
    schema_path = f"schemas/{name}.json"

    if os.path.exists(schema_path) and validate_schema(schema_path):
        logger.info("decision",
                   choice="reuse",
                   artifact=schema_path,
                   rationale="valid_existing_schema")
        return load_schema(schema_path)
    else:
        logger.info("decision",
                   choice="generate",
                   artifact=schema_path,
                   rationale="missing_contract")
        schema = generate_schema(name)
        save_schema(schema_path, schema)
        logger.info("artifact_emit",
                   path=schema_path,
                   hash=compute_hash(schema))
        return schema
```

---

## Cross References

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview with philosophies
- [02-Architecture.md](02-Architecture.md) - Component architecture
- [13-Testing-Validation.md](13-Testing-Validation.md) - QSE framework, UTMW workflow

### Authoritative Source

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE**

### Implementation Details

- [python/services/unified_logger.py](../python/services/unified_logger.py) - Unified logging
- [cf_core/repositories/](../cf_core/repositories/) - Repository pattern implementations
- [modules/ContextForge.Spectre/](../modules/ContextForge.Spectre/) - Terminal UI module

---

**Document Status**: Complete ✅
**Authoritative**: Yes (integrated with Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Engineering Team

---

*"Code clarity mirrors human clarity. Refactorings echo the process of human growth. Every commit is a choice point in context; context objects preserve the lineage of those choices."*
