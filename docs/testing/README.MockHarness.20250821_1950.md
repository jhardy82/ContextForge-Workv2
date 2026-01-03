# Mock SCCM Harness (Unique Scaffold 20250821_1950)

## Quick Start

```powershell
# Start stack
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build\Start-MockStack.20250821_1950.ps1
# Run PSScriptAnalyzer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build\Invoke-PSSA.20250821_1950.ps1 -EnableExitOnErrors
# Run smoke tests
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build\Run-Pester.20250821_1950.ps1 -EnableExitOnFail
# Stop stack
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build\Stop-MockStack.20250821_1950.ps1
# All-in-one
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build\Run-All.20250821_1950.ps1 -ExitOnFail
```

## Toolchain Notes
- PowerShell 5.1 required for operational harness scripts (# HostPolicy: LegacyPS51)
- Uses PSScriptAnalyzer & Pester (installed on demand if missing)
- Logs emitted to `./logs` in JSONL style with minimal event set

## Consolidation Plan
After validation (triple‑check passes) these unique files will be merged into generic names (e.g., `Start-MockStack.ps1`). Decision & evidence logged in tracker `BuildHarness-S1`.
