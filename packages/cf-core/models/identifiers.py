"""ContextForge Identifier Normalization Module.

Provides unified ID handling for tasks, sprints, and projects with
support for multiple prefix formats used across the codebase.

ID Format Variations:
    Format      | Example      | Normalized
    ------------|--------------|------------
    T-prefix    | T-001        | TASK-001
    TASK-prefix | TASK-001     | TASK-001
    S-prefix    | S-001        | SPRINT-001
    SPRINT-     | SPRINT-001   | SPRINT-001
    P-prefix    | P-001        | PROJECT-001
    PROJECT-    | PROJECT-001  | PROJECT-001
    No prefix   | 001          | (requires type hint)

The module ensures all IDs are normalized to a consistent format
while accepting legacy formats for backward compatibility.

Usage:
    from cf_core.models.identifiers import (
        normalize_task_id,
        normalize_sprint_id,
        normalize_project_id,
        generate_task_id,
    )

    # Normalize existing IDs
    task_id = normalize_task_id("T-001")      # → "TASK-001"
    task_id = normalize_task_id("TASK-001")   # → "TASK-001"

    # Generate new IDs
    task_id = generate_task_id()              # → "TASK-a1b2c3d4"
"""

from __future__ import annotations

import re
import uuid
from typing import Literal

# =============================================================================
# ID Prefix Constants
# =============================================================================

class IDPrefix:
    """Standard ID prefixes for ContextForge entities."""

    TASK = "TASK"
    SPRINT = "SPRINT"
    PROJECT = "PROJECT"
    ACTION = "ACTION"
    COMMENT = "COMMENT"
    BLOCKER = "BLOCKER"


# Legacy prefix mappings (old → new)
LEGACY_PREFIXES: dict[str, str] = {
    "T": IDPrefix.TASK,
    "S": IDPrefix.SPRINT,
    "P": IDPrefix.PROJECT,
    "A": IDPrefix.ACTION,
    "C": IDPrefix.COMMENT,
    "B": IDPrefix.BLOCKER,
}


# =============================================================================
# ID Patterns
# =============================================================================

# Pattern components
_ID_SUFFIX = r"[a-zA-Z0-9_-]+"

# Full ID patterns with optional prefixes
TASK_ID_PATTERN = re.compile(
    rf"^(?:TASK-|T-)?({_ID_SUFFIX})$",
    re.IGNORECASE,
)

SPRINT_ID_PATTERN = re.compile(
    rf"^(?:SPRINT-|S-)?({_ID_SUFFIX})$",
    re.IGNORECASE,
)

PROJECT_ID_PATTERN = re.compile(
    rf"^(?:PROJECT-|P-)?({_ID_SUFFIX})$",
    re.IGNORECASE,
)

ACTION_ID_PATTERN = re.compile(
    rf"^(?:ACTION-|A-)?({_ID_SUFFIX})$",
    re.IGNORECASE,
)


# =============================================================================
# Normalization Functions
# =============================================================================

def normalize_task_id(task_id: str) -> str:
    """Normalize a task ID to TASK-xxx format.

    Accepts:
        - "T-001" → "TASK-001"
        - "TASK-001" → "TASK-001"
        - "task-abc" → "TASK-abc"
        - "001" → "TASK-001" (bare suffix)

    Args:
        task_id: Raw task ID string

    Returns:
        Normalized task ID with TASK- prefix

    Raises:
        ValueError: If task_id format is invalid
    """
    return _normalize_id(task_id, IDPrefix.TASK, TASK_ID_PATTERN)


def normalize_sprint_id(sprint_id: str) -> str:
    """Normalize a sprint ID to SPRINT-xxx format.

    Accepts:
        - "S-001" → "SPRINT-001"
        - "SPRINT-001" → "SPRINT-001"
        - "001" → "SPRINT-001"

    Args:
        sprint_id: Raw sprint ID string

    Returns:
        Normalized sprint ID with SPRINT- prefix

    Raises:
        ValueError: If sprint_id format is invalid
    """
    return _normalize_id(sprint_id, IDPrefix.SPRINT, SPRINT_ID_PATTERN)


def normalize_project_id(project_id: str) -> str:
    """Normalize a project ID to PROJECT-xxx format.

    Accepts:
        - "P-001" → "PROJECT-001"
        - "PROJECT-001" → "PROJECT-001"
        - "001" → "PROJECT-001"

    Args:
        project_id: Raw project ID string

    Returns:
        Normalized project ID with PROJECT- prefix

    Raises:
        ValueError: If project_id format is invalid
    """
    return _normalize_id(project_id, IDPrefix.PROJECT, PROJECT_ID_PATTERN)


def normalize_action_id(action_id: str) -> str:
    """Normalize an action item ID to ACTION-xxx format.

    Args:
        action_id: Raw action ID string

    Returns:
        Normalized action ID with ACTION- prefix

    Raises:
        ValueError: If action_id format is invalid
    """
    return _normalize_id(action_id, IDPrefix.ACTION, ACTION_ID_PATTERN)


def _normalize_id(raw_id: str, prefix: str, pattern: re.Pattern[str]) -> str:
    """Internal ID normalization helper.

    Args:
        raw_id: Raw ID string
        prefix: Target prefix (TASK, SPRINT, etc.)
        pattern: Regex pattern for validation

    Returns:
        Normalized ID string

    Raises:
        ValueError: If ID format is invalid
    """
    if not raw_id:
        raise ValueError(f"Empty {prefix.lower()} ID")

    raw_id = raw_id.strip()
    match = pattern.match(raw_id)

    if match:
        suffix = match.group(1)
        return f"{prefix}-{suffix}"

    # If no match, try treating the whole string as a suffix
    if re.match(rf"^{_ID_SUFFIX}$", raw_id):
        return f"{prefix}-{raw_id}"

    raise ValueError(
        f"Invalid {prefix.lower()} ID format: '{raw_id}'. "
        f"Expected format: {prefix}-xxx or xxx"
    )


# =============================================================================
# ID Generation
# =============================================================================

def generate_task_id() -> str:
    """Generate a new unique task ID.

    Returns:
        New task ID in format TASK-xxxxxxxx (8 char UUID prefix)
    """
    return _generate_id(IDPrefix.TASK)


def generate_sprint_id() -> str:
    """Generate a new unique sprint ID.

    Returns:
        New sprint ID in format SPRINT-xxxxxxxx
    """
    return _generate_id(IDPrefix.SPRINT)


def generate_project_id() -> str:
    """Generate a new unique project ID.

    Returns:
        New project ID in format PROJECT-xxxxxxxx
    """
    return _generate_id(IDPrefix.PROJECT)


def generate_action_id() -> str:
    """Generate a new unique action item ID.

    Returns:
        New action ID in format ACTION-xxxxxxxx
    """
    return _generate_id(IDPrefix.ACTION)


def _generate_id(prefix: str, length: int = 8) -> str:
    """Generate a unique ID with the given prefix.

    Args:
        prefix: ID prefix (TASK, SPRINT, etc.)
        length: Length of UUID suffix (default 8)

    Returns:
        Formatted ID string
    """
    suffix = uuid.uuid4().hex[:length]
    return f"{prefix}-{suffix}"


# =============================================================================
# Validation Functions
# =============================================================================

def is_valid_task_id(task_id: str) -> bool:
    """Check if a string is a valid task ID.

    Args:
        task_id: String to validate

    Returns:
        True if valid task ID format
    """
    return _is_valid_id(task_id, TASK_ID_PATTERN)


def is_valid_sprint_id(sprint_id: str) -> bool:
    """Check if a string is a valid sprint ID.

    Args:
        sprint_id: String to validate

    Returns:
        True if valid sprint ID format
    """
    return _is_valid_id(sprint_id, SPRINT_ID_PATTERN)


def is_valid_project_id(project_id: str) -> bool:
    """Check if a string is a valid project ID.

    Args:
        project_id: String to validate

    Returns:
        True if valid project ID format
    """
    return _is_valid_id(project_id, PROJECT_ID_PATTERN)


def _is_valid_id(raw_id: str, pattern: re.Pattern[str]) -> bool:
    """Check if ID matches the expected pattern.

    Args:
        raw_id: ID string to validate
        pattern: Regex pattern for validation

    Returns:
        True if valid
    """
    if not raw_id:
        return False
    return bool(pattern.match(raw_id.strip()))


# =============================================================================
# ID Extraction
# =============================================================================

def extract_id_suffix(full_id: str) -> str:
    """Extract the suffix portion of an ID (without prefix).

    Args:
        full_id: Full ID string (e.g., "TASK-001")

    Returns:
        Suffix portion (e.g., "001")

    Examples:
        >>> extract_id_suffix("TASK-001")
        '001'
        >>> extract_id_suffix("T-abc123")
        'abc123'
    """
    if "-" in full_id:
        return full_id.split("-", 1)[1]
    return full_id


def extract_id_prefix(full_id: str) -> str | None:
    """Extract the prefix portion of an ID.

    Args:
        full_id: Full ID string

    Returns:
        Prefix portion or None if no prefix

    Examples:
        >>> extract_id_prefix("TASK-001")
        'TASK'
        >>> extract_id_prefix("001")
        None
    """
    if "-" in full_id:
        return full_id.split("-", 1)[0].upper()
    return None


def get_id_type(full_id: str) -> str | None:
    """Determine the entity type from an ID.

    Args:
        full_id: Full ID string

    Returns:
        Entity type ("task", "sprint", "project", etc.) or None

    Examples:
        >>> get_id_type("TASK-001")
        'task'
        >>> get_id_type("S-001")
        'sprint'
    """
    prefix = extract_id_prefix(full_id)
    if not prefix:
        return None

    # Check standard prefixes
    type_map = {
        IDPrefix.TASK: "task",
        IDPrefix.SPRINT: "sprint",
        IDPrefix.PROJECT: "project",
        IDPrefix.ACTION: "action",
        IDPrefix.COMMENT: "comment",
        IDPrefix.BLOCKER: "blocker",
    }

    if prefix in type_map:
        return type_map[prefix]

    # Check legacy prefixes
    if prefix in LEGACY_PREFIXES:
        standard_prefix = LEGACY_PREFIXES[prefix]
        return type_map.get(standard_prefix)

    return None


# =============================================================================
# Type Aliases
# =============================================================================

EntityType = Literal["task", "sprint", "project", "action", "comment", "blocker"]


__all__ = [
    # Classes
    "IDPrefix",
    # Constants
    "LEGACY_PREFIXES",
    "TASK_ID_PATTERN",
    "SPRINT_ID_PATTERN",
    "PROJECT_ID_PATTERN",
    "ACTION_ID_PATTERN",
    # Normalization
    "normalize_task_id",
    "normalize_sprint_id",
    "normalize_project_id",
    "normalize_action_id",
    # Generation
    "generate_task_id",
    "generate_sprint_id",
    "generate_project_id",
    "generate_action_id",
    # Validation
    "is_valid_task_id",
    "is_valid_sprint_id",
    "is_valid_project_id",
    # Extraction
    "extract_id_suffix",
    "extract_id_prefix",
    "get_id_type",
    # Types
    "EntityType",
]
