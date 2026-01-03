# DTM Constitutional Dashboard Research & Design Matrix (CF-Enhanced)

Version: 0.1.0 (Research Baseline)
Date: 2025-09-22
Task(s): T-20250922-012 (In Progress), dashboard-research-matrix (this document)
Prepared By: CF-Enhanced Development Agent

## 1. Objective & Scope
Transform the current prototype `dtm_constitutional_dashboard.py` (simulation-only) into a production-grade, constitutional-compliant, extensible dashboard supporting:
- Real data ingestion (performance, tasks, quality gates, compliance evidence)
- Historical time‑series persistence & trend analysis
- Alert rule evaluation & emission via unified logger (`ulog`)
- Provenance + schema versioned JSON export (API/CLI consumption)
- Dependency-injected provider/adapters for testability & future evolution
- CLI subcommands for `cf_cli.py` (export, serve, snapshot, alert-test)
- >=95% confidence threshold prior to promotion (defined in §11)

Patterns Applied:
- Triangle (Stability: provider interfaces, schema versioning, quality gates)
- Circle (Closure: end-to-end cycle metrics→persist→render→alert→AAR)
- Spiral (Iterative enrichment: simulation → partial real → full fidelity)
- Golden Ratio (Optimization: balance freshness vs resource cost in collection frequencies)
- Fractal (Self-similarity: adapter interface conventions align across domains)

## 2. COF (13 Dimensions) & UCL (5 Laws) – Constitutional Analysis
| Dimension | Decision / Observation | CF Enhancement | Rationale | Evidence | Gate |
|-----------|------------------------|----------------|-----------|----------|------|
| Identity | Dashboard = constitutional observability surface (component id: `dtm_dashboard`) | Namespaced artifact & schema id | Avoid ambiguity across tools | File name, planned schema id `cf.dtm.dashboard.v1` | Constitutional |
| Intent | Provide actionable, validated constitutional + performance visibility | Explicit scope boundaries | Prevent scope creep & maintain reliability | This doc + task ADR | Constitutional |
| Stakeholders | DevOps, Architects, Compliance, Performance Eng, DTM Orchestrator | Role-based view filtering (future) | Distinct needs; avoid one-size stagnation | Task list & governance instructions | Cognitive |
| Context | Operates atop DTM performance integration & task system | Provider abstraction isolates external churn | Limits ripple effect of upstream change | Existing integration module | Integration |
| Scope | Phase 1: adapters + persistence + CLI; Phase 2: alerts; Phase 3: drill-down UI | Phased Spiral evolution | Controlled complexity introduction | Roadmap §10 | Operational |
| Time | Collection intervals: perf 30s, tasks 60s, quality gates on change, compliance 120s (initial) | Adjustable dynamic scheduling | Optimize signal vs cost | Update interval param; research defaults | Performance |
| Space | Filesystem (snapshot JSON/HTML), DuckDB (history), optional SQLite (future) | Layered storage plan | Decouple hot vs historical queries | Proposed schemas §5 | Integration |
| Modality | JSON (API), HTML (human), log events (JSONL) | Multi-format only when justified | Reduce redundancy | Logging-first instructions | Operational |
| State | Dashboard states: initializing, collecting, steady, degraded | Emit state transitions via `ulog` | Fast issue triage | Planned event map §7 | Operational |
| Scale | Initially single-node; design for multi-source merge (future) | Fractal naming & version fields | Future horizontal scaling | Schema design + adapter contracts | Integration |
| Risk | Data staleness, adapter failure, alert noise, schema drift | Circuit breaker + freshness TTL + version tags | Preserve trustworthiness | Mitigation plan §9 | Risk |
| Evidence | Hash snapshot JSON, store metrics lineage, log adapter timings | Provenance fields & emission events | Auditability & UCL-1/3 compliance | Evidence field spec §6 | Constitutional |
| Ethics | No PII; only aggregated metrics & task ids; security gating deferred to later task | Redact forbidden fields, explicit allowlist | Prevent leakage | Security placeholder §9 | Constitutional |

UCL Validation:
- UCL-1 Verifiability: All scores derived from explicit adapter outputs (no hidden randomization) – enforced by removal of simulation logic after Phase 2.
- UCL-2 Precedence: General logging & quality gate standards override local ad-hoc metrics (reuse `ulog` schema keys, avoid bespoke formatting).
- UCL-3 Provenance: `provenance` block (inputs, adapters_used, collection_started, duration_ms, source_hashes) embedded in JSON.
- UCL-4 Reproducibility: Adapter parameters (intervals, filters) recorded in snapshot; deterministic ordering.
- UCL-5 Integrity: Raw adapter outputs persisted in DuckDB before transformation; transformation hashed.

## 3. Data Source Contract Matrix
| Domain | Source | Adapter Interface (method) | Core Fields | Frequency | Failure Mode | Freshness TTL | Notes |
|--------|--------|----------------------------|-------------|-----------|--------------|--------------|-------|
| Performance | DTMPerformanceCollector / Orchestrator | `PerformanceDataProvider.collect()` | response_time, task_throughput, cpu_pct, mem_pct, overall_score | 30s | Timeout / HTTP | 90s | Wrap existing collector; add timing + error fields |
| Tasks | DTM Task API / cf_cli layer | `TaskDataProvider.fetch_tasks()` | task_id, name, status, pattern, cof_score?, ucl_score? | 60s | API fail | 180s | Initially basic subset; extend with compliance refs |
| Quality Gates | Quality subsystem / logs | `QualityGateProvider.get_status()` | gate_name, status, score, criteria_met, total, duration_ms | On change / 120s poll | Missing log | 240s | Might tail log or query orchestrator state |
| Compliance (COF/UCL) | Compliance analyzer planned module / evidence logs | `ComplianceProvider.evaluate()` | 13 dimension scores, 5 law scores, evidence_counts | 120s | Analyzer unavailable | 300s | Fallback: last known snapshot |
| Alerts (derived) | Computed local | `AlertEngine.evaluate(metrics, history)` | rule_id, severity, triggered, reason | 30s | N/A | N/A | Stateless ex: first pass; escalate if consecutive |
| History | DuckDB | `HistoryStore.append(snapshot)` | snapshot_id, timestamp, metrics JSON, provenance | per snapshot | IO error | Durable | Append-only; periodic vacuum |

## 4. Adapter Interface (Protocol / ABC Sketch)
```python
from typing import Protocol, runtime_checkable, Sequence, Mapping, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CollectionResult:
    started_at: datetime
    duration_ms: int
    ok: bool
    data: Any
    error: str | None = None

@runtime_checkable
class PerformanceDataProvider(Protocol):
    async def collect(self) -> CollectionResult: ...

@runtime_checkable
class TaskDataProvider(Protocol):
    async def fetch_tasks(self) -> CollectionResult: ...

@runtime_checkable
class QualityGateProvider(Protocol):
    async def get_status(self) -> CollectionResult: ...

@runtime_checkable
class ComplianceProvider(Protocol):
    async def evaluate(self) -> CollectionResult: ...

@runtime_checkable
class HistoryStore(Protocol):
    async def append(self, snapshot: Mapping[str, Any]) -> None: ...
    async def recent(self, limit: int = 50) -> Sequence[Mapping[str, Any]]: ...
```
DI Strategy: Pass providers into `DTMConstitutionalDashboard(__init__, providers: dict[str, Any])`. Fallback to simulation provider objects if missing.

## 5. Persistence & Time‑Series (DuckDB) Design
File: `dash_history.duckdb`
Tables:
```sql
CREATE TABLE dashboard_snapshot (
  snapshot_id TEXT PRIMARY KEY,
  ts TIMESTAMP NOT NULL,
  schema_version TEXT NOT NULL,
  compliance_pct DOUBLE,
  avg_cof DOUBLE,
  avg_ucl DOUBLE,
  perf_overall DOUBLE,
  total_tasks INT,
  constitutional_tasks INT,
  quality_passed INT,
  quality_total INT,
  trend_direction TEXT,
  sacred_json JSON,
  risk_json JSON,
  raw_metrics_json JSON,            -- full metrics blob
  provenance_json JSON,             -- inputs & adapter timing
  alerts_json JSON,                 -- alerts triggered in snapshot
  hash_sha256 TEXT NOT NULL         -- content integrity
);
CREATE INDEX dashboard_snapshot_ts_idx ON dashboard_snapshot(ts);
```
Retention: 14 days rolling (configurable). Archival: export CSV or Parquet weekly (future).

## 6. JSON Snapshot Schema (v1)
Root Keys:
- `schema_version`: `cf.dtm.dashboard.v1`
- `generated_at`, `dtm_base_url`
- `metrics`: (current `DashboardMetrics` + add `hash_fields` subset)
- `cof_dimensions`, `ucl_laws`, `quality_gates`, `task_profiles`
- `alerts`: list[{rule_id, severity, message, triggered_at}]
- `provenance`: { adapters_used: [...], durations_ms: {name: int}, source_hashes: {name: sha256}, collection_started, collection_completed, errors: {adapter: msg}}
- `integrity`: { snapshot_hash, method: "sha256", content_includes: [keys...] }

Hash Calculation: Deterministic ordering → JSON canonical dump of selected keys → sha256 hex.

## 7. Logging & Event Map (ulog)
Baseline events (LOG-001..009 compliance):
- `dashboard_init`
- `dashboard_collect_start` / `dashboard_collect_end` (duration_ms, adapters_ok/failed)
- `dashboard_snapshot_persisted` (snapshot_id, hash)
- `dashboard_alert_triggered` (rule_id, severity, reason)
- `dashboard_state_change` (from, to)
- `dashboard_error` (exception_type, message, adapter?)
Evidence Tier Activation: when COF or UCL average delta > 10% over last 3 snapshots OR quality gate failure appears.

## 8. Alert Rule Specification (Phase 2)
| Rule ID | Condition | Severity | Cooldown | Escalation | Notes |
|---------|-----------|----------|----------|------------|-------|
| perf_response_slow | response_time > 200ms for 3 consecutive snapshots | medium | 90s | escalate to high if >400ms | Performance drift |
| gate_failure | any quality_gate.status == failed | high | 0 | immediate repeat allowed | Must page operator |
| compliance_drop | compliance_percentage decrease >= 0.1 vs prev snapshot | high | 120s | escalate if persists 3 cycles | Constitutional regression |
| stale_data | adapter freshness > TTL | medium | 180s | escalate if >2x TTL | Might disable alerts until recovered |
| perf_cpu_saturation | cpu_pct > 85 for 2 snapshots | medium | 60s | escalate at 95% | Auto-scaling suggestion |

Alert Evaluation Order: data integrity → adapter freshness → critical gates → compliance shifts → performance thresholds → optimization suggestions.

## 9. Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Residual |
|------|--------|------------|-----------|----------|
| Adapter timeout | Stale metrics & misleading compliance | Medium | Timeout + fallback last data + freshness annotation | Low |
| Alert noise | Operator fatigue | High | Cooldown + consecutive trigger logic | Medium |
| Schema drift | Incompatible consumers | Medium | Version pin + integrity hash + CHANGELOG update | Low |
| Performance overhead | Resource contention | Low | Async gather + granular intervals | Low |
| Partial failures hidden | Integrity gap | Medium | explicit adapter error logging + provenance.errors | Low |
| Large task lists degrade HTML | UX lag | Medium | Pagination & lazy render (Phase 3) | Low |

## 10. Iterative Implementation Plan
Phase 1 (Current Sprint): Adapters + DI + JSON schema v1 + DuckDB persistence + provenance + logging & snapshot hashing.
Phase 2: Alert engine + CLI subcommands + adapter hardening + basic tests (unit + integration) + reliability/backoff.
Phase 3: Historical trend visualization (HTML spark lines) + drill-down task/profile filters + pagination.
Phase 4: Security controls (RBAC layers) + documentation & runbooks + final performance tuning.

## 11. Confidence Threshold (≥95%) Criteria
| Criterion | Weight | Measurement | Target |
|-----------|--------|------------|--------|
| Adapter Coverage (perf, tasks, gates, compliance) | 25% | Implemented + tests | 100% |
| Data Integrity (hash + provenance completeness) | 20% | Hash match rate | 100% |
| Persistence Reliability | 15% | Consecutive snapshots persisted (50 run test) | >98% |
| Alert Accuracy | 15% | Synthetic trigger tests | >95% correct |
| Quality Gate Integration | 10% | Gates reflected accurately in snapshots | 100% |
| Performance Overhead | 5% | Collection cycle < 1.5s @ baseline | Pass |
| Test Coverage | 10% | Line/function coverage on dashboard module | >=80% |
Pass Threshold: Σ(weight * achieved %) ≥ 95%. Confidence report emitted as decision event.

## 12. Test Strategy (Preview)
- Unit: Adapter mocks, hashing function, provenance builder, alert evaluator.
- Integration: End-to-end snapshot generation with temporary DuckDB file.
- Property: Hash stability under deterministic inputs.
- Synthetic: Force failure modes (timeouts, partial data) ensure provenance + freshness flags.

## 13. Implementation Rules & Guardrails
- Remove simulated random compliance generation once compliance provider integrated (flag `simulation_mode` for transitional phase, auto-warning if still true after Phase 2).
- All adapters must time operations and include `duration_ms` & `ok` field.
- Any adapter error → still produce snapshot (degraded) with `state=degraded` & `alerts` containing `stale_data`.
- No direct file writes outside defined locations (HTML root, JSON root, DuckDB path). Paths configurable.

## 14. Next Actions (Immediate)
1. Introduce adapter protocols & dependency injection (Phase 1 start).
2. Refactor dashboard constructor to accept providers + history store.
3. Implement DuckDB HistoryStore (append + recent).
4. Implement snapshot hashing + provenance block.
5. Replace internal simulated metrics path with provider fallback wrappers.
6. Add logging events per §7.
7. Commit initial tests for hashing & history store.
8. Produce first persisted snapshot & integrity verify.

## 15. Open Questions (Track)
- Source of ground-truth COF/UCL scores (external analyzer module ETA?)
- Quality gate event feed: direct API vs log tailing.
- Future multi-tenant partitioning requirements?

## 16. AAR (Micro – Research Phase)
What Worked: Rapid gap identification & structured adapter plan.
Risk Exposed: Continued simulation could mask drift.
Decision: Enforce simulation_mode warning + early removal in Phase 2.
Next Spiral Increment: Implement Phase 1 actions above.

---
This research matrix establishes constitutional, architectural, and operational foundation to proceed with implementation while maintaining UCL & COF compliance and enabling iterative refinement toward ≥95% confidence.
