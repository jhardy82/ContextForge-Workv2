from datetime import datetime, timedelta

import pytest

from cf_core.domain.velocity_tracker import HAS_DUCKDB, VelocityTracker


@pytest.mark.skipif(not HAS_DUCKDB, reason="DuckDB not available")
def test_velocity_tracker_record_and_calculate(tmp_path):
    """Verify VelocityTracker works in standalone mode with embedded DuckDB."""
    db_path = tmp_path / "velocity_test.duckdb"
    tracker = VelocityTracker(str(db_path))

    # Record a session
    task_id = "T-100"
    start_time = datetime.now() - timedelta(hours=2)
    end_time = datetime.now()

    tracker.record_session(
        task_id=task_id,
        start_time=start_time,
        end_time=end_time,
        lines_changed=50,
        files_modified=2,
        notes="Migrated test session"
    )

    # Update task details
    tracker.update_task(
        task_id=task_id,
        title="Test Task",
        story_points=3,
        status="completed"
    )

    # Calculate velocity
    velocity = tracker.calculate_velocity()

    assert velocity["completed_tasks"] == 1
    assert velocity["total_hours"] == 2.0
    # 2 hours / 3 points = 0.67 hours/point
    assert 0.6 < velocity["avg_hours_per_point"] < 0.7

    tracker.close()
