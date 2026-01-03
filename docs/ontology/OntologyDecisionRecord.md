# Ontology Decision Record (ODR-0001)

**Status:** Locked
**Correlation ID:** 6b6d5f5e-4b3a-4c2a-9fb1-6d8f3e2c9c11
**Date:** 2025-09-23
**Related Tasks:** ontology-decision-lock, ontology-module-scaffold, ontology-parity-snapshot-cli, evidence-taxonomy-expansion

---
## 1. Purpose / Identity (COF: Identity, Intent)
Establish a falsifiable, measurable baseline for Context Ontology parity evaluation BEFORE any
implementation of the ontology module or parity snapshot CLI. This record freezes thresholds,
methods, retention, and surface embedding so subsequent code changes are testable and auditable.

## 2. Scope (COF: Scope)
In scope: discovery strategy, parity metric definitions, target thresholds, composite index formula, snapshot file schema (v0), retention policy, CLI embedding contract, event taxonomy additions, quality gates.
Out of scope: enrichment/gap classification algorithms (handled by enriched delta task), transformation planning logic, migration plan YAML content, Quantum Sync Engine internals.

## 3. Discovery Method (COF: Modality, Context)
Chosen approach: **Hybrid Static + Runtime Reflection**
- Static (AST + filesystem pattern) extracts declared handlers, model/dataclass fields.
- Runtime reflection inspects loaded cf_cli & dbcli modules to capture dynamic registrations.
- Union set is canonical candidate operation universe; mismatches flagged.
Rationale: Pure runtime misses dead/legacy code risk; pure static misses dynamic plugin/registration patterns.
Risk Mitigation: Log discovery counts (static_count, runtime_count, union_count, overlap_pct). If overlap_pct < 70% emit warning event `ontology_discovery_divergence`.

## 4. Parity Metrics (COF: Evidence, Scale)
| Metric | Definition | Target (Pass) | Criticality |
|--------|------------|---------------|-------------|
| field_coverage_pct | (# universal schema fields represented in cf_cli context pipeline) / (total universal fields) | >= 0.90 | High |
| dimension_coverage_pct | (# COF dimensions with at least one validated mapping) / 13 | >= 0.85 | High |
| critical_ops_completeness | Fraction of mandatory operations (status, create/update task, migration export, parity snapshot) implemented | 1.00 | Blocker |
| operation_overlap_pct | Intersection(cf_cli ops, dbcli ops) / union | >= 0.80 | Medium |
| orphan_ops_pct | Ops in dbcli absent in cf_cli (normalized) / dbcli_total | <= 0.10 | Medium |
| composite_index | Weighted score (see below) | >= 0.88 | High |

Composite Index Formula (v1):
```text
composite_index = 0.30*field_coverage_pct + 0.25*dimension_coverage_pct + 0.25*critical_ops_completeness + 0.10*operation_overlap_pct + 0.10*(1 - orphan_ops_pct)
```
All percentages expressed as decimals (e.g., 0.90). Failing any High criticality metric OR composite_index < target blocks ratification.

## 5. Snapshot Schema (v0) (COF: Modality)
File: `parity_snapshots/ParitySnapshot.<iso8601>.json`
```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-09-23T12:34:56Z",
  "correlation_id": "uuid",
  "metrics": {
    "field_coverage_pct": 0.91,
    "dimension_coverage_pct": 0.85,
    "critical_ops_completeness": 1.0,
    "operation_overlap_pct": 0.82,
    "orphan_ops_pct": 0.07,
    "composite_index": 0.892
  },
  "discovery": {
    "static_count": 42,
    "runtime_count": 39,
    "union_count": 45,
    "overlap_pct": 0.86
  },
  "sets": {
    "missing_fields": ["<field>"],
    "missing_dimensions": ["Risk"],
    "orphan_operations": ["dbcli_prune_legacy"],
    "new_operations_candidate": ["cf_cli_context_export"]
  },
  "hashes": {
    "universal_schema_sha256": "...",
    "cf_cli_introspection_sha256": "...",
    "dbcli_introspection_sha256": "..."
  }
}
```

## 6. Retention Policy (COF: Time)
- Keep last **10** rolling snapshots.
- Add **daily anchor** (first snapshot per UTC day) preserved for 30 days.
- Eviction on write: delete oldest non-anchor beyond window.
- Emit `parity_snapshot_retention` decision event listing retained + evicted filenames.

## 7. CLI Embedding Contract (cf_cli status) (COF: Identity, Context)
Augment `cf_cli status` JSON with block:
```json
"ontology_parity": {
  "latest": {
    "generated_at": "...",
    "field": 0.91,
    "dimension": 0.85,
    "critical_ops": 1.0,
    "composite": 0.892,
    "meets_threshold": true
  },
  "targets": {"field": 0.90, "dimension": 0.85, "composite": 0.88},
  "snapshot_count": 7
}
```
Human (rich) view: compact bar / color-coded pass-fail icons. Alias command planned: `ontology status`.

## 8. Event Taxonomy Additions (COF: Evidence)
New event types (JSONL):
- `ontology_decision_locked` (once; captures thresholds & formula)
- `ontology_discovery_divergence` (conditional)
- `parity_snapshot_emit` (each snapshot; includes metrics + hash, retained_count)
- `parity_snapshot_retention` (post-eviction)
All must include: correlation_id, action, component="ontology", result, metrics subset, duration_ms where applicable.

## 9. Quality Gates (COF: State)
- Gate A: `ontology_decision_locked` event present before module scaffold tests run.
- Gate B: Snapshot command integration tests must assert schema_version and threshold evaluation.
- Gate C: Failing High criticality metric marks snapshot `meets_threshold=false`; CLI must propagate.
- Gate D: Evidence manifest includes latest snapshot hash; parity snapshot absence during ratification blocks authority cutover.

## 10. Risks & Mitigations (COF: Risk)
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Over-fitting composite weights | Misleading readiness | Medium | Revisit weights after 3 snapshots (decision log) |
| Discovery divergence persistent | Incomplete parity view | Low | Emit divergence events; add targeted tests |
| Retention misconfiguration | Loss of forensic trail | Low | Daily anchor rule + manifest references |
| Performance regression (snapshot) | Status latency >50ms | Medium | Lazy-load ontology module; cap introspection time with timeout & log |

## 11. UCL Compliance (COF: Ethics/Evidence)
- Verifiability: Metrics reproducible from snapshot + source introspection outputs.
- Precedence: Universal schema remains higher authority than derived cf_cli fields; missing universal field always counted missing.
- Provenance: Hashes recorded; correlation_id ties to logs.
- Reproducibility: Deterministic metric formula & ordered sets.
- Integrity: No mutation of source artifacts; snapshots append-only until retention eviction.

## 12. Composite Index Justification (COF: Rationale)
Weights emphasize foundational coverage (fields + dimensions + critical ops = 0.80) while still incentivizing operational overlap & low orphan rate (0.20). Provides early warning if structural parity lags even when operations superficially align.

## 13. Change Control (COF: State)
Any future adjustment to thresholds, weights, or schema_version MUST:
1. Emit `ontology_decision_amended` with prior vs new values.
2. Bump `schema_version` (minor for additive, major for breaking).
3. Update JSON Schema (once formalized) & associated tests.

## 14. Implementation Sequencing Alignment
1. Emit lock event (this record).
2. Scaffold module using frozen spec.
3. Implement snapshot command + status embedding.
4. Add evidence taxonomy events & tests.
5. Generate first snapshot (expected to fail or partial - allowed) to validate pipeline.
6. Iterate until targets met ahead of authority ratification.

## 15. Approval / Lock
locked 2025-09-23T18:45:00Z (correlation_id=6b6d5f5e-4b3a-4c2a-9fb1-6d8f3e2c9c11)
Lock Event Emitted: 2025-09-23T18:45:00Z (`ontology_decision_locked`)

---
*End of Ontology Decision Record v1.0*
