"""Context domain model for cf_core.

Provides a rich Pydantic v2 model for Context entities with:
- UCL compliance (no orphans allowed without parent)
- COF dimensional context support
- Hierarchical context relationships
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ContextType = Literal["project", "sprint", "task", "document", "artifact", "decision"]


class Context(BaseModel):
    """Domain model for Context entities (COF/UCL compliant).

    Attributes:
        id: Unique context identifier
        parent_id: Parent context ID (UCL: no orphans)
        context_type: Type of context
        name: Context name
        description: Optional description
        metadata: Flexible metadata dictionary
        tags: List of tags
        created_at: Creation timestamp
        updated_at: Last update timestamp
        evidence_bundle_hash: SHA-256 hash of evidence bundle
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., min_length=1)
    parent_id: str | None = Field(default=None)
    context_type: ContextType = Field(default="artifact")
    name: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    evidence_bundle_hash: str | None = Field(default=None)

    def is_orphan(self) -> bool:
        """Check if context is orphaned (no parent and not root type)."""
        # Projects can be root contexts without parents
        if self.context_type == "project":
            return False
        return self.parent_id is None

    def has_evidence(self) -> bool:
        """Check if context has associated evidence."""
        return self.evidence_bundle_hash is not None


__all__ = ["Context", "ContextType"]
