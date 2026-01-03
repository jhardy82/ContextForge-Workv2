import os
import traceback

import psycopg2
from dotenv import load_dotenv

# Load .env
load_dotenv(".env", override=True)


def log(msg):
    with open("verify_db.log", "a") as f:
        f.write(str(msg) + "\n")


def verify_connection():
    with open("verify_db.log", "w") as f:
        f.write("Starting DB Verify...\n")

    user = os.getenv("APP_DATABASE__USER")
    password = os.getenv("APP_DATABASE__PASSWORD")
    host = os.getenv("APP_DATABASE__HOST")
    port = os.getenv("APP_DATABASE__PORT", "5432")
    db_name = os.getenv("APP_DATABASE__DATABASE", "postgres")

    log(f"Connecting to {host}:{port} as {user}...")

    try:
        conn = psycopg2.connect(
            host=host, user=user, password=password, port=port, dbname=db_name, sslmode="require"
        )
        log("Connected successfully!")

        cur = conn.cursor()

        # Check alembic version
        log("Checking alembic_version...")
        try:
            cur.execute("SELECT version_num FROM alembic_version")
            row = cur.fetchone()
            log(f"Current migration version: {row[0] if row else 'None'}")
        except psycopg2.errors.UndefinedTable:
            log("alembic_version table does not exist.")
            conn.rollback()  # Reset transaction

        # Check tasks table
        log("Checking tables...")
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [r[0] for r in cur.fetchall()]
        log(f"Tables found: {tables}")

        if "tasks" in tables:
            log("Checking tasks columns...")
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name='tasks'"
            )
            columns = [r[0] for r in cur.fetchall()]
            log(f"Tasks columns: {columns}")
            if "project_id" in columns:
                log("SUCCESS: project_id exists.")
            else:
                log("FAILURE: project_id MISSING.")
        else:
            log("FAILURE: tasks table MISSING.")

        conn.close()

    except Exception as e:
        log(f"Connection failed: {e}")
        log(traceback.format_exc())


if __name__ == "__main__":
    verify_connection()
