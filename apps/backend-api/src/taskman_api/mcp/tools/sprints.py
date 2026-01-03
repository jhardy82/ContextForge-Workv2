
from mcp.server.fastmcp import FastMCP

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_db_session
from taskman_api.schemas.sprint import SprintCreate
from taskman_api.services.sprint_service import SprintService


def register_sprint_tools(mcp: FastMCP):
    """Register Sprint management tools."""

    @mcp.tool()
    async def list_sprints(
        limit: int = 20,
        offset: int = 0,
        status: str | None = None
    ) -> str:
        """List sprints."""
        async for session in get_db_session():
            service = SprintService(session)
            try:
                # Assuming generic repository get_multi or specialized search
                sprints = await service.sprint_repo.get_multi(limit=limit, skip=offset)
                return f"Found {len(sprints)} sprints:\n" + \
                       "\n".join([f"- [{s.id}] {s.name} ({s.status})" for s in sprints])
            except Exception as e:
                return f"Error listing sprints: {str(e)}"

    @mcp.tool()
    async def create_sprint(
        name: str,
        goal: str = "",
        start_date: str | None = None, # ISO string
        end_date: str | None = None
    ) -> str:
        """Create a new sprint."""
        async for session in get_db_session():
            service = SprintService(session)
            # Schema might require datetime objects. Pydantic usually parses ISO strings.
            from datetime import datetime

            s_date = datetime.fromisoformat(start_date) if start_date else None
            e_date = datetime.fromisoformat(end_date) if end_date else None

            req = SprintCreate(
                name=name,
                goal=goal,
                start_date=s_date,
                end_date=e_date,
                status="planned"
            )

            result = await service.create(req)
            match result:
                case Ok(sprint):
                    return f"Created Sprint {sprint.id}: {sprint.name}"
                case Err(e):
                    return f"Error creating sprint: {str(e)}"
