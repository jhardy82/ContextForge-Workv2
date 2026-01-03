"""Research configuration module"""
from .taskman_v2_config import (
    TASKMAN_V2_CONFIG,
    get_default_config,
    get_postgres_connection_string,
    get_contextforge_connection_string
)

__all__ = [
    "TASKMAN_V2_CONFIG",
    "get_default_config",
    "get_postgres_connection_string",
    "get_contextforge_connection_string"
]
