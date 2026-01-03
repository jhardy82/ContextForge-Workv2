"""Rate limiter configuration for TaskMan-v2 API.

This module defines the global rate limiter instance used across the application.
It's in a separate module to avoid circular imports between main.py and endpoint modules.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global rate limiter instance
# Used by endpoints via decorator pattern: @limiter.limit("10/minute")
limiter = Limiter(key_func=get_remote_address)
