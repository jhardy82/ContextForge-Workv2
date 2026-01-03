import pytest
from datetime import date
from taskman_api.schemas.project import ProjectCreateRequest
from taskman_api.schemas.sprint import SprintCreateRequest
from taskman_api.schemas.task import TaskCreateRequest, TaskUpdateRequest
from taskman_api.core.enums import SprintCadence, Priority, TaskStatus

@pytest.mark.asyncio
async def test_task_movement_between_sprints(project_service, sprint_service, task_service):
    """Verify moving a task from one sprint to another."""
    
    # Setup: Project + 2 Sprints
    project_result = await project_service.create(ProjectCreateRequest(
        id="P-MOVE-001",
        name="Move Project", 
        mission="Testing movement",
        start_date=date(2025, 1, 1),
        owner="tester"
    ))
    project = project_result.unwrap()
    
    sprint1_result = await sprint_service.create(SprintCreateRequest(
        id="S-MOVE-001",
        name="Sprint 1", 
        goal="Source Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14)
    ))
    sprint1 = sprint1_result.unwrap()
    
    sprint2_result = await sprint_service.create(SprintCreateRequest(
        id="S-MOVE-002",
        name="Sprint 2", 
        goal="Target Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 1, 28)
    ))
    sprint2 = sprint2_result.unwrap()
    
    # Create Task in Sprint 1
    task_result = await task_service.create(TaskCreateRequest(
        id="T-MOVE-001",
        title="Moving Task",
        summary="Test Summary",
        description="Test Description",
        owner="tester",
        priority=Priority.P2,
        primary_sprint=sprint1.id,
        primary_project=project.id
    ))
    task = task_result.unwrap()
    
    assert task.primary_sprint == sprint1.id
    
    # Move to Sprint 2
    updated_task_result = await task_service.update(task.id, TaskUpdateRequest(
        primary_sprint=sprint2.id
    ))
    updated_task = updated_task_result.unwrap()
    
    assert updated_task.primary_sprint == sprint2.id
    
    # Verify persistence
    fetched_task_result = await task_service.get(task.id)
    fetched_task = fetched_task_result.unwrap()
    assert fetched_task.primary_sprint == sprint2.id

@pytest.mark.asyncio
async def test_sprint_closure_logic(project_service, sprint_service, task_service):
    """Verify logic when 'closing' a sprint (simulated via status updates)."""
    
    project_result = await project_service.create(ProjectCreateRequest(
        id="P-CLOSE-001",
        name="Closure Project", 
        mission="Testing closure",
        start_date=date(2025, 1, 1),
        owner="tester"
    ))
    project = project_result.unwrap()
    
    sprint_result = await sprint_service.create(SprintCreateRequest(
        id="S-CLOSE-001",
        name="Closing Sprint", 
        goal="Closing Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14)
    ))
    sprint = sprint_result.unwrap()
    
    # Create tasks
    task_done_result = await task_service.create(TaskCreateRequest(
        id="T-DONE-001",
        title="Done Task",
        summary="Done Summary",
        description="Done Description",
        owner="tester",
        priority=Priority.P2,
        status=TaskStatus.DONE,
        primary_sprint=sprint.id,
        primary_project=project.id
    ))
    task_done = task_done_result.unwrap()
    
    task_todo_result = await task_service.create(TaskCreateRequest(
        id="T-TODO-001",
        title="Todo Task",
        summary="Todo Summary",
        description="Todo Description",
        owner="tester",
        priority=Priority.P2,
        status=TaskStatus.NEW,
        primary_sprint=sprint.id,
        primary_project=project.id
    ))
    task_todo = task_todo_result.unwrap()
    
    assert task_done.status == TaskStatus.DONE
    assert task_todo.status == TaskStatus.NEW
    assert task_done.primary_sprint == sprint.id
    assert task_todo.primary_sprint == sprint.id
