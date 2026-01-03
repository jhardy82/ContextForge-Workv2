# Local-Only Logging Decision (No Cloud Components)

Date: 2025-08-13

Decision: Operate without any cloud logging components. Retain JSONL-first local logging and optionally mirror to Windows Event Log (disabled by default).

How to initialize
- Run: build/Initialize-LocalLogging.ps1 (reads config/logging.local.json)
- Effect: Sets CF_NO_CLOUD=1, applies Event Log options, writes a structured event logging_config_applied

Quick usage
- Initialize (per session):
  - PowerShell 5.1
    & "build/Initialize-LocalLogging.ps1" -Verbose
- Emit a heartbeat from scripts using Write-Heartbeat in build/Logging-Common.ps1
- Summarize logs locally:
  & "build/Summarize-StructuredLogs.ps1" -Days 2 -Verbose

Notes
- Windows Event Log mirroring is local-only and remains off unless enabled in config
- Azure Monitor forwarder scaffold remains present but unused; CF_NO_CLOUD=1 enforces policy
- JSONL files stored under logs/runtime with daily rotation by filename
