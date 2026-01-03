# NSSM Windows Service Deployment Guide
## TaskMan-v2 FastAPI Backend on Windows

**Document Version**: 1.0
**Date**: 2025-12-26
**Target Application**: TaskMan-v2 Backend API (FastAPI + Uvicorn)
**Platform**: Windows Server 2019+ / Windows 10+

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [NSSM Configuration Best Practices](#nssm-configuration-best-practices)
3. [Python Application as Windows Service](#python-application-as-windows-service)
4. [PostgreSQL Integration](#postgresql-integration)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Comparison with Alternatives](#comparison-with-alternatives)
7. [Complete Deployment Example](#complete-deployment-example)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## Executive Summary

### Why NSSM for TaskMan-v2?

**NSSM (Non-Sucking Service Manager)** is the optimal choice for deploying TaskMan-v2 as a Windows Service because:

- **Zero Code Changes**: Works with existing Python applications without service wrapper code
- **Production Proven**: Battle-tested for Python/Node.js applications on Windows
- **Graceful Shutdown**: Handles SIGTERM/SIGINT properly for FastAPI cleanup
- **Built-in Recovery**: Automatic restart on failure with configurable delays
- **Environment Isolation**: Full control over environment variables and working directory
- **Windows Event Log**: Native integration for centralized monitoring

### Deployment Architecture

```
Windows Service (NSSM)
  └─> Python Virtual Environment (.venv)
        └─> Uvicorn ASGI Server
              └─> FastAPI Application (main:app)
                    └─> PostgreSQL Database (Windows Service)
```

---

## 1. NSSM Configuration Best Practices

### 1.1 Service Account Selection

| Account Type | Pros | Cons | Recommended For |
|--------------|------|------|-----------------|
| **LocalSystem** | Full system access, no password management | Too privileged, security risk | **NOT RECOMMENDED** |
| **NetworkService** | Network access, no password, moderate privileges | Limited file system access | Database connections only |
| **LocalService** | Low privileges, no password | No network access, limited DB connectivity | **NOT RECOMMENDED** |
| **Custom Domain/Local User** | Precise permission control, audit trail | Password management required | **RECOMMENDED (Production)** |

#### Production Recommendation: Custom Service Account

```powershell
# Create dedicated service account
$ServiceUser = "TaskManService"
$ServicePassword = (ConvertTo-SecureString "ComplexPassword123!" -AsPlainText -Force)

New-LocalUser -Name $ServiceUser `
    -Password $ServicePassword `
    -Description "TaskMan-v2 API Service Account" `
    -PasswordNeverExpires:$true `
    -UserMayNotChangePassword:$true

# Grant permissions
$Acl = Get-Acl "C:\TaskMan-v2"
$AccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $ServiceUser,
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$Acl.SetAccessRule($AccessRule)
Set-Acl "C:\TaskMan-v2" $Acl

# Grant "Log on as a service" right
$tempPath = [System.IO.Path]::GetTempFileName()
secedit /export /cfg $tempPath /quiet
$currentConfig = Get-Content $tempPath
$newConfig = $currentConfig -replace "(SeServiceLogonRight = .*)", "`$1,$ServiceUser"
$newConfig | Set-Content $tempPath
secedit /configure /db secedit.sdb /cfg $tempPath /areas USER_RIGHTS /quiet
Remove-Item $tempPath
```

### 1.2 Working Directory and Path Configuration

**Critical NSSM Parameters:**

```powershell
# Application path (MUST be Python executable in venv)
nssm set TaskManAPI Application "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe"

# Startup directory (where .env and main.py reside)
nssm set TaskManAPI AppDirectory "C:\TaskMan-v2\backend-api"

# Arguments (using uvicorn module invocation)
nssm set TaskManAPI AppParameters `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4 --log-config logging.json"

# Ensure AppExit actions for uvicorn reload
nssm set TaskManAPI AppExit Default Restart
nssm set TaskManAPI AppExit 0 Restart  # Normal exit triggers restart
```

**Why `python.exe` from venv, not `uvicorn.exe`?**
- NSSM struggles with wrapper scripts (`.exe` launchers in `Scripts/`)
- Direct Python module invocation (`-m uvicorn`) is more reliable
- Allows passing Python flags (e.g., `-OO` for optimization)

### 1.3 Environment Variable Injection

**NSSM Environment Approach:**

```powershell
# Set environment variables (space-delimited)
nssm set TaskManAPI AppEnvironmentExtra `
    "ENVIRONMENT=production" `
    "DATABASE_URL=postgresql://taskman:password@localhost:5432/taskman_v2" `
    "LOG_LEVEL=INFO" `
    "API_PORT=3001" `
    "CF_RUN_ID=svc-$(Get-Date -Format 'yyyyMMdd-HHmmss')" `
    "PYTHONUNBUFFERED=1"

# Alternative: Use .env file (recommended for secrets)
# NSSM will read from AppDirectory automatically if using python-dotenv
```

**Security Best Practice**: Use `.env` file with restricted ACLs instead of NSSM environment variables for secrets:

```powershell
# Lock down .env file permissions
$EnvFile = "C:\TaskMan-v2\backend-api\.env"
$Acl = Get-Acl $EnvFile
$Acl.SetAccessRuleProtection($true, $false)  # Disable inheritance
$Acl.Access | ForEach-Object { $Acl.RemoveAccessRule($_) }  # Remove all rules
$AdminRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Administrators", "FullControl", "Allow"
)
$ServiceRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "TaskManService", "Read", "Allow"
)
$Acl.SetAccessRule($AdminRule)
$Acl.SetAccessRule($ServiceRule)
Set-Acl $EnvFile $Acl
```

### 1.4 Graceful Shutdown Signaling

**NSSM Shutdown Sequence:**

```powershell
# Configure graceful shutdown
nssm set TaskManAPI AppStopMethodSkip 0              # Don't skip any method
nssm set TaskManAPI AppStopMethodConsole 30000       # Send Ctrl+C, wait 30s
nssm set TaskManAPI AppStopMethodWindow 15000        # Send WM_CLOSE, wait 15s
nssm set TaskManAPI AppStopMethodThreads 10000       # Terminate threads, wait 10s
nssm set TaskManAPI AppKill 1                        # Force kill if still running

# FastAPI shutdown handler (in main.py lifespan)
# Already implemented - NSSM Ctrl+C triggers asynccontextmanager cleanup
```

**Verification Test:**

```powershell
# Stop service and check logs for clean shutdown
Stop-Service TaskManAPI -Force
Get-Content "C:\TaskMan-v2\backend-api\logs\api.log" -Tail 20
# Should see: "session_summary" and "api_shutdown" events
```

---

## 2. Python Application as Windows Service

### 2.1 Virtual Environment Activation Within Service

**NSSM automatically activates the venv when using the venv Python path:**

```powershell
# Correct approach - no manual activation needed
nssm set TaskManAPI Application "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe"

# WRONG - do not use activate.bat
# nssm set TaskManAPI Application "cmd.exe"
# nssm set TaskManAPI AppParameters "/c .venv\Scripts\activate.bat && python -m uvicorn..."
```

**How it works:**
1. NSSM launches `C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe`
2. Python automatically uses venv's `site-packages`
3. `sys.path` is correctly configured for venv
4. No shell required (avoids cmd.exe/powershell overhead)

**Verification:**

```powershell
# Test command directly
& "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe" -c "import sys; print(sys.prefix)"
# Output: C:\TaskMan-v2\backend-api\.venv
```

### 2.2 Uvicorn vs Gunicorn on Windows

| Feature | Uvicorn (Windows) | Gunicorn (Windows) |
|---------|-------------------|-------------------|
| **Native Support** | ✅ Fully supported | ❌ Unix-only (fork-based) |
| **Worker Model** | `--workers N` (multiprocessing) | N/A |
| **Performance** | Excellent (async/await) | N/A |
| **Graceful Reload** | ✅ Supported | N/A |
| **Windows Compatibility** | 100% | 0% (requires WSL) |

**Recommendation: Uvicorn with Workers**

```powershell
# Production configuration
nssm set TaskManAPI AppParameters `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4 --log-config logging.json --no-access-log"

# Workers calculation (CPU cores)
$WorkerCount = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
Write-Host "Recommended workers: $WorkerCount"
```

**Gunicorn Alternative (via WSL2 - not recommended):**

```bash
# Only if absolutely required for Unix-specific features
# Requires Windows Subsystem for Linux 2
wsl -d Ubuntu-20.04 -- /TaskMan-v2/backend-api/.venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 2.3 Process Management (Single vs Multiple Workers)

**Worker Strategy Decision Matrix:**

| Scenario | Workers | Rationale |
|----------|---------|-----------|
| **Development/Testing** | 1 | Easier debugging, no process overhead |
| **Production (Light Load)** | 2-4 | Balance concurrency and memory |
| **Production (Heavy Load)** | `CPU_COUNT` | Maximize throughput |
| **High Availability** | `CPU_COUNT + 1` | Worker failure resilience |

**Implementation with NSSM:**

```powershell
# Dynamic worker configuration based on CPU
$CpuCount = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
$WorkerCount = [Math]::Max(2, [Math]::Min($CpuCount, 8))  # Min 2, max 8

nssm set TaskManAPI AppParameters `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers $WorkerCount --log-level info"
```

**Single Worker Mode (for debugging):**

```powershell
# Remove --workers flag for single process
nssm set TaskManAPI AppParameters `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --reload"
# Note: --reload NOT recommended in production
```

### 2.4 Memory Leak Detection and Automatic Restart

**NSSM Built-in Memory Limit:**

```powershell
# Restart if memory exceeds 2GB
nssm set TaskManAPI AppThrottle 30000  # Wait 30s before restart
nssm set TaskManAPI AppRestartDelay 5000  # 5s delay between restarts

# Memory monitoring via PowerShell scheduled task
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument `
    "-NoProfile -File C:\TaskMan-v2\scripts\monitor-memory.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "TaskManAPI-MemoryMonitor" -Action $Action -Trigger $Trigger
```

**Memory Monitor Script (`monitor-memory.ps1`):**

```powershell
# C:\TaskMan-v2\scripts\monitor-memory.ps1
$ServiceName = "TaskManAPI"
$MaxMemoryMB = 2048
$LogFile = "C:\TaskMan-v2\logs\memory-monitor.log"

$Process = Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }

if ($Process) {
    $MemoryMB = [Math]::Round($Process.WorkingSet64 / 1MB, 2)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    if ($MemoryMB -gt $MaxMemoryMB) {
        $Message = "$Timestamp - HIGH MEMORY: $MemoryMB MB (limit: $MaxMemoryMB MB) - Restarting service"
        Add-Content -Path $LogFile -Value $Message
        Restart-Service $ServiceName
    } else {
        $Message = "$Timestamp - Memory OK: $MemoryMB MB"
        Add-Content -Path $LogFile -Value $Message
    }
}
```

**Python-side Memory Profiling (optional):**

```python
# Add to main.py startup
import tracemalloc
tracemalloc.start()

# In periodic health check endpoint
@app.get("/metrics/memory")
async def memory_metrics():
    current, peak = tracemalloc.get_traced_memory()
    return {
        "current_mb": round(current / 1024 / 1024, 2),
        "peak_mb": round(peak / 1024 / 1024, 2)
    }
```

---

## 3. PostgreSQL Integration Options

### 3.1 PostgreSQL as Windows Service

**Installation via Official Installer:**

```powershell
# Download PostgreSQL 15 Windows installer
Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-15.5-1-windows-x64.exe" `
    -OutFile "C:\Temp\postgresql-installer.exe"

# Silent installation
Start-Process "C:\Temp\postgresql-installer.exe" -ArgumentList `
    "--mode unattended --superpassword MySecurePassword --servicename PostgreSQL15 --serverport 5432" `
    -Wait

# Verify service
Get-Service PostgreSQL15
# Status should be "Running"
```

**Service Dependencies (NSSM):**

```powershell
# Ensure TaskManAPI starts AFTER PostgreSQL
nssm set TaskManAPI DependOnService PostgreSQL15
nssm set TaskManAPI Start SERVICE_DELAYED_AUTO_START  # Wait for dependencies
```

### 3.2 Connection Pooling for Service-Based Deployment

**SQLAlchemy Configuration (already in TaskMan-v2):**

```python
# db/session.py - optimized for Windows Service
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/taskman_v2")

# Production pool settings for Windows Service
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_size=10,  # Core connections (should match worker count)
    max_overflow=20,  # Burst capacity
    pool_pre_ping=True,  # Test connections before use (critical for service)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
    connect_args={
        "server_settings": {"application_name": "TaskManAPI"},
        "timeout": 10,  # Connection timeout
        "command_timeout": 30,  # Query timeout
    }
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

**Pool Size Calculation:**

```python
# Recommended formula: (worker_count * 2) + overflow
# Example for 4 workers:
# - pool_size = 10 (core connections)
# - max_overflow = 20 (burst to 30 total)
# - Total max connections: 30 (safe for default PostgreSQL max_connections=100)
```

**PostgreSQL Configuration (`postgresql.conf`):**

```ini
# C:\Program Files\PostgreSQL\15\data\postgresql.conf

# Connection limits
max_connections = 100  # Default, sufficient for single API instance
shared_buffers = 256MB  # 25% of RAM (for 1GB system)

# Query performance
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Logging (for Windows Event Viewer integration)
logging_collector = on
log_destination = 'eventlog'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'none'  # Log only errors in production
log_min_duration_statement = 1000  # Log slow queries (>1s)

# Autovacuum (critical for long-running services)
autovacuum = on
autovacuum_max_workers = 2
autovacuum_naptime = 1min
```

### 3.3 Database Backup Automation Without Docker

**PowerShell Scheduled Task Backup:**

```powershell
# C:\TaskMan-v2\scripts\backup-database.ps1
$BackupDir = "C:\TaskMan-v2\backups"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupFile = "$BackupDir\taskman_v2_$Timestamp.sql"
$PostgreSQLBin = "C:\Program Files\PostgreSQL\15\bin"
$DatabaseName = "taskman_v2"

# Ensure backup directory exists
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# Set PostgreSQL password via environment variable (avoid prompt)
$env:PGPASSWORD = "MySecurePassword"

# Run pg_dump
& "$PostgreSQLBin\pg_dump.exe" -U postgres -F c -b -v -f $BackupFile $DatabaseName

# Remove backups older than 7 days
Get-ChildItem -Path $BackupDir -Filter "taskman_v2_*.sql" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item -Force

# Log completion
$LogFile = "C:\TaskMan-v2\logs\backup.log"
$Message = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Backup completed: $BackupFile"
Add-Content -Path $LogFile -Value $Message
```

**Schedule Backup Task:**

```powershell
# Daily backup at 2 AM
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument `
    "-NoProfile -ExecutionPolicy Bypass -File C:\TaskMan-v2\scripts\backup-database.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "TaskManAPI-DatabaseBackup" `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Description "Daily backup of TaskMan-v2 database"
```

**Backup Restoration:**

```powershell
# C:\TaskMan-v2\scripts\restore-database.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

$PostgreSQLBin = "C:\Program Files\PostgreSQL\15\bin"
$DatabaseName = "taskman_v2"
$env:PGPASSWORD = "MySecurePassword"

# Stop API service before restore
Stop-Service TaskManAPI

# Drop and recreate database
& "$PostgreSQLBin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS $DatabaseName;"
& "$PostgreSQLBin\psql.exe" -U postgres -c "CREATE DATABASE $DatabaseName;"

# Restore from backup
& "$PostgreSQLBin\pg_restore.exe" -U postgres -d $DatabaseName -v $BackupFile

# Restart API service
Start-Service TaskManAPI
```

---

## 4. Monitoring and Logging

### 4.1 Windows Event Log Integration

**NSSM Event Log Configuration:**

```powershell
# Configure NSSM to log to Windows Event Viewer
nssm set TaskManAPI AppStdout "C:\TaskMan-v2\logs\stdout.log"
nssm set TaskManAPI AppStderr "C:\TaskMan-v2\logs\stderr.log"
nssm set TaskManAPI AppRotateFiles 1  # Enable rotation
nssm set TaskManAPI AppRotateOnline 1  # Rotate while running
nssm set TaskManAPI AppRotateSeconds 86400  # Daily rotation
nssm set TaskManAPI AppRotateBytes 10485760  # 10MB max size
```

**Python Logging to Windows Event Log:**

```python
# Add to main.py imports
import logging.handlers

# Windows Event Log handler
class WindowsEventLogHandler(logging.Handler):
    """Custom handler for Windows Event Log via structlog."""

    def emit(self, record):
        # Use PowerShell to write to Event Log
        try:
            import subprocess
            message = self.format(record)
            level_map = {
                logging.DEBUG: "Information",
                logging.INFO: "Information",
                logging.WARNING: "Warning",
                logging.ERROR: "Error",
                logging.CRITICAL: "Error"
            }
            event_type = level_map.get(record.levelno, "Information")

            subprocess.run([
                "powershell", "-Command",
                f"Write-EventLog -LogName Application -Source TaskManAPI -EntryType {event_type} -EventId 1000 -Message '{message}'"
            ], check=False)
        except Exception:
            pass  # Fail silently to avoid disrupting application

# Register Event Log source (run once during installation)
# New-EventLog -LogName Application -Source TaskManAPI
```

**Query Event Logs:**

```powershell
# View TaskManAPI events from last 24 hours
Get-EventLog -LogName Application -Source TaskManAPI -After (Get-Date).AddDays(-1) |
    Format-Table TimeGenerated, EntryType, Message -AutoSize
```

### 4.2 Log Rotation Strategies

**Option A: NSSM Built-in Rotation (Recommended)**

```powershell
# Already configured above - NSSM handles rotation automatically
nssm set TaskManAPI AppRotateFiles 1
nssm set TaskManAPI AppRotateOnline 1
nssm set TaskManAPI AppRotateSeconds 86400  # Daily
nssm set TaskManAPI AppRotateBytes 10485760  # 10MB

# Log files will be renamed: stdout.log -> stdout.log.1, stdout.log.2, etc.
```

**Option B: External Log Rotation (LogRotate for Windows)**

```powershell
# Install via Chocolatey
choco install logrotate-win -y

# Create rotation config: C:\TaskMan-v2\logrotate.conf
@"
C:\TaskMan-v2\logs\*.log {
    daily
    rotate 7
    size 10M
    compress
    delaycompress
    notifempty
    missingok
    create 0644 TaskManService TaskManService
}
"@ | Set-Content "C:\TaskMan-v2\logrotate.conf"

# Schedule via Task Scheduler
$Action = New-ScheduledTaskAction -Execute "C:\ProgramData\chocolatey\bin\logrotate.exe" `
    -Argument "C:\TaskMan-v2\logrotate.conf"
$Trigger = New-ScheduledTaskTrigger -Daily -At "3:00AM"
Register-ScheduledTask -TaskName "TaskManAPI-LogRotate" -Action $Action -Trigger $Trigger
```

**Option C: Python-based Rotation (RotatingFileHandler)**

```python
# In logging.json configuration
{
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "C:\\TaskMan-v2\\logs\\api.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 7,  # Keep 7 days
            "formatter": "json"
        }
    }
}
```

### 4.3 Health Check Implementation for Windows Services

**PowerShell Health Check Script:**

```powershell
# C:\TaskMan-v2\scripts\health-check.ps1
$HealthEndpoint = "http://localhost:3001/health"
$Timeout = 10  # seconds
$LogFile = "C:\TaskMan-v2\logs\health-check.log"

try {
    $Response = Invoke-RestMethod -Uri $HealthEndpoint -TimeoutSec $Timeout -ErrorAction Stop

    if ($Response.status -eq "healthy") {
        $Message = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - HEALTHY - Database: $($Response.database.connected)"
        Add-Content -Path $LogFile -Value $Message
        exit 0  # Success
    } else {
        $Message = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - DEGRADED - Status: $($Response.status)"
        Add-Content -Path $LogFile -Value $Message
        exit 1  # Warning
    }
} catch {
    $Message = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - FAILED - Error: $($_.Exception.Message)"
    Add-Content -Path $LogFile -Value $Message

    # Restart service on 3 consecutive failures
    $FailureCount = (Get-Content $LogFile | Select-String "FAILED" | Select-Object -Last 3).Count
    if ($FailureCount -eq 3) {
        Restart-Service TaskManAPI
        Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Service restarted due to failures"
    }

    exit 2  # Critical
}
```

**Schedule Health Checks:**

```powershell
# Every 5 minutes
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument `
    "-NoProfile -File C:\TaskMan-v2\scripts\health-check.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "TaskManAPI-HealthCheck" -Action $Action -Trigger $Trigger
```

### 4.4 Alerting Options

**Email Alerts via PowerShell:**

```powershell
# C:\TaskMan-v2\scripts\send-alert.ps1
param(
    [string]$Subject,
    [string]$Body
)

$SmtpServer = "smtp.gmail.com"
$SmtpPort = 587
$SmtpUsername = "alerts@yourdomain.com"
$SmtpPassword = ConvertTo-SecureString "app-password" -AsPlainText -Force
$Credential = New-Object System.Management.Automation.PSCredential($SmtpUsername, $SmtpPassword)

Send-MailMessage `
    -From "alerts@yourdomain.com" `
    -To "admin@yourdomain.com" `
    -Subject "[TaskManAPI] $Subject" `
    -Body $Body `
    -SmtpServer $SmtpServer `
    -Port $SmtpPort `
    -UseSsl `
    -Credential $Credential
```

**Integrate with Health Check:**

```powershell
# Modify health-check.ps1 to send alerts
if ($FailureCount -eq 3) {
    & "C:\TaskMan-v2\scripts\send-alert.ps1" `
        -Subject "Service Failure - Auto Restart" `
        -Body "TaskManAPI failed health checks 3 times. Service restarted at $(Get-Date)."
}
```

---

## 5. Comparison with Alternatives

### 5.1 NSSM vs pywin32 (win32serviceutil)

| Feature | NSSM | pywin32 (win32serviceutil) |
|---------|------|---------------------------|
| **Setup Complexity** | ⭐⭐⭐⭐⭐ Simple (no code changes) | ⭐⭐ Requires service wrapper code |
| **Graceful Shutdown** | ✅ Built-in signal handling | ⚠️ Manual signal handling required |
| **Log Rotation** | ✅ Built-in | ❌ Manual implementation |
| **Auto-Restart** | ✅ Configurable | ⚠️ Requires custom logic |
| **Environment Variables** | ✅ Easy configuration | ⚠️ Requires registry manipulation |
| **Debugging** | ⭐⭐⭐⭐⭐ Logs to files | ⭐⭐⭐ Requires debugger |
| **Maintenance** | ✅ Single exe, no dependencies | ⚠️ Requires pywin32 package updates |

**pywin32 Example (for comparison):**

```python
# servicemanager.py - required for pywin32 approach
import win32serviceutil
import win32service
import servicemanager
import uvicorn

class TaskManAPIService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TaskManAPI"
    _svc_display_name_ = "TaskMan-v2 Backend API"

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        config = uvicorn.Config("main:app", host="0.0.0.0", port=3001)
        server = uvicorn.Server(config)
        server.run()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # Graceful shutdown logic here
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TaskManAPIService)
```

**Verdict**: NSSM wins for simplicity and production readiness.

### 5.2 NSSM vs WinSW

| Feature | NSSM | WinSW |
|---------|------|-------|
| **Configuration** | ⭐⭐⭐⭐⭐ CLI-based | ⭐⭐⭐ XML config files |
| **Maturity** | ⭐⭐⭐⭐⭐ Since 2003 | ⭐⭐⭐⭐ Since 2008 |
| **Documentation** | ⭐⭐⭐⭐ Extensive | ⭐⭐⭐ Good |
| **Signal Handling** | ✅ Multiple methods | ✅ Configurable |
| **Log Rotation** | ✅ Built-in | ✅ Built-in |
| **Download Size** | 140KB | 800KB |
| **GitHub Stars** | 12k+ | 9k+ |

**WinSW Example (XML config):**

```xml
<!-- taskman-api.xml -->
<service>
  <id>TaskManAPI</id>
  <name>TaskMan-v2 Backend API</name>
  <description>FastAPI backend for TaskMan-v2</description>
  <executable>C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe</executable>
  <arguments>-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4</arguments>
  <workingdirectory>C:\TaskMan-v2\backend-api</workingdirectory>
  <log mode="roll-by-size">
    <sizeThreshold>10240</sizeThreshold>
    <keepFiles>8</keepFiles>
  </log>
  <onfailure action="restart" delay="10 sec"/>
</service>
```

**Verdict**: NSSM and WinSW are comparable; NSSM preferred for CLI-based workflows.

### 5.3 NSSM vs Docker Desktop

| Feature | NSSM | Docker Desktop (Windows) |
|---------|------|--------------------------|
| **Resource Overhead** | ⭐⭐⭐⭐⭐ Minimal (native) | ⭐⭐ High (VM + WSL2) |
| **Startup Time** | ⭐⭐⭐⭐⭐ <5 seconds | ⭐⭐ 30-60 seconds |
| **Windows Integration** | ⭐⭐⭐⭐⭐ Native services | ⭐⭐⭐ Via WSL2 |
| **Licensing** | ✅ Free, open source | ⚠️ Paid for business (>250 employees) |
| **Complexity** | ⭐⭐⭐⭐ Simple | ⭐⭐ Requires Docker knowledge |
| **Portability** | ⚠️ Windows-only | ⭐⭐⭐⭐⭐ Cross-platform |

**When to Choose NSSM over Docker:**
- Windows Server environments without Hyper-V
- Lightweight deployments (<100 requests/sec)
- Existing Windows infrastructure teams
- License cost constraints
- Direct Windows Event Log integration required

**When to Choose Docker:**
- Multi-cloud deployments (AWS ECS, Azure ACI)
- Microservices architecture
- Development/production parity requirements
- Kubernetes orchestration planned

---

## 6. Complete Deployment Example

### 6.1 Pre-Deployment Checklist

```powershell
# 1. Verify Python installation
python --version  # Should be Python 3.11+

# 2. Create deployment directory
New-Item -ItemType Directory -Path "C:\TaskMan-v2\backend-api" -Force

# 3. Copy application files
Copy-Item -Recurse "C:\Dev\TaskMan-v2\backend-api\*" "C:\TaskMan-v2\backend-api\"

# 4. Create virtual environment
cd C:\TaskMan-v2\backend-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 5. Install dependencies (using uv for speed)
pip install uv
uv sync

# 6. Create .env file
@"
ENVIRONMENT=production
DATABASE_URL=postgresql://taskman:SecurePassword123@localhost:5432/taskman_v2
API_PORT=3001
LOG_LEVEL=INFO
"@ | Set-Content ".env"

# 7. Test application manually
python -m uvicorn main:app --host 0.0.0.0 --port 3001
# Open http://localhost:3001/health in browser - should return {"status": "healthy"}
# Press Ctrl+C to stop
```

### 6.2 NSSM Installation and Service Setup

```powershell
# Download NSSM
$NssmVersion = "2.24"
$NssmUrl = "https://nssm.cc/release/nssm-$NssmVersion.zip"
$DownloadPath = "$env:TEMP\nssm.zip"
$ExtractPath = "C:\Program Files\nssm"

Invoke-WebRequest -Uri $NssmUrl -OutFile $DownloadPath
Expand-Archive -Path $DownloadPath -DestinationPath $ExtractPath -Force

# Add to PATH
$env:Path += ";$ExtractPath\nssm-$NssmVersion\win64"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# Install service
nssm install TaskManAPI "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe" `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4"

# Configure service
nssm set TaskManAPI AppDirectory "C:\TaskMan-v2\backend-api"
nssm set TaskManAPI DisplayName "TaskMan-v2 Backend API"
nssm set TaskManAPI Description "FastAPI backend for TaskMan-v2 task management system"
nssm set TaskManAPI Start SERVICE_DELAYED_AUTO_START

# Environment variables
nssm set TaskManAPI AppEnvironmentExtra `
    "ENVIRONMENT=production" `
    "PYTHONUNBUFFERED=1"

# Logging
New-Item -ItemType Directory -Path "C:\TaskMan-v2\logs" -Force
nssm set TaskManAPI AppStdout "C:\TaskMan-v2\logs\stdout.log"
nssm set TaskManAPI AppStderr "C:\TaskMan-v2\logs\stderr.log"
nssm set TaskManAPI AppRotateFiles 1
nssm set TaskManAPI AppRotateOnline 1
nssm set TaskManAPI AppRotateSeconds 86400
nssm set TaskManAPI AppRotateBytes 10485760

# Graceful shutdown
nssm set TaskManAPI AppStopMethodConsole 30000
nssm set TaskManAPI AppStopMethodWindow 15000
nssm set TaskManAPI AppKill 1

# Auto-restart on failure
nssm set TaskManAPI AppThrottle 30000
nssm set TaskManAPI AppExit Default Restart
nssm set TaskManAPI AppRestartDelay 5000

# Service account (use custom account in production)
# nssm set TaskManAPI ObjectName ".\TaskManService" "ComplexPassword123!"

# Dependencies (after PostgreSQL service is installed)
nssm set TaskManAPI DependOnService PostgreSQL15

# Verify configuration
nssm dump TaskManAPI
```

### 6.3 Start and Verify Service

```powershell
# Start service
Start-Service TaskManAPI

# Check service status
Get-Service TaskManAPI
# Status should be "Running"

# Verify process
Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:3001/health" | ConvertTo-Json -Depth 3

# Check logs
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Tail 20

# Verify startup in Event Viewer
Get-EventLog -LogName Application -Source TaskManAPI -Newest 5 |
    Format-Table TimeGenerated, EntryType, Message -AutoSize
```

### 6.4 Post-Deployment Configuration

```powershell
# 1. Configure Windows Firewall
New-NetFirewallRule -DisplayName "TaskMan API" -Direction Inbound -LocalPort 3001 -Protocol TCP -Action Allow

# 2. Set up scheduled tasks
# - Health checks (every 5 minutes)
# - Memory monitoring (every 5 minutes)
# - Database backups (daily at 2 AM)
# - Log rotation (daily at 3 AM)
# See sections 4.3 and 4.4 for scripts

# 3. Enable Windows Event Log source
New-EventLog -LogName Application -Source TaskManAPI

# 4. Configure PostgreSQL connection pooling
# Edit C:\TaskMan-v2\backend-api\db\session.py
# Set pool_size based on worker count (already configured in section 3.2)

# 5. Test graceful shutdown
Restart-Service TaskManAPI
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Tail 20
# Should see "session_summary" and "api_shutdown" events

# 6. Performance baseline
Invoke-WebRequest -Uri "http://localhost:3001/health" -UseBasicParsing
# Measure-Command { Invoke-WebRequest -Uri "http://localhost:3001/health" }
```

---

## 7. Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Service Starts but API Unreachable

**Symptoms:**
- Service status: Running
- No process visible in Task Manager
- Health endpoint returns 404 or connection refused

**Diagnosis:**

```powershell
# Check NSSM service status
nssm status TaskManAPI

# Check application logs
Get-Content "C:\TaskMan-v2\logs\stderr.log" -Tail 50

# Verify Python process
Get-Process python -FileVersionInfo | Where-Object { $_.FileName -like "*TaskMan-v2*" }
```

**Common Causes:**
1. **Incorrect Python path**: `Application` points to global Python instead of venv
2. **Missing dependencies**: Venv not properly configured
3. **Port conflict**: Another application using port 3001

**Solutions:**

```powershell
# 1. Fix Python path
nssm set TaskManAPI Application "C:\TaskMan-v2\backend-api\.venv\Scripts\python.exe"

# 2. Reinstall venv dependencies
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\Activate.ps1
uv sync

# 3. Check port availability
Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
# If occupied, change port in .env and NSSM arguments
```

#### Issue 2: Database Connection Failures

**Symptoms:**
- Health endpoint returns `"database": {"connected": false}`
- Logs show `asyncpg.exceptions.CannotConnectNowError`

**Diagnosis:**

```powershell
# Test PostgreSQL connectivity
psql -h localhost -p 5432 -U taskman -d taskman_v2 -c "SELECT 1;"

# Check PostgreSQL service
Get-Service PostgreSQL15

# Verify database exists
psql -U postgres -c "\l" | Select-String "taskman_v2"
```

**Solutions:**

```powershell
# 1. Ensure PostgreSQL service is running
Start-Service PostgreSQL15

# 2. Verify DATABASE_URL in .env
$EnvFile = Get-Content "C:\TaskMan-v2\backend-api\.env"
$EnvFile | Select-String "DATABASE_URL"

# 3. Test connection string
$env:DATABASE_URL = "postgresql://taskman:password@localhost:5432/taskman_v2"
cd C:\TaskMan-v2\backend-api
python -c "from db.session import check_db_health; import asyncio; print(asyncio.run(check_db_health()))"

# 4. Check pg_hba.conf (PostgreSQL auth config)
# C:\Program Files\PostgreSQL\15\data\pg_hba.conf
# Ensure line exists: host all all 127.0.0.1/32 md5
```

#### Issue 3: Service Stops After Few Hours

**Symptoms:**
- Service runs initially but stops after 2-6 hours
- Event Viewer shows "Service terminated unexpectedly"

**Diagnosis:**

```powershell
# Check Windows Event Logs
Get-EventLog -LogName Application -Source TaskManAPI -After (Get-Date).AddHours(-24) |
    Where-Object { $_.EntryType -eq "Error" } |
    Format-Table TimeGenerated, Message -AutoSize

# Check for memory issues
Get-Content "C:\TaskMan-v2\logs\memory-monitor.log" -Tail 20

# Check for Python crashes
Get-Content "C:\TaskMan-v2\logs\stderr.log" | Select-String "Traceback"
```

**Common Causes:**
1. **Memory leak**: Python process exceeds available memory
2. **Database connection exhaustion**: Pool size too small
3. **Unhandled exceptions**: Application crashes without recovery

**Solutions:**

```powershell
# 1. Increase memory limit or implement monitoring
nssm set TaskManAPI AppThrottle 30000
# Set up memory monitor (see section 2.4)

# 2. Increase database pool size
# Edit db/session.py:
# pool_size=20, max_overflow=40

# 3. Add global exception handler (already in main.py)
# Ensure all async endpoints have try/except blocks

# 4. Enable automatic restart on failure
nssm set TaskManAPI AppExit Default Restart
nssm set TaskManAPI AppRestartDelay 5000
```

#### Issue 4: Graceful Shutdown Not Working

**Symptoms:**
- Service stop takes >60 seconds
- Logs missing `session_summary` or `api_shutdown` events
- Database connections left open

**Diagnosis:**

```powershell
# Check shutdown sequence
nssm get TaskManAPI AppStopMethodConsole
nssm get TaskManAPI AppStopMethodWindow
nssm get TaskManAPI AppKill

# Test manual stop
Stop-Service TaskManAPI -Verbose
# Monitor logs during stop
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Wait
```

**Solutions:**

```powershell
# 1. Increase shutdown timeout
nssm set TaskManAPI AppStopMethodConsole 60000  # 60 seconds
nssm set TaskManAPI AppStopMethodWindow 30000  # 30 seconds

# 2. Verify uvicorn shutdown handler
# Ensure main.py lifespan function has yield statement (already implemented)

# 3. Test shutdown directly
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 0.0.0.0 --port 3001
# Press Ctrl+C - should see clean shutdown logs
```

#### Issue 5: High CPU Usage

**Symptoms:**
- Python process consuming >80% CPU continuously
- API response times degraded
- Server unresponsive

**Diagnosis:**

```powershell
# Monitor CPU usage
Get-Counter -Counter "\Process(python*)\% Processor Time" -Continuous

# Check worker count
nssm get TaskManAPI AppParameters | Select-String "workers"

# Profile with py-spy (install separately)
pip install py-spy
py-spy top --pid (Get-Process python | Where-Object { $_.Path -like "*TaskMan-v2*" }).Id
```

**Solutions:**

```powershell
# 1. Reduce worker count if over-allocated
$CpuCount = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
$WorkerCount = [Math]::Max(2, [Math]::Floor($CpuCount * 0.75))
nssm set TaskManAPI AppParameters `
    "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers $WorkerCount"

# 2. Check for infinite loops in application code
# Review recent code changes

# 3. Enable query timeout in database
# Edit db/session.py connect_args:
# "command_timeout": 30

# 4. Restart service to clear potential deadlocks
Restart-Service TaskManAPI
```

---

## 8. Production Deployment Checklist

### Pre-Production

- [ ] Virtual environment created with all dependencies installed
- [ ] `.env` file configured with production settings
- [ ] PostgreSQL installed and configured as Windows Service
- [ ] Database schema migrated (`alembic upgrade head`)
- [ ] Service account created with minimum required permissions
- [ ] Firewall rules configured for API port (3001)
- [ ] Health check endpoint tested manually
- [ ] Application logs writing to designated directory

### NSSM Configuration

- [ ] NSSM installed to `C:\Program Files\nssm`
- [ ] Service installed with correct Python venv path
- [ ] Working directory set to application root
- [ ] Environment variables configured (or using .env file)
- [ ] Log rotation enabled (daily or 10MB size limit)
- [ ] Graceful shutdown timeouts configured (30s console, 15s window)
- [ ] Auto-restart on failure enabled
- [ ] Service dependencies set (PostgreSQL)
- [ ] Delayed auto-start configured

### Monitoring

- [ ] Windows Event Log source registered (`New-EventLog -Source TaskManAPI`)
- [ ] Health check scheduled task configured (5-minute interval)
- [ ] Memory monitoring scheduled task configured
- [ ] Email alerting configured for critical failures
- [ ] Log aggregation solution deployed (e.g., Splunk, ELK)

### Database

- [ ] PostgreSQL connection pooling configured (`pool_size=10, max_overflow=20`)
- [ ] Database backup scheduled task configured (daily at 2 AM)
- [ ] Backup retention policy set (7 days minimum)
- [ ] Database restore procedure tested
- [ ] PostgreSQL autovacuum enabled
- [ ] Slow query logging enabled (`log_min_duration_statement = 1000`)

### Security

- [ ] `.env` file permissions restricted (service account read-only)
- [ ] Database password uses strong credentials (16+ characters)
- [ ] Service account has minimum required permissions
- [ ] HTTPS configured (reverse proxy or native TLS)
- [ ] API authentication implemented (if applicable)
- [ ] Security audit completed (Bandit, safety checks)

### Documentation

- [ ] Deployment runbook documented
- [ ] Troubleshooting guide accessible to operations team
- [ ] Rollback procedure documented
- [ ] Service restart procedure documented
- [ ] Emergency contact list created

### Post-Deployment

- [ ] Service started and verified running
- [ ] Health endpoint accessible externally
- [ ] Database connectivity verified
- [ ] Log files being written and rotated
- [ ] Performance baseline captured
- [ ] Monitoring dashboards configured
- [ ] 24-hour burn-in period completed
- [ ] Load testing performed

---

## Appendix A: Quick Reference Commands

### Service Management

```powershell
# Install service
nssm install TaskManAPI "C:\Path\To\.venv\Scripts\python.exe" "-m uvicorn main:app --host 0.0.0.0 --port 3001"

# Start/Stop/Restart
Start-Service TaskManAPI
Stop-Service TaskManAPI
Restart-Service TaskManAPI

# Check status
Get-Service TaskManAPI
nssm status TaskManAPI

# View configuration
nssm dump TaskManAPI

# Edit service (GUI)
nssm edit TaskManAPI

# Remove service
nssm remove TaskManAPI confirm
```

### Logging

```powershell
# Tail logs
Get-Content "C:\TaskMan-v2\logs\stdout.log" -Wait -Tail 20

# View last 50 lines
Get-Content "C:\TaskMan-v2\logs\stderr.log" -Tail 50

# Search logs for errors
Select-String -Path "C:\TaskMan-v2\logs\*.log" -Pattern "error|exception" -CaseSensitive:$false

# View Event Logs
Get-EventLog -LogName Application -Source TaskManAPI -Newest 10
```

### Database

```powershell
# Connect to database
psql -U taskman -d taskman_v2

# Run migrations
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\Activate.ps1
alembic upgrade head

# Backup database
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -F c -f backup.sql taskman_v2

# Restore database
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d taskman_v2 backup.sql
```

### Diagnostics

```powershell
# Check port
Get-NetTCPConnection -LocalPort 3001

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:3001/health"

# Check Python process
Get-Process | Where-Object { $_.Name -eq "python" -and $_.Path -like "*TaskMan-v2*" }

# View service dependencies
sc.exe qc TaskManAPI
```

---

## Appendix B: Configuration Templates

### NSSM Full Configuration Script

```powershell
# nssm-config.ps1 - Complete NSSM service configuration
param(
    [string]$ServiceName = "TaskManAPI",
    [string]$AppPath = "C:\TaskMan-v2\backend-api",
    [int]$Port = 3001,
    [int]$Workers = 4
)

$PythonExe = "$AppPath\.venv\Scripts\python.exe"
$LogDir = "C:\TaskMan-v2\logs"

# Ensure log directory exists
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Install service
nssm install $ServiceName $PythonExe `
    "-m uvicorn main:app --host 0.0.0.0 --port $Port --workers $Workers"

# Basic configuration
nssm set $ServiceName AppDirectory $AppPath
nssm set $ServiceName DisplayName "TaskMan-v2 Backend API"
nssm set $ServiceName Description "FastAPI backend for TaskMan-v2 task management system"
nssm set $ServiceName Start SERVICE_DELAYED_AUTO_START

# Environment
nssm set $ServiceName AppEnvironmentExtra "ENVIRONMENT=production" "PYTHONUNBUFFERED=1"

# Logging with rotation
nssm set $ServiceName AppStdout "$LogDir\stdout.log"
nssm set $ServiceName AppStderr "$LogDir\stderr.log"
nssm set $ServiceName AppRotateFiles 1
nssm set $ServiceName AppRotateOnline 1
nssm set $ServiceName AppRotateSeconds 86400  # Daily
nssm set $ServiceName AppRotateBytes 10485760  # 10MB

# Graceful shutdown
nssm set $ServiceName AppStopMethodConsole 30000
nssm set $ServiceName AppStopMethodWindow 15000
nssm set $ServiceName AppStopMethodThreads 10000
nssm set $ServiceName AppKill 1

# Auto-restart
nssm set $ServiceName AppThrottle 30000
nssm set $ServiceName AppExit Default Restart
nssm set $ServiceName AppRestartDelay 5000

# Dependencies
nssm set $ServiceName DependOnService PostgreSQL15

Write-Host "Service '$ServiceName' configured successfully."
Write-Host "Start with: Start-Service $ServiceName"
```

### Environment File Template

```bash
# .env - TaskMan-v2 Backend Production Configuration

# Application
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=3001

# Database
DATABASE_URL=postgresql://taskman:CHANGE_THIS_PASSWORD@localhost:5432/taskman_v2

# Logging
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Monitoring
CF_RUN_ID=prod-service

# Security (if authentication enabled)
SECRET_KEY=CHANGE_THIS_SECRET_KEY_MINIMUM_32_CHARACTERS
```

---

## Conclusion

NSSM provides a production-ready solution for deploying TaskMan-v2 FastAPI backend as a Windows Service with:

1. **Minimal complexity**: No application code changes required
2. **Robust lifecycle management**: Graceful shutdown, auto-restart, health monitoring
3. **Enterprise integration**: Windows Event Log, Task Scheduler, Active Directory
4. **Operational simplicity**: PowerShell-based management, familiar Windows tooling

This guide provides a complete reference for deploying, monitoring, and troubleshooting the service in production Windows environments.

---

**Document Maintenance:**
- Last updated: 2025-12-26
- Review frequency: Quarterly
- Owner: DevOps Team
- Related docs: `docs/deployment/`, `docs/operations/`
