
from mcp.server.fastmcp import FastMCP

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_db_session
from taskman_api.schemas.task import TaskCreateRequest
from taskman_api.services.task_service import TaskService


def register_task_tools(mcp: FastMCP):
    """Register Task management tools."""

    @mcp.tool()
    async def list_tasks(
        status: str | None = None,
        priority: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> str:
        """List tasks with filtering."""
        # Manually manage session since we aren't in FastAPI request context
        async for session in get_db_session():
            service = TaskService(session)
            # Convert string args to Enums if needed, or pass as is if Service handles it (it typically expects Enums)
            # Service.search methods usually handle None gracefully

            # Note: We need to handle Enum conversion if Service expects it.
            # TaskService.search expects TaskStatus/Priority Enums.
            # Let's import them.
            from taskman_api.core.enums import Priority, TaskStatus

            search_status = TaskStatus(status) if status else None
            search_priority = Priority(priority) if priority else None

            result = await service.search(
                status=search_status,
                priority=search_priority,
                limit=limit,
                offset=offset
            )

            match result:
                case Ok((tasks, total)):
                    # Helper to format response
                    return f"Found {len(tasks)} tasks (Total: {total}):\n" + \
                           "\n".join([f"- [{t.id}] {t.title} ({t.status})" for t in tasks])
                case Err(e):
                    return f"Error listing tasks: {str(e)}"

    @mcp.tool()
    async def create_task(
        title: str,
        primary_project: str,
        primary_sprint: str,
        description: str = "",
        priority: str = "p2"
    ) -> str:
        """Create a new task."""
        async for session in get_db_session():
            service = TaskService(session)

            # Pydantic validation happens in TaskCreateRequest
            req = TaskCreateRequest(
                title=title,
                primary_project=primary_project,
                primary_sprint=primary_sprint,
                description=description,
                priority=priority,
                # Default status is 'new'
            )

            result = await service.create(req)

            match result:
                case Ok(task):
                    return f"Created Task {task.id}: {task.title}"
                case Err(e):
                    return f"Error creating task: {str(e)}"

    @mcp.tool()
    async def get_task(task_id: str) -> str:
        """Get details of a specific task."""
        async for session in get_db_session():
            service = TaskService(session)
            result = await service.get(task_id)

            match result:
                case Ok(task):
                    return f"Task {task.id}:\nTitle: {task.title}\nStatus: {task.status}\nDesc: {task.description}"
                case Err(e):
                    return f"Error: {str(e)}"
