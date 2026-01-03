"""
CF_CORE Validation Module

Multi-agent validation swarm for task management workflows.
"""

from cf_core.validation.base_agent import BaseValidationAgent
from cf_core.validation.orchestrator import ValidationOrchestrator

__all__ = [
    "BaseValidationAgent",
    "ValidationOrchestrator",
]

__version__ = "1.0.0"
