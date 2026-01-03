import os
import sys

import structlog
from dotenv import load_dotenv
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

# Add src to path
sys.path.append("src")

try:
    from taskman_api.db.base import Base
    from taskman_api.models import *  # Ensure all models are registered
except ImportError as e:
    logger.error(
        "import_error", error=str(e), detail="Ensure script is run from backend-api directory"
    )
    sys.exit(1)

def main():
    load_dotenv(override=True)

    db_host = os.getenv("APP_DATABASE__HOST", "127.0.0.1")
    db_port = os.getenv("APP_DATABASE__PORT", "54322")
    db_user = os.getenv("APP_DATABASE__USER", "postgres")
    db_pass = os.getenv("APP_DATABASE__PASSWORD", "postgres")
    db_name = os.getenv("APP_DATABASE__DATABASE", "postgres")

    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    log = logger.bind(db_url=f"postgresql+psycopg2://{db_user}:***@{db_host}:{db_port}/{db_name}")

    log.info("database_initialization_started")

    try:
        engine = create_engine(db_url)

        log.info("dropping_public_schema")
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            log.info("schema_reset_success")

        log.info("creating_tables_from_models")
        Base.metadata.create_all(engine)

        # Verify tables
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]
            log.info("tables_verified", count=len(tables), tables=tables)

        log.info("tables_created_successfully")

        # Mark as migrated in alembic_version
        with engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY)"
                )
            )
            latest_version = "ee44906d5889"
            conn.execute(
                text(f"INSERT INTO alembic_version (version_num) VALUES ('{latest_version}')")
            )
            conn.commit()
            log.info("alembic_version_stamped", version=latest_version)

        log.info("database_initialization_complete")

    except SQLAlchemyError as e:
        log.error("database_operation_failed", error=str(e))
        sys.exit(1)
    except Exception as e:
        log.error("unexpected_error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
