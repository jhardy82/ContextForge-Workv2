$paths = @(
    @{ Name='Core_CurrentUserAllHosts'; Path="$env:USERPROFILE\Documents\PowerShell\profile.ps1" },
    @{ Name='Core_CurrentUserCurrentHost'; Path="$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" },
    @{ Name='Core_AllUsersAllHosts'; Path="$env:ProgramFiles\PowerShell\7\profile.ps1" },
    @{ Name='Core_AllUsersCurrentHost'; Path="$env:ProgramFiles\PowerShell\7\Microsoft.PowerShell_profile.ps1" },
    @{ Name='Desktop_CurrentUserAllHosts'; Path="$env:USERPROFILE\Documents\WindowsPowerShell\profile.ps1" },
    @{ Name='Desktop_CurrentUserCurrentHost'; Path="$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1" },
    @{ Name='Desktop_AllUsersAllHosts'; Path="$env:SystemRoot\System32\WindowsPowerShell\v1.0\profile.ps1" },
    @{ Name='Desktop_AllUsersCurrentHost'; Path="$env:SystemRoot\System32\WindowsPowerShell\v1.0\Microsoft.PowerShell_profile.ps1" }
)

$results = @()

foreach ($p in $paths) {
    $info = @{
        Name = $p.Name
        Path = $p.Path
        Exists = $false
        SizeKB = 0
        Lines = 0
        HasCosmic = $false
        HasWriteHost = $false
        HasPromptOverride = $false
        Header = ""
        Status = "Clean"
    }

    if (Test-Path $p.Path) {
        $info.Exists = $true
        $file = Get-Item $p.Path
        $info.SizeKB = [math]::Round($file.Length / 1KB, 2)

        $content = Get-Content $p.Path -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $lines = $content -split "`n"
            $info.Lines = $lines.Count
            $info.Header = $lines[0..4] -join " | "

            if ($content -match "Cosmic") { $info.HasCosmic = $true; $info.Status = "POLLUTED" }
            if ($content -match "Write-Host") { $info.HasWriteHost = $true; if($info.Status -eq "Clean"){$info.Status = "NOISY"} }
            if ($content -match "function\s+prompt") { $info.HasPromptOverride = $true; if($info.Status -ne "POLLUTED"){$info.Status = "HEAVY"} }

            # Bloat Check
            if ($info.Lines -gt 50) {
                if ($info.Status -eq "Clean") { $info.Status = "BLOATED" }
                elseif ($info.Status -eq "NOISY") { $info.Status = "BLOATED+NOISY" }
            }
        }
    } else {
        $info.Status = "MISSING"
    }

    $results += [PSCustomObject]$info
}

$results | Format-Table -AutoSize
$results | ConvertTo-Json -Depth 2 | Out-File "$PSScriptRoot\profile_analysis.json" -Encoding UTF8
Write-Host "Analysis saved to profile_analysis.json"
