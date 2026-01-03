"""Hierarchical ID generator for cf_core entities.

Provides meaningful, hierarchical ID generation following conventions:
- Project IDs: P-{SHORTNAME} derived from project name
- Sprint IDs: S-{PROJECT}-{YYYYWW} or S-{PROJECT}-{SEQ}
- Task IDs: T-{PROJECT}-{SEQ} or T-{SPRINT}-{SEQ}
- Action IDs: A-{PARENT}-{SEQ}
- Velocity IDs: VM-{TASK}-{YYYYMMDD}

This ensures IDs are:
1. Human-readable and indicative of provenance
2. Hierarchical (child IDs include parent reference)
3. Deterministic when given the same inputs
4. Unique within their scope
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Literal


class IDGenerator:
    """Centralized ID generator for all cf_core entities.

    Implements naming conventions that create meaningful, hierarchical IDs
    rather than random UUIDs.
    """

    # Counters for sequential IDs (would be persisted in production)
    _counters: dict[str, int] = {}

    @classmethod
    def reset_counters(cls) -> None:
        """Reset all counters (useful for testing)."""
        cls._counters = {}

    @classmethod
    def _slugify(cls, text: str, max_length: int = 20) -> str:
        """Convert text to a URL-safe slug.

        Args:
            text: Input text to slugify
            max_length: Maximum length of resulting slug

        Returns:
            Slugified text (uppercase, alphanumeric + hyphens)
        """
        # Normalize unicode characters
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ASCII", "ignore").decode("ASCII")

        # Convert to uppercase and replace spaces/special chars
        text = text.upper()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text).strip("-")

        # Truncate to max_length
        return text[:max_length]

    @classmethod
    def _get_next_seq(cls, scope: str) -> int:
        """Get next sequential number for a given scope.

        Args:
            scope: The scope/context for the counter

        Returns:
            Next sequential number
        """
        current = cls._counters.get(scope, 0)
        cls._counters[scope] = current + 1
        return current + 1

    @classmethod
    def project_id(cls, name: str) -> str:
        """Generate a project ID from project name.

        Format: P-{SHORTNAME}
        Example: "TaskMan v2 Migration" -> "P-TASKMAN-V2-MIGRATION"

        Args:
            name: Project name

        Returns:
            Project ID string
        """
        slug = cls._slugify(name, max_length=30)
        return f"P-{slug}"

    @classmethod
    def project_id_short(cls, name: str, max_words: int = 3) -> str:
        """Generate a shorter project ID using first few words.

        Format: P-{SHORT}
        Example: "TaskMan v2 Migration" -> "P-TASKMAN-V2"

        Args:
            name: Project name
            max_words: Maximum number of words to include

        Returns:
            Project ID string
        """
        words = name.split()[:max_words]
        slug = cls._slugify("-".join(words), max_length=20)
        return f"P-{slug}"

    @classmethod
    def sprint_id(
        cls,
        project_id: str,
        identifier: str | None = None,
        use_week: bool = True,
    ) -> str:
        """Generate a sprint ID with project provenance.

        Format: S-{PROJECT_SHORT}-{YYYYWW} or S-{PROJECT_SHORT}-{SEQ}
        Example: "P-TASKMAN-V2" -> "S-TASKMAN-V2-2025W48"

        Args:
            project_id: Parent project ID
            identifier: Optional explicit identifier (week or name)
            use_week: If True and no identifier, use YYYYWW format

        Returns:
            Sprint ID string
        """
        # Extract project shortname (remove P- prefix)
        project_short = project_id.replace("P-", "", 1)

        if identifier:
            slug = cls._slugify(identifier, max_length=15)
            return f"S-{project_short}-{slug}"
        elif use_week:
            now = datetime.utcnow()
            week = now.strftime("%YW%W")
            return f"S-{project_short}-{week}"
        else:
            seq = cls._get_next_seq(f"sprint:{project_id}")
            return f"S-{project_short}-{seq:03d}"

    @classmethod
    def task_id(
        cls,
        project_id: str | None = None,
        sprint_id: str | None = None,
        title: str | None = None,
    ) -> str:
        """Generate a task ID with hierarchical provenance.

        Format: T-{PARENT_SHORT}-{SEQ} or T-{TITLE_SLUG}-{SEQ}
        Example: "P-TASKMAN" -> "T-TASKMAN-001"

        Args:
            project_id: Parent project ID (preferred)
            sprint_id: Parent sprint ID (if no project)
            title: Task title for slug-based ID (fallback)

        Returns:
            Task ID string
        """
        if project_id:
            parent_short = project_id.replace("P-", "", 1)
            scope = f"task:{project_id}"
        elif sprint_id:
            # Extract sprint's project portion
            parent_short = sprint_id.replace("S-", "", 1).split("-")[0]
            scope = f"task:{sprint_id}"
        elif title:
            parent_short = cls._slugify(title, max_length=15)
            scope = f"task:{parent_short}"
        else:
            parent_short = "UNASSIGNED"
            scope = "task:unassigned"

        seq = cls._get_next_seq(scope)
        return f"T-{parent_short}-{seq:03d}"

    @classmethod
    def action_id(
        cls,
        parent_id: str,
        parent_type: Literal["project", "sprint", "task"],
    ) -> str:
        """Generate an action item ID with parent provenance.

        Format: A-{PARENT_SHORT}-{SEQ}
        Example: "T-TASKMAN-001" -> "A-TASKMAN-001-01"

        Args:
            parent_id: Parent entity ID
            parent_type: Type of parent ('project', 'sprint', 'task')

        Returns:
            Action item ID string
        """
        # Remove prefix from parent ID
        prefix_map = {"project": "P-", "sprint": "S-", "task": "T-"}
        prefix = prefix_map.get(parent_type, "")
        parent_short = parent_id.replace(prefix, "", 1)

        scope = f"action:{parent_id}"
        seq = cls._get_next_seq(scope)
        return f"A-{parent_short}-{seq:02d}"

    @classmethod
    def velocity_metric_id(cls, task_id: str | None = None) -> str:
        """Generate a velocity metric ID.

        Format: VM-{TASK_SHORT}-{YYYYMMDD} or VM-{YYYYMMDD}-{SEQ}

        Args:
            task_id: Associated task ID (optional)

        Returns:
            Velocity metric ID string
        """
        date_str = datetime.utcnow().strftime("%Y%m%d")

        if task_id:
            task_short = task_id.replace("T-", "", 1)[:15]
            return f"VM-{task_short}-{date_str}"
        else:
            seq = cls._get_next_seq(f"velocity:{date_str}")
            return f"VM-{date_str}-{seq:03d}"

    @classmethod
    def context_id(cls, parent_id: str | None = None, name: str | None = None) -> str:
        """Generate a context ID.

        Format: CTX-{PARENT_SHORT}-{SEQ} or CTX-{NAME_SLUG}

        Args:
            parent_id: Parent context ID
            name: Context name for slug

        Returns:
            Context ID string
        """
        if parent_id:
            parent_short = parent_id.replace("CTX-", "", 1)[:15]
            scope = f"context:{parent_id}"
            seq = cls._get_next_seq(scope)
            return f"CTX-{parent_short}-{seq:02d}"
        elif name:
            slug = cls._slugify(name, max_length=20)
            return f"CTX-{slug}"
        else:
            seq = cls._get_next_seq("context:root")
            return f"CTX-ROOT-{seq:03d}"


# Convenience functions for direct import
def generate_project_id(name: str, short: bool = False) -> str:
    """Generate a project ID from name."""
    if short:
        return IDGenerator.project_id_short(name)
    return IDGenerator.project_id(name)


def generate_sprint_id(
    project_id: str,
    identifier: str | None = None,
    use_week: bool = True,
) -> str:
    """Generate a sprint ID with project provenance."""
    return IDGenerator.sprint_id(project_id, identifier, use_week)


def generate_task_id(
    project_id: str | None = None,
    sprint_id: str | None = None,
    title: str | None = None,
) -> str:
    """Generate a task ID with hierarchical provenance."""
    return IDGenerator.task_id(project_id, sprint_id, title)


def generate_action_id(
    parent_id: str,
    parent_type: Literal["project", "sprint", "task"],
) -> str:
    """Generate an action item ID with parent provenance."""
    return IDGenerator.action_id(parent_id, parent_type)


__all__ = [
    "IDGenerator",
    "generate_project_id",
    "generate_sprint_id",
    "generate_task_id",
    "generate_action_id",
]
