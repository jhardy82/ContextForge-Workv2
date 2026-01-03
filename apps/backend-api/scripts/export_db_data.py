import asyncio
import json
import os
import sys

import structlog
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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
sys.path.append("src")

try:
    from taskman_api.db.connection_manager import ConnectionManager
except ImportError as e:
    logger.error(
        "import_error", error=str(e), detail="Ensure script is run from backend-api directory"
    )
    sys.exit(1)

async def export_table(session, table_name, log):
    try:
        result = await session.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = []
        for row in result:
            # zip might need mapping if row is not positional
            rows.append(dict(zip(columns, row, strict=False)))
        log.info("table_exported", table=table_name, row_count=len(rows))
        return rows
    except SQLAlchemyError as e:
        log.error("table_export_failed", table=table_name, error=str(e))
        return []

async def get_tables(session, log):
    try:
        # Check dialect
        dialect = session.bind.dialect.name
        if dialect == "postgresql":
            query = text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
        else:
            query = text("SELECT name FROM sqlite_master WHERE type='table'")

        result = await session.execute(query)
        tables = [row[0] for row in result]
        log.info("tables_discovered", count=len(tables), tables=tables)
        return tables
    except SQLAlchemyError as e:
        log.error("table_discovery_failed", error=str(e))
        return []


async def export_db(manager, source_name):
    log = logger.bind(source=source_name)
    log.info("database_export_started")
    data = {}

    try:
        session_factory = (
            manager.PrimarySession if source_name == "primary" else manager.FallbackSession
        )
        async with session_factory() as session:
            tables = await get_tables(session, log)
            for table in tables:
                if table == "alembic_version":
                    continue
                data[table] = await export_table(session, table, log)
        log.info("database_export_complete", table_count=len(data))
    except Exception as e:
        log.error("database_connection_failed", error=str(e))

    return data


async def main():
    load_dotenv(override=True)

    db_host = os.getenv("APP_DATABASE__HOST")
    db_port = os.getenv("APP_DATABASE__PORT", "5432")
    db_user = os.getenv("APP_DATABASE__USER")
    db_pass = os.getenv("APP_DATABASE__PASSWORD")
    db_name = os.getenv("APP_DATABASE__DATABASE")

    if not all([db_host, db_user, db_pass, db_name]):
        logger.error("missing_env_vars", detail="Ensure APP_DATABASE__* vars are set in .env")
        # Don't exit, ConnectionManager might handle it or we might only want fallback

    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    logger.info("initializing_connection_manager")
    manager = ConnectionManager(database_url=db_url, sqlite_path="taskman.db")

    export_data = {
        "primary": await export_db(manager, "primary"),
        "fallback": await export_db(manager, "fallback"),
    }

    os.makedirs("exports", exist_ok=True)
    output_path = "exports/db_export.json"
    try:
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        logger.info("export_file_written", path=output_path)
    except Exception as e:
        logger.error("file_write_failed", path=output_path, error=str(e))

    # Summary Audit
    for source in ["primary", "fallback"]:
        summary = {table: len(rows) for table, rows in export_data[source].items()}
        logger.info("source_summary", source=source, audit=summary)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
