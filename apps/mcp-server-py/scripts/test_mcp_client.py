import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add workspace root to pythonpath for cf_core
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

async def run_test():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "cf-mcp"],  # Assuming installed via uv or access to pyproject
        env={
            **os.environ,
            "PYTHONPATH": WORKSPACE_ROOT,  # CRITICAL for cf_core resolution
            "UV_PROJECT_ENVIRONMENT": os.path.join(WORKSPACE_ROOT, ".venv") # explicit venv if needed
        }
    )

    # Alternatively, direct python execution if 'cf-mcp' isn't on path yet
    # We are in dev mode, so maybe run module directly
    server_params = StdioServerParameters(
        command=sys.executable, # Use CURRENT python which has dependencies? No, separate process.
        args=["-m", "cf_mcp.server"],
        env={
            **os.environ,
            "PYTHONPATH": os.path.join(WORKSPACE_ROOT, "mcp-server-py", "src") + os.pathsep + WORKSPACE_ROOT,
        }
    )

    print(f"Starting server with PYTHONPATH: {server_params.env['PYTHONPATH']}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Tools found: {[t.name for t in tools.tools]}")
            assert "search_codebase" in [t.name for t in tools.tools]

            # Test Search
            print("Testing search_codebase...")
            result = await session.call_tool("search_codebase", arguments={"query": "velocity"})
            print(f"Search Result: {result.content[0].text[:100]}...")

            # Test Get Context
            # We need a valid ID potentially, or just check 'index_codebase' exists
            print("Testing index_codebase existence...")
            assert "index_codebase" in [t.name for t in tools.tools]

            print("Integration Test Passed!")

if __name__ == "__main__":
    asyncio.run(run_test())
