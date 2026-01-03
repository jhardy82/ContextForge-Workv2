# Troubleshooting Guide

Common areas to check:
- PowerShell 5.1 execution policy: run `build/Ensure-ExecutionPolicy.ps1`.
- Missing modules: validate with PSScriptAnalyzer and Pester tasks under `build/`.
- Logging not initialized: run the VS Code task "Logging: Initialize (Generic)".

If a build/test fails, check:
- `logs/` JSONL for errors
- `build/Outputs/` for last quality run artifacts
- Known error classes in `.github/error-classification/error-taxonomy.yaml`

---

## Troubleshooting Guide (ContextForge + PowerShell 5.1)

Use this guide to diagnose common issues in local runs and CI.

### Quick diagnostics checklist
- Execution policy: ensure scripts can run. If blocked, execute `build/Ensure-ExecutionPolicy.ps1`.
- PowerShell version: confirm Windows PowerShell 5.1 for repository scripts.
- Module availability: verify Pester and PSScriptAnalyzer are installed and loadable.
- Paths: run from the repository root so relative paths (build/, tests/, logs/) resolve.
- Permissions: ensure write access to `logs/` and `build/artifacts/`.

### Evidence locations
- JSONL runtime logs: `logs/`
- Pester artifacts: `build/artifacts/` (NUnit XML, console text, run metadata)
- PSScriptAnalyzer results: `build/artifacts/` with RunId prefix
- Quality summaries: available via tasks under the “Quality” group

### Common failures and fixes
- PSSA findings block build:
  - Run “Quality: PSSA (Incremental)” to focus on changed files.
  - Review findings and fix according to rule descriptions.
- Failing Pester tests:
  - Re-run the suite using “Quality: Run Pester (Generic Path)” targeting the failing folder.
  - Check `tests/fixtures/` usage and mocks; replace brittle time-dependent logic with fixed timestamps.
- Progress bar not visible:
  - Ensure `Write-Progress` is called for operations over 3 seconds.
  - Check `$ProgressPreference` (see about_Preference_Variables).
- Logging missing:
  - Run “Logging: Initialize (Generic)” to set up local logging.
  - Verify `config/logging.local.json` exists and is valid JSON.

### Interpreting PSSA/Pester outputs
- Pester NUnit XML: shows test names, durations, and failures; cross-reference console output for stack traces.
- PSSA output: categorize by rule severity; prioritize errors over warnings for gate passes.
- Incremental modes:
  - Use “Quality: PSSA (Incremental)” and “Quality: Pester (Incremental)” during active development to shorten feedback loops.

### Taxonomy mapping and AAR
- Map observed failures to taxonomy classes in `.github/error-classification/error-taxonomy.yaml`.
  - Examples: `developmental.syntax_error` (PSSA parsing), `fractal.contract_violation` (API shape mismatches), `pentagon.performance_degradation` (perf test regression).
- Tag AARs using `lessons_mapping` to `_system/config/LessonsTaxonomy.yaml`.
- Include environment, RunId, failing file(s), and reproduction steps in the AAR.

### When to escalate
- Repeated failures across runs or environments.
- Security or data loss risks.
- Involves external dependencies not mockable locally.
Provide RunId, relevant log excerpts, failing commands, and environment PSD1 used.

### Task and script references
- Quality: View Latest (Top 1)
- Quality: PSSA (Generic), Quality: PSSA (Incremental)
- Quality: Run Pester (Generic Path), Quality: Pester (Incremental)
- Quality: Generic Chain
- Logging: Initialize (Generic), Logging: Summarize (Generic)
- MPV: Status, MPV: Trends, MPV: Quick Test

### References
- Write-Progress: https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/write-progress
- about_Preference_Variables: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_preference_variables
- Pester docs: https://pester.dev/docs/quick-start
- PSScriptAnalyzer overview: https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/overview
