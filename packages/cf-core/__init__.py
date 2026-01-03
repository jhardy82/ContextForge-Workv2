"""CF Core Package - Task Management with Clean Architecture.

Domain-driven design implementation for task management with repository pattern,
Result monad for error handling, and clean architecture principles.

Package Structure:
    - cf_core.shared: Common utilities (Result monad, exceptions)
    - cf_core.models: Pydantic data models (Task, Sprint, Project)
    - cf_core.domain: Rich domain entities with business logic
    - cf_core.repositories: Data access layer (Repository pattern)
    - cf_core.services: Business logic services (TaskManService)
    - cf_core.cli: Typer-based command-line interface
    - cf_core.mcp: MCP server for AI agent integration

Quick Start::

    from cf_core.shared import Result, NotFoundException
    from cf_core.services.taskman_service import TaskManService

    # Create service
    service = TaskManService()

    # Create a task
    result = service.create_task(title="Example", priority="high")
    if result.is_success:
        print(f"Created: {result.value['id']}")

CLI Usage::

    python -m cf_core.cli.main task list
    python -m cf_core.cli.main task create "New Task" --priority high
    python -m cf_core.cli.main --machine task list  # JSON output
"""

__version__ = "0.1.0"

# Re-export common types for convenience
from cf_core.models.task import Task
from cf_core.services.taskman_service import TaskManService
from cf_core.shared import NotFoundException, Result

__all__ = ["Result", "NotFoundException", "TaskManService", "Task", "__version__"]
