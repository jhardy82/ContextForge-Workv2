from __future__ import annotations

import hashlib
import os
import subprocess
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from cf_core.dao.qse import (
    QSEEvidenceModel,
    QSEGateEvaluationModel,
    QSEQualityGateModel,
    QSERepository,
)
from cf_core.services.metrics import BaseMetricCollector, PytestCoverageCollector


class QSEService:
    """
    Service layer for Quantum Sync Engine (QSE).
    Handles business logic for evidence collection, gate evaluation, and sync coordination.
    """

    def __init__(self, repo: QSERepository):
        self.repo = repo
        self.collectors: dict[str, BaseMetricCollector] = {
            "coverage": PytestCoverageCollector(),
            "minimum test coverage": PytestCoverageCollector(),
        }

    @staticmethod
    def _calculate_file_hash(path: str) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def collect_file_evidence(
        self,
        file_path: str,
        task_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> QSEEvidenceModel:
        """
        Collect evidence from a file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        abs_path = os.path.abspath(file_path)
        file_hash = self._calculate_file_hash(abs_path)
        file_size = os.path.getsize(abs_path)

        ev_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        meta = metadata or {}
        meta.update(
            {
                "original_path": abs_path,
                "collected_via": "cli",
            }
        )

        return await self.repo.create_evidence(
            id=ev_id,
            artifact_type="file",
            artifact_path=abs_path,
            artifact_hash=file_hash,
            file_size_bytes=file_size,
            task_id=task_id,
            session_id=session_id,
            metadata_=meta,
        )

    async def record_evidence(
        self,
        artifact_type: str,
        artifact_hash: str,
        file_size_bytes: int,
        artifact_path: str | None = None,
        task_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> QSEEvidenceModel:
        """
        Record evidence collected externally (e.g. by CLI and pushed to API).
        Does not require file lookup.
        """
        ev_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        meta = metadata or {}
        meta.setdefault("collected_via", "api_push")

        return await self.repo.create_evidence(
            id=ev_id,
            artifact_type=artifact_type,
            artifact_path=artifact_path,
            artifact_hash=artifact_hash,
            file_size_bytes=file_size_bytes,
            task_id=task_id,
            session_id=session_id,
            metadata_=meta,
        )

    async def get_evidence(self, evidence_id: str) -> QSEEvidenceModel | None:
        """
        Retrieve evidence by ID.
        """
        return await self.repo.get_evidence(evidence_id)

    async def collect_command_evidence(
        self,
        command: str,
        task_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> QSEEvidenceModel:
        """
        Collect evidence by running a command.
        """
        # Security Note: This runs shell commands. Ensure 'command' is trusted or sanitized before calling.
        # In a real scenario, we might strictly parse this.

        try:
            # We use subprocess.run for simplicity in this async wrapper context,
            # ideally should be asyncio.create_subprocess_shell
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=False
            )

            output = result.stdout + result.stderr
            exit_code = result.returncode

        except Exception as e:
            output = str(e)
            exit_code = -1

        ev_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        meta = metadata or {}
        meta.update(
            {
                "command": command,
                "exit_code": exit_code,
                "output_preview": output[:200],  # Store preview in metadata
            }
        )

        # We treat the output as the "artifact".
        # Ideally we might save output to a file and hash that,
        # but here we'll hash the output string content.
        content_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()

        return await self.repo.create_evidence(
            id=ev_id,
            artifact_type="command_output",
            artifact_hash=content_hash,  # Logical hash of the output
            file_size_bytes=len(output),
            task_id=task_id,
            session_id=session_id,
            metadata_=meta,
        )

    async def evaluate_gate(
        self,
        gate_name: str,
        current_value: float,
        task_id: str | None = None,
        evidence_ids: list[str] | None = None,
    ) -> QSEGateEvaluationModel:
        """
        Evaluate a specific quality gate.
        """
        target_gate = await self.repo.get_gate_by_name(gate_name)

        if not target_gate:
            raise ValueError(f"Gate '{gate_name}' not found.")

        passed = False
        threshold = (
            float(target_gate.threshold_value) if target_gate.threshold_value is not None else 0.0
        )
        op = target_gate.threshold_operator

        if op == ">=":
            passed = current_value >= threshold
        elif op == ">":
            passed = current_value > threshold
        elif op == "<=":
            passed = current_value <= threshold
        elif op == "<":
            passed = current_value < threshold
        elif op == "==":
            passed = current_value == threshold
        else:
            # Default fallback for safety
            passed = False

        eval_id = f"EVAL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        return await self.repo.create_evaluation(
            id=eval_id,
            gate_id=target_gate.id,
            task_id=task_id,
            actual_value=current_value,
            passed=passed,
            evidence_ids=evidence_ids or [],
        )

    async def sync_inline(
        self,
        session_id: str | None = None,
        task_id: str | None = None,
        paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform an inline synchronization:
        1. Collect evidence from paths (or all tracked files).
        2. Evaluate all applicable quality gates.
        3. Return compliance summary.
        """
        results = {
            "session_id": session_id,
            "evidence_collected": [],
            "gates_evaluated": [],
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 1. Collect Evidence
        # For inline sync, default to recursive scan of current directory if no paths provided
        # BUT for safety, let's just inspect specific critical files for now
        target_paths = paths or ["pyproject.toml", "task.md"]

        evidence_ids = []
        for path in target_paths:
            if os.path.exists(path):
                ev = await self.collect_file_evidence(
                    file_path=path,
                    task_id=task_id,
                    session_id=session_id,
                    metadata={"sync_source": "inline"},
                )
                results["evidence_collected"].append(ev)
                evidence_ids.append(ev.id)

        # 2. Evaluate Gates
        all_gates = await self.repo.list_gates()
        for gate in all_gates:
            collector = self.collectors.get(gate.name.lower())
            if collector:
                # Perform real evaluation
                # For now, we assume default paths for collectors
                metric = await collector.collect()

                eval_res = await self.evaluate_gate(
                    gate_name=gate.name,
                    current_value=metric.value,
                    task_id=task_id,
                    evidence_ids=evidence_ids,
                )
                results["gates_evaluated"].append(
                    {
                        "gate_name": gate.name,
                        "status": "passed" if eval_res.passed else "failed",
                        "reason": f"Value: {metric.value} (Target: {gate.threshold_operator} {gate.threshold_value})",
                        "actual_value": metric.value,
                        "evaluation_id": eval_res.id if hasattr(eval_res, "id") else None,
                    }
                )
            else:
                # Record the "skip" or real eval if implemented
                results["gates_evaluated"].append(
                    {
                        "gate_name": gate.name,
                        "status": "skipped",
                        "reason": f"No metric collector for '{gate.name}'",
                    }
                )

        return results
