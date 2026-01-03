from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    ForeignKey,
    Numeric,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseRepository

# =============================================================================
# Models
# =============================================================================


class QSEEvidenceModel(Base):
    __tablename__ = "qse_evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # EVD-{timestamp}
    artifact_type: Mapped[str] = mapped_column(String, nullable=False)
    artifact_path: Mapped[str | None] = mapped_column(String)
    artifact_hash: Mapped[str | None] = mapped_column(String)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    task_id: Mapped[str | None] = mapped_column(String, index=True)
    session_id: Mapped[str | None] = mapped_column(String, index=True)
    sprint_id: Mapped[str | None] = mapped_column(String)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    collected_by: Mapped[str | None] = mapped_column(String)
    collected_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class QSEQualityGateModel(Base):
    __tablename__ = "qse_quality_gates"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # GATE-{name}
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    gate_type: Mapped[str] = mapped_column(String, nullable=False)
    threshold_value: Mapped[float | None] = mapped_column(Numeric)
    threshold_operator: Mapped[str] = mapped_column(String, default=">=")
    severity: Mapped[str] = mapped_column(String, default="error")
    criteria: Mapped[dict | None] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())


class QSEGateEvaluationModel(Base):
    __tablename__ = "qse_gate_evaluations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    gate_id: Mapped[str] = mapped_column(String, ForeignKey("qse_quality_gates.id"), index=True)
    task_id: Mapped[str | None] = mapped_column(String)
    sprint_id: Mapped[str | None] = mapped_column(String)
    actual_value: Mapped[float | None] = mapped_column(Numeric)
    passed: Mapped[bool | None] = mapped_column(Boolean)
    evidence_ids: Mapped[list[str] | None] = mapped_column(
        JSON
    )  # Store as JSON list for SQLite compatibility
    evaluated_by: Mapped[str | None] = mapped_column(String)
    evaluated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )


class QSESessionModel(Base):
    __tablename__ = "qse_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    task_ids: Mapped[list[str] | None] = mapped_column(JSON)
    sprint_id: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active")
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    end_time: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    summary: Mapped[str | None] = mapped_column(String)
    created_by: Mapped[str | None] = mapped_column(String)


class QSEComplianceChecklistModel(Base):
    __tablename__ = "qse_compliance_checklist"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    checklist_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    item_description: Mapped[str | None] = mapped_column(String)
    gate_id: Mapped[str | None] = mapped_column(String)
    evidence_id: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    checked_by: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())


# =============================================================================
# Repository
# =============================================================================


class QSERepository(BaseRepository[QSEEvidenceModel]):
    """Repository for all QSE operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, QSEEvidenceModel)

    # --- Evidence ---
    async def create_evidence(self, id: str, **kwargs) -> QSEEvidenceModel:
        # We override standard create because ID is manually generated in Service usually, or here.
        # But BaseRepository.create takes kwargs.
        instance = QSEEvidenceModel(id=id, **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def list_evidence(
        self,
        artifact_type: str | None = None,
        task_id: str | None = None,
        session_id: str | None = None,
        limit: int = 20,
    ) -> list[QSEEvidenceModel]:
        stmt = select(QSEEvidenceModel).limit(limit).order_by(QSEEvidenceModel.collected_at.desc())
        if artifact_type:
            stmt = stmt.where(QSEEvidenceModel.artifact_type == artifact_type)
        if task_id:
            stmt = stmt.where(QSEEvidenceModel.task_id == task_id)
        if session_id:
            stmt = stmt.where(QSEEvidenceModel.session_id == session_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_evidence(self, id: str) -> QSEEvidenceModel | None:
        """Get evidence by ID."""
        return await self.session.get(QSEEvidenceModel, id)

    # --- Gates ---
    async def create_gate(self, id: str, **kwargs) -> QSEQualityGateModel:
        instance = QSEQualityGateModel(id=id, **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def list_gates(
        self, gate_type: str | None = None, enabled_only: bool = True
    ) -> list[QSEQualityGateModel]:
        stmt = select(QSEQualityGateModel).order_by(QSEQualityGateModel.name)
        if gate_type:
            stmt = stmt.where(QSEQualityGateModel.gate_type == gate_type)
        if enabled_only:
            stmt = stmt.where(QSEQualityGateModel.enabled == True)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_gate(self, gate_id: str) -> QSEQualityGateModel | None:
        return await self.session.get(QSEQualityGateModel, gate_id)

    async def get_gate_by_name(self, name: str) -> QSEQualityGateModel | None:
        """Retrieve a gate by its unique name."""
        stmt = select(QSEQualityGateModel).where(QSEQualityGateModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_evaluation(self, id: str, **kwargs) -> QSEGateEvaluationModel:
        instance = QSEGateEvaluationModel(id=id, **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_gate_evaluations(
        self, gate_id: str, task_id: str | None = None
    ) -> list[QSEGateEvaluationModel]:
        stmt = (
            select(QSEGateEvaluationModel)
            .where(QSEGateEvaluationModel.gate_id == gate_id)
            .order_by(QSEGateEvaluationModel.evaluated_at.desc())
        )
        if task_id:
            stmt = stmt.where(QSEGateEvaluationModel.task_id == task_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Sessions ---
    async def create_session(self, id: str, **kwargs) -> QSESessionModel:
        instance = QSESessionModel(id=id, **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update_session(self, session_id: str, **kwargs) -> QSESessionModel | None:
        stmt = select(QSESessionModel).where(QSESessionModel.id == session_id)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        if not instance:
            return None

        for k, v in kwargs.items():
            setattr(instance, k, v)
        await self.session.flush()
        return instance

    async def list_sessions(
        self, status: str | None = None, limit: int = 20
    ) -> list[QSESessionModel]:
        stmt = select(QSESessionModel).limit(limit).order_by(QSESessionModel.start_time.desc())
        if status:
            stmt = stmt.where(QSESessionModel.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_session(self, session_id: str) -> QSESessionModel | None:
        return await self.session.get(QSESessionModel, session_id)

    # --- Compliance ---
    async def create_compliance_item(self, id: str, **kwargs) -> QSEComplianceChecklistModel:
        instance = QSEComplianceChecklistModel(id=id, **kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def list_compliance(
        self, checklist_name: str | None = None, gate_id: str | None = None
    ) -> list[QSEComplianceChecklistModel]:
        stmt = select(QSEComplianceChecklistModel).order_by(
            QSEComplianceChecklistModel.created_at.desc()
        )
        if checklist_name:
            stmt = stmt.where(QSEComplianceChecklistModel.checklist_name == checklist_name)
        if gate_id:
            stmt = stmt.where(QSEComplianceChecklistModel.gate_id == gate_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
