# 🚨 CRITICAL: Database Integration Migration - IMPLEMENT IMMEDIATELY

## ⚠️ MIGRATION PRIORITY

**The current `dbcli.py` is a CSV prototype that needs immediate migration to the existing SQLite database to eliminate data fragmentation and leverage the comprehensive tracker platform.**

## � Migration Strategy Summary

| Component | Current State | Target State | Priority |
|-----------|---------------|--------------|----------|
| Data Storage | CSV prototype | SQLite database | CRITICAL |
| Data Source | Non-existent CSV files | Existing trackers.sqlite (30+ tasks) | HIGH |
| Schema | Basic prototype fields | 57-column comprehensive schema | HIGH |
| Operations | Stub implementations | Full database CRUD | CRITICAL |

## � Migration #1: Replace CSV with Database Operations

### Current Broken CSV Approach

```python
def save_tasks(tasks: List[dict]):
    """Save tasks to CSV"""
    tasks_file = get_tasks_csv_path()

    if tasks:
        headers = list(tasks[0].keys())
    else:
        headers = [
            # ... long list of headers
        ]

    try:
        with open(tasks_file, "w", newline="", encoding="utf-8") as f:
            # ⚠️ CRITICAL: NO ACTUAL WRITING HAPPENS HERE!
            pass
        logger.info("Saved tasks", extra={"count": len(tasks), "path": str(tasks_file)})
    except Exception as e:
        if logger:
            pass
        raise
```

### ✅ DATABASE Implementation (IMPLEMENT NOW)

```python
import sqlite3  # REPLACE CSV IMPORT!
from pathlib import Path

def save_tasks(tasks: List[dict]):
    """Save tasks to CSV with atomic write operations"""
    tasks_file = get_tasks_csv_path()

    # Create backup before writing
    backup_file = tasks_file.with_suffix('.csv.backup')
    if tasks_file.exists():
        shutil.copy2(tasks_file, backup_file)

    if tasks:
        headers = list(tasks[0].keys())
    else:
        # Fallback headers for empty list
        headers = [
            "id", "project_id", "sprint_id", "title", "summary", "status",
            "priority", "severity", "assignees", "estimate_points",
            "actual_hours", "created_at", "updated_at", "depends_on",
            "blocks", "labels", "risk_notes", "last_health",
            "last_heartbeat_utc", "audit_tag", "notes", "correlation_hint",
            "schema_version", "batch_id", "task_sequence", "critical_path",
            "risk_level", "mitigation_status", "target_date", "done_date",
            "content_hash", "eff_priority", "work_type",
            "verification_requirements", "validation_state", "origin_source",
            "load_group", "context_objects", "context_dimensions",
            "geometry_shape", "shape_stage", "aar_count", "last_aar_utc",
            "misstep_count", "last_misstep_utc", "evidence_required",
            "evidence_emitted", "execution_trace_log"
        ]

    try:
        # Atomic write: write to temp file first, then rename
        temp_file = tasks_file.with_suffix('.csv.tmp')

        with open(temp_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for task in tasks:
                # Ensure all fields are present with empty string defaults
                row = {header: task.get(header, "") for header in headers}
                writer.writerow(row)

        # Atomic rename (safe on most filesystems)
        temp_file.replace(tasks_file)

        if logger:
            logger.info("Saved tasks", extra={
                "count": len(tasks),
                "path": str(tasks_file),
                "headers_count": len(headers)
            })

    except Exception as e:
        if logger:
            logger.error("Failed to save tasks", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "path": str(tasks_file),
                "count": len(tasks)
            })
        # Restore from backup if it exists
        if backup_file.exists():
            shutil.copy2(backup_file, tasks_file)
            logger.warning("Restored from backup due to save failure")
        raise typer.Exit(f"Failed to save tasks: {e}")
```

## 🔥 Issue #2: Delete Operation Field Name Bug

### Current Broken Code

```python
@tasks_app.command("delete")
def delete_task(
    task_id: str,
    force: Annotated[bool, typer.Option("--force", help="Skip confirmation")] = False,
):
    """Delete a task"""
    # ... validation code ...

    tasks = load_tasks()
    # ❌ WRONG FIELD NAME - will never match!
    tasks = [t for t in tasks if t.get("task_id") != task_id]
    save_tasks(tasks)
```

### ✅ FIXED Implementation

```python
@tasks_app.command("delete")
def delete_task(
    task_id: str,
    force: Annotated[bool, typer.Option("--force", help="Skip confirmation")] = False,
):
    """Delete a task"""
    logger.info("Deleting task", extra={"task_id": task_id, "force": force})

    task = find_task(task_id)
    if not task:
        console.print(f"[red]Error: Task {task_id} not found[/red]")
        raise typer.Exit(1)

    if not force:
        if rich_enabled:
            console.print(f"[yellow]About to delete task: {task.get('title', 'Unknown')}[/yellow]")
            confirm = typer.confirm("Are you sure you want to delete this task?")
            if not confirm:
                console.print("[blue]Delete cancelled[/blue]")
                return
        else:
            response = input(f"Delete task '{task.get('title', 'Unknown')}'? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Delete cancelled")
                return

    tasks = load_tasks()
    original_count = len(tasks)

    # ✅ CORRECT FIELD NAME
    tasks = [t for t in tasks if t.get("id") != task_id]

    if len(tasks) == original_count:
        console.print(f"[red]Error: Task {task_id} was not found in the list[/red]")
        logger.error("Task not found during deletion", extra={"task_id": task_id})
        raise typer.Exit(1)

    save_tasks(tasks)

    if rich_enabled:
        console.print(f"[green]Successfully deleted task {task_id}[/green]")
    else:
        print(f"Successfully deleted task {task_id}")

    logger.info("Deleted task", extra={"task_id": task_id, "deleted_count": 1})
```

## 🔥 Issue #3: Missing Critical Imports

### Required Imports to Add

```python
# Add these imports at the top of dbcli.py
import csv        # CRITICAL: Required for CSV operations
import json       # For configuration and data serialization
import uuid       # For ID generation
import hashlib    # For content hashing and integrity
import re         # For title normalization
import time       # For performance timing
import shutil     # For backup operations
import os         # For file operations
from contextlib import contextmanager  # For transaction contexts
```

## 🔥 Issue #4: Fix Load Operations

### Current Broken Load Function

```python
def load_tasks() -> List[dict]:
    """Load all tasks from CSV"""
    ensure_csv_structure()
    tasks = []
    tasks_file = get_tasks_csv_path()

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            # ❌ EMPTY IMPLEMENTATION BLOCK
            pass
        if logger:
            # ❌ EMPTY LOGGING BLOCK
            pass
    except Exception as e:
        if logger:
            # ❌ EMPTY ERROR HANDLING
            pass

    return tasks
```

### ✅ FIXED Implementation

```python
def load_tasks() -> List[dict]:
    """Load all tasks from CSV"""
    ensure_csv_structure()
    tasks = []
    tasks_file = get_tasks_csv_path()

    if not tasks_file.exists():
        logger.warning("Tasks file does not exist", extra={"path": str(tasks_file)})
        return tasks

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tasks = [row for row in reader]

        if logger:
            logger.info("Loaded tasks", extra={
                "count": len(tasks),
                "path": str(tasks_file)
            })

    except Exception as e:
        if logger:
            logger.error("Failed to load tasks", extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "path": str(tasks_file)
            })
        console.print(f"[red]Error loading tasks: {e}[/red]")
        # Return empty list rather than crashing
        tasks = []

    return tasks
```

## 🔥 Issue #5: Fix Ensure CSV Structure

### Current Broken Implementation

```python
def ensure_csv_structure():
    """Ensure CSV directory and files exist with proper headers"""
    csv_root_path.mkdir(parents=True, exist_ok=True)

    tasks_file = get_tasks_csv_path()
    if not tasks_file.exists():
        headers = [
            # ... list of headers ...
        ]
        with open(tasks_file, "w", newline="", encoding="utf-8") as f:
            # ❌ NO WRITER CREATED OR USED!
            pass
        logger.info("Created tasks.csv with headers", extra={"path": str(tasks_file)})
```

### ✅ FIXED Implementation

```python
def ensure_csv_structure():
    """Ensure CSV directory and files exist with proper headers"""
    csv_root_path.mkdir(parents=True, exist_ok=True)

    tasks_file = get_tasks_csv_path()
    if not tasks_file.exists():
        headers = [
            "id", "project_id", "sprint_id", "title", "summary", "status",
            "priority", "severity", "assignees", "estimate_points",
            "actual_hours", "created_at", "updated_at", "depends_on",
            "blocks", "labels", "risk_notes", "last_health",
            "last_heartbeat_utc", "audit_tag", "notes", "correlation_hint",
            "schema_version", "batch_id", "task_sequence", "critical_path",
            "risk_level", "mitigation_status", "target_date", "done_date",
            "content_hash", "eff_priority", "work_type",
            "verification_requirements", "validation_state", "origin_source",
            "load_group", "context_objects", "context_dimensions",
            "geometry_shape", "shape_stage", "aar_count", "last_aar_utc",
            "misstep_count", "last_misstep_utc", "evidence_required",
            "evidence_emitted", "execution_trace_log"
        ]

        try:
            with open(tasks_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

            if logger:
                logger.info("Created tasks.csv with headers", extra={
                    "path": str(tasks_file),
                    "headers_count": len(headers)
                })
        except Exception as e:
            if logger:
                logger.error("Failed to create tasks.csv", extra={
                    "error": str(e),
                    "path": str(tasks_file)
                })
            raise typer.Exit(f"Failed to create tasks file: {e}")
```

## 🛠️ Complete Implementation Checklist

### Immediate Actions (Do Today)
- [ ] **Add missing imports** (csv, json, uuid, hashlib, re, time, shutil, os)
- [ ] **Fix save_tasks()** with proper CSV writing
- [ ] **Fix load_tasks()** with proper CSV reading
- [ ] **Fix ensure_csv_structure()** with proper CSV creation
- [ ] **Fix delete_task()** field name bug (task_id → id)
- [ ] **Apply same fixes** to save_sprints() and save_projects()

### Data Safety Measures (Do Today)
- [ ] **Create backup script** before applying fixes
- [ ] **Test fixes** on copy of data
- [ ] **Validate** existing data can be loaded correctly
- [ ] **Implement** atomic write operations with temp files

### Validation (Do Today)
- [ ] **Test create operation** - verify data is actually saved
- [ ] **Test delete operation** - verify correct item is removed
- [ ] **Test load operation** - verify data loads correctly
- [ ] **Test error handling** - verify graceful failures

## 🚨 Pre-Implementation Backup Procedure

```bash
# Create backup of current data
cp -r ./trackers/csv ./trackers/csv.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -la ./trackers/csv.backup.*
```

## ⚡ Quick Test Script

Create a test script to verify fixes:

```python
#!/usr/bin/env python3
"""Quick test for critical fixes"""

def test_critical_fixes():
    """Test the critical fixes work correctly"""

    # Test 1: CSV write operations
    test_tasks = [
        {
            "id": "T-20250827-test001",
            "title": "Test Task",
            "status": "planned",
            "priority": "medium"
        }
    ]

    print("Testing save_tasks...")
    save_tasks(test_tasks)

    print("Testing load_tasks...")
    loaded = load_tasks()
    assert len(loaded) >= 1, "Tasks not loaded correctly"

    print("Testing delete_task...")
    # Test delete operation

    print("✅ All critical fixes working!")

if __name__ == "__main__":
    test_critical_fixes()
```

---

**⚠️ DO NOT PROCEED WITH OTHER DEVELOPMENT UNTIL THESE FIXES ARE IMPLEMENTED AND TESTED**

**Implementation Priority**: CRITICAL - Fix today
**Testing Priority**: MANDATORY - Test before deploying
**Backup Priority**: ESSENTIAL - Backup before changes
