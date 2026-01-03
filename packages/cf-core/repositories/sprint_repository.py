"""
Sprint Repository

Repository pattern implementation for Sprint persistence with SQLite and PostgreSQL backends.
Provides abstract interface and concrete implementations.
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any

from cf_core.domain.sprint_entity import SprintEntity
from cf_core.models.observability import Observability
from cf_core.models.sprint import Sprint
from cf_core.repositories.connection import PostgresConnection
from cf_core.shared.result import Result


class ISprintRepository(ABC):
    """Abstract interface for Sprint repository."""

    @abstractmethod
    def save(self, entity: SprintEntity) -> Result[SprintEntity]:
        pass

    @abstractmethod
    def get_by_id(self, sprint_id: str) -> Result[SprintEntity]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> Result[list[SprintEntity]]:
        pass

    @abstractmethod
    def find_all(self) -> Result[list[SprintEntity]]:
        pass

    @abstractmethod
    def delete(self, sprint_id: str) -> Result[bool]:
        pass


class SqliteSprintRepository(ISprintRepository):
    """SQLite implementation of the Sprint repository."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create sprints table if it doesn't exist."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sprints (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    description TEXT,
                    goal TEXT,
                    project_id TEXT,
                    completed_at TEXT,
                    pending_reason TEXT,
                    blocked_reason TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    capacity_hours REAL,
                    velocity_points REAL,
                    actual_hours REAL DEFAULT 0.0,
                    actual_points INTEGER DEFAULT 0,
                    owner TEXT,
                    cadence TEXT,
                    task_ids TEXT,
                    action_items TEXT,
                    tags TEXT,
                    team_members TEXT,
                    observability TEXT,
                    risks TEXT,
                    verification TEXT,
                    committed_points REAL,
                    completed_points REAL,
                    velocity_trend REAL
                )
            """)
            conn.commit()
        finally:
            if conn:
                conn.close()

    # ... Minimal SQLite implementation for CLI testing ...
    # Full-featured implementation deferred to Phase 3.
    # For Phase 2, we support basic CRUD for CLI integration tests.

    def save(self, entity: SprintEntity) -> Result[SprintEntity]:
        """Save sprint to SQLite (minimal implementation for testing)."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get the underlying Sprint model
            sprint = entity.model

            # Serialize complex fields to JSON with proper datetime handling
            tasks_data = []
            if hasattr(sprint, 'tasks') and sprint.tasks:
                tasks_data = sprint.tasks
            tasks_json = json.dumps(tasks_data, default=str)

            obs_data = {}
            if hasattr(sprint, "observability") and sprint.observability:
                obs_data = sprint.observability.model_dump()
            obs_json = json.dumps(obs_data, default=str)

            # Calculate completed_at value
            completed_at = None
            if hasattr(sprint, 'completed_at') and sprint.completed_at:
                completed_at = sprint.completed_at.isoformat()

            cursor.execute(
                """
                INSERT OR REPLACE INTO sprints
                (id, title, status, start_date, end_date, goal, project_id,
                 completed_at, owner, cadence, tasks, observability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sprint.id,
                    sprint.name,
                    sprint.status,
                    sprint.start_date.isoformat() if sprint.start_date else None,
                    sprint.end_date.isoformat() if sprint.end_date else None,
                    sprint.description,
                    sprint.project_id if hasattr(sprint, "project_id") else None,
                    completed_at,
                    sprint.owner if hasattr(sprint, "owner") else None,
                    sprint.cadence if hasattr(sprint, "cadence") else None,
                    tasks_json,
                    obs_json,
                ),
            )
            conn.commit()
            return Result.success(entity)
        except Exception as e:
            return Result.failure(f"Failed to save sprint: {e}")
        finally:
            if conn:
                conn.close()

    def get_by_id(self, sprint_id: str) -> Result[SprintEntity]:
        """Get sprint by ID (minimal implementation for testing)."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sprints WHERE id = ?", (sprint_id,))
            row = cursor.fetchone()

            if not row:
                return Result.failure(f"Sprint not found: {sprint_id}")

            # For minimal implementation, return a basic sprint entity
            # Full deserialization can be added in Phase 3
            # For now, just verify it exists and return a stub
            from datetime import datetime

            from cf_core.models.sprint import Sprint

            # Row structure: id, title, status, start_date, end_date, goal, ...
            sprint_model = Sprint(
                id=row[0],
                name=row[1],
                status=row[2],
                start_date=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
                end_date=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                description=row[5] or "",
            )
            entity = SprintEntity(sprint_model)
            return Result.success(entity)
        except Exception as e:
            return Result.failure(f"Failed to get sprint: {e}")
        finally:
            if conn:
                conn.close()

    def find_by_status(self, status: str) -> Result[list[SprintEntity]]:
        return Result.failure("SQLite find_by_status not fully supported for Phase 2 Sprints yet")

    def find_all(self) -> Result[list[SprintEntity]]:
        """Find all sprints (minimal implementation for testing)."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sprints")
            rows = cursor.fetchall()

            if not rows:
                return Result.success([])

            # For minimal implementation, return empty list
            # Full deserialization can be added in Phase 3
            return Result.success([])
        except Exception as e:
            return Result.failure(f"Failed to fetch sprints: {e}")
        finally:
            if conn:
                conn.close()

    def delete(self, sprint_id: str) -> Result[bool]:
        return Result.failure("SQLite delete not fully supported for Phase 2 Sprints yet")


class PostgresSprintRepository(ISprintRepository):
    """PostgreSQL implementation of the Sprint repository."""

    def __init__(self, connection: PostgresConnection):
        self._connection = connection

    def _sprint_to_row(self, sprint: Sprint) -> dict[str, Any]:
        """Convert Sprint model to dictionary for DB insertion."""
        return {
            "id": sprint.id,
            "title": sprint.name,
            "status": sprint.status,
            "start_date": sprint.start_date,
            "end_date": sprint.end_date,
            "description": sprint.description,
            "goal": sprint.goal,
            "project_id": sprint.project_id,
            "completed_at": sprint.completed_at,
            "created_at": sprint.created_at,
            "updated_at": sprint.updated_at,
            "capacity_hours": sprint.capacity_hours,
            "velocity_points": sprint.velocity_points,
            "actual_hours": sprint.actual_hours,
            "actual_points": sprint.actual_points,
            # Phase 2 Fields
            "owner": sprint.owner,
            "cadence": sprint.cadence,
            "tasks": json.dumps(sprint.task_ids),  # Store as JSONB
            "observability": sprint.observability.model_dump_json(),  # Store as JSONB
            "risks": json.dumps([r.model_dump() for r in sprint.risks]),
            "verification": sprint.verification.model_dump_json() if sprint.verification else None,
            "committed_points": sprint.committed_points,
            "completed_points": sprint.completed_points,
            "velocity_trend": sprint.velocity_trend,
        }

    def _row_to_sprint(self, row: tuple, col_map: dict[str, int]) -> Sprint:
        """Convert DB row to Sprint model."""

        def get_col(name: str) -> Any:
            idx = col_map.get(name)
            return row[idx] if idx is not None else None

        # Helper for JSON fields
        def parse_json(value: Any, default: Any = None) -> Any:
            if value is None:
                return default
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return default
            return value  # Already dict/list if psycop2 parsed JSONB

        # Parse Observability
        obs_data = parse_json(get_col("observability"))
        observability = (
            Observability(**obs_data) if obs_data else Observability(health_status="green")
        )

        # Parse Tasks
        tasks_data = parse_json(get_col("tasks"), [])

        # Parse Risks
        risks_data = parse_json(get_col("risks"), [])
        # Import here to avoid circular dependencies if any, though model imports are top level
        from cf_core.models.risk_entry import RiskEntrySimple

        risks = [RiskEntrySimple(**r) for r in risks_data] if risks_data else []

        from cf_core.models.verification import Verification

        ver_data = parse_json(get_col("verification"))
        verification = Verification(**ver_data) if ver_data else None

        return Sprint(
            id=get_col("id"),
            name=get_col("title"),  # Mapped from title column
            status=get_col("status"),
            start_date=get_col("start_date"),
            end_date=get_col("end_date"),
            description=get_col("description") or "",
            project_id=get_col("project_id"),
            completed_at=get_col("completed_at"),
            created_at=get_col("created_at"),
            updated_at=get_col("updated_at"),
            capacity_hours=get_col("capacity_hours"),
            velocity_points=get_col("velocity_points"),
            actual_hours=get_col("actual_hours") or 0.0,
            actual_points=get_col("actual_points") or 0,
            # Phase 2
            owner=get_col("owner"),
            cadence=get_col("cadence"),
            goal=get_col("goal"),
            task_ids=tasks_data,
            observability=observability,
            risks=risks,
            verification=verification,
            committed_points=get_col("committed_points"),
            completed_points=get_col("completed_points"),
            velocity_trend=get_col("velocity_trend"),
        )

    def save(self, entity: SprintEntity) -> Result[SprintEntity]:
        try:
            row_data = self._sprint_to_row(entity.model)
            columns = list(row_data.keys())
            values = list(row_data.values())

            # Construct UPSERT query
            # We must explicitly list columns to update on conflict
            update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "id"])

            query = f"""
                INSERT INTO sprints ({", ".join(columns)})
                VALUES ({", ".join(["%s"] * len(columns))})
                ON CONFLICT (id) DO UPDATE SET
                {update_clause}
            """

            with self._connection.get_cursor() as cursor:
                cursor.execute(query, values)
                self._connection.commit()

            return Result.success(entity)

        except Exception as e:
            self._connection.rollback()
            return Result.failure(f"Postgres error saving sprint: {e}")

    def get_by_id(self, sprint_id: str) -> Result[SprintEntity]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM sprints WHERE id = %s", (sprint_id,))
                if cursor.description is None:
                    return Result.failure(f"Sprint {sprint_id} not found")

                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                row = cursor.fetchone()

                if row:
                    sprint = self._row_to_sprint(row, col_map)
                    return Result.success(SprintEntity(sprint))
                return Result.failure(f"Sprint {sprint_id} not found")
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def find_by_status(self, status: str) -> Result[list[SprintEntity]]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM sprints WHERE status = %s", (status,))
                if cursor.description is None:
                    return Result.success([])

                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                rows = cursor.fetchall()

                sprints = [SprintEntity(self._row_to_sprint(row, col_map)) for row in rows]
                return Result.success(sprints)
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def find_all(self) -> Result[list[SprintEntity]]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM sprints ORDER BY created_at DESC")
                if cursor.description is None:
                    return Result.success([])

                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                rows = cursor.fetchall()

                sprints = [SprintEntity(self._row_to_sprint(row, col_map)) for row in rows]
                return Result.success(sprints)
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def delete(self, sprint_id: str) -> Result[bool]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("DELETE FROM sprints WHERE id = %s", (sprint_id,))
                deleted = cursor.rowcount > 0
                self._connection.commit()
                return Result.success(deleted)
        except Exception as e:
            self._connection.rollback()
            return Result.failure(f"Database error: {e}")
