"""Unit tests for Phase API endpoints.

Tests phase tracking API endpoints for Tasks, Sprints, and Projects.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taskman_api.core.enums import PhaseStatus
from taskman_api.core.errors import NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.phase import (
    BlockedEntityResponse,
    BlockPhaseRequest,
    EntityInPhaseResponse,
    PhaseAnalyticsResponse,
    PhasesResponse,
    PhaseSummaryResponse,
    PhaseUpdateRequest,
    SkipPhaseRequest,
)


@pytest.fixture
def mock_phase_service():
    """Create mock PhaseService."""
    return AsyncMock()


class TestPhasesSchemas:
    """Test phase request/response schemas."""

    def test_phase_update_request_defaults(self):
        """Test PhaseUpdateRequest with default values."""
        request = PhaseUpdateRequest()
        assert request.status is None
        assert request.blocked_reason is None
        assert request.skip_reason is None
        assert request.additional_fields is None

    def test_phase_update_request_with_status(self):
        """Test PhaseUpdateRequest with status."""
        request = PhaseUpdateRequest(status=PhaseStatus.IN_PROGRESS)
        assert request.status == PhaseStatus.IN_PROGRESS

    def test_phase_update_request_with_blocked_reason(self):
        """Test PhaseUpdateRequest with blocked reason."""
        request = PhaseUpdateRequest(
            status=PhaseStatus.BLOCKED,
            blocked_reason="Waiting for API"
        )
        assert request.status == PhaseStatus.BLOCKED
        assert request.blocked_reason == "Waiting for API"

    def test_block_phase_request(self):
        """Test BlockPhaseRequest schema."""
        request = BlockPhaseRequest(blocked_reason="External dependency")
        assert request.blocked_reason == "External dependency"

    def test_skip_phase_request(self):
        """Test SkipPhaseRequest schema."""
        request = SkipPhaseRequest(skip_reason="Already done in parent")
        assert request.skip_reason == "Already done in parent"

    def test_phases_response(self):
        """Test PhasesResponse schema."""
        response = PhasesResponse(
            entity_id="T-001",
            entity_type="task",
            phases={
                "research": {"status": "in_progress"},
                "planning": {"status": "not_started"},
            }
        )
        assert response.entity_id == "T-001"
        assert response.entity_type == "task"
        assert "research" in response.phases

    def test_phase_summary_response(self):
        """Test PhaseSummaryResponse schema."""
        response = PhaseSummaryResponse(
            entity_id="T-001",
            entity_type="task",
            current_phase="planning",
            phases_completed=1,
            phases_total=4,
            completion_pct=25.0,
            phases={"research": {"status": "completed"}}
        )
        assert response.completion_pct == 25.0
        assert response.current_phase == "planning"

    def test_entity_in_phase_response(self):
        """Test EntityInPhaseResponse schema."""
        response = EntityInPhaseResponse(
            id="T-001",
            phase="implementation",
            status="blocked",
            phase_data={"blocked_reason": "Waiting"}
        )
        assert response.id == "T-001"
        assert response.phase == "implementation"

    def test_blocked_entity_response(self):
        """Test BlockedEntityResponse schema."""
        response = BlockedEntityResponse(
            entity_type="task",
            entity_id="T-001",
            phase="implementation",
            blocked_reason="Waiting for API"
        )
        assert response.entity_type == "task"
        assert response.blocked_reason == "Waiting for API"

    def test_phase_analytics_response(self):
        """Test PhaseAnalyticsResponse schema."""
        response = PhaseAnalyticsResponse(
            entity_type="task",
            total_entities=10,
            by_phase={
                "research": {"not_started": 5, "in_progress": 3, "completed": 2},
            },
            blocked_count=2,
            average_completion_pct=45.5
        )
        assert response.total_entities == 10
        assert response.blocked_count == 2
        assert response.average_completion_pct == 45.5


class TestGetPhasesEndpoint:
    """Test GET /phases/{entity_type}/{entity_id} endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_get_phases_success(self, mock_phase_service):
        """Test successful phases retrieval."""
        phases_data = {
            "research": {"status": "completed"},
            "planning": {"status": "in_progress"},
        }
        mock_phase_service.get_phases.return_value = Ok(phases_data)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import get_phases
            result = await get_phases("task", "T-001", mock_phase_service)

        assert result.entity_id == "T-001"
        assert result.entity_type == "task"
        assert result.phases["research"]["status"] == "completed"

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_get_phases_not_found(self, mock_phase_service):
        """Test phases retrieval for non-existent entity."""
        error = NotFoundError(
            message="Task not found",
            entity_type="task",
            entity_id="T-999"
        )
        mock_phase_service.get_phases.return_value = Err(error)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import get_phases
            with pytest.raises(NotFoundError):
                await get_phases("task", "T-999", mock_phase_service)


class TestGetPhaseSummaryEndpoint:
    """Test GET /phases/{entity_type}/{entity_id}/summary endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_get_phase_summary_success(self, mock_phase_service):
        """Test successful phase summary retrieval."""
        summary_data = {
            "entity_id": "T-001",
            "entity_type": "task",
            "current_phase": "planning",
            "phases_completed": 1,
            "phases_total": 4,
            "completion_pct": 25.0,
            "phases": {"research": {"status": "completed"}}
        }
        mock_phase_service.get_phase_summary.return_value = Ok(summary_data)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import get_phase_summary
            result = await get_phase_summary("task", "T-001", mock_phase_service)

        assert result.completion_pct == 25.0
        assert result.current_phase == "planning"


class TestUpdatePhaseEndpoint:
    """Test PATCH /phases/{entity_type}/{entity_id}/{phase_name} endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_update_phase_success(self, mock_phase_service):
        """Test successful phase update."""
        updated_phase = {"status": "in_progress", "has_research": True}
        mock_phase_service.update_phase.return_value = Ok(updated_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import update_phase
            request = PhaseUpdateRequest(
                status=PhaseStatus.IN_PROGRESS,
                additional_fields={"has_research": True}
            )
            result = await update_phase("task", "T-001", "research", request, mock_phase_service)

        assert result["status"] == "in_progress"
        mock_phase_service.update_phase.assert_called_once()

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_update_phase_invalid(self, mock_phase_service):
        """Test phase update with invalid phase name."""
        error = ValidationError(
            message="Invalid phase 'invalid' for task",
            field="phase_name",
            value="invalid"
        )
        mock_phase_service.update_phase.return_value = Err(error)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import update_phase
            request = PhaseUpdateRequest(status=PhaseStatus.IN_PROGRESS)
            with pytest.raises(ValidationError):
                await update_phase("task", "T-001", "invalid", request, mock_phase_service)


class TestAdvancePhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/advance endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_advance_phase_success(self, mock_phase_service):
        """Test successful phase advancement."""
        advanced_phases = {
            "research": {"status": "completed"},
            "planning": {"status": "in_progress"},
        }
        mock_phase_service.advance_phase.return_value = Ok(advanced_phases)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import advance_phase
            result = await advance_phase("task", "T-001", mock_phase_service)

        assert result.entity_id == "T-001"
        assert result.phases["planning"]["status"] == "in_progress"


class TestBlockPhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/{phase_name}/block endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_block_phase_success(self, mock_phase_service):
        """Test successful phase blocking."""
        blocked_phase = {"status": "blocked", "blocked_reason": "Waiting for API"}
        mock_phase_service.block_phase.return_value = Ok(blocked_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import block_phase
            request = BlockPhaseRequest(blocked_reason="Waiting for API")
            result = await block_phase("task", "T-001", "implementation", request, mock_phase_service)

        assert result["status"] == "blocked"
        assert result["blocked_reason"] == "Waiting for API"

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_block_phase_no_reason(self, mock_phase_service):
        """Test blocking phase without reason."""
        blocked_phase = {"status": "blocked"}
        mock_phase_service.block_phase.return_value = Ok(blocked_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import block_phase
            result = await block_phase("task", "T-001", "implementation", None, mock_phase_service)

        assert result["status"] == "blocked"


class TestUnblockPhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/{phase_name}/unblock endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_unblock_phase_success(self, mock_phase_service):
        """Test successful phase unblocking."""
        unblocked_phase = {"status": "in_progress", "blocked_reason": None}
        mock_phase_service.unblock_phase.return_value = Ok(unblocked_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import unblock_phase
            result = await unblock_phase("task", "T-001", "implementation", mock_phase_service)

        assert result["status"] == "in_progress"


class TestSkipPhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/{phase_name}/skip endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_skip_phase_success(self, mock_phase_service):
        """Test successful phase skipping."""
        skipped_phase = {"status": "skipped", "skip_reason": "Done in parent"}
        mock_phase_service.skip_phase.return_value = Ok(skipped_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import skip_phase
            request = SkipPhaseRequest(skip_reason="Done in parent")
            result = await skip_phase("task", "T-001", "research", request, mock_phase_service)

        assert result["status"] == "skipped"
        assert result["skip_reason"] == "Done in parent"


class TestCompletePhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/{phase_name}/complete endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_complete_phase_success(self, mock_phase_service):
        """Test successful phase completion."""
        completed_phase = {"status": "completed"}
        mock_phase_service.set_phase_status.return_value = Ok(completed_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import complete_phase
            result = await complete_phase("task", "T-001", "research", mock_phase_service)

        assert result["status"] == "completed"
        mock_phase_service.set_phase_status.assert_called_with(
            "T-001", "task", "research", PhaseStatus.COMPLETED
        )


class TestStartPhaseEndpoint:
    """Test POST /phases/{entity_type}/{entity_id}/{phase_name}/start endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_start_phase_success(self, mock_phase_service):
        """Test successful phase start."""
        started_phase = {"status": "in_progress"}
        mock_phase_service.set_phase_status.return_value = Ok(started_phase)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import start_phase
            result = await start_phase("task", "T-001", "research", mock_phase_service)

        assert result["status"] == "in_progress"
        mock_phase_service.set_phase_status.assert_called_with(
            "T-001", "task", "research", PhaseStatus.IN_PROGRESS
        )


class TestFindEntitiesInPhaseEndpoint:
    """Test GET /phases/{entity_type}/search endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_find_entities_in_phase_success(self, mock_phase_service):
        """Test finding entities in a specific phase."""
        entities = [
            {"id": "T-001", "phase": "implementation", "status": "blocked", "phase_data": {}},
            {"id": "T-002", "phase": "implementation", "status": "blocked", "phase_data": {}},
        ]
        mock_phase_service.find_entities_in_phase.return_value = Ok(entities)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import find_entities_in_phase
            result = await find_entities_in_phase(
                "task",
                phase_name="implementation",
                phase_status=PhaseStatus.BLOCKED,
                limit=100,
                offset=0,
                service=mock_phase_service
            )

        assert len(result) == 2
        assert all(isinstance(r, EntityInPhaseResponse) for r in result)


class TestFindBlockedEntitiesEndpoint:
    """Test GET /phases/blocked endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_find_blocked_entities_success(self, mock_phase_service):
        """Test finding all blocked entities."""
        blocked = [
            {"entity_type": "task", "entity_id": "T-001", "phase": "implementation", "blocked_reason": "Waiting"},
        ]
        mock_phase_service.find_blocked_entities.return_value = Ok(blocked)

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import find_blocked_entities
            result = await find_blocked_entities(
                entity_type="task",
                limit=100,
                offset=0,
                service=mock_phase_service
            )

        assert len(result) == 1
        assert isinstance(result[0], BlockedEntityResponse)
        assert result[0].entity_id == "T-001"


class TestPhaseAnalyticsEndpoint:
    """Test GET /phases/{entity_type}/analytics endpoint."""

    @pytest.mark.skip(reason="ADR: Phases API deferred to post-MVP")
    @pytest.mark.asyncio
    async def test_get_phase_analytics_success(self):
        """Test getting phase analytics."""
        # Create mock repository and entities
        mock_entity1 = MagicMock()
        mock_entity1.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "in_progress"},
            "implementation": {"status": "not_started"},
            "testing": {"status": "not_started"},
        }

        mock_entity2 = MagicMock()
        mock_entity2.phases = {
            "research": {"status": "completed"},
            "planning": {"status": "completed"},
            "implementation": {"status": "blocked"},
            "testing": {"status": "not_started"},
        }

        # Create mock repo with async find_all
        mock_repo = AsyncMock()
        mock_repo.find_all.return_value = Ok([mock_entity1, mock_entity2])

        # Create a mock service that returns the repo synchronously
        mock_phase_service = MagicMock()
        mock_phase_service._get_repository.return_value = mock_repo

        with patch("taskman_api.api.v1.phases.get_phase_service", return_value=mock_phase_service):
            from taskman_api.api.v1.phases import get_phase_analytics
            result = await get_phase_analytics(
                "task",
                limit=1000,
                offset=0,
                service=mock_phase_service
            )

        assert isinstance(result, PhaseAnalyticsResponse)
        assert result.total_entities == 2
        assert result.blocked_count == 1  # Only entity2 has blocked phase
