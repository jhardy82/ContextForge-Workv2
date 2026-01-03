$logFile = "setup_db.log"
function Write-Log {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$stamp] $Message"
    Write-Host $logLine
    $logLine | Out-File -FilePath $logFile -Append
}

Write-Log "--- Starting PostgreSQL Setup ---"

# Step 1: Force stop
Write-Log "Stopping database service..."
& docker-compose -f ../docker-compose.taskman-v2.yml stop database 2>&1 | Out-File -FilePath $logFile -Append

# Step 2: Start
Write-Log "Starting database service..."
& docker-compose -f ../docker-compose.taskman-v2.yml up -d database 2>&1 | Out-File -FilePath $logFile -Append

# Step 3: Wait and Verify
Write-Log "Waiting for database to be ready..."
$maxRetries = 10
$retryCount = 0
$isReady = $false

while ($retryCount -lt $maxRetries) {
    Write-Log "Health check attempt $($retryCount + 1)..."
    & docker-compose -f ../docker-compose.taskman-v2.yml exec database pg_isready -U contextforge -d taskman_v2 2>&1 | Out-File -FilePath $logFile -Append
    if ($LASTEXITCODE -eq 0) {
        $isReady = $true
        break
    }
    $retryCount++
    Start-Sleep -Seconds 3
}

if ($isReady) {
    Write-Log "PostgreSQL is READY."
    Write-Log "Last 20 logs from container:"
    & docker-compose -f ../docker-compose.taskman-v2.yml logs --tail 20 database 2>&1 | Out-File -FilePath $logFile -Append
    exit 0
} else {
    Write-Log "ERROR: PostgreSQL failed to become ready after $maxRetries attempts."
    & docker-compose -f ../docker-compose.taskman-v2.yml logs --tail 50 database 2>&1 | Out-File -FilePath $logFile -Append
    exit 1
}
