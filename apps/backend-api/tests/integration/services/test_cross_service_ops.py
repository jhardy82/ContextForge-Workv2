import pytest
from datetime import date
from taskman_api.schemas.project import ProjectCreateRequest
from taskman_api.schemas.sprint import SprintCreateRequest
from taskman_api.schemas.task import TaskCreateRequest, TaskUpdateRequest
from taskman_api.core.enums import SprintCadence, Priority, TaskStatus

@pytest.mark.asyncio
async def test_full_workflow_simulation(project_service, sprint_service, task_service):
    """
    Simulate a full user workflow:
    1. Create Project
    2. Create Sprint
    3. Create Tasks
    4. Move incomplete tasks to next sprint
    """
    
    # 1. Create Project
    project_result = await project_service.create(ProjectCreateRequest(
        id="P-FULL-001",
        name="Full Workflow Project", 
        mission="Testing full workflow",
        start_date=date(2025, 1, 1),
        owner="tester"
    ))
    project = project_result.unwrap()
    
    # 2. Create Sprint 1
    sprint1_result = await sprint_service.create(SprintCreateRequest(
        id="S-FULL-001",
        name="Sprint 1", 
        goal="Initial Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14)
    ))
    sprint1 = sprint1_result.unwrap()
    
    # 3. Create Tasks
    task1_result = await task_service.create(TaskCreateRequest(
        id="T-FULL-001",
        title="Task 1",
        summary="Summary 1",
        description="Desc 1",
        owner="tester",
        priority=Priority.P2,
        primary_sprint=sprint1.id,
        primary_project=project.id
    ))
    task1 = task1_result.unwrap()
    
    task2_result = await task_service.create(TaskCreateRequest(
        id="T-FULL-002",
        title="Task 2",
        summary="Summary 2",
        description="Desc 2",
        owner="tester",
        priority=Priority.P2,
        primary_sprint=sprint1.id,
        primary_project=project.id
    ))
    task2 = task2_result.unwrap()
    
    # Complete Task 1
    await task_service.update(task1.id, TaskUpdateRequest(status=TaskStatus.DONE))
    
    # 4. Create Sprint 2
    sprint2_result = await sprint_service.create(SprintCreateRequest(
        id="S-FULL-002",
        name="Sprint 2", 
        goal="Next Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 1, 28)
    ))
    sprint2 = sprint2_result.unwrap()
    
    # Move incomplete Task 2 to Sprint 2
    await task_service.update(task2.id, TaskUpdateRequest(primary_sprint=sprint2.id))
    
    # Verify final state
    t1_result = await task_service.get(task1.id)
    t1 = t1_result.unwrap()
    
    t2_result = await task_service.get(task2.id)
    t2 = t2_result.unwrap()
    
    assert t1.status == TaskStatus.DONE
    assert t1.primary_sprint == sprint1.id
    
    assert t2.status == TaskStatus.NEW # Default
    assert t2.primary_sprint == sprint2.id
