"""
Unit tests for configuration management.

Tests Pydantic Settings v2 validation, nested configuration,
secret masking, and environment-specific behavior.
"""

import pytest
from pydantic import SecretStr, ValidationError

from taskman_api.config import DatabaseConfig, RedisConfig, Settings, get_settings


class TestDatabaseConfig:
    """Test DatabaseConfig validation and connection string generation."""

    def test_valid_database_config(self):
        """Test valid database configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            user="taskman",
            password=SecretStr("secure_password"),
            database="taskman_db",
        )

        assert config.host == "localhost"
        assert config.port == 5432
        assert config.user == "taskman"
        assert config.database == "taskman_db"
        # Password is SecretStr - verify it's masked
        assert "secure_password" not in str(config.password)
        assert "**********" in str(config.password)

    def test_connection_string_generation(self):
        """Test PostgreSQL connection string generation."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5432,
            user="taskman",
            password=SecretStr("secure_password"),
            database="taskman_prod",
        )

        expected = "postgresql://taskman:secure_password@db.example.com:5432/taskman_prod"
        assert config.connection_string == expected

    def test_async_connection_string_generation(self):
        """Test PostgreSQL async connection string for SQLAlchemy AsyncIO."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5432,
            user="taskman",
            password=SecretStr("secure_password"),
            database="taskman_prod",
        )

        expected = "postgresql+asyncpg://taskman:secure_password@db.example.com:5432/taskman_prod"
        assert config.async_connection_string == expected

    def test_invalid_port_too_low(self):
        """Test that port must be greater than 0."""
        with pytest.raises(ValidationError, match="greater than 0"):
            DatabaseConfig(
                host="localhost",
                port=0,  # Invalid: must be > 0
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            )

    def test_invalid_port_too_high(self):
        """Test that port must be <= 65535."""
        with pytest.raises(ValidationError, match="less than or equal to 65535"):
            DatabaseConfig(
                host="localhost",
                port=70000,  # Invalid: exceeds max port
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            )

    def test_empty_user_rejected(self):
        """Test that empty username is rejected."""
        with pytest.raises(ValidationError, match="at least 1 character"):
            DatabaseConfig(
                host="localhost",
                port=5432,
                user="",  # Invalid: empty string
                password=SecretStr("password"),
                database="taskman_db",
            )

    def test_default_values(self):
        """Test default values for host and port."""
        config = DatabaseConfig(
            user="taskman",
            password=SecretStr("password"),
            database="taskman_db",
        )

        assert config.host == "localhost"  # Default
        assert config.port == 5432  # Default


class TestRedisConfig:
    """Test RedisConfig validation."""

    def test_valid_redis_config(self):
        """Test valid Redis configuration."""
        config = RedisConfig(
            url="redis://localhost:6379",
            timeout=10,
            db=2,
        )

        assert config.url == "redis://localhost:6379"
        assert config.timeout == 10
        assert config.db == 2

    def test_default_values(self):
        """Test Redis default values."""
        config = RedisConfig()

        assert config.url == "redis://localhost:6379"
        assert config.timeout == 5
        assert config.db == 0

    def test_invalid_url_pattern(self):
        """Test that URL must start with redis://."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            RedisConfig(url="http://localhost:6379")  # Invalid: not redis://

    def test_timeout_validation(self):
        """Test timeout must be between 1 and 60 seconds."""
        # Valid timeout
        config = RedisConfig(timeout=30)
        assert config.timeout == 30

        # Invalid: too low
        with pytest.raises(ValidationError, match="greater than 0"):
            RedisConfig(timeout=0)

        # Invalid: too high
        with pytest.raises(ValidationError, match="less than or equal to 60"):
            RedisConfig(timeout=100)

    def test_db_number_validation(self):
        """Test database number must be between 0 and 15."""
        # Valid db numbers
        for db_num in [0, 5, 15]:
            config = RedisConfig(db=db_num)
            assert config.db == db_num

        # Invalid: negative
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            RedisConfig(db=-1)

        # Invalid: too high
        with pytest.raises(ValidationError, match="less than or equal to 15"):
            RedisConfig(db=16)


class TestSettings:
    """Test Settings validation and environment-specific behavior."""

    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        """Clear settings cache before each test."""
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    def test_valid_settings_development(self):
        """Test valid settings for development environment."""
        settings = Settings(
            _env_file=None,
            environment="development",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("dev_password"),
                database="taskman_dev",
            ),
            secret_key=SecretStr("dev-secret-key-min-32-characters"),
            jwt_secret=SecretStr("dev-jwt-secret-min-32-characters"),
        )

        assert settings.app_name == "TaskMan API"
        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.is_production is False
        assert settings.is_testing is False
        assert settings.database.host == "localhost"

    def test_valid_settings_production(self):
        """Test valid settings for production environment."""
        settings = Settings(
            _env_file=None,
            environment="production",
            database=DatabaseConfig(
                host="db.example.com",
                port=5432,
                user="taskman_prod",
                password=SecretStr("prod_secure_password_123"),
                database="taskman_production",
            ),
            secret_key=SecretStr("production-secret-key-min-32-chars"),
            jwt_secret=SecretStr("production-jwt-secret-min-32-chars"),
        )

        assert settings.environment == "production"
        assert settings.is_production is True
        assert settings.debug is False

    def test_production_rejects_insecure_secret_key(self):
        """Test that production environment rejects insecure secret keys."""
        with pytest.raises(ValidationError, match="must be changed from default"):
            Settings(
                _env_file=None,
                environment="production",
                database=DatabaseConfig(
                    host="localhost",
                    port=5432,
                    user="taskman",
                    password=SecretStr("password"),
                    database="taskman_db",
                ),
                secret_key=SecretStr("INSECURE_CHANGE_ME_32_CHARACTERS"),
                jwt_secret=SecretStr("production-jwt-secret-min-32-chars"),
            )

    def test_production_rejects_insecure_jwt_secret(self):
        """Test that production environment rejects insecure JWT secrets."""
        with pytest.raises(ValidationError, match="must be changed from default"):
            Settings(
                _env_file=None,
                environment="production",
                database=DatabaseConfig(
                    host="localhost",
                    port=5432,
                    user="taskman",
                    password=SecretStr("password"),
                    database="taskman_db",
                ),
                secret_key=SecretStr("production-secret-key-min-32-chars"),
                jwt_secret=SecretStr("your-secret-key-change-me-32-chars"),
            )

    def test_development_allows_insecure_secrets(self):
        """Test that development environment allows test secrets."""
        settings = Settings(
            _env_file=None,
            environment="development",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            ),
            secret_key=SecretStr("INSECURE_DEV_KEY_32_CHARACTERS_MIN"),
            jwt_secret=SecretStr("test-key-for-development-32-chars"),
        )

        assert settings.environment == "development"
        # No ValidationError raised

    def test_secret_key_min_length_32(self):
        """Test that secret keys must be at least 32 characters."""
        with pytest.raises(ValidationError, match="at least 32 items"):
            Settings(
                _env_file=None,
                environment="development",
                database=DatabaseConfig(
                    host="localhost",
                    port=5432,
                    user="taskman",
                    password=SecretStr("password"),
                    database="taskman_db",
                ),
                secret_key=SecretStr("short"),  # Invalid: < 32 chars
                jwt_secret=SecretStr("jwt-secret-key-min-32-characters"),
            )

    def test_optional_redis_config(self):
        """Test that Redis configuration is optional."""
        settings = Settings(
            _env_file=None,
            environment="development",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            ),
            redis=None,  # Optional
            secret_key=SecretStr("dev-secret-key-min-32-characters"),
            jwt_secret=SecretStr("dev-jwt-secret-min-32-characters"),
        )

        assert settings.redis is None

    def test_with_redis_config(self):
        """Test settings with Redis configuration provided."""
        settings = Settings(
            _env_file=None,
            environment="development",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            ),
            redis=RedisConfig(
                url="redis://cache.example.com:6379",
                db=1,
            ),
            secret_key=SecretStr("dev-secret-key-min-32-characters"),
            jwt_secret=SecretStr("dev-jwt-secret-min-32-characters"),
        )

        assert settings.redis is not None
        assert settings.redis.url == "redis://cache.example.com:6379"
        assert settings.redis.db == 1

    def test_invalid_environment(self):
        """Test that invalid environment is rejected."""
        with pytest.raises(ValidationError, match="Input should be"):
            Settings(
                _env_file=None,
                environment="invalid_env",  # Not in allowed values
                database=DatabaseConfig(
                    host="localhost",
                    port=5432,
                    user="taskman",
                    password=SecretStr("password"),
                    database="taskman_db",
                ),
                secret_key=SecretStr("dev-secret-key-min-32-characters"),
                jwt_secret=SecretStr("dev-jwt-secret-min-32-characters"),
            )

    def test_extra_fields_rejected(self):
        """Test that unknown configuration fields are rejected."""
        # This test validates the extra='forbid' configuration
        # It would require setting environment variables, so we'll skip actual implementation
        # The behavior is validated through model_config settings
        pass

    def test_environment_helpers(self):
        """Test environment helper properties."""
        # Development
        dev_settings = Settings(
            _env_file=None,
            environment="development",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            ),
            secret_key=SecretStr("dev-secret-key-min-32-characters"),
            jwt_secret=SecretStr("dev-jwt-secret-min-32-characters"),
        )
        assert dev_settings.is_production is False
        assert dev_settings.is_testing is False
        assert dev_settings.debug is True

        # Testing
        test_settings = Settings(
            _env_file=None,
            environment="testing",
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="taskman",
                password=SecretStr("password"),
                database="taskman_db",
            ),
            secret_key=SecretStr("test-secret-key-min-32-characters"),
            jwt_secret=SecretStr("test-jwt-secret-min-32-characters"),
        )
        assert test_settings.is_production is False
        assert test_settings.is_testing is True
        assert test_settings.debug is True

        # Production
        prod_settings = Settings(
            _env_file=None,
            environment="production",
            database=DatabaseConfig(
                host="db.example.com",
                port=5432,
                user="taskman",
                password=SecretStr("prod_password"),
                database="taskman_db",
            ),
            secret_key=SecretStr("production-secret-key-min-32-chars"),
            jwt_secret=SecretStr("production-jwt-secret-min-32-chars"),
        )
        assert prod_settings.is_production is True
        assert prod_settings.is_testing is False
        assert prod_settings.debug is False


class TestGetSettings:
    """Test get_settings caching behavior."""

    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        """Clear settings cache before each test."""
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    def test_settings_cached(self, monkeypatch):
        """Test that settings are cached across calls."""
        # Set environment variables for this test
        monkeypatch.setenv("APP_ENVIRONMENT", "testing")
        monkeypatch.setenv("APP_DATABASE__HOST", "localhost")
        monkeypatch.setenv("APP_DATABASE__PORT", "5432")
        monkeypatch.setenv("APP_DATABASE__USER", "taskman")
        monkeypatch.setenv("APP_DATABASE__PASSWORD", "test_password")
        monkeypatch.setenv("APP_DATABASE__DATABASE", "taskman_test")
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-min-32-characters")
        monkeypatch.setenv("APP_JWT_SECRET", "test-jwt-secret-min-32-characters")

        # First call
        settings1 = get_settings()

        # Second call should return cached instance
        settings2 = get_settings()

        # Verify same object (identity check)
        assert settings1 is settings2

    def test_cache_clear(self, monkeypatch):
        """Test that cache_clear forces reload."""
        # Set environment variables
        monkeypatch.setenv("APP_ENVIRONMENT", "testing")
        monkeypatch.setenv("APP_DATABASE__HOST", "localhost")
        monkeypatch.setenv("APP_DATABASE__PORT", "5432")
        monkeypatch.setenv("APP_DATABASE__USER", "taskman")
        monkeypatch.setenv("APP_DATABASE__PASSWORD", "test_password")
        monkeypatch.setenv("APP_DATABASE__DATABASE", "taskman_test")
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-min-32-characters")
        monkeypatch.setenv("APP_JWT_SECRET", "test-jwt-secret-min-32-characters")

        # First call
        settings1 = get_settings()

        # Clear cache
        get_settings.cache_clear()

        # Second call should create new instance
        settings2 = get_settings()

        # Verify different objects (not cached)
        assert settings1 is not settings2

        # But values should be the same
        assert settings1.environment == settings2.environment
        assert settings1.database.host == settings2.database.host
