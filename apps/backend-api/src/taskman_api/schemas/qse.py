from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvidenceBase(BaseModel):
    artifact_type: str
    artifact_path: str | None = None
    task_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] | None = Field(default_factory=dict, alias="metadata_")

    class Config:
        populate_by_name = True


class EvidenceCreate(EvidenceBase):
    """Schema for creating evidence (e.g. from CLI sync)."""

    # For file evidence, the file content might be uploaded or just the path/metadata
    # For now, expecting CLI to calculate hash and send metadata, or upload file separately?
    # CLI qse.py seems to calculate hash locally.
    # The API endpoint likely receives the metadata record to store in DB.
    artifact_hash: str | None = None
    file_size_bytes: int | None = None
    collected_via: str | None = "api"


class EvidenceResponse(EvidenceBase):
    id: str
    artifact_hash: str | None = None
    file_size_bytes: int | None = None
    collected_at: datetime
    collected_by: str | None = None

    class Config:
        from_attributes = True


class GateBase(BaseModel):
    name: str
    description: str | None = None
    gate_type: str = "custom"
    threshold_value: float | None = None
    threshold_operator: str = ">="
    severity: str = "error"
    criteria: dict[str, Any] | None = None
    enabled: bool = True


class GateCreate(GateBase):
    """Schema for creating a quality gate."""

    pass


class GateResponse(GateBase):
    id: str
    created_at: datetime
    created_by: str | None = None

    class Config:
        from_attributes = True


class EvaluationCreate(BaseModel):
    """Schema for recording a gate evaluation."""

    gate_name: str
    actual_value: float
    task_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    id: str
    gate_id: str
    task_id: str | None = None
    actual_value: float
    passed: bool
    evidence_ids: list[str]
    evaluated_at: datetime
    evaluated_by: str | None = None

    class Config:
        from_attributes = True
