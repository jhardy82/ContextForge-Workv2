import os
import sys

print(f"Current Working Directory: {os.getcwd()}")
print("Python Path (sys.path):")
for path in sys.path:
    print(f"  - {path}")

try:
    import cf_core
    print("SUCCESS: cf_core imported successfully")
    print(f"cf_core file: {cf_core.__file__}")
except ImportError as e:
    print(f"FAILURE: Could not import cf_core. Error: {e}")

try:
    from taskman_api.core import result
    print("SUCCESS: taskman_api.core.result imported successfully")
except ImportError as e:
    print(f"FAILURE: Could not import taskman_api.core.result. Error: {e}")
