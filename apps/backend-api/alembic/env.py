import os
import traceback
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool


# Debug logging
def log_debug(msg):
    with open("alembic_env_internal.log", "a") as f:
        f.write(str(msg) + "\n")


log_debug("env.py starting...")

# Explicitly load .env to ensure Settings/Env vars are populated
try:
    load_dotenv(override=True)
    log_debug(".env loaded with override=True")
except Exception as e:
    log_debug(f"Failed to load .env: {e}")
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import sys

from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
# Fix: .env is in the parent directory (backend-api), not in alembic/
dotenv_path = os.path.join(base_dir, "..", ".env")

with open("alembic_env_internal.log", "a") as f:
    f.write("env.py starting...\n")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
        f.write(f".env loaded from {dotenv_path} with override=True\n")
    else:
        f.write(f"WARNING: .env not found at {dotenv_path}\n")

    # Add src to path to allow importing models
    src_path = os.path.abspath(os.path.join(base_dir, "..", "src"))
    sys.path.insert(0, src_path)
    f.write(f"Added to path: {src_path}\n")

# Add src to pythonpath so we can import taskman_api
try:
    import taskman_api.models  # noqa: F401
    from taskman_api.db.base import Base

    log_debug("Models imported")
    target_metadata = Base.metadata
except Exception as e:
    log_debug(f"Import failed: {e}")
    log_debug(traceback.format_exc())
    raise


def get_url():
    """
    Get database URL from environment, ensuring sync driver for Windows migrations.
    Includes explicit variable fallback support for Cloud Pival setup.
    """
    # Try the new Pydantic-style variables first (most accurate)
    user = os.getenv("APP_DATABASE__USER")
    password = os.getenv("APP_DATABASE__PASSWORD")
    host = os.getenv("APP_DATABASE__HOST")
    port = os.getenv("APP_DATABASE__PORT", "5432")
    db_name = os.getenv("APP_DATABASE__DATABASE", "postgres")

    if user and password and host:
        # Construct sync URL manually
        # Note: passwords might need URL encoding if they contain special chars
        import urllib.parse

        encoded_pwd = urllib.parse.quote_plus(password)
        # Fix: Only require SSL for remote hosts, not local/127.0.0.1
        ssl_mode = "disable" if host in ["127.0.0.1", "localhost"] else "require"
        return f"postgresql://{user}:{encoded_pwd}@{host}:{port}/{db_name}?sslmode={ssl_mode}"

    # Fallback to DATABASE_URL if individual vars aren't set
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise ValueError("DATABASE_URL not found in environment!")

    # Force psycogp2 (sync) driver
    url = url.replace("postgresql+asyncpg://", "postgresql://")

    # Smarter SSL detection
    if "sslmode" not in url:
        is_local = "127.0.0.1" in url or "localhost" in url
        ssl_mode = "disable" if is_local else "require"
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}sslmode={ssl_mode}"

    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
