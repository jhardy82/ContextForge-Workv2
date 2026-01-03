# Index Expansion Checklist

Track additional directories that require localized `INDEX.md` / README expansions beyond the initial remediation.

## Active Targets

### analytics/
- [x] **Research Plan**: Review `analytics/README.md`, source tree, and tests to identify key subcomponents.
- [x] **Implementation Plan**: Add `analytics/INDEX.md` and reference it from the README.

### TaskMan-v2/backend-api/tests/
- [x] **Research Plan**: Inventory pytest suites, E2E specs, and migrations under `TaskMan-v2/backend-api/tests`.
- [x] **Implementation Plan**: Add `TaskMan-v2/backend-api/tests/INDEX.md` and ensure README_INDEX references it.

### TaskMan-v2/backend-api/tests/e2e/
- [x] **Research Plan**: Extract Playwright test coverage, environments, and prerequisites.
- [x] **Implementation Plan**: Expand README with asset table and ensure linkage from parent tests index.

### docs/validation/
- [x] **Research Plan**: Evaluate current validation docs (QSE, quality gates) and identify anchor files.
- [x] **Implementation Plan**: Add `docs/validation/INDEX.md` summarizing validation guides and requirements.

### logs/ and logging artifacts
- [x] **Research Plan**: Determine structure under `logs/`, `log*` folders, and how they tie to logging enhancements.
- [x] **Implementation Plan**: Create `logs/README.md` describing retention, naming, and governance.

### metrics/ & reports/
- [x] **Research Plan**: Map contents of `metrics/`, `reports/`, and related dashboards.
- [x] **Implementation Plan**: Add READMEs highlighting KPIs, reporting cadence, and data sources (`metrics/README.md`, `reports/README.md`).

### orchestrator/
- [x] **Research Plan**: Review orchestration evidence folders (comms, nudges, context, indexes, workspace).
- [x] **Implementation Plan**: Add `orchestrator/README.md` summarizing subdirectories and their purpose.

## Monitoring Tasks

- [ ] **TaskMan MCP Consolidation**: Update this checklist once `projects/taskman-mcp` is merged/migrated.
- [ ] **Quarterly Audit**: Run README/INDEX audit on **2026-02-16** and log findings here.
