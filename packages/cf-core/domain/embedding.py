"""
Embedding Domain Model
Represents a vector embedding for a ContextNode.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """
    Represents a vector embedding for a context node.
    """
    node_id: str = Field(description="ID of the ContextNode this embedding belongs to")
    vector: list[float] = Field(description="The high-dimensional vector representation")
    dimensions: int = Field(description="Dimension count of the vector (e.g., 384)")
    model_name: str = Field(description="Name of the model used to generate this embedding")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for retrieval")

    class Config:
        frozen = True
