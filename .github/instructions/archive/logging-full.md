---
applyTo: "log*, logging*, evidence*, audit*, trace*, debug log*"
description: "Unified logging standards, evidence protocols, and audit requirements"
version: "3.0"
---

# Unified Logging Standards

**Authority**: [09-Development-Guidelines.md](docs/09-Development-Guidelines.md) | Work Codex Principle: "Logs First"

---

## Core Principle

**"Truth lives in records, not assumptions."**

All non-trivial operations must generate structured logs. Missing logs indicate missing governance and create audit gaps.

---

## Baseline Event Set (Required for ALL Operations)

### Mandatory Event Sequence

**Every substantive operation must log**:

1. **`session_start`** — Session initialization with project ID
2. **`task_start`** — Each substantive unit begins
3. **`decision`** — Any branching, reuse, or risk classification
4. **`artifact_touch_batch`** — Read operations ≥1 item
5. **`artifact_emit`** — Each created/modified artifact with hash/size
6. **`warning`** / **`error`** — Structured, one-line JSON each
7. **`task_end`** — With outcome and duration
8. **`session_summary`** — Aggregated counts, failures, evidence, project ID

### Coverage Target

**≥90% of execution paths** must emit baseline events.

**Enforcement**: Gate failures on missing critical events (e.g., `session_start`, `task_start`, `session_summary`).

---

## UnifiedLogger Integration

### Python Implementation

```python
from python.services.unified_logger import logger

# Session start
logger.info("session_start",
           session_id="QSE-20251114-1530-abc123",
           project_id="P-CFWORK-001",
           user="james.hardy1124@gmail.com")

# Task start
logger.info("task_start",
           task_id="TASK-001",
           task_name="Implement JWT authentication",
           estimated_hours=4.5)

# Decision point
logger.info("decision",
           decision_type="branch",
           branch_id="BR-001",
           rationale="OAuth2 vs custom auth",
           selected="oauth2",
           confidence=0.85)

# Artifact read
logger.info("artifact_touch_batch",
           artifacts=["auth.py", "config.yaml", "requirements.txt"],
           operation="read",
           count=3)

# Artifact creation
logger.info("artifact_emit",
           artifact_path=".qse/v2/Artifacts/P-CFWORK-001/ExecutionPlan-001.yaml",
           artifact_type="execution_plan",
           hash="sha256:abc123def456...",
           size_bytes=4096)

# Warning
logger.warning("warning",
              warning_type="test_coverage_low",
              module="auth.py",
              coverage_pct=65,
              threshold=70)

# Error
logger.error("error",
            error_type="validation_failure",
            validator="mypy",
            file="auth.py",
            line=42,
            message="Type annotation missing")

# Task completion
logger.info("task_end",
           task_id="TASK-001",
           outcome="success",
           duration_seconds=14400,
           artifacts_created=7)

# Session summary
logger.info("session_summary",
           session_id="QSE-20251114-1530-abc123",
           project_id="P-CFWORK-001",
           tasks_completed=3,
           artifacts_created=21,
           warnings=2,
           errors=0,
           evidence_bundles=3)
```

### PowerShell Implementation

```powershell
Import-Module ContextForge.Spectre

# Session start
Write-CFLog -Event "session_start" -Data @{
    session_id = "QSE-20251114-1530-abc123"
    project_id = "P-CFWORK-001"
    user = "james.hardy1124@gmail.com"
}

# Task start
Write-CFLog -Event "task_start" -Data @{
    task_id = "TASK-001"
    task_name = "Deploy authentication service"
    estimated_hours = 2.0
}

# Decision point
Write-CFLog -Event "decision" -Data @{
    decision_type = "deployment_strategy"
    selected = "blue_green"
    rationale = "Zero-downtime requirement"
    confidence = 0.9
}

# Artifact emit
Write-CFLog -Event "artifact_emit" -Data @{
    artifact_path = "deploy\auth-service.yaml"
    artifact_type = "kubernetes_manifest"
    hash = (Get-FileHash deploy\auth-service.yaml).Hash
    size_bytes = 2048
}

# Task completion
Write-CFLog -Event "task_end" -Data @{
    task_id = "TASK-001"
    outcome = "success"
    duration_seconds = 7200
}
```

---

## Auto-Promotion Triggers

**UnifiedLogger automatically increases verbosity when**:

### Verbose Level
- Estimated duration ≥10 seconds
- Files touched ≥40
- Complex operation detected

### Trace Level
- Artifacts written ≥5
- Failure retry count ≥2
- Debugging mode enabled

### Evidence Level
- Public API change detected
- High-risk operation flagged
- Compliance requirement triggered

**Manual Override**:
```python
# Force evidence-level logging
with logger.evidence_mode():
    perform_high_risk_operation()
```

---

## Evidence Bundle Requirements

### Structure

Every evidence bundle must contain:

```json
{
  "correlation_id": "QSE-20251114-1530-abc123",
  "project_id": "P-CFWORK-001",
  "session_id": "QSE-20251114-1530-abc123",
  "task_id": "TASK-001",
  "created_at": "2025-11-14T15:30:00Z",
  "artifacts": [
    {
      "path": ".qse/v2/Artifacts/P-CFWORK-001/ExecutionPlan-001.yaml",
      "type": "execution_plan",
      "hash": "sha256:abc123def456...",
      "size_bytes": 4096
    }
  ],
  "logs": [
    {"timestamp": "2025-11-14T15:30:01Z", "event": "session_start", ...},
    {"timestamp": "2025-11-14T15:30:02Z", "event": "task_start", ...}
  ],
  "decisions": [
    {
      "decision_id": "DEC-001",
      "type": "architecture",
      "selected": "oauth2",
      "alternatives": ["custom_auth", "saml"],
      "rationale": "Industry standard, SaaS availability",
      "confidence": 0.85
    }
  ],
  "validation": {
    "quality_gates_passed": ["python_ruff", "mypy_strict", "pytest_coverage"],
    "quality_gates_failed": [],
    "cof_completeness": 13,
    "ucl_compliance": true
  }
}
```

### Storage Location

```
.QSE/v2/Evidence/
└── {projectId}/
    └── {sessionId}/
        ├── evidence-bundle-{timestamp}.jsonl
        ├── artifacts/
        │   ├── ExecutionPlan-001.yaml
        │   └── TestResults-001.json
        └── logs/
            └── session-log-{timestamp}.yaml
```

---

## Logging Coverage Standards

### Python Projects

**Tool**: `pytest-cov`

**Target**: ≥90% statement coverage for logging events

**Validation**:
```bash
pytest --cov=python --cov-report=term-missing --cov-fail-under=90 -m logging_coverage
```

**Exemptions**:
- Trivial getters/setters (if properly annotated)
- Vendored third-party code
- Generated code (protobuf, etc.)

### PowerShell Projects

**Tool**: Pester with custom logging coverage analysis

**Target**: ≥70% function coverage for logging events

**Validation**:
```powershell
Invoke-Pester -Path tests\ -CodeCoverage src\*.ps1 -CodeCoverageThreshold 0.7
```

---

## Structured Logging Format

### JSON Lines (JSONL)

**All logs must be valid JSON Lines format**:

```jsonl
{"timestamp":"2025-11-14T15:30:00Z","level":"info","event":"session_start","session_id":"QSE-20251114-1530-abc123","project_id":"P-CFWORK-001"}
{"timestamp":"2025-11-14T15:30:01Z","level":"info","event":"task_start","task_id":"TASK-001","task_name":"Implement JWT authentication"}
{"timestamp":"2025-11-14T15:32:15Z","level":"warning","event":"warning","warning_type":"test_coverage_low","module":"auth.py","coverage_pct":65}
{"timestamp":"2025-11-14T15:35:00Z","level":"info","event":"task_end","task_id":"TASK-001","outcome":"success","duration_seconds":240}
```

**Benefits**:
- Streamable (process line-by-line)
- Parseable (standard JSON per line)
- Queryable (DuckDB, jq, grep)
- Efficient (no array wrappers)

---

## Credential Redaction

### Automatic Redaction

**UnifiedLogger automatically redacts**:
- `password`, `passwd`, `pwd`
- `token`, `api_key`, `secret`
- `connectionString`, `connection_string`
- `authorization` header values
- Any field containing `_secret` or `_key`

**Example**:
```python
logger.info("database_connect",
           host="172.25.14.122",
           port=5432,
           database="taskman_v2",
           password="SuperSecret123")  # Automatically redacted

# Logged as:
# {"host":"172.25.14.122","port":5432,"database":"taskman_v2","password":"***REDACTED***"}
```

### Manual Redaction

```python
from python.services.unified_logger import redact

sensitive_data = {
    "username": "admin",
    "password": "P@ssw0rd!",
    "api_token": "sk-1234567890abcdef"
}

logger.info("auth_attempt", **redact(sensitive_data))
# {"username":"admin","password":"***REDACTED***","api_token":"***REDACTED***"}
```

---

## Session Log Requirements

### Session Log Format

**Filename**: `QSE-LOG-[shortContext]-[YYYYMMDD]-[SEQ].yaml`

**Structure**:
```yaml
session:
  id: "QSE-20251114-1530-abc123"
  project_id: "P-CFWORK-001"
  project_name: "TaskMan v2 Migration"
  phase: "Implementation"
  started_at: "2025-11-14T15:30:00Z"
  ended_at: "2025-11-14T18:45:00Z"
  duration_seconds: 11700

tasks:
  - id: "TASK-001"
    name: "Implement JWT authentication"
    status: "completed"
    outcome: "success"
    duration_seconds: 14400
    artifacts_created: 7
    evidence_bundle: "EB-TASK-001-20251114.tar.gz"

decisions:
  - id: "DEC-001"
    type: "architecture"
    description: "OAuth2 vs custom authentication"
    selected: "oauth2"
    confidence: 0.85
    rationale: "Industry standard, SaaS availability, security audit ready"

artifacts:
  created:
    - path: ".qse/v2/Artifacts/P-CFWORK-001/ExecutionPlan-001.yaml"
      type: "execution_plan"
      hash: "sha256:abc123def456..."
    - path: "src/auth/jwt_handler.py"
      type: "source_code"
      hash: "sha256:def789ghi012..."

  modified:
    - path: "requirements.txt"
      hash_before: "sha256:old123..."
      hash_after: "sha256:new456..."

evidence:
  bundles:
    - id: "EB-TASK-001-20251114"
      path: ".QSE/v2/Evidence/P-CFWORK-001/QSE-20251114-1530-abc123/evidence-bundle-001.jsonl"
      hash: "sha256:evidence789..."
      size_bytes: 524288

quality_gates:
  passed:
    - "python_ruff"
    - "mypy_strict"
    - "pytest_coverage_70"
    - "cof_completeness"
    - "ucl_compliance"
  failed: []

mcp_tools_invoked:
  - tool: "vibe-check-mcp/constitution_check"
    invocations: 15
    outcomes: ["session_id_synced"]
  - tool: "vibe-check-mcp/vibe_check"
    invocations: 2
    outcomes: ["guidance_provided"]
  - tool: "SeqThinking/sequential_thinking"
    invocations: 8
    outcomes: ["reasoning_logged"]
  - tool: "digitarald.agent-memory/memory"
    invocations: 3
    outcomes: ["lessons_stored"]

summary:
  tasks_completed: 3
  artifacts_created: 21
  artifacts_modified: 5
  warnings: 2
  errors: 0
  evidence_bundles: 3
  quality_gates_passed: 5
  quality_gates_failed: 0
```

---

## Logging Deficit Detection

### Automated Detection

**UnifiedLogger tracks expected vs. actual logging**:

```python
def detect_logging_deficit(operation):
    """Detect missing logs for an operation."""
    expected_events = get_expected_events(operation)
    actual_events = get_logged_events(operation.id)

    missing_events = set(expected_events) - set(actual_events)

    if missing_events:
        logger.warning("logging_deficit",
                      operation_id=operation.id,
                      missing_events=list(missing_events),
                      coverage_pct=len(actual_events) / len(expected_events) * 100)
```

### Manual Review

**Check for missing events**:
```bash
# Python
pytest -m logging_deficit_check

# PowerShell
Invoke-Pester -Tag LoggingDeficit
```

---

## Verification Logging (Evidence Artifacts)

**Lesson Learned**: 2025-12-24 AAR — False claims made without evidence artifacts.

### Log-Before-Conclude Rule (LBC)

All verification commands MUST create evidence artifacts **BEFORE** making any claim:

1. **Format**: `logs/{topic}-{YYYY-MM-DD-HHMM}.txt`
2. **Content**: Raw command output, no interpretation
3. **Access**: Use `read_file` tool for reliable reading (not truncated terminal output)
4. **Citation**: Every claim references the log file path

### Verification Workflow

```powershell
# 1. Create log file
Get-ChildItem -Recurse -Filter "*.py" | Select-String "pattern" | Out-File "logs/verification-2025-12-24.txt" -Force

# 2. Wait for command to complete (terminal output)

# 3. Read log file with read_file tool
# read_file("logs/verification-2025-12-24.txt", 1, 100)

# 4. THEN make claim citing file
# "Based on logs/verification-2025-12-24.txt, X was found/not found"
```

### Zero-Claim Challenge (ZCC)

When claiming "zero", "none", "clean", or "no matches":

1. **Primary verification** → Create log file 1
2. **Secondary verification** (different approach) → Create log file 2
3. **Both must agree** before making the claim
4. **Document both** in any assertion

```markdown
✅ "Based on logs/import-check.txt (0 matches) and logs/grep-verify.txt (0 matches), no imports remain."
❌ "Verified - zero imports" (no evidence citation)
```

---

## Anti-Patterns to Avoid

❌ Making verification claims without log file evidence
❌ Proceeding before terminal output completes
❌ Claiming "zero/none" without secondary verification
❌ Logging sensitive data without redaction
❌ Skipping session_start or session_summary events
❌ Creating artifacts without artifact_emit logs
❌ Not logging decisions at branch points
❌ Missing task_end after task_start
❌ Using print() instead of structured logging
❌ Inconsistent timestamp formats (always ISO 8601)

---

## Definition of Done (Logging)

✅ All baseline events present for operation
✅ ≥90% execution path coverage (Python) or ≥70% (PowerShell)
✅ Session log finalized with project ID and summary
✅ Evidence bundles generated with all artifacts hashed
✅ No sensitive data in logs (automatic redaction verified)
✅ JSONL format validated (jq or DuckDB parseable)
✅ Logging deficit checks passing
✅ MCP tool invocations logged for audit trail

---

**See Also**:
- [09-Development-Guidelines.md](docs/09-Development-Guidelines.md) — Development standards
- `.github/instructions/quality-gates.instructions.md` — Validation requirements
- `.github/instructions/agent-core.instructions.md` — MCP tool logging
