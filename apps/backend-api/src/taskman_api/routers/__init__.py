"""
TaskMan-v2 API Routers Package
Organizes API endpoints into modular router components.
"""

from .action_lists import router as action_lists_router
from .agent import router as agent_router
from .checklists import router as checklists_router
from .conversations import router as conversations_router
from .diagnostic import router as diagnostic_router
from .phases import router as phases_router
from .plans import router as plans_router
from .projects import router as projects_router
from .qse import router as qse_router
from .sprints import router as sprints_router
from .tasks import router as tasks_router

__all__ = [
    "action_lists_router",
    "agent_router",
    "checklists_router",
    "conversations_router",
    "diagnostic_router",
    "phases_router",
    "plans_router",
    "projects_router",
    "sprints_router",
    "qse_router",
    "tasks_router",
]
