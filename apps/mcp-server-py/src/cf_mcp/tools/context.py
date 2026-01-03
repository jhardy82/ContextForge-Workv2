import logging
from typing import Optional
from uuid import uuid4

from mcp.server.fastmcp import Context as MCPContext, FastMCP
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cf_mcp.db import get_db_session
from cf_mcp.models import Context
from cf_mcp.schemas import ContextCreate, ContextList, ContextResponse, ContextUpdate

logger = logging.getLogger(__name__)

def register_context_tools(mcp: FastMCP):
    """Register context management tools with the MCP server."""

    @mcp.tool()
    async def list_contexts(
        ctx: MCPContext,
        page: int = 1,
        per_page: int = 20,
        kind: str | None = None,
        search: str | None = None,
        parent_id: str | None = None
    ) -> ContextList:
        """
        List contexts with pagination and filtering.
        """
        async with get_db_session() as session:
            query = select(Context)

            if kind:
                query = query.where(Context.kind == kind)
            if parent_id:
                query = query.where(Context.parent_id == parent_id)
            if search:
                query = query.where(or_(
                    Context.title.ilike(f"%{search}%"),
                    Context.summary.ilike(f"%{search}%")
                ))

            # Count total
            count_query = select(func.count()).select_from(query.subquery())
            total = (await session.execute(count_query)).scalar_one()

            # Pagination
            query = query.offset((page - 1) * per_page).limit(per_page)
            query = query.order_by(desc(Context.updated_at))

            result = await session.execute(query)
            contexts = result.scalars().all()

            return ContextList(
                contexts=[ContextResponse.model_validate(c, from_attributes=True) for c in contexts],
                total=total,
                page=page,
                per_page=per_page,
                has_more=(page * per_page) < total
            )

    @mcp.tool()
    async def create_context(
        ctx: MCPContext,
        context: ContextCreate
    ) -> ContextResponse:
        """
        Create a new context node.
        """
        async with get_db_session() as session:
            data = context.model_dump(exclude_unset=True)

            # Generate ID if not provided
            if not data.get("id"):
                data["id"] = f"C-{uuid4().hex[:8].upper()}"

            new_context = Context(**data)
            session.add(new_context)
            await session.commit()
            await session.refresh(new_context)

            return ContextResponse.model_validate(new_context, from_attributes=True)

    @mcp.tool()
    async def get_context(
        ctx: MCPContext,
        context_id: str
    ) -> ContextResponse:
        """
        Get a context by ID.
        """
        async with get_db_session() as session:
            result = await session.execute(select(Context).where(Context.id == context_id))
            context = result.scalar_one_or_none()

            if not context:
                raise ValueError(f"Context {context_id} not found")

            return ContextResponse.model_validate(context, from_attributes=True)

    @mcp.tool()
    async def update_context(
        ctx: MCPContext,
        context_id: str,
        update: ContextUpdate
    ) -> ContextResponse:
        """
        Update an existing context.
        """
        async with get_db_session() as session:
            result = await session.execute(select(Context).where(Context.id == context_id))
            context_obj = result.scalar_one_or_none()

            if not context_obj:
                raise ValueError(f"Context {context_id} not found")

            update_data = update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(context_obj, key, value)

            await session.commit()
            await session.refresh(context_obj)

            return ContextResponse.model_validate(context_obj, from_attributes=True)
