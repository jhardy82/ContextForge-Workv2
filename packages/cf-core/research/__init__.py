"""
CF_CORE Research Module

Research agent swarm for analyzing codebases, gathering best practices,
and generating implementation specifications.

The research swarm uses:
- 9 specialized research agents
- Flow-based DAG orchestration
- MCP tool integration (microsoft-learn, github-copilot, memory, database-mcp, etc.)
- Evidence logging for audit trails
- Knowledge graph building
"""

from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.research_orchestrator import ResearchOrchestrator

__all__ = [
    "BaseResearchAgent",
    "ResearchOrchestrator"
]
