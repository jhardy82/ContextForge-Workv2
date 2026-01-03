$ErrorActionPreference = 'SilentlyContinue'
$LogFile = "wsl_full_diagnosis.log"

Start-Transcript -Path $LogFile -Force

Write-Output "=== WSL DIAGNOSTIC REPORT ==="
Get-Date

Write-Output "`n[1] WSL Status & Distributions"
wsl --status
wsl --list --verbose

Write-Output "`n[2] Network Configuration (Host)"
Get-NetAdapter -Name "vEthernet (WSL)" | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed
Get-NetIPAddress -InterfaceAlias "vEthernet (WSL)" -AddressFamily IPv4 | Select-Object IPAddress, PrefixLength

Write-Output "`n[3] Network Configuration (Type 2 - HNS)"
Get-HnsNetwork | Where-Object { $_.Name -like "*WSL*" } | Select-Object Id, Name, Type

Write-Output "`n[4] .wslconfig Checks"
$WslConfigPath = "$env:UserProfile\.wslconfig"
if (Test-Path $WslConfigPath) {
    Write-Output "Found .wslconfig at: $WslConfigPath"
    Get-Content $WslConfigPath
} else {
    Write-Output "WARNING: No .wslconfig found in user profile."
}

Write-Output "`n[5] Resource Checks"
$mem = Get-CimInstance Win32_OperatingSystem
Write-Output "Total Phys Memory: $([math]::round($mem.TotalVisibleMemorySize / 1MB, 2)) GB"
Write-Output "Free Phys Memory:  $([math]::round($mem.FreePhysicalMemory / 1MB, 2)) GB"

Write-Output "`n[6] Port Checks (Host Perspective)"
Write-Output "Checking for listeners on 5432 (Postgres) and 3001 (API)..."
Get-NetTCPConnection -LocalPort 5432, 3001 | Select-Object LocalAddress, LocalPort, OwningProcess, State

Write-Output "`n=== END REPORT ==="
Stop-Transcript
Write-Output "Report saved to $LogFile"
