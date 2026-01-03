"""Phase Tracking Model for cf_core.

Provides lifecycle phase tracking for Task, Sprint, and Project entities:
- Research phase: Has research been conducted? Is adequate research attached?
- Planning phase: Has planning been completed?
- Implementation phase: What is the implementation status?
- Testing/Validation phase: What is the testing and validation status?

Each phase can be: not_started, in_progress, completed, skipped, or blocked.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Phase status values
PhaseStatus = Literal["not_started", "in_progress", "completed", "skipped", "blocked"]


class ResearchPhase(BaseModel):
    """Research phase tracking.

    Tracks whether research has been conducted and if adequate
    research artifacts are attached to the entity.
    """

    model_config = ConfigDict(extra="forbid")

    status: PhaseStatus = Field(default="not_started", description="Research phase status")
    has_research: bool = Field(default=False, description="Whether any research has been conducted")
    research_adequate: bool = Field(default=False, description="Whether attached research is adequate")
    research_artifact_ids: list[str] = Field(
        default_factory=list,
        description="IDs of attached research documents/artifacts"
    )
    notes: str | None = Field(default=None, description="Research phase notes")
    completed_at: datetime | None = Field(default=None, description="When research was completed")

    @model_validator(mode="after")
    def validate_status(self) -> ResearchPhase:
        """Auto-update status based on research fields."""
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = datetime.now(UTC)
        if self.has_research and self.research_adequate and self.status == "not_started":
            self.status = "completed"
        return self


class PlanningPhase(BaseModel):
    """Planning phase tracking.

    Tracks whether planning has been completed, including
    acceptance criteria, definition of done, and implementation plan.
    """

    model_config = ConfigDict(extra="forbid")

    status: PhaseStatus = Field(default="not_started", description="Planning phase status")
    has_acceptance_criteria: bool = Field(default=False, description="Whether acceptance criteria defined")
    has_definition_of_done: bool = Field(default=False, description="Whether DoD defined")
    has_implementation_plan: bool = Field(default=False, description="Whether implementation plan exists")
    plan_artifact_ids: list[str] = Field(
        default_factory=list,
        description="IDs of planning documents (PRDs, specs, etc.)"
    )
    notes: str | None = Field(default=None, description="Planning phase notes")
    completed_at: datetime | None = Field(default=None, description="When planning was completed")

    @model_validator(mode="after")
    def validate_status(self) -> PlanningPhase:
        """Auto-update completed_at when status is completed."""
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = datetime.now(UTC)
        return self


class ImplementationPhase(BaseModel):
    """Implementation phase tracking.

    Tracks the status of implementation work including
    code changes, PRs, and deployments.
    """

    model_config = ConfigDict(extra="forbid")

    status: PhaseStatus = Field(default="not_started", description="Implementation phase status")
    progress_pct: int = Field(default=0, ge=0, le=100, description="Implementation progress percentage")
    has_code_changes: bool = Field(default=False, description="Whether code changes exist")
    has_pull_request: bool = Field(default=False, description="Whether PR has been created")
    pr_merged: bool = Field(default=False, description="Whether PR has been merged")
    deployed: bool = Field(default=False, description="Whether changes have been deployed")
    pr_urls: list[str] = Field(default_factory=list, description="URLs of related pull requests")
    commit_shas: list[str] = Field(default_factory=list, description="Related commit SHAs")
    notes: str | None = Field(default=None, description="Implementation phase notes")
    started_at: datetime | None = Field(default=None, description="When implementation started")
    completed_at: datetime | None = Field(default=None, description="When implementation was completed")

    @model_validator(mode="after")
    def validate_status(self) -> ImplementationPhase:
        """Auto-update timestamps based on status."""
        if self.status == "in_progress" and self.started_at is None:
            self.started_at = datetime.now(UTC)
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = datetime.now(UTC)
        return self


class TestingPhase(BaseModel):
    """Testing and validation phase tracking.

    Tracks the status of testing, QA, and validation activities.
    """

    model_config = ConfigDict(extra="forbid")

    status: PhaseStatus = Field(default="not_started", description="Testing phase status")
    has_unit_tests: bool = Field(default=False, description="Whether unit tests exist")
    has_integration_tests: bool = Field(default=False, description="Whether integration tests exist")
    has_e2e_tests: bool = Field(default=False, description="Whether end-to-end tests exist")
    tests_passing: bool = Field(default=False, description="Whether all tests are passing")
    coverage_pct: float | None = Field(default=None, ge=0, le=100, description="Test coverage percentage")
    has_manual_qa: bool = Field(default=False, description="Whether manual QA has been performed")
    qa_approved: bool = Field(default=False, description="Whether QA has approved")
    validation_notes: str | None = Field(default=None, description="Validation/QA notes")
    test_report_url: str | None = Field(default=None, description="URL to test report")
    started_at: datetime | None = Field(default=None, description="When testing started")
    completed_at: datetime | None = Field(default=None, description="When testing was completed")

    @model_validator(mode="after")
    def validate_status(self) -> TestingPhase:
        """Auto-update timestamps based on status."""
        if self.status == "in_progress" and self.started_at is None:
            self.started_at = datetime.now(UTC)
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = datetime.now(UTC)
        return self


class PhaseTracking(BaseModel):
    """Complete phase tracking for an entity.

    Provides a unified view of all lifecycle phases:
    - Research: Has research been done? Is it adequate?
    - Planning: Is planning complete?
    - Implementation: What's the implementation status?
    - Testing: What's the testing/validation status?

    Usage:
        task.phases.research.status  # "completed"
        task.phases.planning.has_acceptance_criteria  # True
        task.phases.implementation.progress_pct  # 75
        task.phases.testing.tests_passing  # True
    """

    model_config = ConfigDict(extra="forbid")

    research: ResearchPhase = Field(default_factory=ResearchPhase)
    planning: PlanningPhase = Field(default_factory=PlanningPhase)
    implementation: ImplementationPhase = Field(default_factory=ImplementationPhase)
    testing: TestingPhase = Field(default_factory=TestingPhase)

    @property
    def all_phases_complete(self) -> bool:
        """Check if all phases are completed or skipped."""
        return all(
            phase.status in ("completed", "skipped")
            for phase in [self.research, self.planning, self.implementation, self.testing]
        )

    @property
    def current_phase(self) -> str:
        """Determine the current active phase."""
        if self.testing.status == "in_progress":
            return "testing"
        if self.implementation.status == "in_progress":
            return "implementation"
        if self.planning.status == "in_progress":
            return "planning"
        if self.research.status == "in_progress":
            return "research"

        # Find first incomplete phase
        if self.research.status == "not_started":
            return "research"
        if self.planning.status == "not_started":
            return "planning"
        if self.implementation.status == "not_started":
            return "implementation"
        if self.testing.status == "not_started":
            return "testing"

        return "completed"

    @property
    def blocked_phase(self) -> str | None:
        """Return the name of any blocked phase, or None."""
        if self.research.status == "blocked":
            return "research"
        if self.planning.status == "blocked":
            return "planning"
        if self.implementation.status == "blocked":
            return "implementation"
        if self.testing.status == "blocked":
            return "testing"
        return None

    def summary(self) -> dict[str, str]:
        """Return a summary of all phase statuses."""
        return {
            "research": self.research.status,
            "planning": self.planning.status,
            "implementation": self.implementation.status,
            "testing": self.testing.status,
            "current": self.current_phase,
        }
