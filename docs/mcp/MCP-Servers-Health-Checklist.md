## MCP Servers – Health & Integration Checklist

This checklist specializes the unified template for **all MCP servers** (task-manager, git-mcp, database-mcp, etc.). It focuses on health checks, integration, logging, and evidence.

### 0. Project Header & Personas

- **Project / Workstream**: `MCP Servers Health & Integration`  
- **Subsystem(s)**: `MCP-Servers | TaskMan MCP | git-mcp | database-mcp | docker-mcp | …`  
- **Primary Authority**: `CF_CLI` (for orchestration) + individual MCP server owners  
- **Work ID / Epic**: `P-TASKMAN-MCP` / `MCP-Servers-Health`  
- **Current Phase (UTMW)**: `Understand → Think`  

**Personas Involved**

- [x] Researcher (`@researcher`) – enumerate servers, analyze logs, map health behavior  
- [x] Implementer (`@implementer`) – fix health endpoints, timers, infrastructure  
- [x] QA / Validator (`@qa-reviewer`) – verify health checks (HTTP, STDIO), integration tests  
- [x] Infra / Platform (`@infra`, `@platform-obs`) – containers, ports, logging, scaling  
- [ ] Architect (`@api-architect`) – cross‑server design (optional but recommended)  

Status:
- [x] Not started
- [ ] In progress
- [ ] Blocked
- [ ] Done

---

### 1. Tracking Dashboard (Mini-Kanban)

| ID   | Subtask / Milestone                                            | Owner          | Phase | Status   | Evidence Link |
|------|----------------------------------------------------------------|----------------|-------|----------|---------------|
| S-01 | Inventory all MCP servers and their deployment modes           | @researcher    | U     | ☐        | `mcp-servers/*` |
| S-02 | Define standard health interface (HTTP `/api/health`, STDIO ping) | @api-architect | T   | ☐        | …             |
| S-03 | Implement/verify health endpoints across MCP servers           | @implementer   | M     | ☐        | …             |
| S-04 | Standardize logging schema and evidence requirements           | @platform-obs  | M/W   | ☐        | …             |
| S-05 | Add cross‑server MCP health tests and CI integration           | @qa-reviewer   | W     | ☐        | …             |
| S-02 | Collect logs & artifacts                               | @researcher| U               | ☐ Pending      | …             |
| S-03 | Form hypotheses & experiments                          | @researcher| T               | ☐ Pending      | …             |
| S-04 | Design implementation plan (CF_CLI-first)              | @architect | T               | ☐ Pending      | …             |
| S-05 | Implement changes                                      | @implementer| M              | ☐ Pending      | …             |
| S-06 | Validate via tests, logs, metrics                      | @qa-reviewer| W              | ☐ Pending      | …             |
| S-07 | COF/UCL + QSE validation & documentation               | @cof-13d-analyst| W          | ☐ Pending      | …             |

Legend (Status): ☐ Pending · ⏳ In progress · ✔ Done · ⚠ Blocked

---

## 2. Scope & Research Questions (Understand)

**Problem Statement**

- …

**Context & Systems Involved**

- [ ] TaskMan-v2 (PostgreSQL authority)  
- [ ] CF_CORE / `cf_cli` (PostgreSQL primary, SQLite fallback)  
- [ ] MCP Server(s): `…`  
- [ ] UI / VS Code extensions (`vs-code-task-manager`, TaskMan-v2 extension)  
- [ ] QSE / COF / UCL  
- [ ] Gamification / Nudge engines  

**Key Questions**

- Q1: …  
- Q2: …  
- Q3: …  

**Initial Assumptions (to validate/kill)**

- A1: …  
- A2: …  

---

## 3. Evidence Collection (Logs, DB, Tests)

> Principle: Logs-first, CF_CLI-first, no assumptions without evidence.

**Log Sources**

- [ ] `logs/cf_cli.log` (CF_CLI orchestration and MCP tool calls)  
- [ ] `logs/mcp-api-*.log` (MCP backend services)  
- [ ] `logs/mcp-frontend-*.log` (any MCP-related UI / VS Code integration logs)  
- [ ] `logs/system-operations.log` / other infra logs for port/process health  
- [ ] QSE / Gamification logs (when MCP is invoked via QSE/gamification flows)  
 - [ ] MCP server code inventories and structured logging backlog: `reports/logging/logging-inventory-mcp-servers.json`, `reports/logging/MCP-Servers-Structured-Logging-Refactor-Backlog.md`  

**DB / Schema Evidence**

- [ ] PostgreSQL schema & constraints (via DB MCP / CF_CLI)  
- [ ] SQLite schema (fallback/legacy)  

**Evidence Bundle Index (for this project)**

| Bundle ID      | Description                           | Source(s)                         | Hash / ID          |
|----------------|---------------------------------------|-----------------------------------|--------------------|
| EVID-PROJ-001  | …                                     | `logs/…`                          | `sha256:…`         |

Actions:

- [ ] Identify relevant log files and time windows.  
- [ ] Extract error patterns, warnings, anomalies.  
- [ ] Record evidence bundles and hashes (align with `reports/bugs/*` or project‑specific evidence files).  

---

## 4. Hypotheses & Experiment Design (Think)

**Hypothesis Register**

| HYP ID       | Statement (short)                           | Confidence | Evidence Bundles      |
|-------------|----------------------------------------------|-----------|-----------------------|
| HYP-PROJ-01 | …                                            | low/med/high | EVID-PROJ-001, … |

Example detail:

- **HYP-PROJ-01**  
  - Statement: …  
  - Confidence: `low|medium|high`  
  - Evidence: `…`  
  - Tests to run:
    - T1: `…`
    - T2: `…`

**CF_CLI / MCP Repro Plan**

- [ ] Define CF_CLI commands for reproduction (e.g., `python cf_cli.py task update …`).  
- [ ] Define MCP / HTTP requests (TaskMan‑v2 API, MCP server endpoints).  
- [ ] Specify success/failure criteria based on:
  - Log patterns (errors disappear or change as expected).  
  - Task/DB state (CF_CLI + DB MCP).  

---

## 5. Implementation Checklist (Make)

Summary of implementation work; more granular items can live in code/PR descriptions.

- [ ] Confirm authoritative entrypoints (e.g., `cf_cli.py`, `TaskMan-v2 backend`, specific MCP server).  
- [ ] Route operations via CF_CLI and MCP tools rather than direct module/DB access, when possible.  
- [ ] Implement code/config changes in minimal, focused patches.  
- [ ] Update/add tests (unit, integration, QSE harness) close to affected components.  
- [ ] Update docs (README, workspace docs, bug plans) to reflect new behavior/contracts.  

**Implementation Notes**

- Repos/components touched: `…`  
- Branch/PR links: `…`  

---

## 6. Validation & Gates (Win)

### 6.1 Test & Metrics Checklist

- [ ] Python tests (CF_CORE / analytics): `python -m pytest …`  
- [ ] Node/TS tests (TaskMan‑v2 / MCP servers): `npm test`, `npm run test:coverage`  
- [ ] PowerShell tests (where applicable): `pwsh -Command "& build/Run-PesterTests.ps1 -Suite …"`  
- [ ] QSE validation: `qse_cli.py test …`  

**Log-based Validation**

- [ ] Re-run log mining queries for key error signatures (before vs after).  
- [ ] Confirm critical/high patterns are eliminated or significantly reduced.  

**SLI/SLO Snapshot (optional)**

- DB connectivity error rate: …  
- Task mutation success rate: …  
- cf_cli session success rate: …  
- MCP server health rate: …  

### 6.2 Checkpoint Gates

Use gates to decide if the project is ready to progress.

- **Gate 0 – Baseline Ready**  
  - [ ] Dependencies restored (e.g., `npm install` / `pip install` verified).  
  - [ ] Typecheck/build passes (where applicable).  
  - [ ] Baseline metrics documented (e.g., `docs/BASELINE-METRICS.md`).  

- **Gate 1 – Implementation Ready**  
  - [ ] Hypotheses + repro specs finalized.  
  - [ ] Risks & dependencies identified.  

- **Gate 2 – Validation Complete**  
  - [ ] All targeted tests and log checks passed.  
  - [ ] No blocking regressions discovered.  

Record Go/No‑Go decisions and rationale here.

---

## 7. Logging & Observability Checklist

Adapt from UnifiedLogger / project needs.

**Required Events (example)**

- Early‑phase:
  - [ ] `session_start`  
  - [ ] `artifact_touch_batch` / equivalent  
  - [ ] `task_start` / `task_end`  
  - [ ] `decision`  
- Finals:
  - [ ] `session_end`  
  - [ ] `session_summary`  

**Path & Policy**

- [ ] Default logs under `logs/` (project‑local).  
- [ ] Any exceptions (e.g., PowerShell utilities to `C:\Temp`) documented.  

**Redaction**

- [ ] `UNIFIED_LOG_REDACT` configured (if applicable).  
- [ ] `UNIFIED_LOG_REDACT_REGEX` configured (if applicable).  

**JSONL Fields**

Minimum fields for evidence bundling:

- [ ] `timestamp`  
- [ ] `event_type` / `action`  
- [ ] `component`  
- [ ] `error_message` (if applicable)  
- [ ] `stack_trace` (if applicable)  
- [ ] `correlation_id` / `run_id`  
- [ ] `ok` / `command_ok` semantics clearly defined  

---

## 8. COF / UCL & QSE Alignment

**COF Dimensions Impacted (examples)**

- [ ] Reliability  
- [ ] Observability  
- [ ] Integrity / Consistency  
- [ ] UX / Developer Experience  
- [ ] Performance / Efficiency  
- [ ] …  

**UCL Considerations**

- UCL‑1 (e.g., Evidence & Transparency): …  
- UCL‑2 (e.g., Safe Defaults): …  
- UCL‑3/4/5: …  

**QSE Hooks**

- QSE Phase(s): `0–8` (e.g., Phase 2 – Research, Phase 6 – Execution with evidence, Phase 7 – Testing).  
- QSE Work IDs: `W-QSE-…` (if applicable).  
- Linked YAML test checklists (optional):
  - [ ] `qse/artifacts/.../Test.Checklist.….yaml`  
  - [ ] Hashes recorded and verified.  

---

## 9. Collaboration & Hand‑offs

Use this to track human / agent collaboration and decisions.

**Check‑ins / Standups**

- Date: `YYYY-MM-DD`  
  - Participants: `@…`  
  - Highlights:  
    - …  
  - Blockers:  
    - …  

**Decisions & ADRs**

- D1: … (link to ADR or design doc)  
- D2: …  

**Follow‑ups**

- [ ] …  
- [ ] …  

---

## 10. Closure Checklist

Before marking this project workstream **Done**:

- [ ] All high/critical issues have clear outcomes (fixed, deferred, accepted risk) with evidence.  
- [ ] Evidence bundles are updated and cross‑linked from logs/tests (JSONL +, optionally, YAML).  
- [ ] Any new or follow‑on tasks are created via CF_CLI (TaskMan‑v2) and linked here.  
- [ ] COF/UCL considerations are documented and satisfied or explicitly waived with rationale.  
- [ ] A brief AAR or summary is captured in `docs/` (if warranted).  
