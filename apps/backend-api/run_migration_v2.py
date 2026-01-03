import os
import subprocess
import sys
from pathlib import Path

# Setup environment
backend_api_path = Path("c:/Users/James/Documents/Github/GHrepos/SCCMScripts/TaskMan-v2/backend-api")
os.environ["APP_DATABASE__HOST"] = "localhost"
os.environ["APP_DATABASE__PORT"] = "5434"
os.environ["APP_DATABASE__USER"] = "contextforge"
os.environ["APP_DATABASE__PASSWORD"] = "contextforge"
os.environ["APP_DATABASE__DATABASE"] = "taskman_v2"
os.environ["APP_SECRET_KEY"] = "taskman-development-secret-key-32char"
os.environ["APP_JWT_SECRET"] = "taskman-development-jwt-key-32-chars"
os.environ["PYTHONPATH"] = f"src;{backend_api_path.parent.parent}"

output_file = backend_api_path / "migration_out_v3.txt"

print(f"DEBUG: Starting Alembic migration. Output will be written to {output_file}")

with open(output_file, "w") as f:
    try:
        # Run Alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "alembic_ini.txt", "upgrade", "head"],
            cwd=backend_api_path,
            capture_output=True,
            text=True,
            check=True
        )
        f.write("--- STDOUT ---\n")
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
        print("Migration completed successfully.")
    except subprocess.CalledProcessError as e:
        f.write("--- ERROR ---\n")
        f.write(f"Exit Code: {e.returncode}\n")
        f.write("--- STDOUT ---\n")
        f.write(e.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(e.stderr)
        print(f"Migration failed with exit code {e.returncode}")
    except Exception as e:
        f.write(f"CRITICAL ERROR: {e}\n")
        print(f"An unexpected error occurred: {e}")
