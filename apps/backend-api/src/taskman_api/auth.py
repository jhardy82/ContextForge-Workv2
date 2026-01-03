"""
Authentication & Authorization Module
JWT Bearer token validation and user context extraction.
Implements ADR-020 security architecture for ActionList endpoints.
"""

import os
from datetime import datetime, timedelta
from typing import Any

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = structlog.get_logger()

# ============================================================================
# Configuration
# ============================================================================
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()


# ============================================================================
# User Model
# ============================================================================
class User:
    """User context extracted from JWT token."""

    def __init__(
        self,
        user_id: str,
        email: str,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
    ):
        self.user_id = user_id
        self.email = email
        self.roles = roles or []
        self.permissions = permissions or []

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return "admin" in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "roles": self.roles,
            "permissions": self.permissions,
        }


# ============================================================================
# JWT Token Operations
# ============================================================================
def create_access_token(data: dict[str, Any]) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data (must include 'sub' for user_id)

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token({
            "sub": "user-123",
            "email": "user@example.com",
            "roles": ["user"],
            "permissions": ["read", "write"]
        })
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update(
        {
            "exp": expire,
            "iss": "taskman-v2",
            "aud": "taskman-api",
        }
    )

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(
        "access_token_created", user_id=data.get("sub"), expires_in_hours=JWT_EXPIRATION_HOURS
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience="taskman-api")
        return payload
    except JWTError as e:
        logger.warning("token_verification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# ============================================================================
# FastAPI Dependencies
# ============================================================================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    FastAPI dependency that extracts current user from JWT token.

    Usage:
        @router.get("/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.user_id}

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User object with user_id, email, roles, permissions

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Security:
        - Validates JWT signature using HS256 algorithm
        - Checks token expiration
        - Verifies issuer and audience claims
        - Extracts user context from 'sub', 'email', 'roles', 'permissions' claims
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Extract user context from JWT payload
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        logger.warning("token_missing_subject", payload=payload)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User(
        user_id=user_id,
        email=email or "unknown@example.com",
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
    )

    logger.info("user_authenticated", user_id=user_id, email=user.email, roles=user.roles)
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency that requires admin role.

    Usage:
        @router.delete("/admin-only")
        async def admin_endpoint(admin: User = Depends(get_current_admin_user)):
            return {"message": "Admin access granted"}

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object if user has admin role

    Raises:
        HTTPException: 403 if user does not have admin role
    """
    if not current_user.is_admin():
        logger.warning(
            "admin_access_denied",
            user_id=current_user.user_id,
            roles=current_user.roles,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    logger.info("admin_access_granted", user_id=current_user.user_id)
    return current_user


# ============================================================================
# Authorization Helpers
# ============================================================================
def check_ownership(resource_user_id: str, current_user: User) -> None:
    """
    Validate that current user owns the resource or is admin.

    Args:
        resource_user_id: User ID that owns the resource
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if user does not own resource and is not admin

    Example:
        check_ownership(action_list.user_id, current_user)
    """
    if resource_user_id != current_user.user_id and not current_user.is_admin():
        logger.warning(
            "ownership_validation_failed",
            resource_owner=resource_user_id,
            requesting_user=current_user.user_id,
            is_admin=current_user.is_admin(),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this resource",
        )

    # Log admin override access
    if resource_user_id != current_user.user_id and current_user.is_admin():
        logger.warning(
            "admin_ownership_override",
            resource_owner=resource_user_id,
            admin_user=current_user.user_id,
        )
