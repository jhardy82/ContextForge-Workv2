"""
Configuration management using Pydantic Settings v2.

This module provides type-safe, validated configuration for the TaskMan API.
Follows 12-Factor App principles with environment-based configuration.

Environment Variables:
    APP_APP_NAME: Application name (default: "TaskMan API")
    APP_ENVIRONMENT: Deployment environment (development/testing/staging/production)
    APP_DATABASE__HOST: Database host (default: localhost)
    APP_DATABASE__PORT: Database port (default: 5432)
    APP_DATABASE__USER: Database user
    APP_DATABASE__PASSWORD: Database password (SecretStr - never logged)
    APP_DATABASE__DATABASE: Database name
    APP_DATABASE__ECHO_SQL: Enable SQL query logging (default: False)
    APP_DATABASE__POOL_SIZE: Connection pool size (default: 10, range: 1-100)
    APP_DATABASE__MAX_OVERFLOW: Max overflow connections (default: 5, range: 0-50)
    APP_REDIS__URL: Redis connection URL (default: redis://localhost:6379)
    APP_REDIS__DB: Redis database number (default: 0)
    APP_SECRET_KEY: Application secret key (min 32 chars)
    APP_JWT_SECRET: JWT signing secret (min 32 chars)

Usage:
    from taskman_api.config import get_settings

    settings = get_settings()  # Cached singleton
    db_url = settings.database.connection_string
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """
    Nested database configuration with validation.

    Supports PostgreSQL connections with automatic connection string generation.
    Password is masked using SecretStr to prevent accidental logging.
    """

    host: str = Field(
        default="localhost",
        description="Database host address",
    )
    port: int = Field(
        default=5432,
        gt=0,
        le=65535,
        description="Database port number (1-65535)",
    )
    user: str = Field(
        min_length=1,
        description="Database username",
    )
    password: SecretStr = Field(
        description="Database password (masked in logs)",
    )
    database: str = Field(
        min_length=1,
        description="Database name",
    )
    sqlite_path: str = Field(
        default="taskman.db",
        description="Path to fallback SQLite database file",
    )

    # Connection pool configuration
    echo_sql: bool = Field(
        default=False,
        description="Enable SQL query logging (disable in production for performance)",
    )
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size (1-100)",
    )
    max_overflow: int = Field(
        default=5,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size (0-50)",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def connection_string(self) -> str:
        """
        Construct PostgreSQL connection string.

        Returns:
            Connection string in format: postgresql://user:password@host:port/database

        Note:
            Password is retrieved from SecretStr but the returned string should
            not be logged directly.
        """
        pwd = self.password.get_secret_value()
        return f"postgresql://{self.user}:{pwd}@{self.host}:{self.port}/{self.database}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_connection_string(self) -> str:
        """
        Construct PostgreSQL async connection string for SQLAlchemy AsyncIO.

        Returns:
            Connection string in format: postgresql+asyncpg://user:password@host:port/database
        """
        pwd = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{pwd}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """
    Redis connection configuration.

    Validates Redis URL format and connection parameters.
    """

    url: str = Field(
        default="redis://localhost:6379",
        pattern=r"^redis://",
        description="Redis connection URL (must start with redis://)",
    )
    timeout: int = Field(
        default=5,
        gt=0,
        le=60,
        description="Connection timeout in seconds (1-60)",
    )
    db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number (0-15)",
    )


class Settings(BaseSettings):
    """
    Enhanced settings with nested configuration.

    Configuration is loaded from:
    1. Constructor arguments (highest priority)
    2. Environment variables (prefixed with APP_)
    3. .env file
    4. Default values (lowest priority)

    Example .env file:
        APP_ENVIRONMENT=production
        APP_DATABASE__HOST=db.example.com
        APP_DATABASE__PORT=5432
        APP_DATABASE__USER=taskman
        APP_DATABASE__PASSWORD=secure_password
        APP_DATABASE__DATABASE=taskman_prod
        APP_DATABASE__ECHO_SQL=false
        APP_DATABASE__POOL_SIZE=20
        APP_DATABASE__MAX_OVERFLOW=10
        APP_REDIS__URL=redis://cache.example.com:6379
        APP_SECRET_KEY=your-secret-key-min-32-chars
        APP_JWT_SECRET=your-jwt-secret-min-32-chars
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # Enables APP_DATABASE__HOST syntax
        env_prefix="APP_",  # All env vars must start with APP_
        case_sensitive=False,
        validate_default=True,  # Validate defaults on instantiation
        extra="forbid",  # Reject unknown environment variables
    )

    # Application metadata
    app_name: str = Field(
        default="TaskMan API",
        description="Application name",
    )
    environment: Literal["development", "testing", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )

    # Nested configurations
    database: DatabaseConfig = Field(
        description="PostgreSQL database configuration",
    )
    redis: RedisConfig | None = Field(
        default=None,
        description="Redis cache configuration (optional)",
    )

    # Security secrets
    secret_key: SecretStr = Field(
        min_length=32,
        description="Application secret key (minimum 32 characters)",
    )
    jwt_secret: SecretStr = Field(
        min_length=32,
        description="JWT signing secret (minimum 32 characters)",
    )

    @field_validator("secret_key", "jwt_secret")
    @classmethod
    def validate_production_secrets(cls, v: SecretStr, info: Any) -> SecretStr:
        """
        Validate that production secrets are not using insecure defaults.

        Args:
            v: Secret value to validate
            info: Validation context with field name and values

        Raises:
            ValueError: If production environment uses insecure default secrets

        Returns:
            Validated secret value
        """
        # Get environment from context (defaults to 'development' if not set)
        environment = info.data.get("environment", "development")

        if environment == "production":
            insecure_patterns = [
                "INSECURE",
                "CHANGE_ME",
                "your-secret",
                "test-key",
                "dev-key",
            ]
            secret_value = v.get_secret_value().lower()

            for pattern in insecure_patterns:
                if pattern.lower() in secret_value:
                    raise ValueError(
                        f"{info.field_name} must be changed from default in production. "
                        f"Detected insecure pattern: {pattern}"
                    )

        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def debug(self) -> bool:
        """Enable debug mode for development and testing."""
        return self.environment in ("development", "testing")


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings singleton.

    Uses @lru_cache to load configuration only once per process.
    This provides ~100x performance improvement over loading .env on every call.

    Returns:
        Settings: Validated configuration singleton

    Raises:
        ValidationError: If configuration is invalid or required values are missing

    Usage:
        from taskman_api.config import get_settings

        settings = get_settings()
        print(settings.app_name)  # "TaskMan API"
        print(settings.database.host)  # "localhost"
        print(settings.database.connection_string)  # postgresql://...

    Note:
        In tests, clear the cache before each test:
            get_settings.cache_clear()
    """
    return Settings()
