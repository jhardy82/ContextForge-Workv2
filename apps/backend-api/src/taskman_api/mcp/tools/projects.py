from mcp.server.fastmcp import FastMCP

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_db_session
from taskman_api.schemas.project import ProjectCreate
from taskman_api.services.project_service import ProjectService


def register_project_tools(mcp: FastMCP):
    """Register Project management tools."""

    @mcp.tool()
    async def list_projects(
        limit: int = 20,
        offset: int = 0
    ) -> str:
        """List all projects."""
        async for session in get_db_session():
            service = ProjectService(session)
            # ProjectService.list is the standard method for simple listing
            # Or assume we need search if filtering is added later
            try:
                # Use list() if available, or search strategies
                # Checking ProjectRepository/Service standard methods
                projects = await service.project_repo.get_multi(limit=limit, skip=offset)
                total = await service.project_repo.count()

                return f"Found {len(projects)} projects (Total: {total}):\n" + \
                       "\n".join([f"- [{p.id}] {p.name} ({p.status})" for p in projects])
            except Exception as e:
                return f"Error listing projects: {str(e)}"

    @mcp.tool()
    async def create_project(
        name: str,
        description: str = "",  # Maps to 'mission' or 'summary' depending on model, schema uses 'mission'?
        # Checking backend-api schema might be needed, assuming standard ProjectCreate
    ) -> str:
        """Create a new project."""
        async for session in get_db_session():
            service = ProjectService(session)

            # Note: Project schema in backend-api might use 'mission' instead of 'description'.
            # We should check schema, but for now assuming ProjectCreate aligns with model.
            # If ProjectCreate has 'mission', we map description -> mission.
            req = ProjectCreate(
                name=name,
                mission=description, # Assuming mission is the tailored field
                status="active"
            )

            result = await service.create(req)
            match result:
                case Ok(project):
                    return f"Created Project {project.id}: {project.name}"
                case Err(e):
                    return f"Error creating project: {str(e)}"

    @mcp.tool()
    async def get_project(project_id: str) -> str:
        """Get details of a specific project."""
        async for session in get_db_session():
            service = ProjectService(session)
            result = await service.get(project_id)
            match result:
                case Ok(p):
                    return f"Project {p.id}:\nName: {p.name}\nStatus: {p.status}\nMission: {p.mission}"
                case Err(e):
                    return f"Error: {str(e)}"
