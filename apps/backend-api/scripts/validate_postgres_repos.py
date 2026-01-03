import asyncio
import os
import sys

from dotenv import load_dotenv

# Force load .env to override stale shell variables
load_dotenv(".env", override=True)

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from taskman_api.db.session import AsyncSessionLocal, manager
from taskman_api.repositories.postgres_project_repository import PostgresProjectRepository
from taskman_api.repositories.postgres_sprint_repository import PostgresSprintRepository
from taskman_api.repositories.postgres_task_repository import PostgresTaskRepository
from taskman_api.repositories.task_repository import TaskRepository
from taskman_api.services.project_service import ProjectService
from taskman_api.services.sprint_service import SprintService
from taskman_api.services.task_service import TaskService


def log(msg):
    print(msg)
    with open("validate_repos.log", "a") as f:
        f.write(msg + "\n")

async def main():
    # Clear log
    with open("validate_repos.log", "w") as f:
        f.write("Starting Validation...\n")

    log("Validating PostgreSQL Repositories...")

    # Initialize DB (ConnectionManager)
    # This assumes .env is loaded or env vars are set
    # manager.init() is usually called by lifespan or manually?
    # manager is initialized on module import but we might need to explicit connect or just ensure it sees the config.
    # actually manager initializes on access usually or implicitly.

    # Check if using fallback
    log(f"Using Fallback: {manager._using_fallback}")
    if manager._using_fallback:
        log("WARNING: System is using Fallback (SQLite). Postgres tests may fail or use generic repo.")
    else:
        log("System is using Primary (Postgres).")

    try:
        async with AsyncSessionLocal() as session:
            # 1. Test Service Injection
            log("\n--- Testing Service Injection ---")
            task_service = TaskService(session)
            project_service = ProjectService(session)
            sprint_service = SprintService(session)

            log(f"TaskService Repo: {type(task_service.task_repo)}")
            log(f"ProjectService Repo: {type(project_service.project_repo)}")
            log(f"SprintService Repo: {type(sprint_service.sprint_repo)}")

            if not manager._using_fallback:
                assert isinstance(task_service.task_repo, PostgresTaskRepository), "TaskService should use PostgresTaskRepository"
                assert isinstance(project_service.project_repo, PostgresProjectRepository), "ProjectService should use PostgresProjectRepository"
                assert isinstance(sprint_service.sprint_repo, PostgresSprintRepository), "SprintService should use PostgresSprintRepository"
                log("SUCCESS: Correct Repositories Injected.")
            else:
                assert isinstance(task_service.task_repo, TaskRepository), "TaskService should use TaskRepository"
                log("SUCCESS: Correct Repositories Injected (Fallback).")

            # 2. Test Full Text Search (if Postgres)
            if not manager._using_fallback:
                log("\n--- Testing Full Text Search ---")
                repo = task_service.task_repo
                try:
                    log(f"DB URL: {manager.primary_engine.url}")
                    log("Executing search_full_text with 10s timeout...")
                    # Add timeout
                    results, count = await asyncio.wait_for(repo.search_full_text("test"), timeout=10.0)
                    log(f"Search 'test' returned {count} tasks.")
                except TimeoutError:
                    log("CRITICAL: Search timed out after 10s! Connection likely stuck.")
                except Exception as e:
                    log(f"Search failed: {e}")
                    import traceback
                    with open("validate_repos.log", "a") as f:
                        traceback.print_exc(file=f)
            else:
                 log("Skipping search (Fallback).")
    except Exception as e:
        log(f"CRITICAL ERROR: {e}")
        import traceback
        with open("validate_repos.log", "a") as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
