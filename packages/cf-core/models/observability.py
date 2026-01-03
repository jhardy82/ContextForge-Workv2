"""
Observability Model for Tracker Objects

Provides health tracking and heartbeat monitoring for tasks, sprints, and projects.
Aligns with tracker-*.schema.json observability requirements.
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class Observability(BaseModel):
    """
    Observability tracking for all tracker objects.

    Required by JSON schemas for tasks, sprints, and projects.
    Tracks health status and provides evidence log for monitoring.
    """

    model_config = {"extra": "forbid", "validate_assignment": True}

    last_health: Literal["green", "yellow", "red"] = Field(
        description="Health status indicator: green=healthy, yellow=caution, red=critical"
    )

    last_heartbeat_utc: datetime = Field(
        description="Last heartbeat timestamp in UTC"
    )

    evidence_log: list[str] = Field(
        default_factory=list,
        description="Evidence/event log for observability tracking"
    )

    @classmethod
    def create_healthy(cls) -> "Observability":
        """Create a new healthy observability instance."""
        return cls(
            last_health="green",
            last_heartbeat_utc=datetime.now(UTC),
            evidence_log=[],
        )

    @classmethod
    def create_with_status(
        cls,
        health: Literal["green", "yellow", "red"],
        evidence: str | None = None,
    ) -> "Observability":
        """Create observability with specific health status."""
        return cls(
            last_health=health,
            last_heartbeat_utc=datetime.now(UTC),
            evidence_log=[evidence] if evidence else [],
        )

    def update_heartbeat(self) -> None:
        """Update the heartbeat timestamp to now."""
        self.last_heartbeat_utc = datetime.now(UTC)

    def add_evidence(self, evidence: str) -> None:
        """Add an evidence entry to the log."""
        self.evidence_log.append(evidence)

    def set_health(
        self,
        health: Literal["green", "yellow", "red"],
        evidence: str | None = None,
    ) -> None:
        """Update health status with optional evidence."""
        self.last_health = health
        self.last_heartbeat_utc = datetime.now(UTC)
        if evidence:
            self.add_evidence(evidence)
