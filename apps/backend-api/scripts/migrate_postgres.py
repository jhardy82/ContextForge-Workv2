import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def write_log(message, log_file):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}\n"
    print(message)
    with open(log_file, "a") as f:
        f.write(line)


def run_migration():
    log_file = "migrate_postgres.log"
    backend_api_path = Path(__file__).parent.parent

    # Setup environment
    env = os.environ.copy()
    # Explicitly remove polluted DATABASE_URL to force reconstruction from components
    if "DATABASE_URL" in env:
        del env["DATABASE_URL"]

    env["APP_DATABASE__HOST"] = "127.0.0.1"
    env["APP_DATABASE__PORT"] = "5434"
    env["APP_DATABASE__USER"] = "contextforge"
    env["APP_DATABASE__PASSWORD"] = "contextforge"
    env["APP_DATABASE__DATABASE"] = "taskman_v2"
    env["APP_SECRET_KEY"] = "taskman-development-secret-key-32char"
    env["APP_JWT_SECRET"] = "taskman-development-jwt-key-32-chars"
    env["PYTHONPATH"] = f"src;{backend_api_path.parent}"

    write_log("--- Starting Alembic Migration ---", log_file)

    try:
        # Run Alembic upgrade head
        cmd = [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"]
        write_log(f"Running command: {' '.join(cmd)}", log_file)

        process = subprocess.Popen(
            cmd,
            cwd=backend_api_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()

        if stdout:
            write_log("--- STDOUT ---", log_file)
            write_log(stdout, log_file)
        if stderr:
            write_log("--- STDERR ---", log_file)
            write_log(stderr, log_file)

        if process.returncode == 0:
            write_log("Migration SUCCESSFUL.", log_file)
            return True
        else:
            write_log(f"Migration FAILED with code {process.returncode}.", log_file)
            return False

    except Exception as e:
        write_log(f"CRITICAL ERROR: {str(e)}", log_file)
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
