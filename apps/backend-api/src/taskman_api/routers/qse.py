"""
QSE API Router
Exposes Quantum Sync Engine functionality via API.
"""

import structlog
from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from taskman_api.dependencies import QSESvc
from taskman_api.schemas.qse import (
    EvaluationCreate,
    EvaluationResponse,
    EvidenceCreate,
    EvidenceResponse,
    GateCreate,
    GateResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/qse", tags=["QSE"])


@router.get("/gates", response_model=list[GateResponse])
async def list_gates(service: QSESvc, enabled_only: bool = True) -> list[GateResponse]:
    """List all available quality gates."""
    return await service.repo.list_gates(enabled_only=enabled_only)


@router.post("/gates", response_model=GateResponse, status_code=http_status.HTTP_201_CREATED)
async def create_gate(gate: GateCreate, service: QSESvc) -> GateResponse:
    """Create a new quality gate."""
    try:
        # Use GATE-{NAME} as ID pattern
        gate_id = f"GATE-{gate.name.upper().replace(' ', '_')}"
        existing = await service.repo.get_gate(gate_id)
        if existing:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Gate {gate_id} already exists",
            )

        result = await service.repo.create_gate(id=gate_id, **gate.model_dump())
        await service.repo.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: gate creation failed: {type(e).__name__} - {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create quality gate: {str(e)}",
        )


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_gate(evaluation: EvaluationCreate, service: QSESvc) -> EvaluationResponse:
    """Perform a gate evaluation."""
    try:
        result = await service.evaluate_gate(
            gate_name=evaluation.gate_name,
            current_value=evaluation.actual_value,
            task_id=evaluation.task_id,
            evidence_ids=evaluation.evidence_ids,
        )
        await service.repo.commit()
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("evaluation_failed", error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}",
        )


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(evaluation_id: str, service: QSESvc) -> EvaluationResponse:
    """Retrieve evaluation details by ID."""
    from cf_core.dao.qse import QSEGateEvaluationModel

    result = await service.repo.session.get(QSEGateEvaluationModel, evaluation_id)
    if not result:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation {evaluation_id} not found",
        )
    return result


@router.get("/evaluations", response_model=list[EvaluationResponse])
async def list_evaluations(
    service: QSESvc,
    task_id: str | None = None,
    gate_id: str | None = None,
    passed: bool | None = None,
    limit: int = 50,
) -> list[EvaluationResponse]:
    """List all gate evaluations with optional filters."""
    from cf_core.dao.qse import QSEGateEvaluationModel
    from sqlalchemy import select

    stmt = (
        select(QSEGateEvaluationModel)
        .limit(limit)
        .order_by(QSEGateEvaluationModel.evaluated_at.desc())
    )
    if task_id:
        stmt = stmt.where(QSEGateEvaluationModel.task_id == task_id)
    if gate_id:
        stmt = stmt.where(QSEGateEvaluationModel.gate_id == gate_id)
    if passed is not None:
        stmt = stmt.where(QSEGateEvaluationModel.passed == passed)

    result = await service.repo.session.execute(stmt)
    return list(result.scalars().all())


@router.post("/evidence", response_model=EvidenceResponse, status_code=http_status.HTTP_201_CREATED)
async def create_evidence(evidence: EvidenceCreate, service: QSESvc) -> EvidenceResponse:
    """
    Record evidence for a task or session.
    Typically called by the CLI or remote agents.
    """
    try:
        print(f"DEBUG: create_evidence started for {evidence.artifact_type}")
        artifact_hash = evidence.artifact_hash or "unknown"
        file_size = evidence.file_size_bytes or 0

        print("DEBUG: calling service.record_evidence")
        result = await service.record_evidence(
            artifact_type=evidence.artifact_type,
            artifact_hash=artifact_hash,
            file_size_bytes=file_size,
            artifact_path=evidence.artifact_path,
            task_id=evidence.task_id,
            session_id=evidence.session_id,
            metadata=evidence.metadata,
        )
        print("DEBUG: calling service.repo.commit")
        await service.repo.commit()
        print("DEBUG: create_evidence successful")

        logger.info(
            "evidence_recorded", evidence_id=result.id, artifact_type=evidence.artifact_type
        )
        return result

    except Exception as e:
        logger.error("evidence_creation_failed", error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record evidence: {str(e)}",
        )


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: str, service: QSESvc) -> EvidenceResponse:
    """
    Retrieve evidence details by ID.
    """
    result = await service.get_evidence(evidence_id)
    if not result:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Evidence {evidence_id} not found"
        )
    return result


@router.get("/evidence", response_model=list[EvidenceResponse])
async def list_evidence(
    service: QSESvc,
    artifact_type: str | None = None,
    task_id: str | None = None,
    session_id: str | None = None,
    limit: int = 50,
) -> list[EvidenceResponse]:
    """
    List evidence with optional filters.
    """
    return await service.repo.list_evidence(
        artifact_type=artifact_type, task_id=task_id, session_id=session_id, limit=limit
    )
