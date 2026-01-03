from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContextBase(BaseModel):
    """Base Context model."""
    kind: str
    title: str
    summary: str | None = None
    confidence: float = 1.0

    # Dimensions (Flattened for now)
    dim_motivational: str | None = None
    dim_relational: str | None = None
    dim_temporal: str | None = None
    dim_spatial: str | None = None
    dim_resource: str | None = None
    dim_operational: str | None = None
    dim_risk: str | None = None
    dim_policy: str | None = None
    dim_knowledge: str | None = None
    dim_signal: str | None = None
    dim_outcome: str | None = None
    dim_emergent: str | None = None
    dim_cultural: str | None = None

class ContextResponse(ContextBase):
    """Context Response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ContextAncestor(BaseModel):
    id: UUID
    title: str

class ContextResolved(BaseModel):
    """Resolved Context with merged attributes."""
    id: UUID | None
    title: str | None
    kind: str | None
    attributes: dict = Field(default_factory=dict)
    ancestors: list[ContextAncestor] = Field(default_factory=list)
