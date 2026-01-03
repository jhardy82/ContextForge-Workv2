# 15 – Future Roadmap

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [09-Development-Guidelines](09-Development-Guidelines.md)

---

## Overview

This roadmap defines ContextForge's strategic direction through 2027, covering production blockers, platform consolidation, observability enhancement, and innovation initiatives. The roadmap aligns with the 11 Core Philosophies and Sacred Geometry patterns.

### Strategic Vision

**Mission**: Transform ContextForge from development platform to enterprise-grade, AI-native work orchestration system.

**Core Pillars**:
1. **Unified Platform** - CF_Core CLI as single entry point
2. **Production Ready** - TaskMan-v2 deployed with confidence
3. **Observable** - Comprehensive metrics, tracing, logging
4. **Extensible** - Plugin architecture for rapid feature addition
5. **Secure** - Zero-trust security posture

---

## Current State Assessment

### Documentation Maturity

| Category | Completed | Total | Progress | Status |
|----------|-----------|-------|----------|--------|
| **Foundation** | 3/3 | 100% | ✅ Complete | Architecture, COF, Overview |
| **Application** | 3/3 | 100% | ✅ Complete | TaskMan-v2, API, UI |
| **Data & Storage** | 1/1 | 100% | ✅ Complete | Database Design |
| **Engineering Standards** | 4/4 | 100% | ✅ Complete | Guidelines, API, Config, Testing |
| **Operations** | 2/2 | 100% | ✅ Complete | Security, Deployment |
| **Strategic** | 0/2 | 0% | 🔄 In Progress | Roadmap, Optimization |
| **Total** | 11/15 | **73%** | 🔄 In Progress | 4 documents remaining |

**Line Counts**:
- Completed: 8,814 lines
- Target: ~12,700 lines
- Remaining: ~3,900 lines

### TaskMan-v2 Production Readiness

**Overall**: 75% Production Ready

| Component | Status | Progress | Blockers |
|-----------|--------|----------|----------|
| **React 19 Frontend** | ✅ Complete | 100% | None |
| **FastAPI Backend** | ✅ Complete | 95% | P0-005 (JWT auth) |
| **PostgreSQL Schema** | ✅ Complete | 100% | None |
| **DuckDB Analytics** | ✅ Complete | 100% | None |
| **CI/CD Pipeline** | ⚠️ Partial | 40% | P0-006 (automation) |
| **JWT Authentication** | 🔲 Planned | 0% | P0-005 (blocker) |
| **Logging** | ✅ Complete | 100% | None |
| **Docker Deployment** | ✅ Complete | 90% | None |
| **Kubernetes** | 🔲 Planned | 0% | None |

### Test Infrastructure Health

**QSE Framework**: Production Active
- **428 test files** across Python, PowerShell, TypeScript
- **2,226 tests** total (95.8% collection success)
- **93 collection errors** cataloged for remediation

**Coverage Status**:
- Unit Tests: 70% target (current: ~60%)
- Integration Tests: 40% target (current: ~30%)
- System Tests: 25% target (current: ~20%)
- **Branch Coverage**: 0.4% actual → **70% target** (CRITICAL GAP)

**18 GitHub Actions Workflows**:
- 7 blocking workflows
- 11 advisory workflows
- Quality gate enforcement active

### CLI Consolidation Status

**Status**: ✅ **Phase 1 COMPLETE** (December 2025)

**Current State**:
- `cf_core.cli.main` - **PRIMARY unified interface** (task, sprint, project management)
- Legacy CLIs (`dbcli`, `cf_cli`, `tasks_cli`) - **DEPRECATED**

**Completed**:
- Modular CLI architecture implemented (`cf_core/cli/`)
- Task, sprint, project CRUD commands operational
- Machine mode (`--machine`) for AI agent consumption
- Health check and database connectivity commands

**Remaining Work** (Phase 2):
- Migrate remaining dbcli specialty commands (velocity, context)
- Full deprecation removal of legacy CLIs
- CLI plugin architecture for extensibility

See [docs/CLI-REFERENCE.md](CLI-REFERENCE.md) for current command reference.

---

## P0 Blockers (Q1 2026) - Production Critical

### P0-005: JWT Authentication Implementation

**Priority**: CRITICAL 🔥
**Status**: Planned
**Effort**: 3-4 weeks
**Dependencies**: None
**Owner**: Backend Team

**Scope**:
- JWT token generation and verification
- RBAC with 4 roles (Admin, Developer, Viewer, Guest)
- FastAPI middleware integration
- Token refresh mechanism
- Secret management (Azure Key Vault / AWS Secrets Manager)

**Implementation Plan**:
```python
# backend-api/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract user payload."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Usage in routes
@router.post("/tasks")
async def create_task(
    task: TaskCreate,
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create task (authenticated users only)."""
    ...
```

**Success Criteria**:
- ✅ All API endpoints protected
- ✅ RBAC enforced per route
- ✅ Token refresh functional
- ✅ Secrets managed externally
- ✅ Integration tests pass

**Unblocks**: TaskMan-v2 production deployment

---

### P0-006: TaskMan-v2 CI/CD Pipeline

**Priority**: CRITICAL 🔥
**Status**: Partial (40% complete)
**Effort**: 2-3 weeks
**Dependencies**: P0-005 (JWT auth for deployment)
**Owner**: DevOps Team

**Current State**:
- 18 GitHub Actions workflows (7 blocking, 11 advisory)
- Basic linting and unit tests
- No automated deployment

**Required Capabilities**:
1. **Build Pipeline**
   - Frontend: Vite build, TypeScript check
   - Backend: Python package, dependency check
   - Docker: Multi-stage builds

2. **Test Pipeline**
   - Unit tests (pytest, Vitest)
   - Integration tests (API contracts)
   - E2E tests (Playwright)
   - Security scans (Bandit, npm audit)

3. **Deployment Pipeline**
   - Blue-green deployments
   - Database migrations (Alembic)
   - Health checks
   - Rollback capability

4. **Quality Gates**
   - Test coverage thresholds
   - Code quality (SonarQube)
   - Performance benchmarks
   - Security scan pass

**GitHub Actions Workflow Example**:
```yaml
name: TaskMan-v2 CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest --cov=backend --cov-report=xml
      - name: Check coverage threshold
        run: |
          coverage report --fail-under=70

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry
        run: docker-compose push

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl apply -f k8s/production/
          kubectl rollout status deployment/taskman-backend
```

**Success Criteria**:
- ✅ Automated build on every commit
- ✅ Test coverage gates enforced
- ✅ Blue-green deployments functional
- ✅ Rollback tested
- ✅ Zero-downtime deployments

**Unblocks**: Continuous deployment to production

---

### P0-007: Branch Coverage Remediation

**Priority**: HIGH ⚠️
**Status**: Planned
**Effort**: 6-8 weeks
**Dependencies**: Test infrastructure review
**Owner**: Quality Team

**Current State**:
- **0.4% branch coverage** (actual)
- **70% target** (required for production confidence)
- Gap: 69.6 percentage points

**Root Causes**:
1. Focus on unit tests over integration tests
2. Missing edge case coverage
3. Error handling paths untested
4. Configuration branches not exercised

**Remediation Strategy**:

**Phase 1: Assessment** (1 week)
- Run coverage analysis with pytest-cov
- Identify critical paths with 0% coverage
- Prioritize by risk (security, data integrity, core workflows)

**Phase 2: Core Path Coverage** (3 weeks)
- Target: 40% branch coverage
- Focus: Critical user workflows
- Happy paths + primary error cases

**Phase 3: Edge Case Coverage** (2 weeks)
- Target: 60% branch coverage
- Focus: Error handling, validation, edge cases

**Phase 4: Comprehensive Coverage** (2 weeks)
- Target: 70% branch coverage
- Focus: Configuration branches, fallback logic

**Example Coverage Improvement**:
```python
# Before: 0% branch coverage
def process_task(task_id: str):
    task = get_task(task_id)
    update_status(task, "completed")

# After: 100% branch coverage
def process_task(task_id: str):
    """Process task with comprehensive error handling."""
    try:
        task = get_task(task_id)
        if not task:
            logger.error("task_not_found", task_id=task_id)
            return Result.failure("Task not found")

        if task.status == "completed":
            logger.warning("task_already_completed", task_id=task_id)
            return Result.success("Already completed")

        update_status(task, "completed")
        logger.info("task_completed", task_id=task_id)
        return Result.success("Task completed")

    except DatabaseError as e:
        logger.error("database_error", task_id=task_id, error=str(e))
        return Result.failure("Database error")

# Test coverage
def test_process_task_success():
    """Test happy path."""
    assert process_task("TASK-001").is_success

def test_process_task_not_found():
    """Test task not found branch."""
    assert process_task("INVALID").is_failure

def test_process_task_already_completed():
    """Test already completed branch."""
    # Pre-condition: task already completed
    assert process_task("TASK-002").is_success

def test_process_task_database_error():
    """Test database error branch."""
    with mock.patch('get_task', side_effect=DatabaseError):
        assert process_task("TASK-003").is_failure
```

**Success Criteria**:
- ✅ 70% branch coverage achieved
- ✅ All critical paths covered
- ✅ Error handling tested
- ✅ CI gates enforced

---

### P0-008: Test Collection Errors Resolution

**Priority**: MEDIUM
**Status**: In Progress
**Effort**: 3-4 weeks
**Dependencies**: None
**Owner**: Quality Team

**Current State**:
- 95.8% collection success (2,226 collected, 93 errors)
- 428 test files
- Errors cataloged but not remediated

**Error Categories**:
1. **Import Errors** (40%): Missing dependencies, module not found
2. **Syntax Errors** (20%): Python 3.11 compatibility issues
3. **Configuration Errors** (25%): Pytest fixtures missing
4. **Path Errors** (15%): Incorrect relative imports

**Remediation Plan**:

**Week 1: Triage**
- Categorize all 93 errors
- Identify quick wins (fix in <30 min each)
- Defer non-critical legacy tests

**Week 2-3: Fix Import and Syntax Errors**
- Resolve missing dependencies
- Update deprecated syntax
- Fix Python 3.11 compatibility

**Week 4: Configuration and Path Errors**
- Standardize pytest fixtures
- Fix relative import paths
- Update test discovery patterns

**Target**: 99%+ collection success (≤5 deferred errors)

---

## P1 Priorities (Q2 2026) - Strategic Enhancements

### CF_Core CLI Consolidation (Phase 2-3)

**Priority**: HIGH
**Status**: Phase 1 Complete (Planning)
**Effort**: 10-14 weeks
**Dependencies**: None
**Owner**: Platform Team

**Strategic Goal**: Unified CF_Core CLI as PRIMARY interface for entire ecosystem

**Current State**:
- 5 fragmented CLIs (~12,300 scattered lines)
- Inconsistent UX and documentation
- User pain points: "Which CLI do I use?"

**Target State**:
- Single `cf-core` command with plugin architecture
- 7 core plugins (tasks, db, velocity, qse, logs, context, config)
- Consistent argument patterns, output formatting
- <8,000 consolidated lines

**5-Phase Roadmap**:

#### Phase 1: Documentation and Planning ✅ (Complete)
- CF_Core CLI Consolidation Roadmap
- Plugin architecture guide
- Component mapping
- Backward compatibility strategy

#### Phase 2: Core Consolidation (Weeks 1-4)
**Deliverables**:
- Core CLI framework with plugin discovery
- 3 essential plugins (tasks, context, config)
- Unit tests (>80% coverage)
- Developer documentation

```python
# Plugin architecture
from cf_cli.core import BasePlugin

class TasksPlugin(BasePlugin):
    """Tasks plugin for CF_Core CLI."""

    name = "tasks"
    description = "Task management operations"

    def register(self, app):
        """Register tasks commands."""
        @app.command()
        def list(status: str = None):
            """List tasks with optional filtering."""
            ...
```

#### Phase 3: Plugin Migration (Weeks 5-10)
**Deliverables**:
- 4 additional plugins (db, velocity, qse, logs)
- Legacy wrapper implementation
- Migration guides
- Test coverage >75%

#### Phase 4: Legacy Deprecation (Weeks 11-13)
**Deliverables**:
- Deprecation warnings in legacy CLIs
- Automated migration helper
- Internal scripts migrated
- 6-week transition period begins

#### Phase 5: Full Transition (Weeks 14+)
**Deliverables**:
- CF_Core CLI v1.0.0 release
- Legacy code archived
- 100% internal adoption
- User satisfaction >90%

**Success Metrics**:
- Code consolidation: 12,300 → <8,000 lines (35% reduction)
- CLI count: 5 → 1 PRIMARY
- Test coverage: >80% core, >75% plugins
- User onboarding: 2 hours → <30 minutes

---

### PostgreSQL Migration Complete

**Priority**: HIGH
**Status**: 90% Complete
**Effort**: 2-3 weeks
**Dependencies**: None
**Owner**: Infrastructure Team

**Current State**:
- PostgreSQL 15+ operational at 172.25.14.122:5432/taskman_v2
- SQLite legacy data at db/trackers.sqlite
- CSV constants deprecated (direct_csv_access_blocked)

**Remaining Work**:
1. **Data Migration Validation**
   - Verify all legacy SQLite data migrated
   - Validate data integrity (checksums)
   - Confirm no data loss

2. **SQLite Deprecation**
   - Remove SQLite as primary authority
   - Convert to read-only legacy archive
   - Update all documentation references

3. **CSV Constant Removal**
   - Remove hardcoded CSV paths
   - Update tests to use PostgreSQL
   - Validate no CSV references remain

**Success Criteria**:
- ✅ PostgreSQL is ONLY primary authority
- ✅ SQLite read-only or archived
- ✅ CSV constants removed
- ✅ All tests use PostgreSQL
- ✅ Documentation updated

---

## P2 Strategic Features (H2 2026) - Platform Evolution

### Kubernetes Orchestration

**Priority**: MEDIUM
**Status**: Planned
**Effort**: 6-8 weeks
**Dependencies**: P0-006 (CI/CD), Docker deployment
**Owner**: DevOps Team

**Scope**:
- Kubernetes manifests for TaskMan-v2
- Helm charts for deployment
- Horizontal pod autoscaling
- Service mesh integration (Istio)
- Ingress configuration
- Persistent volume management

**Deployment Architecture**:
```
┌─────────────────────────────────────────────────────┐
│                   Ingress (NGINX)                   │
│              https://contextforge.dev               │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────┐           ┌──────▼────┐
    │ Frontend │           │  Backend  │
    │  (React) │           │ (FastAPI) │
    │ 3 replicas           │ 5 replicas│
    └──────────┘           └──────┬────┘
                                  │
                          ┌───────▼────────┐
                          │   PostgreSQL   │
                          │   StatefulSet  │
                          │   (Primary +   │
                          │    Replicas)   │
                          └────────────────┘
```

**Helm Chart Example**:
```yaml
# helm/taskman-v2/values.yaml
replicaCount:
  frontend: 3
  backend: 5

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: contextforge.dev
      paths:
        - path: /
          pathType: Prefix

postgresql:
  enabled: true
  primary:
    persistence:
      enabled: true
      size: 100Gi
  readReplicas:
    replicaCount: 2
```

**Success Criteria**:
- ✅ Zero-downtime deployments
- ✅ Auto-scaling functional
- ✅ 99.9% uptime SLA
- ✅ Disaster recovery tested

---

### Observability Platform (Loki + Grafana + Prometheus)

**Priority**: MEDIUM
**Status**: Planned
**Effort**: 4-6 weeks
**Dependencies**: Kubernetes deployment
**Owner**: SRE Team

**Scope**:

#### 1. Loki Log Aggregation
- Centralized JSONL log storage
- Log querying and filtering (LogQL)
- Retention policies (30 days hot, 1 year cold)
- Alert rules on log patterns

**Configuration**:
```yaml
# loki/config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2025-01-01
      store: boltdb-shipper
      object_store: s3
      schema: v11
      index:
        prefix: loki_index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
  aws:
    s3: s3://contextforge-loki
    region: us-east-1
```

#### 2. Grafana Dashboards
- System health dashboard
- Application metrics dashboard
- User activity dashboard
- Error rate dashboard
- Performance dashboard

**Dashboard Panels**:
1. Request rate (req/s)
2. Response time (p50, p95, p99)
3. Error rate (%)
4. Database connection pool usage
5. Task creation velocity
6. User active sessions

#### 3. Prometheus Metrics
- Application metrics (custom)
- System metrics (node_exporter)
- Database metrics (postgres_exporter)
- Alerting rules

**Metrics Example**:
```python
# backend-api/metrics.py
from prometheus_client import Counter, Histogram, Gauge

task_created_counter = Counter(
    'taskman_tasks_created_total',
    'Total number of tasks created',
    ['status', 'priority']
)

task_duration_histogram = Histogram(
    'taskman_task_duration_seconds',
    'Task completion duration',
    ['task_type']
)

active_users_gauge = Gauge(
    'taskman_active_users',
    'Number of currently active users'
)

# Usage
@router.post("/tasks")
async def create_task(task: TaskCreate):
    task_created_counter.labels(
        status=task.status,
        priority=task.priority
    ).inc()
    ...
```

**Alerting Rules**:
```yaml
# prometheus/alerts.yaml
groups:
  - name: taskman_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} req/s"

      - alert: DatabaseConnectionPoolExhausted
        expr: database_connections_active / database_connections_max > 0.9
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool near capacity"
```

**Success Criteria**:
- ✅ All logs aggregated in Loki
- ✅ 10+ Grafana dashboards operational
- ✅ Real-time alerting functional
- ✅ MTTR (Mean Time To Recovery) <15 minutes

---

### Advanced MCP Integrations

**Priority**: MEDIUM
**Status**: Operational (11 Servers Active)
**Effort**: 2-3 weeks (enhancement only)
**Dependencies**: None
**Owner**: AI Team

**Current State (2025-11-29)**:
- **11 MCP servers operational** via STDIO transport
- Linear integration (SSE remote) for issue tracking
- Database-mcp for PostgreSQL/SQLite operations
- Cognitive reasoning (SeqThinking, vibe-check-mcp)
- Documentation access (context7, microsoft.docs.mcp)
- DuckDB velocity/dashboard analytics

**Operational Servers**:
| Server | Transport | Status | Purpose |
|--------|-----------|--------|---------|
| task-manager | STDIO | ✅ Active | Task/project management |
| database-mcp | STDIO | ✅ Active | Multi-DB operations |
| DuckDB-velocity | STDIO | ✅ Active | Velocity analytics |
| DuckDB-dashboard | STDIO | ✅ Active | Dashboard history |
| SeqThinking | STDIO | ✅ Active | Complex reasoning |
| vibe-check-mcp | STDIO | ✅ Active | Metacognitive checks |
| Memory | STDIO | ✅ Active | Cross-session context |
| linear | SSE | ✅ Active | Linear issue tracking |
| context7 | STDIO | ✅ Active | Library docs |
| microsoft.docs.mcp | STDIO | ✅ Active | Azure/MS docs |
| magic | STDIO | ✅ Active | 21st.dev AI |

**Expansion Scope**:

#### 1. Enhanced Task Operations
```typescript
// New MCP tools
const advanced_mcp_tools = [
  {
    name: "analyze_task_blockers",
    description: "AI analysis of task blockers and recommendations",
    inputSchema: {
      task_id: { type: "string" },
      include_suggestions: { type: "boolean", default: true }
    }
  },
  {
    name: "estimate_task_complexity",
    description: "ML-based task complexity estimation",
    inputSchema: {
      task_description: { type: "string" },
      historical_context: { type: "boolean", default: true }
    }
  },
  {
    name: "suggest_similar_tasks",
    description: "Find similar tasks using embedding similarity",
    inputSchema: {
      task_id: { type: "string" },
      limit: { type: "number", default: 5 }
    }
  }
];
```

#### 2. Context-Aware Suggestions
- COF 13-dimensional analysis integration
- Pattern recognition across historical tasks
- Workflow optimization suggestions

#### 3. Natural Language Queries
```python
# MCP tool: natural_language_query
@mcp.tool()
async def natural_language_query(query: str) -> dict:
    """Execute natural language queries against task database."""
    # Example: "Show all high-priority tasks created last week"

    # Parse query using LLM
    parsed = await llm.parse_query(query)

    # Convert to SQL
    sql = generate_sql(parsed)

    # Execute and format
    results = await db.execute(sql)
    return format_results(results)
```

**Success Criteria**:
- ✅ 10+ new MCP tools
- ✅ Natural language queries functional
- ✅ AI accuracy >80%
- ✅ Response time <2 seconds

---

## P3 Innovation Track (2027+) - Future Vision

### Idea Capture System

**Priority**: LOW
**Status**: Placeholder Documentation
**Effort**: 8-10 weeks
**Dependencies**: Document 06 completion
**Owner**: Product Team

**Vision**: Context-aware idea capture with automatic COF 13-dimensional enrichment

**Key Features**:
1. **Rapid Capture**
   - CLI: `cf-core idea capture "Quick thought..."`
   - API: POST /api/v1/ideas
   - Voice: Transcription → COF enrichment
   - MCP: AI-assisted capture via Claude

2. **COF Integration**
   - Automatic dimension analysis
   - Required: Motivational, Relational, Validation
   - Optional: Context-dependent dimensions
   - Templates for common idea types

3. **Idea → Task Promotion**
   - One-click task creation
   - COF dimensions preserved
   - Evidence bundle generation
   - Workflow Designer integration

4. **Search & Retrieval**
   - Full-text search
   - Graph relationships
   - Dimension-based filtering
   - Similar idea suggestions (embeddings)

**Database Schema**:
```sql
CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- COF Dimensions (13)
    cof_motivational TEXT,
    cof_relational TEXT,
    cof_dimensional TEXT,
    cof_situational TEXT,
    cof_resource TEXT,
    cof_narrative TEXT,
    cof_recursive TEXT,
    cof_computational TEXT,
    cof_emergent TEXT,
    cof_temporal TEXT,
    cof_spatial TEXT,
    cof_holistic TEXT,
    cof_validation TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    promoted_to_task_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'captured',  -- captured, refined, promoted, archived

    -- Search
    embedding VECTOR(1536)  -- For similarity search
);

CREATE INDEX idx_ideas_embedding ON ideas USING ivfflat (embedding);
```

**See**: [06-Idea-Capture-System.md](06-Idea-Capture-System.md) (planned)

---

### Workflow Designer (Sacred Geometry UI)

**Priority**: LOW
**Status**: Placeholder Documentation
**Effort**: 10-12 weeks
**Dependencies**: Document 07 completion, ContextForge.Spectre stable
**Owner**: UI/UX Team

**Vision**: Visual workflow builder using Sacred Geometry patterns as design language

**Sacred Geometry Workflow Patterns**:

1. **Triangle (Stability)**: 3-stage workflows
   ```
   Plan → Execute → Verify
   ```

2. **Circle (Completeness)**: Closed-loop workflows
   ```
   Start → Process → Validate → (back to Start or Complete)
   ```

3. **Spiral (Iteration)**: Iterative workflows
   ```
   Sprint Planning → Development → Testing → Retrospective → (next sprint)
   ```

4. **Golden Ratio (Balance)**: Balanced workflows
   ```
   35% Planning / 65% Execution
   ```

5. **Fractal (Modularity)**: Nested workflows
   ```
   Parent workflow contains sub-workflows maintaining same pattern
   ```

**Visual Designer Features**:
- Drag-and-drop workflow nodes
- Sacred Geometry templates
- Real-time validation
- Export to TaskMan-v2 tasks
- UTMW phase integration
- Progress visualization

**ContextForge.Spectre Integration**:
```powershell
# PowerShell-based Sacred Geometry rendering
Import-Module ContextForge.Spectre

# Render workflow as Sacred Geometry
$workflow = @{
    Pattern = "Spiral"
    Phases = @("Plan", "Execute", "Review", "Iterate")
    CurrentPhase = "Execute"
}

Show-CFWorkflowVisualization -Workflow $workflow -Geometry Spiral
```

**See**: [07-Workflow-Designer.md](07-Workflow-Designer.md) (planned)

---

## Deprecation & Sunset Timeline

### Legacy CLI Retirement

**Timeline**: Q2-Q3 2026 (aligned with CF_Core CLI Phase 4-5)

| Quarter | Component | Action | Status |
|---------|-----------|--------|--------|
| **Q2 2026** | dbcli | Wrapper with deprecation warnings | Planned |
| **Q2 2026** | TaskMan CLI | Wrapper with deprecation warnings | Planned |
| **Q2 2026** | Velocity CLI | Integration into cf-core | Planned |
| **Q3 2026** | Legacy scripts | Archive or migrate | Planned |
| **Q3 2026** | All wrappers | Remove after 6-week grace period | Planned |

**Transition Support**:
- 6-week deprecation warnings
- Automated migration scripts
- Comprehensive migration guides
- Internal training sessions

---

### SQLite Authority Sunset

**Timeline**: Q1 2026 (aligned with PostgreSQL migration complete)

**Phases**:
1. **Q4 2025**: PostgreSQL primary authority confirmed ✅
2. **Q1 2026**: SQLite demoted to read-only legacy
3. **Q1 2026**: CSV constants removed
4. **Q2 2026**: SQLite archived or retired

**Migration Complete Criteria**:
- ✅ All write operations use PostgreSQL
- ✅ No code references SQLite as authority
- ✅ CSV constants removed from codebase
- ✅ Legacy data archived or preserved

---

### CSV Constants Removal

**Timeline**: Q1 2026

**Current Status**: `direct_csv_access_blocked` sentinel active

**Removal Plan**:
1. Validate no active CSV write operations
2. Remove hardcoded CSV paths
3. Update tests to use PostgreSQL or DuckDB
4. Archive legacy CSV data
5. Remove `direct_csv_access_blocked` check (no longer needed)

---

## Success Metrics & KPIs

### Technical Excellence

| Metric | Baseline | Q1 2026 | Q2 2026 | Q4 2026 | Measurement |
|--------|----------|---------|---------|---------|-------------|
| **Documentation Completion** | 73% (11/15) | 100% (15/15) | 100% | 100% | Doc count |
| **Branch Coverage** | 0.4% | 25% | 50% | 70% | pytest --cov |
| **Test Collection Success** | 95.8% | 98% | 99% | 99.5% | pytest collection |
| **CLI Consolidation** | 5 CLIs | 2 CLIs | 1 CLI | 1 CLI | Command count |
| **Code Duplication** | 12,300 lines | 10,000 | 8,500 | <8,000 | SLOC analysis |
| **Build Success Rate** | 85% | 95% | 98% | 99% | CI/CD metrics |

### Platform Maturity

| Metric | Baseline | Q1 2026 | Q2 2026 | Q4 2026 | Measurement |
|--------|----------|---------|---------|---------|-------------|
| **TaskMan-v2 Production Readiness** | 75% | 95% | 100% | 100% | Component checklist |
| **Deployment Automation** | 40% | 80% | 95% | 99% | CI/CD coverage |
| **Observability Coverage** | 30% | 60% | 85% | 95% | Metrics/logs/traces |
| **Security Posture** | Medium | High | High | Very High | Security audit |

### User Experience

| Metric | Baseline | Q1 2026 | Q2 2026 | Q4 2026 | Measurement |
|--------|----------|---------|---------|---------|-------------|
| **CLI Onboarding Time** | 2 hours | 1 hour | 45 min | <30 min | User testing |
| **Command Discoverability** | Low | Medium | High | High | User survey |
| **User Satisfaction** | N/A | 75% | 85% | >90% | Internal survey |
| **Support Ticket Volume** | Baseline | -20% | -40% | -50% | Ticket count |

---

## Risk Assessment & Mitigation

### High Risk: P0 Blocker Delays

**Risk**: P0-005 (JWT) or P0-006 (CI/CD) delayed → production deployment blocked

**Impact**: HIGH - Revenue loss, stakeholder confidence
**Probability**: MEDIUM (technical complexity)

**Mitigation**:
1. **Parallel development**: Start P0-006 before P0-005 complete
2. **External expertise**: Bring in security consultant for JWT review
3. **Phased rollout**: Deploy without JWT to staging first
4. **Rollback plan**: Maintain current manual deployment as fallback

---

### Medium Risk: Branch Coverage Gap Too Large

**Risk**: 0.4% → 70% gap too ambitious, team burnout

**Impact**: MEDIUM - Quality concerns, schedule delays
**Probability**: MEDIUM

**Mitigation**:
1. **Phased targets**: 25% → 50% → 70% over 3 quarters
2. **Automated generation**: Use coverage-guided fuzzing
3. **Prioritize**: Focus on critical paths first
4. **Tooling**: Invest in test generation tools

---

### Medium Risk: CLI Consolidation Resistance

**Risk**: Users resist migrating to CF_Core CLI

**Impact**: MEDIUM - Maintenance burden, fragmented ecosystem
**Probability**: LOW

**Mitigation**:
1. **Wrapper pattern**: Legacy CLIs continue working
2. **6-week grace period**: No forced migration
3. **Training**: Internal workshops and documentation
4. **Executive sponsorship**: Top-down support

---

### Low Risk: Documentation Lag

**Risk**: Documentation falls behind implementation

**Impact**: LOW - User confusion, onboarding friction
**Probability**: LOW (documentation-first culture)

**Mitigation**:
1. **Auto-generated docs**: OpenAPI, Typer auto-help
2. **Doc-first sprints**: Complete docs before features
3. **Review gates**: Documentation review mandatory
4. **Living docs**: Embed examples in code

---

## Dependencies & Prerequisites

### Technical Dependencies

| Dependency | Version | Status | Blocker For |
|------------|---------|--------|-------------|
| **Python** | ≥3.11 | ✅ Available | All Python work |
| **PostgreSQL** | 15+ | ✅ Operational | TaskMan-v2 production |
| **React** | 19 | ✅ Complete | Frontend features |
| **FastAPI** | 0.100+ | ✅ Complete | Backend features |
| **Kubernetes** | 1.28+ | 🔲 Planned | K8s deployment |
| **Prometheus** | Latest | 🔲 Planned | Observability |
| **Loki** | Latest | 🔲 Planned | Log aggregation |

### Organizational Prerequisites

- [ ] Executive approval for 2026-2027 roadmap
- [ ] Development team allocation (Q1 2026: 3-4 developers)
- [ ] Budget approval for cloud infrastructure (K8s, observability)
- [ ] User acceptance testing team identified
- [ ] Security audit scheduled (Q1 2026)

---

## Next Steps (Immediate Actions)

### This Week (2025-11-11 to 2025-11-15)

**Documentation**:
- [x] Complete 15-Future-Roadmap.md (this document)
- [ ] Complete 08-Optimization-Standards.md (performance, profiling)
- [ ] Update 00-ContextForge-Library-Index.md with roadmap

**Planning**:
- [ ] Review P0 blocker estimates with engineering team
- [ ] Schedule P0-005 (JWT) kickoff meeting
- [ ] Allocate resources for branch coverage remediation

**Communication**:
- [ ] Present roadmap to executive sponsors
- [ ] Announce 2026-2027 strategic direction to team
- [ ] Schedule quarterly roadmap reviews

### Next 2 Weeks (2025-11-18 to 2025-11-29)

**Complete Remaining Documentation**:
- [ ] 06-Idea-Capture-System.md
- [ ] 07-Workflow-Designer.md
- [ ] Validation & packaging (manifest, TOC, quick-start)

**Begin P0 Blockers**:
- [ ] P0-005 (JWT): Design review and implementation plan
- [ ] P0-006 (CI/CD): GitHub Actions workflow design
- [ ] P0-007 (Coverage): Coverage analysis and prioritization

---

## Appendix A: Strategic Alignment

### Core Philosophies Integration

| Philosophy | Roadmap Alignment |
|------------|-------------------|
| **1. Logging First** | Observability platform (Loki + Grafana) |
| **2. Python-First** | CF_Core CLI Python consolidation |
| **3. Database Authority** | PostgreSQL migration complete |
| **4. Quality Gates** | Branch coverage remediation |
| **5. Evidence Bundles** | Maintained across all new features |
| **6. Context Awareness** | Idea Capture System (COF integration) |
| **7. Sacred Geometry** | Workflow Designer visual language |
| **8. Result Monad** | Continued pattern enforcement |
| **9. Unified Vocabulary** | CLI consolidation, consistent UX |
| **10. Order & Flow** | UTMW workflow integration |
| **11. Iteration** | Agile roadmap with quarterly reviews |

---

## Appendix B: Related Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **CF_Core CLI Consolidation Roadmap** | Detailed CLI migration plan | [projects/P-CFWORK-DOCUMENTATION/CF-CORE-CLI-CONSOLIDATION-ROADMAP.md](../projects/P-CFWORK-DOCUMENTATION/CF-CORE-CLI-CONSOLIDATION-ROADMAP.md) |
| **01-Overview** | System overview and philosophies | [01-Overview.md](01-Overview.md) |
| **09-Development-Guidelines** | Engineering standards | [09-Development-Guidelines.md](09-Development-Guidelines.md) |
| **13-Testing-Validation** | Quality framework | [13-Testing-Validation.md](13-Testing-Validation.md) |
| **06-Idea-Capture-System** | Feature design (planned) | [06-Idea-Capture-System.md](06-Idea-Capture-System.md) |
| **07-Workflow-Designer** | Feature design (planned) | [07-Workflow-Designer.md](07-Workflow-Designer.md) |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-11 | ContextForge Team | Initial roadmap creation |
| 2.0 | 2025-11-11 | Claude (Sonnet 4.5) | Comprehensive strategic roadmap with 2027 vision |

---

**Document Status**: Complete ✅
**Authoritative**: Yes
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Strategy Team

---

*"The future is not predicted; it is built with intention, evidence, and iterative refinement."*
