import logging

from mcp.server.fastmcp import FastMCP

from taskman_api.config import get_settings

# Get settings
settings = get_settings()

# Configure logging
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger("taskman.mcp")

# Initialize FastMCP
mcp = FastMCP("TaskMan-v2-Unified", dependencies=["asyncpg", "sqlalchemy"])


@mcp.tool()
async def health_check() -> str:
    """Check database connectivity and server status."""
    from taskman_api.db.session import check_db_health

    # Lazy init DB if needed (idempotent usually)
    # await init_db()

    health = await check_db_health()
    return f"Status: {health.get('status', 'unknown')}, Connected: {health.get('connected', False)}"


def main():
    """Entry point for the MCP server."""
    from taskman_api.mcp.tools import register_all_tools

    # Register all ported tools
    register_all_tools(mcp)

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
