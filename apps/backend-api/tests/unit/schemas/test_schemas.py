"""Unit tests for Project, Sprint, and ActionList schemas.

Consolidated test suite for remaining Pydantic schemas.
"""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from taskman_api.core.enums import ActionListStatus, ProjectStatus, SprintCadence, SprintStatus
from taskman_api.schemas.action_list import (
    ActionListCreateRequest,
    ActionListResponse,
    ActionListUpdateRequest,
)
from taskman_api.schemas.project import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from taskman_api.schemas.sprint import SprintCreateRequest, SprintResponse, SprintUpdateRequest


class TestProjectSchemas:
    """Test suite for Project schemas."""

    def test_project_create_request_valid(self):
        """Test creating a valid project create request."""
        data = {
            "id": "P-TEST-001",
            "name": "Test Project",
            "mission": "Test mission",
            "start_date": date(2025, 1, 1),
            "owner": "test.owner",
        }

        request = ProjectCreateRequest(**data)
        assert request.id == "P-TEST-001"
        assert request.status == ProjectStatus.NEW  # Default

    def test_project_id_pattern_validation(self):
        """Test project ID pattern validation."""
        # Valid patterns
        valid_ids = ["P-TEST", "P-TASKMAN-V2", "P-ABC_123"]
        for pid in valid_ids:
            data = {
                "id": pid,
                "name": "Test",
                "mission": "Mission",
                "start_date": date(2025, 1, 1),
                "owner": "owner",
            }
            request = ProjectCreateRequest(**data)
            assert request.id == pid

        # Invalid patterns
        invalid_ids = ["PROJECT-001", "P", "P-@invalid"]
        for pid in invalid_ids:
            data = {
                "id": pid,
                "name": "Test",
                "mission": "Mission",
                "start_date": date(2025, 1, 1),
                "owner": "owner",
            }
            with pytest.raises(ValidationError):
                ProjectCreateRequest(**data)

    def test_project_update_request_partial(self):
        """Test partial project updates."""
        data = {"name": "Updated Name", "status": ProjectStatus.ACTIVE}

        request = ProjectUpdateRequest(**data)
        assert request.name == "Updated Name"
        assert request.status == ProjectStatus.ACTIVE
        assert request.mission is None  # Not provided

    def test_project_response_serialization(self):
        """Test project response serialization."""
        data = {
            "id": "P-TEST",
            "name": "Project",
            "mission": "Mission",
            "status": ProjectStatus.ACTIVE,
            "start_date": date(2025, 1, 1),
            "target_end_date": None,
            "owner": "owner",
            "sponsors": [],
            "stakeholders": [],
            "repositories": [],
            "comms_channels": [],
            "okrs": [],
            "kpis": [],
            "roadmap": [],
            "risks": [],
            "assumptions": [],
            "constraints": [],
            "dependencies_external": [],
            "sprints": [],
            "related_projects": [],
            "shared_components": [],
            "security_posture": None,
            "compliance_requirements": [],
            "governance": {},
            "success_metrics": [],
            "mpv_policy": {},
            "tnve_mandate": False,
            "evidence_root": None,
            "observability": {},
            "phases": {
                "research": {"status": "not_started", "has_market_research": False, "has_technical_research": False, "research_adequate": False},
                "planning": {"status": "not_started", "has_prd": False, "has_architecture": False, "has_roadmap": False},
            },
            "pending_reason": None,
            "blocked_reason": None,
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }

        response = ProjectResponse(**data)
        assert response.id == "P-TEST"
        assert isinstance(response.model_dump(), dict)


class TestSprintSchemas:
    """Test suite for Sprint schemas."""

    def test_sprint_create_request_valid(self):
        """Test creating a valid sprint create request."""
        data = {
            "id": "S-2025-01",
            "name": "Sprint 1",
            "goal": "Sprint goal",
            "cadence": SprintCadence.BIWEEKLY,
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 1, 14),
            "owner": "scrum.master",
            "primary_project": "P-TEST",
        }

        request = SprintCreateRequest(**data)
        assert request.id == "S-2025-01"
        assert request.status == SprintStatus.NEW  # Default
        assert request.cadence == SprintCadence.BIWEEKLY

    def test_sprint_id_pattern_validation(self):
        """Test sprint ID pattern validation."""
        # Valid patterns
        valid_ids = ["S-2025-01", "S-TEST-SPRINT", "S-ABC_123"]
        for sid in valid_ids:
            data = {
                "id": sid,
                "name": "Sprint",
                "goal": "Goal",
                "cadence": SprintCadence.WEEKLY,
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 7),
                "owner": "owner",
                "primary_project": "P-TEST",
            }
            request = SprintCreateRequest(**data)
            assert request.id == sid

        # Invalid patterns
        invalid_ids = ["SPRINT-01", "S", "S-@invalid"]
        for sid in invalid_ids:
            data = {
                "id": sid,
                "name": "Sprint",
                "goal": "Goal",
                "cadence": SprintCadence.WEEKLY,
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 7),
                "owner": "owner",
                "primary_project": "P-TEST",
            }
            with pytest.raises(ValidationError):
                SprintCreateRequest(**data)

    def test_sprint_velocity_points_non_negative(self):
        """Test velocity points must be non-negative."""
        data = {
            "id": "S-TEST",
            "name": "Sprint",
            "goal": "Goal",
            "cadence": SprintCadence.WEEKLY,
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 1, 7),
            "owner": "owner",
            "primary_project": "P-TEST",
            "velocity_target_points": -5,  # Invalid
        }

        with pytest.raises(ValidationError):
            SprintCreateRequest(**data)

        # Valid non-negative
        data["velocity_target_points"] = 10.5
        request = SprintCreateRequest(**data)
        assert request.velocity_target_points == 10.5

    def test_sprint_update_request_partial(self):
        """Test partial sprint updates."""
        data = {
            "status": SprintStatus.ACTIVE,
            "actual_points": 8.0,
        }

        request = SprintUpdateRequest(**data)
        assert request.status == SprintStatus.ACTIVE
        assert request.actual_points == 8.0
        assert request.name is None

    def test_sprint_response_with_metrics(self):
        """Test sprint response with metrics."""
        data = {
            "id": "S-TEST",
            "name": "Sprint",
            "goal": "Goal",
            "cadence": SprintCadence.BIWEEKLY,
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 1, 14),
            "status": SprintStatus.ACTIVE,
            "owner": "owner",
            "primary_project": "P-TEST",
            "tasks": [],
            "imported_tasks": [],
            "related_projects": [],
            "velocity_target_points": 20.0,
            "committed_points": 18.0,
            "actual_points": 16.0,
            "carried_over_points": 2.0,
            "definition_of_done": [],
            "dependencies": {},
            "scope_changes": [],
            "risks": [],
            "ceremonies": {},
            "metrics": {"throughput": 16, "predictability_pct": 88.9},
            "timezone": "America/New_York",
            "observability": {},
            "phases": {
                "planning": {"status": "not_started", "has_sprint_goal": False, "has_capacity_plan": False, "tasks_estimated": False},
                "implementation": {"status": "not_started", "progress_pct": 0, "tasks_completed": 0, "tasks_total": 0},
            },
            "pending_reason": None,
            "blocked_reason": None,
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }

        response = SprintResponse(**data)
        assert response.metrics["throughput"] == 16
        assert response.timezone == "America/New_York"


class TestActionListSchemas:
    """Test suite for ActionList schemas."""

    def test_action_list_create_request_valid(self):
        """Test creating a valid action list create request."""
        data = {
            "id": "AL-TEST-001",
            "title": "Test Action List",
            "status": "active",
            "items": [{"task": "Item 1", "done": False}],
        }

        request = ActionListCreateRequest(**data)
        assert request.id == "AL-TEST-001"
        assert request.title == "Test Action List"
        assert len(request.items) == 1

    def test_action_list_with_associations(self):
        """Test action list with project/sprint associations."""
        data = {
            "id": "AL-TEST",
            "title": "Action List",
            "status": "active",
            "project_id": "P-TEST",
            "sprint_id": "S-TEST",
            "items": [],
        }

        request = ActionListCreateRequest(**data)
        assert request.project_id == "P-TEST"
        assert request.sprint_id == "S-TEST"

    def test_action_list_soft_delete_fields(self):
        """Test action list soft delete fields (Response schema only)."""
        data = {
            "id": "AL-TEST",
            "title": "Action List",
            "status": ActionListStatus.ACTIVE,
            "parent_deleted_at": datetime(2025, 1, 1, 12, 0, 0),
            "parent_deletion_note": {"reason": "Project closed"},
            "items": [],
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }

        response = ActionListResponse(**data)
        assert response.parent_deleted_at is not None
        assert response.parent_deletion_note["reason"] == "Project closed"

    def test_action_list_update_request_partial(self):
        """Test partial action list updates."""
        data = {
            "title": "Updated Title",
            "completed_at": datetime(2025, 1, 15),
        }

        request = ActionListUpdateRequest(**data)
        assert request.title == "Updated Title"
        assert request.completed_at is not None
        assert request.status is None

    def test_action_list_response_with_metadata(self):
        """Test action list response with metadata."""
        data = {
            "id": "AL-TEST",
            "title": "Action List",
            "description": "Description",
            "status": "active",
            "owner": "owner",
            "tags": ["tag1", "tag2"],
            "project_id": "P-TEST",
            "sprint_id": None,
            "items": [{"task": "Item", "done": True}],
            "geometry_shape": "Circle",
            "priority": "high",
            "due_date": None,
            "evidence_refs": [],
            "extra_metadata": {"custom": "value"},
            "notes": "Some notes",
            "parent_deleted_at": None,
            "parent_deletion_note": {},
            "completed_at": None,
            "created_at": datetime(2025, 1, 1),
            "updated_at": datetime(2025, 1, 1),
        }

        response = ActionListResponse(**data)
        assert response.tags == ["tag1", "tag2"]
        assert response.extra_metadata["custom"] == "value"
        assert response.geometry_shape == "Circle"


class TestBaseSchemaConfiguration:
    """Test base schema configuration."""

    def test_strict_type_validation(self):
        """Test that type coercion is enabled (strict=False)."""
        from taskman_api.schemas.base import TaskManBaseModel

        class TestSchema(TaskManBaseModel):
            value: int

        # Non-strict mode should coerce string to int
        result = TestSchema(value="123")  # String coerced to int
        assert result.value == 123
        assert isinstance(result.value, int)

    def test_from_attributes_orm_mode(self):
        """Test ORM mode (from_attributes) is enabled."""
        from taskman_api.schemas.base import TaskManBaseModel

        class MockORM:
            def __init__(self):
                self.id = "test"
                self.name = "Test Name"

        class TestSchema(TaskManBaseModel):
            id: str
            name: str

        orm_obj = MockORM()
        schema = TestSchema.model_validate(orm_obj)

        assert schema.id == "test"
        assert schema.name == "Test Name"
