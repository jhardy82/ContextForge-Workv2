"""
Project Repository

Repository pattern implementation for Project persistence with SQLite and PostgreSQL backends.
Provides abstract interface and concrete implementations.
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any

from cf_core.domain.project_entity import ProjectEntity
from cf_core.models.observability import Observability
from cf_core.models.project import Project
from cf_core.repositories.connection import PostgresConnection
from cf_core.shared.result import Result


class IProjectRepository(ABC):
    """Abstract interface for Project repository."""

    @abstractmethod
    def save(self, entity: ProjectEntity) -> Result[ProjectEntity]:
        pass

    @abstractmethod
    def get_by_id(self, project_id: str) -> Result[ProjectEntity]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> Result[list[ProjectEntity]]:
        pass

    @abstractmethod
    def find_by_owner(self, owner: str) -> Result[list[ProjectEntity]]:
        pass

    @abstractmethod
    def find_all(self) -> Result[list[ProjectEntity]]:
        pass

    @abstractmethod
    def delete(self, project_id: str) -> Result[bool]:
        pass


class SqliteProjectRepository(IProjectRepository):
    """SQLite implementation of the Project repository."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create projects table if it doesn't exist."""
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    description TEXT,
                    owner TEXT,
                    start_date TEXT,
                    target_end_date TEXT,
                    completed_at TEXT,
                    pending_reason TEXT,
                    blocked_reason TEXT,
                    context_ids TEXT,
                    sprint_ids TEXT,
                    task_ids TEXT,
                    action_items TEXT,
                    team_members TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    mission TEXT,
                    vision TEXT,
                    roadmap_url TEXT,
                    observability TEXT,
                    sponsors TEXT,
                    stakeholders TEXT,
                    risks TEXT,
                    milestones TEXT,
                    resources TEXT,
                    dependencies TEXT,
                    quality_gates TEXT,
                    budget REAL,
                    spend REAL,
                    progress REAL,
                    health_score INTEGER
                )
            """)
            conn.commit()
        finally:
            if conn:
                conn.close()

    def _project_to_row(self, project: Project) -> dict:
        """Convert Project model to dictionary for SQLite insertion."""
        from cf_core.models.action_item import ActionItem

        def to_json(obj):
            if obj is None:
                return None
            if hasattr(obj, "model_dump"):
                return json.dumps(obj.model_dump(mode="json"))
            if isinstance(obj, list) and obj and hasattr(obj[0], "model_dump"):
                return json.dumps([item.model_dump(mode="json") for item in obj])
            return json.dumps(obj, default=str)

        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "description": project.description,
            "owner": project.owner,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "target_end_date": project.target_end_date.isoformat() if project.target_end_date else None,
            "completed_at": project.completed_at.isoformat() if project.completed_at else None,
            "pending_reason": project.pending_reason,
            "blocked_reason": project.blocked_reason,
            "context_ids": to_json(project.context_ids),
            "sprint_ids": to_json(project.sprint_ids),
            "task_ids": to_json(project.task_ids),
            "action_items": to_json(project.action_items),
            "team_members": to_json(project.team_members),
            "tags": to_json(project.tags),
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "mission": project.mission,
            "vision": project.vision,
            "roadmap_url": project.roadmap_url,
            "observability": to_json(project.observability),
            "sponsors": to_json(project.sponsors),
            "stakeholders": to_json(project.stakeholders),
            "risks": to_json(project.risks),
            "milestones": to_json(project.milestones),
            "resources": to_json(project.resources),
            "dependencies": to_json(project.dependencies),
            "quality_gates": to_json(project.quality_gates),
            "budget": project.budget,
            "spend": project.spend,
            "progress": project.progress,
            "health_score": project.health_score,
        }

    def _row_to_project(self, row: sqlite3.Row) -> Project:
        """Convert database row to Project model."""
        from datetime import datetime
        from cf_core.models.action_item import ActionItem
        from cf_core.models.risk_entry import RiskEntrySimple

        def parse_date(s):
            return datetime.fromisoformat(s) if s else None

        def parse_json(s, default=None):
            if s is None:
                return default if default is not None else []
            if isinstance(s, str):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    return default if default is not None else []
            return s

        # Parse observability
        obs_data = parse_json(row["observability"], {})
        if obs_data:
            observability = Observability(**obs_data)
        else:
            observability = Observability.create_healthy()

        # Parse action items
        action_items_data = parse_json(row["action_items"], [])
        action_items = [ActionItem(**ai) for ai in action_items_data]

        # Parse risks
        risks_data = parse_json(row["risks"], [])
        risks = [RiskEntrySimple(**r) for r in risks_data]

        from datetime import UTC
        return Project(
            id=row["id"],
            name=row["name"],
            status=row["status"],
            description=row["description"] or "",
            owner=row["owner"],
            start_date=parse_date(row["start_date"]),
            target_end_date=parse_date(row["target_end_date"]),
            completed_at=parse_date(row["completed_at"]),
            pending_reason=row["pending_reason"],
            blocked_reason=row["blocked_reason"],
            context_ids=parse_json(row["context_ids"], []),
            sprint_ids=parse_json(row["sprint_ids"], []),
            task_ids=parse_json(row["task_ids"], []),
            action_items=action_items,
            team_members=parse_json(row["team_members"], []),
            tags=parse_json(row["tags"], []),
            created_at=parse_date(row["created_at"]) or datetime.now(UTC),
            updated_at=parse_date(row["updated_at"]) or datetime.now(UTC),
            mission=row["mission"],
            vision=row["vision"],
            roadmap_url=row["roadmap_url"],
            observability=observability,
            sponsors=parse_json(row["sponsors"], []),
            stakeholders=parse_json(row["stakeholders"], []),
            risks=risks,
            milestones=parse_json(row["milestones"], []),
            resources=parse_json(row["resources"], []),
            dependencies=parse_json(row["dependencies"], []),
            quality_gates=parse_json(row["quality_gates"], None) or None,
            budget=row["budget"],
            spend=row["spend"],
            progress=row["progress"],
            health_score=row["health_score"],
        )

    def save(self, entity: ProjectEntity) -> Result[ProjectEntity]:
        try:
            row_dict = self._project_to_row(entity.project)
            columns = ", ".join(row_dict.keys())
            placeholders = ", ".join(["?"] * len(row_dict))
            values = list(row_dict.values())

            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO projects ({columns}) VALUES ({placeholders})", values
                )
                conn.commit()
                return Result.success(entity)
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error saving project: {e}")

    def get_by_id(self, project_id: str) -> Result[ProjectEntity]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()
                if not row:
                    return Result.failure(f"Project with id '{project_id}' not found")
                return Result.success(ProjectEntity(self._row_to_project(row)))
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error getting project: {e}")

    def find_by_status(self, status: str) -> Result[list[ProjectEntity]]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE status = ?", (status,))
                rows = cursor.fetchall()
                return Result.success([ProjectEntity(self._row_to_project(row)) for row in rows])
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error: {e}")

    def find_by_owner(self, owner: str) -> Result[list[ProjectEntity]]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE owner = ?", (owner,))
                rows = cursor.fetchall()
                return Result.success([ProjectEntity(self._row_to_project(row)) for row in rows])
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error: {e}")

    def find_all(self) -> Result[list[ProjectEntity]]:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return Result.success([ProjectEntity(self._row_to_project(row)) for row in rows])
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error: {e}")

    def delete(self, project_id: str) -> Result[bool]:
        try:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    return Result.success(True)
                return Result.failure(f"Project with id '{project_id}' not found")
            finally:
                conn.close()
        except sqlite3.Error as e:
            return Result.failure(f"Database error: {e}")


class PostgresProjectRepository(IProjectRepository):
    """PostgreSQL implementation of the Project repository."""

    def __init__(self, connection: PostgresConnection):
        self._connection = connection

    def _project_to_row(self, project: Project) -> dict[str, Any]:
        """Convert Project model to dictionary for DB insertion."""
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "description": project.description,
            "owner": project.owner,
            "start_date": project.start_date,
            "target_end_date": project.target_end_date,
            "completed_at": project.completed_at,
            "pending_reason": project.pending_reason,
            "blocked_reason": project.blocked_reason,
            # Simple Lists (TEXT[] or JSONB - using JSONB for consistency)
            "context_ids": json.dumps(project.context_ids),
            "sprint_ids": json.dumps(project.sprint_ids),
            "task_ids": json.dumps(project.task_ids),
            "tags": json.dumps(project.tags),
            # Phase 2 Fields
            "mission": project.mission,
            "vision": project.vision,
            "roadmap_url": project.roadmap_url,
            # Complex JSON Fields
            "observability": project.observability.model_dump_json(),
            "team_members": json.dumps(project.team_members),
            "sponsors": json.dumps(project.sponsors),
            "stakeholders": json.dumps(project.stakeholders),
            "risks": json.dumps([r.model_dump() for r in project.risks]),
            "milestones": json.dumps(project.milestones),
            "resources": json.dumps(project.resources),
            "dependencies": json.dumps(project.dependencies),
            "quality_gates": json.dumps(project.quality_gates) if project.quality_gates else None,
            # Metrics
            "budget": project.budget,
            "spend": project.spend,
            "progress": project.progress,
            "health_score": project.health_score,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }

    def _row_to_project(self, row: tuple, col_map: dict[str, int]) -> Project:
        """Convert DB row to Project model."""

        def get_col(name: str) -> Any:
            idx = col_map.get(name)
            return row[idx] if idx is not None else None

        def parse_json(value: Any, default: Any = None) -> Any:
            if value is None:
                return default
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return default
            return value

        # Parse complex objects
        obs_data = parse_json(get_col("observability"))
        observability = (
            Observability(**obs_data) if obs_data else Observability(health_status="green")
        )

        from cf_core.models.risk_entry import RiskEntrySimple

        risks_data = parse_json(get_col("risks"), [])
        risks = [RiskEntrySimple(**r) for r in risks_data] if risks_data else []

        return Project(
            id=get_col("id"),
            name=get_col("name"),
            status=get_col("status"),
            description=get_col("description") or "",
            owner=get_col("owner"),
            start_date=get_col("start_date"),
            target_end_date=get_col("target_end_date"),
            completed_at=get_col("completed_at"),
            pending_reason=get_col("pending_reason"),
            blocked_reason=get_col("blocked_reason"),
            context_ids=parse_json(get_col("context_ids"), []),
            sprint_ids=parse_json(get_col("sprint_ids"), []),
            task_ids=parse_json(get_col("task_ids"), []),
            tags=parse_json(get_col("tags"), []),
            mission=get_col("mission"),
            vision=get_col("vision"),
            roadmap_url=get_col("roadmap_url"),
            observability=observability,
            team_members=parse_json(get_col("team_members"), []),
            sponsors=parse_json(get_col("sponsors"), []),
            stakeholders=parse_json(get_col("stakeholders"), []),
            risks=risks,
            milestones=parse_json(get_col("milestones"), []),
            resources=parse_json(get_col("resources"), []),
            dependencies=parse_json(get_col("dependencies"), []),
            quality_gates=parse_json(get_col("quality_gates")),
            budget=get_col("budget"),
            spend=get_col("spend"),
            progress=get_col("progress"),
            health_score=get_col("health_score"),
            created_at=get_col("created_at"),
            updated_at=get_col("updated_at"),
        )

    def save(self, entity: ProjectEntity) -> Result[ProjectEntity]:
        try:
            row_data = self._project_to_row(entity.project)
            columns = list(row_data.keys())
            values = list(row_data.values())

            update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "id"])

            query = f"""
                INSERT INTO projects ({", ".join(columns)})
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
            return Result.failure(f"Postgres error saving project: {e}")

    def get_by_id(self, project_id: str) -> Result[ProjectEntity]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                row = cursor.fetchone()

                if row:
                    project = self._row_to_project(row, col_map)
                    return Result.success(ProjectEntity(project))
                return Result.failure(f"Project {project_id} not found")
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def find_by_status(self, status: str) -> Result[list[ProjectEntity]]:
        try:
            with self._connection.get_cursor() as cursor:
                # Assuming projects table has valid status column values
                cursor.execute("SELECT * FROM projects WHERE status = %s", (status,))
                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                rows = cursor.fetchall()
                return Result.success(
                    [ProjectEntity(self._row_to_project(row, col_map)) for row in rows]
                )
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def find_by_owner(self, owner: str) -> Result[list[ProjectEntity]]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM projects WHERE owner = %s", (owner,))
                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                rows = cursor.fetchall()
                return Result.success(
                    [ProjectEntity(self._row_to_project(row, col_map)) for row in rows]
                )
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def find_all(self) -> Result[list[ProjectEntity]]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
                col_map = {desc[0]: i for i, desc in enumerate(cursor.description)}
                return Result.success(
                    [ProjectEntity(self._row_to_project(row, col_map)) for row in cursor.fetchall()]
                )
        except Exception as e:
            return Result.failure(f"Database error: {e}")

    def delete(self, project_id: str) -> Result[bool]:
        try:
            with self._connection.get_cursor() as cursor:
                cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                deleted = cursor.rowcount > 0
                self._connection.commit()
                return Result.success(deleted)
        except Exception as e:
            self._connection.rollback()
            return Result.failure(f"Database error: {e}")
