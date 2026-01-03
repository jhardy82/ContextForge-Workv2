# WU Scan Source & Co‑Management Analysis – Full Context (Default Prompt Template Optimized for GPT‑5)

Version: 2025‑08‑12.3
Author: [Your Name or Team]
Model Target: GitHub Copilot Agent (GPT‑5, Agent Mode) – No access to ChatGPT; all required context embedded here
Primary References: Microsoft Learn documentation (use as primary authoritative source), embedded workspace and design context.

---

## Objective

Enhance and validate `Get-WUScanSource.ps1` so that it:

1. Detects Windows Update scan source and co‑management workload configuration on local endpoints.
2. Merges with Configuration Manager–sourced expectations when run in an admin/console context.
3. Outputs human‑readable summaries with clear rationale and exact policy sources.
4. Generates machine‑readable evidence bundles.
5. Passes all workspace quality gates.

---

## Scope

In scope:

- PowerShell 5.1 execution.
- Local detection using registry, PolicyManager CSP keys, COM APIs, GPO application, CCM logs.
- Co‑management workload flag detection and decoding.
- Evidence bundle generation to `C:\temp` or provided path.
- Optional CM module enrichment.
- Integration with `/tests/` and `/build/Run-WUScanSourceTests.ps1`.

Out of scope:

- Live SCCM/Intune connections during test runs.
- Remote collection unless explicitly enabled.

---

## Embedded Context – Design & Requirements

Environment Scope:

- Windows 10 (1607+ LTSC) and Windows 11 (21H2+), covering WSUS, WUfB, and hybrid scan source per KB5005101.

Co‑Management Overview:

- Workloads: Compliance, Device configuration, Endpoint Protection, Resource access,
 Client apps, Office C2R apps, Windows Update policies.
- Workload states: ConfigMgr → Pilot → Intune.
- If WU Policies workload is Intune: expect cloud WU client policies; if ConfigMgr:
 expect WSUS/SUP.

Key Data Sources:

- Registry: `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate` (+`AU`), `HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Update`.
- COM: `Microsoft.Update.ServiceManager`, `Microsoft.Update.AutoUpdate`.
- Logs: `CoManagementHandler.log`, `WUAHandler.log`.
- GPO: WSUS, AU, DualScan, DoNotConnect, MU/Drivers.

Outputs Required:

- JSON, CSV, Markdown, TXT, `.reg`.
- TL;DR summary with exact policy sources.
- Evidence naming: `C:\temp\Evidence\<Computer>_<yyyyMMdd_HHmmss>`.

Conflict Types & Severity:

- A: Expected WSUS, Actual WU; B: Both WSUS and CSP without precedence; C: WSUS enforced but invalid URL.
- Critical / High / Medium / Low with plain-language impact.

Testing & Quality Gates:

- Mocks in `/tests/mocks/`; 4 WU-specific Pester tests.
- Run tests via `/build/Run-WUScanSourceTests.ps1`.
- PSSA with `/build/PSSA.Settings.psd1` (zero warnings, PS5.1 compliant).

---

## Process Rules

1. Follow default prompt template structure and maintain idempotence.
2. Only enhance logic where tests exist or will be added.
3. Generate all evidence formats in required structure.
4. Mark assumptions in code comments.
5. Use Microsoft Learn as primary source for all authoritative behaviors.

---

## Definition of Done

- All Pester tests pass.
- PSSA passes with zero warnings.
- Evidence bundles validated against `/tests/SCCM.Get-WUScanSource.Evidence.Tests.ps1`.
- TL;DR summaries meet explanation standards.
- CM enrichment works when module is present, skips gracefully otherwise.
- AAR entries created in `/AAR/`.

---

## AAR Integration

- Format: Markdown + JSONL.
- Store in `/AAR/`.
- Fields: date, change description, rationale, impacted files, test coverage changes, follow‑up actions.
- Feed lessons learned into conflict taxonomy, tests, and documentation.

---

## References

- Windows Update scan source policy – https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus
- WSUS GPO settings – https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates
- Policy CSP – Update – https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update
- ConfigMgr co‑management workloads – https://learn.microsoft.com/en-us/intune/configmgr/comanage/workloads
- ConfigMgr module reference – https://learn.microsoft.com/en-us/powershell/module/configurationmanager/
