import logging
import os
import sys
from pathlib import Path

# Add workspace root to sys.path to find cf_core and cf_mcp
workspace_root = Path(__file__).resolve().parents[3]
sys.path.append(str(workspace_root))
sys.path.append(str(workspace_root / "TaskMan-v2/mcp-server-py/src"))

# Mock cf_core settings if needed, or let it load from environment/defaults
# We might typically need to set the DB path explicitly for testing if we don't want to touch the real one.
# But for "verification" we often want to test the real integration locally.
# Let's use a temporary DB path for safety if possible, or just read-only.

from cf_mcp.server import mcp
from cf_mcp.tools import register_tools

from cf_core.services.search.vector_store import DuckDBVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_mcp")


def main():
    logger.info("Starting MCP Verification...")

    # 1. Register tools (to ensure decorators run and everything initializes)
    register_tools(mcp)
    logger.info("Tools registered.")

    # Import functions directly to test logic
    from cf_mcp.tools import get_context_node, index_codebase, search_codebase

    # 2. Test Indexing
    logger.info("Testing 'index_codebase'...")
    # Use a safe path (e.g., current script dir)
    target_path = "TaskMan-v2/mcp-server-py/scripts"

    # Check if tools are callable (FastMCP decorators usually preserve callability)
    # If they are async, we need asyncio. If sync, just call.
    # Our implementation in tools/__init__.py used 'def', not 'async def'.

    try:
        idx_res = index_codebase(path=target_path)
        logger.info(f"Index Result: {idx_res}")
    except Exception as e:
        logger.error(f"Index failed: {e}")

    # 3. Test Search
    logger.info("Testing 'search_codebase'...")
    try:
        search_res = search_codebase(query="verification", limit=1)
        logger.info(f"Search Result: {search_res}")

        if "No relevant code found" in search_res or "Result" in search_res:
            logger.info("Search Logic Verified.")
        else:
            logger.warning("Search returned unexpected format.")

    except Exception as e:
        logger.error(f"Search failed: {e}")

    logger.info("Verification Complete.")


if __name__ == "__main__":
    main()
