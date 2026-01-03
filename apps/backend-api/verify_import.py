import os
import sys

# Add src to pythonpath
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from taskman_api.models.project import Project
    print("Import successful. Project:", Project)
    from taskman_api.db.custom_types import JSONVariant
    print("JSONVariant imported:", JSONVariant)
except Exception:
    import traceback
    traceback.print_exc()
