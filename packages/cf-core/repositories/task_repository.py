"""
Task Repository

Repository pattern implementation for Task persistence with SQLite and PostgreSQL backends.
Provides interface and concrete implementations for schema-aligned Task model.
"""

import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timezone
from typing import Any, List, Optional

from cf_core.domain.task_entity import TaskEntity
from cf_core.models.action_item import ActionItem
from cf_core.models.action_taken import ActionTaken
from cf_core.models.blocker_entry import BlockerEntry
from cf_core.models.observability import Observability
from cf_core.models.quality_gates import QualityGates
from cf_core.models.relationship_ref import RelationshipRef
from cf_core.models.risk_entry import RiskEntrySimple
from cf_core.models.task import Task
from cf_core.models.verification import Verification
from cf_core.repositories.connection import PostgresConnection, SQLiteConnection
from cf_core.shared.result import Result

logger = logging.getLogger(__name__)


class ITaskRepository(ABC):
    """
    Abstract interface for Task repository.
    """

    @abstractmethod
    def save(self, entity: TaskEntity) -> Result[TaskEntity]:
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Result[TaskEntity]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> Result[list[TaskEntity]]:
        pass

    @abstractmethod
    def find_by_assignee(self, assignee: str) -> Result[list[TaskEntity]]:
        pass

    @abstractmethod
    def find_by_sprint(self, sprint_id: str) -> Result[list[TaskEntity]]:
        pass

    @abstractmethod
    def find_all(self) -> Result[list[TaskEntity]]:
        pass

    @abstractmethod
    def search(
        self,
        query: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        sprint_id: str | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TaskEntity]]:
        pass

    @abstractmethod
    def count(self) -> Result[int]:
        pass

    @abstractmethod
    def delete(self, task_id: str) -> Result[bool]:
        pass


class SqliteTaskRepository(ITaskRepository):
    """
    SQLite implementation of the Task repository.
    """

    def __init__(self, db_path: str):
        self._db_path = db_path
        self.db = SQLiteConnection(db_path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create tasks table if it doesn't exist."""
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                # Simplified schema for SQLite (using TEXT/JSON mostly)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        status TEXT NOT NULL,
                        priority TEXT NOT NULL DEFAULT 'medium',
                        description TEXT,
                        project_id TEXT,
                        sprint_id TEXT,
                        assignee TEXT,
                        blocked_reason TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        completed_at TEXT,
                        estimated_hours REAL,
                        actual_hours REAL,
                        tags TEXT,
                        depends_on TEXT,
                        action_items TEXT,

                        -- New Fields (Phase 2)
                        summary TEXT,
                        owner TEXT,
                        primary_project TEXT,
                        primary_sprint TEXT,
                        observability TEXT,
                        labels TEXT,
                        severity TEXT,
                        work_type TEXT,
                        work_stream TEXT,
                        stage TEXT,
                        shape TEXT,
                        assignees TEXT,
                        parents TEXT,
                        blocks TEXT,
                        related_projects TEXT,
                        related_sprints TEXT,
                        related_links TEXT,
                        estimate_points REAL,
                        story_points INTEGER,
                        actual_time_hours REAL,
                        due_at TEXT,
                        due_date TEXT,
                        last_heartbeat_utc TEXT,
                        acceptance_criteria TEXT,
                        definition_of_done TEXT,
                        blockers TEXT,
                        actions_taken TEXT,
                        quality_gates TEXT,
                        verification TEXT,
                        risks TEXT,
                        business_value_score INTEGER,
                        cost_of_delay_score INTEGER,
                        automation_candidate INTEGER,
                        cycle_time_days REAL
                    )
                """)
        except sqlite3.Error as e:
            logger.error(f"SQLite schema creation error: {e}")

    def _task_to_row(self, task: Task) -> dict:
        """Convert Task model to dictionary for SQLite insertion."""

        # Helper for JSON serialization with datetime handling
        def to_json(obj):
            if obj is None:
                return None
            if hasattr(obj, "model_dump"):
                return json.dumps(obj.model_dump(mode="json"))  # mode="json" handles datetime
            if isinstance(obj, list) and obj and hasattr(obj[0], "model_dump"):
                return json.dumps([item.model_dump(mode="json") for item in obj])
            return json.dumps(obj, default=str)  # fallback: convert datetime to string

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": f"p{min(task.priority, 3)}",
            "description": task.description,
            # Legacy
            "project_id": task.project_id,
            "sprint_id": task.sprint_id,
            "assignee": task.assignee,
            "blocked_reason": task.blocked_reason,
            # Timestamps
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            # Legacy metrics
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            # JSON arrays
            "tags": to_json(task.tags),
            "depends_on": to_json(task.depends_on),
            "action_items": to_json(task.action_items),
            # NEW FIELDS
            "summary": task.summary,
            "owner": task.owner,
            "primary_project": task.primary_project,
            "primary_sprint": task.primary_sprint,
            "observability": to_json(task.observability),
            "labels": to_json(task.labels),
            "severity": task.severity,
            "work_type": task.work_type,
            "work_stream": task.work_stream,
            "stage": task.stage,
            "shape": task.shape,
            "assignees": to_json(task.assignees),
            "parents": to_json(task.parents),
            "blocks": to_json(task.blocks),
            "related_projects": to_json(task.related_projects),
            "related_sprints": to_json(task.related_sprints),
            "related_links": to_json(task.related_links),
            "estimate_points": task.estimate_points,
            "story_points": task.story_points,
            "actual_time_hours": task.actual_time_hours,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "acceptance_criteria": to_json(task.acceptance_criteria),
            "definition_of_done": to_json(task.definition_of_done),
            "blockers": to_json(task.blockers),
            "actions_taken": to_json(task.actions_taken),
            "quality_gates": to_json(task.quality_gates),
            "verification": to_json(task.verification),
            "risks": to_json(task.risks),
            "business_value_score": task.business_value_score,
            "cost_of_delay_score": task.cost_of_delay_score,
            "automation_candidate": 1 if task.automation_candidate else 0,
            "cycle_time_days": task.cycle_time_days,
        }

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert database row to Task model."""

        # Helper helpers
        def parse_date(s):
            return datetime.fromisoformat(s) if s else None

        def parse_json(s, default=None):
            return json.loads(s) if s else (default if default is not None else [])

        # Parse Observability
        obs_data = parse_json(row["observability"], {})
        if obs_data:
            observability = Observability(**obs_data)
        else:
            observability = Observability.create_healthy()

        # Parse Complex Lists
        blockers = [BlockerEntry(**b) for b in parse_json(row["blockers"])]
        actions_taken = [ActionTaken(**a) for a in parse_json(row["actions_taken"])]
        related_projects = [RelationshipRef(**r) for r in parse_json(row["related_projects"])]
        related_sprints = [RelationshipRef(**r) for r in parse_json(row["related_sprints"])]
        risks = [RiskEntrySimple(**r) for r in parse_json(row["risks"])]
        action_items = [ActionItem(**ai) for ai in parse_json(row["action_items"])]

        # Parse Complex Objects
        qg_data = parse_json(row["quality_gates"], None)
        quality_gates = QualityGates(**qg_data) if qg_data else None

        ver_data = parse_json(row["verification"], None)
        verification = Verification(**ver_data) if ver_data else None

        # Fallbacks for required fields if data is missing (migration)
        primary_project = row["primary_project"] or row["project_id"] or "P-UNKNOWN"
        primary_sprint = row["primary_sprint"] or row["sprint_id"] or "S-BACKLOG"
        owner = row["owner"] or row["assignee"] or "unassigned"
        summary = row["summary"] or row["title"] or "No summary"

        return Task(
            id=row["id"],
            title=row["title"],
            summary=summary,
            description=row["description"] or "",
            status=row["status"],
            owner=owner,
            priority=row["priority"] or "medium",
            created_at=parse_date(row["created_at"]) or datetime.now(UTC),
            updated_at=parse_date(row["updated_at"]) or datetime.now(UTC),
            primary_project=primary_project,
            primary_sprint=primary_sprint,
            observability=observability,
            # Optional fields
            assignees=parse_json(row["assignees"]),
            parents=parse_json(row["parents"]),
            depends_on=parse_json(row["depends_on"]),
            blocks=parse_json(row["blocks"]),
            related_projects=related_projects,
            related_sprints=related_sprints,
            related_links=parse_json(row["related_links"]),
            estimate_points=row["estimate_points"],
            story_points=row["story_points"],
            actual_time_hours=row["actual_time_hours"],
            due_at=parse_date(row["due_at"]),
            due_date=parse_date(row["due_date"]),
            labels=parse_json(row["labels"]) or parse_json(row["tags"]) or [],
            # Backward compatibility: populate tags from database tags column
            tags=parse_json(row["tags"]) or [],
            severity=row["severity"],
            work_type=row["work_type"],
            work_stream=row["work_stream"],
            stage=row["stage"],
            shape=row["shape"],
            acceptance_criteria=parse_json(row["acceptance_criteria"]),
            definition_of_done=parse_json(row["definition_of_done"]),
            blockers=blockers,
            actions_taken=actions_taken,
            quality_gates=quality_gates,
            verification=verification,
            risks=risks,
            business_value_score=row["business_value_score"],
            cost_of_delay_score=row["cost_of_delay_score"],
            automation_candidate=bool(row["automation_candidate"]),
            cycle_time_days=row["cycle_time_days"],
            completed_at=parse_date(row["completed_at"]),
            # Legacy fields (auto-synced by model but passed here for completeness)
            project_id=row["project_id"],
            sprint_id=row["sprint_id"],
            assignee=row["assignee"],
            blocked_reason=row["blocked_reason"],
            estimated_hours=row["estimated_hours"],
            actual_hours=row["actual_hours"],
            action_items=action_items,
        )

    def save(self, entity: TaskEntity) -> Result[TaskEntity]:
        try:
            row_dict = self._task_to_row(entity.task)
            columns = ", ".join(row_dict.keys())
            placeholders = ", ".join(["?"] * len(row_dict))
            values = list(row_dict.values())

            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO tasks ({columns}) VALUES ({placeholders})", values
                )
                return Result.success(entity)
        except sqlite3.Error as e:
            return Result.failure(f"Database error saving task: {e}")

    # ... get_by_id, search, etc using row_factory
    def get_by_id(self, task_id: str) -> Result[TaskEntity]:
        try:
            with self.db.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if not row:
                    return Result.failure(f"Task with id '{task_id}' not found")
                return Result.success(TaskEntity(self._row_to_task(row)))
        except sqlite3.Error as e:
            return Result.failure(f"Database error getting task: {e}")

    def search(self, **filters) -> Result[list[TaskEntity]]:
        # Implementing search using dynamic filter builder
        try:
            with self.db.connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                sql = "SELECT * FROM tasks WHERE 1=1"
                params = []

                # Filter by status
                status = filters.get("status")
                if status:
                    sql += " AND status = ?"
                    params.append(status)

                # Filter by assignee
                assignee = filters.get("assignee")
                if assignee:
                    sql += " AND assignee = ?"
                    params.append(assignee)

                # Filter by sprint_id
                sprint_id = filters.get("sprint_id")
                if sprint_id:
                    sql += " AND sprint_id = ?"
                    params.append(sprint_id)

                # Filter by query (title/description search)
                query = filters.get("query")
                if query:
                    sql += " AND (title LIKE ? OR description LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])

                limit = filters.get("limit", 100)
                offset = filters.get("offset", 0)

                sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return Result.success([TaskEntity(self._row_to_task(row)) for row in rows])
        except sqlite3.Error as e:
            return Result.failure(f"Error: {e}")

    # Standard implementations for interface methods
    def find_by_status(self, status: str) -> Result[list[TaskEntity]]:
        return self.search(status=status)

    def find_by_assignee(self, assignee: str) -> Result[list[TaskEntity]]:
        return self.search(assignee=assignee)

    def find_by_sprint(self, sprint_id: str) -> Result[list[TaskEntity]]:
        return self.search(sprint_id=sprint_id)

    def find_all(self) -> Result[list[TaskEntity]]:
        return self.search(limit=1000)

    def count(self) -> Result[int]:
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tasks")
                return Result.success(cursor.fetchone()[0])
        except sqlite3.Error as e:
            return Result.failure(str(e))

    def delete(self, task_id: str) -> Result[bool]:
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                if cursor.rowcount == 0:
                    return Result.failure(f"Task with id '{task_id}' not found")
                return Result.success(True)
        except sqlite3.Error as e:
            return Result.failure(str(e))


class PostgresTaskRepository(ITaskRepository):
    """
    PostgreSQL implementation of the Task repository.
    """

    def __init__(self, connection: PostgresConnection):
        self.db = connection
        # Schema already handled by migrations (0005)

    def _task_to_row(self, task: Task) -> dict:
        """Convert Task model to dictionary for PostgreSQL insertion."""
        # Similar to SQLite but JSON fields handled by adapter
        # But we pass dict keys to INSERT, so we need consistent map

        # Helper to serialize objects to JSON string, handling datetime
        def to_json(obj):
            if obj is None:
                return None
            if hasattr(obj, "model_dump"):
                return json.dumps(obj.model_dump(mode="json"))  # mode="json" handles datetime
            if isinstance(obj, list) and obj and hasattr(obj[0], "model_dump"):
                return json.dumps([item.model_dump(mode="json") for item in obj])
            return json.dumps(obj, default=str)  # fallback for datetime

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": f"p{min(task.priority, 3)}",
            "description": task.description,
            # Legacy
            "project_id": task.project_id,
            "sprint_id": task.sprint_id,
            "assignee": task.assignee,
            "blocked_reason": task.blocked_reason,
            # Timestamps
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at,
            # Legacy metrics
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            # JSON arrays - Postgres adapter can handle list/dict for JSONB?
            # Safer to use json.dumps for strict JSONB conformance via string
            "tags": to_json(task.tags),
            "depends_on": to_json(task.depends_on),
            "action_items": to_json(task.action_items),
            # NEW FIELDS
            "summary": task.summary,
            "owner": task.owner,
            "primary_project": task.primary_project,
            "primary_sprint": task.primary_sprint,
            "observability": to_json(task.observability),
            "labels": to_json(task.labels),
            "severity": task.severity,
            "work_type": task.work_type,
            "work_stream": task.work_stream,
            "stage": task.stage,
            "shape": task.shape,
            "assignees": to_json(task.assignees),
            "parents": to_json(task.parents),
            "blocks": to_json(task.blocks),
            "related_projects": to_json(task.related_projects),
            "related_sprints": to_json(task.related_sprints),
            "related_links": to_json(task.related_links),
            "estimate_points": task.estimate_points,
            "story_points": task.story_points,
            "actual_time_hours": task.actual_time_hours,
            "due_at": task.due_at,
            "due_date": task.due_date,
            "acceptance_criteria": to_json(task.acceptance_criteria),
            "definition_of_done": to_json(task.definition_of_done),
            "blockers": to_json(task.blockers),
            "actions_taken": to_json(task.actions_taken),
            "quality_gates": to_json(task.quality_gates),
            "verification": to_json(task.verification),
            "risks": to_json(task.risks),
            "business_value_score": task.business_value_score,
            "cost_of_delay_score": task.cost_of_delay_score,
            "automation_candidate": 1 if task.automation_candidate else 0,
            "cycle_time_days": task.cycle_time_days,
        }

    def _row_to_task(self, row: dict) -> Task:
        """Convert database row to Task model."""

        # Helper helpers
        def parse_json_field(val, default=None):
            if val is None:
                return default if default is not None else []
            if isinstance(val, str):
                return json.loads(val)
            return val  # Already parsed by psycopg2

        # Parse Observability
        obs_data = parse_json_field(row.get("observability"), {})
        if obs_data:
            observability = Observability(**obs_data)
        else:
            observability = Observability.create_healthy()

        # Parse Complex Lists
        blockers = [BlockerEntry(**b) for b in parse_json_field(row.get("blockers"))]
        actions_taken = [ActionTaken(**a) for a in parse_json_field(row.get("actions_taken"))]
        related_projects = [
            RelationshipRef(**r) for r in parse_json_field(row.get("related_projects"))
        ]
        related_sprints = [
            RelationshipRef(**r) for r in parse_json_field(row.get("related_sprints"))
        ]
        risks = [RiskEntrySimple(**r) for r in parse_json_field(row.get("risks"))]
        action_items = [ActionItem(**ai) for ai in parse_json_field(row.get("action_items"))]

        # Parse Complex Objects
        qg_data = parse_json_field(row.get("quality_gates"), None)
        quality_gates = QualityGates(**qg_data) if qg_data else None

        ver_data = parse_json_field(row.get("verification"), None)
        verification = Verification(**ver_data) if ver_data else None

        # Fallbacks
        primary_project = row.get("primary_project") or row.get("project_id") or "P-UNKNOWN"
        primary_sprint = row.get("primary_sprint") or row.get("sprint_id") or "S-BACKLOG"
        owner = row.get("owner") or row.get("assignee") or "unassigned"
        summary = row.get("summary") or row.get("title") or "No summary"

        return Task(
            id=row["id"],
            title=row["title"],
            summary=summary,
            description=row.get("description") or "",
            status=row["status"],
            owner=owner,
            priority=row.get("priority", "medium"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            primary_project=primary_project,
            primary_sprint=primary_sprint,
            observability=observability,
            # Optional fields
            assignees=parse_json_field(row.get("assignees")),
            parents=parse_json_field(row.get("parents")),
            depends_on=parse_json_field(row.get("depends_on")),
            blocks=parse_json_field(row.get("blocks")),
            related_projects=related_projects,
            related_sprints=related_sprints,
            related_links=parse_json_field(row.get("related_links")),
            estimate_points=row.get("estimate_points"),
            story_points=row.get("story_points"),
            actual_time_hours=row.get("actual_time_hours"),
            due_at=row.get("due_at"),
            due_date=row.get("due_date"),
            labels=parse_json_field(row.get("labels")) or parse_json_field(row.get("tags")) or [],
            severity=row.get("severity"),
            work_type=row.get("work_type"),
            work_stream=row.get("work_stream"),
            stage=row.get("stage"),
            shape=row.get("shape"),
            acceptance_criteria=parse_json_field(row.get("acceptance_criteria")),
            definition_of_done=parse_json_field(row.get("definition_of_done")),
            blockers=blockers,
            actions_taken=actions_taken,
            quality_gates=quality_gates,
            verification=verification,
            risks=risks,
            business_value_score=row.get("business_value_score"),
            cost_of_delay_score=row.get("cost_of_delay_score"),
            automation_candidate=bool(row.get("automation_candidate", 0)),
            cycle_time_days=row.get("cycle_time_days"),
            completed_at=row.get("completed_at"),
            # Legacy fields
            project_id=row.get("project_id"),
            sprint_id=row.get("sprint_id"),
            assignee=row.get("assignee"),
            blocked_reason=row.get("blocked_reason"),
            estimated_hours=row.get("estimated_hours"),
            actual_hours=row.get("actual_hours"),
            action_items=action_items,
        )

    def save(self, entity: TaskEntity) -> Result[TaskEntity]:
        try:
            row_dict = self._task_to_row(entity.task)
            columns = ", ".join(row_dict.keys())
            placeholders = ", ".join(["%s"] * len(row_dict))
            values = list(row_dict.values())

            # Construct ON CONFLICT logic for UPSERT - update all columns except ID and created_at
            update_clause = ", ".join(
                [f"{k} = EXCLUDED.{k}" for k in row_dict.keys() if k not in ["id", "created_at"]]
            )

            sql = f"""
                INSERT INTO tasks ({columns}) VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET {update_clause}
            """

            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, values)
            return Result.success(entity)
        except Exception as e:
            return Result.failure(f"PostgreSQL error saving task: {e}")

    def get_by_id(self, task_id: str) -> Result[TaskEntity]:
        try:
            from psycopg2.extras import RealDictCursor
            with self.db.connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                    row = cursor.fetchone()
                    if not row:
                        return Result.failure(f"Task with id '{task_id}' not found")
                    return Result.success(TaskEntity(self._row_to_task(row)))
        except Exception as e:
            return Result.failure(f"PostgreSQL error getting task: {e}")

    def search(self, **filters) -> Result[list[TaskEntity]]:
        try:
            from psycopg2.extras import RealDictCursor
            with self.db.connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    sql = "SELECT * FROM tasks WHERE 1=1"
                    params = []

                    # Basic filters
                    for key in ["status", "priority", "assignee", "sprint_id", "project_id"]:
                        val = filters.get(key)
                        if val:
                            sql += f" AND {key} = %s"
                            params.append(val)

                    query = filters.get("query")
                    if query:
                        sql += " AND (title ILIKE %s OR description ILIKE %s)"
                        params.extend([f"%{query}%", f"%{query}%"])

                    limit = filters.get("limit", 100)
                    offset = filters.get("offset", 0)

                    sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                    params.extend([limit, offset])

                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    return Result.success([TaskEntity(self._row_to_task(row)) for row in rows])
        except Exception as e:
            return Result.failure(f"PostgreSQL error: {e}")

    def count(self) -> Result[int]:
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM tasks")
                    return Result.success(cursor.fetchone()[0])
        except Exception as e:
            return Result.failure(str(e))

    def delete(self, task_id: str) -> Result[bool]:
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                    return Result.success(cursor.rowcount > 0)
        except Exception as e:
            return Result.failure(str(e))

    # Standard implementations
    def find_by_status(self, status: str) -> Result[list[TaskEntity]]:
        return self.search(status=status)

    def find_by_assignee(self, assignee: str) -> Result[list[TaskEntity]]:
        return self.search(assignee=assignee)

    def find_by_sprint(self, sprint_id: str) -> Result[list[TaskEntity]]:
        return self.search(sprint_id=sprint_id)

    def find_all(self) -> Result[list[TaskEntity]]:
        return self.search(limit=1000)
