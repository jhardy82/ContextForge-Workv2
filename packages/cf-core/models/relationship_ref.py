"""
Relationship Reference Model

Used for multi-project and multi-sprint associations in tasks.
"""

from pydantic import BaseModel, Field


class RelationshipRef(BaseModel):
    """Reference to a related entity with relationship type."""

    model_config = {"extra": "forbid"}

    id: str = Field(description="Related entity ID")
    relationship_type: str = Field(
        description="Type of relationship (e.g., 'depends_on', 'blocks', 'related')"
    )
