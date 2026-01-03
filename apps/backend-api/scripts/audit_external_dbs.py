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

def audit_db(port, user, password, database):
    db_url = f"postgresql+psycopg2://{user}:{password}@127.0.0.1:{port}/{database}"
    log = logger.bind(port=port, db=database)
    log.info("auditing_database")

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Check for tables
            result = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]

            summary = {}
            for table in tables:
                cnt = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                summary[table] = cnt

            log.info("audit_complete", table_count=len(tables), summary=summary)
            return summary
    except SQLAlchemyError as e:
        log.error("audit_failed", error=str(e))
        return None

def main():
    # Ports to check
    targets = [
        {"port": 5432, "user": "postgres", "pass": "postgres", "db": "postgres"},
        {"port": 5434, "user": "postgres", "pass": "postgres", "db": "postgres"},
        {"port": 5434, "user": "contextforge", "pass": "contextforge", "db": "taskman_v2"},
    ]

    combined_results = {}
    for t in targets:
        res = audit_db(t["port"], t["user"], t["pass"], t["db"])
        if res:
            combined_results[f"{t['port']}_{t['db']}"] = res

    print(f"Audit results: {combined_results}")

if __name__ == "__main__":
    main()
