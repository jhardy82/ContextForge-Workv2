# TaskManMcpIntegration Module - Implementation Handoff

**Project**: TaskMan MCP Integration - PowerShell Module Restructure
**Phase**: Architecture → Implementation
**Date**: 2025-12-30
**Architect**: GitHub Copilot (Architect Mode)
**Target Implementer**: Coder Agent

---

## Executive Summary

This handoff package contains the complete architecture specification for transforming the TaskMan MCP Integration scripts into a properly structured PowerShell module. The design follows Microsoft Script Module standards and enables PSGallery publication.

**Design Authority**: [ADR-001-TaskManMcpIntegration-Module-Structure.md](./ADR-001-TaskManMcpIntegration-Module-Structure.md)

---

## Module Structure Diagram

```
TaskManMcpIntegration/                      # Module root directory
│
├── TaskManMcpIntegration.psd1              # Module manifest (metadata)
│   ├── Version: 1.0.0
│   ├── GUID: 8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d
│   ├── FunctionsToExport: Start-McpServers, Test-McpHeartbeat
│   ├── ScriptsToProcess: Scripts\Test-Prerequisites.ps1
│   └── PSData: Tags, ProjectUri, ReleaseNotes
│
├── TaskManMcpIntegration.psm1              # Root module loader
│   ├── Auto-imports Public/*.ps1
│   ├── Sets module variables ($script:ConfigDirectory)
│   └── Exports public functions
│
├── Public/                                 # Exported functions (user-facing API)
│   ├── Start-McpServers.ps1                # Main automation entry point
│   │   ├── SupportsShouldProcess (WhatIf)
│   │   ├── Parameters: ServerNames, Force, SkipHealthCheck
│   │   └── Returns: Server startup status
│   │
│   └── Test-McpHeartbeat.ps1               # Health check utility
│       ├── Validates MCP server configurations
│       ├── Checks Python/Node/npm availability
│       └── Returns: Health check results
│
├── Private/                                # Internal helpers (not exported)
│   └── (empty - reserved for future refactoring)
│
├── Scripts/                                # Non-function scripts (ScriptsToProcess)
│   ├── Test-Prerequisites.ps1              # Runs on module import
│   │   ├── Validates: Python 3.11+, Node 18+, npm 9+, uv
│   │   ├── Behavior: Warn only, never blocks import
│   │   └── Output: Verbose/Warning messages
│   │
│   └── unified_logger.py                   # Cross-language logging utility
│       ├── Python 3.11+ compatible
│       └── Used by Start-McpServers.ps1
│
├── Config/                                 # Configuration templates
│   └── mcp_config.template.json            # MCP server config template
│       ├── Placeholders: {{USER_HOME}}, {{WORKSPACE_ROOT}}, {{GITHUB_TOKEN}}
│       ├── User config location: $HOME\.taskman\mcp_config.json
│       └── Format: MCP JSON Schema compliant
│
├── Tests/                                  # Pester tests (v5.0+)
│   └── TaskManMcpIntegration.Tests.ps1     # Module validation tests
│       ├── Module manifest validation
│       ├── Function export verification
│       ├── Configuration template tests
│       └── Minimum coverage: 80%
│
└── en-US/                                  # Help files (Get-Help integration)
    └── about_TaskManMcpIntegration.help.txt
        ├── Prerequisites
        ├── Quick Start
        └── Configuration
```

---

## File Migration Mapping

### Migration Table

| # | Source File | Destination File | Action | Validation |
|---|-------------|------------------|--------|------------|
| 1 | `scripts/Start-McpServers.ps1` | `TaskManMcpIntegration/Public/Start-McpServers.ps1` | **Move** | Verify 543 lines, comment-based help intact |
| 2 | `scripts/Test-McpHeartbeat.ps1` | `TaskManMcpIntegration/Public/Test-McpHeartbeat.ps1` | **Move** | Verify 132 lines, imports ContextForge.Observability |
| 3 | `python/unified_logger.py` | `TaskManMcpIntegration/Scripts/unified_logger.py` | **Copy** | Verify Python 3.11+ syntax, no modification needed |
| 4 | `tests/Test-TaskManMcpIntegration.ps1` | `TaskManMcpIntegration/Tests/TaskManMcpIntegration.Tests.ps1` | **Move + Rename** | Verify Pester v5 compatible, BeforeAll/Describe/It blocks |
| 5 | `.mcp.json` | `TaskManMcpIntegration/Config/mcp_config.template.json` | **Copy + Redact** | Replace secrets with `{{PLACEHOLDERS}}` |
| 6 | (none) | `TaskManMcpIntegration/TaskManMcpIntegration.psd1` | **Create** | Use New-ModuleManifest cmdlet |
| 7 | (none) | `TaskManMcpIntegration/TaskManMcpIntegration.psm1` | **Create** | Auto-loader pattern with Export-ModuleMember |
| 8 | (none) | `TaskManMcpIntegration/Scripts/Test-Prerequisites.ps1` | **Create** | Dependency validation logic |
| 9 | (none) | `TaskManMcpIntegration/en-US/about_TaskManMcpIntegration.help.txt` | **Create** | About help topic |

### Files NOT Migrated (Keep in Root)

| File | Location | Rationale |
|------|----------|-----------|
| `docs/TaskMan-MCP-Integration-Guide.md` | Root `docs/` | Workspace-level documentation |
| `docs/TaskMan-MCP-User-Guide.md` | Root `docs/` | Multi-technology guide (PowerShell + Python + Node) |
| `docs/TaskMan-MCP-Troubleshooting.md` | Root `docs/` | Cross-module troubleshooting |
| `.mcp.json` | Root | VS Code MCP configuration (separate from module) |
| `.mcp/github-server.json` | Root `.mcp/` | VS Code-specific configs |
| `.mcp/postgres-server.json` | Root `.mcp/` | VS Code-specific configs |

---

## Implementation Steps (Detailed)

### Step 1: Generate Module GUID (1 min)

```powershell
# Run this to generate a new unique GUID for the module
$moduleGuid = [guid]::NewGuid().ToString()
Write-Host "Module GUID: $moduleGuid" -ForegroundColor Green

# Expected output (yours will be different):
# Module GUID: 8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d
```

**Action**: Copy this GUID for use in Step 3.

---

### Step 2: Create Directory Structure (2 min)

```powershell
# Navigate to repository root
cd C:\Users\James\Documents\Github\GHrepos\SCCMScripts

# Create module directory structure
$modulePath = '.\TaskManMcpIntegration'
$directories = @('Public', 'Private', 'Scripts', 'Config', 'Tests', 'en-US')

foreach ($dir in $directories) {
    $fullPath = Join-Path $modulePath $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "✓ Created: $fullPath" -ForegroundColor Green
}
```

**Validation**:
```powershell
Get-ChildItem .\TaskManMcpIntegration -Directory
# Should show: Config, en-US, Private, Public, Scripts, Tests
```

---

### Step 3: Create Module Manifest (5 min)

```powershell
# Use the GUID from Step 1
$moduleGuid = '8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d'  # Replace with your GUID

$manifestParams = @{
    Path = '.\TaskManMcpIntegration\TaskManMcpIntegration.psd1'
    RootModule = 'TaskManMcpIntegration.psm1'
    ModuleVersion = '1.0.0'
    GUID = $moduleGuid
    Author = 'TaskMan Development Team'
    CompanyName = 'ContextForge'
    Copyright = '(c) 2025 ContextForge. All rights reserved.'
    Description = @'
TaskMan MCP Integration module provides automated management and health monitoring
for Model Context Protocol (MCP) servers used in TaskMan v2. Includes intelligent
agent detection, comprehensive observability, and cross-language logging support.

EXTERNAL DEPENDENCIES (must be installed separately):
- Python 3.11+ with uv package manager
- Node.js 18+ with npm
- MCP server packages (@modelcontextprotocol/*)
'@
    PowerShellVersion = '7.0'
    CompatiblePSEditions = @('Core')
    ScriptsToProcess = @('Scripts\Test-Prerequisites.ps1')
    FunctionsToExport = @('Start-McpServers', 'Test-McpHeartbeat')
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    Tags = @('MCP', 'TaskMan', 'ModelContextProtocol', 'Automation',
             'Observability', 'AgentDetection', 'CrossPlatform')
    ProjectUri = 'https://github.com/YourOrg/SCCMScripts'
    LicenseUri = 'https://github.com/YourOrg/SCCMScripts/blob/main/LICENSE'
    ReleaseNotes = @'
## 1.0.0 - Initial Release (2025-12-30)

### Features
- Automated MCP server startup with intelligent agent detection
- Comprehensive health check and heartbeat monitoring
- Cross-language logging bridge (PowerShell ↔ Python)
- Session tracking with unique identifiers
- Evidence bundle generation for observability

### Requirements
- PowerShell 7.0+
- Python 3.11+ with uv
- Node.js 18+ with npm
- ContextForge.AgentDetection module
- ContextForge.Observability module
'@
}

New-ModuleManifest @manifestParams
Write-Host "✓ Created module manifest" -ForegroundColor Green
```

**Validation**:
```powershell
Test-ModuleManifest -Path .\TaskManMcpIntegration\TaskManMcpIntegration.psd1
# Should return manifest object with no errors
```

---

### Step 4: Migrate Public Functions (5 min)

```powershell
# Migrate Start-McpServers.ps1
Move-Item -Path .\scripts\Start-McpServers.ps1 `
          -Destination .\TaskManMcpIntegration\Public\Start-McpServers.ps1 `
          -Force
Write-Host "✓ Moved Start-McpServers.ps1" -ForegroundColor Green

# Migrate Test-McpHeartbeat.ps1
Move-Item -Path .\scripts\Test-McpHeartbeat.ps1 `
          -Destination .\TaskManMcpIntegration\Public\Test-McpHeartbeat.ps1 `
          -Force
Write-Host "✓ Moved Test-McpHeartbeat.ps1" -ForegroundColor Green
```

**Validation**:
```powershell
Get-ChildItem .\TaskManMcpIntegration\Public\*.ps1
# Should show: Start-McpServers.ps1, Test-McpHeartbeat.ps1

# Verify line counts
(Get-Content .\TaskManMcpIntegration\Public\Start-McpServers.ps1).Count  # Should be ~543
(Get-Content .\TaskManMcpIntegration\Public\Test-McpHeartbeat.ps1).Count # Should be ~132
```

---

### Step 5: Migrate Scripts (3 min)

```powershell
# Copy unified_logger.py (don't move - may be used elsewhere)
Copy-Item -Path .\python\unified_logger.py `
          -Destination .\TaskManMcpIntegration\Scripts\unified_logger.py `
          -Force
Write-Host "✓ Copied unified_logger.py" -ForegroundColor Green
```

**Validation**:
```powershell
Test-Path .\TaskManMcpIntegration\Scripts\unified_logger.py  # Should be True
Test-Path .\python\unified_logger.py  # Should still be True (original remains)
```

---

### Step 6: Create Config Template (8 min)

```powershell
# Read current .mcp.json configuration
$currentConfig = Get-Content .\.mcp.json -Raw | ConvertFrom-Json

# Create template with placeholders
$template = @{
    '$schema' = 'https://modelcontextprotocol.io/schema/mcp.json'
    mcpServers = @{
        Filesystem = @{
            type = 'stdio'
            command = 'npx'
            args = @('-y', '@modelcontextprotocol/server-filesystem', '{{USER_HOME}}', '{{WORKSPACE_ROOT}}')
        }
        Memory = @{
            type = 'stdio'
            command = 'npx'
            args = @('-y', '@modelcontextprotocol/server-memory')
        }
        'Sequential-Thinking' = @{
            type = 'stdio'
            command = 'npx'
            args = @('-y', '@modelcontextprotocol/server-sequential-thinking')
            env = @{
                DISABLE_THOUGHT_LOGGING = 'false'
            }
        }
        'GitHub-Local' = @{
            type = 'stdio'
            command = 'node'
            args = @('-e', "require('github-mcp-server')")
            env = @{
                GITHUB_TOKEN = '{{GITHUB_TOKEN}}'
            }
        }
        Context7 = @{
            type = 'stdio'
            command = 'npx'
            args = @('-y', '@context7/mcp')
            env = @{
                CONTEXT7_API_KEY = '{{CONTEXT7_API_KEY}}'
            }
        }
        'TaskMan-API' = @{
            type = 'stdio'
            command = 'node'
            args = @('{{WORKSPACE_ROOT}}/taskman-mcp-v2/build/index.js')
        }
    }
}

# Save template
$template | ConvertTo-Json -Depth 10 |
    Set-Content .\TaskManMcpIntegration\Config\mcp_config.template.json
Write-Host "✓ Created config template with placeholders" -ForegroundColor Green
```

**Validation**:
```powershell
$content = Get-Content .\TaskManMcpIntegration\Config\mcp_config.template.json -Raw
$content -match '\{\{USER_HOME\}\}'        # Should be True
$content -match '\{\{WORKSPACE_ROOT\}\}'   # Should be True
$content -match '\{\{GITHUB_TOKEN\}\}'     # Should be True
$content | ConvertFrom-Json  # Should parse successfully
```

---

### Step 7: Create Root Module Loader (10 min)

Create file: `TaskManMcpIntegration\TaskManMcpIntegration.psm1`

```powershell
@'
#Requires -Version 7.0

<#
.SYNOPSIS
    TaskManMcpIntegration module loader

.DESCRIPTION
    Automatically imports all public functions and validates module prerequisites.
    This script is executed when Import-Module TaskManMcpIntegration is called.

.NOTES
    Version: 1.0.0
    Author: TaskMan Development Team
#>

$ErrorActionPreference = 'Stop'

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

$ModuleRoot = $PSScriptRoot

# ============================================================================
# IMPORT PUBLIC FUNCTIONS
# ============================================================================

Write-Verbose "TaskManMcpIntegration: Loading public functions..."

$PublicFunctions = @(Get-ChildItem -Path "$ModuleRoot\Public\*.ps1" -ErrorAction SilentlyContinue)

foreach ($Import in $PublicFunctions) {
    try {
        . $Import.FullName
        Write-Verbose "  ✓ Imported: $($Import.BaseName)"
    } catch {
        Write-Error "Failed to import function $($Import.FullName): $_"
        throw
    }
}

Write-Verbose "TaskManMcpIntegration: Loaded $($PublicFunctions.Count) public functions"

# ============================================================================
# MODULE VARIABLES
# ============================================================================

# Module configuration directory (user-specific)
$script:ConfigDirectory = Join-Path $env:USERPROFILE '.taskman'
if (-not (Test-Path $script:ConfigDirectory)) {
    New-Item -ItemType Directory -Path $script:ConfigDirectory -Force | Out-Null
}

# Template location
$script:ConfigTemplate = Join-Path $ModuleRoot 'Config\mcp_config.template.json'

Write-Verbose "TaskManMcpIntegration: Module loaded successfully"
Write-Verbose "  Config directory: $script:ConfigDirectory"
Write-Verbose "  Template location: $script:ConfigTemplate"

# ============================================================================
# EXPORT MODULE MEMBERS
# ============================================================================

Export-ModuleMember -Function $PublicFunctions.BaseName
'@ | Set-Content .\TaskManMcpIntegration\TaskManMcpIntegration.psm1

Write-Host "✓ Created root module loader" -ForegroundColor Green
```

**Validation**:
```powershell
# Test module import
Import-Module .\TaskManMcpIntegration -Force -Verbose
# Should show: "Loaded 2 public functions"

Get-Command -Module TaskManMcpIntegration
# Should show: Start-McpServers, Test-McpHeartbeat
```

---

### Step 8: Create Prerequisites Validator (15 min)

Create file: `TaskManMcpIntegration\Scripts\Test-Prerequisites.ps1`

```powershell
@'
<#
.SYNOPSIS
    Validates external dependencies for TaskManMcpIntegration module

.DESCRIPTION
    Executed automatically on module import via ScriptsToProcess.
    Checks for required external tools (Python, Node.js, npm) and emits
    warnings if missing. Does NOT block module import to allow offline usage.

.NOTES
    Version: 1.0.0
    Phase: Module Initialization
#>

$ErrorActionPreference = 'Continue'

Write-Verbose "TaskManMcpIntegration: Validating prerequisites..."

$prerequisites = @{
    'Python' = @{
        Command = 'python'
        MinVersion = '3.11.0'
        CheckCmd = { python --version 2>&1 }
        Pattern = 'Python (\d+\.\d+\.\d+)'
    }
    'uv' = @{
        Command = 'uv'
        MinVersion = '0.1.0'
        CheckCmd = { uv --version 2>&1 }
        Pattern = 'uv (\d+\.\d+\.\d+)'
    }
    'Node.js' = @{
        Command = 'node'
        MinVersion = '18.0.0'
        CheckCmd = { node --version 2>&1 }
        Pattern = 'v(\d+\.\d+\.\d+)'
    }
    'npm' = @{
        Command = 'npm'
        MinVersion = '9.0.0'
        CheckCmd = { npm --version 2>&1 }
        Pattern = '(\d+\.\d+\.\d+)'
    }
}

$missingTools = @()
$versionWarnings = @()

foreach ($tool in $prerequisites.GetEnumerator()) {
    $name = $tool.Key
    $config = $tool.Value

    # Check if command exists
    $found = Get-Command $config.Command -ErrorAction SilentlyContinue

    if (-not $found) {
        $missingTools += $name
        Write-Warning "  ✗ $name not found in PATH (required: $($config.MinVersion)+)"
        continue
    }

    # Check version
    try {
        $output = & $config.CheckCmd
        if ($output -match $config.Pattern) {
            $version = [version]$matches[1]
            $minVersion = [version]$config.MinVersion

            if ($version -lt $minVersion) {
                $versionWarnings += "$name $version (need $minVersion+)"
                Write-Warning "  ⚠ $name version $version is below minimum $minVersion"
            } else {
                Write-Verbose "  ✓ $name $version"
            }
        } else {
            Write-Verbose "  ? $name found but version unknown"
        }
    } catch {
        Write-Verbose "  ? $name found but version check failed: $_"
    }
}

# Summary
if ($missingTools.Count -gt 0) {
    Write-Warning @"

TaskManMcpIntegration: Missing prerequisites detected!
The following tools are required for full functionality:
$(($missingTools | ForEach-Object { "  - $_" }) -join "`n")

Installation instructions: https://github.com/YourOrg/SCCMScripts/docs/TaskMan-MCP-Integration-Guide.md

Note: Module imported successfully, but some features may not work.
"@
} else {
    Write-Verbose "TaskManMcpIntegration: All prerequisites validated successfully"
}
'@ | Set-Content .\TaskManMcpIntegration\Scripts\Test-Prerequisites.ps1

Write-Host "✓ Created prerequisites validator" -ForegroundColor Green
```

**Validation**:
```powershell
# Test prerequisite validation (should run on import)
Import-Module .\TaskManMcpIntegration -Force -Verbose
# Should show dependency checks in verbose output
```

---

### Step 9: Migrate Tests (5 min)

```powershell
# Move and rename test file
Move-Item -Path .\tests\Test-TaskManMcpIntegration.ps1 `
          -Destination .\TaskManMcpIntegration\Tests\TaskManMcpIntegration.Tests.ps1 `
          -Force
Write-Host "✓ Moved test file" -ForegroundColor Green

# Update test file to reference module from relative path
$testContent = Get-Content .\TaskManMcpIntegration\Tests\TaskManMcpIntegration.Tests.ps1 -Raw
$testContent = $testContent -replace 'Import-Module .*ContextForge\.Observability.*', `
    'Import-Module "$PSScriptRoot\..\TaskManMcpIntegration.psd1" -Force'
$testContent | Set-Content .\TaskManMcpIntegration\Tests\TaskManMcpIntegration.Tests.ps1
Write-Host "✓ Updated test file imports" -ForegroundColor Green
```

**Validation**:
```powershell
Invoke-Pester -Path .\TaskManMcpIntegration\Tests\ -Output Detailed
# Should run tests (may have some failures initially - OK for Phase 1)
```

---

### Step 10: Create Help File (10 min)

Create file: `TaskManMcpIntegration\en-US\about_TaskManMcpIntegration.help.txt`

```powershell
@'
TOPIC
    about_TaskManMcpIntegration

SHORT DESCRIPTION
    TaskMan MCP Integration module for automated MCP server management

LONG DESCRIPTION
    The TaskManMcpIntegration module provides comprehensive automation and
    observability for Model Context Protocol (MCP) servers used in TaskMan v2.

    Key Features:
    - Automated server startup with intelligent agent detection
    - Health check and heartbeat monitoring
    - Cross-language logging (PowerShell ↔ Python)
    - Session tracking with unique identifiers
    - Evidence bundle generation for observability

PREREQUISITES
    - PowerShell 7.0 or later
    - Python 3.11+ with uv package manager
    - Node.js 18+ with npm
    - ContextForge.AgentDetection module
    - ContextForge.Observability module

INSTALLATION
    Install from PowerShell Gallery:

        Install-Module -Name TaskManMcpIntegration -Scope CurrentUser

    Or manually copy to PowerShell module path:

        $modulePath = "$HOME\Documents\PowerShell\Modules\TaskManMcpIntegration"
        Copy-Item -Path .\TaskManMcpIntegration -Destination $modulePath -Recurse

QUICK START
    Import the module:

        Import-Module TaskManMcpIntegration

    Start all configured MCP servers:

        Start-McpServers -Force

    Run health check on all servers:

        Test-McpHeartbeat

    Start specific servers only:

        Start-McpServers -ServerNames "TaskMan-API", "GitHub-Local"

CONFIGURATION
    Configuration templates are stored in:

        $HOME\.taskman\mcp_config.json

    Template location:

        <ModuleRoot>\Config\mcp_config.template.json

SEE ALSO
    - Start-McpServers
    - Test-McpHeartbeat
    - https://github.com/YourOrg/SCCMScripts/docs/TaskMan-MCP-Integration-Guide.md
'@ | Set-Content .\TaskManMcpIntegration\en-US\about_TaskManMcpIntegration.help.txt

Write-Host "✓ Created help file" -ForegroundColor Green
```

**Validation**:
```powershell
Import-Module .\TaskManMcpIntegration -Force
Get-Help about_TaskManMcpIntegration
# Should display help topic
```

---

### Step 11: Final Validation (10 min)

```powershell
# 1. Test module manifest
Test-ModuleManifest -Path .\TaskManMcpIntegration\TaskManMcpIntegration.psd1

# 2. Import module and verify
Import-Module .\TaskManMcpIntegration -Force -Verbose

# 3. Verify exported functions
$commands = Get-Command -Module TaskManMcpIntegration
Write-Host "Exported functions: $($commands.Name -join ', ')" -ForegroundColor Cyan

# 4. Check function help
Get-Help Start-McpServers -Full
Get-Help Test-McpHeartbeat -Full

# 5. Verify directory structure
Get-ChildItem .\TaskManMcpIntegration -Recurse -File |
    Select-Object FullName, Length | Format-Table

# 6. Run Pester tests
Invoke-Pester -Path .\TaskManMcpIntegration\Tests\ -Output Detailed

# 7. Test WhatIf support
Start-McpServers -WhatIf

Write-Host "`n✅ Module validation complete!" -ForegroundColor Green
```

---

## Validation Checklist

**Module Structure**:
- [ ] `TaskManMcpIntegration/` directory created
- [ ] All subdirectories exist: Public, Private, Scripts, Config, Tests, en-US
- [ ] `.psd1` manifest file created
- [ ] `.psm1` loader file created

**File Migration**:
- [ ] `Start-McpServers.ps1` in Public/ (543 lines)
- [ ] `Test-McpHeartbeat.ps1` in Public/ (132 lines)
- [ ] `unified_logger.py` in Scripts/
- [ ] `TaskManMcpIntegration.Tests.ps1` in Tests/
- [ ] `mcp_config.template.json` in Config/ with placeholders

**Functionality**:
- [ ] `Test-ModuleManifest` passes with zero errors
- [ ] `Import-Module TaskManMcpIntegration` succeeds
- [ ] `Get-Command -Module TaskManMcpIntegration` shows 2 functions
- [ ] `Get-Help Start-McpServers` displays help
- [ ] `Get-Help about_TaskManMcpIntegration` displays about topic
- [ ] Prerequisites validation runs on import (warnings OK)
- [ ] `Start-McpServers -WhatIf` works

**Testing**:
- [ ] Pester tests run without fatal errors
- [ ] Config template is valid JSON
- [ ] Placeholders present in template: `{{USER_HOME}}`, `{{WORKSPACE_ROOT}}`, `{{GITHUB_TOKEN}}`

---

## Known Issues / Expected Warnings

1. **ContextForge Module Dependencies**: Tests may fail if ContextForge.AgentDetection and ContextForge.Observability modules are not installed. This is expected.

2. **Prerequisite Warnings**: Module import will show warnings if Python/Node.js/npm missing. This is intentional (warn-only behavior).

3. **Test Failures**: Initial test run may have failures due to environment-specific paths. Update tests as needed.

4. **Help File**: Basic text format only (Phase 1). Future: Convert to MAML XML for rich Get-Help.

---

## Next Steps (Post-Implementation)

1. **Validation**: Run complete validation checklist
2. **Documentation**: Update root README.md with installation instructions
3. **Git Commit**: Commit new module structure with descriptive message
4. **Testing**: Expand test coverage to 80%+
5. **PSGallery**: Prepare for publishing (requires PSGallery account)

---

## Questions for User (Before Proceeding)

1. **Module GUID**: Use generated GUID `8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d` or specific one?
2. **GitHub URLs**: Replace `YourOrg` with actual organization name?
3. **License**: Confirm license URI is correct?
4. **Dependencies**: Are ContextForge.AgentDetection and ContextForge.Observability modules ready?
5. **Config Placeholders**: Any additional placeholders needed beyond USER_HOME, WORKSPACE_ROOT, GITHUB_TOKEN, CONTEXT7_API_KEY?

---

## Handoff Authority

This implementation specification is derived from:
- **ADR**: [ADR-001-TaskManMcpIntegration-Module-Structure.md](./ADR-001-TaskManMcpIntegration-Module-Structure.md)
- **Standards**: Microsoft PowerShell Module Development Guidelines
- **Testing**: Pester v5.0+ Best Practices

**Estimated Implementation Time**: 2 hours 10 minutes
**Complexity**: Medium
**Risk Level**: Low (reversible via Git)

**Approval Status**: ⏳ Pending user review
**Ready for Coder**: ✅ Yes (pending GUID generation)

---

**End of Handoff Document**
