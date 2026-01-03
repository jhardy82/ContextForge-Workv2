from cf_core.dao.context import ContextRepository
from mcp.server.fastmcp import FastMCP

from taskman_api.dependencies import get_db_session

# cf_core might not have a full Service layer exposed in dependencies yet, utilizing Repository directly via generic pattern
# or check if ContextService exists in backend-api/services (it wasn't in list i saw earlier, only Repo in dep.py)

def register_context_tools(mcp: FastMCP):
    """Register Context (ContextForge) tools."""

    @mcp.tool()
    async def list_contexts(limit: int = 50) -> str:
        """List active contexts."""
        async for session in get_db_session():
            repo = ContextRepository(session)
            contexts = await repo.get_multi(limit=limit)
            return "\n".join([f"- [{c.id}] {c.title} ({c.kind})" for c in contexts])

    @mcp.tool()
    async def get_context(context_id: str) -> str:
        """Retrieve a specific context context."""
        async for session in get_db_session():
            repo = ContextRepository(session)
            ctx = await repo.get(context_id)
            if ctx:
                return f"Context {ctx.id}:\nTitle: {ctx.title}\nContent: {str(ctx.content)[:200]}..."
            return "Context not found."
