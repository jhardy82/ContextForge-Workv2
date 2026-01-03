import asyncio
import json
import os
import sys

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
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

# Source database configuration for port 5433
DB_USER = "contextforge"
DB_PASS = "contextforge"
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_NAME = "contextforge"

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def export_table(session, table_name, log):
    try:
        result = await session.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = []
        for row in result:
            # Map Row object to dictionary
            rows.append(dict(zip(columns, row, strict=False)))
        log.info("table_exported", table=table_name, row_count=len(rows))
        return rows
    except Exception as e:
        log.error("table_export_failed", table=table_name, error=str(e))
        return []

async def main():
    log = logger.bind(port=DB_PORT, db=DB_NAME)
    log.info("inspection_started")

    engine = create_async_engine(DB_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    data = {}
    target_tables = ["projects", "sprints", "tasks", "contexts", "schema_versions"]

    try:
        async with async_session() as session:
            for table in target_tables:
                data[table] = await export_table(session, table, log)

        log.info("inspection_complete", table_count=len(data))
    except Exception as e:
        log.error("connection_failed", error=str(e))
    finally:
        await engine.dispose()

    # Save to file
    os.makedirs("exports", exist_ok=True)
    output_path = "exports/contextforge_dump.json"
    try:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        log.info("dump_written", path=output_path)
    except Exception as e:
        log.error("file_write_failed", path=output_path, error=str(e))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
