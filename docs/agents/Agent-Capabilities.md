# Agent Capabilities - ContextForge Work Coding Agent

## Metadata

| Field | Value |
|-------|--------|
| **Agent Version** | v2.0.0 |
| **Copilot Instruction Version** | v3.2.1 |
| **Last Updated** | 2025-08-06T15:30:00Z |
| **Unicode Support** | ASCII-safe (UTF-8 compatible) |
| **Primary Platform** | Windows PowerShell 5.1 |
| **Agent ID Pattern** | `copilot-[identifier]` |

---

## Mission Statement

The ContextForge Work coding agent is designed to deliver enterprise-grade automation solutions following the **ContextForge Universal Methodology**. It specializes in PowerShell 5.1 scripting for SCCM, Microsoft 365, and Windows infrastructure management while maintaining strict compliance with Sacred Geometry Framework principles.

---

## Core Design Principles

### 🌟 Sacred Geometry Framework

The agent operates within six geometric paradigms that drive development evolution:

- **Triangle (🔺)**: Stable foundations with error handling, syntax validation, and logging
- **Circle (🔵)**: Unified workflows with integration testing and dependency management
- **Spiral (🌀)**: Iterative improvement with regression testing and changelog updates
- **Fractal (🔗)**: Modular reuse with interface contracts and component validation
- **Pentagon (⭐)**: Resonant harmony with logging verification and performance testing
- **Dodecahedron (🌐)**: Full system integration with end-to-end testing and AAR completion

### 🌳 Sacred Tree Architecture

- **Roots**: Validated foundational deliverables (schemas, validation rules)
- **Trunk**: Unified integration layer (orchestration scripts, common functions)
- **Branches**: Modular functional subsystems (SCCM modules, M365 modules)
- **Leaves**: User-facing interfaces (CLI tools, reports, documentation)

### 🧠 Core Mandates

1. **Workspace First**: Reuse existing validated artifacts when possible
2. **Logs First**: All execution must be logged with intent and outcome
3. **Trust-but-Verify**: Include validation frameworks for all deliverables

---

## Core Tools and Libraries

### PowerShell 5.1 (Primary Platform)

**Purpose**: Production scripting for SCCM, M365, and Windows infrastructure
**Compatibility**: PowerShell 5.1 syntax exclusively for operational scripts
**Implementation Files**:

- `SCCM/Invoke-SCCMInfrastructureEvaluation.ps1` - Infrastructure evaluation
- `SCCM/Invoke-SCCMClientHealthEvaluation.ps1` - Client health assessment
- `docs/Test-AgentCapabilities.ps1` - Capability validation framework
- `Initialize-ContextForgeModernization.ps1` - Workspace initialization

**Key Configuration**:

```powershell
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
```

**Key Features**:

- SCCM console session integration (assumes existing session)
- Microsoft.PowerShell.SecretManagement for credential handling
- Comprehensive error handling with try/catch blocks
- Built-in transcript logging with `Start-Transcript`

**Example Usage**:

```powershell
# Standard script header with ContextForge compliance
#Requires -Version 5.1
<#
.SYNOPSIS
    ContextForge compliant PowerShell script
.NOTES
    Agent: copilot-[identifier]
    Phase: Triangle (Stable Foundations)
    Created: $(Get-Date).ToString('o')
#>

$ErrorActionPreference = 'Stop'
$AgentId = 'copilot-[identifier]'

# Initialize logging
$LogPath = "C:\temp\Log_ScriptName_$(Get-Date -Format 'yyyyMMdd_HHmmss').jsonl"
Start-Transcript -Path $LogPath.Replace('.jsonl', '.txt') -Append
```

### JSONL Logging System

**Purpose**: Primary structured logging format for audit trails and analysis
**Format**: JSON Lines with standardized schema
**Implementation Files**:

- `docs/Test-AgentCapabilities.ps1` - Contains `Write-JSONLLog` function implementation
- `SCCM/Invoke-SCCMInfrastructureEvaluation.ps1` - Production logging examples
- `SCCM/Invoke-SCCMClientHealthEvaluation.ps1` - Structured logging patterns

**Schema**:

```json
{
  "timestamp": "2025-08-06T15:30:00.000Z",
  "agent_id": "copilot-identifier",
  "level": "INFO|WARN|ERROR",
  "message": "Human readable message",
  "data": {}
}
```

**Implementation**:

```powershell
function Write-JSONLLog {
    param(
        [string]$Level,
        [string]$Message,
        [hashtable]$Data = @{}
    )

    $LogEntry = @{
        timestamp = (Get-Date).ToString('o')
        agent_id = $AgentId
        level = $Level
        message = $Message
        data = $Data
    } | ConvertTo-Json -Compress

    Add-Content -Path $LogPath -Value $LogEntry
}
```

### SQLite (Fallback Storage)

**Purpose**: Structured data storage when JSONL is insufficient
**Use Cases**: Complex relational data, cross-session state persistence
**Configuration**: Auto-initialized when needed, UTF-8 encoding

### Pester Testing Framework

**Purpose**: Unit and integration testing for PowerShell modules
**Version**: Compatible with PowerShell 5.1
**Integration**: Automated testing in validation pipelines
**Implementation Files**:

- `tests/Test-ContextForgeCompliance.ps1` - Workspace compliance testing
- `SCCM/Test-SCCMInfrastructureEvaluation.ps1` - Infrastructure testing
- `SCCM/Test-SCCMHealthEvaluationCompliance.ps1` - Health evaluation testing
- `docs/Test-AgentCapabilities.ps1` - Capability validation testing

### PSScriptAnalyzer

**Purpose**: Static code analysis and PowerShell best practices enforcement
**Rules**: Microsoft recommended rule set plus ContextForge custom rules
**Integration**: Pre-commit validation and CI/CD pipeline integration
**Command Reference**: `Invoke-ScriptAnalyzer -Path <script> -Settings PSGallery`

### Microsoft Configuration Manager (SCCM) Module

**Purpose**: SCCM infrastructure management and client health evaluation
**Assumption**: SCCM console session already established
**Implementation Files**:

- `SCCM/Invoke-SCCMInfrastructureEvaluation.ps1` - Main infrastructure evaluation
- `SCCM/Invoke-SCCMClientHealthEvaluation.ps1` - Client health assessment
- `SCCM/GatherUpgradeLogs.ps1` - Log collection utilities
- `SCCM/DisableCredGuard.ps1` - Security configuration management

**Key Cmdlets**:

- `Get-CMClientSetting` - Client configuration management
- `Get-CMDeviceCollection` - Device collection operations
- `Get-CMBaseline` - Configuration baseline evaluation
- `Get-CMDevice` - Device information retrieval
- `Get-CMSite` - Site configuration details

**Example**:

```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/configurationmanager/get-cmclientsetting
Get-CMClientSetting -Name "Default Client Settings"
```

---

## Configuration Flags and Switches

### Standard Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-WhatIf` | Switch | False | Simulation mode - no actual changes |
| `-Verbose` | Switch | False | Detailed execution logging |
| `-Force` | Switch | False | Bypass confirmations |
| `-NonInteractive` | Switch | False | Suppress all user prompts |
| `-DryRun` | Switch | False | Execute without side effects |

### ContextForge Specific Flags

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-ChaosMode` | Switch | False | Inject random failures for testing |
| `-ErrorRate` | Double | 0.0 | Failure injection rate (0.0-1.0) |
| `-SampleDevices` | Int | 10 | Number of devices for testing |
| `-SkipCompliance` | Switch | False | Bypass ContextForge validation |
| `-GenerateReports` | Switch | False | Create comprehensive output reports |
| `-MockMode` | Switch | False | Use mock data instead of live systems |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CONTEXTFORGE_AGENT_ID` | Override default agent identifier | `copilot-default` |
| `CONTEXTFORGE_LOG_LEVEL` | Logging verbosity | `INFO` |
| `CONTEXTFORGE_WORKSPACE` | Workspace root path | Current directory |

---

## Validation Model

### Shape-Based Validation Matrix

Each Sacred Geometry shape requires specific validation criteria:

| Shape | Validation Requirements |
|-------|------------------------|
| **Triangle** | Error handling implementation, syntax linting, logging configuration |
| **Circle** | Integration testing with external dependencies, dependency mapping |
| **Spiral** | Regression testing, changelog updates, version control |
| **Fractal** | Interface contract testing, module reuse validation |
| **Pentagon** | Logging verification, performance testing, resource monitoring |
| **Dodecahedron** | End-to-end testing, dependency graph validation, AAR completion |

### Validation Tools

**Trust-but-Verify (TV) Framework**:

- `.tv.yaml` configuration files
- `validate_*.ps1` validation scripts
- System state capture before/after operations
- Assumption documentation and verification

**Implementation Files**:

- `docs/trust-but-verify-capabilities.yaml` - Validation configuration
- `docs/Test-AgentCapabilities.ps1` - Main validation script
- `tests/Test-ContextForgeCompliance.ps1` - Compliance validation

**Example TV Configuration**:

```yaml
# .tv.yaml
validation_checks:
  - name: "SCCM_Module_Available"
    test: "Get-Module -Name ConfigurationManager -ListAvailable"
    expected: true
  - name: "PowerShell_Version"
    test: "$PSVersionTable.PSVersion.Major"
    expected: 5
```

### Schema Validation

**Context Object Schema**: `/schemas/context-object.schema.yaml`

- Validates all ContextForge objects against standardized structure
- Required fields: `confidence`, `dimensions`, `agent_id`, `created_at`, `task_id`, `shape`
- Optional validation status tracking and recovery plans

**Implementation Files**:

- `docs/trust-but-verify-capabilities.yaml` - Active validation schema
- `schemas/` directory - Schema definition files (if present)
- `docs/Test-AgentCapabilities.ps1` - Schema compliance validation

### Compliance Testing

**Test Framework**: `Test-ContextForgeCompliance.ps1`

- Validates workspace structure and artifact compliance
- Checks Sacred Geometry shape coverage
- Validates schema adherence
- Generates compliance reports

**Implementation Files**:

- `tests/Test-ContextForgeCompliance.ps1` - Main compliance framework
- `SCCM/Test-SCCMInfrastructureEvaluationCompliance.ps1` - SCCM-specific compliance
- `SCCM/Test-SCCMHealthEvaluationCompliance.ps1` - Health evaluation compliance

---

## Expected Artifact Types

### Primary Deliverables

**PowerShell Scripts** (`.ps1`):

- Main functional scripts with ContextForge headers
- PowerShell 5.1 compatibility required
- Comprehensive error handling and logging
- Support for standard parameters (`-WhatIf`, `-Verbose`, etc.)

**Documentation** (`.md`):

- README files with usage instructions
- After Action Reviews (AARs) with project analysis
- Troubleshooting guides
- API documentation

**Configuration Files** (`.yaml`, `.json`):

- Schema definitions for validation
- Configuration templates
- Environment-specific settings

### Secondary Deliverables

**Test Files**:

- Pester test scripts (`Test-*.ps1`)
- Mock data generators
- Validation frameworks
- Compliance checkers

**Log Files**:

- JSONL structured logs (`.jsonl`)
- PowerShell transcripts (`.txt`)
- Performance metrics
- Error reports

**Output Reports**:

- JSON machine-readable results
- CSV human-readable summaries
- HTML formatted reports
- Executive summaries

### Communication Handoff Files

**Required Structure** (`Communication-to-ChatGPT.yaml`):

```yaml
agent_id: "copilot-[identifier]"
timestamp: "2025-08-06T15:30:00Z"
task_shape: "triangle|circle|spiral|fractal|pentagon|dodecahedron"
task_stage: "initialization|development|validation|completion"
task_weight: 1.0

input_sources: []
output_artifacts: {}
aar_summary:
  objectives_met: []
  challenges_encountered: []
  lessons_learned: []
  success_metrics: {}
```

---

## Extension Model

### Plugin Architecture

**Module Structure**:

```
/modules/
  /sccm/          → SCCM-specific functionality
  /m365/          → Microsoft 365 integration
  /azure/         → Azure resource management
  /security/      → Security and compliance tools
```

**Plugin Interface**:

```powershell
# Required module structure
Export-ModuleMember -Function @(
    'Initialize-ModuleContext',
    'Test-ModuleCompliance',
    'Export-ModuleResults'
)
```

### Event Bus System

**Event Types**:

- `BeforeExecution`: Pre-operation hooks
- `AfterValidation`: Post-validation processing
- `OnError`: Error handling and recovery
- `OnCompletion`: Cleanup and reporting

**Event Handler Registration**:

```powershell
Register-ContextForgeEvent -EventType "BeforeExecution" -Handler {
    param($Context)
    Write-JSONLLog -Level "INFO" -Message "Operation starting" -Data $Context
}
```

### Submodule Integration

**Git Submodules**: Support for external ContextForge-compliant modules
**Package Management**: PowerShell Gallery integration for approved modules
**Validation**: All external modules must pass ContextForge compliance testing

### Optional Azure DevTest Labs Support

**Integration Points**:

- Automated test environment provisioning
- Mock data seeding for complex scenarios
- Performance testing at scale
- Cleanup and resource management

**Configuration**:

```powershell
$AzureTestConfig = @{
    SubscriptionId = "guid"
    ResourceGroup = "contextforge-test"
    LabName = "contextforge-lab"
    EnableCleanup = $true
}
```

---

## Code Examples

### Module Import Pattern

```powershell
# Standard ContextForge module import
Import-Module ".\modules\sccm\ContextForge.SCCM.psm1" -Force

# Initialize module context
$SCCMContext = Initialize-SCCMModuleContext -AgentId $AgentId -LogPath $LogPath

# Validate module compliance
$ComplianceResult = Test-SCCMModuleCompliance -Context $SCCMContext
if (-not $ComplianceResult.Passed) {
    throw "Module compliance validation failed: $($ComplianceResult.Failures -join ', ')"
}
```

### Dry Run Implementation

```powershell
function Invoke-SCCMOperation {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$DeviceCollection,

        [Parameter(Mandatory=$false)]
        [switch]$DryRun
    )

    begin {
        Write-JSONLLog -Level "INFO" -Message "SCCM operation initiated" -Data @{
            collection = $DeviceCollection
            dry_run = $DryRun.IsPresent
        }
    }

    process {
        if ($DryRun -or $WhatIfPreference) {
            Write-Host "DRY RUN: Would process collection '$DeviceCollection'" -ForegroundColor Yellow
            return @{
                Status = "Simulated"
                Collection = $DeviceCollection
                DeviceCount = 100  # Mock data
            }
        }

        if ($PSCmdlet.ShouldProcess($DeviceCollection, "Process SCCM Collection")) {
            # Actual implementation
            $Result = Get-CMDeviceCollection -Name $DeviceCollection
            Write-JSONLLog -Level "INFO" -Message "Collection processed" -Data $Result
            return $Result
        }
    }
}
```

### Mock Data Generation

```powershell
function New-MockSCCMEnvironment {
    param(
        [int]$DeviceCount = 100,
        [double]$ErrorRate = 0.1,
        [switch]$ChaosMode
    )

    $MockDevices = 1..$DeviceCount | ForEach-Object {
        @{
            Name = "DEVICE-$($_.ToString('D4'))"
            LastHeartbeat = (Get-Date).AddHours(-(Get-Random -Minimum 1 -Maximum 48))
            ClientVersion = "5.00.9040.1000"
            OSVersion = "10.0.19045"
            HasErrors = $(if ($ChaosMode) { (Get-Random) -lt $ErrorRate } else { $false })
        }
    }

    return @{
        Devices = $MockDevices
        Collections = @("All Workstations", "Test Group", "Production Servers")
        SiteCode = "CM1"
    }
}
```

---

## Copilot Instruction Synchronization

### Version Tracking

**Current Instruction Version**: v3.2.1
**Last Sync**: 2025-08-06T09:41:45Z
**Update Frequency**: Bi-weekly or on critical changes
**Source Mechanism**: GitHub repository `.github/copilot-instructions.md`

### Sync Process

1. **Validation**: Instructions validated against ContextForge schema
2. **Compatibility Check**: PowerShell 5.1 syntax verification
3. **Integration Testing**: Test scenarios executed with new instructions
4. **Rollout**: Gradual deployment with rollback capability

### Update Detection

**Change Indicators**:

- Version number increment in instruction header
- SHA-256 hash comparison of instruction content
- Capability matrix modification
- Tool availability changes

**Automatic Sync Triggers**:

- GitHub webhook notifications
- Scheduled validation checks
- Agent startup validation
- Manual sync requests

### Configuration Management

**Instruction Storage**:

```
/.github/
  copilot-instructions.md     → Primary instruction set
  /schemas/                   → Validation schemas
  /validation/               → Compliance rules
  /prompt_modules/           → Modular instruction components
```

**Version Control**:

- Git-based version tracking
- Semantic versioning (major.minor.patch)
- Change documentation in commit messages
- Release notes for major updates

---

## Platform Profiles

### SCCM (System Center Configuration Manager)

**Integration Assumptions**:

- SCCM console session pre-established
- ConfigurationManager module available
- Appropriate permissions for device and collection management

**Core Capabilities**:

- Client health evaluation and remediation
- Configuration baseline management
- Device collection operations
- Software deployment status monitoring

**Standard Parameters**:

- Support for `-WhatIf`, `-Verbose`, `-Force`
- SCCM context serialization via `ConvertTo-Json -Depth 5`
- Error handling for connection timeouts and permissions

### Microsoft 365

**Integration Assumptions**:

- Valid Microsoft Graph token with appropriate scopes
- PowerShell Graph SDK modules available
- Tenant-agnostic implementation

**Core Capabilities**:

- User and group management
- Exchange Online administration
- SharePoint Online operations
- Teams configuration management

**Rate Limiting**:

- Automatic retry with exponential backoff
- Rate limit error detection and logging
- Throttling awareness and queue management

### Azure

**Integration Assumptions**:

- Azure PowerShell modules available
- Valid Azure context with subscription access
- Resource group and subscription scope management

**Core Capabilities**:

- Resource deployment and management
- Policy compliance monitoring
- Cost optimization analysis
- Security configuration validation

---

## Security and Compliance

### Credential Management

**Secure Storage**:

- Microsoft.PowerShell.SecretManagement for production secrets
- `.env` files with `python-dotenv` for development
- Environment variables for CI/CD integration
- Mock credential providers for testing

**Security Principles**:

- No plain-text secrets in source code or logs
- Secrets rotation capability
- Audit trail for secret access
- Fail-secure defaults

### Compliance Features

**Data Protection**:

- PII detection and masking in logs
- GDPR compliance for data processing
- Data retention policies
- Secure deletion capabilities

**Audit Requirements**:

- Complete operation logging
- Change tracking with before/after states
- User attribution for all operations
- Compliance report generation

---

## Performance and Monitoring

### Progress Feedback

**User Experience Requirements**:

- `Write-Progress` for operations exceeding 3 seconds
- Real-time status updates with meaningful messages
- Percentage completion when calculable
- ETA estimation for long-running operations

**Implementation Example**:

```powershell
Write-Progress -Activity "Infrastructure Evaluation" `
               -Status "Processing device $currentDevice of $totalDevices" `
               -PercentComplete (($currentDevice / $totalDevices) * 100) `
               -SecondsRemaining $estimatedSecondsRemaining
```

### Performance Metrics

**Tracked Metrics**:

- Execution time per operation
- Memory utilization during processing
- Network latency for external calls
- Error rates and retry statistics

**Monitoring Integration**:

- Windows Performance Counters
- Custom metric collection
- Performance baseline establishment
- Anomaly detection and alerting

---

## Error Handling and Recovery

### Comprehensive Error Management

**Error Classification**:

- Transient errors (network, timeouts) - automatic retry
- Configuration errors (permissions, missing modules) - user guidance
- Data errors (malformed input, validation failures) - detailed reporting
- System errors (disk space, memory) - graceful degradation

**Recovery Strategies**:

```powershell
try {
    $Result = Invoke-ExternalOperation
    Write-JSONLLog -Level "INFO" -Message "Operation successful" -Data $Result
}
catch [System.Net.WebException] {
    # Network-related errors - retry with backoff
    Start-Sleep -Seconds (2 * $RetryCount)
    if ($RetryCount -lt 3) {
        $RetryCount++
        continue
    }
    throw
}
catch [System.UnauthorizedAccessException] {
    # Permission errors - provide guidance
    Write-JSONLLog -Level "ERROR" -Message "Permission denied" -Data @{
        operation = "Invoke-ExternalOperation"
        guidance = "Verify account has appropriate permissions"
    }
    throw
}
catch {
    # Generic error handling with AAR generation
    $ErrorContext = @{
        Operation = "Invoke-ExternalOperation"
        Error = $_.Exception.Message
        StackTrace = $_.ScriptStackTrace
        Timestamp = Get-Date
    }
    Write-JSONLLog -Level "ERROR" -Message "Unexpected error" -Data $ErrorContext
    New-AAREntry -Type "Error" -Context $ErrorContext
    throw
}
```

### Automatic AAR Generation

**AAR Triggers**:

- Significant operation failures
- Performance threshold violations
- Compliance validation failures
- Unexpected system behavior

**AAR Content**:

- Root cause analysis
- Impact assessment
- Remediation recommendations
- Prevention strategies

---

## Trust-but-Verify Validation Results

**Last Validation**: 2025-08-06T14:37:16Z
**Validation Agent**: copilot-validation-agent-001
**Overall Status**: ✅ PASS (100% success rate)

### Validated Capabilities

| Capability | Status | Details |
|------------|--------|---------|
| **PowerShell 5.1 Environment** | ✅ PASS | Version 5.1.26100.4652 confirmed |
| **JSONL Logging System** | ✅ PASS | Log file creation and parsing successful |
| **Configuration Management** | ✅ PASS | Environment variable handling verified |
| **Validation Framework** | ✅ PASS | Schema files and validation rules present |
| **Sacred Geometry Framework** | ✅ PASS | Shape validation rules implemented |
| **Error Handling** | ✅ PASS | Exception handling patterns functional |
| **Documentation System** | ✅ PASS | Agent-Capabilities.md exists and accessible |
| **Communication Handoff** | ✅ PASS | YAML handoff files present and structured |

### Validation Methodology

The Trust-but-Verify protocol employed the following verification approach:

1. **Environmental Validation**: Confirmed PowerShell 5.1+ availability and core functionality
2. **Functional Testing**: Verified JSONL logging, environment variables, and error handling
3. **Structural Validation**: Confirmed presence of schema files, validation rules, and documentation
4. **Integration Testing**: Tested end-to-end capability chains and communication protocols

### Continuous Validation

The validation framework includes:

- **Automated Testing**: `Test-AgentCapabilities.ps1` script for continuous validation
- **Configuration Baseline**: `trust-but-verify-capabilities.yaml` defining validation criteria
- **Reporting**: JSON and JSONL output for audit trails and analysis
- **Monitoring**: Success rate tracking with 80% minimum threshold

### Validation Artifacts

Generated validation artifacts:

- Validation transcript logs (`.txt`)
- Structured JSONL audit trail (`.jsonl`)
- Detailed JSON validation report (`.json`)
- Trust-but-Verify configuration (`.yaml`)

---

## Future Capabilities and Roadmap

### Planned Enhancements

**Q3 2025**:

- Enhanced Azure DevTest Labs integration
- Advanced chaos engineering capabilities
- Machine learning-based performance optimization
- Real-time compliance monitoring

**Q4 2025**:

- Multi-cloud support (AWS, GCP)
- Advanced security scanning integration
- Automated documentation generation
- Federated agent coordination

### Experimental Features

**Beta Capabilities**:

- Natural language operation descriptions
- Predictive failure analysis
- Automated remediation suggestions
- Cross-platform compatibility (PowerShell Core)

**Research Areas**:

- Quantum-resistant cryptography integration
- Advanced AI-powered troubleshooting
- Blockchain-based audit trails
- Zero-trust security model implementation

---

## Support and Documentation

### Knowledge Base

**Internal Documentation**:

- `/docs/` - Comprehensive technical documentation
- `/examples/` - Working code samples and templates
- `/troubleshooting/` - Common issues and solutions
- `/best-practices/` - Recommended patterns and approaches

**External Resources**:

- Microsoft Learn documentation integration
- PowerShell Gallery module documentation
- ContextForge methodology white papers
- Community best practices compilation

### Community Integration

**Contribution Guidelines**:

- ContextForge compliance requirements
- Code review and validation processes
- Documentation standards
- Testing requirements

**Support Channels**:

- GitHub Issues for bug reports
- Discussion forums for best practices
- Documentation wiki for knowledge sharing
- Regular community calls for updates

---

*This document represents the complete capabilities matrix for the ContextForge Work coding agent as of 2025-08-06. For the most current information, consult the live documentation in the workspace repository.*
