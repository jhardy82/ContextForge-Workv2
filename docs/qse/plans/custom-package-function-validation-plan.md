# Custom Python Package Function Validation Plan

**Created**: 2025-11-28
**Updated**: 2025-11-29
**Status**: In Progress (Phase 1: 80% - Package 5 remaining)
**Complexity**: 🔴 COMPLEX (Multiple packages, cross-domain validation)
**COF Dimensions**: Technical, Validation, Computational, Holistic
**Checklist**: [Custom Package Validation Checklist](../checklists/custom-package-validation-checklist.md)

---

## 📋 Executive Summary

This plan systematically researches and validates all functions surfaced by our custom-installed Python packages. The validation ensures each function:
- Works correctly with current dependencies
- Has proper test coverage
- Integrates with the ContextForge ecosystem
- Maintains Sacred Geometry patterns (stability, completeness, modularity)

---

## 🎯 Custom Packages Identified

### 1. **unified-logger-proto** (v0.0.2)
**Location**: `projects/unified_logger/`
**Purpose**: Prototype unified structlog-based logger with redaction and evidence generation

### 2. **contextforge-orch-helper** (v0.1.0)
**Location**: `./` (root pyproject.toml)
**Purpose**: Unified ContextForge helper & orchestration environment

### 3. **dynamic-task-manager** (v0.1.0)
**Location**: `dynamic-task-manager/`
**Purpose**: Advanced task management system with workspace integration

### 4. **cf-analytics** (v0.1.0)
**Location**: `analytics/`
**Purpose**: ContextForge analytics enrichment layer for PowerShell governance artifacts

### 5. **cf-tracker** (v0.1.0)
**Location**: `cli/python/cf_tracker/`
**Purpose**: Python-first tracker system with DuckDB backend

---

## 📦 Package 1: unified-logger-proto

### Module: `unified_logger.core`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `configure_logging` | `(force: bool = False) -> None` | Configure structlog if not already configured | 🔍 Research | P0 |
| `get_logger` | `(name: str = "unified_logger")` | Factory returning configured structlog logger | 🔍 Research | P0 |
| `_serializer` | `(obj: Any, *, default=None) -> str` | Serialize event dict to JSON (orjson/fallback) | 🔍 Research | P1 |
| `_compiled_patterns` | `() -> list[re.Pattern[str]]` | Compile redaction patterns from env | 🔍 Research | P1 |
| `_redact_processor` | `(logger, method_name, event_dict)` | Structlog processor for credential redaction | 🔍 Research | P0 |
| `_add_correlation` | `(logger, method_name, event_dict)` | Add correlation_id to events | 🔍 Research | P0 |
| `_otel_processor_chain` | `()` | OpenTelemetry processor chain (optional) | 🔍 Research | P2 |

### Module: `unified_logger.models`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `Project` | Pydantic BaseModel | Project entity model | 🔍 Research | P0 |
| `Sprint` | Pydantic BaseModel | Sprint entity model | 🔍 Research | P0 |
| `Action` | Pydantic BaseModel | Action entity model | 🔍 Research | P0 |
| `export_model_schemas` | `(output_dir: str \| Path) -> list[Path]` | Export JSON schemas for models | 🔍 Research | P1 |
| `compile_validators` | `() -> dict[str, Any]` | Compile fastjsonschema validators | 🔍 Research | P2 |

### Module: `unified_logger.retry_helper`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `retrying` | `(func: Callable) -> Callable` | Tenacity retry decorator wrapper | 🔍 Research | P1 |
| `log_with_retry` | `(event: str, **fields) -> None` | Log with automatic retry support | 🔍 Research | P1 |

### Existing Tests
- `test_logger_basic.py`
- `test_redaction_and_level.py`
- `test_metrics_counters.py`
- `test_models_schema.py`
- `test_validators_optional.py`
- `test_exception_logging.py`

---

## 📦 Package 2: dynamic-task-manager

### Module: `backend.api.server`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `execute_cf_cli` | `(command: list[str], capture_json: bool = True) -> dict` | Execute cf_cli.py command and return response | 🔍 Research | P0 |
| `ConnectionManager.connect` | `async (websocket: WebSocket)` | Accept WebSocket connection | 🔍 Research | P0 |
| `ConnectionManager.disconnect` | `(websocket: WebSocket)` | Remove WebSocket connection | 🔍 Research | P0 |
| `ConnectionManager.broadcast` | `async (message: str)` | Broadcast to all connections | 🔍 Research | P0 |
| `ConnectionManager.send_personal_message` | `async (message, websocket)` | Send to specific client | 🔍 Research | P1 |

### Module: `backend.terminal_ui.unified_logger`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `ulog` | `(action, target, result, severity, **fields) -> None` | Emit structured JSONL events with Rich support | 🔍 Research | P0 |
| `setup_rich_logging` | `(log_level: str = "DEBUG") -> None` | Configure Rich logging handler | 🔍 Research | P1 |

### Pydantic Models

| Model | Fields | Purpose | Test Status | Priority |
|-------|--------|---------|-------------|----------|
| `TaskRequest` | title, description, project, sprint, priority, status | Create task request | 🔍 Research | P0 |
| `TaskUpdate` | id, title, description, status, actual_hours, notes | Update task request | 🔍 Research | P0 |
| `StatusResponse` | success, message, data | API response wrapper | 🔍 Research | P0 |

### API Endpoints (FastAPI Routes)

| Endpoint | Method | Purpose | Test Status | Priority |
|----------|--------|---------|-------------|----------|
| `/api/docs` | GET | Swagger documentation | 🔍 Research | P1 |
| `/api/health` | GET | Health check | 🔍 Research | P0 |
| `/ws/updates` | WebSocket | Real-time task updates | 🔍 Research | P0 |

---

## 📦 Package 3: cf-analytics

### Module: `cf_analytics.cli`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `app` | `Typer(...)` | Main analytics CLI application | 🔍 Research | P0 |
| `write_json` | `(path: Path, obj) -> None` | Write JSON to file path | 🔍 Research | P1 |
| `run` | `@app.command()` | Run analytics enrichment pipeline | 🔍 Research | P0 |

### Module: `cf_analytics.enrich`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `EnrichmentInputs` | `@dataclass` | Dataclass for enrichment input parameters | 🔍 Research | P0 |
| `utc_now_iso` | `() -> str` | Get current UTC timestamp in ISO format | 🔍 Research | P1 |
| `load_snapshots` | `(path: Path) -> list[SnapshotRecord]` | Load historical snapshots from JSONL file | 🔍 Research | P0 |
| `append_snapshot` | `(path: Path, record: SnapshotRecord) -> None` | Append snapshot record to JSONL file | 🔍 Research | P0 |
| `compute_deltas` | `(history: list[SnapshotRecord], current: SnapshotRecord) -> dict` | Calculate metric deltas between snapshots | 🔍 Research | P0 |
| `enrich` | `(inputs: EnrichmentInputs, workdir: Path) -> EnrichedSummary` | Main enrichment function | 🔍 Research | P0 |

### Module: `cf_analytics.loader`

| Class/Function | Signature | Purpose | Test Status | Priority |
|----------------|-----------|---------|-------------|----------|
| `ARTIFACT_FILENAMES` | `dict[str, str]` | Mapping of artifact types to filenames | 🔍 Research | P1 |
| `ArtifactLoader` | `class` | Artifact loading orchestrator | 🔍 Research | P0 |
| `ArtifactLoader.__init__` | `(root: Path) -> None` | Initialize loader with root path | 🔍 Research | P0 |
| `ArtifactLoader._load_json` | `(path: Path) -> dict \| None` | Safe JSON file loader | 🔍 Research | P1 |
| `ArtifactLoader.find_gap_report` | `() -> Path \| None` | Search for gap report in output directories | 🔍 Research | P1 |
| `ArtifactLoader.load` | `() -> dict[str, Any]` | Load all known artifacts | 🔍 Research | P0 |
| `ArtifactLoader.to_models` | `(raw: dict) -> dict[str, Any]` | Convert raw dicts to Pydantic models | 🔍 Research | P0 |

### Module: `cf_analytics.models`

| Model | Fields | Purpose | Test Status | Priority |
|-------|--------|---------|-------------|----------|
| `ArtifactBase` | schema_id, schema_version, generated_utc | Base model for artifacts | 🔍 Research | P1 |
| `BacklogCounts` | total, status_counts, phase_counts, etc. | Backlog statistics model | 🔍 Research | P0 |
| `TriageCategory` | name, count | PSSA triage category | 🔍 Research | P1 |
| `TriageSummary` | total_findings, categories, run_id | PSSA triage summary | 🔍 Research | P0 |
| `GapPresence` | name, present, path | Gap presence indicator | 🔍 Research | P1 |
| `GapReport` | expected_count, present_count, missing_count, etc. | Governance gap report | 🔍 Research | P0 |
| `ParitySummary` | exit_code_match | Parity check result | 🔍 Research | P1 |
| `ParityReport` | parity_summary | Full parity report | 🔍 Research | P1 |
| `MetricsPhase1` | event_count, processing_ms, memory_bytes_peak | Phase 1 metrics | 🔍 Research | P1 |
| `RichSummaryModel` | backlog, pssa_triage, parity, gap_report, etc. | Complete rich summary | 🔍 Research | P0 |
| `SnapshotRecord` | timestamp, completion_pct, pssa_findings, etc. | Point-in-time snapshot | 🔍 Research | P0 |
| `EnrichedSummary` | enriched_metrics, source_artifacts, validation | Final enriched output | 🔍 Research | P0 |

---

## 📦 Package 4: cf-tracker

**Location**: `cli/python/cf_tracker/`
**Entry Point**: `tracker` CLI command
**Purpose**: Python-first tracker with DuckDB and Markdown backends

### Module: `cf_tracker.cli` (341 lines)

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| `app` | `Typer(name="tracker")` | Main tracker CLI application | 🔍 Research | P0 |
| `project_app` | `Typer(name="project")` | Project management subcommands | 🔍 Research | P0 |
| `sprint_app` | `Typer(name="sprint")` | Sprint management subcommands | 🔍 Research | P0 |
| `task_app` | `Typer(name="task")` | Task management subcommands | 🔍 Research | P0 |
| `tools_app` | `Typer(name="tools")` | Tooling utilities subcommands | 🔍 Research | P1 |
| `_get_service` | `() -> TrackerService` | Factory for TrackerService instance | 🔍 Research | P0 |
| `create` | `@app.command()` | Create new tracker item | 🔍 Research | P0 |
| `get` | `@app.command()` | Get tracker item by ID | 🔍 Research | P0 |
| `update` | `@app.command()` | Update tracker status | 🔍 Research | P0 |
| `heartbeat` | `@app.command()` | Touch tracker updated_utc timestamp | 🔍 Research | P0 |
| `list` | `@app.command()` | List trackers with optional kind filter | 🔍 Research | P0 |
| `tools_eval` | `@tools_app.command("eval")` | Evaluate expression | 🔍 Research | P1 |
| `tools_install` | `@tools_app.command("install")` | Install package(s) | 🔍 Research | P1 |
| `tools_migrate` | `@tools_app.command("migrate")` | Run migration | 🔍 Research | P1 |

### Module: `cf_tracker.tracker_service` (203 lines)

| Class/Function | Signature | Purpose | Test Status | Priority |
|----------------|-----------|---------|-------------|----------|
| `TrackerService` | `class` | Main service for tracker operations | 🔍 Research | P0 |
| `TrackerService.__init__` | `(backend: str = "markdown")` | Initialize with markdown/duckdb backend | 🔍 Research | P0 |
| `TrackerService.create` | `(kind, title, owner, status) -> Tracker` | Create new tracker record | 🔍 Research | P0 |
| `TrackerService.get` | `(tracker_id: str) -> Tracker \| None` | Get tracker by ID | 🔍 Research | P0 |
| `TrackerService.update_status` | `(tracker_id: str, status: str) -> Tracker` | Update tracker status | 🔍 Research | P0 |
| `TrackerService.heartbeat` | `(tracker_id: str) -> Tracker` | Touch updated_utc timestamp | 🔍 Research | P0 |
| `TrackerService.list` | `(kind: str \| None = None) -> list[Tracker]` | List trackers, optionally filtered by kind | 🔍 Research | P0 |
| `_markdown_create` | Internal method | Markdown backend create | 🔍 Research | P1 |
| `_markdown_get` | Internal method | Markdown backend get | 🔍 Research | P1 |
| `_duckdb_create` | Internal method | DuckDB backend create | 🔍 Research | P1 |
| `_duckdb_get` | Internal method | DuckDB backend get | 🔍 Research | P1 |

### Module: `cf_tracker.models`

| Model | Fields | Purpose | Test Status | Priority |
|-------|--------|---------|-------------|----------|
| `Tracker` | id, kind, title, owner, status, created_utc, updated_utc | Core tracker entity model | 🔍 Research | P0 |
| `Tracker.touch()` | `() -> None` | Update timestamp to current UTC | 🔍 Research | P0 |

### Module: `cf_tracker.duckdb_builder`

| Function | Signature | Purpose | Test Status | Priority |
|----------|-----------|---------|-------------|----------|
| *Query builders* | *Research needed* | DuckDB query construction | 🔍 Research | P1 |

---

## 🔬 Validation Phases

### Phase 1: Function Discovery (Researcher)
**Agent**: `researcher`
**Duration**: 2-3 hours

1. **unified-logger-proto**: Read all module files, document all functions
2. **dynamic-task-manager**: Examine backend API and terminal_ui modules
3. **cf-analytics**: Map cli, enrich, loader, models modules
4. **cf-tracker**: Document cli, db, models, services, duckdb_builder

**Deliverable**: Completed function inventory with signatures

---

### Phase 2: Existing Test Analysis (Researcher → Tester)
**Agent**: `researcher` + `tester`
**Duration**: 1-2 hours

1. Run existing test suites for each package
2. Measure current coverage
3. Identify untested functions
4. Document test gaps

**Deliverable**: Test coverage report and gap analysis

---

### Phase 3: Integration Validation (Coder)
**Agent**: `coder`
**Duration**: 3-4 hours

1. Verify cross-package imports work correctly
2. Test function interactions between packages
3. Validate environment variable handling
4. Check optional dependency fallbacks (orjson, tenacity, fastjsonschema, prometheus_client)

**Deliverable**: Integration test suite

---

### Phase 4: API Contract Validation (Tester)
**Agent**: `tester`
**Duration**: 2-3 hours

1. Validate FastAPI endpoints (dynamic-task-manager)
2. Test WebSocket connections
3. Verify Pydantic model serialization/deserialization
4. Check CLI entry points (cf-analyze, tracker, ulog-demo)

**Deliverable**: API contract test results

---

### Phase 5: Evidence Bundle Generation (Documenter)
**Agent**: `documenter`
**Duration**: 1-2 hours

1. Generate test execution evidence
2. Create validation reports
3. Update package documentation
4. Link evidence to UCL compliance

**Deliverable**: Evidence bundle with SHA-256 hashes

---

## 📊 Validation Criteria

### Per-Function Validation Checklist

- [ ] Function signature documented
- [ ] Purpose clearly described
- [ ] Unit test exists
- [ ] Edge cases covered
- [ ] Error handling verified
- [ ] Type hints validated (mypy)
- [ ] Documentation complete

### Per-Package Validation Checklist

- [ ] All exports verified
- [ ] `__all__` matches actual exports
- [ ] Version string accurate
- [ ] Dependencies resolved correctly
- [ ] Entry points functional
- [ ] Integration tests passing

---

## 🎯 Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Function documentation coverage | 100% | ~85% (5 packages inventoried) |
| Unit test coverage | ≥70% | TBD (Phase 2) |
| Integration test coverage | ≥40% | TBD (Phase 3) |
| API contract validation | 100% | TBD (Phase 4) |
| Mypy strict compliance | 100% | TBD |
| Entry point functionality | 100% | TBD |

---

## 📅 Timeline

| Phase | Agent | Duration | Start | Status |
|-------|-------|----------|-------|--------|
| 1. Function Discovery | researcher | 2-3h | 2025-11-28 | ✅ Complete |
| 2. Test Analysis | researcher + tester | 1-2h | TBD | ⏳ Pending |
| 3. Integration Validation | coder | 3-4h | TBD | ⏳ Pending |
| 4. API Contract Validation | tester | 2-3h | TBD | ⏳ Pending |
| 5. Evidence Generation | documenter | 1-2h | TBD | ⏳ Pending |

**Total Estimated Effort**: 9-14 hours

---

## 🔗 Related Documents

### Project Configuration
- [pyproject.toml](../pyproject.toml) - Root package configuration
- [unified_logger/README.md](../projects/unified_logger/README.md) - Logger documentation
- [dynamic-task-manager/README.md](../dynamic-task-manager/README.md) - DTM documentation
- [analytics/README.md](../analytics/README.md) - Analytics documentation
- [cf_tracker/](../cli/python/cf_tracker/) - Tracker package

### Research Reports
- [AI Agent Terminal Requirements](../research/INTEGRATOR-CC-REPORT-AI-Agent-Terminal-Requirements-20251125.md) - Terminal integration requirements analysis
- [MCP Shell Integration Patterns](../research/INTEGRATOR-MCP-REPORT-Shell-Integration-Patterns-20251125.md) - MCP server shell integration patterns
- [Environment Variable Precedence](../research/SENTINEL-ENV-REPORT-Environment-Variable-Precedence-20251125.md) - Environment variable precedence analysis
- [Shell Config Precedence](../research/SHELL-CONFIG-PRECEDENCE-AI-Agent-Observability-20251126.md) - Shell configuration precedence for AI observability
- [Shell Prompt Configuration](../research/SHELL-PROMPT-CONFIG-AI-Agent-Visibility-20251125.md) - Shell prompt configuration for AI visibility

### Project Tracking
- [Custom Package Validation Checklist](../checklists/custom-package-validation-checklist.md) - Detailed task checklist

---

## 📝 Notes

### Sacred Geometry Alignment
- **Triangle (Stability)**: Each function validated for correct behavior
- **Circle (Completeness)**: Full coverage of all exported functions
- **Spiral (Iteration)**: Incremental validation per package
- **Fractal (Modularity)**: Function-level granularity scales to package-level

### UCL Compliance
- All validation evidence must be anchored to this plan
- No orphaned test results
- Evidence bundles with SHA-256 hashes required

---

*Generated by ContextForge Orchestrator - "Context Before Action"*
