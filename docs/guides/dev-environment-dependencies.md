---
created: 2025-08-14
author: SCCM-InfraEval-Agent
version: 1.0.0
purpose: Modern development environment dependencies and setup (PS 5.1 prod compatibility, PS 7 dev tooling)
---

# Modern Development Environment Dependencies

This guide documents external dependencies (modules, CLIs, extensions) to create a fast, reliable development environment while keeping production scripts compatible with Windows PowerShell 5.1.

- Production target: Windows PowerShell 5.1 (compatibility baseline)
- Development shell: PowerShell 7.4.x (side-by-side) for tooling, speed, and newer SDKs

## Modernization options (choose-your-path)

Below are explicit modernization options with trade-offs. Note: Bundling/selection is handled by the ChatGPT orchestrator; this document enumerates options only.

- Option A: Side-by-side PowerShell 7 for tooling
  - Summary: Keep PS 5.1 for production execution; use PS 7.4 for tests, analyzers, CLI SDKs.
  - Tools: PowerShell 7.4, Pester, PSScriptAnalyzer.
  - Effort: Low; immediate benefit.
  - Risk: Low; no production runtime change.
  - PS 5.1 impact: None; compatibility preserved.

- Option B: Editor and extensions uplift
  - Summary: Standardize VS Code + core extensions for consistent authoring and review.
  - Tools: PowerShell extension, Pester Test Explorer, Markdownlint, YAML, GitLens, EditorConfig.
  - Effort: Low.
  - Risk: Low.
  - PS 5.1 impact: None.

- Option C: Quality gate hardening
  - Summary: Enforce Pester and PSScriptAnalyzer in local tasks and CI; incremental runs for speed.
  - Tools: Pester, PSScriptAnalyzer, existing build scripts.
  - Effort: Low–Medium (wiring + pinning).
  - Risk: Low; catches regressions earlier.
  - PS 5.1 impact: None; tests still validate 5.1.

- Option D: Dev-only Python orchestration
  - Summary: Use Python (via PDM) for log processing, JSONL/SQLite reporting, and tooling.
  - Tools: Python 3.11+, PDM, tqdm, python-dotenv, orjson, sqlite-utils, pandas (optional).
  - Effort: Medium (env bootstrapping + scripts).
  - Risk: Low–Medium (new stack for dev only).
  - PS 5.1 impact: None; scripts remain PowerShell.

- Option E: CLI utilities for logs and packaging
  - Summary: Add jq, sqlite3, 7z for faster inspection and packaging flows.
  - Tools: jq, SQLite CLI, 7-Zip CLI.
  - Effort: Low.
  - Risk: Low.
  - PS 5.1 impact: None.

- Option F: Cloud SDK channel (dev-only)
  - Summary: Use Az modules/CLI and Microsoft Graph SDK on PS 7 for cloud tasks.
  - Tools: Az.Accounts (+ targeted Az modules), Microsoft Graph PowerShell SDK v2, Azure CLI.
  - Effort: Medium (auth patterns, pinning).
  - Risk: Medium (SDK churn), keep isolated to PS 7.
  - PS 5.1 impact: None to low (don’t require SDKs under 5.1).

- Option G: Concurrency helpers
  - Summary: For PS 5.1, add PoshRSJob selectively; PS 7 uses ThreadJob.
  - Tools: PoshRSJob (5.1), built-in ThreadJob (7.x).
  - Effort: Low–Medium (guard code paths).
  - Risk: Medium (concurrency complexity).
  - PS 5.1 impact: None if guarded.

- Option H: Dev containers or WSL2 (advanced)
  - Summary: Use VS Code Dev Containers or WSL2 for isolated dev; keep outputs PS 5.1-compatible.
  - Tools: VS Code Dev Containers, Docker Desktop, WSL2.
  - Effort: Medium–High (container definitions, onboarding).
  - Risk: Medium (environment drift vs prod), good for consistency.
  - PS 5.1 impact: None to low (validate outputs on 5.1).

- Option I: Git hooks and pre-commit checks
  - Summary: Enforce lint/tests pre-commit; speed via incremental runs and caching.
  - Tools: Existing pre-commit scripts, Pester/PSSA, EditorConfig.
  - Effort: Low.
  - Risk: Low.
  - PS 5.1 impact: None.

- Option J: Observability uplift (optional)
  - Summary: Keep JSONL + SQLite; optionally forward summaries to Seq or Azure Monitor from CI.
  - Tools: JSONL/SQLite (current), optional connectors.
  - Effort: Medium.
  - Risk: Medium (external services/governance).
  - PS 5.1 impact: None.

## Profiles
- Production (PS 5.1): Execute SCCM/enterprise automation scripts. Validate all cmdlets on PS 5.1.
- Development (PS 7.4): Run tests, analyzers, Graph/Azure SDKs, background watchers, and heavy tooling.

## Must-have: PowerShell foundations
- PowerShell 7.4.x (side-by-side with Windows PowerShell 5.1)
- PSReadLine 2.3+ (install for both shells for consistent editing)
- Pester 5.7.x (tests, coverage)
- PSScriptAnalyzer 1.24.x (static analysis with repo settings)
- Microsoft.PowerShell.SecretManagement + SecretStore (secure local secrets)
- powershell-yaml (YAML IO for handoff/config files)
- PlatyPS (generate/update Markdown help)

## Recommended: Dev productivity
- jq (JSON/JSONL slicing in terminal)
- SQLite CLI (sqlite3.exe) to inspect SQLite fallback logs
- 7-Zip CLI (7z.exe) for packaging and SFX operations
- Azure CLI (az) if you script against Azure
- Az PowerShell modules (pin versions; prefer using in PS 7)
- Microsoft Graph PowerShell SDK v2 (prefer PS 7)
- PoshRSJob (if you need parallelism on PS 5.1); PS 7 has ThreadJob built-in

## Agent-centric enablement (solo human + multi-agent team)

Focus: headless-by-default, secure credentials, consistent logs, and protocol-friendly integration for agents like GitHub Copilot, Gemini CLI, Blackbox, and future agents.

- Shell/runtime
  - Prefer PS 7.4 for agent-run tasks (faster startup, better .NET) while keeping PS 5.1 for prod script validation.
  - Background watchers and detached runs use PS 7 where feasible.

- Protocols and integration
  - Standardize on non-interactive task surfaces (-WhatIf, -Verbose, -Force, -NonInteractive) across scripts.
  - Optional: Model Context Protocol (MCP) readiness to enable agent plug-ins via a common protocol (Node/Python servers).
  - Use JSON/JSONL as primary agent IO; keep CSV/Markdown for summaries.

- Tooling for agents
  - GitHub CLI (gh) for repo ops, PRs, and issue workflows.
  - ripgrep (rg) for fast codebase search that agents can leverage.
  - jq for JSON/JSONL slicing; sqlite3 for log DB inspection.
  - SecretManagement + SecretStore to avoid plain-text API keys; support env-var fallbacks for CI.

- Logging and evidence
  - Continue JSONL + SQLite dual-write; maintain stable schemas and timestamps.
  - Keep logs under `logs/` with per-run metadata; agents can emit `Communication-to-ChatGPT.yaml` and AARs.

- Security
  - Use least-privilege tokens; store locally via SecretStore, pass to agents via environment injection.
  - Avoid writing tokens to transcripts; redact before persistence.

## ChatGPT usage: prompt authoring and data analysis

Use ChatGPT for context-rich prompt drafting and for summarizing or classifying logs and artifacts, while preserving security and reproducibility.

- Prompt authoring best practices
  - State goal, constraints (PS 5.1 prod, PS 7 dev), and desired output schema up front.
  - Provide minimal, relevant context: file paths, snippets, and artifacts rather than entire files when possible.
  - Ask for structured outputs (JSON/CSV/markdown) with explicit keys and examples.
  - Include edge cases and acceptance checks (e.g., Pester/PSSA green, non-interactive).

- Data analysis via ChatGPT
  - Summarize Pester/PSSA results by feeding artifact paths and brief excerpts; request a JSON summary with pass/fail counts and recommendations.
  - For large logs, chunk inputs and request per-chunk JSON; merge locally.
  - Emit `Communication-to-ChatGPT.yaml` and AAR summaries for traceability.

- Security and privacy
  - Redact secrets/PII before sharing. Store tokens in SecretStore and inject as env vars when calling CLIs/SDKs.
  - Prefer synthetic or sanitized samples for debugging.

- Tooling
  - Azure OpenAI or OpenAI CLI/SDK (optional) for scripted automation; prefer PS 7 for these tasks.
  - Manage keys with SecretManagement/SecretStore; avoid plain-text config.

- Minimal prompt scaffolds

```markdown
System: You are a senior PowerShell engineer. Production scripts must run on PS 5.1; dev tooling may use PS 7.

User:
Goal: Analyze test results and suggest fixes.
Context:
- Pester NUnit XML: build/artifacts/Pester-Results-NUnit-20250814_162614.xml
- PSSA Summary: build/artifacts/Quality-Summary-PSSA_INC_NOW.json
Constraints:
- No interactive prompts; PS 5.1 compatibility for production scripts.
Output:
- JSON with keys: { "issues": [], "recommendations": [], "next_steps": [] }
```

```markdown
System: You are a documentation assistant.

User:
Goal: Draft a modernization plan.
Context: See docs/guides/dev-environment-dependencies.md (sections: Options A–J).
Output: Markdown with a 3-phase rollout and a risk matrix table.
```

## Python (dev-only, orchestration)
- Python 3.11+
- PDM (package and venv manager)
- Packages: tqdm, python-dotenv, orjson, sqlite-utils, pandas (optional)

## VS Code extensions
- PowerShell (ms-vscode.powershell)
- Pester Test Explorer (pspester.pester-test)
- Markdownlint (DavidAnson.vscode-markdownlint)
- YAML (redhat.vscode-yaml)
- GitLens (eamodio.gitlens)
- EditorConfig (EditorConfig.EditorConfig)

## Compatibility guidance
- Keep PS 5.1 as the execution target for production scripts and SCCM tooling.
- Prefer PS 7 for Graph/Az SDKs and heavy CI tasks (avoid .NET binding issues on 5.1).
- Pin versions of Pester, PSScriptAnalyzer, and critical modules for reproducibility.

## Installation (Windows)

### PowerShell modules (run in Windows PowerShell 5.1 and again in PowerShell 7)

```powershell
# Optionally trust PSGallery first (admin shell recommended)
# Set-PSRepository -Name PSGallery -InstallationPolicy Trusted

Install-Module Pester -Scope CurrentUser -Force
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force
Install-Module Microsoft.PowerShell.SecretManagement -Scope CurrentUser -Force
Install-Module Microsoft.PowerShell.SecretStore -Scope CurrentUser -Force
Install-Module PlatyPS -Scope CurrentUser -Force
Install-Module powershell-yaml -Scope CurrentUser -Force
```

### CLI tools via Winget (optional)

```powershell
winget install --id Microsoft.PowerShell -e
winget install jqlang.jq
winget install 7zip.7zip
winget install SQLite.sqlite
winget install Microsoft.AzureCLI
```

### Python (dev only)

```powershell
# Install PDM (one-time)
py -3 -m pip install --user pdm
# Initialize env in repo root
pdm config python.use_venv true
pdm init  # interactive; or use pdm add directly if already set up
# Add packages
pdm add tqdm python-dotenv orjson sqlite-utils pandas
```

## Validation
- Pester: Run the quality and unit tests in PS 7 to validate the dev toolchain, then verify critical scripts also pass on PS 5.1.
- PSScriptAnalyzer: Ensure settings from the repo settings file apply and produce 0 findings on clean runs.
- Smoke checks: `Get-Module Pester,PSScriptAnalyzer,Microsoft.PowerShell.SecretManagement -ListAvailable` in both shells.

## 🖥️ CLI Usage
- Pester (folder scope):

```powershell
# PS 7 recommended for speed; PS 5.1 for prod parity
& .\build\Run-PesterTests.ps1 -Path .\tests\quality -EnableCache
```

- PSScriptAnalyzer (incremental):

```powershell
& .\build\Invoke-PSSA-Incremental.ps1 -Mode ErrorsOnly -EnableCache -RunId PSSA_INC_DEV
```

- Secrets (local store):

```powershell
Register-SecretVault -Name LocalSecretStore -ModuleName Microsoft.PowerShell.SecretStore -DefaultVault
```

- YAML IO (example):

```powershell
$obj = Get-Content .\config\settings.yaml | ConvertFrom-Yaml
```

- Python (dev orchestration):

```powershell
pdm run python scripts\validate_env.py
```

## ✅ Trust-but-Verify Checklist
- [ ] All functions have docstrings (for scripts, ensure comment-based help)
- [ ] Progress indicators implemented where operations >3s
- [ ] Error handling included with actionable guidance
- [ ] Tests written and passing (Pester + PSSA clean)
- [ ] CLI usage documented (above)
- [ ] Agent tooling installed (gh, jq, ripgrep, sqlite3) or equivalents
- [ ] Secrets stored via SecretManagement/SecretStore; no plain-text tokens

<!-- Bundling intentionally omitted; selection is handled by the ChatGPT orchestrator. -->

## Phased rollout

- Phase 1 (week 0–1)
  - Install PS 7.4, core VS Code extensions (A, B).
  - Pin Pester/PSScriptAnalyzer versions and verify tasks (C).

- Phase 2 (week 2–3)
  - Add jq/sqlite3/7z (E).
  - Introduce Python via PDM for dev-only orchestration (D).

- Phase 3 (week 4+)
  - Layer in cloud SDKs under PS 7 (F).
  - Optionally add Dev Containers/WSL2 (H) and pre-commit enforcement (I).
