import asyncio
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Define connection details explicitly (matching migrate_postgres.py)
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "5434",
    "user": "contextforge",
    "password": "contextforge",
    "database": "taskman_v2"
}

DATABASE_URL = f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

async def reset_schema():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        print("Dropping all tables in public schema...")
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        print("Schema reset complete.")

    await engine.dispose()

def run_alembic_upgrade():
    print("Running Alembic upgrade head...")
    backend_api_path = Path(__file__).parent.parent

    # Setup environment exactly like migrate_postgres.py
    env = os.environ.copy()
    if "DATABASE_URL" in env:
        del env["DATABASE_URL"]

    env["APP_DATABASE__HOST"] = DB_CONFIG["host"]
    env["APP_DATABASE__PORT"] = DB_CONFIG["port"]
    env["APP_DATABASE__USER"] = DB_CONFIG["user"]
    env["APP_DATABASE__PASSWORD"] = DB_CONFIG["password"]
    env["APP_DATABASE__DATABASE"] = DB_CONFIG["database"]

    cmd = [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"]

    process = subprocess.run(
        cmd,
        cwd=backend_api_path,
        env=env,
        capture_output=True,
        text=True
    )

    print("--- STDOUT ---")
    print(process.stdout)
    print("--- STDERR ---")
    print(process.stderr)

    if process.returncode != 0:
        print(f"Alembic upgrade failed with code {process.returncode}")
        sys.exit(process.returncode)
    else:
        print("Alembic upgrade successful.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(reset_schema())
        run_alembic_upgrade()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
