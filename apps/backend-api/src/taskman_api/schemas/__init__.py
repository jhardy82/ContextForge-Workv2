"""
Centralized Pydantic schemas for TaskMan-v2 API.
All schemas match the full database complexity.
"""

# Enums
from taskman_api.core.enums import (
    ActionListStatus,
    HealthStatus,
    ProjectStatus,
    Shape,
    SprintCadence,
    SprintStatus,
    Stage,
    TaskStatus,
    WorkType,
)
from taskman_api.core.enums import Priority as TaskPriority
from taskman_api.core.enums import Severity as TaskSeverity

# ActionList schemas
from taskman_api.schemas.action_list import (
    ActionListAddItemRequest,
    ActionListCollection,
    ActionListCreate,
    ActionListItem,
    ActionListResponse,
    ActionListUpdate,
    ReorderItemsRequest,
)

# Base classes and mixins
from taskman_api.schemas.base import (
    BusinessMetricsMixin,
    ContextForgeMixin,
    DependencyMixin,
    MetadataMixin,
    ObservabilityMixin,
    OwnershipMixin,
    ProjectSprintAssociationMixin,
    QualityMixin,
    RiskMixin,
    TaskManBaseModel,
    TimestampMixin,
)

# Project schemas
from taskman_api.schemas.project import ProjectCreate, ProjectList, ProjectResponse, ProjectUpdate

# Sprint schemas
from taskman_api.schemas.sprint import (
    SprintCreate,
    SprintList,
    SprintProgress,
    SprintResponse,
    SprintUpdate,
)

# Task schemas
from taskman_api.schemas.task import TaskCreate, TaskList, TaskResponse, TaskUpdate

__all__ = [
    # Enums
    "TaskStatus",
    "TaskPriority",
    "TaskSeverity",
    "ProjectStatus",
    "SprintStatus",
    "SprintCadence",
    "ActionListStatus",
    "HealthStatus",
    "Shape",
    "Stage",
    "WorkType",
    # Base
    "TaskManBaseModel",
    "TimestampMixin",
    "ObservabilityMixin",
    "OwnershipMixin",
    "ProjectSprintAssociationMixin",
    "DependencyMixin",
    "QualityMixin",
    "MetadataMixin",
    "ContextForgeMixin",
    "BusinessMetricsMixin",
    "RiskMixin",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskList",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectList",
    # Sprint
    "SprintCreate",
    "SprintUpdate",
    "SprintResponse",
    "SprintList",
    "SprintProgress",
    # ActionList
    "ActionListCreate",
    "ActionListUpdate",
    "ActionListResponse",
    "ActionListCollection",
    "ActionListItem",
    "ActionListAddItemRequest",
    "ReorderItemsRequest",
]
