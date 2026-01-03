"""
Context Node Domain Entity
Represents a semantic unit of code (Class, Function, Module) in the Knowledge Graph.
"""
from typing import Literal

from pydantic import BaseModel, Field


class ContextNode(BaseModel):
    """
    Represents a code entity in the context graph.
    Mapped from AST nodes parsed by Tree-Sitter.
    """
    id: str = Field(description="Unique identifier (e.g., file_path::class::method)")
    type: Literal["module", "class", "function", "method", "import"] = Field(description="Type of the code entity")
    name: str = Field(description="Name of the entity")
    file_path: str = Field(description="Relative path to the file")
    start_line: int = Field(description="Start line number (0-indexed)")
    end_line: int = Field(description="End line number (0-indexed)")

    # Relationships
    parent_id: str | None = Field(default=None, description="ID of the parent node (e.g., class for a method)")
    dependencies: list[str] = Field(default_factory=list, description="List of node IDs this node depends on")

    # Metadata
    docstring: str | None = Field(default=None, description="Extracted docstring")
    complexity: int | None = Field(default=None, description="Cyclomatic complexity (optional)")

    class Config:
        frozen = True
