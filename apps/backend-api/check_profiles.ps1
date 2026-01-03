$paths = @(
    @{ Name = 'AllUsersAllHosts'; Path = $PROFILE.AllUsersAllHosts },
    @{ Name = 'AllUsersCurrentHost'; Path = $PROFILE.AllUsersCurrentHost },
    @{ Name = 'CurrentUserAllHosts'; Path = $PROFILE.CurrentUserAllHosts },
    @{ Name = 'CurrentUserCurrentHost'; Path = $PROFILE.CurrentUserCurrentHost }
)

$outFile = "C:\Users\James\Documents\Github\GHrepos\SCCMScripts\TaskMan-v2\backend-api\profiles_report_absolute.txt"
"--- PROFILE AUDIT START ---" | Out-File -FilePath $outFile -Encoding UTF8

foreach ($p in $paths) {
    $exists = Test-Path $p.Path
    $info = @{
        Name = $p.Name
        Path = $p.Path
        Exists = $exists
        ContentStart = ""
        LineCount = 0
    }

    $out = @()
    if ($exists) {
        $content = Get-Content $p.Path
        $info.LineCount = $content.Count
        if ($info.LineCount -gt 0) {
            $info.ContentStart = ($content | Select-Object -First 5) -join "`n"
        }

        $out += "--- $($p.Name) ---"
        $out += "Path: $($p.Path)"
        $out += "Lines: $($info.LineCount)"
        $out += "Content Preview:"
        $out += $info.ContentStart
        $out += "-----------------"
    } else {
        $out += "--- $($p.Name) ---"
        $out += "Path: $($p.Path)"
        $out += "[DOES NOT EXIST]"
        $out += "-----------------"
    }
    $out | Out-File -FilePath $outFile -Append -Encoding UTF8
}
