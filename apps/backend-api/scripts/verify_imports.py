#!/usr/bin/env python
"""Verify all models, database layer, and repository imports."""

from dependencies import get_db_session
from models import ActionList, Project, Sprint, Task
from repositories import ProjectRepository, TaskRepository

print("All imports OK!")
print(f"Task columns: {list(Task.__table__.columns.keys())}")
print(f"Sprint columns: {list(Sprint.__table__.columns.keys())[:10]}...")
print(f"Project columns: {list(Project.__table__.columns.keys())[:10]}...")
print(f"ActionList columns: {list(ActionList.__table__.columns.keys())}")
print(f"Repositories: {TaskRepository.__name__}, {ProjectRepository.__name__}")
print(f"Dependencies: {get_db_session.__name__}")
