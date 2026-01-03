import pytest

from cf_core.domain.project_entity import ProjectEntity
from cf_core.models.observability import Observability


def test_project_entity_create_full():
    """Verify ProjectEntity.create handles all new MVP fields."""
    project = ProjectEntity.create(
        project_id="P-001",
        name="Test Project",
        mission="To Create Tests",
        vision="A world with 100% coverage",
        observability=Observability.create_healthy(),
    )

    assert project.mission == "To Create Tests"
    assert project.vision == "A world with 100% coverage"
    assert project.observability.last_health == "green"


def test_project_entity_create_defaults():
    """Verify defaults for optional fields."""
    project = ProjectEntity.create(project_id="P-002", name="Minimal Project")

    assert project.mission is None
    assert project.vision is None
    assert isinstance(project.observability, Observability)
    assert project.observability.last_health == "green"  # Default healthy
