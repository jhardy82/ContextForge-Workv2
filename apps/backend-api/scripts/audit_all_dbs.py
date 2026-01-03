import os
import sqlite3

import structlog
from sqlalchemy import create_engine, text
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


def audit_postgres(port, user, password, database):
    db_url = f"postgresql+psycopg2://{user}:{password}@127.0.0.1:{port}/{database}"
    log = logger.bind(port=port, db=database, type="postgres")
    log.info("auditing_database")

    try:
        # Use short timeout for connection
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]

            summary = {}
            for table in tables:
                try:
                    cnt = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                    summary[table] = cnt
                except:
                    summary[table] = "error"

            log.info("audit_complete", table_count=len(tables), summary=summary)
            return summary
    except SQLAlchemyError as e:
        log.error("audit_failed", error=str(e))
        return None


def audit_sqlite(path):
    log = logger.bind(path=path, type="sqlite")
    log.info("auditing_database")
    if not os.path.exists(path):
        log.error("file_not_found")
        return None

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        summary = {}
        for table in tables:
            cursor.execute(f"SELECT count(*) FROM {table}")
            summary[table] = cursor.fetchone()[0]

        log.info("audit_complete", table_count=len(tables), summary=summary)
        conn.close()
        return summary
    except Exception as e:
        log.error("audit_failed", error=str(e))
        return None


def main():
    targets = [
        {
            "type": "pg",
            "port": 5432,
            "user": "context_admin",
            "pass": "SacredGeometry123!",
            "db": "context_forge",
        },
        {
            "type": "pg",
            "port": 5433,
            "user": "contextforge",
            "pass": "contextforge",
            "db": "contextforge",
        },
        {
            "type": "pg",
            "port": 5435,
            "user": "taskman",
            "pass": "taskman_dev_password",
            "db": "taskman_dev",
        },
        {"type": "pg", "port": 5434, "user": "postgres", "pass": "postgres", "db": "taskman_v2"},
        {"type": "sqlite", "path": "taskman.db"},
        {"type": "sqlite", "path": "backend-api/taskman.db"},
        {"type": "sqlite", "path": "contextforge.db"},
        {"type": "sqlite", "path": "tasks.db"},
        {"type": "sqlite", "path": "orch.sqlite"},
        {"type": "sqlite", "path": "tracker.sqlite"},
    ]

    for t in targets:
        if t["type"] == "pg":
            audit_postgres(t["port"], t["user"], t["pass"], t["db"])
        else:
            audit_sqlite(t["path"])


if __name__ == "__main__":
    main()
