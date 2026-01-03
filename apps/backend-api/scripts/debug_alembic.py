import os

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

# Load .env
load_dotenv(".env", override=True)

def log(msg):
    with open("alembic_debug.log", "a") as f:
        f.write(str(msg) + "\n")

def debug_alembic():
    with open("alembic_debug.log", "w") as f:
        f.write("Starting Alembic Debug...\n")

    alembic_cfg = Config("alembic.ini")

    # Force set sqlalchemy.url in config object just in case
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        sync_url = db_url.replace("+asyncpg", "")
        log(f"Using DB URL: {sync_url.split('@')[1] if '@' in sync_url else 'HIDDEN'}")
        alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    try:
        log("Running alembic upgrade head...")
        command.upgrade(alembic_cfg, "head")
        log("Upgrade complete.")

        log("Running alembic current...")
        command.current(alembic_cfg) # This prints to stdout usually, might miss it unless captured.
        # But exceptions will be caught.
    except Exception as e:
        log(f"Alembic failed: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    debug_alembic()
