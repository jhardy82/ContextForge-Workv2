# Joyride Enablement Plan

**Initiative**: Quantum Persona Terminal Augmentation (Agent–Terminal Interaction Lift)
**Date**: 2025-11-16
**Personas Engaged**: DevOps Platform Engineer, Site Reliability Engineer, Software Quality Engineer, Engineering Team Lead, Workplace Productivity Specialist, Digital Transformation Strategist

---
## 1. Objectives & Constraints
- Reduce manual diagnostic time (logs, test failures, connection checks) by ≥40% within 4 weeks.
- Decrease mean time-to-first actionable test failure insight from ~90s baseline to <30s.
- Maintain CI pipeline added latency per Joyride automation <3s (hard ceiling).
- Ensure <1% script invocation error rate (SRE reliability gate).
- Provide observable adoption telemetry (daily active unique personas using scripts) with weekly trend.

Constraints:
- Non-invasive: scripts must *read* VS Code state, not mutate production sources unless explicitly confirmed.
- Privacy: never persist secret values; redact tokens/password patterns automatically.
- Rollback: any script must be removable by deleting a single file (no global side effects).

### 1.1 Measurement Specifications (Added for Objective Validation)
To ensure each objective is empirically verifiable the following metric definitions and collection protocols apply:

| Objective | Metric Definition | Collection Method | Sample Size Requirement | Success Threshold | Formula |
|-----------|-------------------|-------------------|-------------------------|-------------------|---------|
| Diagnostic time reduction | Manual diagnostic time = time from command invocation (diagnostics quick pick or log locator) to cursor positioned at actionable target (failing test line, error line, or DB status message). | Telemetry event pair (`script_invoked` → `diagnostic_opened` / `log_error_jumped`) timestamp delta; fallback manual stopwatch for first 3 baselines. | ≥10 baseline samples across ≥2 personas before Phase 1 exit | ≥40% reduction vs baseline average at Week 4 | `(baseline_mean - current_mean)/baseline_mean` |
| Time-to-first actionable test failure insight | MTTA (Mean Time To Actionable) = time from opening failing test file to issuance of first remediation command (`pytest -k`, code edit, or note). | Instrument command palette action or editor change → telemetry custom `actionable_commit` event. | ≥10 baseline sequences | <30s sustained median | `median(delta(actionable_commit - diagnostic_opened))` |
| CI added latency ceiling | Additional latency per automation invocation (ms). | Measure script execution latency (`latency_ms`) and ensure CI hook wrappers log `ci_wrapper_latency`. | All CI invocations over 24h window | <3000ms worst-case (hard ceiling) | `max(ci_wrapper_latency)` |
| Invocation error rate | Error rate = error events / total events. | Count `telemetry_event_emitted` with `is_error=true`. | ≥50 events observation window | <1% sustained | `(error_events / total_events)*100` |
| Adoption (DAU personas) | Distinct personas invoking any Joyride script within a rolling 24h window. | Aggregate `persona` field in telemetry snapshots. | Daily | ≥6 by end of Week 4; interim ≥2 by Day 5 | `count(distinct persona)` |
| MTTR improvement | Mean Time To Resolution (test failure) = time from first failure detection to successful re-run passing. | Correlate failure detection timestamp (pytest failure parse) to next passing run via `mttr_pass_event`. | ≥5 failure cycles per week | -25% Week 2; -40% Week 4 vs baseline | `(baseline_mttr - current_mttr)/baseline_mttr` |

Instrumentation Preconditions:
1. Baseline capture must only commence after `telemetry.cljs` wrapper is implemented to avoid skew from missing latency/error fields.
2. Baseline adoption requires ≥2 personas; if not met extend baseline window +24h and annotate variance.
3. All latency measurements store both `latency_ms` and derived percentiles (p50, p95) in daily snapshot for reliability gating.
4. Any metric lacking required sample size is flagged in snapshot with `incomplete_baseline: true` and excluded from improvement claims.
5. All formulas recorded verbatim in `docs/telemetry/schema.yaml` to prevent later interpretive drift.
6. Redaction precedes hashing; payload hash computed on redacted structure to ensure reproducibility.

Objective Validation Notes:
- Current placeholders (e.g., diagnostic time, MTTR) require at least 24h sampling window post wrapper deployment.
- Adoption threshold staged (Day 5 interim, Week 4 final) aligns with internal tooling diffusion curves; will be revisited after external benchmark task.
- Error rate objective validated only after ≥50 events; until then mark reliability status `probing`.


---
## 2. Phased Rollout
### Phase 0 – Baseline & Instrumentation (Day 0–2)
Tasks:
1. Capture baseline metrics manually:
   - Time to locate last test failure.
   - Time to triage a log error (terminal scroll / search).
   - Frequency of DB connection probe commands.
2. Implement lightweight telemetry recording (workspace storage JSON): events: `script_invoked`, `diagnostic_opened`, `log_error_jumped`.
3. Confirm persona access & security constraints.

Exit Criteria: Baseline metrics stored in `docs/metrics/baseline.yaml` + telemetry stub active.

### Phase 1 – Quick Win Scripts (Day 3–7)
Deliverables:
- `diagnostics_quickpick.cljs`: Pick & jump to diagnostics.
- `log_error_locator.cljs`: Surface last N error lines from an attached log file / terminal snapshot (future: streaming not yet supported via API; fallback to file-tail approach).
- `db_connection_probe.cljs`: Issue a lightweight HTTP health call or PG ping via an external helper (if feasible) and display result.

Exit Criteria: Invocation latency <300ms median; error rate <2%; adoption ≥5 distinct invocations/day after day 5.

### Phase 2 – Context Overlays (Week 2)
Deliverables:
- Side-panel summary (diagnostics counts + failing test modules).
- Auto-suggest next action (e.g., "Run pytest -k <failing_test>").
- Performance/latency mini-gauge (requires SRE feed JSON).

Exit Criteria: Overlay loads <500ms; persona satisfaction survey (qualitative) positive (>70% helpful rating).

### Phase 3 – Proactive Intelligence (Week 3–4)
Deliverables:
- Pattern detection: recurring failure signature clustering.
- Suggestion ranking: top 3 probable root causes (SQE + SRE curated model rules).
- Integration: DevOps gating (block overlay if CI red build unresolved > X hours).

Exit Criteria: MTTR reduction >25%; repetitive failure triage time reduced >50% vs baseline.

### Phase 4 – Strategic Optimization & Feedback Loop (Continuous)
- Quarterly review (Strategist + Team Lead): align to evolving KPIs.
- Expand scripts based on logged friction vectors.
- Sunset underused scripts (<5 uses in 2 weeks) after review.

---
## 3. Sample Script Reference (Phase 1)
Primary example delivered in repository: `.joyride/scripts/diagnostics_quickpick.cljs` (see file for implementation). Additional quick-win scripts follow identical pattern: require `vscode`, gather context, present quick pick, open target.

---
## 4. Telemetry & Metrics
| Metric | Source | Baseline (Day 0) | Target | Owner |
|--------|--------|------------------|--------|-------|
| Daily active script users | Telemetry JSON | 0–1 (manual observation) | ≥6 personas by Week 4 | Productivity Specialist |
| Median invocation latency | Time delta inside script | ~420ms (initial prototype) | <300ms Phase 1 | DevOps |
| Error invocation rate | Error catcher wrapper | ~0% (insufficient sample) | <1% stable | SRE |
| MTTR (test failure) | Manual + script log timestamps | ~90s | -25% Week 2; -40% Week 4 | SQE |
| Diagnostic jump success | Post-open verification | 100% (1 pilot jump) | ≥95% sustained | SQE |
| Suggestion accuracy (Phase 3) | Post-action survey | N/A (not implemented) | ≥70% helpful | Strategist |

Baseline values will be formalized in `docs/metrics/baseline.yaml` (see Section 11) after a 24h
measurement window (Day 0–1). Placeholder baselines above are documented for transparency;
they must be replaced with measured samples (≥10 invocations) before Phase 1 exit criteria
evaluation.

Data Storage & Telemetry Strategy:
- Local workspace `state.json` (non-sensitive) rotated daily (filename pattern: `.joyride/telemetry/state-YYYYMMDD.json`).
- Each daily telemetry snapshot hashed (SHA-256) and logged via unified logger (`event_type="telemetry_daily_snapshot"`).
- Redaction pass applied to any value matching secret regex (`/(password|token|secret|api[_-]?key)/i`).
- Planned aggregation: optional weekly roll-up file `docs/metrics/telemetry-weekly.yaml`.

### 4.1 Telemetry Event Schema (Stub)
Schema will reside at `docs/telemetry/schema.yaml` and define events:
| Event | Required Fields | Optional Fields | Notes |
|-------|-----------------|-----------------|-------|
| script_invoked | timestamp, script_id | latency_ms, persona | Emitted at script entry. |
| diagnostic_opened | timestamp, file, line | severity, latency_ms | Validates jump success. |
| log_error_jumped | timestamp, file, line | error_code, latency_ms | For future log locator script. |
| db_probe_executed | timestamp, target | status, latency_ms, error | Phase 1/2 DB health probe. |
| suggestion_presented | timestamp, suggestion_id | accepted, persona | Phase 3 intelligence. |

All events share a correlation id (`corr_id`) and include a hashed (`sha256`) snapshot of the minimal payload for integrity (`payload_hash`).

---
## 5. Risk & Mitigation
| Risk | Impact | Probability | Detection | Mitigation | Owner |
|------|--------|------------|-----------|-----------|-------|
| API limitation (terminal read) | Delays log summarizer | Medium | Attempted API call failure metrics | Use file-tail strategy; defer terminal capture until extension update | DevOps |
| Performance overhead | Slower editor responsiveness | Low–Medium | Latency > target in telemetry (p95 >300ms) | Lazy-load scripts; memoize diagnostics list per 5s interval | SRE |
| Feature creep | Timeline slip | Medium | Scope delta vs phase exit criteria | Rigid scope gates; weekly review; backlog triage | Team Lead |
| Low adoption | Diminished ROI | Medium | DAU < threshold for 3 consecutive days | Persona micro-tutorial pop-up; feedback huddle | Productivity Specialist |
| Privacy leak (secrets in telemetry) | Compliance risk | Low | Redaction audit report / regex match count | Automatic redaction + periodic scan | SQE |
| Baseline drift (unstable initial values) | Misleading improvement claims | Medium | Variance >25% between Day0 and Day1 samples | Extend baseline window to 48h; annotate variance | Strategist |

---
## 6. Rollback Plan
- Remove script files under `.joyride/scripts/` to disable features immediately.
- Delete telemetry JSON to clear stored invocation history.
- Provide manual fallback commands via README.

---
## 7. Next Immediate Actions
**Status Legend**: ✅ done · ▶ in-progress · ⏳ pending · ❗ requires decision

1. Diagnostics quick pick script – ✅ (instrument latency capture still pending enhancement).
2. Telemetry wrapper util (`telemetry.cljs` with event emit + redaction) – ▶ (implement before full baseline measurement cycle).
3. Baseline metrics capture (24h sample → write `docs/metrics/baseline.yaml`) – ⏳ (start Day 0 immediately after wrapper util ready).
4. Log error locator prototype (`log_error_locator.cljs`) – ⏳ (requires configurable log path setting, default `.logs/app.log`).
5. DB connection probe script – ⏳ (graceful handling of missing PG credentials; fallback messaging).
6. Risk table update & periodic detection routine – ✅ (table patched; implement detection script later in Phase 1).
7. Evidence bundle pattern doc snippet (`docs/telemetry/evidence.md`) – ⏳ (define payload_hash + rotation procedure).
8. Add caching (TTL 5s) + latency measurement to diagnostics script – ⏳ (improves p95 target attainment).

---
## 8. Alignment to COF 13D (Summary)
- Motivational: Productivity + MTTR reduction.
- Relational: Integrates with testing, CI, SRE dashboards.
- Situational: PostgreSQL credentials pending; plan isolates non-dependent scripts first.
- Resource: 6 personas distributed by specialty; low initial tooling cost.
- Narrative: Faster cognitive loop turning raw errors into actions.
- Recursive: Weekly friction vector review feeding next sprint.
- Computational: Simple data structures initially; future clustering algorithm.
- Emergent: Potential discovery of latent failure patterns.
- Temporal: Phased timeline with explicit exit criteria.
- Spatial: Local editor scripts; data localized, optional central aggregator later.
- Holistic: Integrates reliability, test quality, UX, strategic value.
- Validation: Metrics & telemetry gating per phase.
- Integration: Scripts dovetail with existing CI/test workflows, minimal intrusion.

---
## 9. Definition of Done (Phase 1)
| Criterion | Description | Evidence Source |
|-----------|-------------|-----------------|
| Diagnostics quick pick operational | Script runs, p95 latency <300ms after caching | Telemetry latency metrics + manual spot check |
| Baseline metrics captured | `docs/metrics/baseline.yaml` contains ≥10 invocation samples + MTTR measurement | Baseline file hash + logger event `baseline_recorded` |
| Telemetry reliability | Error events / total events <1% | Daily snapshot stats (`error_rate`) |
| Adoption threshold | ≥2 distinct personas (user ids) by Day 5 | Telemetry aggregation (`distinct_personas`) |
| Redaction functioning | 0 secret pattern leaks detected in daily audit | Audit log `telemetry_redaction_audit` |
| Risk detection routine stub | Script logs detection metrics for latency & adoption | `risk_detection` events |

---
## 10. Appendix: Invocation Patterns
Example user invocation (Command Palette): `> Joyride: Diagnostics Quick Pick`
Future quick commands: `> Joyride: Last Log Errors`, `> Joyride: DB Health Probe`.

---
**Maintainer Rotation**: Team Lead rotates quarterly; fallback: DevOps Engineer.

---
## 11. Baseline Metrics (Planned Artifact)
Path: `docs/metrics/baseline.yaml`

Example (initial structure):
```yaml
captured_at: 2025-11-17T09:00:00Z
window_hours: 24
samples:
   diagnostic_invocations: 12
   log_error_locator_invocations: 0
latency_ms:
   diagnostics_quickpick:
      p50: 310
      p95: 445
mttr_test_failure_seconds:
   baseline: 90
   target_phase1: 65
adoption:
   distinct_personas: 2
telemetry:
   error_events: 0
   total_events: 38
   error_rate_pct: 0.0
hash: <sha256-populated-by-script>
```

## 12. Evidence & Logging
Every daily telemetry rotation produces:
1. JSON snapshot file (`state-YYYYMMDD.json`).
2. SHA-256 hash recorded via unified logger.
3. Optional compression into `telemetry-YYYYMMDD.tar.gz` if size >50KB.

Logger events:
- `telemetry_event_emitted` (per event)
- `telemetry_daily_snapshot` (roll-up) with fields: `date`, `distinct_personas`, `error_rate`, `p95_latency`, `mttr_sample_count`.
- `baseline_recorded` (once baseline file written).

Retention: 14 days rolling; manual archive beyond that if needed.

## 13. Pending Artifacts Index
| Artifact | Purpose | Phase | Status |
|----------|---------|-------|--------|
| `docs/metrics/baseline.yaml` | Formal baseline values | 0 | Pending |
| `docs/telemetry/schema.yaml` | Event & field specification | 0 | Pending |
| `.joyride/scripts/log_error_locator.cljs` | Surfacing recent log errors | 1 | Pending |
| `.joyride/scripts/db_connection_probe.cljs` | Connection health visibility | 1 | Pending |
| `docs/telemetry/evidence.md` | Evidence bundle pattern | 1 | Pending |
| Diagnostics script caching enhancement | Performance improvement | 1 | Pending |
