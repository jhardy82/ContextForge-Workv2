import logging
from typing import Optional
from uuid import uuid4

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cf_mcp.db import get_db_session
from cf_mcp.models import Sprint
from cf_mcp.schemas import SprintCreate, SprintList, SprintResponse, SprintUpdate

logger = logging.getLogger(__name__)

def register_sprint_tools(mcp: FastMCP):
    """Register sprint management tools with the MCP server."""

    @mcp.tool()
    async def list_sprints(
        ctx: Context,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        project_id: str | None = None
    ) -> SprintList:
        """
        List sprints with pagination and filtering.
        """
        async with get_db_session() as session:
            query = select(Sprint)

            if status:
                query = query.where(Sprint.status == status)
            if project_id:
                query = query.where(Sprint.project_id == project_id)

            # Count total
            count_query = select(func.count()).select_from(query.subquery())
            total = (await session.execute(count_query)).scalar_one()

            # Pagination
            query = query.offset((page - 1) * per_page).limit(per_page)
            query = query.order_by(desc(Sprint.created_at))

            result = await session.execute(query)
            sprints = result.scalars().all()

            return SprintList(
                sprints=[SprintResponse.model_validate(s, from_attributes=True) for s in sprints],
                total=total,
                page=page,
                per_page=per_page,
                has_more=(page * per_page) < total
            )

    @mcp.tool()
    async def create_sprint(
        ctx: Context,
        sprint: SprintCreate
    ) -> SprintResponse:
        """
        Create a new sprint.
        """
        async with get_db_session() as session:
            sprint_data = sprint.model_dump(exclude_unset=True)

            # Generate ID if not provided
            if not sprint_data.get("id"):
                sprint_data["id"] = f"S-{uuid4().hex[:8].upper()}"

            new_sprint = Sprint(**sprint_data)
            session.add(new_sprint)
            await session.commit()
            await session.refresh(new_sprint)

            return SprintResponse.model_validate(new_sprint, from_attributes=True)

    @mcp.tool()
    async def get_sprint(
        ctx: Context,
        sprint_id: str
    ) -> SprintResponse:
        """
        Get a sprint by ID.
        """
        async with get_db_session() as session:
            result = await session.execute(select(Sprint).where(Sprint.id == sprint_id))
            sprint = result.scalar_one_or_none()

            if not sprint:
                raise ValueError(f"Sprint {sprint_id} not found")

            return SprintResponse.model_validate(sprint, from_attributes=True)

    @mcp.tool()
    async def update_sprint(
        ctx: Context,
        sprint_id: str,
        update: SprintUpdate
    ) -> SprintResponse:
        """
        Update an existing sprint.
        """
        async with get_db_session() as session:
            result = await session.execute(select(Sprint).where(Sprint.id == sprint_id))
            sprint_obj = result.scalar_one_or_none()

            if not sprint_obj:
                raise ValueError(f"Sprint {sprint_id} not found")

            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(sprint_obj, key, value)

            await session.commit()
            await session.refresh(sprint_obj)

            return SprintResponse.model_validate(sprint_obj, from_attributes=True)
