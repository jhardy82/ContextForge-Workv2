import sys
from pathlib import Path

# Add src and the project root to sys.path
backend_api_path = Path("c:/Users/James/Documents/Github/GHrepos/SCCMScripts/TaskMan-v2/backend-api")
src_path = backend_api_path / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(backend_api_path))

print(f"DEBUG: sys.path is {sys.path}")

try:
    from taskman_api.config import get_settings
    settings = get_settings()
    print(f"App Name: {settings.app_name}")
    print(f"Environment: {settings.environment}")
    print(f"Database Host: {settings.database.host}")
    print(f"Database Port: {settings.database.port}")
    print(f"Database Name: {settings.database.database}")

    # Try to connect
    import psycopg2
    pwd = settings.database.password.get_secret_value()
    print("Attempting to connect to PostgreSQL...")
    conn = psycopg2.connect(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=pwd,
        dbname=settings.database.database
    )
    print("Successfully connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
