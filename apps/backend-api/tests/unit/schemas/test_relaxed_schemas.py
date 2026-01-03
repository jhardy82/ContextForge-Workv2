from taskman_api.core.enums import ProjectStatus, SprintCadence, SprintStatus, TaskStatus
from taskman_api.schemas.project import ProjectCreate
from taskman_api.schemas.sprint import SprintCreate
from taskman_api.schemas.task import TaskCreate


def test_create_task_backlog_support():
    """Verify creating a task without a primary sprint (Backlog)."""
    task_data = {
        "id": "T-BACKLOG-001",
        "title": "Backlog Task",
        "summary": "Task for backlog",
        # description is now optional
        "status": TaskStatus.NEW,
        "owner": "user",
        "primary_project": "P-001",
        # primary_sprint is now optional
    }
    task = TaskCreate(**task_data)
    assert task.primary_sprint is None
    assert task.description is None

def test_create_project_draft_support():
    """Verify creating a project without mission or start_date (Draft)."""
    project_data = {
        "id": "P-DRAFT-001",
        "name": "Draft Project",
        # mission is now optional
        "status": ProjectStatus.NEW,
        # start_date is now optional
        "owner": "admin",
    }
    project = ProjectCreate(**project_data)
    assert project.mission is None
    assert project.start_date is None

def test_create_sprint_draft_support():
    """Verify creating a sprint without goal or dates (Draft)."""
    sprint_data = {
        "id": "S-DRAFT-001",
        "name": "Draft Sprint",
        # goal is now optional
        "cadence": SprintCadence.BIWEEKLY,
        # start_date, end_date are optional
        "status": SprintStatus.NEW,
        "owner": "scrum_master",
        "primary_project": "P-001",
    }
    sprint = SprintCreate(**sprint_data)
    assert sprint.goal is None
    assert sprint.start_date is None
    assert sprint.end_date is None
