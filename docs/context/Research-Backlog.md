# Research Backlog (PS 5.1-first, Modern Workplace Engineering)

Last updated: 2025-08-13
Maintainer: ContextForge.Core

## Prioritized topics

- [ ] 1) Telemetry and logging architecture (breadth and selection)
  - Scope: JSONL baseline vs Windows Event Log vs Azure Monitor (Logs Ingestion API), PSFramework fit, rotation/locking, retry/buffering
  - Outputs: Decision record, minimal PoCs (-EnableEventLog hook; PS7 DCR forwarder), runbook
  - Key sources: Microsoft Learn (Start-Transcript, Write-Information, Write-EventLog, Get-WinEvent, Logs Ingestion); PSFramework; AzLogDcrIngestPS

- [ ] 2) Windows Update scan source detection (WU/WUfB/WSUS)
  - Scope: Reliable detection heuristics in PS 5.1; WUA COM APIs; CIM/registry signals; PSWindowsUpdate behaviors; offline scenarios
  - Outputs: Validated detection matrix, test harness enhancements, edge-case mocks
  - Key sources: WUA documentation, PSWindowsUpdate docs, MVP posts on WUfB/WSUS

- [ ] 3) SCCM/MECM automation baselines (PS 5.1, console session)
  - Scope: Supported cmdlets (Get-CMBaseline, Get-CMDeviceCollection, etc.), safe assumptions when console is present, throttling/long runs
  - Outputs: Cmdlet availability matrix, patterns cookbook, mockable wrappers
  - Key sources: ConfigMgr PowerShell docs; Microsoft Learn

- [ ] 4) Microsoft Graph usage patterns for Intune/M365 (SDK v2)
  - Scope: Auth flows, scopes, throttling/backoff, pagination, batching, beta vs v1.0, SDK module selection and pinning
  - Outputs: Patterns guide, retry policy utilities, sample queries with unit tests
  - Key sources: Graph PowerShell SDK repo/docs; Learn rate-limiting guidance

- [ ] 5) Packaging and software distribution
  - Scope: IntuneWin32App module, Winget/WingetTools, Evergreen sourcing, version pinning, hash validation, content caching
  - Outputs: Packaging playbook, sample pipelines, security checks (hash/signature)
  - Key sources: IntuneWin32App repo; Evergreen docs; Winget/WinGet-CLI docs

- [ ] 6) Security hardening and secrets
  - Scope: Microsoft.PowerShell.SecretManagement, DPAPI/Windows Credential Manager, Key Vault integration, code signing/timestamping, transcript redaction
  - Outputs: Secrets policy, signing guide, sample vault adapters, AAR for security incidents
  - Key sources: SecretManagement docs; Authenticode; Learn security guidance

- [ ] 7) Error taxonomy and AAR generation
  - Scope: Standardize error categories/severity, enrich ErrorRecord, system state capture, auto-AAR triggers, recovery playbooks
  - Outputs: Error schema, helper functions, Pester tests for error flows
  - Key sources: PowerShell error handling best practices; internal methodology

- [ ] 8) Performance and scalability
  - Scope: Batching/streaming large datasets, Write-Progress with ETA, advisory locks, contention on shared logs, resource monitoring
  - Outputs: Perf patterns, lock helpers, micro-bench harness, metrics collection hooks
  - Key sources: .NET GC/memory notes; PS performance tips; methodology guidance

- [ ] 9) Quality enforcement pipeline
  - Scope: Pester 5.7.x patterns (mocks, TestDrive), PSScriptAnalyzer enterprise rules, pre-commit checks, VS Code tasks wiring for params
  - Outputs: Expanded tests, rule waivers policy, task improvements exposing -TargetPath/-ArtifactsDir
  - Key sources: Pester docs; PSSA rules; task runner docs

- [ ] 10) Module/version management in constrained environments
  - Scope: PowerShellGet v2 vs v3, internal repositories, offline caching, module pinning, deterministic builds
  - Outputs: Module sourcing policy, lockfile/manifest approach, offline bootstrap script
  - Key sources: PowerShellGet docs; NuGet provider guidance

- [ ] 11) Output schemas and compatibility
  - Scope: JSON/CSV schemas, metadata headers, schema versioning, backward compatibility, CSV column order
  - Outputs: Schema contracts, validators, converters; tests for compatibility
  - Key sources: Internal interface standards; tooling for validation

- [ ] 12) Documentation and help pipeline
  - Scope: PlatyPS for help generation, doc standards (markdownlint), CHANGELOG conventions, troubleshooting sections
  - Outputs: Automated help stubs, lint settings, doc CI hooks
  - Key sources: PlatyPS; markdownlint; Keep a Changelog

## Backlog candidates
- PS 7 bridge patterns library (wrapping PS 7-only features behind PS 5.1 ops)
- Proxy/offline operations strategy for Graph/Intune/WinGet
- Localization/internationalization readiness for user-facing outputs

## Working agreements
- Deliverables include citations, tests (where applicable), and a short AAR on notable findings
- Update evidence diary on each significant research milestone
- Prefer minimal, demonstrable PoCs for decisions with trade-offs
