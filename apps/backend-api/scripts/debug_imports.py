import os
import sys

print("Starting debug script...")
with open("debug_out.txt", "w") as f:
    f.write("Starting debug script...\n")
    try:
        # Add src to pythonpath
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
        f.write(f"Adding to path: {src_path}\n")
        sys.path.append(src_path)

        try:
            import structlog
            f.write("Successfully imported structlog\n")
        except ImportError as e:
            f.write(f"Failed to import structlog: {e}\n")

        try:
            import sqlalchemy
            f.write(f"Successfully imported sqlalchemy: {sqlalchemy.__version__}\n")
        except ImportError as e:
            f.write(f"Failed to import sqlalchemy: {e}\n")

        import taskman_api
        f.write(f"Successfully imported taskman_api from {taskman_api.__file__}\n")

        f.write("Successfully imported manager\n")

    except Exception as e:
        f.write(f"ERROR: {e}\n")
        import traceback
        traceback.print_exc(file=f)

print("Debug script finished.")
