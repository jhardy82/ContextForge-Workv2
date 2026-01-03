"""Pytest fixtures for service layer tests.

Provides mock repositories and sample data for service testing.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

# Imports moved inside fixtures to prevent early loading for coverage
# from taskman_api.core.enums ...
# from taskman_api.models ...

# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_task() -> "Task":
    """Create sample task for testing.

    Note: acceptance_criteria and definition_of_done must be list[dict]
    to match TaskResponse schema expectations.
    """
    from taskman_api.core.enums import Priority, TaskStatus
    from taskman_api.models.task import Task

    return Task(
        id="T-TEST-001",
        title="Test Task",
        summary="Test task summary",
        description="Test task description",
        status=TaskStatus.NEW,
        owner="test.owner",
        assignees=["assignee1"],
        priority=Priority.P1,
        severity=None,
        primary_project="P-TEST-001",
        primary_sprint="S-TEST-001",
        related_projects=[],
        related_sprints=[],
        estimate_points=5.0,
        actual_time_hours=None,
        due_at=None,
        parents=[],
        depends_on=[],
        blocks=[],
        blockers=[],
        acceptance_criteria=[{"text": "Criterion 1", "completed": False}],
        definition_of_done=["DoD 1"],
        quality_gates={},
        verification={},
        actions_taken=[],
        labels=["test"],
        related_links=[],
        shape=None,
        stage=None,
        work_type=None,
        work_stream=None,
        business_value_score=8,
        cost_of_delay_score=6,
        automation_candidate=False,
        cycle_time_days=None,
        risks=[],
        observability={},

        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_project() -> "Project":
    """Create sample project for testing.

    Uses only fields that exist in the current Project model.
    """
    from taskman_api.core.enums import ProjectStatus
    from taskman_api.models.project import Project

    return Project(
        id="P-TEST-001",
        name="Test Project",
        mission="Test project mission",
        status=ProjectStatus.ACTIVE,
        start_date="2025-01-01",
        owner="project.owner",
        # JSON fields stored as text
        sponsors="[]",
        stakeholders="[]",
        repositories="[]",
        comms_channels="[]",
        okrs="[]",
        kpis="[]",
        roadmap="[]",
        risks="[]",
        assumptions="[]",
        constraints="[]",
        dependencies_external="[]",
        related_projects="[]",
        shared_components="[]",
        compliance_requirements="[]",
        governance="{}",
        success_metrics="[]",
        mpv_policy="{}",
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
    )


@pytest.fixture
def sample_sprint() -> "Sprint":
    """Create sample sprint for testing.

    Uses only fields that exist in the current Sprint model.
    """
    from taskman_api.core.enums import SprintStatus
    from taskman_api.models.sprint import Sprint

    return Sprint(
        id="S-TEST-001",
        name="Sprint 1",
        goal="Sprint goal",
        cadence="biweekly",
        start_date="2025-01-01",
        end_date="2025-01-14",
        status=SprintStatus.ACTIVE,
        owner="scrum.master",
        project_id="P-TEST-001",  # Use actual column name
        # JSON fields stored as text
        ceremonies="{}",
        risks="[]",
        dependencies="{}",
        related_projects="[]",
        # Velocity metrics
        committed_points="18",
        delivered_points="16",
        velocity_actual=0.8,
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
    )


@pytest.fixture
def sample_action_list() -> "ActionList":
    """Create sample action list for testing.

    Uses only fields that exist in the current ActionList model.
    ActionList uses 'name' not 'title'.
    """
    from taskman_api.models.action_list import ActionList

    return ActionList(
        id="AL-TEST-001",
        name="Test Action List",  # 'name' not 'title'
        description="Test description",
        status="active",
        task_ids=[],  # List of task IDs
    )


# ============================================================================
# Mock Repository Fixtures
# ============================================================================


@pytest.fixture
def mock_task_repository(mocker, sample_task):
    """Create mock TaskRepository for service tests.

    BaseRepository methods return entities directly (not wrapped in Result).
    Uses correct method names: get_by_id, get_all (not find_by_id, find_all).
    """
    mock_repo = mocker.Mock()

    # Mock create - returns entity directly
    mock_repo.create = AsyncMock(return_value=sample_task)

    # Mock get_by_id - returns entity or None
    mock_repo.get_by_id = AsyncMock(return_value=sample_task)

    # Mock get_all - returns list of entities
    mock_repo.get_all = AsyncMock(return_value=[sample_task])

    # Mock update - returns updated entity
    mock_repo.update = AsyncMock(return_value=sample_task)

    # Mock delete - returns None (void)
    mock_repo.delete = AsyncMock(return_value=None)

    # Mock exists - returns bool
    mock_repo.exists = AsyncMock(return_value=True)

    # Mock count - returns int
    mock_repo.count = AsyncMock(return_value=1)

    # Mock specialized methods (used by TaskRepository subclass)
    mock_repo.get_by_status = AsyncMock(return_value=[sample_task])
    mock_repo.get_by_priority = AsyncMock(return_value=[sample_task])
    mock_repo.get_by_owner = AsyncMock(return_value=[sample_task])
    mock_repo.get_by_project = AsyncMock(return_value=[sample_task])
    mock_repo.get_by_sprint = AsyncMock(return_value=[sample_task])
    mock_repo.search = AsyncMock(return_value=[sample_task])

    # Mock find_by methods (find_ prefix returns Ok-wrapped results for service layer)
    from taskman_api.core.result import Ok

    mock_repo.find_by_id = AsyncMock(return_value=Ok(sample_task))
    mock_repo.find_by_project = AsyncMock(return_value=Ok([sample_task]))
    mock_repo.find_by_sprint = AsyncMock(return_value=Ok([sample_task]))
    mock_repo.find_by_status = AsyncMock(return_value=Ok([sample_task]))
    mock_repo.find_by_priority = AsyncMock(return_value=Ok([sample_task]))

    return mock_repo


@pytest.fixture
def mock_project_repository(mocker, sample_project):
    """Create mock ProjectRepository for service tests.

    BaseRepository methods return entities directly (not wrapped in Result).
    """
    mock_repo = mocker.Mock()

    # Mock create - returns entity directly
    mock_repo.create = AsyncMock(return_value=sample_project)

    # Mock get_by_id - returns entity or None
    mock_repo.get_by_id = AsyncMock(return_value=sample_project)

    # Mock get_all - returns list of entities
    mock_repo.get_all = AsyncMock(return_value=[sample_project])

    # Mock update - returns updated entity
    mock_repo.update = AsyncMock(return_value=sample_project)

    # Mock delete - returns None (void)
    mock_repo.delete = AsyncMock(return_value=None)

    # Mock exists - returns bool
    mock_repo.exists = AsyncMock(return_value=True)

    # Mock count - returns int
    mock_repo.count = AsyncMock(return_value=1)

    # Mock specialized methods (get_ prefix returns entities directly)
    mock_repo.get_by_status = AsyncMock(return_value=[sample_project])
    mock_repo.get_by_owner = AsyncMock(return_value=[sample_project])
    mock_repo.search = AsyncMock(return_value=[sample_project])

    # Mock find_by methods (find_ prefix returns Ok-wrapped results for service layer)
    from taskman_api.core.result import Ok

    mock_repo.find_by_id = AsyncMock(return_value=Ok(sample_project))
    mock_repo.find_by_status = AsyncMock(return_value=Ok([sample_project]))
    mock_repo.find_by_owner = AsyncMock(return_value=Ok([sample_project]))
    mock_repo.find_by_project = AsyncMock(return_value=Ok([sample_project]))

    return mock_repo


@pytest.fixture
def mock_sprint_repository(mocker, sample_sprint):
    """Create mock SprintRepository for service tests.

    BaseRepository methods return entities directly (not wrapped in Result).
    """
    mock_repo = mocker.Mock()

    # Mock create - returns entity directly
    mock_repo.create = AsyncMock(return_value=sample_sprint)

    # Mock get_by_id - returns entity or None
    mock_repo.get_by_id = AsyncMock(return_value=sample_sprint)

    # Mock get_all - returns list of entities
    mock_repo.get_all = AsyncMock(return_value=[sample_sprint])

    # Mock update - returns updated entity
    mock_repo.update = AsyncMock(return_value=sample_sprint)

    # Mock delete - returns None (void)
    mock_repo.delete = AsyncMock(return_value=None)

    # Mock exists - returns bool
    mock_repo.exists = AsyncMock(return_value=True)

    # Mock count - returns int
    mock_repo.count = AsyncMock(return_value=1)

    # Mock specialized methods (get_ prefix returns entities directly)
    mock_repo.get_by_status = AsyncMock(return_value=[sample_sprint])
    mock_repo.get_by_project = AsyncMock(return_value=[sample_sprint])
    mock_repo.get_active_sprints = AsyncMock(return_value=[sample_sprint])
    mock_repo.search = AsyncMock(return_value=[sample_sprint])

    # Mock find_by methods (find_ prefix returns Ok-wrapped results for service layer)
    from taskman_api.core.result import Ok

    mock_repo.find_by_id = AsyncMock(return_value=Ok(sample_sprint))
    mock_repo.find_by_status = AsyncMock(return_value=Ok([sample_sprint]))
    mock_repo.find_by_project = AsyncMock(return_value=Ok([sample_sprint]))
    mock_repo.find_by_sprint = AsyncMock(return_value=Ok([sample_sprint]))
    mock_repo.find_current_sprints = AsyncMock(return_value=Ok([sample_sprint]))

    return mock_repo


@pytest.fixture
def mock_action_list_repository(mocker, sample_action_list):
    """Create mock ActionListRepository for service tests.

    BaseRepository methods return entities directly (not wrapped in Result).
    """
    mock_repo = mocker.Mock()

    # Mock create - returns entity directly
    mock_repo.create = AsyncMock(return_value=sample_action_list)

    # Mock get_by_id - returns entity or None
    mock_repo.get_by_id = AsyncMock(return_value=sample_action_list)

    # Mock get_all - returns list of entities
    mock_repo.get_all = AsyncMock(return_value=[sample_action_list])

    # Mock update - returns updated entity
    mock_repo.update = AsyncMock(return_value=sample_action_list)

    # Mock delete - returns None (void)
    mock_repo.delete = AsyncMock(return_value=None)

    # Mock exists - returns bool
    mock_repo.exists = AsyncMock(return_value=True)

    # Mock count - returns int
    mock_repo.count = AsyncMock(return_value=1)

    # Mock specialized methods
    mock_repo.get_by_project = AsyncMock(return_value=[sample_action_list])
    mock_repo.get_by_sprint = AsyncMock(return_value=[sample_action_list])
    mock_repo.search = AsyncMock(return_value=[sample_action_list])

    return mock_repo
