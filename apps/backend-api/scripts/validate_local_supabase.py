import asyncio
import os
import sys

# Define base path and load .env before any other imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

import structlog

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
    from taskman_api.db.session import AsyncSessionLocal, manager
    from taskman_api.repositories import (
        PostgresProjectRepository,
        PostgresSprintRepository,
        PostgresTaskRepository,
    )
except ImportError as e:
    logger.error("import_error", error=str(e))
    sys.exit(1)

async def validate():
    log = logger.bind(task="validation")
    log.info("starting_validation")

    async with AsyncSessionLocal() as session:
        project_repo = PostgresProjectRepository(session)
        sprint_repo = PostgresSprintRepository(session)
        task_repo = PostgresTaskRepository(session)

        projects = await project_repo.get_all()
        sprints = await sprint_repo.get_all()
        tasks = await task_repo.get_all()

        log.info("validation_results",
                 projects_count=len(projects),
                 sprints_count=len(sprints),
                 tasks_count=len(tasks))

        if len(projects) > 0:
            log.info("sample_project", id=projects[0].id, name=projects[0].name)
        if len(sprints) > 0:
            log.info("sample_sprint", id=sprints[0].id, name=sprints[0].name)
        if len(tasks) > 0:
            log.info("sample_task", id=tasks[0].id, title=tasks[0].title)

if __name__ == "__main__":
    asyncio.run(validate())
