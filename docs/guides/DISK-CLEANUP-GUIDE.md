# Disk Cleanup Guide

> **Quick Reference**: Complete guide for reclaiming disk space in your workspace and Windows system

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Automated Cleanup Scripts](#automated-cleanup-scripts)
3. [Manual Cleanup Steps](#manual-cleanup-steps)
4. [Expected Results](#expected-results)
5. [Safety Information](#safety-information)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Recommended Execution Order

```powershell
# Step 1: Preview what will be cleaned
.\scripts\Invoke-DiskCleanupVerification.ps1 -IncludeSystemDirs

# Step 2: Clean workspace files (safe, no admin required)
.\scripts\Invoke-WorkspaceCleanup.ps1 -WhatIf    # Preview
.\scripts\Invoke-WorkspaceCleanup.ps1            # Execute

# Step 3: Clean system caches (safe, no admin required)
.\scripts\Invoke-SystemCacheCleanup.ps1

# Step 4: Clean Windows system (requires admin)
.\scripts\Invoke-AdminCleanup.ps1

# Step 5: Manual browser/app cleanup (see below)
```

**Total Expected Recovery**: 12-19 GB (up to 40+ GB with WSL removal)

---

## Automated Cleanup Scripts

### 1. Invoke-DiskCleanupVerification.ps1

**Purpose**: Preview and analyze files that can be cleaned up

**Usage**:
```powershell
# Workspace analysis only
.\scripts\Invoke-DiskCleanupVerification.ps1

# Include system directories
.\scripts\Invoke-DiskCleanupVerification.ps1 -IncludeSystemDirs
```

**What It Does**:
- Scans for obsolete files
- Calculates potential space savings
- Does NOT delete anything
- Provides detailed report

**Privileges**: Standard user

---

### 2. Invoke-WorkspaceCleanup.ps1

**Purpose**: Clean workspace project files

**Usage**:
```powershell
# Preview mode
.\scripts\Invoke-WorkspaceCleanup.ps1 -WhatIf

# Execute cleanup
.\scripts\Invoke-WorkspaceCleanup.ps1

# Include optional node_modules cleanup
.\scripts\Invoke-WorkspaceCleanup.ps1 -IncludeNodeModules

# Skip confirmations
.\scripts\Invoke-WorkspaceCleanup.ps1 -Force
```

**What It Cleans**:
- ✅ `__pycache__` directories (100+ locations)
- ✅ `.pytest_cache` directories
- ✅ Test database files (100+ files in `data/`, `db/`)
- ✅ Old backups and archives
- ✅ `.bak` files
- ✅ Test output files
- ✅ Build artifacts and coverage reports
- ✅ Logs older than 30 days
- ✅ Virtual environments (example projects)
- ⚠️ `node_modules` (optional with `-IncludeNodeModules`)

**Expected Recovery**: 3-6 GB

**Privileges**: Standard user

---

### 3. Invoke-SystemCacheCleanup.ps1

**Purpose**: Clean development tool caches and temporary files

**Usage**:
```powershell
# Standard cleanup
.\scripts\Invoke-SystemCacheCleanup.ps1

# Preview mode
.\scripts\Invoke-SystemCacheCleanup.ps1 -WhatIf

# Skip Temp directory
.\scripts\Invoke-SystemCacheCleanup.ps1 -SkipTemp
```

**What It Cleans**:
- ✅ NPM cache (~1.7 GB)
- ✅ UV Python cache (~1.9 GB)
- ✅ pip cache
- ✅ Go build cache
- ✅ VS Code caches (~1.5 GB)
- ✅ Temp directory (~2 GB)
- ✅ Jedi Python cache

**Expected Recovery**: 7-10 GB

**Privileges**: Standard user

---

### 4. Invoke-AdminCleanup.ps1

**Purpose**: Windows system cleanup (DISM, component store)

**Usage**:
```powershell
# Standard cleanup (safe)
.\scripts\Invoke-AdminCleanup.ps1

# Aggressive cleanup (removes update rollback)
.\scripts\Invoke-AdminCleanup.ps1 -IncludeResetBase

# Enable component store compression
.\scripts\Invoke-AdminCleanup.ps1 -CompressComponentStore
```

**What It Cleans**:
- ✅ Windows component store (WinSxS) (~1-3 GB)
- ✅ Windows Update cache
- ✅ System Temp directory
- ⚠️ Component store compression (optional, 2-4 GB additional)

**Expected Recovery**: 1-3 GB (up to 7 GB with compression)

**Privileges**: **Administrator required**

**⚠️ Warning**: `-IncludeResetBase` removes ability to uninstall Windows updates

---

## Manual Cleanup Steps

### Browser Cache Cleanup

#### Microsoft Edge

1. Open Edge → Settings (`edge://settings/`)
2. Privacy, search, and services
3. Choose what to clear → **Clear now**
4. Time range: **All time**
5. Select:
   - ✅ Cached images and files
   - ✅ Cookies and site data
   - ✅ Browsing history (optional)
6. Click **Clear now**

**Expected Recovery**: 0.5-1 GB

---

#### Google Chrome

1. Open Chrome → Settings (`chrome://settings/`)
2. Privacy and security → **Clear browsing data**
3. Time range: **All time**
4. Select:
   - ✅ Cached images and files
   - ✅ Cookies and other site data
5. Click **Clear data**

**Expected Recovery**: 0.3-0.5 GB

---

### Microsoft Teams Cache

1. **Close Teams completely**
   - Right-click Teams in system tray
   - Select **Quit**

2. **Clear cache**:
   ```powershell
   # Delete Teams cache
   Remove-Item "$env:APPDATA\Microsoft\Teams\Cache" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\blob_storage" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\databases" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\GPUcache" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\IndexedDB" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\Local Storage" -Recurse -Force
   Remove-Item "$env:APPDATA\Microsoft\Teams\tmp" -Recurse -Force
   ```

3. **Restart Teams**

**Expected Recovery**: 0.5-1 GB

---

### Windows Disk Cleanup Utility

```powershell
# Open Disk Cleanup
cleanmgr.exe

# Or configure advanced options
cleanmgr.exe /sageset:1    # Configure cleanup options
cleanmgr.exe /sagerun:1    # Run configured cleanup
```

**What to Select**:
- ✅ Temporary files
- ✅ Delivery Optimization Files
- ✅ Thumbnails
- ✅ Previous Windows installations (if upgrading)
- ✅ Windows Update Cleanup

**Expected Recovery**: 1-5 GB

---

### WSL (Windows Subsystem for Linux) Review

**⚠️ High Impact - 24 GB Potential**

#### Check WSL Usage

```powershell
# List all WSL distributions
wsl --list --verbose

# Check WSL status
wsl --status
```

#### If WSL Is Not Needed

```powershell
# Unregister a specific distribution
wsl --unregister <distribution-name>

# Or uninstall WSL completely
wsl --uninstall
```

**Expected Recovery**: 0-24 GB (only if WSL not in use)

---

## Expected Results

### Summary Table

| Category | Recovery | Method | Admin Required |
|----------|----------|--------|----------------|
| **Workspace Files** | 3-6 GB | Automated script | No |
| **System Caches** | 7-10 GB | Automated script | No |
| **Windows System (DISM)** | 1-3 GB | Automated script | Yes |
| **Browser Caches** | 1-2 GB | Manual | No |
| **Teams Cache** | 0.5-1 GB | Manual | No |
| **Disk Cleanup** | 1-5 GB | Windows tool | No |
| **WSL (Optional)** | 0-24 GB | Manual | No |
| **Total (Conservative)** | **12-19 GB** | Mixed | Some |
| **Total (With WSL)** | **36-43 GB** | Mixed | Some |

---

## Safety Information

### Safe to Delete

✅ **Python Caches** (`__pycache__`, `.pytest_cache`)
- Automatically regenerated when running Python code

✅ **NPM/pip/UV Caches**
- Packages will be re-downloaded when needed

✅ **Test Databases** (timestamped `.db` files in `data/`)
- These are test artifacts, not production data

✅ **Build Artifacts** (`build/htmlcov/`, old test results)
- Can be regenerated by running tests/builds

✅ **Temp Directories**
- Designed to be temporary

✅ **Browser Caches**
- Will be rebuilt as you browse

✅ **VS Code Caches**
- VS Code recreates these automatically

---

### Preserved Files

❌ **DO NOT DELETE**:
- `db/trackers.sqlite` - Active database
- `testResults.xml` - Current test results
- `node_modules/` in root - Active dependencies
- `.QSE/v2/Sessions/2025-11-12/` - Current session
- `AppData\Local\Programs\` - Installed applications
- `AppData\Roaming\Code\User\` - VS Code settings

---

### Critical Warnings

⚠️ **WinSxS Directory**
- **NEVER manually delete files from C:\Windows\WinSxS**
- Only clean via DISM or Windows tools
- Manual deletion WILL break Windows

⚠️ **DISM /ResetBase**
- Removes ability to uninstall Windows updates
- Use only if you're sure you won't need to rollback

⚠️ **WSL**
- Only remove if you're certain you don't use Linux environments
- Verify with `wsl --list` before deleting

---

## Troubleshooting

### "Access Denied" Errors

**Cause**: Files in use by running applications

**Solution**:
```powershell
# Close applications and retry
# Or restart computer and run cleanup immediately
```

---

### "DISM Failed" Error

**Cause**: Insufficient privileges or Windows Update running

**Solution**:
```powershell
# 1. Ensure running as Administrator
# 2. Check Windows Update isn't running
# 3. Restart and try again
```

---

### Script Not Found

**Cause**: Running from wrong directory

**Solution**:
```powershell
# Navigate to workspace root
cd "C:\Users\james.e.hardy\Documents\PowerShell Projects"

# Then run scripts
.\scripts\Invoke-WorkspaceCleanup.ps1
```

---

### "Command Not Found" (npm, pip, uv)

**Cause**: Tool not in PATH or not installed

**Solution**: Script will skip tools that aren't found. This is safe and expected.

---

### Files Not Being Deleted

**Cause**: Files locked by applications

**Solution**:
1. Close Visual Studio Code
2. Close all terminals
3. Close browsers
4. Restart computer
5. Run cleanup scripts immediately after boot

---

### How to Verify Space Reclaimed

```powershell
# Check free space before cleanup
Get-PSDrive C | Select-Object Used, Free

# Run cleanup scripts...

# Check free space after cleanup
Get-PSDrive C | Select-Object Used, Free

# Or use Windows File Explorer:
# This PC → Right-click C: → Properties
```

---

## Maintenance Schedule

### Weekly
- Clear browser caches (via browser settings)

### Monthly
- Run `Invoke-WorkspaceCleanup.ps1`
- Run `Invoke-SystemCacheCleanup.ps1`
- Clear Teams cache (if using Teams)

### Quarterly
- Run `Invoke-AdminCleanup.ps1` (as admin)
- Run Windows Disk Cleanup
- Review and archive old backups

### Annual
- Review installed applications and uninstall unused ones
- Check WSL usage
- Consider component store compression if space-constrained

---

## Additional Resources

### PowerShell Commands Reference

```powershell
# Check disk space
Get-PSDrive C

# Check folder size
Get-ChildItem -Path "C:\Path" -Recurse |
    Measure-Object -Property Length -Sum |
    Select-Object @{Name="Size(GB)";Expression={$_.Sum / 1GB}}

# List largest directories
Get-ChildItem -Path "C:\Path" -Directory |
    ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            SizeGB = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue |
                     Measure-Object -Property Length -Sum).Sum / 1GB
        }
    } | Sort-Object SizeGB -Descending

# Clear specific cache manually
Remove-Item "$env:LOCALAPPDATA\npm-cache" -Recurse -Force

# Run Windows Disk Cleanup
cleanmgr.exe

# Check DISM component store
DISM.exe /Online /Cleanup-Image /AnalyzeComponentStore
```

---

## Support

### Issues or Questions?

1. **Verify script execution**:
   ```powershell
   Get-ExecutionPolicy
   # If Restricted, run:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Review logs**: Scripts provide detailed output showing what was cleaned

3. **Run in preview mode** (`-WhatIf`) to see what would happen without making changes

4. **Check the verification script** first to understand what will be cleaned

---

## Summary Checklist

Use this checklist to track your cleanup progress:

- [ ] Run verification script to preview cleanup
- [ ] Run workspace cleanup script
- [ ] Run system cache cleanup script
- [ ] Clear Microsoft Edge cache
- [ ] Clear Google Chrome cache
- [ ] Clear Microsoft Teams cache (if applicable)
- [ ] Run Windows Disk Cleanup utility
- [ ] Run admin cleanup script (as administrator)
- [ ] Review WSL usage and clean if not needed
- [ ] Verify disk space has been reclaimed
- [ ] Restart computer to complete cleanup
- [ ] Schedule monthly maintenance

---

**Last Updated**: 2025-11-12
**Scripts Location**: `scripts/`
**Estimated Total Time**: 15-30 minutes (excluding DISM, which may take longer)
