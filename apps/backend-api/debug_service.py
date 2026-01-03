import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.models.task import Task
from taskman_api.schemas.task import TaskCreateRequest, TaskResponse
from taskman_api.services.base import BaseService

sample_task = Task(
    id='T-TEST-001',
    title='Test Task',
    summary='Test task summary',
    description='Test task description',
    status=TaskStatus.NEW,
    owner='test.owner',
    assignees=['assignee1'],
    priority=Priority.P1,
    primary_project='P-TEST-001',
    primary_sprint='S-TEST-001',
    related_projects=[],
    related_sprints=[],
    estimate_points=5.0,
    actual_time_hours=None,
    due_at=None,
    parents=[],
    depends_on=[],
    blocks=[],
    blockers=[],
    acceptance_criteria=[{'text': 'Criterion 1', 'completed': False}],
    definition_of_done=['DoD 1'],
    quality_gates={},
    verification={},
    actions_taken=[],
    labels=['test'],
    related_links=[],
    created_at=datetime(2025, 1, 1, 12, 0, 0),
    updated_at=datetime(2025, 1, 1, 12, 0, 0),
)

mock_repo = Mock()
mock_repo.create = AsyncMock(return_value=sample_task)

service = BaseService(mock_repo, Task, TaskResponse)
request = TaskCreateRequest(
    id='T-TEST-001',
    title='Test Task',
    summary='Summary',
    description='Description',
    owner='test.owner',
    priority=Priority.P1,
    primary_project='P-TEST-001',
    primary_sprint='S-TEST-001',
)

async def test():
    result = await service.create(request)
    print(f'Result type: {type(result).__name__}')
    if hasattr(result, 'err'):
        err = result.err()
        if err:
            print(f'Error message: {err.message}')
    if hasattr(result, 'ok'):
        ok = result.ok()
        if ok:
            print(f'Success: {ok}')

asyncio.run(test())
