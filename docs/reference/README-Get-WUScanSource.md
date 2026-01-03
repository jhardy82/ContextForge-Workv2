# Get-WUScanSource (PowerShell 5.1)

Purpose: Diagnose the Windows Update scan source and policy provenance (GPO/CSP/local), surface
conflicts mapped to Microsoft Learn guidance, and export an evidence bundle for auditing.

## Quick start

- Run (summary only):
  - `PowerShell -ExecutionPolicy Bypass -File .\SCCM\Get-WUScanSource.ps1 -SummaryOnly`
- Run (non-interactive full object):
  - `PowerShell -ExecutionPolicy Bypass -File .\SCCM\Get-WUScanSource.ps1 -NonInteractive`
- Export results and evidence:
  - `PowerShell -ExecutionPolicy Bypass -File .\SCCM\Get-WUScanSource.ps1 \`
     -ExportJson .\Outputs\scan.json \`
     -ExportCsv .\Outputs\scan.csv \`
     -ExportEvidenceDir .\Outputs\evidence \`
     -NonInteractive`
- One-click harness (recommended):
  - Use VS Code task: “Quality: Run WUScanSource Harness”

## Outputs

- scan.json: Full result object with LikelyScanSource, PolicyConfigured_* flags, conflicts, and Learn
  references.
- scan.csv: Tabular summary of key fields.
- evidence/ (bundle):
  - Summary.md/txt, gpresult output, registry exports, WindowsUpdate.log (optional), Windows Update
    Client events summary, WU services, Hashes.csv manifest.

## Evidence validator

- Harness runs build/Validate-WUScanEvidence.ps1 after export to ensure required files exist and are
  non-empty, and to verify scan.json/csv hashes against Hashes.csv when present.
- Validation result is logged to logs/WUScanSource/run_`<timestamp>` .jsonl with event type
  `evidence_validation`.

## Flags of interest

- Proxy/TLS: SetProxyBehaviorForUpdateDetection, DoNotEnforceEnterpriseTLSCertPinningForUpdateDetection
- PublicOnlineBlocked: DoNotConnectToWindowsUpdateInternetLocations
- UX lockouts: DisableWindowsUpdateAccess (ADMX_ICM), SetDisableUXWUAccess (CSP)
- Driver exclusion: ExcludeWUDriversInQualityUpdate
- MU service + WSUS: AllowMUUpdateService (possible conflicts under WSUS)

## Progress and logging

- Long-running operations display Write-Progress with ETA.
- Transcript written to C:\\temp (Harness); JSONL audit lines under logs/WUScanSource/.

## Compatibility

- PowerShell 5.1 only. Tested on Windows 10/11 Enterprise.

## Troubleshooting

- If evidence validation fails, check evidence/ for missing or empty files and ensure the Hashes.csv
  manifest includes scan.json and scan.csv entries.
- If COM calls fail, ensure Windows Update client components are intact; see WindowsUpdate.log and
  WU_Events_Summary.json under evidence/.
