from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from taskman_api.dependencies import ContextRepo

# Configure structured logger
logger = structlog.get_logger()

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's chat message")
    context: dict[str, Any] | None = Field(
        default_factory=dict, description="Client-side context (e.g., current page)"
    )


class ChatResponse(BaseModel):
    message: str
    action: str | None = None
    data: dict[str, Any] | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest, context_repo: ContextRepo) -> ChatResponse:
    """
    Handle natural language interactions from the frontend agent.
    Currently implements basic command matching for demonstration.
    """
    logger.info("agent_chat_request", message=request.message, context=request.context)

    msg_lower = request.message.lower()

    try:
        # 1. Project Listing
        if "list projects" in msg_lower or "show projects" in msg_lower:
            # We can re-use the logic from projects router conceptually or call a service
            # For now, let's just return a static response or simulated data
            # Ideally: projects = await project_service.get_all()
            return ChatResponse(
                message="I can help you view your projects. Check the sidebar for the full list.",
                action="navigate",
                data={"view": "projects"},
            )

        # 1.5 Context Navigation
        # "Show me Auth", "Visualize Context", "Go to Authentication"
        if any(kw in msg_lower for kw in ["show me", "visualize", "go to", "explore"]):
            # Extract potential context name
            # "Show me Authentication" -> "Authentication"
            # Simple heuristic: take last words or everything after keyword
            target_name = None
            for kw in ["show me ", "visualize ", "go to ", "explore "]:
                if kw in msg_lower:
                    target_name = request.message[msg_lower.find(kw) + len(kw) :].strip(" .?!")
                    break

            if target_name:
                # Search in DB
                context_node = await context_repo.get_by_title_or_id(target_name)
                if context_node:
                    return ChatResponse(
                        message=f"Navigating to context node: '{context_node.title}'.",
                        action="navigate_context",
                        data={
                            "id": str(context_node.id),
                            "title": context_node.title,
                            "kind": context_node.kind,
                        },
                    )
                else:
                    # If not found, fall through or return suggestions
                    # For now, generic response
                    pass

        # 2. Create Task
        if "create task" in msg_lower or "add task" in msg_lower:
            # Simple extraction strategy
            # "Create task Buy Milk" -> title="Buy Milk"
            parts = request.message.split("task", 1)
            if len(parts) > 1 and parts[1].strip():
                title = parts[1].strip()
                # Mock calling task creation logic
                # new_task = await create_task(TaskCreate(title=title, ...))
                return ChatResponse(
                    message=f"I've drafted a task for you: '{title}'.",
                    action="create_task_draft",
                    data={"title": title},
                )

            return ChatResponse(message="What task would you like me to create?")

        # 3. Default Fallback
        return ChatResponse(
            message=f"I received your message: '{request.message}'. I'm still learning how to process complex requests."
        )

    except Exception as e:
        logger.error("agent_chat_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
