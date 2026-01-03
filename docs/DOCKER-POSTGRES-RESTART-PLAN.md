# Docker PostgreSQL Restart & Validation Plan

**Project**: Docker Desktop Recovery & PostgreSQL Container Validation
**Complexity**: MODERATE
**Estimated Effort**: 30-45 minutes (including wait times)
**Risk Level**: MEDIUM
**Created**: 2025-12-29

---

## Executive Summary

**Objective**: Restart Docker Desktop on Windows and validate that the PostgreSQL container (taskman_v2) is running and accessible on localhost:5433.

**Key Challenge**: Docker daemon may be offline, requiring multi-method restart approach with progressive escalation.

**Success Criteria**:
- ✅ Docker Desktop running and responsive
- ✅ PostgreSQL container running on localhost:5433
- ✅ Database `taskman_v2` accessible with credentials contextforge/contextforge
- ✅ Container passes health checks

---

## Requirements Summary

### Explicit Requirements
- [REQ-1] Restart Docker Desktop on Windows
- [REQ-2] Validate PostgreSQL container on localhost:5433
- [REQ-3] Confirm database `taskman_v2` is accessible
- [REQ-4] Use credentials: contextforge/contextforge
- [REQ-5] Leverage existing restart script at `scripts/Restart-Docker.ps1`

### Implicit Requirements
- [IMP-1] Container data must persist through restart
- [IMP-2] No data corruption or loss
- [IMP-3] Minimal downtime
- [IMP-4] Full diagnostic logging for troubleshooting

### Constraints
- [CON-1] Windows environment only
- [CON-2] Docker daemon may be completely offline
- [CON-3] Must use PowerShell 7.0+
- [CON-4] May require Administrator privileges for service operations

### Success Criteria
- [SC-1] `docker ps` command succeeds
- [SC-2] PostgreSQL container visible in `docker ps` output
- [SC-3] Port 5433 is actively listening
- [SC-4] Database connection succeeds with psql/PowerShell
- [SC-5] Health check returns "healthy" status

---

## Work Breakdown Structure

### Phase 1: Pre-Flight Assessment (5-10 minutes)
**Duration**: 5-10 minutes
**Owner**: Operator
**Objective**: Understand current system state and identify failure mode

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 1.1 | Check Docker Desktop process status | 2 min | - |
| 1.2 | Attempt basic Docker command (`docker ps`) | 1 min | - |
| 1.3 | Check Docker Windows services | 2 min | - |
| 1.4 | Identify port 5433 listeners (if any) | 2 min | - |
| 1.5 | Review recent Docker/container logs | 3 min | - |

**Deliverables**:
- [ ] Current state classification (Offline / Partial / Degraded)
- [ ] List of running/stopped Docker processes
- [ ] Service status report
- [ ] Initial diagnostics logged

**Commands**:
```powershell
# 1.1 - Check Docker processes
Get-Process -Name "Docker Desktop","com.docker.service","dockerd" -ErrorAction SilentlyContinue |
    Format-Table Name, Id, CPU, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet/1MB,2)}}

# 1.2 - Test Docker CLI
docker ps 2>&1 | Out-String

# 1.3 - Check Windows services
Get-Service -Name "com.docker.service","docker" -ErrorAction SilentlyContinue |
    Format-Table Name, DisplayName, Status, StartType

# 1.4 - Check port 5433
Get-NetTCPConnection -LocalPort 5433 -ErrorAction SilentlyContinue |
    Format-Table LocalAddress, LocalPort, State, OwningProcess

# 1.5 - Recent Docker Desktop logs (if accessible)
# Location: %LOCALAPPDATA%\Docker\log.txt
$logPath = "$env:LOCALAPPDATA\Docker\log.txt"
if (Test-Path $logPath) {
    Get-Content $logPath -Tail 50
}
```

**Expected Outcomes**:
- **Best Case**: Docker running but container stopped (proceed to Phase 3)
- **Likely Case**: Docker daemon offline (proceed to Phase 2)
- **Worst Case**: Docker corrupted/unresponsive (Phase 2 Force method)

---

### Phase 2: Docker Desktop Restart (10-15 minutes)
**Duration**: 10-15 minutes (including health check wait time)
**Owner**: Operator
**Objective**: Restore Docker Desktop to fully operational state

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 2.1 | Execute Graceful restart method | 5 min | 1.5 |
| 2.2 | Monitor restart progress | 3 min | 2.1 |
| 2.3 | Verify Docker daemon health | 2 min | 2.2 |
| 2.4 | FALLBACK: Force restart if graceful fails | 5 min | 2.3 |
| 2.5 | ESCALATION: Service restart (Admin) | 5 min | 2.4 |

**Deliverables**:
- [ ] Docker Desktop running and responsive
- [ ] `docker ps` command succeeds
- [ ] Restart method used documented
- [ ] Restart logs captured

#### Primary Method: Graceful Restart
```powershell
# Execute graceful restart with 90-second health check
.\scripts\Restart-Docker.ps1 -Method Graceful -WaitForHealthy 90 -Verbose

# Expected log location:
# logs\docker-restart-YYYYMMDD-HHmmss.log
```

**Success Indicators**:
- ✅ Log shows "Docker is healthy and ready!"
- ✅ Log shows "✅ Docker is responding to commands"
- ✅ Exit code 0

**Failure Indicators**:
- ❌ "Docker did not become healthy within X seconds"
- ❌ Exit code 1
- ❌ Processes not starting

#### Fallback 1: Force Restart
```powershell
# If graceful fails, escalate to force kill
.\scripts\Restart-Docker.ps1 -Method Force -WaitForHealthy 90 -Verbose
```

**When to Use**:
- Graceful restart times out
- Docker processes are hung/unresponsive
- Service is in "Starting" state indefinitely

#### Fallback 2: Service Restart (Requires Admin)
```powershell
# Run PowerShell as Administrator
Start-Process pwsh -Verb RunAs

# Then execute:
.\scripts\Restart-Docker.ps1 -Method Service -WaitForHealthy 90 -Verbose
```

**When to Use**:
- Force restart fails
- Docker service shows "Stopped" and won't start
- Windows service issues suspected

#### Diagnostic Mode (Optional - Use for Troubleshooting)
```powershell
# Full diagnostic with pre/post comparisons
.\scripts\Restart-Docker.ps1 -Method Diagnostic -WaitForHealthy 120 -Verbose
```

**Provides**:
- Docker version info
- Process details with CPU usage
- Service status before/after
- Container inventory before/after
- Specific PostgreSQL container check (port 5433)

**Expected Outcomes**:
- **Success**: Docker daemon healthy, CLI responsive
- **Partial**: Docker running but slow/degraded (proceed with monitoring)
- **Failure**: All methods exhausted (escalate to Docker Desktop reinstall)

---

### Phase 3: Container Discovery & Validation (5 minutes)
**Duration**: 5 minutes
**Owner**: Operator
**Objective**: Locate and validate PostgreSQL container configuration

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 3.1 | List all containers (running + stopped) | 1 min | 2.3 |
| 3.2 | Identify PostgreSQL container name | 2 min | 3.1 |
| 3.3 | Inspect container configuration | 2 min | 3.2 |
| 3.4 | Verify port mapping (5433 → 5432) | 1 min | 3.3 |

**Deliverables**:
- [ ] PostgreSQL container identified
- [ ] Container name documented
- [ ] Port mapping confirmed
- [ ] Container state assessed (running/stopped/missing)

**Commands**:
```powershell
# 3.1 - List all containers
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 3.2 - Find PostgreSQL containers specifically
docker ps -a --filter "ancestor=postgres" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Alternative: Search by port 5433
docker ps -a --filter "publish=5433" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 3.3 - Inspect container (replace CONTAINER_NAME)
docker inspect CONTAINER_NAME | ConvertFrom-Json | Select-Object Name, State, Config, NetworkSettings

# 3.4 - Verify port mapping
docker port CONTAINER_NAME 5432
# Expected output: 0.0.0.0:5433
```

**Container Name Candidates** (based on codebase analysis):
- `taskman-postgres` (TaskMan-v2 docker-compose.taskman-v2.yml - **Most Likely**)
- `qse-test-db` (docker-compose.test.yml)
- `task-manager-postgres` (vs-code-task-manager)
- `contextforge-postgres` (devcontainer)

**Expected Outcomes**:
- **Best Case**: Container running, port 5433 mapped correctly
- **Likely Case**: Container stopped but exists (proceed to Phase 4)
- **Problem Case**: Container missing (proceed to Phase 5)

---

### Phase 4: Container Startup & Health Check (5 minutes)
**Duration**: 5 minutes
**Owner**: Operator
**Objective**: Start PostgreSQL container and verify health

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 4.1 | Start PostgreSQL container | 1 min | 3.2 |
| 4.2 | Monitor container startup logs | 2 min | 4.1 |
| 4.3 | Verify container health status | 2 min | 4.2 |
| 4.4 | Confirm port 5433 listening | 1 min | 4.3 |

**Deliverables**:
- [ ] Container started successfully
- [ ] Health check passing
- [ ] Port 5433 listening
- [ ] No error logs

**Commands**:
```powershell
# 4.1 - Start container (replace CONTAINER_NAME)
docker start CONTAINER_NAME

# 4.2 - Watch startup logs (Ctrl+C to exit)
docker logs -f CONTAINER_NAME

# Look for successful indicators:
# - "database system is ready to accept connections"
# - "PostgreSQL init process complete"

# 4.3 - Check health status
docker ps --filter "name=CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}"
# Look for "(healthy)" in status

# Alternative: Inspect health directly
docker inspect --format='{{json .State.Health}}' CONTAINER_NAME | ConvertFrom-Json

# 4.4 - Verify port listening
Test-NetConnection -ComputerName localhost -Port 5433
# Expected: TcpTestSucceeded : True
```

**Health Check Indicators**:
```
✅ HEALTHY:
  - Status: "healthy" in docker ps
  - Logs: "ready to accept connections"
  - Port: 5433 responding

⚠️ STARTING:
  - Status: "health: starting"
  - Wait 30-60 seconds, recheck

❌ UNHEALTHY:
  - Status: "unhealthy"
  - Logs show errors
  - Proceed to troubleshooting
```

**Expected Outcomes**:
- **Success**: Container healthy within 60 seconds
- **Delayed**: Container starting, wait longer
- **Failure**: Container crashes or unhealthy (see Phase 6)

---

### Phase 5: Database Connection Validation (5-10 minutes)
**Duration**: 5-10 minutes
**Owner**: Operator
**Objective**: Confirm database connectivity and credentials

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 5.1 | Test connection with psql (if available) | 2 min | 4.3 |
| 5.2 | Test connection with PowerShell | 3 min | 4.3 |
| 5.3 | Verify database `taskman_v2` exists | 2 min | 5.1 or 5.2 |
| 5.4 | Test table access (basic query) | 2 min | 5.3 |
| 5.5 | Document connection string | 1 min | 5.4 |

**Deliverables**:
- [ ] Database connection successful
- [ ] Database `taskman_v2` confirmed
- [ ] Basic query executes
- [ ] Connection string validated

#### Method 1: psql (Recommended)
```powershell
# Install psql if not available (optional)
# winget install PostgreSQL.PostgreSQL

# Test connection
psql "postgresql://contextforge:contextforge@localhost:5433/taskman_v2" -c "\conninfo"

# Expected output:
# You are connected to database "taskman_v2" as user "contextforge" on host "localhost" (address "127.0.0.1") at port "5433".

# Verify database
psql "postgresql://contextforge:contextforge@localhost:5433/taskman_v2" -c "\l"

# Basic query
psql "postgresql://contextforge:contextforge@localhost:5433/taskman_v2" -c "SELECT version();"
```

#### Method 2: PowerShell with Npgsql (if psql unavailable)
```powershell
# Install Npgsql if needed
# Install-Module -Name Npgsql -Scope CurrentUser

# Test connection
$connectionString = "Host=localhost;Port=5433;Database=taskman_v2;Username=contextforge;Password=contextforge"
try {
    $conn = New-Object Npgsql.NpgsqlConnection($connectionString)
    $conn.Open()
    Write-Host "✅ Connection successful!" -ForegroundColor Green
    Write-Host "Server version: $($conn.ServerVersion)"

    # Test query
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT current_database(), current_user, version()"
    $reader = $cmd.ExecuteReader()
    while ($reader.Read()) {
        Write-Host "Database: $($reader[0])"
        Write-Host "User: $($reader[1])"
        Write-Host "Version: $($reader[2])"
    }
    $reader.Close()
    $conn.Close()
} catch {
    Write-Host "❌ Connection failed: $_" -ForegroundColor Red
}
```

#### Method 3: Docker exec (Fallback)
```powershell
# Execute psql inside the container
docker exec CONTAINER_NAME psql -U contextforge -d taskman_v2 -c "SELECT current_database(), current_user;"

# List databases
docker exec CONTAINER_NAME psql -U contextforge -c "\l"

# Check if taskman_v2 exists
docker exec CONTAINER_NAME psql -U contextforge -c "\l taskman_v2"
```

**Expected Outcomes**:
- **Success**: All connection methods work, queries execute
- **Partial**: Connection works but slow/intermittent
- **Failure**: Connection refused (check Phase 6)

---

### Phase 6: Troubleshooting & Recovery (If Issues Occur)
**Duration**: 10-20 minutes (varies by issue)
**Owner**: Operator
**Objective**: Diagnose and resolve common failure modes

| Issue | Diagnostic | Resolution | Estimate |
|-------|------------|------------|----------|
| Container missing | Check docker-compose files | Recreate from compose | 10 min |
| Health check failing | Review container logs | Fix config, restart | 5 min |
| Port conflict (5433 in use) | Check port listeners | Stop conflicting process | 5 min |
| Database doesn't exist | List databases | Restore from backup | 15 min |
| Connection refused | Verify pg_hba.conf | Fix auth config | 10 min |

#### Issue 1: Container Missing
```powershell
# Recreate using docker-compose
cd TaskMan-v2
docker-compose -f docker-compose.taskman-v2.yml up -d database

# Verify creation
docker ps -a --filter "name=taskman-postgres"

# NOTE: This compose file maps to port 5434, not 5433!
# If you need port 5433, modify the compose file or use:
docker run -d \
    --name taskman-postgres \
    -e POSTGRES_DB=taskman_v2 \
    -e POSTGRES_USER=contextforge \
    -e POSTGRES_PASSWORD=contextforge \
    -p 5433:5432 \
    -v taskman-postgres-data:/var/lib/postgresql/data \
    postgres:16-alpine
```

#### Issue 2: Health Check Failing
```powershell
# Check detailed logs
docker logs CONTAINER_NAME --tail 100

# Common issues:
# - Permissions on data volume
# - Corrupted data directory
# - Insufficient resources

# Resolution: Remove and recreate with fresh volume
docker stop CONTAINER_NAME
docker rm CONTAINER_NAME
# WARNING: This deletes data!
docker volume rm taskman-postgres-data
# Then recreate (see Issue 1)
```

#### Issue 3: Port 5433 Already in Use
```powershell
# Identify conflicting process
Get-NetTCPConnection -LocalPort 5433 |
    Select-Object -ExpandProperty OwningProcess |
    ForEach-Object { Get-Process -Id $_ }

# Options:
# 1. Stop the conflicting process
# 2. Use different port (e.g., 5434)
# 3. Start container with --publish 5435:5432 (alternative port)
```

#### Issue 4: Database Missing
```powershell
# List databases inside container
docker exec CONTAINER_NAME psql -U contextforge -c "\l"

# If taskman_v2 missing, create it:
docker exec CONTAINER_NAME psql -U contextforge -c "CREATE DATABASE taskman_v2;"

# Restore from backup (if available)
# docker exec -i CONTAINER_NAME psql -U contextforge -d taskman_v2 < backup.sql
```

#### Issue 5: Connection Refused
```powershell
# Check pg_hba.conf inside container
docker exec CONTAINER_NAME cat /var/lib/postgresql/data/pg_hba.conf

# Should contain:
# host all all all md5

# If not, you may need to customize the image or use environment variables
# Most postgres images allow connections by default
```

---

### Phase 7: Final Validation & Documentation (5 minutes)
**Duration**: 5 minutes
**Owner**: Operator
**Objective**: Confirm all success criteria and document state

| Task | Description | Estimate | Dependencies |
|------|-------------|----------|--------------|
| 7.1 | Execute full validation checklist | 3 min | 5.4 |
| 7.2 | Document final configuration | 2 min | 7.1 |
| 7.3 | Create recovery snapshot (optional) | 5 min | 7.2 |

**Deliverables**:
- [ ] All success criteria verified
- [ ] System configuration documented
- [ ] Logs archived
- [ ] Recovery procedures updated

**Full Validation Checklist**:
```powershell
# Run this comprehensive validation script
$validationResults = @()

# 1. Docker daemon
try {
    $dockerVersion = docker version --format '{{.Server.Version}}' 2>$null
    if ($?) {
        $validationResults += "✅ Docker daemon: v$dockerVersion"
    } else {
        $validationResults += "❌ Docker daemon: Not responding"
    }
} catch {
    $validationResults += "❌ Docker daemon: Error - $_"
}

# 2. PostgreSQL container
try {
    $containerStatus = docker ps --filter "publish=5433" --format "{{.Names}} - {{.Status}}"
    if ($containerStatus) {
        $validationResults += "✅ PostgreSQL container: $containerStatus"
    } else {
        $validationResults += "❌ PostgreSQL container: Not found on port 5433"
    }
} catch {
    $validationResults += "❌ PostgreSQL container: Error - $_"
}

# 3. Port 5433 listening
try {
    $portTest = Test-NetConnection -ComputerName localhost -Port 5433 -WarningAction SilentlyContinue
    if ($portTest.TcpTestSucceeded) {
        $validationResults += "✅ Port 5433: Listening"
    } else {
        $validationResults += "❌ Port 5433: Not accessible"
    }
} catch {
    $validationResults += "❌ Port 5433: Error - $_"
}

# 4. Database connection
try {
    $dbTest = docker exec CONTAINER_NAME psql -U contextforge -d taskman_v2 -t -c "SELECT 'Connected' as status" 2>$null
    if ($dbTest -match "Connected") {
        $validationResults += "✅ Database taskman_v2: Accessible"
    } else {
        $validationResults += "❌ Database taskman_v2: Connection failed"
    }
} catch {
    $validationResults += "❌ Database taskman_v2: Error - $_"
}

# 5. Container health
try {
    $health = docker inspect --format='{{.State.Health.Status}}' CONTAINER_NAME 2>$null
    if ($health -eq "healthy") {
        $validationResults += "✅ Health check: Passing"
    } else {
        $validationResults += "⚠️  Health check: $health"
    }
} catch {
    $validationResults += "❌ Health check: Error - $_"
}

# Display results
Write-Host "`n=== VALIDATION RESULTS ===" -ForegroundColor Cyan
$validationResults | ForEach-Object { Write-Host $_ }

# Summary
$passed = ($validationResults | Where-Object { $_ -match "✅" }).Count
$total = $validationResults.Count
Write-Host "`nValidation: $passed/$total checks passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
```

**Configuration Documentation Template**:
```markdown
## PostgreSQL Container Configuration - [DATE]

**Container Name**: [CONTAINER_NAME]
**Image**: postgres:16-alpine
**Status**: Running (healthy)
**Port Mapping**: 5433:5432
**Volume**: taskman-postgres-data

**Database Details**:
- Database: taskman_v2
- User: contextforge
- Password: contextforge
- Connection: postgresql://contextforge:contextforge@localhost:5433/taskman_v2

**Docker Compose**: TaskMan-v2/docker-compose.taskman-v2.yml (NOTE: Uses port 5434)

**Restart Method Used**: [Graceful/Force/Service/Diagnostic]

**Restart Duration**: [X minutes]

**Issues Encountered**: [None / List issues]

**Validation Status**: [X/5 checks passed]
```

---

## Dependency Graph

```mermaid
graph TD
    A[Phase 1: Pre-Flight Assessment] --> B{Docker Status?}
    B -->|Offline| C[Phase 2: Docker Restart]
    B -->|Running| D[Phase 3: Container Discovery]
    C --> E{Restart Success?}
    E -->|Yes| D
    E -->|No| F[Phase 6: Troubleshooting]
    D --> G{Container Exists?}
    G -->|Yes - Running| H[Phase 5: DB Validation]
    G -->|Yes - Stopped| I[Phase 4: Container Startup]
    G -->|No| F
    I --> J{Startup Success?}
    J -->|Yes| H
    J -->|No| F
    H --> K{Connection Success?}
    K -->|Yes| L[Phase 7: Final Validation]
    K -->|No| F
    F --> M{Issue Resolved?}
    M -->|Yes| D
    M -->|No| N[Escalate]
    L --> O[✅ Complete]
```

---

## Risk Register

| ID | Risk | Probability | Impact | Score | Mitigation |
|----|------|-------------|--------|-------|------------|
| R1 | Docker Desktop won't start | Medium | High | 🔴 | Multiple restart methods (Graceful → Force → Service), reinstall as last resort |
| R2 | Container data corrupted | Low | High | 🟡 | Regular backups, volume inspection before removal |
| R3 | Port 5433 conflict | Low | Medium | 🟢 | Port scan first, use alternative port if needed |
| R4 | Database doesn't exist | Medium | Medium | 🟡 | Create database if missing, restore from backup |
| R5 | Network isolation issues | Low | Medium | 🟢 | Docker network inspect, recreate if needed |
| R6 | Insufficient system resources | Low | High | 🟡 | Check available memory/disk before starting |
| R7 | Windows Firewall blocking | Low | Low | 🟢 | Localhost (127.0.0.1) typically exempt |
| R8 | Container image missing | Low | Medium | 🟢 | Pull postgres:16-alpine if needed |

---

## Success Metrics

### Primary Success Criteria (All Required)
- ✅ `docker ps` returns exit code 0
- ✅ PostgreSQL container visible in output
- ✅ `Test-NetConnection -Port 5433` succeeds
- ✅ Database connection with psql/PowerShell succeeds
- ✅ Container health status is "healthy"

### Secondary Success Criteria (Nice to Have)
- ✅ Restart completed in < 15 minutes
- ✅ No data loss
- ✅ All logs captured for audit
- ✅ Container auto-restarts on system reboot
- ✅ Graceful method succeeded (no force required)

### Performance Benchmarks
- Docker restart: < 5 minutes
- Container startup: < 60 seconds
- Database connection: < 3 seconds
- Health check passes: < 30 seconds

---

## Rollback Plan (If Critical Failure)

### Scenario 1: Cannot Start Docker Desktop
```powershell
# Option 1: Restart Docker Desktop service via Windows Services
Get-Service "com.docker.service" | Restart-Service

# Option 2: Reset Docker Desktop to factory defaults
# Warning: This removes all containers, images, volumes
& "C:\Program Files\Docker\Docker\Docker Desktop.exe" --factory-reset

# Option 3: Reinstall Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/
```

### Scenario 2: Container Data Corrupted
```powershell
# Restore from backup (if available)
docker volume create taskman-postgres-data-backup-[DATE]
docker run --rm \
    -v taskman-postgres-data:/source \
    -v taskman-postgres-data-backup-[DATE]:/backup \
    alpine sh -c "cp -a /source/. /backup/"

# Start fresh container with restored volume
docker run -d \
    --name taskman-postgres-restored \
    -v taskman-postgres-data-backup-[DATE]:/var/lib/postgresql/data \
    -p 5433:5432 \
    -e POSTGRES_DB=taskman_v2 \
    -e POSTGRES_USER=contextforge \
    -e POSTGRES_PASSWORD=contextforge \
    postgres:16-alpine
```

### Scenario 3: Cannot Connect to Database
```powershell
# Fallback to alternative database instance
# Check if TaskMan-v2 compose is running on port 5434 instead
Test-NetConnection -Port 5434

# Update connection string to use 5434
$connectionString = "postgresql://contextforge:contextforge@localhost:5434/taskman_v2"

# Or: Start temporary database for emergency use
docker run -d \
    --name postgres-temp \
    -p 5435:5432 \
    -e POSTGRES_DB=taskman_v2 \
    -e POSTGRES_USER=contextforge \
    -e POSTGRES_PASSWORD=contextforge \
    postgres:16-alpine
```

---

## Quick Reference Commands

### Status Checks (Copy-Paste Ready)
```powershell
# Docker daemon
docker version --format 'Server: {{.Server.Version}}'

# Running containers
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# PostgreSQL container specifically
docker ps --filter "publish=5433" --format "{{.Names}} - {{.Status}}"

# Port 5433
Test-NetConnection -ComputerName localhost -Port 5433

# Database connection
psql "postgresql://contextforge:contextforge@localhost:5433/taskman_v2" -c "\conninfo"
```

### Emergency Commands
```powershell
# Quick restart Docker Desktop
.\scripts\Restart-Docker.ps1 -Method Force -WaitForHealthy 60

# Force start container
docker start -a CONTAINER_NAME

# View live logs
docker logs -f CONTAINER_NAME

# Emergency database dump
docker exec CONTAINER_NAME pg_dump -U contextforge taskman_v2 > "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').sql"
```

---

## Execution Summary Template

After completing the plan, document the actual execution:

```markdown
## Execution Log - [DATE TIME]

**Operator**: [Your Name]
**Duration**: [Start Time] → [End Time] ([Total Minutes])

### Phases Completed
- [x] Phase 1: Pre-Flight Assessment
- [x] Phase 2: Docker Restart
- [ ] Phase 3: Container Discovery
- [ ] Phase 4: Container Startup
- [ ] Phase 5: DB Validation
- [ ] Phase 7: Final Validation

### Method Used
- Docker Restart: [Graceful/Force/Service/Diagnostic]
- Container: [Found/Recreated/Restored]

### Issues Encountered
1. [Issue description] → [Resolution]
2. [Issue description] → [Resolution]

### Final Status
- Docker: [✅/❌]
- Container: [✅/❌]
- Database: [✅/❌]
- Validation: [X/5 checks passed]

### Logs
- Restart log: [Path]
- Container log: [Path]
- Validation results: [Path]

### Next Steps
- [ ] [Action item if any issues remain]
- [ ] [Preventive measures]
```

---

## Notes

### Docker Compose Port Confusion ⚠️
**CRITICAL**: The workspace has multiple docker-compose files with different port mappings:
- `TaskMan-v2/docker-compose.taskman-v2.yml` → **Port 5434**
- `docker-compose.test.yml` → **Port 5433**
- `docker-compose.taskman.yml` → **Port 5434**

**Action Required**: Determine which compose file is authoritative. If 5433 is required, either:
1. Use `docker-compose.test.yml` (but it creates `qse-test-db`, not `taskman_v2`)
2. Manually start container on port 5433
3. Modify TaskMan-v2 compose to use 5433 instead of 5434

### Container Name Resolution
If validation shows no container on port 5433:
```powershell
# Check 5434 instead (TaskMan-v2 default)
docker ps --filter "publish=5434"

# Check all PostgreSQL containers
docker ps -a --filter "ancestor=postgres"
```

### Resource Requirements
- **Docker Desktop**: ~2 GB RAM minimum
- **PostgreSQL Container**: ~256 MB RAM minimum
- **Disk Space**: ~500 MB for images + data

---

**Document Version**: 1.0
**Last Updated**: 2025-12-29
**Next Review**: After first execution
