from datetime import date

import pytest

from taskman_api.core.enums import Priority, SprintCadence
from taskman_api.schemas.project import ProjectCreateRequest
from taskman_api.schemas.sprint import SprintCreateRequest
from taskman_api.schemas.task import TaskCreateRequest


@pytest.mark.asyncio
async def test_project_sprint_task_hierarchy(project_service, sprint_service, task_service):
    """Verify Project -> Sprint -> Task hierarchy creation and retrieval."""

    # 1. Create Project
    project_data = ProjectCreateRequest(
        id="P-INTEGRATION-001",
        name="Integration Project",
        mission="Testing hierarchy",
        start_date=date(2025, 1, 1),
        owner="tester",
    )
    project_result = await project_service.create(project_data)
    project = project_result.unwrap()
    assert project.id == "P-INTEGRATION-001"

    # 2. Create Sprint linked to Project
    sprint_data = SprintCreateRequest(
        id="S-INTEGRATION-001",
        name="Sprint 1",
        goal="First Sprint",
        cadence=SprintCadence.BIWEEKLY,
        primary_project=project.id,
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14),
    )
    sprint_result = await sprint_service.create(sprint_data)
    sprint = sprint_result.unwrap()
    assert sprint.id == "S-INTEGRATION-001"
    assert sprint.primary_project == project.id

    # 3. Create Task linked to Sprint
    task_data = TaskCreateRequest(
        id="T-INTEGRATION-001",
        title="Integration Task",
        summary="Test Summary",
        description="Test Description",
        owner="tester",
        priority=Priority.P2,
        primary_sprint=sprint.id,
        primary_project=project.id,
    )
    task_result = await task_service.create(task_data)
    task = task_result.unwrap()
    assert task.id == "T-INTEGRATION-001"
    assert task.primary_sprint == sprint.id
    assert task.primary_project == project.id

    # 4. Verification
    fetched_project_result = await project_service.get(project.id)
    fetched_project = fetched_project_result.unwrap()
    assert fetched_project.name == "Integration Project"

    fetched_sprint_result = await sprint_service.get(sprint.id)
    fetched_sprint = fetched_sprint_result.unwrap()
    assert fetched_sprint.primary_project == project.id

    fetched_task_result = await task_service.get(task.id)
    fetched_task = fetched_task_result.unwrap()
    assert fetched_task.primary_sprint == sprint.id
    assert fetched_task.primary_project == project.id

@pytest.mark.asyncio
async def test_orphan_prevention(sprint_service, task_service):
    """Verify that creating entities with invalid parent IDs fails."""

    sprint_data = SprintCreateRequest(
        id="S-ORPHAN-001",
        name="Orphan Sprint",
        goal="Should fail",
        cadence=SprintCadence.BIWEEKLY,
        primary_project="P-NON-EXISTENT",
        owner="tester",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 14),
    )

    # Assuming service returns Err or raises exception for invalid parent
    # If it returns Result, we check for is_err()
    result = await sprint_service.create(sprint_data)
    assert result.is_err() or result.is_ok() is False # Depending on implementation, might raise or return Err
