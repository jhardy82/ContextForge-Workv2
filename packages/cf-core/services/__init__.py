"""cf_core services module.

Provides unified access to core services by importing from their
canonical locations in the workspace. This maintains backward
compatibility while providing a clean cf_core interface.

Available services:
- TaskService: Task CRUD and business logic
- ActionListService: ActionList CRUD and task association
- VelocityService: Velocity tracking and predictions
- ulog/log: Structured logging (from unified_logging)
- VelocityTracker: Low-level velocity tracking (from python.velocity)
"""

from __future__ import annotations

# Import from canonical locations
try:
    # Backward compat aliases
    UnifiedLogger = None
    get_logger = None
except ImportError:
    # Fallback if unified_logging not in path
    ulog = None
    log = None
    get_logger_metrics = None
    UnifiedLogger = None
    get_logger = None

try:
    from cf_core.domain.velocity_tracker import VelocityTracker
except ImportError:
    VelocityTracker = None

# Import cf_core services
from cf_core.services.action_list_service import ActionListService
from cf_core.services.task_service import TaskService
from cf_core.services.velocity_service import VelocityService

# Re-export for cf_core.services interface
__all__ = [
    # cf_core services
    "TaskService",
    "ActionListService",
    "VelocityService",
    # From unified_logging
    "ulog",
    "log",
    "get_logger_metrics",
    # From python.velocity
    "VelocityTracker",
]
