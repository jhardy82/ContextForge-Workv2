import json
import os
import sys
import traceback

# Force stdout/stderr to be unbuffered
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("Starting script...", file=sys.stderr)

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
print("Path configured.", file=sys.stderr)

try:
    print("Importing main...", file=sys.stderr)
    from taskman_api.main import app

    print("Exporting openapi...", file=sys.stderr)
    json_str = json.dumps(app.openapi(), indent=2)
    print(json_str)  # To stdout
    print("Done.", file=sys.stderr)
except Exception:
    traceback.print_exc()
    sys.exit(1)
