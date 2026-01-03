import os
import sys

import psycopg2

try:
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    print(f"DEBUG: Connecting to {db_host}:{db_port}...")

    conn = psycopg2.connect(
        host=db_host,
        database="postgres",
        user="postgres",
        password="postgres",
        port=db_port
    )
    print(f"SUCCESS: Connected to PostgreSQL on {db_host}:{db_port}")
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"FAILURE: Could not connect to {db_host}:{db_port}. Error: {e}")
    sys.exit(1)
