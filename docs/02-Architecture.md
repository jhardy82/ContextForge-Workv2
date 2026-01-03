# 02 – Architecture

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [03-Context-Ontology-Framework](03-Context-Ontology-Framework.md) | [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md) | [05-Database-Design-Implementation](05-Database-Design-Implementation.md)

---

## System Architecture

### High-Level Context Diagram

```
User (Engineer) → cf_core.cli.main → Storage → Analytics → Logs
                        ↓
          (PostgreSQL Authority + DuckDB + context.yaml)
                        ↓
                  Evidence Bundles (JSONL + SHA-256)
```

> **Note**: Legacy CLIs (`dbcli`, `cf_cli`, `tasks_cli`) are deprecated. Use `python -m cf_core.cli.main` for all operations.

### Component Diagram

```mermaid
flowchart TB
    UI[CLI Tools]
    CLI[dbcli + cf_cli + tasks_cli]
    TM[TaskMan-v2 React UI]
    MCP[MCP Servers]

    PG[(PostgreSQL Authority)]
    DUCK[(DuckDB Velocity)]
    SQLITE[(SQLite Legacy)]
    CTX[context.yaml + JSON]

    CF[cf_core Domain]
    SPEC[ContextForge.Spectre]
    QSE[QSE Framework]

    LOG[Unified Logger JSONL]

    UI --> CLI
    TM --> CLI
    MCP --> CLI

    CLI --> PG
    CLI --> DUCK
    CLI --> SQLITE
```

---

## Direct Database Access Pattern

ContextForge uses **direct database access** instead of MCP middleware for maximum performance and simplicity.

### Access Methods

**Three production-ready approaches**:

1. **Python psycopg2** (168ms P95 latency) - **Recommended for automation**
   - Fastest method
   - Environment variable support
   - Helper: `scripts/db_auth.py`

2. **Docker exec** (223ms P95 latency) - **Recommended for debugging**
   - Excellent for ad-hoc queries
   - No additional dependencies
   - Direct psql CLI access

3. **PowerShell wrapper** - Uses `Get-DatabaseCredentials.ps1`
   - Cross-platform compatibility
   - Environment variable support
   - Integrates with Windows automation

### Performance Analysis

| Method | P95 Latency | Use Case |
|--------|-------------|----------|
| Python psycopg2 | 168ms | Automation, scripts, scheduled tasks |
| Docker exec | 223ms | Debugging, manual queries, exploration |
| MCP (rejected) | 193-243ms | ❌ Higher overhead, complexity without benefit |

**Decision Rationale**: Direct access is 30% faster than MCP theoretical overhead with zero configuration complexity. MCP approach deprecated in favor of direct database access.

### Database Infrastructure

**Production Databases** (Docker containers):
- **taskman_v2** - localhost:5434 (PostgreSQL 16) - Primary TaskMan database
- **contextforge** - localhost:5433 (PostGIS 15) - ContextForge project database
- **context_forge** - localhost:5432 (PostgreSQL 15) - Sacred Geometry database

**Credentials**: `contextforge/contextforge` (dev default, override via environment variables for production)

### Documentation

**Quick References**:
- [DATABASE-QUICK-REFERENCE.md](DATABASE-QUICK-REFERENCE.md) - 30-second access guide
- [AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md) - Comprehensive 500+ line guide
- [DATABASE-EXAMPLE-QUERIES.md](DATABASE-EXAMPLE-QUERIES.md) - 30+ tested SQL examples
- [DATABASE-TROUBLESHOOTING-FLOWCHART.md](DATABASE-TROUBLESHOOTING-FLOWCHART.md) - Decision tree diagrams

**Security & Production**:
- [SECURITY-REVIEW-DATABASE-ACCESS.md](../SECURITY-REVIEW-DATABASE-ACCESS.md) - 9 security findings
- [PRODUCTION-DATABASE-DEPLOYMENT.md](PRODUCTION-DATABASE-DEPLOYMENT.md) - Production deployment guide
- [DATABASE-PERFORMANCE-ANALYSIS.md](DATABASE-PERFORMANCE-ANALYSIS.md) - Benchmark results

**MCP Deprecation**: See [archive/mcp-deprecated/README.md](../archive/mcp-deprecated/README.md) for rationale.

---

```mermaid
flowchart TB
    CLI --> CTX
    CLI --> CF
    CLI --> SPEC
    CLI --> QSE
    CLI --> LOG

    CF --> PG
    CF --> SQLITE

    subgraph Storage[Storage Layer]
        PG
        DUCK
        SQLITE
        CTX
    end

    subgraph Domain[Domain Layer]
        CF
        SPEC
        QSE
    end

    subgraph Evidence[Evidence Layer]
        LOG
    end
```

---

## Component Inventory

### CLI Tools (Command Layer)

| Component | Purpose | Technology | Status |
|-----------|---------|------------|--------|
| **dbcli** | Authoritative tracker operations | Python Typer | ✅ Production |
| **cf_cli** | ContextForge workflows | Python Typer | ✅ Production |
| **tasks_cli** | Task management | Python Typer | ✅ Production |

**Command Groups**:
- `task` - Task CRUD (create, start, complete, update)
- `sprint` - Sprint management and status
- `project` - Project lifecycle
- `status` - System health checks
- `velocity` - Analytics recording
- `context` - COF context operations

### Storage Layer (Data Authority)

| Component | Purpose | Technology | Authority |
|-----------|---------|------------|-----------|
| **PostgreSQL** | TaskMan-v2 task database | PostgreSQL 15+ | **PRIMARY** |
| **DuckDB** | Velocity analytics | DuckDB | Analytics |
| **SQLite** | Legacy tracker database | SQLite 3 | Supplementary |
| **context.yaml** | Context objects | YAML + JSON | Config |

**Database Authority Principle** (Codex Addendum A):
- PostgreSQL (`172.25.14.122:5432/taskman_v2`) is **primary task management authority** for TaskMan-v2
- SQLite (`db/trackers.sqlite`) maintains legacy tracker data and supplementary context
- Runtime CSV mutation **blocked** (`direct_csv_access_blocked`)
- Legacy CSV constants only for migration

### Domain Layer (Business Logic)

| Component | Purpose | Pattern | Status |
|-----------|---------|---------|--------|
| **cf_core** | Domain entities | DDD, Repository, Result Monad | ✅ Production |
| **ContextForge.Spectre** | Terminal UI | Sacred Geometry glyphs | ✅ Production |
| **QSE Framework** | Quality gates | UTMW workflow | ✅ Production |

**cf_core Architecture**:
- `domain/` - Entities with business logic (Task, Sprint, Project)
- `repositories/` - Persistence abstraction (Repository pattern)
- `models/` - Pydantic data structures
- `shared/` - Result monad, exceptions

### Application Layer

| Component | Purpose | Technology | Status |
|-----------|---------|------------|--------|
| **TaskMan-v2 Frontend** | React 19 UI | TypeScript, Vite | 75% Ready |
| **TaskMan-v2 Backend** | FastAPI REST API | Python 3.11+ | 75% Ready |
| **MCP Python Server** | AI integration | MCP Protocol | ✅ 36/36 tests |
| **MCP TypeScript Server** | AI integration (alt) | TypeScript | ✅ Active |

### Evidence Layer (Observability)

| Component | Purpose | Format | Status |
|-----------|---------|--------|--------|
| **Unified Logger** | Structured logging | JSONL | ✅ Production |
| **Evidence Bundles** | Cryptographic proof | SHA-256 hash | ✅ Production |
| **Event Taxonomy** | Standard events | Codex Addendum B | ✅ Defined |

**Logging Taxonomy** (Key Events):
- `task_create`, `task_start`, `task_update`, `task_complete`
- `sprint_status`, `project_update`
- `artifact_emit`, `decision`, `authority_check`
- `direct_csv_access_blocked`

---

## Data Flows

### Task Lifecycle Flow

```
┌────────────────────────────────────────────────────┐
│ 1. CLI: dbcli.py task create "JWT Auth"           │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 2. Domain: cf_core Task entity validation         │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 3. Repository: PostgreSQL INSERT (authority)      │
│    - Emit: task_create event (JSONL)              │
│    - Hash: SHA-256 evidence bundle                │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 4. Context: Update context.yaml + JSON shadow     │
│    - Merge with COF 13D metadata                  │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 5. Analytics: DuckDB velocity record (optional)   │
│    - Sprint velocity calculation                  │
└────────────────────────────────────────────────────┘
```

### Evidence Bundle Flow

```
┌─────────────────┐
│ State Mutation  │ → Emit Event
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Unified Logger  │ → JSONL append
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SHA-256 Hash    │ → Evidence bundle
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Update  │ → evidence_bundle_hash field
└─────────────────┘
```

### Authority Check Flow

```
┌──────────────────┐
│ Write Operation  │
└────────┬─────────┘
         │
         ▼
      Check Sentinel
         │
    ┌────┴────┐
    │ Exists? │
    └────┬────┘
         │
    ┌────┴────┐
    │   YES   │──→ Use PostgreSQL (authority)
    └─────────┘
         │
    ┌────┴────┐
    │   NO    │──→ Block + Emit: direct_csv_access_blocked
    └─────────┘
```

---

## Sacred Geometry Integration

From [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md):

### Architectural Patterns

**Triangle (Stability)**:
- Three-layer architecture: CLI → Domain → Storage
- Triple-check protocol: Build → Log → Validate

**Circle (Completeness)**:
- COF 13-dimensional analysis for all contexts
- Evidence bundles close the loop

**Spiral (Iteration)**:
- DuckDB velocity tracking (0.23 hrs/point baseline)
- Retrospectives every 2 weeks

**Golden Ratio (Balance)**:
- 35% focused test coverage (not 100%)
- Right-sized solutions (Codex: "Best tool for the context")

**Fractal (Modularity)**:
- Repository pattern at all layers
- Reusable components (cf_core, Spectre)

---

## Error Handling & Logging

### Error Handling Strategy

**Broad CLI Exception Capture**:
```python
try:
    result = service.create_task(task)
    if result.is_success:
        logger.info("task_create", task_id=result.value.task_id)
    else:
        logger.error("task_create_failed", error=result.error)
        sys.exit(1)
except Exception as e:
    logger.exception("unexpected_error", error=str(e))
    sys.exit(1)
```

**Exit Codes**:
- `0` - Success
- `1` - Error (operational failure)
- `2` - Usage error (invalid arguments)
- `4` - Optional dependency missing

### Logging Baseline

**Event Flow** (from [01-Overview.md](01-Overview.md)):
```
session_start → task_start → decision → artifact_emit → task_end → session_summary
```

**Quality Targets** (Codex Addendum C):
- ≥90% logging coverage (mutating code paths)
- UTC timestamps, no PII
- JSON or enriched logger format

---

## Extensibility

### Adding New CLI Commands

**1. Create Typer Subcommand Module**:
```python
# dbcli_extensions/velocity_forecast.py
import typer

app = typer.Typer()

@app.command("forecast")
def forecast_velocity(sprint_id: str):
    """Forecast sprint completion"""
    # Implementation
    logger.info("velocity_forecast", sprint_id=sprint_id)
```

**2. Register via Main App**:
```python
# dbcli.py
from dbcli_extensions import velocity_forecast

app.add_typer(velocity_forecast.app, name="forecast")
```

**3. Keep Event Emission Consistent**:
- Use standard event taxonomy (Codex Appendix B)
- Emit domain events for state mutations
- Emit decision events for guard clauses

---

## Security Posture

### Secret Management

**Principle**: "Secret refs only; environment variables or SecretManagement; no plaintext credentials persisted."

**Implementation**:
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")  # ✅ Environment variable
API_KEY = load_secret("api_key")           # ✅ Secret manager

# ❌ NEVER:
# DATABASE_URL = "postgresql://user:pass@host/db"
```

**Tools**:
- PowerShell: `SecretManagement` module
- Python: `python-dotenv` + `.env` (gitignored)
- Production: Azure Key Vault, AWS Secrets Manager

---

## Operational Footprint

### Local-First Architecture

**Principle**: Offline-tolerant (core flows without network)

**Health Checks**:
```bash
# Database authority status
python dbcli.py status migration

# DuckDB analytics status
python dbcli.py status duckdb

# Context sync status
python dbcli.py context status
```

### Future: Containerization

**Planned** (not yet implemented):
```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "dbcli.py", "server"]
```

---

## Cross References

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview with philosophies
- [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) - COF 13D + UCL
- [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 details
- [05-Database-Design-Implementation.md](05-Database-Design-Implementation.md) - Storage layer

### Authoritative Reference

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE**

### Implementation Details

- [cf_core/README.md](../cf_core/README.md) - Domain-Driven Design patterns
- [modules/ContextForge.Spectre/](../modules/ContextForge.Spectre/) - Terminal UI module

---

**Document Status**: Complete ✅
**Authoritative**: Yes (integrated with Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Architecture Team

---

*"Architecture balances order and flow."*
