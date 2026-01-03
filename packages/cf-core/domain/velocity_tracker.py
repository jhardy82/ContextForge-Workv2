"""
DuckDB-based Velocity Tracker for ContextForge.
Migrated from python.velocity for standalone capability.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Use cf_core internal logging if needed, or stdlib logging
from cf_core.logging import get_logger

logger = get_logger("velocity_tracker")

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False


class VelocityTracker:
    """Tracks project velocity metrics using embedded DuckDB.

    Persists work sessions, task estimates, and calculates
    real-world velocity factors (hours/point).
    """

    def __init__(self, db_path: str = "db/velocity.duckdb"):
        if not HAS_DUCKDB:
            logger.warning("DuckDB not available. Velocity tracking disabled.")
            return

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))
        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize DuckDB schema for velocity tracking."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS work_sessions (
            session_id VARCHAR PRIMARY KEY,
            task_id VARCHAR NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration_minutes INTEGER,
            lines_changed INTEGER DEFAULT 0,
            files_modified INTEGER DEFAULT 0,
            complexity_score INTEGER DEFAULT 1,
            session_type VARCHAR DEFAULT 'development',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            task_id VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            estimated_hours DECIMAL(5,2),
            actual_hours DECIMAL(5,2),
            complexity_category VARCHAR DEFAULT 'medium',
            status VARCHAR DEFAULT 'new',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            story_points INTEGER DEFAULT 3,
            task_type VARCHAR DEFAULT 'feature',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS velocity_metrics (
            metric_id VARCHAR PRIMARY KEY,
            sprint_id VARCHAR,
            measurement_date TIMESTAMP NOT NULL,
            planned_points INTEGER,
            completed_points INTEGER,
            velocity_score DECIMAL(5,2),
            burndown_trend DECIMAL(5,2),
            prediction_accuracy DECIMAL(5,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS complexity_factors (
            factor_id VARCHAR PRIMARY KEY,
            task_id VARCHAR NOT NULL,
            factor_type VARCHAR NOT NULL,
            factor_value DECIMAL(5,2) NOT NULL,
            impact_weight DECIMAL(3,2) DEFAULT 1.0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.conn.execute(schema_sql)
        logger.info("DuckDB velocity tracking schema initialized")

    def record_session(
        self,
        task_id: str,
        start_time: datetime,
        end_time: datetime | None = None,
        lines_changed: int = 0,
        files_modified: int = 0,
        complexity_score: int = 1,
        session_type: str = "development",
        notes: str = "",
    ) -> str:
        """Record a work session."""
        if not HAS_DUCKDB:
            return ""

        session_id = f"{task_id}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        duration_minutes = None

        if end_time:
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

        insert_sql = """
        INSERT INTO work_sessions
        (session_id, task_id, start_time, end_time, duration_minutes,
         lines_changed, files_modified, complexity_score, session_type, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.conn.execute(
            insert_sql,
            [
                session_id,
                task_id,
                start_time,
                end_time,
                duration_minutes,
                lines_changed,
                files_modified,
                complexity_score,
                session_type,
                notes,
            ],
        )

        logger.info(f"Recorded session {session_id} for task {task_id}")
        return session_id

    def update_task(
        self,
        task_id: str,
        title: str,
        estimated_hours: float | None = None,
        actual_hours: float | None = None,
        complexity_category: str = "medium",
        status: str = "new",
        story_points: int = 3,
        task_type: str = "feature",
    ):
        """Update or insert task information."""
        if not HAS_DUCKDB:
            return

        upsert_sql = """
        INSERT INTO tasks (task_id, title, estimated_hours, actual_hours,
                          complexity_category, status, story_points, task_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (task_id) DO UPDATE SET
            title = excluded.title,
            estimated_hours = excluded.estimated_hours,
            actual_hours = excluded.actual_hours,
            complexity_category = excluded.complexity_category,
            status = excluded.status,
            story_points = excluded.story_points,
            task_type = excluded.task_type
        """

        self.conn.execute(
            upsert_sql,
            [
                task_id,
                title,
                estimated_hours,
                actual_hours,
                complexity_category,
                status,
                story_points,
                task_type,
            ],
        )

        logger.info(f"Updated task {task_id}: {title}")

    def calculate_velocity(self, days_back: int = 30) -> dict[str, Any]:
        """Calculate velocity metrics based on recent history."""
        if not HAS_DUCKDB:
            return {}

        velocity_sql = f"""
        WITH session_summary AS (
            SELECT
                task_id,
                SUM(duration_minutes) / 60.0 as total_hours,
                SUM(lines_changed) as total_lines,
                SUM(files_modified) as total_files,
                AVG(complexity_score) as avg_complexity,
                COUNT(*) as session_count
            FROM work_sessions
            WHERE start_time >= (CURRENT_TIMESTAMP - INTERVAL '{days_back}' DAY)
            GROUP BY task_id
        ),
        task_velocity AS (
            SELECT
                t.task_id,
                t.title,
                t.story_points,
                t.complexity_category,
                s.total_hours,
                s.total_lines,
                s.total_files,
                s.avg_complexity,
                s.session_count,
                CASE
                    WHEN t.story_points > 0 AND s.total_hours > 0
                    THEN s.total_hours / t.story_points
                    ELSE NULL
                END as hours_per_point
            FROM tasks t
            LEFT JOIN session_summary s ON t.task_id = s.task_id
            WHERE s.total_hours IS NOT NULL
        )
        SELECT
            COUNT(*) as completed_tasks,
            SUM(story_points) as total_points,
            SUM(total_hours) as total_hours,
            AVG(hours_per_point) as avg_hours_per_point,
            SUM(total_lines) as total_lines_changed,
            SUM(total_files) as total_files_modified,
            AVG(avg_complexity) as avg_complexity_score
        FROM task_velocity
        """

        result = self.conn.execute(velocity_sql).fetchone()

        if result and result[0] > 0:
            velocity_data = {
                "completed_tasks": result[0],
                "total_points": result[1] or 0,
                "total_hours": round(result[2] or 0, 2),
                "avg_hours_per_point": round(result[3] or 0, 2),
                "total_lines_changed": result[4] or 0,
                "total_files_modified": result[5] or 0,
                "avg_complexity_score": round(result[6] or 1, 2),
                "days_analyzed": days_back,
                "points_per_day": round((result[1] or 0) / days_back, 2),
                "hours_per_day": round((result[2] or 0) / days_back, 2),
            }
        else:
            velocity_data = {
                "completed_tasks": 0,
                "total_points": 0,
                "total_hours": 0,
                "avg_hours_per_point": 8.0,  # Default estimate
                "total_lines_changed": 0,
                "total_files_modified": 0,
                "avg_complexity_score": 1,
                "days_analyzed": days_back,
                "points_per_day": 0,
                "hours_per_day": 0,
            }

        return velocity_data

    def predict_completion(self, story_points: int, complexity_multiplier: float = 1.0) -> dict[str, Any]:
        """Predict completion time based on velocity data."""
        if not HAS_DUCKDB:
            return {}

        velocity = self.calculate_velocity()

        if velocity.get("avg_hours_per_point", 0) > 0:
            base_hours = story_points * velocity["avg_hours_per_point"]
            adjusted_hours = base_hours * complexity_multiplier

            # Calculate confidence based on data quality
            confidence = min(90, 50 + (velocity["completed_tasks"] * 5))

            prediction = {
                "estimated_hours": round(adjusted_hours, 1),
                "estimated_days": round(adjusted_hours / 8, 1),
                "confidence_percentage": confidence,
                "base_hours_per_point": velocity["avg_hours_per_point"],
                "complexity_multiplier": complexity_multiplier,
                "data_quality": {
                    "tasks_analyzed": velocity["completed_tasks"],
                    "days_of_data": velocity["days_analyzed"],
                    "avg_complexity": velocity["avg_complexity_score"],
                },
            }
        else:
            # Fallback to industry standards
            prediction = {
                "estimated_hours": story_points * 8.0 * complexity_multiplier,
                "estimated_days": story_points * 1.0 * complexity_multiplier,
                "confidence_percentage": 25,
                "base_hours_per_point": 8.0,
                "complexity_multiplier": complexity_multiplier,
                "data_quality": {"tasks_analyzed": 0, "days_of_data": 0, "avg_complexity": 1.0},
                "note": "Using industry default - no historical data available",
            }

        return prediction

    def close(self):
        """Close database connection."""
        if HAS_DUCKDB and hasattr(self, 'conn'):
            self.conn.close()
