# Technical Architecture: Database-Integrated CLI

## 🏗️ Architecture Overview

Transform DBCLI from CSV prototype to production database-integrated CLI leveraging the existing `trackers.sqlite` unified database with 57-column schema and 30+ existing tasks.

## 🎯 Design Principles

### Core Principles
1. **Database-First**: All operations target SQLite database as single source of truth
2. **Schema Utilization**: Leverage existing 57-column comprehensive tracker schema
3. **Rich Queries**: Support complex filtering and relationship navigation
4. **CLI Excellence**: Typer + Rich console for superior user experience
5. **Copilot Integration**: Enhanced instructions for automated tracker operations
6. **No Data Duplication**: Eliminate CSV/YAML fragmentation

### Quality Attributes
- **Consistency**: Single database source eliminates data fragmentation
- **Performance**: SQLite efficiency for expected dataset size (<1000 tasks)
- **Usability**: Rich console output leveraging full schema
- **Integration**: Seamless Copilot workflow with database operations
- **Extensibility**: Database schema supports future enhancements

## 📁 Target Module Structure

```
dbcli/
├── __init__.py
├── main.py                    # CLI entry point with typer app
├── core/
│   ├── __init__.py
│   ├── config.py             # Database connection configuration
│   ├── database.py           # SQLite connection and query utilities
│   └── exceptions.py         # CLI-specific exceptions
├── models/
│   ├── __init__.py
│   ├── task.py              # Task data model (57 columns)
│   ├── sprint.py            # Sprint data model
│   ├── project.py           # Project data model
│   └── label.py             # Label and relationship models
├── commands/
│   ├── __init__.py
│   ├── tasks.py             # Task CRUD commands
│   ├── sprints.py           # Sprint management commands
│   ├── projects.py          # Project management commands
│   ├── search.py            # Advanced search and filtering
│   └── reports.py           # Analytics and reporting
├── formatters/
│   ├── __init__.py
│   ├── table.py             # Rich table formatting
│   ├── json.py              # JSON output formatting
│   └── markdown.py          # Markdown export formatting
└── integrations/
    ├── __init__.py
    ├── copilot.py           # Copilot helper functions
    └── logger.py            # UnifiedLogger integration
```

│   │   ├── schemas.py       # JSON schemas
│   │   ├── validators.py    # Validation logic
│   │   └── relationships.py # Cross-entity validation
│   └── storage/
│       ├── **init**.py
│       ├── csv_handler.py   # CSV operations
│       ├── backup.py        # Backup management
│       └── cache.py         # Caching layer
├── services/
│   ├── **init**.py
│   ├── task_service.py      # Task business logic
│   ├── sprint_service.py    # Sprint business logic
│   ├── project_service.py   # Project business logic
│   ├── duplicate_service.py # Duplicate detection
│   ├── analytics_service.py # Analytics and reporting
│   └── workflow_service.py  # Workflow automation
├── cli/
│   ├── **init**.py
│   ├── commands/
│   │   ├── **init**.py
│   │   ├── tasks.py         # Task CLI commands
│   │   ├── sprints.py       # Sprint CLI commands
│   │   ├── projects.py      # Project CLI commands
│   │   ├── workflow.py      # Workflow CLI commands
│   │   └── duplicates.py    # Duplicate CLI commands
│   ├── formatters/
│   │   ├── **init**.py
│   │   ├── table.py         # Rich table formatting
│   │   ├── json.py          # JSON output
│   │   └── export.py        # Export formatters
│   └── utils/
│       ├── **init**.py
│       ├── console.py       # Console utilities
│       └── pagination.py    # Pagination support
├── plugins/
│   ├── **init**.py
│   ├── manager.py           # Plugin management
│   └── interfaces.py       # Plugin interfaces
└── tests/
    ├── **init**.py
    ├── unit/
    ├── integration/

## 🔧 Core Components Design

### 1. Database Integration Layer

#### SQLite Connection Manager

```python
# core/database.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

class DatabaseManager:
    """SQLite database connection and query management"""

    def __init__(self, db_path: str = "db/trackers.sqlite"):
        self.db_path = Path(db_path)
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Verify database file exists"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return results as dictionaries"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_command(self, command: str, params: tuple = ()) -> int:
        """Execute command and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(command, params)
            conn.commit()
            return cursor.rowcount
```

#### Task Data Model (57 Columns)

```python
# models/task.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    """Task model matching trackers.sqlite schema (57 columns)"""
    # Core fields
    id: str
    project_id: str = ""
    sprint_id: str = ""
    title: str = ""
    summary: str = ""
    status: str = "todo"
    priority: str = "medium"

    # Details
    severity: str = ""
    assignees: str = ""
    estimate_points: str = ""
    actual_hours: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Relationships
    depends_on: str = ""
    blocks: str = ""
    labels: str = ""

    # Management
    risk_notes: str = ""
    last_health: str = "green"
    last_heartbeat_utc: str = ""
    audit_tag: str = ""
    notes: str = ""

    # ... (additional 35+ columns from schema)

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Task':
        """Create Task from database row"""
        return cls(**row)

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {k: v for k, v in self.__dict__.items() if v is not None}
```

        # Apply business rules
        task = Task.from_dict(task_data)

        # Check for duplicates if requested
        if task_data.get("check_duplicates", True):
            similar = self.find_similar_tasks(task.title)
            if similar:
                self.logger.warning("Similar tasks found", extra={
                    "new_task_title": task.title,
                    "similar_count": len(similar)
                })

        # Save with transaction
        self.task_repo.save(task.to_dict())

        self.logger.info("Task created", extra={"task_id": task.id})
        return task

    def find_similar_tasks(self, title: str, threshold: float = 0.85) -> List[Task]:
        """Find tasks with similar titles"""
        # Implementation using difflib or ML similarity
        pass

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Task:
        """Update existing task with validation"""
        existing = self.task_repo.find_by_id(task_id)
        if not existing:
            raise TaskNotFoundError(f"Task {task_id} not found")

        # Apply updates with validation
        updated_data = {**existing, **updates}
        updated_data["updated_at"] = datetime.now().isoformat()

        task = Task.from_dict(updated_data)
        self.task_repo.save(task.to_dict())

        return task

```

### 3. Storage Layer Architecture

#### CSV Handler with Transactions

```python
# data/storage/csv_handler.py
import csv
import json
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Any
from ..backup import BackupManager
from ...core.logging import get_logger

class CSVHandler:
    """Handle CSV operations with transaction safety"""

    def __init__(self, csv_root: Path):
        self.csv_root = Path(csv_root)
        self.backup_manager = BackupManager(csv_root)
        self.logger = get_logger(__name__)

    @contextmanager
    def transaction(self, entity_name: str):
        """Transaction context for safe operations"""
        csv_file = self.csv_root / f"{entity_name}.csv"
        backup_file = None

        try:
            # Create backup
            if csv_file.exists():
                backup_file = self.backup_manager.create_backup(csv_file)

            yield csv_file

            # Transaction succeeded, clean up backup
            if backup_file:
                backup_file.unlink()

        except Exception as e:
            # Transaction failed, restore backup
            if backup_file and backup_file.exists():
                backup_file.replace(csv_file)
                self.logger.warning("Restored from backup due to transaction failure")
            raise

    def load_entities(self, entity_name: str) -> List[Dict[str, Any]]:
        """Load entities from CSV with error handling"""
        csv_file = self.csv_root / f"{entity_name}.csv"

        if not csv_file.exists():
            return []

        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                entities = [row for row in reader]

            self.logger.debug("Loaded entities", extra={
                "entity_name": entity_name,
### 2. CLI Command Architecture

#### Task Management Commands

```python
# commands/tasks.py
import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from ..core.database import DatabaseManager
from ..models.task import Task
from ..formatters.table import format_task_table

app = typer.Typer(help="Task management commands")
console = Console()
db = DatabaseManager()

@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    project: Optional[str] = typer.Option(None, help="Filter by project_id"),
    sprint: Optional[str] = typer.Option(None, help="Filter by sprint_id"),
    limit: int = typer.Option(20, help="Maximum number of results")
):
    """List tasks with optional filtering"""
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if project:
        query += " AND project_id = ?"
        params.append(project)
    if sprint:
        query += " AND sprint_id = ?"
        params.append(sprint)

    query += f" LIMIT {limit}"

    rows = db.execute_query(query, tuple(params))
    tasks = [Task.from_db_row(row) for row in rows]

    table = format_task_table(tasks)
    console.print(table)

@app.command("create")
def create_task(
    title: str = typer.Argument(..., help="Task title"),
    project_id: str = typer.Option("", help="Project ID"),
    status: str = typer.Option("todo", help="Initial status")
):
    """Create a new task"""
    # Generate unique ID
    from datetime import datetime
    import uuid
    task_id = f"T-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"

    query = """
    INSERT INTO tasks (id, title, project_id, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    now = datetime.now().isoformat()
    params = (task_id, title, project_id, status, now, now)

    affected = db.execute_command(query, params)
    if affected > 0:
        console.print(f"✅ Created task: {task_id}")
    else:
        console.print("❌ Failed to create task")

@app.command("update")
def update_task(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    title: Optional[str] = typer.Option(None, help="New title"),
    status: Optional[str] = typer.Option(None, help="New status"),
    project_id: Optional[str] = typer.Option(None, help="New project ID")
):
    """Update task fields"""
    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if status:
        updates.append("status = ?")
        params.append(status)
    if project_id:
        updates.append("project_id = ?")
        params.append(project_id)

    if not updates:
        console.print("❌ No updates specified")
        return

    from datetime import datetime
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(task_id)

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    affected = db.execute_command(query, tuple(params))

    if affected > 0:
        console.print(f"✅ Updated task: {task_id}")
    else:
        console.print(f"❌ Task not found: {task_id}")
```

from ...core.config import get_config
from ..formatters.table import TaskTableFormatter

app = typer.Typer(help="Task management commands")
console = Console()

@app.command("create")
def create_task(
    title: str,
    description: str = "",
    status: str = "planned",
    priority: str = "medium",
    check_duplicates: bool = True,
    ctx: typer.Context = typer.Context
):
    """Create a new task with validation and duplicate checking"""
    config = get_config()
    task_service = TaskService(config.get_task_repository())

    try:
        task = task_service.create_task({
            "title": title,
            "summary": description,
            "status": status,
            "priority": priority,
            "check_duplicates": check_duplicates
        })

        console.print(f"[green]Created task {task.id}: {task.title}[/green]")

    except Exception as e:
        console.print(f"[red]Error creating task: {e}[/red]")
        raise typer.Exit(1)

@app.command("list")
def list_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    format: str = "table",
    ctx: typer.Context = typer.Context
):
    """List tasks with filtering and formatting"""
    config = get_config()
    task_service = TaskService(config.get_task_repository())

    try:
        tasks = task_service.list_tasks(status=status, limit=limit)

        if format == "table":
            formatter = TaskTableFormatter()
            table = formatter.format(tasks)
            console.print(table)
        elif format == "json":
            import json
            print(json.dumps([task.to_dict() for task in tasks], indent=2))

    except Exception as e:
        console.print(f"[red]Error listing tasks: {e}[/red]")
        raise typer.Exit(1)

```

## 🔧 Configuration Management

### Configuration System

```python
# core/config.py
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    csv_root: Path
    backup_dir: Path
    schema_version: str = "2.0"

@dataclass
class PerformanceConfig:
    cache_ttl: int = 300
    max_cache_size: int = 1000
    index_rebuild_interval: int = 3600

@dataclass
class DBCLIConfig:
    database: DatabaseConfig
    performance: PerformanceConfig
    features: dict
    logging: dict

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'DBCLIConfig':
        """Load configuration from file"""
        if not config_path:
            config_path = Path("config/dbcli.yaml")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        return cls(
            database=DatabaseConfig(**data["database"]),
            performance=PerformanceConfig(**data["performance"]),
            features=data.get("features", {}),
            logging=data.get("logging", {})
        )
```

## 🚀 Migration Strategy

### Phase 1: Parallel Implementation
1. Create new module structure alongside existing monolith
2. Implement core data layer with proper CSV operations
3. Add transaction safety and backup mechanisms
4. Create comprehensive test suite

### Phase 2: Service Layer Migration
1. Extract business logic into service classes
2. Implement validation and relationship management
3. Add caching and performance optimizations
4. Create analytics and reporting capabilities

### Phase 3: CLI Refactoring
1. Split CLI commands into separate modules
2. Implement rich formatting and error handling
3. Add configuration management and plugin support
4. Create comprehensive documentation

### Phase 4: Advanced Features
1. Implement plugin architecture
2. Add advanced analytics and reporting
3. Create import/export framework
4. Add performance monitoring and optimization

## 📊 Performance Targets

### Response Time Goals
- **Simple queries** (by ID): <10ms
- **Filtered queries** (by status/priority): <50ms
- **Complex queries** (cross-entity): <100ms
- **Bulk operations** (100+ records): <500ms

### Scalability Targets
- **Small datasets** (<1k records): No optimization needed
- **Medium datasets** (1k-10k records): Caching and indexing
- **Large datasets** (10k+ records): Advanced optimization with potential SQLite backend

### Memory Usage
- **Base memory usage**: <50MB
- **With caching** (10k records): <200MB
- **Large operations**: <500MB peak

---

**Architecture Version**: 2.0
**Last Updated**: August 27, 2025
**Status**: Design Phase
**Implementation Timeline**: 4 weeks
