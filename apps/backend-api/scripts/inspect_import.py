import inspect
import os
import sys

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models import task
    from models.task import Task

    print(f"Task module file: {task.__file__}")
    print(f"Task class defined in: {inspect.getfile(Task)}")
    print(f"Task class columns: {[c.name for c in Task.__table__.columns]}")

except Exception as e:
    print(f"ERROR: {e}")
