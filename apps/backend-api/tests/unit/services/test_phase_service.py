"""Unit tests for PhaseService.

Tests phase tracking operations for Tasks, Sprints, and Projects.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taskman_api.core.enums import PhaseStatus
from taskman_api.core.errors import NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.services.phase_service import (
    TASK_PHASES,
    SPRINT_PHASES,
    PROJECT_PHASES,
    PhaseService,
)


@pytest.fixture
def mock_session():
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def phase_service(mock_session):
    """Create PhaseService with mocked repositories."""
    with patch("taskman_api.services.phase_service.TaskRepository") as mock_task_repo, \
         patch("taskman_api.services.phase_service.SprintRepository") as mock_sprint_repo, \
         patch("taskman_api.services.phase_service.ProjectRepository") as mock_project_repo:

        # Create mock repository instances
        mock_task_repo.return_value = AsyncMock()
        mock_sprint_repo.return_value = AsyncMock()
        mock_project_repo.return_value = AsyncMock()

        service = PhaseService(mock_session)
        service.task_repo = mock_task_repo.return_value
        service.sprint_repo = mock_sprint_repo.return_value
        service.project_repo = mock_project_repo.return_value

        yield service


class TestPhaseConstants:
    """Test phase constants are correct."""

    def test_task_phases(self):
        """Test task has 4 phases."""
        assert TASK_PHASES == ["research", "planning", "implementation", "testing"]
        assert len(TASK_PHASES) == 4

    def test_sprint_phases(self):
        """Test sprint has 2 phases."""
        assert SPRINT_PHASES == ["planning", "implementation"]
        assert len(SPRINT_PHASES) == 2

    def test_project_phases(self):
        """Test project has 2 phases."""
        assert PROJECT_PHASES == ["research", "planning"]
        assert len(PROJECT_PHASES) == 2


class TestGetValidPhases:
    """Test getting valid phases for entity types."""

    def test_get_valid_phases_task(self, phase_service):
        """Test getting valid phases for task."""
        phases = phase_service._get_valid_phases("task")
        assert phases == ["research", "planning", "implementation", "testing"]

    def test_get_valid_phases_sprint(self, phase_service):
        """Test getting valid phases for sprint."""
        phases = phase_service._get_valid_phases("sprint")
        assert phases == ["planning", "implementation"]

    def test_get_valid_phases_project(self, phase_service):
        """Test getting valid phases for project."""
        phases = phase_service._get_valid_phases("project")
        assert phases == ["research", "planning"]


class TestGetPhases:
    """Test getting phases for an entity."""

    @pytest.mark.asyncio
    async def test_get_phases_success(self, phase_service):
        """Test successful phase retrieval."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "in_progress", "has_research": True},
            "planning": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.get_phases("T-001", "task")

        assert isinstance(result, Ok)
        assert result.value["research"]["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_get_phases_not_found(self, phase_service):
        """Test phase retrieval for non-existent entity."""
        phase_service.task_repo.find_by_id.return_value = Err(
            NotFoundError("Task not found", entity_type="task", entity_id="T-999")
        )

        result = await phase_service.get_phases("T-999", "task")

        assert isinstance(result, Err)
        assert isinstance(result.error, NotFoundError)


class TestGetPhaseStatus:
    """Test getting status of a specific phase."""

    @pytest.mark.asyncio
    async def test_get_phase_status_success(self, phase_service):
        """Test successful phase status retrieval."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "in_progress"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.get_phase_status("T-001", "task", "research")

        assert isinstance(result, Ok)
        assert result.value == PhaseStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_phase_status_invalid_phase(self, phase_service):
        """Test invalid phase name for entity type."""
        result = await phase_service.get_phase_status("T-001", "task", "invalid_phase")

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)
        assert "Invalid phase" in result.error.message

    @pytest.mark.asyncio
    async def test_get_phase_status_sprint_invalid_phase(self, phase_service):
        """Test sprint rejects task-only phases."""
        result = await phase_service.get_phase_status("S-001", "sprint", "testing")

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)


class TestUpdatePhase:
    """Test updating phase data."""

    @pytest.mark.asyncio
    async def test_update_phase_success(self, phase_service):
        """Test successful phase update."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "not_started", "has_research": False},
            "planning": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "research": {"status": "in_progress", "has_research": True},
            "planning": {"status": "not_started"},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.update_phase(
            "T-001", "task", "research",
            {"status": "in_progress", "has_research": True}
        )

        assert isinstance(result, Ok)
        assert result.value["status"] == "in_progress"
        assert result.value["has_research"] is True

    @pytest.mark.asyncio
    async def test_update_phase_invalid_phase(self, phase_service):
        """Test updating invalid phase name."""
        result = await phase_service.update_phase(
            "T-001", "task", "invalid",
            {"status": "in_progress"}
        )

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)


class TestSetPhaseStatus:
    """Test setting phase status with validation."""

    @pytest.mark.asyncio
    async def test_set_phase_status_valid_transition(self, phase_service):
        """Test valid phase status transition."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "research": {"status": "in_progress"},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.set_phase_status(
            "T-001", "task", "research", PhaseStatus.IN_PROGRESS
        )

        assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_set_phase_status_invalid_transition(self, phase_service):
        """Test invalid phase status transition."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "completed"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        # COMPLETED is terminal, can't transition to IN_PROGRESS
        result = await phase_service.set_phase_status(
            "T-001", "task", "research", PhaseStatus.IN_PROGRESS
        )

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)
        assert "Invalid phase transition" in result.error.message


class TestPhaseTransitionValidation:
    """Test phase transition validation rules."""

    def test_valid_transitions_from_not_started(self, phase_service):
        """Test valid transitions from NOT_STARTED."""
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.NOT_STARTED, PhaseStatus.IN_PROGRESS
        )
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.NOT_STARTED, PhaseStatus.SKIPPED
        )

    def test_invalid_transitions_from_not_started(self, phase_service):
        """Test invalid transitions from NOT_STARTED."""
        assert not phase_service._is_valid_phase_transition(
            PhaseStatus.NOT_STARTED, PhaseStatus.COMPLETED
        )
        assert not phase_service._is_valid_phase_transition(
            PhaseStatus.NOT_STARTED, PhaseStatus.BLOCKED
        )

    def test_valid_transitions_from_in_progress(self, phase_service):
        """Test valid transitions from IN_PROGRESS."""
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.IN_PROGRESS, PhaseStatus.COMPLETED
        )
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.IN_PROGRESS, PhaseStatus.BLOCKED
        )
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.IN_PROGRESS, PhaseStatus.SKIPPED
        )

    def test_valid_transitions_from_blocked(self, phase_service):
        """Test valid transitions from BLOCKED."""
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.BLOCKED, PhaseStatus.IN_PROGRESS
        )
        assert phase_service._is_valid_phase_transition(
            PhaseStatus.BLOCKED, PhaseStatus.SKIPPED
        )

    def test_no_transitions_from_completed(self, phase_service):
        """Test COMPLETED is terminal."""
        assert not phase_service._is_valid_phase_transition(
            PhaseStatus.COMPLETED, PhaseStatus.IN_PROGRESS
        )
        assert not phase_service._is_valid_phase_transition(
            PhaseStatus.COMPLETED, PhaseStatus.BLOCKED
        )

    def test_no_transitions_from_skipped(self, phase_service):
        """Test SKIPPED is terminal."""
        assert not phase_service._is_valid_phase_transition(
            PhaseStatus.SKIPPED, PhaseStatus.IN_PROGRESS
        )


class TestAdvancePhase:
    """Test advancing to next phase."""

    @pytest.mark.asyncio
    async def test_advance_phase_start_first_phase(self, phase_service):
        """Test starting first phase when all are not_started."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "not_started"},
            "planning": {"status": "not_started"},
            "implementation": {"status": "not_started"},
            "testing": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "research": {"status": "in_progress"},
            "planning": {"status": "not_started"},
            "implementation": {"status": "not_started"},
            "testing": {"status": "not_started"},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.advance_phase("T-001", "task")

        assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_advance_phase_no_phases_to_advance(self, phase_service):
        """Test error when all phases are complete."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "completed"},
            "implementation": {"status": "completed"},
            "testing": {"status": "completed"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.advance_phase("T-001", "task")

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)
        assert "No phases available" in result.error.message


class TestBlockUnblockPhase:
    """Test blocking and unblocking phases."""

    @pytest.mark.asyncio
    async def test_block_phase_with_reason(self, phase_service):
        """Test blocking a phase with reason."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "implementation": {"status": "in_progress"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "implementation": {"status": "blocked", "blocked_reason": "Waiting for API"},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.block_phase(
            "T-001", "task", "implementation",
            "Waiting for API"
        )

        assert isinstance(result, Ok)

    @pytest.mark.asyncio
    async def test_unblock_phase(self, phase_service):
        """Test unblocking a phase."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "implementation": {"status": "blocked", "blocked_reason": "Waiting"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "implementation": {"status": "in_progress", "blocked_reason": None},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.unblock_phase("T-001", "task", "implementation")

        assert isinstance(result, Ok)


class TestSkipPhase:
    """Test skipping phases."""

    @pytest.mark.asyncio
    async def test_skip_phase_with_reason(self, phase_service):
        """Test skipping a phase with reason."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        updated_entity = MagicMock()
        updated_entity.phases = {
            "research": {"status": "skipped", "skip_reason": "Done in parent"},
        }
        phase_service.task_repo.update.return_value = Ok(updated_entity)

        result = await phase_service.skip_phase(
            "T-001", "task", "research",
            "Done in parent"
        )

        assert isinstance(result, Ok)


class TestGetPhaseSummary:
    """Test getting phase summary."""

    @pytest.mark.asyncio
    async def test_get_phase_summary_all_complete(self, phase_service):
        """Test summary when all phases complete."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "completed"},
            "implementation": {"status": "completed"},
            "testing": {"status": "completed"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.get_phase_summary("T-001", "task")

        assert isinstance(result, Ok)
        summary = result.value
        assert summary["entity_id"] == "T-001"
        assert summary["entity_type"] == "task"
        assert summary["phases_completed"] == 4
        assert summary["phases_total"] == 4
        assert summary["completion_pct"] == 100.0
        assert summary["current_phase"] is None

    @pytest.mark.asyncio
    async def test_get_phase_summary_in_progress(self, phase_service):
        """Test summary with current phase in progress."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "in_progress"},
            "implementation": {"status": "not_started"},
            "testing": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.get_phase_summary("T-001", "task")

        assert isinstance(result, Ok)
        summary = result.value
        assert summary["current_phase"] == "planning"
        assert summary["phases_completed"] == 1
        assert summary["completion_pct"] == 25.0

    @pytest.mark.asyncio
    async def test_get_phase_summary_skipped_counts_as_done(self, phase_service):
        """Test that skipped phases count as completed."""
        mock_entity = MagicMock()
        mock_entity.phases = {
            "research": {"status": "skipped"},
            "planning": {"status": "completed"},
            "implementation": {"status": "not_started"},
            "testing": {"status": "not_started"},
        }
        phase_service.task_repo.find_by_id.return_value = Ok(mock_entity)

        result = await phase_service.get_phase_summary("T-001", "task")

        assert isinstance(result, Ok)
        summary = result.value
        assert summary["phases_completed"] == 2  # skipped + completed


class TestFindEntitiesInPhase:
    """Test finding entities in a specific phase."""

    @pytest.mark.asyncio
    async def test_find_entities_in_phase_success(self, phase_service):
        """Test finding entities in a specific phase."""
        mock_entity1 = MagicMock()
        mock_entity1.id = "T-001"
        mock_entity1.phases = {
            "implementation": {"status": "blocked", "blocked_reason": "Waiting"},
        }

        mock_entity2 = MagicMock()
        mock_entity2.id = "T-002"
        mock_entity2.phases = {
            "implementation": {"status": "in_progress"},
        }

        phase_service.task_repo.find_all.return_value = Ok([mock_entity1, mock_entity2])

        result = await phase_service.find_entities_in_phase(
            "task", "implementation", PhaseStatus.BLOCKED
        )

        assert isinstance(result, Ok)
        assert len(result.value) == 1
        assert result.value[0]["id"] == "T-001"

    @pytest.mark.asyncio
    async def test_find_entities_in_phase_invalid_phase(self, phase_service):
        """Test finding entities with invalid phase."""
        result = await phase_service.find_entities_in_phase(
            "task", "invalid_phase"
        )

        assert isinstance(result, Err)
        assert isinstance(result.error, ValidationError)


class TestFindBlockedEntities:
    """Test finding all blocked entities."""

    @pytest.mark.asyncio
    async def test_find_blocked_entities_single_type(self, phase_service):
        """Test finding blocked entities of one type."""
        mock_entity = MagicMock()
        mock_entity.id = "T-001"
        mock_entity.phases = {
            "implementation": {"status": "blocked", "blocked_reason": "Waiting"},
        }

        phase_service.task_repo.find_all.return_value = Ok([mock_entity])

        result = await phase_service.find_blocked_entities("task")

        assert isinstance(result, Ok)
        assert len(result.value) == 1
        assert result.value[0]["entity_id"] == "T-001"
        assert result.value[0]["phase"] == "implementation"
        assert result.value[0]["blocked_reason"] == "Waiting"

    @pytest.mark.asyncio
    async def test_find_blocked_entities_all_types(self, phase_service):
        """Test finding blocked entities across all types."""
        mock_task = MagicMock()
        mock_task.id = "T-001"
        mock_task.phases = {"implementation": {"status": "blocked"}}

        mock_sprint = MagicMock()
        mock_sprint.id = "S-001"
        mock_sprint.phases = {"planning": {"status": "blocked"}}

        mock_project = MagicMock()
        mock_project.id = "P-001"
        mock_project.phases = {"research": {"status": "in_progress"}}

        phase_service.task_repo.find_all.return_value = Ok([mock_task])
        phase_service.sprint_repo.find_all.return_value = Ok([mock_sprint])
        phase_service.project_repo.find_all.return_value = Ok([mock_project])

        result = await phase_service.find_blocked_entities()

        assert isinstance(result, Ok)
        assert len(result.value) == 2  # Task and Sprint blocked, not Project
