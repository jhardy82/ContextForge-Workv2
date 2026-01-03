import logging

from mcp.server.fastmcp import FastMCP

from cf_mcp.config import settings
from cf_mcp.db import get_db
from cf_mcp.tools import register_tools

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("TaskMan-Python", dependencies=["asyncpg", "sqlalchemy"])


@mcp.on_startup
async def on_startup(context):
    """Initialize database connection on startup."""
    print("Starting TaskMan-Python MCP Server...")
    print(f"Connecting to database at {settings.DATABASE_URL.split('@')[-1]}")  # Log safe URL


@mcp.tool()
async def health_check() -> str:
    """Check database connectivity."""
    try:
        async for session in get_db():
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
        return "Database Connected Successfully"
    except Exception as e:
        return f"Database Connection Failed: {str(e)}"


# Tools from tools.py will be re-imported/registered here in future milestones


def main():
    """Entry point for the MCP server."""
    logger.info("Starting ContextForge MCP Server...")
    # Tools are registered via decorators or explicit registration if needed.
    # We will import the tools module to ensure decorators run.
    register_tools(mcp)
    from cf_mcp.tools.tasks import register_task_tools

    register_task_tools(mcp)

    from cf_mcp.tools.projects import register_project_tools

    register_project_tools(mcp)

    from cf_mcp.tools.sprints import register_sprint_tools

    register_sprint_tools(mcp)

    # Run the server (auto-selects transport based on args, defaults to stdio)
    mcp.run()


if __name__ == "__main__":
    main()
