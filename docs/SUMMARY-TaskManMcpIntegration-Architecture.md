# TaskManMcpIntegration PowerShell Module - Architecture Design Summary

**Project**: TaskMan MCP Integration - Module Restructure
**Phase**: Architecture Design COMPLETE ✅
**Date**: 2025-12-30
**Architect**: GitHub Copilot (Architect Mode)
**Status**: Ready for Implementation Handoff

---

## 📋 Executive Summary

Comprehensive PowerShell module architecture designed following Microsoft Script Module standards. Transforms loose scripts into a publishable PSGallery module with proper structure, testing, and documentation.

**Outcome**: Production-ready module specification with complete implementation guide.

---

## 📦 Deliverables

### Core Documents

1. **[ADR-001: Module Structure Decision](./ADR-001-TaskManMcpIntegration-Module-Structure.md)** (17.8 KB)
   - Complete architecture decision record
   - Trade-off analysis (3 options evaluated)
   - Design rationale with COF 13D considerations
   - Module manifest specification (with GUID)
   - Root loader implementation (.psm1)
   - Prerequisites validator (warn-only)
   - Config template strategy ({{PLACEHOLDERS}})
   - Help file structure
   - Validation plan with success criteria

2. **[HANDOFF: Implementation Guide](./HANDOFF-TaskManMcpIntegration-Module.md)** (15.2 KB)
   - Step-by-step implementation instructions (11 steps)
   - Copy-paste ready PowerShell commands
   - File migration mapping with validation
   - Expected time: 2 hours 10 minutes
   - Validation checklist (23 items)
   - Known issues and mitigations
   - Questions for user approval

3. **Visual Diagram**: Mermaid module structure diagram (rendered above)

---

## 🏗️ Module Architecture

### Directory Structure

```
TaskManMcpIntegration/
├── TaskManMcpIntegration.psd1      # Manifest (metadata, exports, PSGallery data)
├── TaskManMcpIntegration.psm1      # Auto-loader (imports Public/*.ps1)
├── Public/                         # 2 exported functions
│   ├── Start-McpServers.ps1        # (543 lines, moved from scripts/)
│   └── Test-McpHeartbeat.ps1       # (132 lines, moved from scripts/)
├── Private/                        # Internal helpers (empty Phase 1)
├── Scripts/                        # Non-function scripts
│   ├── Test-Prerequisites.ps1      # Dependency validation (new)
│   └── unified_logger.py           # Python logging (copied from python/)
├── Config/
│   └── mcp_config.template.json    # Config template with {{PLACEHOLDERS}}
├── Tests/
│   └── TaskManMcpIntegration.Tests.ps1  # Pester v5 tests
└── en-US/
    └── about_TaskManMcpIntegration.help.txt  # Get-Help topic
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Structure** | Hierarchical (Option 2) | Right-sized complexity, PSGallery-ready |
| **Docs Location** | Root `docs/` | Visibility, multi-technology scope |
| **Function Names** | Keep `Start-McpServers` | Brevity, established references |
| **Config Storage** | `~/.taskman/` + template | Security, update-safe, convention |
| **Prerequisites** | Warn-only | Offline usage, gradual setup, CI flexibility |

---

## 📊 File Migration Summary

| Source | Destination | Action |
|--------|-------------|--------|
| `scripts/Start-McpServers.ps1` | `Public/` | Move (543 lines) |
| `scripts/Test-McpHeartbeat.ps1` | `Public/` | Move (132 lines) |
| `python/unified_logger.py` | `Scripts/` | Copy |
| `tests/Test-TaskManMcpIntegration.ps1` | `Tests/` | Move + rename |
| `.mcp.json` | `Config/mcp_config.template.json` | Copy + redact |
| `docs/*.md` | *(no change)* | Keep in root |

**New Files Created**: 4
- `TaskManMcpIntegration.psd1` (manifest)
- `TaskManMcpIntegration.psm1` (loader)
- `Scripts/Test-Prerequisites.ps1` (validator)
- `en-US/about_TaskManMcpIntegration.help.txt` (help)

---

## ✅ Validation Plan

### Automated Checks

```powershell
# 1. Manifest validation
Test-ModuleManifest -Path .\TaskManMcpIntegration\TaskManMcpIntegration.psd1

# 2. Module import test
Import-Module .\TaskManMcpIntegration -Force -Verbose

# 3. Function export verification
Get-Command -Module TaskManMcpIntegration  # Should show 2 functions

# 4. Pester test execution
Invoke-Pester -Path .\TaskManMcpIntegration\Tests\ -Output Detailed

# 5. Help system integration
Get-Help Start-McpServers -Full
Get-Help about_TaskManMcpIntegration

# 6. WhatIf support
Start-McpServers -WhatIf
```

### Success Criteria

- ✅ `Test-ModuleManifest` passes (zero errors)
- ✅ Module imports without fatal errors
- ✅ Exactly 2 functions exported
- ✅ Help system functional
- ✅ Prerequisites validator runs on import
- ✅ Pester tests execute (≥80% pass rate)
- ✅ Config template is valid JSON with placeholders

---

## 🎯 Quality Attributes

### PSGallery Readiness

- ✅ Valid `.psd1` manifest with GUID
- ✅ Semantic versioning (1.0.0)
- ✅ PSData tags, ProjectUri, LicenseUri, ReleaseNotes
- ✅ CompatiblePSEditions: Core (cross-platform)
- ✅ PowerShellVersion: 7.0+ requirement

### User Experience

- ✅ Simple installation: `Install-Module TaskManMcpIntegration`
- ✅ Auto-import functions on module load
- ✅ Integrated Get-Help documentation
- ✅ Clear prerequisite warnings (non-blocking)
- ✅ Template-based configuration with placeholders

### Maintainability

- ✅ Public/Private separation (future refactoring ready)
- ✅ Test isolation with Pester v5
- ✅ Verbose logging for troubleshooting
- ✅ Module-scoped variables for configuration

---

## 🚀 Implementation Readiness

### Prerequisites for Coder

- [x] Architecture specification complete
- [x] File migration mapping documented
- [x] PowerShell command sequences provided
- [x] Validation checklist prepared
- [x] Expected warnings documented

### Estimated Effort

| Phase | Time | Complexity |
|-------|------|------------|
| Structure creation | 30 min | Low |
| File migration | 20 min | Low |
| Module files | 40 min | Medium |
| Validation | 20 min | Low |
| Documentation | 20 min | Low |
| **TOTAL** | **2h 10min** | **Medium** |

### Risk Assessment

- **Technical Risk**: Low (reversible via Git)
- **Breaking Changes**: None (scripts remain functional)
- **Dependency Risk**: Medium (requires ContextForge.* modules)
- **Testing Risk**: Low (existing tests migrate with updates)

---

## 📝 Open Questions (User Approval Required)

1. **Module GUID**: Use generated `8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d` or custom?
2. **GitHub URLs**: Replace `YourOrg` with actual organization name?
3. **License**: Confirm license URI path is correct?
4. **Icon**: Do we have a module icon URL for PSGallery?
5. **Dependencies**: Are ContextForge.AgentDetection and Observability modules published?
6. **Config Placeholders**: Need any beyond USER_HOME, WORKSPACE_ROOT, GITHUB_TOKEN, CONTEXT7_API_KEY?

---

## 🔄 Next Steps

### Immediate (Handoff to Coder)

1. User reviews ADR-001 and approves design decisions
2. User answers open questions above
3. Generate final module GUID
4. Coder executes 11-step implementation plan
5. Run validation checklist

### Post-Implementation

1. Update root README.md with installation instructions
2. Commit to Git with descriptive message
3. Expand Pester test coverage to ≥80%
4. Create module README.md
5. Prepare PSGallery publishing (requires account)

### Future Enhancements (Phase 2)

- Add `New-McpConfiguration` function
- Add `Get-McpServerStatus` monitoring
- Add `Stop-McpServers` / `Restart-McpServer`
- Convert help to MAML XML for rich Get-Help
- Add pipeline support to Start-McpServers
- Publish ContextForge.AgentDetection module
- Publish ContextForge.Observability module

---

## 📚 References

- Microsoft PowerShell Module Design: https://docs.microsoft.com/en-us/powershell/scripting/developer/module/designing-your-module
- about_Modules: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_modules
- PSScriptAnalyzer Rules: https://github.com/PowerShell/PSScriptAnalyzer
- Pester v5 Documentation: https://pester.dev/docs/quick-start

---

## 🎓 COF 13D Analysis (Abbreviated)

### Key Dimensions Addressed

1. **Motivational**: Enable PSGallery distribution, simplify user installation
2. **Relational**: Dependencies on ContextForge.* modules documented
3. **Situational**: Cross-platform (Windows/Linux/Mac), PowerShell 7.0+
4. **Resource**: 2h10m implementation time, medium complexity
5. **Computational**: Auto-loader pattern for efficient function import
6. **Temporal**: Phased approach (Phase 1 structure, Phase 2 enhancements)
7. **Holistic**: Integrates with existing ContextForge ecosystem
8. **Validation**: Comprehensive checklist with automated tests
9. **Integration**: Module fits into PowerShell module ecosystem

*Full COF analysis in ADR-001*

---

## ✅ Architecture Approval Status

**Design Complete**: ✅
**Validation Plan**: ✅
**Implementation Guide**: ✅
**Documentation**: ✅
**Handoff Ready**: ✅

**Pending**: User review and approval of open questions
**Next Agent**: Coder (implementation)

---

**Architecture Phase: COMPLETE** 🎉

All design artifacts delivered. Ready for user review and coder implementation.

*For detailed specifications, see [ADR-001](./ADR-001-TaskManMcpIntegration-Module-Structure.md) and [Implementation Handoff](./HANDOFF-TaskManMcpIntegration-Module.md)*
