# WU Scan Source & Co-Management Context (Agent Answers)

Generated: 2025-08-12T00:00:00Z
Author: GitHub Copilot Agent (context-only; no live SCCM access)

Notes
- Sources are Microsoft Learn/Docs unless marked Assumption.
- Windows PowerShell 5.1 target. Terminology reflects current Microsoft naming (Windows Update client policies = formerly WUfB).

---

## Environment & Scope

1) In-scope Windows versions (scan source logic)
- Windows 10 versions 1607+ through 22H2, incl. LTSC where applicable.
- Windows 11 21H2, 22H2, 23H2 and later.
- Rationale: Update Policy CSP applicability spans Win10 1507+ with most modern policies from 1607+; WSUS/WU behavior changes with KB5005101 (scan source policy) for Win10 2004+ and all Win11.
  - Policy CSP – Update (applicability tables). [link](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update)
  - Use Windows Update client policies and WSUS together (scan source policy; Win10 2004+/Win11). [link](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus)

2) Typical co-management configurations
- Paths: Existing ConfigMgr clients auto-enrolled to Intune; or Intune-enrolled devices with ConfigMgr client later. [overview](https://learn.microsoft.com/en-us/intune/configmgr/comanage/overview)
- Staging: Pilot collections per workload; sliders: Configuration Manager → Pilot Intune → Intune. [switch workloads](https://learn.microsoft.com/en-us/intune/configmgr/comanage/how-to-switch-workloads)
- Cloud attach wizard (2111+) for onboarding; pilot group concept used indefinitely if desired. [enable](https://learn.microsoft.com/en-us/intune/configmgr/comanage/how-to-enable)

3) Co-management workload sliders (focus: Windows Update policies)
- Supported workloads: Compliance, Windows Update policies, Resource access, Endpoint Protection, Device configuration, Office C2R apps, Client apps. [workloads](https://learn.microsoft.com/en-us/intune/configmgr/comanage/workloads)
- Windows Update policies slider: When moved to Intune, Win quality/feature updates are governed by Windows Update client policies; ConfigMgr software updates workflow should be disabled via client settings for those devices. [WU policies](https://learn.microsoft.com/en-us/intune/configmgr/comanage/workloads#windows-update-policies)

4) Co-management device collections
- Separate pilot collections per workload; distinct assignments via Staging tab. [switch workloads](https://learn.microsoft.com/en-us/intune/configmgr/comanage/how-to-switch-workloads#switch-workloads)
- Built-in “Co-management Eligible Devices” collection (2111+). [enable (2111+)](https://learn.microsoft.com/en-us/intune/configmgr/comanage/how-to-enable)

5) Win10 vs Win11 update policy handling differences
- Dual Scan: Deprecated/unsupported on Windows 11; on Win10 replaced by scan source policy and not recommended. [DisableDualScan + default scan behavior](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus#default-scan-behavior)
- Scan source policy (KB5005101): Introduces explicit per-update-class source selection on Win10 2004+ and all Win11. [wufb-wsus](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus)

---

## Policy & Configuration Sources

6) Authoritative sources for scan settings
- WSUS/GPO: “Specify intranet Microsoft update service location” and related WU policies. [WSUS client GPO](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates)
- Configuration Manager: SUP config + client local policy sets WSUS URL; avoid domain GPO overriding SUP. [ConfigMgr manage settings](https://learn.microsoft.com/en-us/intune/configmgr/sum/get-started/manage-settings-for-software-updates#group-policy-settings-for-software-updates)
- Intune/MDM: Update Policy CSP (scan source, deferrals, drivers, MU, etc.). [Policy CSP – Update](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update)
- Hybrid/co-managed: If WU policies workload is Intune, Windows Update client policies govern; ConfigMgr SU workflow disabled for those devices. [WU policies workload](https://learn.microsoft.com/en-us/intune/configmgr/comanage/workloads#windows-update-policies)

7) Relevant registry keys and WMI/COM
- WSUS/GPO:
  - HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate (WUServer, WUStatusServer, DoNotConnectToWindowsUpdateInternetLocations, DisableDualScan, ExcludeWUDriversFromQualityUpdates) and subkey AU (UseWUServer, AUOptions, ScheduledInstallDay/Time, DetectionFrequency).
  - Services registration: HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Services. [Azure UM reg refs](https://learn.microsoft.com/en-us/azure/update-manager/configure-wu-agent#wsus-configuration-settings)
- MDM CSP (device-applied values mirrored): HKLM\SOFTWARE\Microsoft\PolicyManager\default\Update and \current\device\Update for BranchReadinessLevel, Defer*, ExcludeWUDriversInQualityUpdate, etc. [configure WUfB summary](https://learn.microsoft.com/en-us/windows/deployment/update/waas-configure-wufb#summary-mdm-and-group-policy-settings-for-windows-10,-version-1703-and-later)
- WUA COM:
  - Microsoft.Update.AutoUpdate (IsManaged, Settings)
  - Microsoft.Update.ServiceManager (Services collection; known service IDs for WU/MU; WSUS as managed server). [How WU works + service IDs](https://learn.microsoft.com/en-us/windows/deployment/update/how-windows-update-works#scanning-updates)

8) Common GPOs applied
- Configure Automatic Updates; Automatic Updates detection frequency; Specify intranet Microsoft update service location; Do not connect to any Windows Update Internet locations; Do not include drivers with Windows Updates; Allow signed content from intranet Microsoft update service location; Remove access to use all Windows Update features. [WSUS GPO list](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates)

9) Standard CSPs for Windows Update client policies
- Manage updates offered from Windows Update: AllowMUUpdateService, ExcludeWUDriversInQualityUpdate, BranchReadinessLevel, DeferFeature/QualityUpdatesPeriodInDays, Pause*, TargetReleaseVersion, DisableWUfBSafeguards, etc.
- Manage updates offered from WSUS: UpdateServiceUrl; SetPolicyDrivenUpdateSourceForFeature/Quality/Driver/OtherUpdates; DetectionFrequency; SetProxyBehaviorForUpdateDetection. [Policy CSP – Update](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update)

10) Dual Scan implications
- Win10: If WSUS URL and deferral policies are both configured, device may scan WU unless dual scan disabled or scan source policy set. [wufb-wsus default behavior](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus#default-scan-behavior)
- Win11: Dual Scan policy no longer supported; use scan source policy to control sources. [wufb-wsus](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus)
- Enabling “Do not connect to any Windows Update Internet locations” removes “Check online…” option and enforces intranet-only. [GPO behavior](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates#do-not-connect-to-any-windows-update-internet-locations)

---

## Co‑Management Detection & Evidence

11) Local detection of co-management state
- Files/logs: %WinDir%\CCM\Logs\CoManagementHandler.log (capabilities, auto-enroll), WUAHandler.log (WUfB state). [troubleshoot co-management](https://learn.microsoft.com/en-us/troubleshoot/mem/intune/comanage-configmgr/troubleshoot-co-management-workloads#frequently-asked-questions)
- Registry: HKLM\SOFTWARE\Microsoft\CCM\CoManagementSettings (Assumption: capabilities/workloadFlags persisted here; actual key names vary by client version; verify in lab).
- WMI: CCM client namespace (Assumption: co-management settings exposed via root\ccm provider; confirm in lab).

12) Bitmask mapping for co-management capabilities (workloadFlags)
- Based on Microsoft sample log snippets:
  - 2 = Compliance policies (log references checking workload 2 for compliance)
  - 4 = Resource access policies
  - 16 = Windows Update policies (WUfB)
- Other common workloads (assumed mapping from field practice; verify in tenant):
  - 1 = Device configuration
  - 8 = Endpoint Protection
  - 32 = Office Click-to-Run apps
  - 64 = Client apps
- Source: log examples showing checks like “Verifying if workload 16 is enabled in workloadFlags …” in WUAHandler.log; mapping beyond 2/4/16 marked Assumption. [co-management logs](https://learn.microsoft.com/en-us/troubleshoot/mem/intune/comanage-configmgr/troubleshoot-co-management-workloads#frequently-asked-questions)

13) Evidence export structure (recommended)
- Files
  - CoManagementHandler.log (excerpt window around capability evaluation)
  - WUAHandler.log (WUfB state and workload flag checks)
  - Registry exports: HKLM\SOFTWARE\Microsoft\CCM\CoManagement*; HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate (and AU); HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Services; HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Update
  - Decoded workload mapping (JSON + CSV): integer flags → enabled workload names
- Manifest
  - EvidenceManifest.json with items[] entries (file, size, hash_algo="SHA-256", hash)
  - Hashes.csv (legacy)
- TL;DR
  - Summary.md: one-paragraph conclusion and key drivers for decision

14) Definition of mismatch (expected vs actual scan source)
- Expected source derives from authority:
  - If WU policies workload = Intune: expect Windows Update client policies (cloud) for feature/quality updates per scan source policy. [integration](https://learn.microsoft.com/en-us/intune/configmgr/sum/deploy-use/integrate-windows-update-for-business-windows-10)
  - If workload = ConfigMgr: expect WSUS/SUP as scan source.
- Mismatch examples
  - Workload slider → Intune but registry shows WUServer/UseWUServer forcing WSUS
  - Workload slider → ConfigMgr but CSP UpdateServiceUrl/SetPolicyDrivenUpdateSource* directing to WU
  - Conflicting GPO (“DoNotConnect…”) blocking WU when WU is expected

---

## Script Behavior & Output

15) Remote mode support?
- Recommendation: Prefer local evidence by default; optionally support remote collection via PowerShell Remoting/WMI where allowed. Many enterprises restrict remote COM/WU API calls; keep remote optional and read-only to avoid side-effects. Assumption.

16) Evidence bundle formats
- JSON: machine-readable results and manifest
- CSV: tabular summaries (e.g., services, mappings)
- Markdown: Summary.md TL;DR with key bullets
- TXT: raw tool outputs (e.g., gpresult)
- .reg: registry exports for reproducibility
- Aligns with multi-format guidance. [Policy CSP, WU docs]

17) TL;DR summary guidance
- Plain language: “This device is scanning against WSUS (GPO) while co-management slider expects Windows Update (Intune). Action: remove WSUS GPO or move workload back.”
- Include: detected authority, key signals (GPO/CSP/COM), risk (dual scan or unknown), next actions.

18) Conflict categorization (severity/type + actions)
- Severity
  - Critical: Blocking update source (e.g., DoNotConnect… enabled but WU required; invalid WSUS URL). [KB 80072EE6 cause](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/error-80072ee6-downlaod-wsus-update)
  - High: Workload/source mismatch; dual-scan risk on Win10; scan source not explicitly set on Win11 transition
  - Medium: Drivers/MU settings conflict with policy intent; store access removed unintentionally
  - Low: Cosmetic or fallback-only settings
- Types
  - Source mismatch; Policy collision (GPO vs CSP); Network/proxy; Registration/service drift
- Actions (plain language)
  - If moving to WU: disable WSUS GPOs, clear HKLM\…\WindowsUpdate WSUS values, set scan source policy, ensure internet endpoints allowed. [wufb-wsus](https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus) [autopatch-conflicts](https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/references/windows-autopatch-conflicting-configurations#resolving-conflicts)
  - If staying on WSUS: remove/avoid WUfB deferrals; consider DisableDualScan (Win10) or explicit WSUS scan source (Win10 2004+/Win11)

19) Map co-management workloads to detected WU config
- Output include
  - workloadFlags integer + decoded workloads
  - Effective scan source per class (Feature/Quality/Drivers/Other) from CSP scan source policy on Win10 2004+/Win11; else inferred from WSUS GPOs + WUA COM default
  - Authority decision: ConfigMgr vs Intune for Windows Update policies

---

## Testing & Validation

20) Recommended scenarios
- Normal
  - WSUS-only via GPO; WU-only via CSP; Co-managed with WU policies on Intune
- Conflict
  - WSUS GPO + Intune WU policies; DoNotConnect… enabled but WU expected; Dual-scan risk on Win10 with deferrals + WSUS URL
- Edge
  - Empty/invalid WSUS URL (80072EE6) [KB](https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/error-80072ee6-downlaod-wsus-update)
  - Drivers excluded via GPO/CSP with driver program enrollments [drivers](https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/manage/windows-autopatch-driver-and-firmware-update-programmatic-controls#policy-considerations-for-drivers)
  - MU opt-in state differences (Microsoft Update registration) [opt-in MU](https://learn.microsoft.com/en-us/windows/win32/wua_sdk/opt-in-to-microsoft-update#example)

21) Unit test coverage focus
- AUOptions/DetectionFrequency/ScheduledInstall* translations
- WSUS vs WU inference precedence on Win10 vs Win11 (scan source policy present/absent)
- Co-management workloadFlags decoding and authority mapping

22) Validating results (prod vs lab)
- Lab: deterministic mocks for registry, COM (WUA), gpresult, logs; assert inference and conflicts
- Prod: read-only evidence export; avoid changing service registrations; optional safe gpresult/reg query

23) Deterministic mocking recommendation
- Yes: mock registry (WindowsUpdate/PolicyManager), WUA COM state (IsManaged, Services), gpresult output, co-management bitmask
- Enables scenario replay and CI (Pester 5.x)

24) Existing mock data (from project)
- 20+ WU scenarios (Learn-backed) with translations and evidence validation; ValueTranslation tests; Evidence bundle tests with SHA-256 manifest items[]. Assumption based on repository summary.

25) Missing mock data (valuable additions)
- Invalid WSUS URL variants (schema/port errors) → expect 80072EE6 classification
- Win11 explicit scan source policy permutations for each class (Feature/Quality/Drivers/Other)
- Coexistence with third-party MDM (coexistence mode): ensure ConfigMgr deactivates SU workload [coexistence](https://learn.microsoft.com/en-us/intune/configmgr/comanage/coexistence)
- Proxy edge cases: system vs user proxy impact on detection [proxy behavior](https://learn.microsoft.com/en-us/windows/deployment/update/how-windows-update-works#scanning-updates)

---

## Documentation & AAR Integration

26) Include glossary?
- Yes. Define key registry values (WUServer, UseWUServer, DoNotConnect…), CSP nodes (BranchReadinessLevel, UpdateServiceUrl, SetPolicyDrivenUpdateSource*), and workloads. Improves operator clarity.

27) Lessons learned (AAR) format/storage
- JSONL per-run plus Markdown AAR summary; store under AAR/ with timestamps; include root cause, signals, decision, and remediation list. Aligns with org methodology.

28) Feedback loop from AARs
- Yes. Recurrent issues (e.g., specific conflicting GPOs, common misconfigs) should become:
  - Detection rules/conflict taxonomy entries
  - New focused tests and mocks
  - Playbook snippets in docs and TL;DR templates

---

## Appendix: Key citations
- WSUS client GPOs: https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates
- Scan source policy and defaults: https://learn.microsoft.com/en-us/windows/deployment/update/wufb-wsus
- Policy CSP – Update: https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-update
- WU engine internals/service IDs: https://learn.microsoft.com/en-us/windows/deployment/update/how-windows-update-works#scanning-updates
- ConfigMgr + WU policies integration: https://learn.microsoft.com/en-us/intune/configmgr/sum/deploy-use/integrate-windows-update-for-business-windows-10
- Co-management overview/workloads/switching: https://learn.microsoft.com/en-us/intune/configmgr/comanage/overview | https://learn.microsoft.com/en-us/intune/configmgr/comanage/workloads | https://learn.microsoft.com/en-us/intune/configmgr/comanage/how-to-switch-workloads
- Co-management troubleshooting logs: https://learn.microsoft.com/en-us/troubleshoot/mem/intune/comanage-configmgr/troubleshoot-co-management-workloads#frequently-asked-questions
- Autopatch conflicting configurations (cleanup examples): https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/references/windows-autopatch-conflicting-configurations#resolving-conflicts
- Invalid WSUS URL error: https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/error-80072ee6-downlaod-wsus-update
