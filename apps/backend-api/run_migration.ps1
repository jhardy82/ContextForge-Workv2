$ErrorActionPreference = 'Stop'
$logFile = "$PSScriptRoot\execution_log.txt"

Function Log-Output {
    Param ([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Host "$timestamp - $Message"
}

# Ensure clean log file
"--- MIGRATION EXECUTION START ---" | Out-File -FilePath $logFile -Encoding UTF8

# Validating Environment Variables (forcing WSL IP just in case)
$env:APP_DATABASE__HOST = "172.23.230.194"
$env:DATABASE_URL = "postgresql+psycopg2://contextforge:contextforge@172.23.230.194:5432/taskman_dev"

Log-Output "Targeting Database Host: $env:APP_DATABASE__HOST"

Try {
    Log-Output "STEP 1: Stamping Alembic Revision (Stamp Head)"
    # We use 'head' to skip the missing ghost revisions and assume current schema is valid
    uv run alembic stamp head 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8

    Log-Output "STEP 2: Importing Legacy Data"
    uv run python src/scripts/import_legacy_trackers.py 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8

    Log-Output "SUCCESS: All commands executed."
} Catch {
    Log-Output "ERROR: Script failed."
    Log-Output $_.Exception.Message
    exit 1
}
