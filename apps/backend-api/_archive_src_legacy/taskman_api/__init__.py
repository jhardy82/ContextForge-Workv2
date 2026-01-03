"""
TaskMan API - Configuration Management Package.

This package provides type-safe configuration management using Pydantic Settings v2.
"""

from taskman_api.config import DatabaseConfig, RedisConfig, Settings, get_settings

__all__ = [
    "DatabaseConfig",
    "RedisConfig",
    "Settings",
    "get_settings",
]

__version__ = "0.1.0"
