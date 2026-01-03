"""Unit tests for Task Pydantic schemas.

Tests validation rules and field constraints.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from taskman_api.core.enums import Priority, Severity, TaskStatus
from taskman_api.core.enums import Shape as GeometryShape
from taskman_api.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest


class TestTaskCreateRequest:
    """Test suite for TaskCreateRequest validation."""

    def test_valid_task_create_request(self):
        """Test creating a valid task create request."""
        data = {
            "id": "T-TEST-001",
            "title": "Test Task",
            "summary": "Test summary",
            "description": "Test description",
            "owner": "test.owner",
            "priority": Priority.P1,
            "primary_project": "P-TEST-001",
            "primary_sprint": "S-TEST-001",
        }

        request = TaskCreateRequest(**data)

        assert request.id == "T-TEST-001"
        assert request.title == "Test Task"
        assert request.status == TaskStatus.NEW  # Default value
        assert request.assignees == []  # Default empty list

    def test_task_id_pattern_validation_success(self):
        """Test task ID pattern validation with valid patterns."""
        valid_ids = [
            "T-001",
            "T-FEAT-123",
            "T-BUG-456",
            "T-ABC_DEF-789",
            "T-test-with-hyphens",
        ]

        for task_id in valid_ids:
            data = {
                "id": task_id,
                "title": "Test",
                "summary": "Summary",
                "description": "Description",
                "owner": "owner",
                "priority": Priority.P2,
                "primary_project": "P-TEST",
                "primary_sprint": "S-TEST",
            }
            request = TaskCreateRequest(**data)
            assert request.id == task_id

    def test_task_id_pattern_validation_failure(self):
        """Test task ID pattern validation with invalid patterns."""
        # Test pattern validation errors
        pattern_invalid_ids = [
            "TASK-001",  # Wrong prefix
            "T001",  # Missing hyphen
            "T-",  # No ID part
            "T-@invalid",  # Invalid character
        ]

        for task_id in pattern_invalid_ids:
            data = {
                "id": task_id,
                "title": "Test",
                "summary": "Summary",
                "description": "Description",
                "owner": "owner",
                "priority": Priority.P2,
                "primary_project": "P-TEST",
                "primary_sprint": "S-TEST",
            }

            with pytest.raises(ValidationError) as exc_info:
                TaskCreateRequest(**data)

            errors = exc_info.value.errors()
            assert any("pattern" in str(err).lower() for err in errors)

        # Test min_length validation (empty string)
        data = {
            "id": "",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P2,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
        }
        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(**data)
        errors = exc_info.value.errors()
        assert any("pattern" in str(err).lower() for err in errors)

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        # Missing required fields
        data = {
            "id": "T-TEST-001",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(**data)

        errors = exc_info.value.errors()
        required_fields = {
            "title",
            "summary",
            "owner",
            "primary_project",
        }
        error_fields = {err["loc"][0] for err in errors}

        assert required_fields.issubset(error_fields)

    def test_title_max_length_validation(self):
        """Test title maximum length validation."""
        data = {
            "id": "T-TEST-001",
            "title": "x" * 501,  # Exceeds 500 char limit
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P2,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "title" for err in errors)

    def test_estimate_points_non_negative(self):
        """Test estimate_points must be non-negative."""
        data = {
            "id": "T-TEST-001",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P2,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
            "estimate_points": -5,  # Negative value
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(err["loc"][0] == "estimate_points" for err in errors)

    def test_business_value_score_range(self):
        """Test business_value_score must be 0-10."""
        # Test below range
        data = {
            "id": "T-TEST-001",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P2,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
            "business_value_score": -1,
        }

        with pytest.raises(ValidationError):
            TaskCreateRequest(**data)

        # Test above range
        data["business_value_score"] = 101

        with pytest.raises(ValidationError):
            TaskCreateRequest(**data)

        # Test valid range
        data["business_value_score"] = 5
        request = TaskCreateRequest(**data)
        assert request.business_value_score == 5

    def test_enum_field_validation(self):
        """Test enum field validation."""
        data = {
            "id": "T-TEST-001",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P1,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
            "status": TaskStatus.IN_PROGRESS,
            "severity": Severity.SEV2,
            "shape": GeometryShape.CIRCLE,
        }

        request = TaskCreateRequest(**data)
        assert request.status == TaskStatus.IN_PROGRESS
        assert request.severity == Severity.SEV2
        assert request.shape == GeometryShape.CIRCLE

    def test_default_values(self):
        """Test default values are applied correctly."""
        data = {
            "id": "T-TEST-001",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "owner": "owner",
            "priority": Priority.P2,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
        }

        request = TaskCreateRequest(**data)
        assert request.status == TaskStatus.NEW
        assert request.assignees == []
        assert request.labels == []
        assert request.related_projects == []
        assert request.automation_candidate is False


class TestTaskUpdateRequest:
    """Test suite for TaskUpdateRequest validation."""

    def test_partial_update_all_fields_optional(self):
        """Test that all fields are optional for partial updates."""
        data = {"title": "Updated Title"}

        request = TaskUpdateRequest(**data)
        assert request.title == "Updated Title"
        assert request.summary is None
        assert request.description is None

    def test_update_with_multiple_fields(self):
        """Test updating multiple fields at once."""
        data = {
            "title": "Updated Title",
            "status": TaskStatus.IN_PROGRESS,
            "estimate_points": 5.0,
        }

        request = TaskUpdateRequest(**data)
        assert request.title == "Updated Title"
        assert request.status == TaskStatus.IN_PROGRESS
        assert request.estimate_points == 5.0

    def test_update_validation_rules_still_apply(self):
        """Test that validation rules still apply to update requests."""
        # Test title min length
        data = {"title": ""}

        with pytest.raises(ValidationError):
            TaskUpdateRequest(**data)

        # Test estimate_points non-negative
        data = {"estimate_points": -1}

        with pytest.raises(ValidationError):
            TaskUpdateRequest(**data)


class TestTaskResponse:
    """Test suite for TaskResponse schema."""

    def test_response_from_orm_model(self):
        """Test creating response from ORM model."""
        from taskman_api.models.task import Task

        # Create mock ORM task
        task = Task(
            id="T-TEST-001",
            title="Test Task",
            summary="Summary",
            description="Description",
            status=TaskStatus.NEW,
            owner="owner",
            assignees=[],
            priority=Priority.P1,
            primary_project="P-TEST",
            primary_sprint="S-TEST",
            related_projects=[],
            related_sprints=[],
            parents=[],
            depends_on=[],
            blocks=[],
            blockers=[],
            acceptance_criteria=[],
            definition_of_done=[],
            quality_gates={},
            verification={},
            actions_taken=[],
            labels=[],
            related_links=[],
            risks=[],
            observability={},
        )
        # Note: 'phases' tracked separately in TaskPhase model (not a Task field)

        # Set timestamps manually (normally set by TimestampMixin)
        task.created_at = datetime(2025, 1, 1, 12, 0, 0)
        task.updated_at = datetime(2025, 1, 1, 12, 0, 0)

        # Create response from ORM model
        response = TaskResponse.model_validate(task)

        assert response.id == "T-TEST-001"
        assert response.title == "Test Task"
        assert response.created_at == task.created_at
        assert response.updated_at == task.updated_at

    def test_response_serialization(self):
        """Test response can be serialized to dict/JSON."""
        data = {
            "id": "T-TEST-001",
            "title": "Test",
            "summary": "Summary",
            "description": "Description",
            "status": TaskStatus.NEW,
            "owner": "owner",
            "assignees": [],
            "priority": Priority.P1,
            "severity": None,
            "primary_project": "P-TEST",
            "primary_sprint": "S-TEST",
            "related_projects": [],
            "related_sprints": [],
            "estimate_points": None,
            "actual_time_hours": None,
            "due_at": None,
            "parents": [],
            "depends_on": [],
            "blocks": [],
            "blockers": [],
            "acceptance_criteria": [],
            "definition_of_done": [],
            "quality_gates": {},
            "verification": {},
            "actions_taken": [],
            "labels": [],
            "related_links": [],
            "shape": None,
            "stage": None,
            "work_type": None,
            "work_stream": None,
            "business_value_score": None,
            "cost_of_delay_score": None,
            "automation_candidate": None,
            "cycle_time_days": None,
            "risks": [],
            "observability": {},
            "phases": {
                "research": {"status": "not_started", "has_research": False, "research_adequate": False},
                "planning": {"status": "not_started", "has_acceptance_criteria": False, "has_definition_of_done": False},
                "implementation": {"status": "not_started", "progress_pct": 0, "has_code_changes": False},
                "testing": {"status": "not_started", "has_unit_tests": False, "tests_passing": False},
            },
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
            "updated_at": datetime(2025, 1, 1, 12, 0, 0),
        }

        response = TaskResponse(**data)
        response_dict = response.model_dump()

        assert isinstance(response_dict, dict)
        assert response_dict["id"] == "T-TEST-001"
        assert response_dict["title"] == "Test"
