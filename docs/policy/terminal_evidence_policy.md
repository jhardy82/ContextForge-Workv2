# Terminal Evidence Policy

Policy Version: 2025-08-26

Directive: Confirmation of success from the terminal alone is acceptable **0%** of the time.

Rationale:
- Terminal exit code / absence of errors is an insufficient signal (silent failures & suppressed output observed).
- Reliability requires artifact + structured log corroboration.

Enforcement Rules:
1. Every substantive test or governance run MUST emit:
   - Structured JSONL events (minimum event set: session_start, task_start, decision, artifact_emit, task_end, session_summary).
   - At least one machine-parseable artifact (summary.json, junit.xml, reconcile.json, coverage.xml, etc.).
2. A run reporting zero executed tests with exit code 0 SHALL be reclassified as anomaly and forced non‑zero exit (custom code 6).
3. Harnesses MUST snapshot minimal environment context (cwd, interpreter path, filtered env vars) prior to execution.
4. Missing required artifacts triggers failure classification regardless of terminal text.
5. Fallback execution path (in‑process pytest) MUST activate if subprocess yields no output lines.

Implementation Hooks:
- `python/tools/pytest_capture.py` enforces zero-test anomaly detection and includes `SUCCESS_VALIDATION_POLICY` constant.
- Tracker actions (`evidence_policy_reinforced`, `terminal_evidence_policy_doc_added`) record adoption.

Acceptance Indicators:
- Presence of `env.json`, `summary.json`, and `raw.log` (or explicit fallback log events) per capture run.
- No green runs with executed=0 unless inventory=0 AND explicit skip rationale event present.

Escalation:
- First violation: warning + remediation guidance.
- Repeat violation: mark task health yellow.
- Third consecutive violation: mark health red and create remediation backlog task.

Change Log:
- 2025-08-26: Initial policy established.
