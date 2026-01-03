# External Dependencies Modernization Plan — WUScanSource

Purpose
- Define, pin, and operationalize external dependencies for the WUScanSource effort.
- Ensure predictable, repeatable local runs and CI readiness with enterprise-friendly controls.

Scope
- PowerShell 5.1 modules for quality, docs, and optional UX.
- Python (dev/orchestration only) for automation, validation, and summarization.
- Installation, versioning, offline support, and integration into existing tasks.

Constraints and principles
- Primary runtime: Windows PowerShell 5.1; diagnostics must remain 5.1 compatible.
- Orchestrator and tooling may use Python; do not introduce Python into production scripts.
- Pin versions to known-good; prefer deterministic installs and offline mirrors.
- No plaintext secrets; use SecretManagement or environment variables.

Environments and compatibility
- Windows 10/11 with Windows PowerShell 5.1.
- Enterprise laptops with proxy and policy constraints.
- Optional: Admin elevation improves evidence coverage (gpresult), but not required to run.

Dependency inventory

PowerShell modules (required)
- Pester 5.7.x
  - Purpose: Unit/integration tests. Enforced already by build tasks.
  - Install: Install-Module Pester -RequiredVersion 5.7.0 -Scope CurrentUser -Force
  - Offline: Save-Module -Name Pester -RequiredVersion 5.7.0 -Path .\tools\psgallery
- PSScriptAnalyzer
  - Purpose: Static analysis with enterprise settings (build/Invoke-PSSA.ps1).
  - Install: Install-Module PSScriptAnalyzer -Scope CurrentUser -Force
  - Offline: Save-Module -Name PSScriptAnalyzer -Path .\tools\psgallery

PowerShell modules (optional)
- PSFramework — structured logging/helpers for advanced scenarios.
- ImportExcel — export human-friendly XLSX summaries (optional only).
- PlatyPS — generate/update markdown help if we modularize later.
- Microsoft.PowerShell.SecretManagement — secure secret storage when needed.
- ThreadJob — background jobs on 5.1 if concurrency is later required.

Python packages (dev/orchestration core)
- Typer — CLI framework.
- Rich — console UI and tables/panels.
- jsonschema — JSON schema validation of outputs.
- python-json-logger — structured logs.
- tenacity — robust retries/backoff.
- PyYAML — YAML in/out for handoffs.

Python packages (optional)
- pydantic — models and validation (nice-to-have).
- jinja2 — templated markdown/HTML reports.
- psutil — system metrics for diagnostics.
- orjson — faster JSON (fallback to stdlib if absent).
- SQLAlchemy — optional SQLite history store.
- textual — full TUI if needed.
- pyinstaller — single-file distributable if sharing orchestrator.

Versioning and pinning strategy
- PowerShell modules: pin Pester to 5.7.x via existing bootstrap; pin others to a vetted minor.
- Maintain a module pin list in config/dependencies/ps-modules.json (planned).
- Python: prefer pyproject.toml with locked versions; fallback to requirements.txt if needed.
- Keep pins stable; update only via deliberate, logged bumps.

Installation workflows

PowerShell (modules)
- Deterministic install
  - Online: Install-Module -Name MODULE_NAME -RequiredVersion VERSION -Scope CurrentUser -Force
  - Offline: Save-Module -Name MODULE_NAME -RequiredVersion VERSION -Path .\tools\psgallery;
    then Install-Module -Scope CurrentUser -Repository PSGallery -Name MODULE_NAME
    -RequiredVersion VERSION -SkipPublisherCheck -AllowClobber -Force
- Integrate into build/Bootstrap-Quality.ps1 to assert versions and exit on mismatch.

Python (orchestrator)
- Preferred: pyproject.toml with pinned versions; install via pip or pdm.
- Online: pip install -r requirements.txt (or) pip install . in the project with pyproject.
- Offline: build wheelhouse (pip download -d .\\tools\\wheelhouse -r requirements.txt);
   then pip install --no-index --find-links .\\tools\\wheelhouse -r requirements.txt.
- Keep CLI under cli/ with entry script (planned): cli/orchestrator.py.

Integration into tasks
- Add VS Code tasks (planned)
  - Orchestrator: Bootstrap Python (create venv, install pins).
  - Orchestrator: Run P1 + Validate (invoke existing PS batch + validator).
  - Orchestrator: Summarize Latest Run (Rich panel + write MD/YAML).
- Keep existing quality tasks as-is (Pester 5.7.x, PSScriptAnalyzer).

Security and compliance
- No plaintext secrets in source or logs.
- Use Microsoft.PowerShell.SecretManagement for any required secrets.
- Respect proxies and enterprise policies; honor -WhatIf/-Verbose where relevant.

Offline/air-gapped support
- Commit module and wheel manifests to tools/ with README on refresh steps.
- Provide Save-Module and pip download scripts in build/ to refresh caches.
- Validate installs against cached artifacts in CI/local before network fallback.

Quality gates
- Continue PSScriptAnalyzer with enterprise settings (build/Invoke-PSSA.ps1).
- Continue Pester tests (build/Run-PesterTests.ps1).
- Add jsonschema validation for ScanResult.json and Evidence manifest via orchestrator.

Rollout phases
- Phase 0 — This plan, pin lists skeleton, and doc cross-links.
- Phase 1 — PowerShell module bootstrap verification and optional pins for PSScriptAnalyzer.
- Phase 2 — Python orchestrator scaffolding with pinned core deps and minimal CLI.
- Phase 3 — Tasks wiring and schema validation; summaries exported to docs/.
- Phase 4 — Offline caches and periodic refresh scripts; optional packaging.

Risks and mitigations
- Network/proxy issues → use cached modules and wheelhouse; retries (tenacity).
- Version drift → explicit pins and bootstrap checks; scheduled pin reviews.
- Elevation-required steps (gpresult) → warn-only; document benefits.
- PS 5.1 syntax constraints → avoid newer syntax in production scripts.

References
- docs/Quality-Tooling-Guide.md
- docs/reference/Python-Installation-Guide-ContextForge.md
- .github/copilot-instructions.md (methodology and standards)
