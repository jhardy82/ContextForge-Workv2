import datetime
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Sync URL construction
url = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")

with open("alembic_diagnostic.log", "w", encoding="utf-8") as f:
    f.write(f"Diagnostic Run: {datetime.datetime.now()}\n")
    f.write(f"Connecting to: {url.split('@')[1] if '@' in url else 'INVALID_URL'}\n")

    try:
        conn = psycopg2.connect(url, sslmode="require")
        cur = conn.cursor()

        # Check tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [r[0] for r in cur.fetchall()]
        f.write(f"\nExisting Tables ({len(tables)}):\n")
        for t in sorted(tables):
            f.write(f" - {t}\n")

        # Check version
        if "alembic_version" in tables:
            cur.execute("SELECT version_num FROM alembic_version;")
            v = cur.fetchone()
            f.write(f"\nCurrent Alembic Version: {v[0] if v else 'None'}\n")
        else:
            f.write("\nNo alembic_version table found.\n")

        conn.close()
        f.write("\nSUCCESS: Connection closed.\n")

    except Exception as e:
        f.write(f"\n❌ FAILURE: {e}\n")
