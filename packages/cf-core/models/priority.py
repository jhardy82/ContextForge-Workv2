"""ContextForge Unified Priority Module.

Provides a unified Priority class that accepts both string and integer
representations, enabling interoperability between cf_core (string-based)
and MCP/TaskMan (integer-based) priority systems.

Priority Mapping:
    Integer | String   | Display Name
    --------|----------|-------------
    0       | none     | No Priority
    1       | urgent   | Urgent (P1)
    2       | high     | High (P2)
    3       | medium   | Medium (P3)
    4       | low      | Low (P4)
    5       | critical | Critical (P0) - cf_core extension

Bidirectional Conversion:
    - Priority.from_int(1) → Priority.URGENT
    - Priority.from_string("high") → Priority.HIGH
    - Priority.MEDIUM.to_int() → 3
    - Priority.LOW.to_string() → "low"

Usage:
    from cf_core.models.priority import Priority, normalize_priority

    # Accept any format
    p = normalize_priority("high")    # → Priority.HIGH
    p = normalize_priority(2)         # → Priority.HIGH
    p = normalize_priority("P2")      # → Priority.HIGH

    # Use in models
    class Task(BaseModel):
        priority: Priority = Priority.MEDIUM
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

# =============================================================================
# Priority Aliases
# =============================================================================

PRIORITY_ALIASES: dict[str, str] = {
    # P-notation (common in project management)
    "p0": "critical",
    "p1": "urgent",
    "p2": "high",
    "p3": "medium",
    "p4": "low",
    "p5": "none",
    # Alternative names
    "highest": "critical",
    "important": "high",
    "normal": "medium",
    "minor": "low",
    "trivial": "none",
    "default": "medium",
    # Integer strings
    "0": "none",
    "1": "urgent",
    "2": "high",
    "3": "medium",
    "4": "low",
    "5": "critical",
}


# =============================================================================
# Priority Enum
# =============================================================================

class Priority(str, Enum):
    """Unified priority enum with bidirectional int/string conversion.

    Supports both cf_core string-based ("low", "medium", "high", "critical")
    and MCP integer-based (0-4) priority systems.

    The integer mapping follows TaskMan MCP conventions:
        0 = No priority (None/Unset)
        1 = Urgent (highest urgency)
        2 = High
        3 = Medium (Normal)
        4 = Low

    cf_core extends with CRITICAL (5) for "stop everything" scenarios.
    """

    NONE = "none"
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

    @classmethod
    def from_int(cls, value: int) -> Priority:
        """Create Priority from integer value.

        Args:
            value: Integer priority (0-5)

        Returns:
            Corresponding Priority enum

        Raises:
            ValueError: If value is not in valid range
        """
        int_map = {
            0: cls.NONE,
            1: cls.URGENT,
            2: cls.HIGH,
            3: cls.MEDIUM,
            4: cls.LOW,
            5: cls.CRITICAL,
        }
        if value not in int_map:
            raise ValueError(f"Invalid priority integer: {value}. Valid: 0-5")
        return int_map[value]

    @classmethod
    def from_string(cls, value: str) -> Priority:
        """Create Priority from string value.

        Args:
            value: String priority (case-insensitive, supports aliases)

        Returns:
            Corresponding Priority enum

        Raises:
            ValueError: If value is not a valid priority
        """
        normalized = normalize_priority_string(value)
        try:
            return cls(normalized)
        except ValueError:
            valid = ", ".join(p.value for p in cls)
            raise ValueError(f"Invalid priority '{value}'. Valid: {valid}")

    @classmethod
    def from_any(cls, value: int | str | Priority) -> Priority:
        """Create Priority from any supported type.

        Args:
            value: Priority as int, string, or Priority enum

        Returns:
            Priority enum

        Raises:
            ValueError: If value cannot be converted
        """
        if isinstance(value, Priority):
            return value
        if isinstance(value, int):
            return cls.from_int(value)
        if isinstance(value, str):
            # Check if string is an integer
            if value.isdigit():
                return cls.from_int(int(value))
            return cls.from_string(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to Priority")

    def to_int(self) -> int:
        """Convert Priority to integer representation.

        Returns:
            Integer value (0-5)
        """
        int_map = {
            Priority.NONE: 0,
            Priority.URGENT: 1,
            Priority.HIGH: 2,
            Priority.MEDIUM: 3,
            Priority.LOW: 4,
            Priority.CRITICAL: 5,
        }
        return int_map[self]

    def to_string(self) -> str:
        """Convert Priority to string representation.

        Returns:
            Lowercase string value
        """
        return self.value

    @property
    def display_name(self) -> str:
        """Get human-readable display name."""
        display_map = {
            Priority.NONE: "No Priority",
            Priority.URGENT: "Urgent (P1)",
            Priority.HIGH: "High (P2)",
            Priority.MEDIUM: "Medium (P3)",
            Priority.LOW: "Low (P4)",
            Priority.CRITICAL: "Critical (P0)",
        }
        return display_map[self]

    @property
    def sort_order(self) -> int:
        """Get sort order (lower = higher priority).

        Critical and Urgent sort first, None sorts last.
        """
        order_map = {
            Priority.CRITICAL: 0,
            Priority.URGENT: 1,
            Priority.HIGH: 2,
            Priority.MEDIUM: 3,
            Priority.LOW: 4,
            Priority.NONE: 5,
        }
        return order_map[self]

    @property
    def is_high_priority(self) -> bool:
        """Check if priority is considered high (critical, urgent, high)."""
        return self in (Priority.CRITICAL, Priority.URGENT, Priority.HIGH)

    @property
    def is_low_priority(self) -> bool:
        """Check if priority is considered low (low, none)."""
        return self in (Priority.LOW, Priority.NONE)

    @property
    def color(self) -> str:
        """Get color code for UI rendering.

        Returns:
            CSS-compatible color name for priority visualization
        """
        color_map = {
            Priority.CRITICAL: "red",
            Priority.URGENT: "orange",
            Priority.HIGH: "orange",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green",
            Priority.NONE: "gray",
        }
        return color_map[self]

    @property
    def score(self) -> int:
        """Get numeric score for priority sorting and calculations.

        Returns:
            Integer score (higher = more important)
        """
        score_map = {
            Priority.CRITICAL: 5,
            Priority.URGENT: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
            Priority.NONE: 0,
        }
        return score_map[self]

    def __lt__(self, other: Priority) -> bool:
        """Compare priorities (lower priority < higher priority)."""
        if not isinstance(other, Priority):
            return NotImplemented
        return self.sort_order > other.sort_order

    def __le__(self, other: Priority) -> bool:
        """Compare priorities (lower priority <= higher priority)."""
        if not isinstance(other, Priority):
            return NotImplemented
        return self.sort_order >= other.sort_order

    def __gt__(self, other: Priority) -> bool:
        """Compare priorities (higher priority > lower priority)."""
        if not isinstance(other, Priority):
            return NotImplemented
        return self.sort_order < other.sort_order

    def __ge__(self, other: Priority) -> bool:
        """Compare priorities."""
        if not isinstance(other, Priority):
            return NotImplemented
        return self.sort_order <= other.sort_order


# =============================================================================
# Normalization Functions
# =============================================================================

def normalize_priority_string(value: str) -> str:
    """Normalize a priority string, applying aliases.

    Args:
        value: Raw priority string

    Returns:
        Normalized priority string (lowercase, alias-resolved)

    Examples:
        >>> normalize_priority_string("HIGH")
        'high'
        >>> normalize_priority_string("P2")
        'high'
        >>> normalize_priority_string("important")
        'high'
    """
    normalized = value.lower().strip()
    return PRIORITY_ALIASES.get(normalized, normalized)


def normalize_priority(value: int | str | Priority) -> Priority:
    """Normalize any priority value to Priority enum.

    This is the main entry point for priority normalization,
    accepting integers, strings, and Priority enums.

    Args:
        value: Priority in any supported format

    Returns:
        Priority enum

    Examples:
        >>> normalize_priority(2)
        <Priority.HIGH: 'high'>
        >>> normalize_priority("P1")
        <Priority.URGENT: 'urgent'>
        >>> normalize_priority("medium")
        <Priority.MEDIUM: 'medium'>
    """
    return Priority.from_any(value)


def is_valid_priority(value: int | str) -> bool:
    """Check if a value is a valid priority.

    Args:
        value: Priority value to validate

    Returns:
        True if valid priority
    """
    try:
        normalize_priority(value)
        return True
    except ValueError:
        return False


# =============================================================================
# Type Aliases
# =============================================================================

PriorityLiteral = Literal["none", "urgent", "high", "medium", "low", "critical"]
PriorityInt = Literal[0, 1, 2, 3, 4, 5]
PriorityInput = PriorityLiteral | PriorityInt | Priority


# =============================================================================
# Default Priority
# =============================================================================

DEFAULT_PRIORITY = Priority.MEDIUM


__all__ = [
    # Enum
    "Priority",
    # Constants
    "PRIORITY_ALIASES",
    "DEFAULT_PRIORITY",
    # Type Aliases
    "PriorityLiteral",
    "PriorityInt",
    "PriorityInput",
    # Functions
    "normalize_priority",
    "normalize_priority_string",
    "is_valid_priority",
]
