# Custom Package Validation Checklist

**Plan**: [Custom Package Function Validation Plan](../plans/custom-package-function-validation-plan.md)
**Created**: 2025-11-28
**Updated**: 2025-11-29
**Status**: Active (Phase 1: 80%)

---

## 📊 Progress Overview

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Function Discovery | 🔄 In Progress | 80% |
| Phase 2: Test Analysis | ⏳ Pending | 0% |
| Phase 3: Integration Validation | ⏳ Pending | 0% |
| Phase 4: API Contract Validation | ⏳ Pending | 0% |
| Phase 5: Evidence Generation | ⏳ Pending | 0% |

---

## 📦 Phase 1: Function Discovery

### Package 1: unified-logger-proto ✅

- [x] Identify package location (`projects/unified_logger/`)
- [x] Document `unified_logger.core` functions
  - [x] `configure_logging` - Configure structlog
  - [x] `get_logger` - Logger factory
  - [x] `_serializer` - JSON serialization
  - [x] `_compiled_patterns` - Redaction patterns
  - [x] `_redact_processor` - Credential redaction
  - [x] `_add_correlation` - Correlation ID injection
  - [x] `_otel_processor_chain` - OpenTelemetry integration
- [x] Document `unified_logger.models` classes
  - [x] `Project` - Project entity
  - [x] `Sprint` - Sprint entity
  - [x] `Action` - Action entity
  - [x] `export_model_schemas` - Schema export
  - [x] `compile_validators` - Validator compilation
- [x] Document `unified_logger.retry_helper` functions
- [x] Catalog existing tests (6 test files)

### Package 2: dynamic-task-manager ✅

- [x] Identify package location (`dynamic-task-manager/`)
- [x] Document `backend.api.server` functions
  - [x] `execute_cf_cli` - CLI command execution
  - [x] `ConnectionManager` class and methods
- [x] Document `backend.terminal_ui.unified_logger` functions
  - [x] `ulog` - Structured event emitter
  - [x] `setup_rich_logging` - Rich logging setup
- [x] Document Pydantic models (`TaskRequest`, `TaskUpdate`, `StatusResponse`)
- [x] Document API endpoints

### Package 3: cf-analytics ✅

- [x] Identify package location (`analytics/`)
- [x] Document `cf_analytics.cli` functions
  - [x] `app` - Typer CLI
  - [x] `write_json` - JSON writer
  - [x] `run` - Pipeline runner
- [x] Document `cf_analytics.enrich` functions
  - [x] `EnrichmentInputs` dataclass
  - [x] `utc_now_iso` - Timestamp utility
  - [x] `load_snapshots` - Snapshot loader
  - [x] `append_snapshot` - Snapshot writer
  - [x] `compute_deltas` - Delta calculator
  - [x] `enrich` - Main enrichment function
- [x] Document `cf_analytics.loader` classes
  - [x] `ArtifactLoader` class
  - [x] `ARTIFACT_FILENAMES` constant
- [x] Document `cf_analytics.models` (15+ models)

### Package 4: cf-tracker ✅

- [x] Identify package location (`cli/python/cf_tracker/`)
- [x] Document `cf_tracker.cli` commands (14 commands)
  - [x] `app` - Main Typer app
  - [x] `project_app` - Project subcommands
  - [x] `sprint_app` - Sprint subcommands
  - [x] `task_app` - Task subcommands
  - [x] `tools_app` - Tools subcommands
  - [x] `_get_service` - Service factory
  - [x] CRUD commands (`create`, `get`, `update`, `heartbeat`, `list`)
  - [x] Tools commands (`eval`, `install`, `migrate`)
- [x] Document `cf_tracker.tracker_service` (12 methods)
  - [x] `TrackerService` class
  - [x] Service methods (`create`, `get`, `update_status`, `heartbeat`, `list`)
  - [x] Backend methods (markdown and duckdb)
- [x] Document `cf_tracker.models`
  - [x] `Tracker` model

### Package 5: contextforge-orch-helper ⏳

- [x] Identify package location (root `pyproject.toml`)
- [ ] Document `src/cli_plugins/` modules
- [ ] Document `src/core/` modules
- [ ] Document `src/db/` modules
- [ ] Document `src/models/` modules
- [ ] Document `src/utilities/` modules
- [ ] Document `src/unified_logger.py`

---

## 🧪 Phase 2: Test Analysis

### unified-logger-proto

- [ ] Run test suite: `pytest projects/unified_logger/tests/ -v`
- [ ] Measure coverage: `pytest --cov=unified_logger`
- [ ] Document test gaps
- [ ] Identify untested functions

### dynamic-task-manager

- [ ] Run test suite (if exists)
- [ ] Measure coverage
- [ ] Document test gaps

### cf-analytics

- [ ] Run test suite (if exists)
- [ ] Measure coverage
- [ ] Document test gaps

### cf-tracker

- [ ] Run test suite (if exists)
- [ ] Measure coverage
- [ ] Document test gaps

### contextforge-orch-helper

- [ ] Run test suite: `pytest tests/ -v`
- [ ] Measure coverage
- [ ] Document test gaps

---

## 🔗 Phase 3: Integration Validation

### Cross-Package Imports

- [ ] Verify `unified_logger` importable from all packages
- [ ] Test `cf_core` integration with custom packages
- [ ] Validate shared model compatibility

### Optional Dependencies

- [ ] Test with `orjson` available
- [ ] Test with `orjson` unavailable (fallback)
- [ ] Test with `tenacity` available
- [ ] Test with `tenacity` unavailable
- [ ] Test with `fastjsonschema` available
- [ ] Test with `prometheus_client` available

### Environment Variable Handling

- [ ] Verify `LOG_LEVEL` propagation
- [ ] Verify `LOG_REDACTION_PATTERNS` parsing
- [ ] Verify `CORRELATION_ID` injection
- [ ] Verify `OTEL_*` configuration

---

## 📡 Phase 4: API Contract Validation

### dynamic-task-manager API

- [ ] Validate `/api/health` endpoint
- [ ] Validate `/api/docs` endpoint
- [ ] Test WebSocket `/ws/updates` connection
- [ ] Verify `TaskRequest` schema
- [ ] Verify `TaskUpdate` schema
- [ ] Verify `StatusResponse` schema

### CLI Entry Points

- [ ] Test `ulog-demo` command
- [ ] Test `cf-analyze` command
- [ ] Test `tracker` command
- [ ] Verify help text accuracy

---

## 📝 Phase 5: Evidence Generation

### Test Execution Evidence

- [ ] Generate pytest execution report
- [ ] Calculate overall coverage percentage
- [ ] Create coverage report HTML

### Validation Reports

- [ ] Create function validation summary
- [ ] Create integration test report
- [ ] Create API contract report

### Documentation Updates

- [ ] Update package READMEs with validation results
- [ ] Update this checklist with final status
- [ ] Update plan with completion status

### UCL Compliance

- [ ] Generate evidence bundle
- [ ] Compute SHA-256 hashes
- [ ] Link evidence to validation plan

---

## 📚 Research References

| Report | Date | Relevance |
|--------|------|-----------|
| [AI Agent Terminal Requirements](../research/INTEGRATOR-CC-REPORT-AI-Agent-Terminal-Requirements-20251125.md) | 2025-11-26 | Terminal integration patterns |
| [MCP Shell Integration Patterns](../research/INTEGRATOR-MCP-REPORT-Shell-Integration-Patterns-20251125.md) | 2025-11-26 | MCP server integration |
| [Environment Variable Precedence](../research/SENTINEL-ENV-REPORT-Environment-Variable-Precedence-20251125.md) | 2025-11-26 | Env var handling validation |
| [Shell Config Precedence](../research/SHELL-CONFIG-PRECEDENCE-AI-Agent-Observability-20251126.md) | 2025-11-26 | Configuration precedence |
| [Shell Prompt Configuration](../research/SHELL-PROMPT-CONFIG-AI-Agent-Visibility-20251125.md) | 2025-11-26 | Prompt configuration |

---

## 📋 Additional Work Identified

### High Priority (P0)

- [ ] Package 5 (contextforge-orch-helper) full function discovery
- [ ] Create missing test suites for packages without tests
- [ ] Resolve pytest collection errors in `projects/unified_logger/tests/`

### Medium Priority (P1)

- [ ] Document `cf_tracker.duckdb_builder` module (query builders)
- [ ] Create integration tests for cross-package imports
- [ ] Validate type hints with mypy strict mode

### Low Priority (P2)

- [ ] Document private/internal functions (`_` prefixed)
- [ ] Create performance benchmarks
- [ ] Add OpenTelemetry integration tests

---

## ✅ Completion Criteria

| Criterion | Status |
|-----------|--------|
| All 5 packages function-documented | 🔄 80% (Package 5 incomplete) |
| Test coverage ≥70% per package | ⏳ Pending |
| Integration tests passing | ⏳ Pending |
| API contracts validated | ⏳ Pending |
| Evidence bundle generated | ⏳ Pending |
| Documentation updated | ⏳ Pending |

---

*Generated by ContextForge Orchestrator*
*Sacred Geometry: Triangle (stability through systematic validation)*
