"""ContextForge Unified Status Module.

Provides merged status enums that unify cf_core's 5-status model with
TaskMan MCP's 7-status model into a comprehensive 9-status system.

Status Mapping:
    cf_core (5)    | MCP (7)      | Merged (9)
    --------------|--------------|-------------
    -             | planned      | planned
    -             | new          | new
    todo (alias)  | pending      | pending
    in_progress   | in_progress  | in_progress
    blocked       | blocked      | blocked
    done (alias)  | completed    | completed
    cancelled     | cancelled    | cancelled
    -             | -            | on_hold (new)
    -             | -            | archived (new)

Aliases ensure backward compatibility:
    - "todo" → "pending"
    - "done" → "completed"

Usage:
    from cf_core.models.status import TaskStatus, normalize_status

    status = normalize_status("todo")  # Returns "pending"
    status = normalize_status("done")  # Returns "completed"
    status = TaskStatus.PENDING       # Enum access
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

# =============================================================================
# Status Aliases (Backward Compatibility)
# =============================================================================

STATUS_ALIASES: dict[str, str] = {
    # cf_core aliases
    "todo": "pending",
    "done": "completed",
    # Common variations
    "complete": "completed",
    "cancel": "cancelled",
    "wip": "in_progress",
    "active": "in_progress",
    "hold": "on_hold",
    "waiting": "pending",
    "backlog": "planned",
    "open": "new",
}


# =============================================================================
# Task Status Enum
# =============================================================================

class TaskStatus(str, Enum):
    """Unified task status enum supporting 9 states.

    Lifecycle Flow:
        planned → new → pending → in_progress → completed
                                ↓
                             blocked → (resume) → in_progress
                                ↓
                             on_hold → (resume) → pending/in_progress
                                ↓
                           cancelled (terminal)
                                ↓
                            archived (terminal)

    State Categories:
        - Planning: planned, new
        - Active: pending, in_progress
        - Blocked: blocked, on_hold
        - Terminal: completed, cancelled, archived
    """

    # Planning states
    PLANNED = "planned"
    NEW = "new"

    # Active states
    PENDING = "pending"
    IN_PROGRESS = "in_progress"

    # Blocked states
    BLOCKED = "blocked"
    ON_HOLD = "on_hold"

    # Terminal states
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

    @classmethod
    def from_string(cls, value: str) -> TaskStatus:
        """Create TaskStatus from string, handling aliases.

        Args:
            value: Status string (case-insensitive, supports aliases)

        Returns:
            TaskStatus enum member

        Raises:
            ValueError: If value is not a valid status or alias
        """
        normalized = normalize_status(value)
        try:
            return cls(normalized)
        except ValueError:
            valid = ", ".join(s.value for s in cls)
            raise ValueError(f"Invalid status '{value}'. Valid: {valid}")

    @property
    def is_planning(self) -> bool:
        """Check if status is a planning state."""
        return self in (TaskStatus.PLANNED, TaskStatus.NEW)

    @property
    def is_active(self) -> bool:
        """Check if status is an active working state."""
        return self in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)

    @property
    def is_blocked(self) -> bool:
        """Check if status is a blocked/waiting state."""
        return self in (TaskStatus.BLOCKED, TaskStatus.ON_HOLD)

    @property
    def is_terminal(self) -> bool:
        """Check if status is a terminal state (no transitions out)."""
        return self in (TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.ARCHIVED)

    @property
    def is_closed(self) -> bool:
        """Check if status represents a closed/finished task."""
        return self in (TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.ARCHIVED)

    @property
    def category(self) -> str:
        """Get the category name for this status."""
        if self.is_planning:
            return "planning"
        elif self.is_active:
            return "active"
        elif self.is_blocked:
            return "blocked"
        else:
            return "terminal"

    def can_transition_to(self, target: TaskStatus) -> bool:
        """Check if transition to target status is valid.

        Valid transitions follow the lifecycle flow with some flexibility
        for real-world usage patterns.
        """
        return target in VALID_TRANSITIONS.get(self, set())


# =============================================================================
# Sprint Status Enum
# =============================================================================

class SprintStatus(str, Enum):
    """Sprint lifecycle status.

    Lifecycle: planned → active → completed
                          ↓
                       cancelled
    """

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def is_open(self) -> bool:
        """Check if sprint is open for work."""
        return self == SprintStatus.ACTIVE

    @property
    def is_closed(self) -> bool:
        """Check if sprint is closed."""
        return self in (SprintStatus.COMPLETED, SprintStatus.CANCELLED)


# =============================================================================
# Project Status Enum
# =============================================================================

class ProjectStatus(str, Enum):
    """Project lifecycle status.

    Extended 8-status model for comprehensive project tracking.
    """

    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

    @property
    def is_active(self) -> bool:
        """Check if project is actively being worked on."""
        return self in (ProjectStatus.ACTIVE, ProjectStatus.AT_RISK)

    @property
    def is_closed(self) -> bool:
        """Check if project is closed."""
        return self in (
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
            ProjectStatus.ARCHIVED,
        )


# =============================================================================
# Valid Transitions
# =============================================================================

VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PLANNED: {
        TaskStatus.NEW,
        TaskStatus.PENDING,
        TaskStatus.CANCELLED,
        TaskStatus.ARCHIVED,
    },
    TaskStatus.NEW: {
        TaskStatus.PENDING,
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.CANCELLED,
        TaskStatus.ARCHIVED,
    },
    TaskStatus.PENDING: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.ON_HOLD,
        TaskStatus.CANCELLED,
    },
    TaskStatus.IN_PROGRESS: {
        TaskStatus.PENDING,
        TaskStatus.BLOCKED,
        TaskStatus.ON_HOLD,
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.BLOCKED: {
        TaskStatus.PENDING,
        TaskStatus.IN_PROGRESS,
        TaskStatus.ON_HOLD,
        TaskStatus.CANCELLED,
    },
    TaskStatus.ON_HOLD: {
        TaskStatus.PENDING,
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.CANCELLED,
        TaskStatus.ARCHIVED,
    },
    TaskStatus.COMPLETED: {
        TaskStatus.ARCHIVED,
        # Allow reopening in exceptional cases
        TaskStatus.IN_PROGRESS,
    },
    TaskStatus.CANCELLED: {
        TaskStatus.ARCHIVED,
        # Allow revival in exceptional cases
        TaskStatus.PENDING,
    },
    TaskStatus.ARCHIVED: set(),  # Terminal - no transitions out
}


# =============================================================================
# Normalization Functions
# =============================================================================

def normalize_status(value: str) -> str:
    """Normalize a status string, applying aliases.

    Args:
        value: Raw status string

    Returns:
        Normalized status string (lowercase, alias-resolved)

    Examples:
        >>> normalize_status("TODO")
        'pending'
        >>> normalize_status("Done")
        'completed'
        >>> normalize_status("in_progress")
        'in_progress'
    """
    normalized = value.lower().strip()
    return STATUS_ALIASES.get(normalized, normalized)


def is_valid_status(value: str) -> bool:
    """Check if a status string is valid (including aliases).

    Args:
        value: Status string to validate

    Returns:
        True if valid status or alias
    """
    normalized = normalize_status(value)
    return normalized in {s.value for s in TaskStatus}


# =============================================================================
# Type Aliases for Type Hints
# =============================================================================

TaskStatusLiteral = Literal[
    "planned",
    "new",
    "pending",
    "in_progress",
    "blocked",
    "on_hold",
    "completed",
    "cancelled",
    "archived",
]

SprintStatusLiteral = Literal["planned", "active", "completed", "cancelled"]

ProjectStatusLiteral = Literal[
    "draft",
    "planning",
    "active",
    "on_hold",
    "at_risk",
    "completed",
    "cancelled",
    "archived",
]


__all__ = [
    # Enums
    "TaskStatus",
    "SprintStatus",
    "ProjectStatus",
    # Literals
    "TaskStatusLiteral",
    "SprintStatusLiteral",
    "ProjectStatusLiteral",
    # Constants
    "STATUS_ALIASES",
    "VALID_TRANSITIONS",
    # Functions
    "normalize_status",
    "is_valid_status",
]
