"""
cf_core.models

Domain models for ContextForge with:
- Rich Pydantic v2 models (Task, Sprint, Project)
- ActionItem for embedded action lists
- Hierarchical ID generation utilities
- Context model for UCL compliance

Falls back to minimal dataclass stubs if upstream models unavailable.
"""

from dataclasses import dataclass
from typing import Optional

# Export ActionItem and ID generator (always available)
from cf_core.models.action_item import ActionItem, ActionItemPriority, ActionItemStatus
from cf_core.models.id_generator import (
    IDGenerator,
    generate_action_id,
    generate_project_id,
    generate_sprint_id,
    generate_task_id,
)

# ID normalization (accepts T-xxx, TASK-xxx formats)
from cf_core.models.identifiers import (
    IDPrefix,
    extract_id_prefix,
    extract_id_suffix,
    get_id_type,
    is_valid_project_id,
    is_valid_sprint_id,
    is_valid_task_id,
    normalize_action_id,
    normalize_project_id,
    normalize_sprint_id,
    normalize_task_id,
)

# Unified priority system (bidirectional int/string conversion)
from cf_core.models.priority import (
    DEFAULT_PRIORITY,
    PRIORITY_ALIASES,
    Priority,
    is_valid_priority,
    normalize_priority,
)

# Unified status system (9-status with backward compatibility)
from cf_core.models.status import (
    STATUS_ALIASES,
    TaskStatus as UnifiedTaskStatus,
    is_valid_status,
    normalize_status,
)

# Velocity tracking model
from cf_core.models.velocity import VelocityMetric

# Phase tracking model
from cf_core.models.phase_tracking import (
    PhaseTracking,
    PhaseStatus,
    ResearchPhase,
    PlanningPhase,
    ImplementationPhase,
    TestingPhase,
)

# Try to use rich Pydantic models from cf_core.models
try:
    from cf_core.models.project import Project, ProjectStatus
    from cf_core.models.sprint import Sprint, SprintStatus
    from cf_core.models.task import Task, TaskStatus
    HAVE_RICH_MODELS = True
except ImportError:
    # Try upstream python.api.models
    try:
        from python.api.models.project import Project  # type: ignore
        from python.api.models.sprint import Sprint  # type: ignore
        from python.api.models.task import Task  # type: ignore
        HAVE_RICH_MODELS = True
    except Exception:
        HAVE_RICH_MODELS = False

# Provide minimal stubs when models are unavailable
if not HAVE_RICH_MODELS:
    @dataclass
    class Task:  # type: ignore[no-redef]
        id: str
        title: str
        status: str = "todo"
        priority: str = "medium"
        action_items: list = None  # type: ignore

        def __post_init__(self):
            if self.action_items is None:
                self.action_items = []

    @dataclass
    class Sprint:  # type: ignore[no-redef]
        id: str
        title: str
        status: str = "planned"
        action_items: list = None  # type: ignore

        def __post_init__(self):
            if self.action_items is None:
                self.action_items = []

    @dataclass
    class Project:  # type: ignore[no-redef]
        id: str
        name: str
        status: str = "active"
        action_items: list = None  # type: ignore

        def __post_init__(self):
            if self.action_items is None:
                self.action_items = []

    # Type stubs for completeness
    TaskStatus = str
    TaskPriority = str
    SprintStatus = str
    ProjectStatus = str


# Context model for UCL compliance (always available)
@dataclass
class Context:
    """Context entity for UCL compliance tracking."""
    id: str
    parent_id: str | None = None


__all__ = [
    # Core models
    "Task",
    "Sprint",
    "Project",
    "Context",
    "VelocityMetric",
    # Phase tracking
    "PhaseTracking",
    "PhaseStatus",
    "ResearchPhase",
    "PlanningPhase",
    "ImplementationPhase",
    "TestingPhase",
    # Action items
    "ActionItem",
    "ActionItemStatus",
    "ActionItemPriority",
    # ID generation
    "IDGenerator",
    "generate_project_id",
    "generate_sprint_id",
    "generate_task_id",
    "generate_action_id",
    # Type literals (when available)
    "TaskStatus",
    "TaskPriority",
    "SprintStatus",
    "ProjectStatus",
    # Unified status system
    "UnifiedTaskStatus",
    "STATUS_ALIASES",
    "normalize_status",
    "is_valid_status",
    # Unified priority system
    "Priority",
    "PRIORITY_ALIASES",
    "normalize_priority",
    "is_valid_priority",
    "DEFAULT_PRIORITY",
    # ID normalization
    "IDPrefix",
    "normalize_task_id",
    "normalize_sprint_id",
    "normalize_project_id",
    "normalize_action_id",
    "is_valid_task_id",
    "is_valid_sprint_id",
    "is_valid_project_id",
    "extract_id_suffix",
    "extract_id_prefix",
    "get_id_type",
    # Feature flag
    "HAVE_RICH_MODELS",
]
