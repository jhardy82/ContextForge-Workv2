"""
Shared pytest fixtures for TaskMan API tests.

This conftest.py provides common fixtures and configuration for all test suites.
"""

import os
from collections.abc import Generator

import pytest
from pydantic import SecretStr

# Validated: Moved imports inside fixtures to prevent early module loading
# from taskman_api.config import DatabaseConfig, RedisConfig, Settings, get_settings


@pytest.fixture(scope="session", autouse=True)
def set_test_environment() -> None:
    """
    Set TEST environment for entire test session.

    This ensures all tests run in testing mode, preventing accidental
    connections to development or production databases.
    """
    os.environ["APP_ENVIRONMENT"] = "testing"


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    """
    Clear settings cache before and after each test.

    This ensures each test gets a fresh configuration instance,
    preventing test pollution from cached settings.

    Usage:
        Automatically applied to all tests via autouse=True.
    """
    from taskman_api.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_database_config() -> "DatabaseConfig":
    from taskman_api.config import DatabaseConfig
    """
    Provide test database configuration.

    Returns:
        DatabaseConfig with test-safe values isolated from development.

    Example:
        >>> def test_connection(test_database_config):
        ...     assert test_database_config.port == 5433  # Isolated port
    """
    return DatabaseConfig(
        host="localhost",
        port=5433,  # Different from dev (5432) for isolation
        user="taskman_test",
        password=SecretStr("test_password_safe"),
        database="taskman_test",
    )


@pytest.fixture
def test_redis_config() -> "RedisConfig":
    from taskman_api.config import RedisConfig
    """
    Provide test Redis configuration.

    Returns:
        RedisConfig with test-safe values isolated from development.

    Example:
        >>> def test_cache(test_redis_config):
        ...     assert test_redis_config.db == 15  # Isolated cache
    """
    return RedisConfig(
        url="redis://localhost:6379",
        timeout=5,
        db=15,  # Different from dev (0) for cache isolation
    )


@pytest.fixture
def test_settings(
    test_database_config: "DatabaseConfig",
    test_redis_config: "RedisConfig",
) -> "Settings":
    from taskman_api.config import Settings
    """
    Provide complete test settings configuration.

    Args:
        test_database_config: Isolated database configuration
        test_redis_config: Isolated Redis configuration

    Returns:
        Settings configured for testing environment

    Example:
        >>> def test_app(test_settings):
        ...     assert test_settings.environment == "testing"
        ...     assert test_settings.debug is True
    """
    return Settings(
        _env_file=None,
        environment="testing",
        database=test_database_config,
        redis=test_redis_config,
        secret_key=SecretStr("test-secret-key-min-32-characters"),
        jwt_secret=SecretStr("test-jwt-secret-min-32-characters"),
    )


@pytest.fixture
def minimal_test_settings() -> "Settings":
    from taskman_api.config import DatabaseConfig, Settings
    """
    Provide minimal test settings without Redis.

    Useful for tests that don't require caching.

    Returns:
        Settings with only required configuration

    Example:
        >>> def test_no_cache(minimal_test_settings):
        ...     assert minimal_test_settings.redis is None
    """
    return Settings(
        _env_file=None,
        environment="testing",
        database=DatabaseConfig(
            host="localhost",
            port=5433,
            user="taskman_test",
            password=SecretStr("test_password"),
            database="taskman_test",
        ),
        redis=None,  # No Redis for minimal tests
        secret_key=SecretStr("test-secret-key-min-32-characters"),
        jwt_secret=SecretStr("test-jwt-secret-min-32-characters"),
    )


@pytest.fixture
def production_like_settings() -> "Settings":
    from taskman_api.config import DatabaseConfig, RedisConfig, Settings
    """
    Provide production-like settings for integration tests.

    Returns:
        Settings configured with production environment constraints

    Example:
        >>> def test_prod_validation(production_like_settings):
        ...     assert production_like_settings.is_production is True
        ...     assert production_like_settings.debug is False
    """
    return Settings(
        environment="production",
        database=DatabaseConfig(
            host="db.example.com",
            port=5432,
            user="taskman_prod",
            password=SecretStr("production_secure_password_123"),
            database="taskman_production",
        ),
        redis=RedisConfig(
            url="redis://cache.example.com:6379",
            timeout=10,
            db=0,
        ),
        secret_key=SecretStr("production-secret-key-min-32-chars"),
        jwt_secret=SecretStr("production-jwt-secret-min-32-chars"),
    )
