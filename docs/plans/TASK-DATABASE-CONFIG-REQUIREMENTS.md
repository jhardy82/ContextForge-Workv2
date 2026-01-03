# TaskSettings Database Configuration Requirements

**Analysis Date**: 2025-12-04
**Analyst**: Database Integration Expert
**Scope**: TASK_DATABASE_URL override mechanism for TaskSettings
**References**: 
- `src/config/db_settings.py` (DBSettings pattern)
- `src/config/task_settings.py` (current implementation)
- `src/cli_plugins/{config,logs,qse}_db.py` (asyncpg usage patterns)
- `dbcli.py`, `tasks_cli.py` (database consumers)

---

## Executive Summary

This document specifies complete database configuration requirements for TaskSettings based on:
1. **Extracted DBSettings patterns** from `db_settings.py` (DATABASE_URL parsing, masking, validation)
2. **Current task_settings.py implementation** (TASK_DATABASE_URL override logic)
3. **AsyncPG usage patterns** from CLI plugin database managers (pool configuration)
4. **Security patterns** (SecretStr, URL masking, password protection)

**Current Status**: `task_settings.py` (lines 293-306) has basic override logic but lacks:
- DBConnectionConfig structured parsing
- URL masking for logs
- Pool configuration settings
- Legacy environment variable bridging

---

## 1. DBSettings Override Pattern Analysis

### Source: `src/config/db_settings.py`

#### 1.1 DBConnectionConfig Class

**Location**: Lines 35-76

```python
class DBConnectionConfig(BaseModel):
    """Database connection configuration.
    
    Attributes:
        database_url: PostgreSQL connection URL
        password: Database password (masked in logs)
    """

    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/taskman_v2",
        description="PostgreSQL connection URL",
    )
    password: SecretStr | None = Field(
        default=None,
        description="Database password (overrides URL password if provided)",
    )

    def get_masked_url(self) -> str:
        """Get connection URL with password masked for safe logging.
        
        Returns:
            URL with password replaced by '***'
        """
        url = self.database_url
        # Simple masking: replace password part in URL
        if "@" in url and "://" in url:
            protocol, rest = url.split("://", 1)
            if "@" in rest:
                creds, host = rest.split("@", 1)
                if ":" in creds:
                    user, _ = creds.split(":", 1)
                    return f"{protocol}://{user}:***@{host}"
        return url

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Normalize database URL format."""
        if not v:
            raise ValueError("database_url cannot be empty")
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("database_url must start with postgresql:// or postgres://")
        return v
```

**Key Features**:
- SecretStr for password field (masked in logs/errors)
- `get_masked_url()` method for safe logging
- URL validation (postgres:// prefix required)
- Support for explicit password override

#### 1.2 DBPoolConfig Class

**Location**: Lines 79-117

```python
class DBPoolConfig(BaseModel):
    """Database connection pool configuration.
    
    Attributes:
        min_size: Minimum number of connections in pool
        max_size: Maximum number of connections in pool
        timeout_seconds: Connection acquisition timeout
    """

    min_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Minimum pool size",
    )
    max_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum pool size",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection acquisition timeout in seconds",
    )

    @model_validator(mode="after")
    def validate_pool_sizes(self) -> "DBPoolConfig":
        """Ensure min_size <= max_size."""
        if self.min_size > self.max_size:
            raise ValueError(
                f"min_size ({self.min_size}) cannot be greater than "
                f"max_size ({self.max_size})"
            )
        return self
```

**Key Features**:
- Bounded pool size (1-50 min, 1-100 max)
- Timeout configuration (1-300 seconds)
- Cross-field validation (min <= max)

#### 1.3 DBSSLConfig Class

**Location**: Lines 120-145

```python
class DBSSLConfig(BaseModel):
    """Database SSL configuration.
    
    Attributes:
        mode: SSL connection mode
    """

    mode: SSLMode = Field(
        default="prefer",
        description="SSL mode for database connections",
    )

    @field_validator("mode")
    @classmethod
    def validate_ssl_mode(cls, v: str) -> str:
        """Validate SSL mode is one of the allowed values."""
        valid_modes = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
        if v not in valid_modes:
            raise ValueError(
                f"Invalid SSL mode: {v}. Must be one of: {', '.join(sorted(valid_modes))}"
            )
        return v
```

**Key Features**:
- SSL mode validation (6 valid options)
- Default: "prefer" (opportunistic SSL)

#### 1.4 Legacy Environment Variable Bridging

**Location**: Lines 195-238 (`bridge_legacy_env_vars`)

```python
@model_validator(mode="before")
@classmethod
def bridge_legacy_env_vars(cls, values: dict) -> dict:
    """Bridge legacy environment variables to new structure.
    
    Maps legacy DBCLI_* and DATABASE_URL variables to new DB_* structure.
    
    Legacy mappings:
        DATABASE_URL -> DB_CONNECTION__DATABASE_URL
        DBCLI_PG_DSN -> DB_CONNECTION__DATABASE_URL
        PG_PASSWORD -> DB_CONNECTION__PASSWORD
        DB_POOL_MIN -> DB_POOL__MIN_SIZE
        DB_POOL_MAX -> DB_POOL__MAX_SIZE
    """
    import os

    # Legacy DATABASE_URL support
    if "DATABASE_URL" in os.environ and "connection" not in values:
        if "connection" not in values:
            values["connection"] = {}
        if isinstance(values["connection"], dict):
            values["connection"]["database_url"] = os.environ["DATABASE_URL"]

    # Legacy DBCLI_PG_DSN support
    if "DBCLI_PG_DSN" in os.environ and "connection" not in values:
        if "connection" not in values:
            values["connection"] = {}
        if isinstance(values["connection"], dict):
            values["connection"]["database_url"] = os.environ["DBCLI_PG_DSN"]

    # Legacy PG_PASSWORD support
    if "PG_PASSWORD" in os.environ:
        if "connection" not in values:
            values["connection"] = {}
        if isinstance(values["connection"], dict):
            values["connection"]["password"] = os.environ["PG_PASSWORD"]

    # Legacy pool size variables
    if "DB_POOL_MIN" in os.environ:
        if "pool" not in values:
            values["pool"] = {}
        if isinstance(values["pool"], dict):
            values["pool"]["min_size"] = int(os.environ["DB_POOL_MIN"])

    if "DB_POOL_MAX" in os.environ:
        if "pool" not in values:
            values["pool"] = {}
        if isinstance(values["pool"], dict):
            values["pool"]["max_size"] = int(os.environ["DB_POOL_MAX"])

    return values
```

**Key Features**:
- Supports legacy DATABASE_URL (global standard)
- Supports legacy DBCLI_PG_DSN (dbcli-specific)
- Supports pool size overrides (DB_POOL_MIN/MAX)
- Password override via PG_PASSWORD

---

## 2. Current tasks_cli.py Database Usage

### Analysis: No Direct AsyncPG Usage Found

**Search Results**: No matches for `asyncpg`, `create_pool`, `pool.acquire` in `tasks_cli.py`

**Implication**: `tasks_cli.py` likely uses:
1. **Synchronous database access** (psycopg2 or similar)
2. **Indirect database access** through imported modules
3. **Environment variable DATABASE_URL** passed to external tools

**Evidence** from grep search:
- Line 330: `db_url = os.environ.get("TASK_DATABASE_URL")`
- Line 335: `os.environ["TASK_DATABASE_URL"] = self.database_url`

**Pattern**: Environment variable passthrough, not direct connection management.

---

## 3. AsyncPG Integration Patterns

### Source: `src/cli_plugins/{config,logs,qse}_db.py`

All three plugin database managers follow identical patterns:

#### 3.1 Connection Pool Creation

**Pattern** (from `config_db.py` line 63, `logs_db.py` line 66, `qse_db.py` line 66):

```python
async def connect(self) -> None:
    """Create connection pool to PostgreSQL."""
    if self._pool is None:
        try:
            self._pool = await asyncpg.create_pool(
                self.conn_str,
                min_size=2,
                max_size=10,
                command_timeout=60  # logs_db.py, qse_db.py only
            )
            self.log("xxx_db_connected", pool_size=10)
        except Exception as e:
            self.log("xxx_db_connection_failed", error=str(e))
            raise XxxDBError(f"Failed to connect to database: {e}") from e
```

**Standard Pool Configuration**:
- `min_size`: 2 connections
- `max_size`: 10 connections
- `command_timeout`: 60 seconds (for long-running queries)

#### 3.2 Connection Pool Usage

**Pattern** (from all three DB managers):

```python
async def get_setting(self, key: str, profile: str = "default") -> Optional[Dict[str, Any]]:
    """Fetch config setting from database."""
    query = """SELECT ... FROM config_settings WHERE key = $1 AND profile = $2"""

    async with self._pool.acquire() as conn:
        row = await conn.fetchrow(query, key, profile)
        # Process result...
```

**Key Features**:
- Context manager for connection acquisition
- Parameterized queries (SQL injection protection)
- Automatic connection return to pool

#### 3.3 Connection Pool Cleanup

**Pattern** (from all three DB managers):

```python
async def disconnect(self) -> None:
    """Close connection pool."""
    if self._pool:
        await self._pool.close()
        self._pool = None
        self.log("xxx_db_disconnected")
```

---

## 4. Environment Variable Precedence

### Current Implementation: `src/config/task_settings.py` Lines 293-306

```python
@model_validator(mode="after")
def override_database_url(self) -> "TaskSettings":
    """
    Override DATABASE_URL if TASK_DATABASE_URL is explicitly set.
    
    This allows task-specific database configuration to take precedence
    over the global CF_DATABASE_URL setting.
    """
    import os
    
    task_db_url = os.environ.get("TASK_DATABASE_URL")
    if task_db_url:
        self.database_url = task_db_url
    
    return self
```

### Required Override Order

**Precedence** (highest to lowest):

1. **TASK_DATABASE_URL** (task-specific override)
2. **DATABASE_URL** (global standard via DBSettings bridging)
3. **CF_DATABASE_URL** (ContextForge global setting)
4. **Default** (`postgresql://localhost:5432/taskman_v2`)

### Enhanced Override Logic

```python
@model_validator(mode="before")
@classmethod
def bridge_task_database_url(cls, values: dict) -> dict:
    """Bridge TASK_DATABASE_URL and DATABASE_URL environment variables.
    
    Precedence:
        1. TASK_DATABASE_URL (task-specific)
        2. DATABASE_URL (global standard)
        3. CF_DATABASE_URL (ContextForge global)
        4. Default value
    """
    import os
    
    # Check for task-specific override first
    task_db_url = os.environ.get("TASK_DATABASE_URL")
    if task_db_url:
        if "database_url" not in values:
            values["database_url"] = task_db_url
        return values
    
    # Fall back to global DATABASE_URL
    global_db_url = os.environ.get("DATABASE_URL")
    if global_db_url:
        if "database_url" not in values:
            values["database_url"] = global_db_url
        return values
    
    # Fall back to CF_DATABASE_URL
    cf_db_url = os.environ.get("CF_DATABASE_URL")
    if cf_db_url:
        if "database_url" not in values:
            values["database_url"] = cf_db_url
    
    return values
```

---

## 5. Security Patterns

### 5.1 SecretStr Usage for Passwords

**Source**: `db_settings.py` Line 47

```python
password: SecretStr | None = Field(
    default=None,
    description="Database password (overrides URL password if provided)",
)
```

**Benefits**:
- Passwords masked in Pydantic repr/str
- Prevents accidental password logging
- `.get_secret_value()` required for access

### 5.2 URL Masking Pattern

**Source**: `db_settings.py` Lines 49-62

```python
def get_masked_url(self) -> str:
    """Get connection URL with password masked for safe logging.
    
    Returns:
        URL with password replaced by '***'
    """
    url = self.database_url
    # Simple masking: replace password part in URL
    if "@" in url and "://" in url:
        protocol, rest = url.split("://", 1)
        if "@" in rest:
            creds, host = rest.split("@", 1)
            if ":" in creds:
                user, _ = creds.split(":", 1)
                return f"{protocol}://{user}:***@{host}"
    return url
```

**Example**:
- Input: `postgresql://user:mypassword@localhost:5432/db`
- Output: `postgresql://user:***@localhost:5432/db`

### 5.3 Connection String Validation

**Source**: `db_settings.py` Lines 64-71

```python
@field_validator("database_url")
@classmethod
def normalize_database_url(cls, v: str) -> str:
    """Normalize database URL format."""
    if not v:
        raise ValueError("database_url cannot be empty")
    if not v.startswith(("postgresql://", "postgres://")):
        raise ValueError("database_url must start with postgresql:// or postgres://")
    return v
```

**Validation Rules**:
- Non-empty string required
- Must start with `postgresql://` or `postgres://`
- No other protocol allowed

---

## 6. Complete Implementation Requirements

### REQUIREMENT 1: DBConnectionConfig for TaskSettings

```python
from pydantic import SecretStr, Field, field_validator
from src.config.models import BaseModel

class TaskDBConnectionConfig(BaseModel):
    """Task-specific database connection configuration.
    
    Attributes:
        database_url: PostgreSQL connection URL
        password: Database password (masked in logs)
    """
    
    database_url: str = Field(
        default="postgresql://localhost:5432/taskman_v2",
        description="PostgreSQL connection URL for task management",
    )
    
    password: SecretStr | None = Field(
        default=None,
        description="Database password (overrides URL password if provided)",
    )
    
    def get_masked_url(self) -> str:
        """Get connection URL with password masked for safe logging.
        
        Returns:
            URL with password replaced by '***'
            
        Example:
            >>> config = TaskDBConnectionConfig(
            ...     database_url="postgresql://user:secret@host:5432/db"
            ... )
            >>> config.get_masked_url()
            'postgresql://user:***@host:5432/db'
        """
        url = self.database_url
        
        # Mask password in URL
        if "@" in url and "://" in url:
            protocol, rest = url.split("://", 1)
            if "@" in rest:
                creds, host = rest.split("@", 1)
                if ":" in creds:
                    user, _ = creds.split(":", 1)
                    return f"{protocol}://{user}:***@{host}"
        
        return url
    
    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Normalize database URL format.
        
        Raises:
            ValueError: If URL is empty or has invalid protocol
        """
        if not v:
            raise ValueError("database_url cannot be empty")
        
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "database_url must start with postgresql:// or postgres://"
            )
        
        return v
```

### REQUIREMENT 2: DBPoolConfig for TaskSettings

```python
from pydantic import Field, model_validator
from src.config.models import BaseModel

class TaskDBPoolConfig(BaseModel):
    """Task-specific database connection pool configuration.
    
    Based on observed patterns from CLI plugin database managers:
    - config_db.py: min=2, max=10
    - logs_db.py: min=2, max=10, timeout=60
    - qse_db.py: min=2, max=10, timeout=60
    
    Attributes:
        min_size: Minimum number of connections in pool
        max_size: Maximum number of connections in pool
        timeout_seconds: Connection acquisition timeout
        command_timeout_seconds: Query execution timeout
    """
    
    min_size: int = Field(
        default=2,
        ge=1,
        le=50,
        description="Minimum pool size (default: 2 based on plugin patterns)",
    )
    
    max_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum pool size (default: 10 based on plugin patterns)",
    )
    
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection acquisition timeout in seconds",
    )
    
    command_timeout_seconds: int = Field(
        default=60,
        ge=1,
        le=600,
        description="Query execution timeout (default: 60 from logs/qse patterns)",
    )
    
    @model_validator(mode="after")
    def validate_pool_sizes(self) -> "TaskDBPoolConfig":
        """Ensure min_size <= max_size.
        
        Raises:
            ValueError: If min_size > max_size
        """
        if self.min_size > self.max_size:
            raise ValueError(
                f"min_size ({self.min_size}) cannot be greater than "
                f"max_size ({self.max_size})"
            )
        return self
```

### REQUIREMENT 3: Enhanced TaskSettings with Database Config

```python
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict
from src.config.base import BaseAppSettings

class TaskSettings(BaseAppSettings):
    """Complete task management configuration with database integration.
    
    Environment Variable Precedence:
        1. TASK_DATABASE_URL (task-specific override)
        2. DATABASE_URL (global standard)
        3. CF_DATABASE_URL (ContextForge global)
        4. Default value
    
    Example:
        >>> settings = get_task_settings()
        >>> 
        >>> # Access connection config
        >>> db_url = settings.db_connection.database_url
        >>> masked = settings.db_connection.get_masked_url()
        >>> 
        >>> # Access pool config
        >>> min_conn = settings.db_pool.min_size
        >>> max_conn = settings.db_pool.max_size
    """
    
    model_config = SettingsConfigDict(
        env_prefix="TASK_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Nested database configuration
    db_connection: TaskDBConnectionConfig = Field(
        default_factory=TaskDBConnectionConfig,
        description="Database connection configuration",
    )
    
    db_pool: TaskDBPoolConfig = Field(
        default_factory=TaskDBPoolConfig,
        description="Connection pool configuration",
    )
    
    # Backward compatibility: expose database_url at root level
    @property
    def database_url(self) -> str:
        """Database URL for backward compatibility."""
        return self.db_connection.database_url
    
    @database_url.setter
    def database_url(self, value: str) -> None:
        """Set database URL (backward compatibility)."""
        self.db_connection.database_url = value
    
    def get_masked_db_url(self) -> str:
        """Get masked database URL for safe logging.
        
        Returns:
            Database URL with password replaced by '***'
        """
        return self.db_connection.get_masked_url()
    
    @model_validator(mode="before")
    @classmethod
    def bridge_task_database_url(cls, values: dict) -> dict:
        """Bridge TASK_DATABASE_URL and DATABASE_URL environment variables.
        
        Precedence:
            1. TASK_DATABASE_URL (task-specific)
            2. DATABASE_URL (global standard)
            3. CF_DATABASE_URL (ContextForge global)
            4. Default value
        
        Environment Variable Mappings:
            - TASK_DATABASE_URL -> db_connection.database_url
            - TASK_DB_CONNECTION__DATABASE_URL (nested)
            - DATABASE_URL -> db_connection.database_url (fallback)
            - CF_DATABASE_URL -> db_connection.database_url (final fallback)
            
            - TASK_DB_POOL__MIN_SIZE -> db_pool.min_size
            - TASK_DB_POOL__MAX_SIZE -> db_pool.max_size
            - TASK_DB_POOL__TIMEOUT_SECONDS -> db_pool.timeout_seconds
            - TASK_DB_POOL__COMMAND_TIMEOUT_SECONDS -> db_pool.command_timeout_seconds
        """
        import os
        
        # Initialize nested dicts if not present
        if "db_connection" not in values:
            values["db_connection"] = {}
        
        # Ensure db_connection is dict (not model instance)
        if not isinstance(values["db_connection"], dict):
            values["db_connection"] = {}
        
        # Check for task-specific override first (highest precedence)
        task_db_url = os.environ.get("TASK_DATABASE_URL")
        if task_db_url and "database_url" not in values["db_connection"]:
            values["db_connection"]["database_url"] = task_db_url
            return values
        
        # Fall back to global DATABASE_URL
        global_db_url = os.environ.get("DATABASE_URL")
        if global_db_url and "database_url" not in values["db_connection"]:
            values["db_connection"]["database_url"] = global_db_url
            return values
        
        # Fall back to CF_DATABASE_URL
        cf_db_url = os.environ.get("CF_DATABASE_URL")
        if cf_db_url and "database_url" not in values["db_connection"]:
            values["db_connection"]["database_url"] = cf_db_url
        
        return values
    
    def apply_to_environment(self) -> None:
        """Export TaskSettings to environment variables for backward compatibility.
        
        Exports:
            - TASK_DATABASE_URL: Database connection string
            - TASK_DB_CONNECTION__DATABASE_URL: Nested form
            - DATABASE_URL: Global standard (for legacy tools)
            - TASK_DB_POOL__MIN_SIZE: Pool minimum
            - TASK_DB_POOL__MAX_SIZE: Pool maximum
            - TASK_DB_POOL__TIMEOUT_SECONDS: Acquisition timeout
            - TASK_DB_POOL__COMMAND_TIMEOUT_SECONDS: Query timeout
        """
        import os
        
        # Export database URL (all forms for compatibility)
        db_url = self.db_connection.database_url
        os.environ["TASK_DATABASE_URL"] = db_url
        os.environ["TASK_DB_CONNECTION__DATABASE_URL"] = db_url
        os.environ["DATABASE_URL"] = db_url  # Global standard
        
        # Export pool configuration
        os.environ["TASK_DB_POOL__MIN_SIZE"] = str(self.db_pool.min_size)
        os.environ["TASK_DB_POOL__MAX_SIZE"] = str(self.db_pool.max_size)
        os.environ["TASK_DB_POOL__TIMEOUT_SECONDS"] = str(self.db_pool.timeout_seconds)
        os.environ["TASK_DB_POOL__COMMAND_TIMEOUT_SECONDS"] = str(self.db_pool.command_timeout_seconds)


@lru_cache
def get_task_settings() -> TaskSettings:
    """Get cached TaskSettings singleton instance.
    
    Returns:
        TaskSettings: Validated task management configuration
    """
    return TaskSettings()


def clear_task_settings_cache() -> None:
    """Clear the task settings cache.
    
    Forces get_task_settings() to reload configuration from environment
    on the next call. Useful for testing.
    """
    get_task_settings.cache_clear()
```

---

## 7. Usage Examples

### Example 1: Basic Database Configuration

```python
from src.config.task_settings import get_task_settings

# Get settings
settings = get_task_settings()

# Access database URL
db_url = settings.database_url  # Backward compatible property
print(f"Database: {settings.get_masked_db_url()}")  # Safe logging

# Access pool configuration
print(f"Pool: {settings.db_pool.min_size}-{settings.db_pool.max_size} connections")
print(f"Timeout: {settings.db_pool.timeout_seconds}s")
```

### Example 2: Environment Variable Precedence

```bash
# .env file
CF_DATABASE_URL=postgresql://cf:pass@localhost:5432/cf_db
DATABASE_URL=postgresql://global:pass@localhost:5432/global_db
TASK_DATABASE_URL=postgresql://task:pass@localhost:5432/task_db

# Python
from src.config.task_settings import get_task_settings
settings = get_task_settings()

# Result: uses TASK_DATABASE_URL (highest precedence)
assert settings.database_url == "postgresql://task:pass@localhost:5432/task_db"
```

### Example 3: AsyncPG Integration

```python
import asyncpg
from src.config.task_settings import get_task_settings

async def create_task_pool():
    """Create AsyncPG pool using TaskSettings configuration."""
    settings = get_task_settings()
    
    pool = await asyncpg.create_pool(
        settings.db_connection.database_url,
        min_size=settings.db_pool.min_size,
        max_size=settings.db_pool.max_size,
        timeout=settings.db_pool.timeout_seconds,
        command_timeout=settings.db_pool.command_timeout_seconds,
    )
    
    return pool
```

### Example 4: Safe Logging

```python
from src.config.task_settings import get_task_settings

settings = get_task_settings()

# ❌ Unsafe: exposes password
print(f"Database: {settings.database_url}")
# Output: postgresql://user:mypassword@host:5432/db

# ✅ Safe: password masked
print(f"Database: {settings.get_masked_db_url()}")
# Output: postgresql://user:***@host:5432/db
```

---

## 8. Testing Requirements

### Unit Tests

```python
import pytest
from src.config.task_settings import TaskSettings, get_task_settings, clear_task_settings_cache

def test_database_url_precedence_task_override(monkeypatch):
    """Test TASK_DATABASE_URL takes precedence over DATABASE_URL."""
    monkeypatch.setenv("CF_DATABASE_URL", "postgresql://cf:5432/cf_db")
    monkeypatch.setenv("DATABASE_URL", "postgresql://global:5432/global_db")
    monkeypatch.setenv("TASK_DATABASE_URL", "postgresql://task:5432/task_db")
    
    clear_task_settings_cache()
    settings = get_task_settings()
    
    assert settings.database_url == "postgresql://task:5432/task_db"


def test_database_url_precedence_database_fallback(monkeypatch):
    """Test DATABASE_URL used when TASK_DATABASE_URL not set."""
    monkeypatch.setenv("CF_DATABASE_URL", "postgresql://cf:5432/cf_db")
    monkeypatch.setenv("DATABASE_URL", "postgresql://global:5432/global_db")
    monkeypatch.delenv("TASK_DATABASE_URL", raising=False)
    
    clear_task_settings_cache()
    settings = get_task_settings()
    
    assert settings.database_url == "postgresql://global:5432/global_db"


def test_database_url_precedence_cf_fallback(monkeypatch):
    """Test CF_DATABASE_URL used when DATABASE_URL not set."""
    monkeypatch.setenv("CF_DATABASE_URL", "postgresql://cf:5432/cf_db")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("TASK_DATABASE_URL", raising=False)
    
    clear_task_settings_cache()
    settings = get_task_settings()
    
    assert settings.database_url == "postgresql://cf:5432/cf_db"


def test_get_masked_url():
    """Test password masking in database URL."""
    settings = TaskSettings(
        db_connection={"database_url": "postgresql://user:secret123@localhost:5432/db"}
    )
    
    masked = settings.get_masked_db_url()
    
    assert masked == "postgresql://user:***@localhost:5432/db"
    assert "secret123" not in masked


def test_pool_size_validation():
    """Test pool size validation (min <= max)."""
    with pytest.raises(ValueError, match="min_size.*cannot be greater than.*max_size"):
        TaskSettings(
            db_pool={"min_size": 20, "max_size": 10}
        )


def test_database_url_validation_empty():
    """Test database URL cannot be empty."""
    with pytest.raises(ValueError, match="database_url cannot be empty"):
        TaskSettings(
            db_connection={"database_url": ""}
        )


def test_database_url_validation_invalid_protocol():
    """Test database URL must be PostgreSQL."""
    with pytest.raises(ValueError, match="must start with postgresql://"):
        TaskSettings(
            db_connection={"database_url": "mysql://localhost:3306/db"}
        )
```

---

## 9. Migration Path

### Phase 1: Add DBConnectionConfig and DBPoolConfig

1. Create `TaskDBConnectionConfig` class with `get_masked_url()`
2. Create `TaskDBPoolConfig` class with validation
3. Add to `task_settings.py` alongside existing fields

### Phase 2: Update TaskSettings

1. Add `db_connection: TaskDBConnectionConfig` field
2. Add `db_pool: TaskDBPoolConfig` field
3. Keep `database_url` property for backward compatibility
4. Update `bridge_task_database_url` validator

### Phase 3: Update Consumers

1. Update `tasks_cli.py` to use `settings.db_connection.database_url`
2. Update logging to use `settings.get_masked_db_url()`
3. Update pool creation to use `settings.db_pool` parameters

### Phase 4: Testing & Validation

1. Unit tests for precedence (TASK > DATABASE > CF > default)
2. Unit tests for masking
3. Unit tests for validation
4. Integration tests with real database
5. Verify backward compatibility with existing code

---

## 10. Summary Checklist

- ✅ **REQUIREMENT 1**: DBConnectionConfig with `get_masked_url()` and validation
- ✅ **REQUIREMENT 2**: DBPoolConfig with min/max/timeout and validation
- ✅ **REQUIREMENT 3**: Enhanced TaskSettings with nested database config
- ✅ **REQUIREMENT 4**: Environment variable precedence (TASK > DATABASE > CF > default)
- ✅ **REQUIREMENT 5**: SecretStr for password fields
- ✅ **REQUIREMENT 6**: URL masking for safe logging
- ✅ **REQUIREMENT 7**: Connection string validation
- ✅ **REQUIREMENT 8**: AsyncPG pool configuration patterns
- ✅ **REQUIREMENT 9**: Backward compatibility (`database_url` property)
- ✅ **REQUIREMENT 10**: `apply_to_environment()` for legacy code bridging

**All database configuration requirements extracted and documented.**
