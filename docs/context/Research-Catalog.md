# Modern Workplace Engineering Research Catalog

Purpose
- Single, refreshable catalog of qualitative, authoritative, and verified sources to inform
  PowerShell 5.1–first, SCCM/Intune/M365 workflows.
- Scope includes: PowerShell modules, vendor docs, GitHub repos, and MVP/expert blogs used by practitioners.

Metadata
- Last refreshed: 2025-08-13T00:00:00Z
- Refresh cadence: Monthly, and on major module releases or policy changes
- Maintainer: ContextForge.Core
- PowerShell baseline: Windows PowerShell 5.1 (note: some items require PS 7+; see flags)

Validation criteria
- Source type: First-party vendor, official gallery page, or recognized MVP/expert
- Signals: Maintainer credibility, update recency, download/adoption, license clarity, PS version compatibility
- Cross-check: When possible, corroborate across Gallery, repo, and author docs

## PowerShell Gallery modules (authoritative listings)
- PSWindowsUpdate
  - Gallery: https://www.powershellgallery.com/packages/PSWindowsUpdate
  - Notes: Windows Update client management; PS 5.1+; actively maintained
- Evergreen
  - Gallery: https://www.powershellgallery.com/packages/Evergreen
  - Notes: Latest app versions and URLs from vendor sources; PS 3.0+; pairs with stealthpuppy docs
- PolicyFileEditor
  - Gallery: https://www.powershellgallery.com/packages/PolicyFileEditor
  - Notes: Edit local GPO registry.pol; PS 2.0+; widely used for ADMX-backed settings
- Microsoft.Graph
  - Gallery: https://www.powershellgallery.com/packages/Microsoft.Graph
  - Notes: Official Graph SDK meta-module; PS 5.1+; broad API coverage
- ExchangeOnlineManagement
  - Gallery: https://www.powershellgallery.com/packages/ExchangeOnlineManagement
  - Notes: REST-backed EXO v3; PS 3.0+; replaces legacy WinRM basic auth
- PnP.PowerShell (PS 7.4+ required)
  - Gallery: https://www.powershellgallery.com/packages/PnP.PowerShell
  - Notes: M365 PnP cmdlets; not compatible with PS 5.1; use only in dev/automation contexts supporting 7+
- IntuneWin32App
  - Gallery: https://www.powershellgallery.com/packages/IntuneWin32App
  - Notes: Manage Win32 apps in Intune; PS 5.0+; community-maintained by MSEndpointMgr
- WingetTools
  - Gallery: https://www.powershellgallery.com/packages/WingetTools
  - Notes: Utility cmdlets for winget; PS 5.1; authored by Jeff Hicks

## Vendor/community documentation
- Evergreen documentation (stealthpuppy)
  - URL: https://stealthpuppy.com/evergreen/
  - Notes: Design, trust model, functions, and examples maintained by Aaron Parker (MVP)

## GitHub repositories (primary sources)
- MSEndpointMgr/IntuneWin32App
  - URL: https://github.com/MSEndpointMgr/IntuneWin32App
  - Notes: Functions for packaging, publishing, and assigning Win32 apps; readme includes end-to-end examples
- microsoftgraph/msgraph-sdk-powershell
  - URL: https://github.com/microsoftgraph/msgraph-sdk-powershell
  - Notes: Official SDK repository; authentication patterns, modules table, and upgrade notes

## MVP/expert blogs (practitioner guidance)
- Oliver Kieselbach
  - URL: https://oliverkieselbach.com/
  - Topics: Autopilot, Intune, SyncML tooling, deployment automation, troubleshooting
- Peter van der Woude
  - URL: https://petervanderwoude.nl/
  - Topics: Intune device config, Edge management, recovery features, policy hygiene; timely weekly posts
- Andrew Taylor
  - URL: https://andrewstaylor.com/
  - Topics: Intune best practices, Autopilot Device Prep, EUC tools, reporting approaches
- Martin Bengtsson (imab.dk)
  - URL: https://www.imab.dk/
  - Topics: Intune/SCCM security hardening, file associations, built-in apps, practical remediation scripts

## Selection rationale and compatibility flags
- PS baseline: All recommended modules are PS 5.1-compatible except PnP.PowerShell (PS 7.4+)
- Recency: Evergreen, Microsoft.Graph, and EXO receive frequent updates; blogs above active through 2025
- Credibility: Official galleries/repos and long-standing MVP authors with enterprise focus

## How we use this catalog
- Research-first: Cite Gallery + repo + (when applicable) author docs
- Implementation: Prefer official SDKs (Microsoft.Graph) and trusted community modules (IntuneWin32App, Evergreen)
- Risks and caveats:
  - PnP.PowerShell requires PS 7.4+; avoid in PS 5.1 operational scripts
  - Community modules may have breaking changes; pin versions for production

## Refresh plan
- Monthly sweep: Re-verify module versions, PS minimums, and last-published dates
- Event-driven: Refresh on major Windows/Intune/Graph service releases
- Evidence: Log updates in AAR and JSONL audit with deltas and links

---
End of catalog.
