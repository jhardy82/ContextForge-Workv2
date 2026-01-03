import asyncio
import json
import os
import sys

# Define base path and load .env before any other imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

import structlog
from dateutil import parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

# Add src to path
sys.path.append(os.path.join(BASE_DIR, "src"))

try:
    from taskman_api.db.base import Base
    from taskman_api.models import Project, Sprint, Task
except ImportError as e:
    logger.error(
        "import_error",
        error=str(e),
        detail=f"Run from backend-api directory. Path: {os.path.join(BASE_DIR, 'src')}",
    )
    sys.exit(1)


def safe_parse_json(value):
    if not value:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except:
        return value


def safe_parse_datetime(value):
    if not value:
        return None
    try:
        # Pydantic/SQLAlchemy might handle strings for Projects/Sprints if they are String(32)
        # But for Task, they are actual DateTime objects.
        return parser.parse(value)
    except:
        return None


async def seed_data(session_factory, data):
    log = logger.bind(task="seeding")

    # 1. Seed Projects
    log.info("seeding_projects", count=len(data.get("projects", [])))
    with session_factory() as session:
        for p_data in data.get("projects", []):
            obs = p_data.get("observability") or {}
            project = Project(
                id=p_data["id"],
                name=p_data.get("name"),
                title=p_data.get("title"),
                mission=p_data.get("mission"),
                description=p_data.get("description"),
                status=p_data.get("status", "new"),
                owner=p_data.get("owner"),
                sponsors=safe_parse_json(p_data.get("sponsors")),
                stakeholders=safe_parse_json(p_data.get("stakeholders")),
                start_date=p_data.get("start_date"),
                target_end_date=p_data.get("target_end_date"),
                actual_end_date=p_data.get("actual_end_date"),
                created_at=p_data.get("created_at"),
                updated_at=p_data.get("updated_at"),
                last_health=obs.get("last_health"),
                last_heartbeat_utc=obs.get("last_heartbeat_utc"),
                risks=safe_parse_json(p_data.get("risks")),
            )
            session.merge(project)
        session.commit()
    log.info("projects_seeded")

    # 2. Seed Sprints
    log.info("seeding_sprints", count=len(data.get("sprints", [])))
    with session_factory() as session:
        for s_data in data.get("sprints", []):
            obs = safe_parse_json(s_data.get("observability")) or {}
            sprint = Sprint(
                id=s_data["id"],
                name=s_data.get("name"),
                title=s_data.get("title"),
                goal=s_data.get("goal"),
                status=s_data.get("status", "planned"),
                project_id=s_data.get("project_id"),
                start_date=s_data.get("start_date"),
                end_date=s_data.get("end_date"),
                created_at=s_data.get("created_at"),
                updated_at=s_data.get("updated_at"),
                last_health=obs.get("last_health"),
                last_heartbeat_utc=obs.get("last_heartbeat_utc"),
                observability=obs,
                risks=safe_parse_json(s_data.get("risks")),
            )
            session.merge(sprint)
        session.commit()
    log.info("sprints_seeded")

    # 3. Seed Tasks
    log.info("seeding_tasks", count=len(data.get("tasks", [])))
    with session_factory() as session:
        for t_data in data.get("tasks", []):
            obs = t_data.get("observability") or {}
            # Ensure mandatory fields are not None
            task = Task(
                id=t_data["id"],
                title=t_data.get("title") or "Untitled Task",
                summary=t_data.get("summary") or t_data.get("title") or "No Summary",
                description=t_data.get("description") or "",
                status=t_data.get("status", "new"),
                owner=t_data.get("owner", "unassigned"),
                primary_project=t_data.get("primary_project")
                or t_data.get("project_id")
                or "P-DEFAULT",
                primary_sprint=t_data.get("primary_sprint")
                or t_data.get("sprint_id")
                or "S-DEFAULT",
                priority=str(t_data.get("priority") or "p2").lower(),
                created_at=safe_parse_datetime(t_data.get("created_at")),
                updated_at=safe_parse_datetime(t_data.get("updated_at")),
                due_at=safe_parse_datetime(t_data.get("due_at")),
                observability=obs,
                tags=str(t_data.get("tags", "")),
                labels=safe_parse_json(t_data.get("labels")),
            )
            session.merge(task)
        session.commit()
    log.info("tasks_seeded")


def main():
    # Target: Local Supabase
    db_host = os.getenv("APP_DATABASE__HOST", "127.0.0.1")
    db_port = os.getenv("APP_DATABASE__PORT", "54322")
    db_user = os.getenv("APP_DATABASE__USER", "postgres")
    db_pass = os.getenv("APP_DATABASE__PASSWORD", "postgres")
    db_name = os.getenv("APP_DATABASE__DATABASE", "postgres")

    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    # Load legacy data
    dump_path = os.path.join(os.path.dirname(BASE_DIR), "exports", "contextforge_dump.json")
    if not os.path.exists(dump_path):
        logger.error("dump_not_found", path=dump_path)
        sys.exit(1)

    with open(dump_path) as f:
        data = json.load(f)

    asyncio.run(seed_data(Session, data))
    logger.info("seeding_process_finished")


if __name__ == "__main__":
    main()
