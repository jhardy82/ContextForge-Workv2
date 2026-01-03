"""Enumeration types for TaskMan API.

All enums follow the JSON schema definitions from schemas/tracker-*.schema.json.
"""

from enum import Enum


class TaskStatus(str, Enum):
    """Task lifecycle status.

    Enum values from tracker-task.schema.json.
    """
    NEW = "new"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    DROPPED = "dropped"


class Priority(str, Enum):
    """Task priority levels.

    Higher priority (p0) = more urgent, lower priority (p3) = less urgent.
    """
    P0 = "p0"  # Critical - Immediate attention required
    P1 = "p1"  # High - Important, should be done soon
    P2 = "p2"  # Medium - Normal priority
    P3 = "p3"  # Low - Can be deferred


class Severity(str, Enum):
    """Task severity levels for incidents/bugs.

    Severity indicates impact, priority indicates urgency.
    """
    SEV1 = "sev1"  # Critical - System down, major impact
    SEV2 = "sev2"  # High - Major feature impaired
    SEV3 = "sev3"  # Medium - Minor feature impaired
    SEV4 = "sev4"  # Low - Cosmetic or minor issue


class ProjectStatus(str, Enum):
    """Project lifecycle status.

    Enum values from tracker-project.schema.json.
    """
    DISCOVERY = "discovery"  # Initial research and planning
    ACTIVE = "active"        # Actively being worked on
    PAUSED = "paused"        # Temporarily on hold
    CLOSED = "closed"        # Completed or cancelled


class SprintStatus(str, Enum):
    """Sprint lifecycle status.

    Enum values from tracker-sprint.schema.json.
    """
    PLANNED = "planned"  # Scheduled but not yet started
    ACTIVE = "active"    # Currently in progress
    CLOSED = "closed"    # Completed


class SprintCadence(str, Enum):
    """Sprint cadence/frequency.

    Enum values from tracker-sprint.schema.json.
    """
    WEEKLY = "weekly"        # 1-week sprints
    BIWEEKLY = "biweekly"    # 2-week sprints (most common)
    MONTHLY = "monthly"      # 4-week sprints
    CUSTOM = "custom"        # Custom duration


class WorkType(str, Enum):
    """Categorical work type classification.

    Used for task categorization and reporting.
    """
    FEATURE = "feature"          # New functionality
    REFACTOR = "refactor"        # Code improvement without new features
    GOVERNANCE = "governance"    # Policy, compliance, documentation
    MIGRATION = "migration"      # System/data migration work
    BUG = "bug"                  # Bug fix
    TECH_DEBT = "tech_debt"      # Technical debt reduction
    RESEARCH = "research"        # Spike, investigation, POC


class GeometryShape(str, Enum):
    """Sacred Geometry shape classification.

    ContextForge integration - geometric patterns for work analysis.
    Enum values from tracker-task.schema.json.
    """
    TRIANGLE = "Triangle"          # Foundation work (3 points)
    CIRCLE = "Circle"              # Iterative/cyclical work
    SPIRAL = "Spiral"              # Progressive evolution
    FRACTAL = "Fractal"            # Self-similar, scalable patterns
    PENTAGON = "Pentagon"          # Phi-ratio harmonics (5 points)
    DODECAHEDRON = "Dodecahedron"  # Complex multi-faceted work (12 faces)


class HealthStatus(str, Enum):
    """Observability health status.

    Used in observability field for tasks, projects, sprints.
    """
    GREEN = "green"    # Healthy, on track
    YELLOW = "yellow"  # Warning, needs attention
    RED = "red"        # Critical, urgent action required


class RiskLevel(str, Enum):
    """Risk impact and likelihood levels.

    Used in risk entries for tasks, projects, sprints.
    """
    LOW = "low"    # Low impact/likelihood
    MED = "med"    # Medium impact/likelihood
    HIGH = "high"  # High impact/likelihood


class MilestoneStatus(str, Enum):
    """Project milestone status.

    From tracker-project.schema.json roadmap.
    """
    PLANNED = "planned"        # Scheduled but not started
    IN_PROGRESS = "in_progress"  # Currently being worked on
    DONE = "done"              # Completed
    AT_RISK = "at_risk"        # Behind schedule or blocked


class ScopeChangeType(str, Enum):
    """Sprint scope change types.

    From tracker-sprint.schema.json scope_changes.
    """
    ADD = "add"        # Task added to sprint
    REMOVE = "remove"  # Task removed from sprint
    RESIZE = "resize"  # Task estimate changed


class QualityGateResult(str, Enum):
    """Quality gate pass/fail result.

    From tracker-task.schema.json quality_gates.
    """
    PASS = "pass"  # Quality gate passed  # nosec B105 - not a password
    FAIL = "fail"  # Quality gate failed


class VerificationResult(str, Enum):
    """MPV verification evidence result.

    From tracker-task.schema.json verification.mpv_evidence.
    """
    PASS = "pass"  # Verification passed  # nosec B105 - not a password
    FAIL = "fail"  # Verification failed
