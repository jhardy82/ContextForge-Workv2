import os
import sys

print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"CWD: {os.getcwd()}")
sys.stdout.flush()

try:
    print("Attempting import...", flush=True)
    import cf_core

    print(f"cf_core found at: {cf_core.__file__}", flush=True)
    from taskman_api.dependencies import get_db_session

    print("Import Successful", flush=True)
except ImportError as e:
    print(f"Import Failed: {e}", file=sys.stderr, flush=True)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr, flush=True)
