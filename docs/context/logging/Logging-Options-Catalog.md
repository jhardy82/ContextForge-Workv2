# PowerShell Logging Options Catalog (PS 5.1–first)

Last refreshed: 2025-08-13
Refresh cadence: Quarterly, or on major module/service changes
Maintainer: ContextForge.Core

## Built-in/logging-adjacent primitives (Microsoft Learn)
- Transcripts — Start-Transcript / Stop-Transcript (session capture; text; host output)
  - Docs: https://learn.microsoft.com/powershell/module/microsoft.powershell.host/start-transcript
  - Pros: Zero deps, full session trace; easy opt-in per-run
  - Cons: Unstructured text; mixes input/output; large files; harder for analytics
- Information stream — Write-Information / $InformationPreference; Write-Host wrapper
  - Docs: https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/write-information
  - Pros: Structured-ish record with tags; capturable/redirection (6>)
  - Cons: Requires discipline; default hidden (SilentlyContinue); not JSON by default
- Windows Event Log — Write-EventLog (classic); Get-WinEvent for retrieval
  - Docs: https://learn.microsoft.com/powershell/module/microsoft.powershell.management/write-eventlog
  - Pros: Centralized Windows telemetry; severity, event IDs; SIEM connectors
  - Cons: Source registration friction; classic logs vs modern channels; admin rights often required
- ETW/Providers (via Get-WinEvent) — Advanced filtering (XPath/XML)
  - Docs: https://learn.microsoft.com/powershell/module/microsoft.powershell.diagnostics/get-winevent
  - Pros: High-fidelity OS/service events; scalable
  - Cons: Complex schema/filters; not a direct write path from PS 5.1 scripts

## Cloud ingestion (Azure Monitor)
- Azure Monitor Logs — Logs Ingestion API (Data Collection Rules)
  - Overview: https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview
  - Samples: https://learn.microsoft.com/azure/azure-monitor/logs/tutorial-logs-ingestion-code#sample-code
  - Pros: First-party; transformations; RBAC; multiple destinations
  - Cons: Requires PS 7+ in samples; setup (DCR/DCE) overhead; JSON shaping discipline
- Legacy HTTP Data Collector API (migrate off)
  - Migration: https://learn.microsoft.com/azure/azure-monitor/logs/custom-logs-migrate
  - Pros: Established pattern; many community samples
  - Cons: Legacy; fewer features vs Logs Ingestion API

## Community modules (shortlist)
- PSFramework
  - Repo: https://github.com/PowershellFrameworkCollective/psframework
  - Notes: Rich logging (Write-PSFMessage), configuration system, JSON targets, telemetry adapters
  - Pros: Mature, enterprise-friendly features, message levels, structured context
  - Cons: Learning curve; dependency surface
- Polaris.Logging or Serilog-based integrations (via PS7)
  - Serilog: https://serilog.net/ (PS 7.x ecosystems often rely on .NET logging)
  - Pros: Powerful sinks (files, seq, ELK, Azure)
  - Cons: Typically PS 7+; introduces .NET deps
- PoshRSJob + custom JSONL
  - Pattern: Offload logging to background jobs writing JSONL with file rotation
  - Pros: Stays PS 5.1 compatible; simple; aligns with our JSONL-first
  - Cons: DIY responsibility for rotation/retry/locking
- AzLogDcrIngestPS (community helper for Logs Ingestion API)
  - Repo: https://github.com/KnudsenMorten/AzLogDcrIngestPS
  - Notes: Automates DCR ingestion; complements Azure Monitor path

## Selection criteria (our context)
- Compatibility: Windows PowerShell 5.1 first for operational/SCCM
- Structure: JSON/JSONL as primary for machine analytics; CSV summaries
- Reliability: Resilient to network issues (local buffering, retry)
- Integrations: Windows Event Log optional, Azure Monitor optional/upgrade path
- Complexity: Prefer lightweight; avoid heavy dependencies unless justified

## Recommended options (tiered)
- Tier 0 (Baseline, PS 5.1-native):
  - JSONL-first file logging (our existing build/Logging-Common.ps1 patterns)
  - Transcripts for full-session capture on demand
  - Information stream for user-facing progress/context (opt-in redirection)
- Tier 1 (Windows-native centralization):
  - Optional Write-EventLog for critical events with event IDs (requires source setup/admin)
- Tier 2 (Cloud analytics):
  - Azure Monitor Logs Ingestion API via queued JSONL → PS7 bridge job or AzLogDcrIngestPS

## Comparison snapshot
- JSONL (local)
  - Pros: Simple, portable, minimal deps, aligns with repo; easy to parse and batch ship
  - Cons: Needs rotation and locking strategy; local disk reliance
- Windows Event Log
  - Pros: Central visibility; standard tooling; alerting via Event Viewer/SIEM
  - Cons: Source registration/admin rights; schema rigidity; classic vs modern
- Azure Monitor Logs
  - Pros: Query (KQL), retention, analytics, dashboards, alerting; transformations
  - Cons: Infra setup; PS7 likely; costs; network dependency
- PSFramework
  - Pros: Rich, structured logging with levels, configuration, routing
  - Cons: Added dependency/learning; may be overkill for small scripts

## Implementation notes for this repo
- Keep PS 5.1 JSONL logging as the authoritative baseline (run_start/run_end/heartbeat).
- Add optional Windows Event Log hook for high-severity incidents (guarded by -EnableEventLog switch).
- Provide an optional PS7 companion sender to forward JSONL batches to Azure Monitor Log Ingestion API.
- Consider PSFramework for new tooling that benefits from standardized message levels and routing.

## Next steps
- Prototype: Add a thin module to route critical logs to Windows Event Log (opt-in).
- Prototype: PS7 forwarding script to DCR using AzLogDcrIngestPS or raw REST.
- Evaluate PSFramework fit for future modules; keep baseline dependency‑light for SCCM.
