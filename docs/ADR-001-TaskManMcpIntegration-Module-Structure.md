# ADR-001: TaskManMcpIntegration PowerShell Module Structure

## Status
**Proposed** | Date: 2025-12-30 | Architect Agent

## Context

TaskMan MCP Integration currently exists as a collection of loose scripts in the `scripts/` directory without proper PowerShell module packaging. This creates challenges for:

1. **Distribution**: Users must manually copy scripts and maintain dependencies
2. **Versioning**: No standard version management or release tracking
3. **Discoverability**: Functions not auto-imported; users must dot-source scripts
4. **PSGallery Publishing**: Cannot publish to PowerShell Gallery without manifest
5. **Testing**: Test organization scattered across workspace
6. **Documentation**: Help files not integrated with Get-Help system

### Current State

```
SCCMScripts/
├── scripts/
│   ├── Start-McpServers.ps1         # Main automation entry point
│   ├── Test-McpHeartbeat.ps1        # Health check utility
│   └── (238+ other scripts)
├── tests/
│   └── Test-TaskManMcpIntegration.ps1  # Integration tests
├── python/
│   └── unified_logger.py            # Cross-language logging
├── .mcp/
│   ├── github-server.json
│   └── postgres-server.json
├── .mcp.json                        # VS Code MCP configuration
└── docs/
    ├── TaskMan-MCP-Integration-Guide.md
    ├── TaskMan-MCP-User-Guide.md
    └── TaskMan-MCP-Troubleshooting.md
```

### External Dependencies

- **Python**: 3.11+ with `uv` package manager
- **Node.js**: 18+ with npm
- **PowerShell**: 7.0+ (cross-platform)
- **MCP Servers**: Various npm packages (@modelcontextprotocol/*)

## Decision Drivers

1. **Microsoft Best Practices**: Follow official PowerShell module development standards
2. **PSGallery Readiness**: Enable publishing to PowerShell Gallery
3. **User Experience**: Simple installation via `Install-Module`
4. **Maintainability**: Clear separation of public/private functions
5. **Testing**: Pester-compatible test organization
6. **Documentation**: Integrated Get-Help support
7. **Configuration**: Template-based setup for sensitive data

## Considered Options

### Option 1: Monolithic Module (Single Directory)
**Structure**: All files in one `TaskManMcpIntegration/` directory

**Pros**:
- Simplest structure
- Minimal file organization overhead

**Cons**:
- Poor separation of concerns
- Hard to maintain as module grows
- Difficult to separate public from private functions
- Test organization unclear

**Estimated Effort**: 2 hours

### Option 2: Hierarchical Module (Recommended)
**Structure**: Organized by function type (Public/Private/Scripts/Config/Tests)

**Pros**:
- Clear separation of public API from internal helpers
- Easy to maintain and extend
- Standard PowerShell module pattern
- Test isolation
- Config templating for sensitive data

**Cons**:
- More files and folders to manage
- Requires auto-loader (.psm1) to import functions

**Estimated Effort**: 4 hours

### Option 3: Multi-Module Approach
**Structure**: Separate modules for AgentDetection, Observability, McpIntegration

**Pros**:
- Maximum modularity
- Each module can be versioned independently

**Cons**:
- Significant complexity increase
- Inter-module dependency management
- Harder for users to install

**Estimated Effort**: 12+ hours

## Decision

**We will use Option 2: Hierarchical Module Structure**

### Rationale

1. **Standards Alignment**: Matches Microsoft's recommended module structure
2. **Right-Sized Complexity**: Provides organization without over-engineering
3. **PSGallery Compatibility**: Manifest structure required for publishing
4. **Maintainability**: Clear boundaries for public vs. internal code
5. **Testability**: Dedicated test directory with Pester support
6. **Configuration Management**: Template-based config separation

## Module Architecture

### Directory Structure

```
TaskManMcpIntegration/
├── TaskManMcpIntegration.psd1      # Module manifest (metadata, exports)
├── TaskManMcpIntegration.psm1      # Root module loader (auto-imports Public/)
├── Public/                         # Exported functions (FunctionsToExport)
│   ├── Start-McpServers.ps1        # Main server automation
│   └── Test-McpHeartbeat.ps1       # Health check utility
├── Private/                        # Internal helpers (not exported)
│   └── (empty for Phase 1 - reserved for future refactoring)
├── Scripts/                        # Non-function scripts (ScriptsToProcess)
│   ├── Test-Prerequisites.ps1      # Validate Python/Node/npm on import
│   └── unified_logger.py           # Cross-language logging utility
├── Config/                         # Configuration templates
│   └── mcp_config.template.json    # Template with {{PLACEHOLDERS}}
├── Tests/                          # Pester tests
│   └── TaskManMcpIntegration.Tests.ps1
└── en-US/                          # Help files (MAML XML)
    └── about_TaskManMcpIntegration.help.txt
```

### File Migration Mapping

| Source | Destination | Action |
|--------|-------------|--------|
| `scripts/Start-McpServers.ps1` | `Public/Start-McpServers.ps1` | Move + preserve header |
| `scripts/Test-McpHeartbeat.ps1` | `Public/Test-McpHeartbeat.ps1` | Move + preserve header |
| `python/unified_logger.py` | `Scripts/unified_logger.py` | Move (non-PowerShell script) |
| `tests/Test-TaskManMcpIntegration.ps1` | `Tests/TaskManMcpIntegration.Tests.ps1` | Move + rename |
| `.mcp.json` | `Config/mcp_config.template.json` | Copy + redact secrets |
| `docs/TaskMan-MCP-*.md` | *(Keep in root docs/)* | No change (visibility) |

## Detailed Component Specifications

### 1. Module Manifest (TaskManMcpIntegration.psd1)

```powershell
@{
    # Core metadata
    RootModule = 'TaskManMcpIntegration.psm1'
    ModuleVersion = '1.0.0'
    GUID = '8a7d4c5e-2b3f-4a1e-9c6d-7e8f0a1b2c3d'  # Generate new GUID
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

    # Requirements
    PowerShellVersion = '7.0'
    CompatiblePSEditions = @('Core')

    # Scripts to run on module import
    ScriptsToProcess = @(
        'Scripts\Test-Prerequisites.ps1'
    )

    # Functions to export (only Public functions)
    FunctionsToExport = @(
        'Start-McpServers',
        'Test-McpHeartbeat'
    )

    # Cmdlets, variables, aliases (none for Phase 1)
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()

    # Private data for PSGallery
    PrivateData = @{
        PSData = @{
            Tags = @('MCP', 'TaskMan', 'ModelContextProtocol', 'Automation',
                     'Observability', 'AgentDetection', 'CrossPlatform')
            LicenseUri = 'https://github.com/YourOrg/SCCMScripts/blob/main/LICENSE'
            ProjectUri = 'https://github.com/YourOrg/SCCMScripts'
            IconUri = ''  # Optional: Add module icon URL
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

### Installation
Install-Module -Name TaskManMcpIntegration -Scope CurrentUser

### Quick Start
Import-Module TaskManMcpIntegration
Start-McpServers -Force
Test-McpHeartbeat
'@
            ExternalModuleDependencies = @(
                # Note: These are other PowerShell modules, not system dependencies
                'ContextForge.AgentDetection',
                'ContextForge.Observability'
            )
        }
    }
}
```

### 2. Root Module Loader (TaskManMcpIntegration.psm1)

```powershell
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
```

### 3. Prerequisites Validator (Scripts/Test-Prerequisites.ps1)

```powershell
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
```

### 4. Configuration Template (Config/mcp_config.template.json)

```json
{
  "$schema": "https://modelcontextprotocol.io/schema/mcp.json",
  "mcpServers": {
    "Filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "{{USER_HOME}}", "{{WORKSPACE_ROOT}}"]
    },
    "Memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "Sequential-Thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {
        "DISABLE_THOUGHT_LOGGING": "false"
      }
    },
    "GitHub-Local": {
      "type": "stdio",
      "command": "node",
      "args": ["-e", "require('github-mcp-server')"],
      "env": {
        "GITHUB_TOKEN": "{{GITHUB_TOKEN}}"
      }
    },
    "Context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@context7/mcp"],
      "env": {
        "CONTEXT7_API_KEY": "{{CONTEXT7_API_KEY}}"
      }
    },
    "TaskMan-API": {
      "type": "stdio",
      "command": "node",
      "args": ["{{WORKSPACE_ROOT}}/taskman-mcp-v2/build/index.js"]
    }
  }
}
```

**Placeholder replacement strategy**:
- `{{USER_HOME}}` → `$env:USERPROFILE` (Windows) or `$env:HOME` (Linux/Mac)
- `{{WORKSPACE_ROOT}}` → Project root path
- `{{GITHUB_TOKEN}}` → User-provided environment variable
- `{{CONTEXT7_API_KEY}}` → User-provided environment variable

### 5. Test File (Tests/TaskManMcpIntegration.Tests.ps1)

```powershell
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.0.0' }

BeforeAll {
    # Import module under test
    Import-Module "$PSScriptRoot\..\TaskManMcpIntegration.psd1" -Force
}

Describe 'TaskManMcpIntegration Module' {

    Context 'Module Manifest' {
        It 'Should have a valid manifest' {
            Test-ModuleManifest -Path "$PSScriptRoot\..\TaskManMcpIntegration.psd1" -ErrorAction Stop
        }

        It 'Should export Start-McpServers function' {
            Get-Command Start-McpServers -Module TaskManMcpIntegration | Should -Not -BeNullOrEmpty
        }

        It 'Should export Test-McpHeartbeat function' {
            Get-Command Test-McpHeartbeat -Module TaskManMcpIntegration | Should -Not -BeNullOrEmpty
        }
    }

    Context 'Function Availability' {
        It 'Should load all public functions' {
            $commands = Get-Command -Module TaskManMcpIntegration
            $commands.Count | Should -Be 2
        }
    }

    Context 'Configuration Template' {
        It 'Should have config template file' {
            $templatePath = Join-Path (Split-Path $PSScriptRoot) 'Config\mcp_config.template.json'
            $templatePath | Should -Exist
        }

        It 'Should have valid JSON template' {
            $templatePath = Join-Path (Split-Path $PSScriptRoot) 'Config\mcp_config.template.json'
            $content = Get-Content $templatePath -Raw
            { $content | ConvertFrom-Json } | Should -Not -Throw
        }

        It 'Should contain placeholder tokens' {
            $templatePath = Join-Path (Split-Path $PSScriptRoot) 'Config\mcp_config.template.json'
            $content = Get-Content $templatePath -Raw
            $content | Should -Match '\{\{USER_HOME\}\}'
            $content | Should -Match '\{\{WORKSPACE_ROOT\}\}'
        }
    }
}

Describe 'Start-McpServers' {
    It 'Should have WhatIf support' {
        Get-Command Start-McpServers | Select-Object -ExpandProperty Parameters |
            Should -HaveKey 'WhatIf'
    }

    It 'Should have Force parameter' {
        Get-Command Start-McpServers | Select-Object -ExpandProperty Parameters |
            Should -HaveKey 'Force'
    }
}

Describe 'Test-McpHeartbeat' {
    It 'Should be available as a command' {
        Get-Command Test-McpHeartbeat | Should -Not -BeNullOrEmpty
    }
}
```

### 6. Help File Stub (en-US/about_TaskManMcpIntegration.help.txt)

```
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
```

## Design Decisions

### Decision 1: Documentation Location

**Question**: Should docs/ remain in root or move to module?

**Decision**: **Keep in root `docs/` directory**

**Rationale**:
1. **Visibility**: Root docs are easier to find in GitHub
2. **Scope**: Guides cover more than just the PowerShell module (Python, Node.js)
3. **Navigation**: Users expect README/docs at repository root
4. **Cross-reference**: Other modules may reference these docs

**Alternative**: Create `TaskManMcpIntegration/docs/` for module-specific docs only

### Decision 2: Function Naming Convention

**Question**: Keep `Start-McpServers` or rename to `Start-TaskManMcpServer`?

**Decision**: **Keep current naming: `Start-McpServers`, `Test-McpHeartbeat`**

**Rationale**:
1. **Brevity**: Shorter names are easier to type
2. **Established**: Already documented and referenced in multiple files
3. **Scope**: Module name provides namespace (TaskManMcpIntegration\Start-McpServers)
4. **Clarity**: "MCP Servers" is descriptive enough within module context

**PowerShell Best Practice Note**: Technically should follow Verb-Noun pattern with approved verbs (✓ Start, Test are approved). "McpServers" is the noun.

### Decision 3: Config File Location

**Question**: Store config in module directory or user home?

**Decision**: **Hybrid approach**
- **Template**: `<ModuleRoot>/Config/mcp_config.template.json` (read-only)
- **Actual Config**: `$HOME\.taskman\mcp_config.json` (user-writable)

**Rationale**:
1. **Security**: User home directory keeps secrets out of module
2. **Updates**: Module updates don't overwrite user config
3. **Portability**: Users can version control their config separately
4. **Convention**: Follows .ssh/, .aws/, .kube/ pattern

**Implementation**:
- On first run, copy template to `~\.taskman\` and prompt for placeholder values
- Module reads from user directory, falls back to template if missing

### Decision 4: Prerequisite Validation Behavior

**Question**: Block module import if Python/Node.js missing?

**Decision**: **Warn but don't block**

**Rationale**:
1. **Offline Usage**: Users may import module to read help/docs
2. **Gradual Setup**: Allow partial functionality while dependencies install
3. **CI/CD**: Some CI environments may load module for linting without running
4. **Flexibility**: Let users decide if they need full functionality

**Implementation**:
- `Test-Prerequisites.ps1` emits warnings but never throws
- Functions validate their own prerequisites at runtime and provide clear errors

## Validation Plan

### Validation Checklist

```powershell
# 1. Module Manifest Validation
Test-ModuleManifest -Path .\TaskManMcpIntegration\TaskManMcpIntegration.psd1

# 2. Module Import
Import-Module .\TaskManMcpIntegration -Force -Verbose

# 3. Function Export Verification
Get-Command -Module TaskManMcpIntegration
# Expected output: Start-McpServers, Test-McpHeartbeat

# 4. Get-Help Integration
Get-Help Start-McpServers -Full
Get-Help Test-McpHeartbeat -Full

# 5. Prerequisite Validation (ScriptsToProcess)
# Should run automatically on import and display warnings if missing tools

# 6. File Structure Verification
Test-Path .\TaskManMcpIntegration\Public\Start-McpServers.ps1
Test-Path .\TaskManMcpIntegration\Public\Test-McpHeartbeat.ps1
Test-Path .\TaskManMcpIntegration\Scripts\Test-Prerequisites.ps1
Test-Path .\TaskManMcpIntegration\Scripts\unified_logger.py
Test-Path .\TaskManMcpIntegration\Config\mcp_config.template.json

# 7. Pester Test Execution
Invoke-Pester -Path .\TaskManMcpIntegration\Tests\ -Output Detailed

# 8. WhatIf Support
Start-McpServers -WhatIf

# 9. Config Template Validation
$template = Get-Content .\TaskManMcpIntegration\Config\mcp_config.template.json -Raw
$template | ConvertFrom-Json  # Should parse without errors
$template -match '\{\{' # Should contain placeholders
```

### Success Criteria

- [ ] `Test-ModuleManifest` passes with zero errors
- [ ] `Import-Module TaskManMcpIntegration` succeeds without fatal errors
- [ ] `Get-Command -Module TaskManMcpIntegration` returns exactly 2 functions
- [ ] `Get-Help Start-McpServers` displays function help
- [ ] ScriptsToProcess executes and displays prerequisite status
- [ ] All file paths exist after migration
- [ ] Pester tests run and pass (minimum 80% coverage)
- [ ] Config template is valid JSON with placeholders
- [ ] Module can be removed and reimported without errors

## Implementation Plan (Handoff to Coder)

### Phase 1: Structure Creation (30 min)

1. Create directory structure:
   ```powershell
   New-Item -ItemType Directory -Path TaskManMcpIntegration\{Public,Private,Scripts,Config,Tests,en-US}
   ```

2. Generate GUID for manifest:
   ```powershell
   [guid]::NewGuid().ToString()
   ```

3. Create manifest file using `New-ModuleManifest` with provided specifications

### Phase 2: File Migration (20 min)

4. Move files according to migration mapping table
5. Rename test file to follow Pester convention (.Tests.ps1)
6. Copy .mcp.json to Config/mcp_config.template.json and redact secrets

### Phase 3: Module Files (40 min)

7. Create `TaskManMcpIntegration.psm1` with Public function auto-loader
8. Create `Scripts/Test-Prerequisites.ps1` with dependency validation
9. Create `en-US/about_TaskManMcpIntegration.help.txt`
10. Create `Tests/TaskManMcpIntegration.Tests.ps1` with manifest/function tests

### Phase 4: Validation (20 min)

11. Run validation checklist
12. Fix any manifest errors
13. Verify all public functions are exported
14. Confirm Pester tests pass

### Phase 5: Documentation (20 min)

15. Update root README.md with module installation instructions
16. Add comment-based help to Public functions (Get-Help compatible)
17. Create module README.md in TaskManMcpIntegration/

**Total Estimated Time**: 2 hours 10 minutes

## Consequences

### Positive

1. **PSGallery Ready**: Can publish to PowerShell Gallery for easy distribution
2. **Standard Structure**: Follows Microsoft best practices, familiar to PowerShell developers
3. **Auto-Import**: Users don't need to dot-source scripts manually
4. **Testable**: Pester tests isolated in dedicated directory
5. **Versionable**: Semantic versioning via manifest enables upgrade tracking
6. **Discoverable**: Functions appear in `Get-Command -Module` and `Get-Help`
7. **Secure**: Config templates keep secrets out of source control

### Negative

1. **Migration Effort**: Existing scripts must be moved (one-time cost)
2. **Complexity**: More files and folders to maintain
3. **Dependencies**: Users must install ContextForge.AgentDetection and Observability modules
4. **Learning Curve**: Team must understand module structure conventions

### Neutral

1. **Documentation**: Root docs remain separate from module
2. **Configuration**: Hybrid template + user config approach requires explanation
3. **Prerequisites**: Warn-only validation may confuse users expecting strict checks

## Related Decisions

- None (first ADR for this project)
- Future ADR: ContextForge.AgentDetection module structure
- Future ADR: ContextForge.Observability module structure

## Notes

### Open Questions for User Confirmation

1. **Module GUID**: Should we generate new or use specific GUID?
2. **GitHub URLs**: Replace `YourOrg` with actual organization name
3. **License**: Confirm license type (MIT, Apache, proprietary)
4. **Icon**: Do we have a module icon URL for PSGallery?
5. **Dependent Modules**: Are ContextForge.AgentDetection and Observability ready to publish?

### Future Enhancements (Out of Scope for Phase 1)

- [ ] Add `New-McpConfiguration` function to generate config from template
- [ ] Add `Get-McpServerStatus` for runtime monitoring
- [ ] Add `Stop-McpServers` for graceful shutdown
- [ ] Add `Restart-McpServer` for individual server restarts
- [ ] Convert en-US help to MAML XML for rich Get-Help experience
- [ ] Add pipeline support to Start-McpServers (accept server names from pipeline)
- [ ] Add `-PassThru` parameter to return server objects

### References

- [PowerShell Module Design Best Practices](https://docs.microsoft.com/en-us/powershell/scripting/developer/module/designing-your-module)
- [about_Modules](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_modules)
- [How to Write a PowerShell Script Module](https://docs.microsoft.com/en-us/powershell/scripting/developer/module/how-to-write-a-powershell-script-module)
- [PSScriptAnalyzer Rules](https://github.com/PowerShell/PSScriptAnalyzer/blob/master/RuleDocumentation/README.md)
