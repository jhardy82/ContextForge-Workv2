<#
.SYNOPSIS
    Runs TaskMan-v2 Python MCP tests inside WSL.

.DESCRIPTION
    This script acts as a bridge between Windows PowerShell and the WSL environment.
    It sets the working directory to the project root (converting Windows path to WSL context automatically via --cd)
    and executes the test suite using `uv run pytest`.

.PARAMETER Distro
    Optional name of the WSL distribution to use. Defaults to the system default.

.EXAMPLE
    .\Invoke-TaskManTests.ps1
    Runs tests in default WSL distro.

.EXAMPLE
    .\Invoke-TaskManTests.ps1 -Distro Ubuntu-22.04
    Runs tests in specific distro.
#>
param(
    [string]$Distro = ''
)

$ErrorActionPreference = 'Stop'

# Get the project root (assuming script is in /scripts or root)
$ScriptRoot = $PSScriptRoot
$ProjectRoot = Resolve-Path "$ScriptRoot\.."

Write-Host "📂 Project Root: $ProjectRoot" -ForegroundColor Cyan

# Construct WSL command arguments
$WslArgs = @('--cd', "$ProjectRoot")

if (![string]::IsNullOrWhiteSpace($Distro)) {
    $WslArgs += ('-d', $Distro)
}

# Command to run inside WSL
# We pass bash, -l, -c, and the command string as SEPARATE arguments to wsl.exe
# Using python -m pytest avoids bin executable permission issues on mounted drives
# UV_LINK_MODE=copy avoids hardlink errors on cross-filesystem mounts
$TestCommand = 'export UV_LINK_MODE=copy; uv run python -m pytest tests/test_async_context.py -v'

Write-Host '🚀 Executing in WSL...' -ForegroundColor Green
Write-Host "   Command: bash -l -c '$TestCommand'" -ForegroundColor Gray

# Execute
# Splitting arguments explicitly so PowerShell passes them correctly to the native executable
& wsl.exe @WslArgs bash -l -c $TestCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host '✅ Tests Passed!' -ForegroundColor Green
} else {
    Write-Host "❌ Tests Failed (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
