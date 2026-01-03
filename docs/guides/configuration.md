# Configuration Guide

This guide explains how to configure the workspace for local development with PowerShell 5.1.

- Logging: see `config/logging.local.json` used by `build/Initialize-LocalLogging.ps1`.
- Environments: PSD1 files in `config/environments/` (dev/test/prod) hold parameter defaults.
- Settings: put non-secret defaults in `config/settings/`.

Notes
- Do not store secrets in repo. Use SecretManagement in PowerShell.
- Prefer Write-Progress for long operations and JSONL logs under `logs/`.

---

## Configuration Guide (ContextForge + PowerShell 5.1)

This guide shows how to configure environments, logging, and settings for local development and CI using Windows PowerShell 5.1.

### Environments (PSD1)
- Location: `config/environments/` containing `dev.psd1`, `test.psd1`, `prod.psd1`.
- Recommended keys:
  - `Name` (string): Environment name
  - `LoggingRoot` (string): Path for logs (default: `logs`)
  - `ArtifactsRoot` (string): Path for quality outputs (default: `build/artifacts`)
  - `FeatureFlags` (hashtable): Toggle optional behaviors
  - `SettingsPath` (string): Path to additional settings (default: `config/settings`)

Example `test.psd1`:

```powershell
@{
  Name = 'test'
  LoggingRoot = 'logs'
  ArtifactsRoot = 'build/artifacts'
  FeatureFlags = @{ EnableCache = $true }
  SettingsPath = 'config/settings'
}
```

Load in scripts:

```powershell
$envName = $env:APP_ENVIRONMENT
if (-not $envName) { $envName = 'test' }
$envPath = Join-Path $PSScriptRoot ("..\..\config\environments\$envName.psd1")
$EnvConfig = Import-PowerShellDataFile -Path $envPath
```

### Logging configuration
- File: `config/logging.local.json` used by `build/Initialize-LocalLogging.ps1` to bootstrap local-only logging.
- Suggested structure:

```json
{
  "log_root": "logs",
  "level": "INFO",
  "formats": ["jsonl"],
  "rotate_max_mb": 20,
  "rotate_backups": 5
}
```

- Outputs: JSONL files under `logs/` and metadata under `build/Outputs/` when quality tasks run.
- Customize by editing the JSON file and re-running the VS Code task “Logging: Initialize (Generic)”.

### Settings
- Location: `config/settings/` for non-secret defaults per module/feature.
- Example `config/settings/wuscan.json`:

```json
{ "scan_timeout_seconds": 60, "retry_max": 3 }
```

Consume in scripts:

```powershell
$settingsPath = Join-Path $PSScriptRoot '..\..\config\settings\wuscan.json'
if (Test-Path $settingsPath) { $WUSettings = Get-Content -Raw -Path $settingsPath | ConvertFrom-Json }
```

### Secrets (SecretManagement)
- Do not store secrets in the repository.
- Use Microsoft.PowerShell.SecretManagement to retrieve credentials at runtime.
- Reference: https://learn.microsoft.com/powershell/module/microsoft.powershell.secretmanagement/

Pattern:

```powershell
try {
  $token = Get-Secret -Name 'GraphToken' -AsPlainText
} catch {
  Write-Warning 'Secret GraphToken not available. Using mock flow.'
}
```

### Initialization flow
1) Initialize logging: run the VS Code task “Logging: Initialize (Generic)”.

2) Optional: Update context cache: run “MPV: Update Context Cache”.

3) Validate quality:
   - Static: “Quality: PSSA (Incremental)”
   - Tests: “Quality: Pester (Incremental)” or “Quality: Run Pester (Generic Path)”

### Validation and troubleshooting
- Check `logs/` for JSONL entries; summarize via task “Logging: Summarize (Generic)”.

- See `build/artifacts/` for NUnit XML and console outputs from Pester.

- If progress bars are missing, review `$ProgressPreference` (about_Preference_Variables) and ensure long operations use Write-Progress.

- For more, see `docs/guides/troubleshooting.md`.

### Versioning and promotion
- Keep PSD1s small; changes flow dev → test → prod via PRs.
- Checklist:
  - Update PSD1 keys and defaults as needed.
  - Validate with PSSA (ErrorsOnly) on changed files.
  - Run targeted Pester tests for affected components.
  - Update `CHANGELOG.md` and, if necessary, add AAR notes mapping to the error taxonomy.

### References
- SecretManagement: https://learn.microsoft.com/powershell/module/microsoft.powershell.secretmanagement/
- about_Preference_Variables: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_preference_variables
- Pester quick start: https://pester.dev/docs/quick-start
- PSScriptAnalyzer overview: https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/overview
