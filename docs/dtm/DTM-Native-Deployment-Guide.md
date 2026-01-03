# DTM Docker-Free Deployment Guide

## 🎯 Overview
Deploy Dynamic Task Manager natively without Docker, integrating with existing CF_CLI, PostgreSQL, and Python infrastructure.

## 📋 Available Deployment Options

### 1. **Python-Native Integration** (RECOMMENDED)
- **Pros**: Full integration with existing CF_CLI, PostgreSQL, Python .venv
- **Cons**: Requires database setup
- **Best for**: Production use with existing infrastructure

### 2. **Standalone Node.js API** (Quick Start)
- **Pros**: Minimal setup, immediate deployment
- **Cons**: In-memory storage, separate from existing workflows
- **Best for**: Testing and development

### 3. **Hybrid Web Application** (Full UI)
- **Pros**: Complete web interface with React frontend
- **Cons**: More complex setup, Node.js dependency
- **Best for**: Teams needing web-based task management

## 🔧 Implementation: Python-Native Integration

### Phase 1: Environment Setup

```powershell
# Navigate to DTM directory
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects\dynamic-task-manager"

# Install DTM as Python package in existing .venv
& "c:\Users\james.e.hardy\Documents\PowerShell Projects\.venv\Scripts\Activate.ps1"
pip install -e .

# Install backend requirements
pip install -r backend/requirements.txt

# Additional dependencies for database integration
pip install psycopg2-binary sqlalchemy alembic
```

### Phase 2: Database Configuration

**Create DTM PostgreSQL Schema:**

```sql
-- DTM Tables Schema
CREATE SCHEMA IF NOT EXISTS dtm;

CREATE TABLE dtm.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dtm.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES dtm.projects(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(20) DEFAULT 'medium',
    assignee VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    tags JSONB,
    metadata JSONB
);

CREATE TABLE dtm.task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES dtm.tasks(id),
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project_id ON dtm.tasks(project_id);
CREATE INDEX idx_tasks_status ON dtm.tasks(status);
CREATE INDEX idx_tasks_assignee ON dtm.tasks(assignee);
CREATE INDEX idx_task_history_task_id ON dtm.task_history(task_id);
```

### Phase 3: CF_CLI Integration

**Create DTM CLI Commands:**

```python
# File: python/dtm_cli_integration.py
"""DTM integration with CF_CLI for native task management."""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import psycopg2
from sqlalchemy import create_engine, text
import json
from datetime import datetime

console = Console()
app = typer.Typer(name="dtm", help="Dynamic Task Manager commands")

class DTMDatabase:
    """Database interface for DTM native deployment."""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "postgresql://localhost:5432/contextforge"
        self.engine = create_engine(self.connection_string)

    def get_tasks(self, project_id: str = None, status: str = None) -> List[dict]:
        """Retrieve tasks with optional filtering."""
        with self.engine.connect() as conn:
            query = """
                SELECT t.*, p.name as project_name
                FROM dtm.tasks t
                LEFT JOIN dtm.projects p ON t.project_id = p.id
                WHERE 1=1
            """
            params = {}

            if project_id:
                query += " AND t.project_id = :project_id"
                params['project_id'] = project_id

            if status:
                query += " AND t.status = :status"
                params['status'] = status

            query += " ORDER BY t.created_at DESC"

            result = conn.execute(text(query), params)
            return [dict(row._mapping) for row in result]

    def create_task(self, title: str, description: str = None,
                   project_id: str = None, priority: str = "medium") -> str:
        """Create new task and return task ID."""
        with self.engine.connect() as conn:
            query = """
                INSERT INTO dtm.tasks (title, description, project_id, priority)
                VALUES (:title, :description, :project_id, :priority)
                RETURNING id
            """
            result = conn.execute(text(query), {
                'title': title,
                'description': description,
                'project_id': project_id,
                'priority': priority
            })
            conn.commit()
            return str(result.fetchone()[0])

# CLI Commands
@app.command()
def list_tasks(
    project: Optional[str] = tyner.Option(None, "--project", "-p", help="Filter by project"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """List tasks with optional filtering."""
    db = DTMDatabase()
    tasks = db.get_tasks(project_id=project, status=status)

    if json_output:
        console.print_json(json.dumps(tasks, default=str, indent=2))
        return

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Dynamic Task Manager - Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Project", style="blue")
    table.add_column("Created", style="dim")

    for task in tasks:
        table.add_row(
            str(task['id'])[:8],
            task['title'],
            task['status'],
            task['priority'],
            task.get('project_name', 'None'),
            task['created_at'].strftime("%Y-%m-%d") if task['created_at'] else ""
        )

    console.print(table)

@app.command()
def create_task(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Task description"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project ID"),
    priority: str = typer.Option("medium", "--priority", help="Task priority (low/medium/high)")
):
    """Create a new task."""
    db = DTMDatabase()
    task_id = db.create_task(title, description, project, priority)

    console.print(Panel(
        f"[green]✓ Task created successfully![/green]\n"
        f"Task ID: [cyan]{task_id}[/cyan]\n"
        f"Title: [white]{title}[/white]\n"
        f"Priority: [yellow]{priority}[/yellow]",
        title="Task Created"
    ))

@app.command()
def status():
    """Show DTM system status."""
    db = DTMDatabase()

    try:
        tasks = db.get_tasks()
        task_counts = {}
        for task in tasks:
            status = task['status']
            task_counts[status] = task_counts.get(status, 0) + 1

        status_panel = Panel(
            f"[green]✓ DTM Native Deployment Active[/green]\n"
            f"Database: [cyan]Connected[/cyan]\n"
            f"Total Tasks: [white]{len(tasks)}[/white]\n"
            f"Status Breakdown: [dim]{task_counts}[/dim]",
            title="DTM Status"
        )
        console.print(status_panel)

    except Exception as e:
        console.print(f"[red]✗ DTM Status Error: {e}[/red]")

if __name__ == "__main__":
    app()
```

### Phase 4: Integration with Existing Workflows

**Add DTM to CF_CLI main interface:**

```python
# Add to cf_cli.py
from python.dtm_cli_integration import app as dtm_app

# In main CLI app:
app.add_typer(dtm_app, name="dtm")
```

### Phase 5: Agent Todo MCP Synchronization

**Create bidirectional sync between DTM and Agent Todo MCP:**

```python
# File: python/dtm_mcp_sync.py
"""Synchronize DTM with Agent Todo MCP for unified task management."""

from typing import List, Dict
import json
from pathlib import Path

class DTMAgentTodoSync:
    """Bidirectional synchronization between DTM and Agent Todo MCP."""

    def __init__(self, dtm_db, mcp_client):
        self.dtm_db = dtm_db
        self.mcp_client = mcp_client

    def sync_todo_to_dtm(self, todo_id: str) -> str:
        """Import Agent Todo MCP task into DTM."""
        # Implementation for importing MCP tasks
        pass

    def sync_dtm_to_todo(self, task_id: str) -> str:
        """Export DTM task to Agent Todo MCP."""
        # Implementation for exporting DTM tasks
        pass

    def full_sync(self) -> Dict[str, int]:
        """Perform full bidirectional synchronization."""
        # Implementation for complete sync
        pass
```

## 🚀 Quick Start: Standalone Node.js API

For immediate deployment without database setup:

```powershell
# Navigate to DTM directory
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects\dynamic-task-manager"

# Install Node.js dependencies
npm install

# Start API server
node server.js
```

**Access Points:**
- API: http://localhost:8080
- Health Check: http://localhost:8080/health
- Tasks API: http://localhost:8080/api/tasks

## 🌐 Full Web Interface Option

For complete web UI with React frontend:

```powershell
# Install dependencies
npm install

# Build frontend
npm run build

# Start development server
npm run dev
```

**Access Points:**
- Web UI: http://localhost:5173
- API Backend: http://localhost:8080

## 🔄 Migration from Docker

**If you have existing Docker data to migrate:**

1. **Export Docker data:**
```bash
# If Docker containers are accessible
docker exec dtm-backend python -c "
import json
# Export logic here
"
```

2. **Import to native deployment:**
```python
# Use DTM CLI to import data
python cf_cli.py dtm import-data --file exported_data.json
```

## 🔍 Testing the Deployment

```powershell
# Test DTM integration
python cf_cli.py dtm status

# Create test task
python cf_cli.py dtm create-task "Test Native DTM" --desc "Testing Docker-free deployment"

# List tasks
python cf_cli.py dtm list-tasks

# Test with rich output
python cf_cli.py dtm list-tasks --json | python -m json.tool
```

## 🎯 Next Steps

1. **Phase 1**: Install Python-native DTM integration
2. **Phase 2**: Setup PostgreSQL schema and database connection
3. **Phase 3**: Test basic task management functionality
4. **Phase 4**: Integrate with Agent Todo MCP synchronization
5. **Phase 5**: Connect with QSE workflow phases

## 🆘 Troubleshooting

**Common Issues:**
- **Database Connection**: Verify PostgreSQL service running and connection string
- **Python Dependencies**: Use virtual environment and install all requirements
- **Path Issues**: Ensure all file paths are absolute when needed

**Support Commands:**
```powershell
# Check Python environment
python -c "import sys; print(sys.executable)"

# Verify database connection
python -c "import psycopg2; print('PostgreSQL driver available')"

# Test DTM package installation
python -c "import dynamic_task_manager; print('DTM package installed')"
```
