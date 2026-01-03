# Consolidated Lessons from Communication-to-ChatGPT Artifacts

This file preserves distilled lessons before bulk removal of historical
`Communication-to-ChatGPT-*` artifacts (implementation handoffs, logging analyses,
sprint gap reports, CLI guide completions). The original 190+ files were high‑granularity
per-session outputs; they are now replaced by durable standards (instructions file,
README docs, logger evidence, tracker DB authority). Removing them reduces noise and
drift risk while retaining actionable knowledge.

## Core Themes

### 1. Logging & Observability
- Maintain Minimal Viable Events (session_start → session_summary) for every substantive run.
- Include artifact hashes (artifact_emit) for integrity and compliance.
- Use JSONL as authoritative, with optional Rich/Markdown only for human scan.
- Detect and remediate logging gaps early (decision events: logging_gap_detected, logging_deficit).

### 2. CLI Design & Documentation
- Prefer a slim, stable minimal CLI for orchestration and a richer Typer/Rich CLI for interactive exploration.
- Provide consistent flags: --json / --limit / --order-by / --descending.
- Emit machine-consumable JSON always identical in schema across commands.
- Avoid duplication: centralize shared formatting + DB access helpers.

### 3. Database Authority Migration
- Single source of truth: SQLite replaces ad‑hoc CSV edits once sentinel present.
- All mutations flow through CLI commands (no manual CSV writes) → enables heartbeats + audit.
- Normalization step cleans legacy/partial rows before promotion.

### 4. Gap Analysis → Sprint Framing Pattern
1. Enumerate missing capabilities (search/show/update/delete, analytics, workflow, tests).
2. Map each gap to a tracker task with geometry shape & stage.
3. Establish sprint + project scaffolding; log heartbeats during implementation.
4. Validate via targeted smoke + integration tests before closing tasks.

### 5. Velocity & Forecasting
- Capture sessions retroactively by hours with contextual metrics (lines/files complexity).
- Derive hours_per_point over 30‑day rolling window; fallback defaults when insufficient data.
- Confidence scales with completed_tasks; always surface confidence percentage.

### 6. Evidence & Risk Management
- Elevate to evidence tier only on triggers (public_api_change, high_risk, lines_changed threshold).
- Keep evidence lean: requirement_id, validation_status, timestamp, hash chain.
- Archive verbose narrative outputs once consolidated into standards to avoid drift.

### 7. Testing & Quality Gates
- Fast “Gate” suite for fail‑fast; extended suites (Governance, Orchestrator, LoggingExtended) for deeper assurance.
- Incremental analyzers (PSSA/Pester incremental) reduce cycle time; cache hits logged.
- Broad exceptions only at final CLI boundary; inner layers use narrow exception taxonomy.

### 8. Sustainable Artifact Hygiene
- Prefer a single canonical summary over many near‑duplicate session reports.
- Periodically prune superseded comm artifacts after extracting lessons (this file is the retained synthesis).

## Representative Best Practices (Retained)
- Direct Python invocation (no nested pwsh wrappers) for governance + trackers.
- Structured logging first; console output is convenience.
- Order/limit parameters on list commands for predictable pagination.
- Hash + size every emitted file; store under deterministic paths.

## Actionable Follow-Ups (Optional)

| Area | Next Step | Benefit |
|------|-----------|---------|
| Logging | Add automated coverage scan to CI summary badge | Continuous visibility |
| Velocity | Introduce outlier trimming for hours_per_point | Stability of forecasts |
| CLI | Generate JSON schema for each --json output | Contract validation |
| Testing | Add mutation tests for drift detection logic | Robustness |
| Evidence | Auto-link evidence entries to tracker IDs | Traceability |

## Rationale for Deletion
The removed files were: transient per-session communication handoffs, overlapping in
content with authoritative instruction standards and tracker data. Retaining all
increased cognitive and governance overhead. This consolidation honors the
"Workspace First" reuse principle and reduces drift vectors.

## Hash (Integrity of This Summary)
Will be emitted by logging pipeline on next run as artifact_emit.

---
Consolidation timestamp: {{AUTO_UPDATE_AT_RUNTIME}}
Session: Communication Cleanup
