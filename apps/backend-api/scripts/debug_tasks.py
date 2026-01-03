import asyncio
import os
import sys

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import get_async_session as get_session
from repositories.task_repository import TaskRepository


async def debug_tasks():
    print("--- DEBUGGNG TASKS ENDPOINT LOGIC ---")
    try:
        session_gen = get_session()
        session = await anext(session_gen)
        print("Session retrieved.")

        repo = TaskRepository(session)
        print("Repository initialized.")

        print("Attempting to fetch tasks...")
        tasks = await repo.get_all()
        print(f"Successfully retrieved {len(tasks)} tasks.")
        for t in tasks:
            print(f"- {t.title} (ID: {t.id})")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'session' in locals():
            await session.close()
        print("--- END DEBUG ---")

if __name__ == "__main__":
    asyncio.run(debug_tasks())
