from datetime import date

import pytest

from taskman_api.core.enums import Priority, SprintCadence, TaskStatus
from taskman_api.core.errors import NotFoundError
from taskman_api.schemas.project import ProjectCreateRequest
from taskman_api.schemas.sprint import SprintCreateRequest
from taskman_api.schemas.task import TaskCreateRequest, TaskUpdateRequest


@pytest.mark.asyncio
async def test_create_task_with_invalid_project(task_service, sprint_service, project_service):
    """Test creating a task with a non-existent project ID."""
    # Create a valid project first to create a valid sprint
    project_result = await project_service.create(
        ProjectCreateRequest(
            id="P-VALID-001",
            name="Valid Project",
            mission="Mission",
            start_date=date(2025, 1, 1),
            owner="tester",
        )
    )
    project = project_result.unwrap()

    # Create a valid sprint
    sprint_result = await sprint_service.create(
        SprintCreateRequest(
            id="S-VALID-001",
            name="Valid Sprint",
            goal="Goal",
            cadence=SprintCadence.BIWEEKLY,
            primary_project=project.id,
            owner="tester",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 14),
        )
    )
    sprint = sprint_result.unwrap()

    task_data = TaskCreateRequest(
        id="T-INV-PROJ",
        title="Invalid Project Task",
        summary="Summary",
        description="Description",
        owner="tester",
        primary_project="NON-EXISTENT-PROJECT",
        primary_sprint=sprint.id,
        priority=Priority.P3,
    )

    result = await task_service.create(task_data)

    assert result.is_err()
    assert isinstance(result.unwrap_err(), NotFoundError)
    assert "Project" in str(result.unwrap_err())


@pytest.mark.asyncio
async def test_create_task_with_invalid_sprint(task_service, project_service):
    """Test creating a task with a non-existent sprint ID."""
    # Create a valid project
    project_result = await project_service.create(
        ProjectCreateRequest(
            id="P-VALID-002",
            name="Valid Project 2",
            mission="Mission",
            start_date=date(2025, 1, 1),
            owner="tester",
        )
    )
    project = project_result.unwrap()

    task_data = TaskCreateRequest(
        id="T-INV-SPRINT",
        title="Invalid Sprint Task",
        summary="Summary",
        description="Description",
        owner="tester",
        primary_project=project.id,
        primary_sprint="NON-EXISTENT-SPRINT",
        priority=Priority.P3,
    )

    result = await task_service.create(task_data)

    assert result.is_err()
    assert isinstance(result.unwrap_err(), NotFoundError)
    assert "Sprint" in str(result.unwrap_err())

@pytest.mark.asyncio
async def test_update_task_with_invalid_foreign_keys(task_service, project_service, sprint_service):
    """Test that updating a task with invalid project_id or sprint_id fails."""
    # Create a valid project
    project_result = await project_service.create(ProjectCreateRequest(
        id="P-VALID-003",
        name="Valid Project 3",
        mission="Mission",
        start_date=date(2025, 1, 1),
        owner="tester"
    ))
    project = project_result.unwrap()

    # Create a valid sprint
    sprint_result = await sprint_service.create(SprintCreateRequest(
        id="S-VALID-003",
        name="Valid Sprint 3",
        goal="Goal",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14)
    ))
    sprint = sprint_result.unwrap()

    # Create a valid task
    task_data = TaskCreateRequest(
        id="T-UPDATE-TEST",
        title="Task to Update",
        summary="Summary",
        description="This task will be updated",
        owner="tester",
        primary_project=project.id,
        primary_sprint=sprint.id,
        priority=Priority.P3,
        status=TaskStatus.NEW,
    )
    result = await task_service.create(task_data)
    assert result.is_ok()
    task = result.unwrap()

    # Try to update with invalid project_id
    update_data_project = TaskUpdateRequest(primary_project="NON-EXISTENT-PROJECT")
    result_project = await task_service.update(task.id, update_data_project)
    assert result_project.is_err()
    assert isinstance(result_project.unwrap_err(), NotFoundError)
    assert "Project" in str(result_project.unwrap_err())

    # Try to update with invalid sprint_id
    update_data_sprint = TaskUpdateRequest(primary_sprint="NON-EXISTENT-SPRINT")
    result_sprint = await task_service.update(task.id, update_data_sprint)
    assert result_sprint.is_err()
    assert isinstance(result_sprint.unwrap_err(), NotFoundError)
    assert "Sprint" in str(result_sprint.unwrap_err())
