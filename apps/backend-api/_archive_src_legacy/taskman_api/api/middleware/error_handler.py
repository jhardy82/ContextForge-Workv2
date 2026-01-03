"""Error handling middleware for FastAPI.

Converts AppError exceptions to RFC 9457 Problem Details responses.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from taskman_api.core.errors import (
    AppError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)


async def error_handler_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Handle errors and convert to RFC 9457 Problem Details.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response with RFC 9457 Problem Details on error
    """
    try:
        response = await call_next(request)
        return response
    except AppError as error:
        # Convert AppError to RFC 9457 Problem Details
        problem_details = error.to_problem_details(instance=str(request.url))
        return JSONResponse(
            status_code=error.status_code, content=problem_details, headers={}
        )
    except Exception as error:
        # Unexpected error - convert to 500 Internal Server Error
        import traceback
        print("\n\n===== UNEXPECTED EXCEPTION =====")
        print(f"Type: {type(error).__name__}")
        print(f"Message: {str(error)}")
        print(f"Traceback:\n{''.join(traceback.format_tb(error.__traceback__))}")
        print("================================\n\n")

        problem_details = {
            "type": "https://api.taskman-v2.local/problems/internal-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(error),
            "instance": str(request.url),
        }
        return JSONResponse(status_code=500, content=problem_details)


def get_status_code_for_error(error: AppError) -> int:
    """Get HTTP status code for error type.

    Args:
        error: AppError instance

    Returns:
        HTTP status code
    """
    error_status_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    return error_status_map.get(type(error), status.HTTP_500_INTERNAL_SERVER_ERROR)
