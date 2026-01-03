# Windows Update Scan Source: Research Dossier (Learn-aligned)

Purpose: Canonical conditions that determine Windows Update scan source and related behavior,
with citations and actionable test coverage notes for `SCCM/Get-WUScanSource.ps1`.

## Canonical sources (Microsoft Learn)
- Use Windows Update client policies and WSUS together (scan-source policy, default behaviors, registry caveat):
  - https://learn.microsoft.com/windows/deployment/update/wufb-wsus
  - https://learn.microsoft.com/windows/deployment/update/wufb-wsus#configure-the-scan-sources
  - https://learn.microsoft.com/windows/deployment/update/wufb-wsus#default-scan-behavior
- Policy CSP – Update (SetPolicyDrivenUpdateSourceFor {Feature|Quality|Driver|Other},
  UpdateServiceUrl/Alternate, MU, proxy/TLS, offerings):
  - https://learn.microsoft.com/windows/client-management/mdm/policy-csp-update
- WSUS GPOs and keys (WUServer, WUStatusServer, UseWUServer; DoNotConnect…):
  - https://learn.microsoft.com/windows-server/administration/windows-server-update-services/deploy/4-configure-group-policy-settings-for-automatic-updates
- Autopatch conflicting configurations (keys to flag):
  - https://learn.microsoft.com/windows/deployment/windows-autopatch/references/windows-autopatch-conflicting-configurations
- WUfB + WSUS integration nuance (MU deferral behavior; ConfigMgr identity):
  - https://learn.microsoft.com/windows/deployment/update/waas-integrate-wufb
  - https://learn.microsoft.com/intune/configmgr/sum/deploy-use/integrate-windows-update-for-business-windows-10
- ADMX_ICM RemoveWindowsUpdate_ICM (UX block):
  - https://learn.microsoft.com/windows/client-management/mdm/policy-csp-admx-icm#removewindowsupdate_icm
- WUfB offerings and gating (TRV/ProductVersion, BranchReadinessLevel, ManagePreviewBuilds,
  Pause/Defer, DisableWUfBSafeguards, ExcludeWUDriversInQualityUpdate):
  - https://learn.microsoft.com/windows/deployment/update/waas-configure-wufb
  - https://learn.microsoft.com/windows/deployment/update/waas-wufb-csp-mdm

## Conditions that affect scan source (and intent) to detect/assert
- Scan-source policies per update class (Feature/Quality/Driver/Other):
  - CSP: SetPolicyDrivenUpdateSourceForFeatureUpdates | QualityUpdates | DriverUpdates | OtherUpdates.
  - Require UpdateServiceUrl when selecting WSUS; also consider UpdateServiceUrlAlternate and FillEmptyContentUrls.
  - Registry-only edits need `UseUpdateClassPolicySource`; otherwise scan source may not change.
- Defaults (OS-specific):
  - Win10: WSUS + deferrals can cause scans to WU unless scan-source is set or DisableDualScan=1.
  - Win11: WSUS remains unless scan-source set to WU.
- Dual Scan:
  - DisableDualScan (deprecated on Win11; replaced by scan-source on Win10 2004+).
- WSUS classic policy state:
  - WUServer, WUStatusServer, UseWUServer; client-side targeting hints; AUOptions/DetectionFrequency.
- Microsoft Update enablement:
  - AllowMUUpdateService; MU service GUID registration; removal via ServiceManager.
  - MU + WSUS nuance: MU content from Microsoft Update without WUfB deferral.
- UX/network/public reachability constraints:
  - DoNotConnectToWindowsUpdateInternetLocations; DisableWindowsUpdateAccess/SetDisableUXWUAccess.
  - SetProxyBehaviorForUpdateDetection; WinHTTP proxy; DoNotEnforceEnterpriseTLSCertPinningForUpdateDetection.
- WUfB offerings and guardrails (intent evidence):
  - TargetReleaseVersion + ProductVersion pair; BranchReadinessLevel + ManagePreviewBuilds;
    Pause/Defer; DisableWUfBSafeguards; ExcludeWUDriversInQualityUpdate.

## Recommended flags and evidence fields
- EffectiveScanSource per class (Feature/Quality/Driver/Other) with values:
  WSUS | WU | Invalid: URL missing (for WSUS without UpdateServiceUrl).
- Conflicts/Warnings:
  - ApiDefaultMismatch; DualScanRisk; MUUnderWSUS; CSP-AllowUpdateService-under-WSUS.
  - PublicOnlineBlocked (DoNotConnectToWindowsUpdateInternetLocations=1 with WU source).
  - WUUXBlocked (DisableWindowsUpdateAccess/SetDisableUXWUAccess enabled).
  - ScanSourceRegistryCaveat (SetPolicyDrivenUpdateSource* present via registry but UseUpdateClassPolicySource absent).
  - ProxyMismatch (CSP SetProxyBehavior… vs WinHTTP state); TLSPinningDisabled (DoNotEnforceEnterpriseTLSCertPinningForUpdateDetection=1).
  - MUDeferralBypass (AllowMUUpdateService=1 + WSUS configured).
- Provenance bundle:
  - CSP path values; WSUS keys; MU registration state; gpresult snippets; WU COM defaults; event log hints; netsh winhttp.
  - WUfB offerings: TRV/ProductVersion validity; BranchReadiness mapping; ManagePreviewBuilds value;
    Pause/Defer days; DisableWUfBSafeguards; ExcludeWUDrivers.

## Test additions to reduce “Unknowns”
- Scan-source integrity
  - SetPolicyDrivenUpdateSourceX=WSUS + missing UpdateServiceUrl → Invalid + conflict.
  - SetPolicyDrivenUpdateSourceX present but UseUpdateClassPolicySource missing (when registry path used) → warning flag.
- OS-aware defaults
  - Win10: WSUS + deferral > 0 + no scan-source + DualScan not set → expect WU.
  - Win10 + DisableDualScan=1 → expect WSUS.
  - Win11: WSUS + no scan-source → expect WSUS.
- Public/UX constraints
  - DoNotConnect…=1 with WU → PublicOnlineBlocked.
  - DisableWindowsUpdateAccess/SetDisableUXWUAccess → WUUXBlocked.
- MU interactions
  - AllowMUUpdateService=1 + WSUS → MUDeferralBypass advisory.
- Proxy/TLS
  - SetProxyBehavior… present vs WinHTTP proxy; DoNotEnforceEnterpriseTLSCertPinningForUpdateDetection=1 flagged.
- Offerings
  - TRV/ProductVersion pair validation; BranchReadiness/ManagePreviewBuilds combos; Pause/Defer presence and ranges.

## Notes
- BranchReadinessLevel mappings should align with current channels (Dev/Beta/Release Preview) and GA value (e.g., 32 Current/GA).
- Document source URLs in code comments where checks are implemented for traceability.
