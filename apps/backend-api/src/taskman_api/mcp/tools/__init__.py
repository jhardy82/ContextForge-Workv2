from mcp.server.fastmcp import FastMCP

from taskman_api.mcp.tools.context import register_context_tools
from taskman_api.mcp.tools.projects import register_project_tools
from taskman_api.mcp.tools.sprints import register_sprint_tools
from taskman_api.mcp.tools.tasks import register_task_tools


def register_all_tools(mcp: FastMCP):
    """Register all domains."""
    register_task_tools(mcp)
    register_project_tools(mcp)
    register_sprint_tools(mcp)
    register_context_tools(mcp)
