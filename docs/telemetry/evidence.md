## Telemetry Evidence & Integrity Protocol

**Version:** 1.0.0
**Scope:** Joyride Quantum Persona Terminal Augmentation telemetry artifacts.

### 1. Artefact Types
| Artifact | Pattern | Purpose | Integrity | Rotation |
|----------|---------|---------|-----------|----------|
| Event stream (raw) | `.joyride/telemetry/telemetry-YYYY-MM-DD.jsonl` | Append-only per event | Per-line SHA-256 (payload_hash) | Daily file |
| Daily snapshot | `.joyride/telemetry/state-YYYYMMDD.json` | Aggregates (p50/p95, counts) | Whole-file SHA-256 logged | Daily file |
| Baseline metrics | `docs/metrics/baseline.yaml` | Pre-optimization benchmark | Whole-file SHA-256 + baseline_recorded event | Once (Phase 0) |
| Weekly roll‑up (optional) | `docs/metrics/telemetry-weekly.yaml` | Trend consolidation | SHA-256 logged | Weekly (if enabled) |

### 2. Event Integrity
Each event emits: `payload_hash = sha256(redacted_payload_json)`. Redaction ALWAYS precedes hashing. Removed keys listed in `redacted_keys` for audit transparency.

### 3. Daily Rotation
At first event after UTC date change:
1. Close previous JSONL handle (append completed).
2. Emit `telemetry_daily_snapshot` with: `{date, distinct_personas, error_rate, latency_p95, mttr_sample_count, file_hash}`.
3. If size > 50KB → compress (`telemetry-YYYY-MM-DD.tar.gz`) & emit `telemetry_archive_created`.

### 4. Baseline Capture
Baseline file written **only after** thresholds met:
* ≥10 diagnostic_invocation samples
* ≥10 actionable_commit sequences (if measuring MTTA)
* ≥2 distinct personas
* ≥50 total events for error rate computation

Then emit `baseline_recorded` with: `{hash, sample_counts, captured_at}`.

### 5. Redaction Patterns
Regex set (case-insensitive):
```
password | token | secret | api[_-]?key | credential | authorization
```
Strategy: drop matching keys entirely, never persist value placeholder. Audit pass can count pattern matches before removal; log `telemetry_redaction_audit`.

### 6. Verification Workflow
1. **Line Audit**: Random sample 20 events → ensure no raw secret values present.
2. **Hash Consistency**: Recompute hash for 5 sampled payloads; mismatch ⇒ emit `telemetry_integrity_failure`.
3. **Baseline Stability**: Compare Day0 vs Day1 variance; if >25% latency mean delta ⇒ flag `baseline_variance_high`.

### 7. Pruning Policy
Keep last 14 daily raw files + snapshots. Older: optional manual archive (`archive/telemetry/YYYY/MM/` with manifest containing file name + sha256). Ensure manifest hashed to create immutable chain.

### 8. Chain of Custody (Optional Enhancement)
For stronger tamper resistance: maintain a running Merkle root across daily file hashes; store root in `evidence-chain.yaml`.

### 9. Failure Handling
If write fails (I/O error):
* Emit `telemetry_write_error` (is_error=true) with errno/message.
* Retry max 3 times (exponential backoff 100ms, 250ms, 500ms).
* On persistent failure: surface VS Code warning & pause telemetry until next invocation.

### 10. Metrics Coupling
Improvement claims MUST reference baseline hash + snapshot date. If `incomplete_baseline=true` present in events, exclude from computation.

### 11. Adoption Calculation
Distinct personas per 24h window derived from daily snapshot; improvement gating requires previous 24h adoption ≥2 personas or extended baseline window.

### 12. Risk Detection Events
Emit `risk_detection` when:
* `latency_p95` > 300ms Phase 1 target
* `error_rate_pct` ≥ 1%
* `distinct_personas` < 2 after Day 5

Payload: `{metric, value, threshold, status}`.

### 13. Definition of Done (Telemetry Integrity Phase)
| Criterion | Evidence |
|-----------|----------|
| Redaction functioning | No secret regex matches post-write in audit sample |
| Baseline recorded | `baseline_recorded` event with hash |
| Daily snapshot emission | Presence of `telemetry_daily_snapshot` events ≥1/day |
| Error rate gating | `error_rate_pct` computed after ≥50 events |
| Risk detection active | At least one `risk_detection` event when threshold breached |

---
Maintainer: SQE Persona (rotating quarterly)
