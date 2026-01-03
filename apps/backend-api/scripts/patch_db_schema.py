import os
import sys

from sqlalchemy import create_engine, text

# Define base path and load .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

def patch_schema():
    print("Patching database schema (Sync)...")

    # DB Config (Match seed_local_db.py defaults)
    db_host = os.getenv("APP_DATABASE__HOST", "127.0.0.1")
    db_port = os.getenv("APP_DATABASE__PORT", "54322")
    db_user = os.getenv("APP_DATABASE__USER", "postgres")
    db_pass = os.getenv("APP_DATABASE__PASSWORD", "postgres")
    # Note: seed_local_db uses 'postgres' db name by default for connection string?
    # Check if 'taskman' is used? Default env usually postgres.
    db_name = os.getenv("APP_DATABASE__DATABASE", "postgres")

    db_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    print(f"Connecting to: {db_url}")

    try:
        engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as connection:
            print("Adding 'title' column to 'projects' table...")
            connection.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS title VARCHAR(256)"))
            print("Schema patched successfully.")
    except Exception as e:
        print(f"Error patching schema: {e}")

if __name__ == "__main__":
    patch_schema()
