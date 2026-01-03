"""
Context API Router
Exposes Knowledge Graph operations.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from taskman_api.dependencies import ContextRepo
from taskman_api.schemas.context import ContextResolved, ContextResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get("/{identifier}", response_model=ContextResponse | ContextResolved)
async def get_context(
    identifier: str,
    repo: ContextRepo,
    resolve: bool = Query(False, description="Resolve attributes from ancestors"),
):
    """
    Get context by ID or Title.
    If resolve=True, returns merged attributes from ancestry chain.
    """
    target = await repo.get_by_title_or_id(identifier)

    if not target:
        logger.warning("context_not_found", identifier=identifier)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Context '{identifier}' not found"
        )

    if resolve:
        resolved_data = await repo.resolve_context(target.id)
        if not resolved_data:
            raise HTTPException(status_code=404, detail="Failed to resolve context")
        return ContextResolved(**resolved_data)

    return target


@router.get("/tree", tags=["experimental"])
async def get_context_tree(
    repo: ContextRepo, root: str | None = Query(None, description="Root context ID or Title")
):
    """
    Get hierarchy tree.
    Returns: List of nodes with depth and path information.
    """
    root_id = None
    if root:
        node = await repo.get_by_title_or_id(root)
        if node:
            root_id = node.id
        else:
            raise HTTPException(status_code=404, detail=f"Root '{root}' not found")

    tree_nodes = await repo.get_context_tree(root_id)
    return tree_nodes
