import os
import sys
import traceback

print("--- DIAGNOSTIC START ---")
print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    # Add parent dir to path to find main.py
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    print(f"Added {parent_dir} to path.")

    print("Importing main...")
    from main import app

    print("Main imported SUCCESSFULLY.")

except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"STARTUP ERROR: {e}")
    traceback.print_exc()

print("--- DIAGNOSTIC END ---")
