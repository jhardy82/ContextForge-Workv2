"""
Diagnostic route - adds detailed error logging endpoint
"""

import sys
import traceback

from fastapi import APIRouter

router = APIRouter()


@router.get("/debug/error-test")
async def error_test():
    """Test endpoint that captures and returns detailed error info"""
    try:
        from taskman_api.dependencies import ProjectRepo

        # Try to create a test function that uses the repo
        async def test_func(repo: ProjectRepo):
            projects, total = await repo.search(limit=1)
            return {"ok": True, "count": total}

        return {"status": "dependencies_ok", "message": "ProjectRepo imports successfully"}
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "python_path": sys.path,
        }

        # Write to file for analysis
        with open("/app/diagnostic_error.txt", "w") as f:
            f.write(f"Error Type: {error_details['error_type']}\n")
            f.write(f"Error Message: {error_details['error_message']}\n\n")
            f.write(f"Traceback:\n{error_details['traceback']}\n\n")
            f.write(f"Python Path:\n{chr(10).join(sys.path)}")

        return error_details
