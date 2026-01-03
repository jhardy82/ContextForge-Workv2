# NSSM Quick Reference Guide
## TaskMan-v2 Windows Service Management

**Quick access commands for day-to-day operations**

---

## Installation & Deployment

```powershell
# One-command deployment (automated)
.\scripts\deploy-windows-service.ps1

# Custom deployment
.\scripts\deploy-windows-service.ps1 -AppPath "D:\Apps\TaskMan" -Port 8080 -Workers 8

# With custom service account
.\scripts\deploy-windows-service.ps1 -ServiceAccount ".\TaskManService" -ServicePassword (Read-Host -AsSecureString)
```

---

## Service Management

```powershell
# Start service
Start-Service TaskManAPI

# Stop service
Stop-Service TaskManAPI

# Restart service
Restart-Service TaskManAPI

# Check status
Get-Service TaskManAPI

# Check detailed status
Get-Service TaskManAPI | Format-List *

# NSSM-specific status
nssm status TaskManAPI
```

---

## Configuration Management

```powershell
# View all configuration
nssm dump TaskManAPI

# Edit service (GUI)
nssm edit TaskManAPI

# Change worker count
nssm set TaskManAPI AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 8"
Restart-Service TaskManAPI

# Change environment variable
nssm set TaskManAPI AppEnvironmentExtra "ENVIRONMENT=production" "LOG_LEVEL=DEBUG"
Restart-Service TaskManAPI

# Change service account
nssm set TaskManAPI ObjectName ".\NewAccount" "NewPassword"

# View specific parameter
nssm get TaskManAPI AppParameters
nssm get TaskManAPI AppDirectory
nssm get TaskManAPI ObjectName
```

---

## Monitoring & Logs

```powershell
# Tail live logs (stdout)
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Wait -Tail 20

# Tail live logs (stderr)
Get-Content "C:\TaskMan-v2\logs\stderr.log" -Wait -Tail 20

# View last 50 lines
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Tail 50

# Search logs for errors
Select-String -Path "C:\TaskMan-v2\logs\*.log" -Pattern "error|exception|traceback" -CaseSensitive:$false

# View Windows Event Logs
Get-EventLog -LogName Application -Source TaskManAPI -Newest 10

# View health monitoring logs
Get-Content "C:\TaskMan-v2\logs\health-monitor.log" -Tail 50

# Check current log file sizes
Get-ChildItem "C:\TaskMan-v2\logs" | Select-Object Name, @{Name="Size(MB)";Expression={[Math]::Round($_.Length / 1MB, 2)}} | Sort-Object "Size(MB)" -Descending
```

---

## Health Checks

```powershell
# Manual health check (basic)
Invoke-RestMethod -Uri "http://localhost:3001/health" | ConvertTo-Json -Depth 3

# Manual health check (formatted)
$Health = Invoke-RestMethod -Uri "http://localhost:3001/health"
Write-Host "Status: $($Health.status)" -ForegroundColor $(if($Health.status -eq 'healthy'){'Green'}else{'Red'})
Write-Host "Database: $($Health.database.connected)" -ForegroundColor $(if($Health.database.connected){'Green'}else{'Red'})
Write-Host "Latency: $($Health.database.latency_ms) ms"

# Run monitoring script manually
.\scripts\monitor-service-health.ps1

# View health monitoring state
Get-Content "C:\TaskMan-v2\logs\health-state.json" | ConvertFrom-Json | Format-List
```

---

## Performance Monitoring

```powershell
# Check CPU usage
Get-Counter "\Process(python*)\% Processor Time" -SampleInterval 2 -MaxSamples 5

# Check memory usage
$Process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }
$MemoryMB = [Math]::Round($Process.WorkingSet64 / 1MB, 2)
Write-Host "Memory Usage: $MemoryMB MB"

# Monitor in real-time
while ($true) {
    $Process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }
    if ($Process) {
        $MemoryMB = [Math]::Round($Process.WorkingSet64 / 1MB, 2)
        $CpuPercent = [Math]::Round($Process.CPU, 2)
        Write-Host "$(Get-Date -Format 'HH:mm:ss') - Memory: $MemoryMB MB, CPU: $CpuPercent s"
    }
    Start-Sleep -Seconds 5
}

# View process details
Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" } | Format-List *
```

---

## Database Management

```powershell
# Connect to database
psql -U taskman -d taskman_v2

# Run migrations
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\Activate.ps1
alembic upgrade head

# Backup database
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -F c -f "C:\TaskMan-v2\backups\taskman_v2_$(Get-Date -Format 'yyyyMMdd-HHmmss').sql" taskman_v2

# Restore database (stop service first!)
Stop-Service TaskManAPI
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d taskman_v2 "C:\TaskMan-v2\backups\taskman_v2_20251226-120000.sql"
Start-Service TaskManAPI

# List recent backups
Get-ChildItem "C:\TaskMan-v2\backups" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, LastWriteTime, @{Name="Size(MB)";Expression={[Math]::Round($_.Length / 1MB, 2)}}
```

---

## Troubleshooting

```powershell
# Full diagnostic report
@"
========================================
TaskMan-v2 Service Diagnostic Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
========================================

Service Status:
$((Get-Service TaskManAPI | Format-List * | Out-String).Trim())

Process Information:
$((Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" } | Format-List * | Out-String).Trim())

Port Check (3001):
$((Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Format-Table | Out-String).Trim())

Recent Errors (stdout.log):
$((Select-String -Path "C:\TaskMan-v2\logs\stdout.log" -Pattern "error|exception" -Context 2 | Select-Object -Last 5 | Out-String).Trim())

Recent Errors (stderr.log):
$((Select-String -Path "C:\TaskMan-v2\logs\stderr.log" -Pattern "error|exception|traceback" -Context 2 | Select-Object -Last 5 | Out-String).Trim())

Recent Event Log Entries:
$((Get-EventLog -LogName Application -Source TaskManAPI -Newest 5 | Format-Table TimeGenerated, EntryType, Message -AutoSize | Out-String).Trim())
========================================
"@ | Out-File "C:\TaskMan-v2\logs\diagnostic-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

Write-Host "Diagnostic report saved to C:\TaskMan-v2\logs\"

# Check port availability
Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
# If no output, port is free
# If output shows LISTEN, something is using it

# Test if port is responding
Test-NetConnection -ComputerName localhost -Port 3001

# Check Python virtual environment
$PythonExe = "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe"
if (Test-Path $PythonExe) {
    & $PythonExe --version
    & $PythonExe -c "import sys; print(sys.prefix)"
} else {
    Write-Host "Python venv not found!" -ForegroundColor Red
}

# Test database connection (Python)
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\Activate.ps1
python -c "import asyncio; from db.session import check_db_health; print(asyncio.run(check_db_health()))"

# Check NSSM configuration
nssm dump TaskManAPI | Out-File "C:\TaskMan-v2\logs\nssm-config.txt"
Write-Host "NSSM configuration exported to C:\TaskMan-v2\logs\nssm-config.txt"
```

---

## Common Issues & Solutions

### Issue: Service won't start

```powershell
# Check NSSM application path
nssm get TaskManAPI Application
# Should be: C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe

# Check working directory
nssm get TaskManAPI AppDirectory
# Should be: C:\TaskMan-v2\backend-api

# Check stderr logs
Get-Content "C:\TaskMan-v2\logs\stderr.log" -Tail 50

# Test command manually
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 3001
# If this works, NSSM config is wrong
```

### Issue: Database connection failed

```powershell
# Check PostgreSQL service
Get-Service PostgreSQL*

# Test direct connection
psql -h localhost -p 5432 -U taskman -d taskman_v2 -c "SELECT 1;"

# Check DATABASE_URL in .env
Get-Content "C:\TaskMan-v2\backend-api\.env" | Select-String "DATABASE_URL"

# Verify PostgreSQL is listening
Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
```

### Issue: High memory usage

```powershell
# Check current memory
$Process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }
[Math]::Round($Process.WorkingSet64 / 1MB, 2)

# Reduce worker count
nssm set TaskManAPI AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 2"
Restart-Service TaskManAPI

# Set up memory monitoring
# Schedule .\scripts\monitor-service-health.ps1 to run every 5 minutes
```

### Issue: API not responding

```powershell
# Check if service is running
Get-Service TaskManAPI

# Check if Python process exists
Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }

# Check if port is listening
Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue

# Check firewall
Get-NetFirewallRule -DisplayName "TaskMan-v2*"

# Test connectivity
Test-NetConnection -ComputerName localhost -Port 3001
Invoke-WebRequest -Uri "http://localhost:3001/health" -UseBasicParsing
```

---

## Scheduled Tasks

```powershell
# Set up health monitoring (every 5 minutes)
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\TaskMan-v2\scripts\monitor-service-health.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "TaskManAPI-HealthMonitor" -Action $Action -Trigger $Trigger -Principal $Principal

# View scheduled tasks
Get-ScheduledTask -TaskName "TaskManAPI*"

# Run scheduled task manually
Start-ScheduledTask -TaskName "TaskManAPI-HealthMonitor"

# View task history
Get-ScheduledTaskInfo -TaskName "TaskManAPI-HealthMonitor"

# Disable task
Disable-ScheduledTask -TaskName "TaskManAPI-HealthMonitor"

# Remove task
Unregister-ScheduledTask -TaskName "TaskManAPI-HealthMonitor" -Confirm:$false
```

---

## Backup & Restore Service Configuration

```powershell
# Backup NSSM configuration
nssm dump TaskManAPI | Out-File "C:\TaskMan-v2\backups\nssm-config-$(Get-Date -Format 'yyyyMMdd').txt"

# Backup entire service configuration (registry export)
reg export "HKLM\SYSTEM\CurrentControlSet\Services\TaskManAPI" "C:\TaskMan-v2\backups\service-registry-$(Get-Date -Format 'yyyyMMdd').reg" /y

# Restore service (reinstall from backup config file)
# Parse backup file and reconstruct nssm commands
# (Manual process - review backup file and apply relevant nssm set commands)
```

---

## Uninstall Service

```powershell
# Stop service
Stop-Service TaskManAPI

# Remove service
nssm remove TaskManAPI confirm

# Remove Windows Event Log source
Remove-EventLog -Source TaskManAPI

# Remove firewall rule
Remove-NetFirewallRule -DisplayName "TaskMan-v2*"

# Remove scheduled tasks
Get-ScheduledTask -TaskName "TaskManAPI*" | Unregister-ScheduledTask -Confirm:$false

# Optional: Remove application files
# Remove-Item -Recurse -Force "C:\TaskMan-v2"
```

---

## Testing & Validation

```powershell
# End-to-end test sequence
function Test-TaskManService {
    Write-Host "Testing TaskMan-v2 Service..." -ForegroundColor Cyan

    # 1. Service status
    $Service = Get-Service TaskManAPI
    Write-Host "Service Status: $($Service.Status)" -ForegroundColor $(if($Service.Status -eq 'Running'){'Green'}else{'Red'})

    # 2. Process check
    $Process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }
    Write-Host "Process Running: $($null -ne $Process)" -ForegroundColor $(if($null -ne $Process){'Green'}else{'Red'})

    # 3. Port listening
    $Port = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
    Write-Host "Port 3001 Listening: $($null -ne $Port)" -ForegroundColor $(if($null -ne $Port){'Green'}else{'Red'})

    # 4. Health endpoint
    try {
        $Health = Invoke-RestMethod -Uri "http://localhost:3001/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "Health Status: $($Health.status)" -ForegroundColor $(if($Health.status -eq 'healthy'){'Green'}else{'Yellow'})
        Write-Host "Database Connected: $($Health.database.connected)" -ForegroundColor $(if($Health.database.connected){'Green'}else{'Red'})
    } catch {
        Write-Host "Health Endpoint: FAILED" -ForegroundColor Red
    }

    # 5. API docs accessible
    try {
        $Docs = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "API Docs: ACCESSIBLE ($($Docs.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "API Docs: FAILED" -ForegroundColor Red
    }

    Write-Host "`nTest completed!" -ForegroundColor Cyan
}

# Run test
Test-TaskManService
```

---

## Performance Tuning

```powershell
# Optimal worker count (CPU cores - 1, min 2, max 8)
$CpuCount = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
$OptimalWorkers = [Math]::Max(2, [Math]::Min($CpuCount - 1, 8))
Write-Host "Recommended workers: $OptimalWorkers (CPU cores: $CpuCount)"

nssm set TaskManAPI AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers $OptimalWorkers"
Restart-Service TaskManAPI

# Increase shutdown timeout for graceful cleanup
nssm set TaskManAPI AppStopMethodConsole 60000  # 60 seconds
nssm set TaskManAPI AppStopMethodWindow 30000   # 30 seconds

# Reduce restart throttle for faster recovery
nssm set TaskManAPI AppRestartDelay 3000  # 3 seconds
nssm set TaskManAPI AppThrottle 15000     # 15 seconds

# Database connection pool tuning (edit db/session.py)
# pool_size = worker_count * 2
# max_overflow = pool_size * 2
```

---

## Quick Copy-Paste Commands

```powershell
# Full status check (one command)
Get-Service TaskManAPI; Invoke-RestMethod http://localhost:3001/health | ConvertTo-Json

# Restart and watch logs
Restart-Service TaskManAPI; Start-Sleep 3; Get-Content C:\TaskMan-v2\logs\stdout.log -Wait -Tail 20

# Check last 100 lines of both logs
Get-Content C:\TaskMan-v2\logs\stdout.log -Tail 100; Write-Host "`n=== STDERR ===" -ForegroundColor Yellow; Get-Content C:\TaskMan-v2\logs\stderr.log -Tail 100

# Search all logs for specific term
Get-ChildItem C:\TaskMan-v2\logs\*.log | Select-String "database connection" -Context 2

# Export diagnostic bundle
$BundleDir = "C:\TaskMan-v2\diagnostics-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $BundleDir -Force
nssm dump TaskManAPI | Out-File "$BundleDir\nssm-config.txt"
Copy-Item "C:\TaskMan-v2\logs\*.log" $BundleDir
Get-Service TaskManAPI | Format-List * | Out-File "$BundleDir\service-status.txt"
Get-EventLog -LogName Application -Source TaskManAPI -Newest 50 | Export-Csv "$BundleDir\event-log.csv"
Write-Host "Diagnostic bundle created: $BundleDir"
```

---

## References

- Full Documentation: `C:\TaskMan-v2\docs\NSSM_Windows_Service_Deployment.md`
- Deployment Script: `C:\TaskMan-v2\scripts\deploy-windows-service.ps1`
- Monitoring Script: `C:\TaskMan-v2\scripts\monitor-service-health.ps1`
- NSSM Official Docs: https://nssm.cc/usage
