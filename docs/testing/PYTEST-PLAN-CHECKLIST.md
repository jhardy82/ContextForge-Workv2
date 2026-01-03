# Pytest Plan — Comprehensive Execution Checklist

Date: 2025-11-28
Branch: `feat/taskman-v2-python-mcp-research-20251125`
Repository: `jhardy82/SCCMScripts`

This checklist provides an end-to-end, actionable tracker for the recovered pytest plan, aligned to workspace tasks and quality gates. Use it to plan, execute, and audit test operations with clear ownership, status signals, and evidence links.

## Quick Links
- Tasks: `test:quick`, `test:smoke`, `test:coverage`, `test:full`, `test:targeted`, `test:failed`, `test:watch`
- Quality: `quality:format`, `quality:lint`, `quality:type`, `quality:gate`
- Coverage HTML: `artifacts/coverage/html/index.html`
- Smoke Report: `artifacts/test/smoke/report.html`
- Full Report: `artifacts/test/full/report.html`

---

## 1) Preflight & Environment

- [ ] Python venv activated (PowerShell 7)
  - Command:
    ```powershell
    & ".\.venv\Scripts\Activate.ps1"
    ```
- [ ] Environment check completed
  - Command:
    ```powershell
    pwsh -Command "Write-Host '=== Environment Check ===' -ForegroundColor Cyan; Write-Host 'Python:' -NoNewline; python --version; Write-Host 'PowerShell:' -NoNewline; pwsh --version; Write-Host 'Pytest:' -NoNewline; pytest --version; Write-Host 'Pester:' -NoNewline; (Get-Module Pester -ListAvailable | Select-Object -First 1).Version"
    ```
- [ ] Workspace artifacts directory present
  - Outcome: `artifacts/` tree created by tasks; verify write permissions

Owner: `@test-engineer` | Evidence: `artifacts/test/*` | Due: `YYYY-MM-DD`

---

## 2) Lanes & Commands (Runbook)

### A. Quick Lane (fastest feedback)
- [ ] Run quick suite (parallel, minimal output)
  - Command:
    ```powershell
    pytest tests/ -q -x --maxfail=3 -p no:sugar -p no:timer --benchmark-skip --tb=line --no-header -n auto
    ```
  - Artifacts: `artifacts/test/quick/*` (when using task)
  - Task: `test:quick`

### B. Smoke Lane (unit + not slow)
- [ ] Run smoke suite with reports
  - Command:
    ```powershell
    pytest tests/ -m 'unit and not slow' --maxfail=5 -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=short --junitxml=artifacts/test/smoke/junit.xml --json-report --json-report-file=artifacts/test/smoke/results.json --html=artifacts/test/smoke/report.html --self-contained-html
    ```
  - Task: `test:smoke`
  - Evidence:
    - JUnit: `artifacts/test/smoke/junit.xml`
    - HTML: `artifacts/test/smoke/report.html`
    - JSON: `artifacts/test/smoke/results.json`

### C. Coverage Lane (full + coverage)
- [ ] Run coverage suite and publish reports
  - Command:
    ```powershell
    pytest tests/ --cov=src --cov=python --cov-report=html:artifacts/coverage/html --cov-report=term-missing --cov-report=json:artifacts/coverage/coverage.json --cov-report=xml:artifacts/coverage/coverage.xml -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=short --junitxml=artifacts/test/coverage/junit.xml --json-report --json-report-file=artifacts/test/coverage/results.json --html=artifacts/test/coverage/report.html --self-contained-html
    ```
  - Task: `test:coverage`
  - Evidence: coverage HTML/JSON/XML + test reports

### D. Full Suite (strict markers + coverage)
- [ ] Run complete suite with strict markers
  - Command:
    ```powershell
    pytest tests/ -v --cov=src --cov=python --cov-report=html:artifacts/coverage/html --cov-report=term-missing --cov-report=json:artifacts/coverage/coverage.json --cov-report=xml:artifacts/coverage/coverage.xml -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=short --strict-markers --junitxml=artifacts/test/full/junit.xml --json-report --json-report-file=artifacts/test/full/results.json --html=artifacts/test/full/report.html --self-contained-html
    ```
  - Task: `test:full`
  - Evidence: JUnit, HTML, JSON, coverage

### E. Targeted & Failed
- [ ] Targeted path/markers run
  - Command:
    ```powershell
    pytest tests/<path> -v -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=short -m '<markers>' --junitxml=artifacts/test/targeted/junit.xml --json-report --json-report-file=artifacts/test/targeted/results.json --html=artifacts/test/targeted/report.html --self-contained-html
    ```
  - Task: `test:targeted`
- [ ] Re-run last failed tests
  - Command:
    ```powershell
    pytest --lf -v -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=long --maxfail=1 --junitxml=artifacts/test/failed/junit.xml --json-report --json-report-file=artifacts/test/failed/results.json --html=artifacts/test/failed/report.html --self-contained-html
    ```
  - Task: `test:failed`

### F. Watch Mode (TDD)
- [ ] Start pytest watch in background
  - Command:
    ```powershell
    ptw tests/ -- -v -p no:sugar -p no:timer --benchmark-skip --tb=short --color=yes
    ```
  - Task: `test:watch` (background)

Owner: `@git-flow-manager` | Evidence: `artifacts/test/*` | Due: rolling

---

## 3) Markers & Scoping

- [ ] Ensure consistent marker usage
  - `unit` → Smoke lane
  - `slow` → Excluded in smoke; allowed in coverage/full lanes
  - `integration`, `system`, `e2e` → Coverage/full lanes
  - `quality_gate` → Use in CI-enforced tests
- [ ] Verify strict markers in `test:full` to prevent leakage

Owner: `@test-engineer` | Evidence: pytest logs | Due: rolling

---

## 4) Coverage Targets (Pragmatic)

- [ ] Unit ≥ 70% (target ≥ 80%)
- [ ] Integration ≥ 40%
- [ ] System ≥ 25%
- [ ] Logging path coverage ≥ 90%
- [ ] Review coverage HTML: `artifacts/coverage/html/index.html`

Owner: `@software-quality-engineer` | Evidence: coverage JSON/XML/HTML | Due: sprint end

---

## 5) Quality Gate Sequence (Pre‑merge)

- [ ] Format (ruff)
  - Command:
    ```powershell
    ruff format .
    ```
- [ ] Lint (ruff)
  - Command:
    ```powershell
    ruff check .
    ```
- [ ] Type (mypy strict)
  - Command:
    ```powershell
    mypy src/ --strict --html-report=artifacts/quality/mypy-html --json-report artifacts/quality/mypy.json
    ```
- [ ] Smoke tests (unit, not slow)
  - Command:
    ```powershell
    pytest tests/ -m 'unit and not slow' --maxfail=5 -p no:sugar -p no:timer --benchmark-skip --show-progress --color=yes --tb=short
    ```
- [ ] Optional: Coverage threshold check in CI

Task: `quality:gate` (runs format → lint → type → smoke)

Owner: `@devops-platform-engineer` | Evidence: artifacts/quality/* + artifacts/test/smoke/* | Due: per PR

---

## 6) Evidence & Logging

- [ ] Ensure each lane writes JUnit, JSON, and HTML where applicable
- [ ] Store coverage artifacts (HTML, JSON, XML)
- [ ] Link reports in PR description when relevant
- [ ] Redact sensitive data in logs

Owner: `@software-quality-engineer` | Evidence: artifacts/* | Due: per run

---

## 7) CI/CD Alignment

- [ ] Map lanes to CI jobs (blocking vs advisory)
  - Blocking: format, lint, type, smoke
  - Advisory: coverage publish, performance (benchmark skip by default)
- [ ] Publish coverage HTML and test reports as CI artifacts
- [ ] Enforce strict markers on full suite in CI

Owner: `@devops-platform-engineer` | Evidence: CI logs & artifacts | Due: pipeline updates

---

## 8) Advanced Tracking (Ownership & Status)

Use the table below to track execution across lanes per sprint or PR.

| Lane          | Owner                         | Status     | Start (UTC)        | End (UTC)          | Artifacts Link                              | Notes |
|---------------|-------------------------------|------------|--------------------|--------------------|---------------------------------------------|-------|
| quick         | @test-engineer                | ☐ ☐ ☐      |                    |                    | artifacts/test/quick/                       |       |
| smoke         | @test-engineer                | ☐ ☐ ☐      |                    |                    | artifacts/test/smoke/report.html            |       |
| coverage      | @software-quality-engineer    | ☐ ☐ ☐      |                    |                    | artifacts/coverage/html/index.html          |       |
| full          | @software-quality-engineer    | ☐ ☐ ☐      |                    |                    | artifacts/test/full/report.html             |       |
| targeted      | @test-engineer                | ☐ ☐ ☐      |                    |                    | artifacts/test/targeted/report.html         |       |
| failed        | @test-engineer                | ☐ ☐ ☐      |                    |                    | artifacts/test/failed/report.html           |       |
| watch (TDD)   | @engineering-team             | ☐ ☐ ☐      |                    |                    | N/A                                         |       |

Legend: ☐ planned | ☐ running | ☐ complete

---

## 9) Immediate Next Steps

- [ ] Cross‑check tasks: confirm all lanes available in `.vscode/tasks.json`
- [ ] Execute `test:smoke` for fast feedback
- [ ] Review artifacts; capture issues and open tickets if needed
- [ ] (Optional) Run `test:coverage` to refresh coverage dashboards

Owner: `@git-flow-manager` | Evidence: artifacts/test/smoke/* | Due: today

---

## 10) Audit Checklist (Closeout)

- [ ] All lanes executed at least once this sprint
- [ ] Coverage targets met or documented exceptions
- [ ] CI gates green for last PR
- [ ] Reports linked in PR or AAR
- [ ] Lessons learned captured (AAR)

Owner: `@engineering-team-lead` | Evidence: CI + AAR docs | Due: sprint review
