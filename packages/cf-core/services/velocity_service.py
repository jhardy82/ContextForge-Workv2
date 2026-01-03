"""Velocity service for cf_core.

Provides velocity tracking and calculation services.
Wraps the canonical python/velocity/velocity_tracker.py implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cf_core.models import VelocityMetric

if TYPE_CHECKING:
    from cf_core.database import DatabaseConnection

# Try to import the local velocity tracker
try:
    from cf_core.domain.velocity_tracker import VelocityTracker as _VelocityTracker
    HAS_VELOCITY_TRACKER = True
except ImportError:
    _VelocityTracker: Any = None
    HAS_VELOCITY_TRACKER = False


class VelocityService:
    """Service for velocity tracking and calculations.

    This service provides a clean interface for velocity operations,
    wrapping the canonical VelocityTracker when available.

    Attributes:
        db: Database connection instance
        baseline_hours_per_point: Default velocity baseline (0.23 hrs/point)
    """

    # Default baseline from DuckDB velocity data
    DEFAULT_BASELINE = 0.23  # hours per story point

    def __init__(
        self,
        db: DatabaseConnection | None = None,
        baseline_hours_per_point: float | None = None,
    ) -> None:
        """Initialize velocity service.

        Args:
            db: Optional database connection
            baseline_hours_per_point: Override default baseline
        """
        self.db = db
        self.baseline_hours_per_point = baseline_hours_per_point or self.DEFAULT_BASELINE
        self._metrics: list[VelocityMetric] = []

        # Initialize canonical tracker if available
        self._tracker = _VelocityTracker() if HAS_VELOCITY_TRACKER else None

    def record_velocity(
        self,
        sprint_id: str | None = None,
        task_id: str | None = None,
        story_points: float = 0.0,
        actual_hours: float = 0.0,
        estimated_hours: float = 0.0,
        notes: str = "",
    ) -> VelocityMetric:
        """Record a velocity metric.

        Args:
            sprint_id: Associated sprint ID
            task_id: Associated task ID
            story_points: Story points completed
            actual_hours: Actual hours spent
            estimated_hours: Estimated hours
            notes: Optional notes

        Returns:
            Created VelocityMetric
        """
        metric_id = self._generate_metric_id()
        metric = VelocityMetric(
            id=metric_id,
            sprint_id=sprint_id,
            task_id=task_id,
            story_points=story_points,
            actual_hours=actual_hours,
            estimated_hours=estimated_hours,
            notes=notes,
        )
        self._metrics.append(metric)
        return metric

    def predict_time(
        self,
        story_points: int,
        complexity_multiplier: float = 1.0,
    ) -> dict:
        """Predict completion time using velocity baseline.

        Uses DuckDB velocity data when available, otherwise uses default baseline.

        Args:
            story_points: Fibonacci estimate (1, 2, 3, 5, 8, 13)
            complexity_multiplier: Adjustment factor (0.8-1.5)
                - 0.8: Similar work recently completed
                - 1.0: Standard complexity
                - 1.2: Novel approach or technology
                - 1.5: High risk, unproven technique

        Returns:
            Dict with estimated_hours, estimated_days, confidence_percentage
        """
        estimated_hours = story_points * self.baseline_hours_per_point * complexity_multiplier
        estimated_days = estimated_hours / 8  # Assuming 8-hour workday

        # Confidence decreases with complexity and story points
        base_confidence = 85
        confidence_penalty = (story_points - 3) * 5
        complexity_penalty = (complexity_multiplier - 1.0) * 20

        confidence = max(40, base_confidence - confidence_penalty - complexity_penalty)

        return {
            "estimated_hours": round(estimated_hours, 1),
            "estimated_days": round(estimated_days, 2),
            "confidence_percentage": int(confidence),
            "base_hours_per_point": self.baseline_hours_per_point,
            "complexity_multiplier": complexity_multiplier,
            "story_points": story_points,
        }

    def get_sprint_velocity(self, sprint_id: str) -> dict:
        """Calculate velocity metrics for a sprint.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Dict with total_points, total_hours, velocity, metrics_count
        """
        sprint_metrics = [m for m in self._metrics if m.sprint_id == sprint_id]

        total_points = sum(m.story_points for m in sprint_metrics)
        total_hours = sum(m.actual_hours for m in sprint_metrics)

        velocity = total_hours / total_points if total_points > 0 else None

        return {
            "sprint_id": sprint_id,
            "total_points": total_points,
            "total_hours": total_hours,
            "velocity_hours_per_point": velocity,
            "metrics_count": len(sprint_metrics),
        }

    def update_baseline(self) -> float:
        """Recalculate baseline from recorded metrics.

        Returns:
            Updated baseline hours per point
        """
        if not self._metrics:
            return self.baseline_hours_per_point

        total_points = sum(m.story_points for m in self._metrics)
        total_hours = sum(m.actual_hours for m in self._metrics)

        if total_points > 0:
            self.baseline_hours_per_point = total_hours / total_points

        return self.baseline_hours_per_point

    def _generate_metric_id(self) -> str:
        """Generate a unique metric ID."""
        import uuid
        return f"VM-{uuid.uuid4().hex[:8].upper()}"


__all__ = ["VelocityService", "HAS_VELOCITY_TRACKER"]
