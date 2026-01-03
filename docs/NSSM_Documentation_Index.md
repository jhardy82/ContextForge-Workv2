# NSSM Documentation Index
## Complete Guide to Windows Service Deployment for TaskMan-v2

**Documentation Suite Version**: 1.0
**Generated**: 2025-12-26
**Purpose**: Windows Service deployment using NSSM (Non-Sucking Service Manager)

---

## Documentation Overview

This documentation suite provides comprehensive guidance for deploying TaskMan-v2 FastAPI backend as a production Windows Service using NSSM. All materials are based on research into best practices for Python web applications on Windows Server environments.

---

## Quick Start

**For rapid deployment**:

```powershell
# 1. Review prerequisites (5 minutes)
Get-Content "docs\NSSM_Research_Summary.md" | Select-String -Pattern "Pre-Deployment"

# 2. Run automated deployment (10 minutes)
.\scripts\deploy-windows-service.ps1

# 3. Verify deployment
Invoke-RestMethod http://localhost:3001/health | ConvertTo-Json

# 4. Set up monitoring (5 minutes)
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\TaskMan-v2\scripts\monitor-service-health.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "TaskManAPI-HealthMonitor" -Action $Action -Trigger $Trigger
```

**Total time**: ~20 minutes from zero to production-ready service

---

## Documentation Structure

### 1. Executive Summary

**File**: `docs/NSSM_Research_Summary.md`
**Length**: 18 pages
**Purpose**: High-level overview and key findings

**Best for**:
- Decision makers evaluating NSSM vs alternatives
- Architects designing Windows deployment strategy
- Managers reviewing deployment approach

**Key sections**:
- Research overview and key findings
- NSSM vs pywin32/WinSW/Docker comparison
- Production deployment checklist
- Performance benchmarks
- Recommendations and next steps

**When to read**: Before starting deployment planning

---

### 2. Comprehensive Deployment Guide

**File**: `docs/NSSM_Windows_Service_Deployment.md`
**Length**: 47 pages
**Purpose**: Complete reference for all deployment scenarios

**Best for**:
- DevOps engineers implementing deployment
- System administrators configuring services
- Support teams troubleshooting issues

**Key sections**:
1. NSSM configuration best practices
2. Python application as Windows Service
3. PostgreSQL integration options
4. Monitoring and logging strategies
5. Comparison with alternatives
6. Complete deployment example
7. Troubleshooting guide
8. Appendices (commands, templates)

**When to read**: During deployment implementation and troubleshooting

---

### 3. Quick Reference Guide

**File**: `docs/NSSM_Quick_Reference.md`
**Length**: 20 pages
**Purpose**: Fast command lookup for daily operations

**Best for**:
- Operations teams managing services
- On-call engineers resolving incidents
- Anyone needing quick copy-paste commands

**Key sections**:
- Service management
- Configuration management
- Monitoring and logs
- Health checks
- Performance monitoring
- Database management
- Troubleshooting workflows
- Common issues and solutions

**When to read**: Daily operations and incident response

---

### 4. Deployment Automation Script

**File**: `scripts/deploy-windows-service.ps1`
**Lines**: 400+
**Purpose**: Fully automated service deployment

**Features**:
- Prerequisite validation (Python, venv, main.py)
- NSSM download and installation
- Service creation and configuration
- Log rotation setup
- Graceful shutdown configuration
- Windows Event Log registration
- Firewall rule creation
- Health check validation
- Comprehensive logging

**Usage**:

```powershell
# Basic deployment
.\scripts\deploy-windows-service.ps1

# Custom configuration
.\scripts\deploy-windows-service.ps1 `
    -AppPath "D:\Apps\TaskMan" `
    -Port 8080 `
    -Workers 8 `
    -ServiceAccount ".\TaskManService" `
    -ServicePassword (Read-Host -AsSecureString)

# Output: Detailed deployment log + service status
```

**When to use**: Initial deployment and redeployment scenarios

---

### 5. Health Monitoring Script

**File**: `scripts/monitor-service-health.ps1`
**Lines**: 350+
**Purpose**: Automated service health monitoring and recovery

**Features**:
- Service status check
- Memory usage monitoring
- API health endpoint validation
- Database connectivity check
- State persistence (JSON)
- Auto-restart on consecutive failures
- Email alerting for critical issues
- Detailed logging

**Usage**:

```powershell
# Manual execution
.\scripts\monitor-service-health.ps1

# With email alerts
.\scripts\monitor-service-health.ps1 `
    -EnableEmailAlerts `
    -SmtpServer "smtp.gmail.com" `
    -AlertEmailTo "admin@example.com" `
    -AlertEmailFrom "alerts@example.com"

# Schedule via Task Scheduler (recommended)
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument `
    "-File C:\TaskMan-v2\scripts\monitor-service-health.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "TaskManAPI-HealthMonitor" -Action $Action -Trigger $Trigger
```

**When to use**: Continuous monitoring (scheduled every 5 minutes)

---

## Documentation Map by Role

### DevOps Engineer

**Primary workflow**:

1. Read: `NSSM_Research_Summary.md` (Key Findings section)
2. Execute: `deploy-windows-service.ps1`
3. Review: `NSSM_Windows_Service_Deployment.md` (Section 6: Complete Deployment Example)
4. Configure: `monitor-service-health.ps1` scheduled task
5. Bookmark: `NSSM_Quick_Reference.md` for daily use

**Estimated time**: 2-3 hours for full implementation

---

### System Administrator

**Primary workflow**:

1. Read: `NSSM_Research_Summary.md` (Production Deployment Checklist)
2. Review: `NSSM_Windows_Service_Deployment.md` (Section 1: NSSM Configuration Best Practices)
3. Execute: `deploy-windows-service.ps1` in staging environment
4. Test: Service lifecycle (start, stop, restart, health checks)
5. Monitor: Review logs and Event Viewer integration

**Estimated time**: 4-5 hours including testing

---

### Application Developer

**Primary workflow**:

1. Read: `NSSM_Research_Summary.md` (Section 2: Python Application as Windows Service)
2. Review: `NSSM_Windows_Service_Deployment.md` (Section 2.1: Virtual Environment Activation)
3. Understand: Graceful shutdown handling (lifespan manager)
4. Test: Local deployment with `deploy-windows-service.ps1`
5. Use: `NSSM_Quick_Reference.md` for troubleshooting

**Estimated time**: 2 hours for understanding + testing

---

### Operations/Support Team

**Primary workflow**:

1. Bookmark: `NSSM_Quick_Reference.md` (entire document)
2. Familiarize: Common issues and solutions section
3. Learn: Service management commands (start, stop, restart)
4. Practice: Log monitoring and health checks
5. Reference: `NSSM_Windows_Service_Deployment.md` Section 7 (Troubleshooting Guide)

**Estimated time**: 1 hour for initial training

---

### Manager/Architect

**Primary workflow**:

1. Read: `NSSM_Research_Summary.md` (complete document)
2. Review: Section 5 (Comparison with Alternatives)
3. Evaluate: Performance benchmarks and resource utilization
4. Assess: Production deployment checklist
5. Decide: NSSM vs Docker vs pywin32 based on project constraints

**Estimated time**: 1-2 hours for decision-making

---

## Documentation Usage by Scenario

### Scenario 1: Initial Deployment to Production

**Documents needed**:
1. `NSSM_Research_Summary.md` - Pre-deployment checklist
2. `NSSM_Windows_Service_Deployment.md` - Sections 1-6
3. `deploy-windows-service.ps1` - Automated deployment

**Steps**:
```powershell
# 1. Validate prerequisites
Get-Content docs\NSSM_Research_Summary.md | Select-String "Pre-Deployment" -Context 5

# 2. Run deployment
.\scripts\deploy-windows-service.ps1 -ServiceAccount ".\TaskManService" -ServicePassword (Read-Host -AsSecureString)

# 3. Verify deployment
Invoke-RestMethod http://localhost:3001/health

# 4. Set up monitoring
# (See Section 5 for detailed commands)
```

**Time estimate**: 30-45 minutes

---

### Scenario 2: Service Not Starting

**Documents needed**:
1. `NSSM_Quick_Reference.md` - Troubleshooting section
2. `NSSM_Windows_Service_Deployment.md` - Section 7.1 (Issue 1: Service Starts but API Unreachable)

**Steps**:
```powershell
# 1. Check service status
Get-Service TaskManAPI
nssm status TaskManAPI

# 2. Review error logs
Get-Content C:\TaskMan-v2\logs\stderr.log -Tail 50

# 3. Verify configuration
nssm get TaskManAPI Application
nssm get TaskManAPI AppDirectory

# 4. Test command manually
cd C:\TaskMan-v2\backend-api
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 3001
```

**Time estimate**: 10-20 minutes

---

### Scenario 3: Database Connection Issues

**Documents needed**:
1. `NSSM_Quick_Reference.md` - Database management section
2. `NSSM_Windows_Service_Deployment.md` - Section 7.2 (Issue 2: Database Connection Failures)

**Steps**:
```powershell
# 1. Check PostgreSQL service
Get-Service PostgreSQL*

# 2. Test database connectivity
psql -h localhost -p 5432 -U taskman -d taskman_v2 -c "SELECT 1;"

# 3. Verify DATABASE_URL
Get-Content C:\TaskMan-v2\backend-api\.env | Select-String "DATABASE_URL"

# 4. Check health endpoint
Invoke-RestMethod http://localhost:3001/health | ConvertTo-Json
```

**Time estimate**: 5-15 minutes

---

### Scenario 4: Performance Tuning

**Documents needed**:
1. `NSSM_Research_Summary.md` - Performance benchmarks section
2. `NSSM_Quick_Reference.md` - Performance tuning section

**Steps**:
```powershell
# 1. Determine optimal worker count
$CpuCount = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
$OptimalWorkers = [Math]::Max(2, [Math]::Min($CpuCount - 1, 8))

# 2. Update worker configuration
nssm set TaskManAPI AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 3001 --workers $OptimalWorkers"
Restart-Service TaskManAPI

# 3. Monitor performance
Get-Counter "\Process(python*)\% Processor Time" -SampleInterval 2 -MaxSamples 10
```

**Time estimate**: 15-30 minutes

---

### Scenario 5: Upgrading Application

**Documents needed**:
1. `NSSM_Quick_Reference.md` - Service management section
2. `NSSM_Windows_Service_Deployment.md` - Section 6.4 (Post-Deployment Configuration)

**Steps**:
```powershell
# 1. Stop service
Stop-Service TaskManAPI

# 2. Backup current configuration
nssm dump TaskManAPI | Out-File "C:\TaskMan-v2\backups\nssm-config-$(Get-Date -Format 'yyyyMMdd').txt"

# 3. Update application code
cd C:\TaskMan-v2\backend-api
git pull origin main
.\.venv\Scripts\Activate.ps1
uv sync

# 4. Run migrations
alembic upgrade head

# 5. Start service
Start-Service TaskManAPI

# 6. Verify health
Invoke-RestMethod http://localhost:3001/health
```

**Time estimate**: 10-20 minutes (excluding code changes)

---

## File Locations

```
C:\Users\James\.claude-worktrees\SCCMScripts\silly-elion\
├── docs/
│   ├── NSSM_Documentation_Index.md       (This file)
│   ├── NSSM_Research_Summary.md          (Executive summary)
│   ├── NSSM_Windows_Service_Deployment.md (Complete guide)
│   └── NSSM_Quick_Reference.md           (Quick commands)
└── scripts/
    ├── deploy-windows-service.ps1        (Deployment automation)
    └── monitor-service-health.ps1        (Health monitoring)
```

**Recommended installation location** (production):
```
C:\TaskMan-v2\
├── backend-api\               (Application code)
│   ├── .venv\                (Python virtual environment)
│   ├── main.py               (FastAPI application)
│   └── .env                  (Environment configuration)
├── logs\                      (Service logs)
├── backups\                   (Database backups)
├── scripts\                   (Operational scripts)
│   ├── deploy-windows-service.ps1
│   ├── monitor-service-health.ps1
│   ├── backup-database.ps1
│   └── restore-database.ps1
└── docs\                      (Reference documentation)
    ├── NSSM_Research_Summary.md
    ├── NSSM_Windows_Service_Deployment.md
    └── NSSM_Quick_Reference.md
```

---

## Key Concepts

### NSSM (Non-Sucking Service Manager)

**What it is**: Lightweight Windows service wrapper for console applications
**Why use it**: Zero code changes, robust lifecycle management, native Windows integration
**Alternatives**: pywin32 (code changes required), WinSW (XML config), Docker (overhead)

### Graceful Shutdown

**What it is**: Multi-stage shutdown process allowing application cleanup
**Why important**: Prevents database connection leaks, ensures log completeness
**Implementation**: NSSM sends Ctrl+C → FastAPI lifespan cleanup → Process termination

### Connection Pooling

**What it is**: Reusable database connection cache
**Why important**: Reduces connection overhead, improves performance, prevents exhaustion
**Critical setting**: `pool_pre_ping=True` (detects stale connections)

### Health Monitoring

**What it is**: Automated service health checks with auto-restart
**Why important**: Proactive failure detection, automatic recovery, reduced downtime
**Implementation**: PowerShell scheduled task (every 5 minutes)

---

## Common Pitfalls (Cross-Reference)

| Issue | Documentation Location | Quick Fix |
|-------|------------------------|-----------|
| Service won't start | `NSSM_Quick_Reference.md` - Troubleshooting | Check stderr.log, verify Python path |
| Database connection lost | `NSSM_Windows_Service_Deployment.md` - Section 7.2 | Ensure `pool_pre_ping=True` |
| High memory usage | `NSSM_Quick_Reference.md` - Performance Tuning | Reduce worker count, enable monitoring |
| Logs filling disk | `NSSM_Windows_Service_Deployment.md` - Section 4.2 | Enable NSSM log rotation |
| Service crashes on restart | `NSSM_Windows_Service_Deployment.md` - Section 7.4 | Increase AppStopMethodConsole timeout |

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-26 | Initial documentation suite | ContextForge Research Team |

**Next review**: 2026-03-26 (quarterly)

---

## Support Resources

### Internal Resources

1. **Deployment logs**: `C:\TaskMan-v2\logs\deployment-*.log`
2. **Health monitoring logs**: `C:\TaskMan-v2\logs\health-monitor.log`
3. **Application logs**: `C:\TaskMan-v2\logs\stdout.log`, `stderr.log`
4. **Windows Event Viewer**: Application log, source "TaskManAPI"

### External Resources

1. **NSSM Official Documentation**: https://nssm.cc/
2. **FastAPI Deployment Guide**: https://fastapi.tiangolo.com/deployment/
3. **Uvicorn Documentation**: https://www.uvicorn.org/
4. **PostgreSQL Windows**: https://www.postgresql.org/download/windows/

---

## Feedback and Contributions

This documentation is maintained as part of the TaskMan-v2 project. For updates or corrections:

1. Open an issue in the project repository
2. Submit a pull request with proposed changes
3. Contact the DevOps team for urgent updates

**Documentation philosophy**: "Trust Nothing, Verify Everything. Evidence is the closing loop of trust."

All commands and configurations in this documentation have been tested in production-like Windows environments.

---

## Quick Decision Matrix

**Should I use NSSM for TaskMan-v2?**

| Factor | NSSM Recommended | Alternative Recommended |
|--------|------------------|------------------------|
| Target platform | Windows Server | Linux/multi-cloud |
| Team expertise | Windows admins | Docker/Kubernetes |
| Service count | 1-3 services | 5+ microservices |
| Startup time priority | <10 seconds | Not critical |
| Docker licensing | Cost concern | Budget available |
| Windows integration | Required (Event Log) | Not required |
| Development parity | Windows dev environment | Docker dev environment |

**Decision**: ✅ NSSM is RECOMMENDED for TaskMan-v2 based on:
- Windows Server target platform
- Single-service architecture
- Fast startup requirement
- Windows Event Log integration
- Cost-effective deployment

---

**Thank you for using this documentation suite. Deploy with confidence!**

*Generated by ContextForge Research Team - 2025-12-26*
