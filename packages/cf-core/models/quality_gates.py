"""
Quality Gates Model

Test, lint, and security status tracking.
"""

from typing import Literal

from pydantic import BaseModel, Field


class TestResults(BaseModel):
    """Test execution results."""

    model_config = {"extra": "forbid"}

    passed: int = Field(ge=0, description="Number of tests passed")
    total: int = Field(ge=0, description="Total number of tests")
    coverage_pct: float = Field(ge=0, le=100, description="Code coverage percentage")


class QualityGates(BaseModel):
    """
    Quality gate status for tasks.

    Tracks automated quality checks: tests, linting, security, performance.
    """

    model_config = {"extra": "forbid"}

    tests: TestResults | None = None
    lint: Literal["pass", "fail"] | None = None
    security_scan: Literal["pass", "fail"] | None = None
    performance_check: Literal["pass", "fail"] | None = None
