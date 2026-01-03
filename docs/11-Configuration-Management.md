# 11 – Configuration Management

**Status**: Complete
**Version**: 2.1
**Last Updated**: 2025-12-25
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [12-Security-Authentication](12-Security-Authentication.md) | [src/config/README.md](../src/config/README.md)

---

## Overview

ContextForge uses **multi-layered configuration management** with Pydantic Settings for type-safe, environment-aware configuration across Python, PowerShell, and TypeScript components.

### Configuration Philosophy

**Core Principles**:
1. **Secret Refs Only** - No plaintext credentials in source control
2. **Environment Aware** - Dev, staging, production configs
3. **Type Safety** - Pydantic validation with JSON Schema
4. **Hierarchical Loading** - CLI args → Env vars → .env → Defaults
5. **Fail Fast** - Configuration validation at startup

**Constitutional Alignment**:
- **UCL Compliance**: Reproducible configuration across environments
- **Sacred Geometry**: Circle (complete config coverage), Triangle (stability through validation)
- **COF Dimensions**: Infrastructure (config layer), Intent (operational requirements)

---

## Configuration Architecture

### Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  1. CLI Arguments (highest priority)                    │
│     --log-level DEBUG --database-url postgres://...    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. Environment Variables                                │
│     DATABASE_URL, LOG_LEVEL, CORS_ORIGINS              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. .env File                                           │
│     Development convenience, gitignored                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. Default Values                                       │
│     Hardcoded fallbacks in code                         │
└─────────────────────────────────────────────────────────┘
```

### Configuration Domains

| Domain | Purpose | Owner |
|--------|---------|-------|
| **Application** | App metadata, versioning | Platform |
| **Database** | Connection strings, pooling | Infrastructure |
| **Server** | Host, port, workers | Operations |
| **Logging** | Level, format, backends | Observability |
| **Security** | JWT, secrets, CORS | Security |
| **Features** | Feature flags, toggles | Product |
| **Agent** | MCP keys, Client sync secrets | AI/DevEx |

---

## Agent Environment Configuration

### Workspace Root .env

All AI Agents (Claude Desktop, Antigravity) rely on a **centralized** `.env` file in the workspace root (`SCCMScripts/.env`). This file manages secrets that are injected into client configurations via `Sync-McpSettings.ps1`.

**Key Variables**:

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_TOKEN` | Yes | Token for `github` MCP server (Permissions: repo, workflow, user) |
| `MCP_DATABASE_SECRET_KEY` | Yes | Security key for `taskman-v2` database operations |
| `BRAVE_API_KEY` | No | API key for `brave-search` server (if enabled) |
| `TASKMAN_DB_PATH` | No | Override path for TaskMan SQLite DB (Default: `db/taskman.db`) |

> **⚠️ Security**: This file is excluded from git (`.gitignore`). Use `.env.example` as a template.

## Python Configuration (Pydantic Settings)

### TaskMan-v2 Backend Configuration

**File**: `TaskMan-v2/backend-api/config.py`

```python
"""
Configuration management for TaskMan-v2 Backend API
Uses pydantic-settings for environment variable management
"""

from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "TaskMan-v2 Backend API"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"

    # Database (PostgreSQL primary authority)
    database_url: str = (
        "postgresql://contextforge:contextforge@172.25.14.122:5432/taskman_v2"
    )
    database_echo: bool = False  # SQLAlchemy query logging

    # Connection Pooling
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600  # 1 hour

    # CORS - Union type allows both str input (from env) and list output
    cors_origins: Union[str, list[str]] = (
        "http://localhost:5000,http://localhost:3000,http://taskman-v2-frontend:5000"
    )

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Handle CORS_ORIGINS from environment - supports JSON array or CSV."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v.strip() == '':
                return ["http://localhost:5000", "http://localhost:3000"]
            # Try JSON array first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Fall back to comma-separated
            if ',' in v:
                return [origin.strip() for origin in v.split(',') if origin.strip()]
            return [v]
        return ["http://localhost:5000", "http://localhost:3000"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json | text

    # Security
    secret_key: str = "taskman-v2-dev-secret-key-change-in-production"
    jwt_secret: str = "jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Feature Flags
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_swagger: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="null",
    )


# Global settings instance
settings = Settings()
```

**Usage**:

```python
from config import settings

# Database connection
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True
)

# Feature flags
if settings.enable_metrics:
    setup_prometheus_metrics()
```

### CF-Enhanced CLI Configuration

**File**: `cf_core/config/settings.py`

The CLI uses a unified configuration model that strictly adheres to 12-factor app principles.

**Environment Variable Prefix**: `CONTEXTFORGE_`

```python
"""
ContextForge Unified Settings Module.

Provides pydantic-settings based configuration with layered sources:
1. CLI flags (--machine, --output, etc.) - highest priority
2. Environment variables (CONTEXTFORGE_*)
3. Project TOML (.contextforge.toml)
4. User TOML (~/.contextforge/config.toml)
5. Defaults - lowest priority
"""
```

**Key Configuration Sections**:

| Section | Env Var Pattern | Description |
|---------|-----------------|-------------|
| **Core** | `CONTEXTFORGE_MACHINE_MODE` | Enable machine mode (JSON output, no color) |
| **Output** | `CONTEXTFORGE_OUTPUT_*` | Format, color, verbosity settings |
| **Logging** | `CONTEXTFORGE_LOG_*` | Log levels, formats, file paths |
| **Database** | `CONTEXTFORGE_DB_*` | Database connection URL and pooling |
| **MCP** | `CONTEXTFORGE_MCP_*` | Agent protocol settings |
| **Project** | `CONTEXTFORGE_PROJECT_*` | Project root and identity |
| **Trace** | `CONTEXTFORGE_TRACE_*` | OpenTelemetry observability settings |

#### OpenTelemetry Configuration

ContextForge CLI supports OpenTelemetry for performance monitoring and distributed tracing.

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTEXTFORGE_TRACE_ENABLE` | `false` | Enable/disable tracing |
| `CONTEXTFORGE_TRACE_ENDPOINT` | `http://localhost:4317` | OTLP collector endpoint |
| `CONTEXTFORGE_TRACE_SERVICE_NAME` | `contextforge-cli` | Service name for traces |

**Example `.env`**:
```bash
CONTEXTFORGE_OUTPUT_FORMAT=table
CONTEXTFORGE_LOG_LEVEL=INFO
CONTEXTFORGE_DB_URL=sqlite:///db/taskman.db
CONTEXTFORGE_TRACE_ENABLE=true
```

### Inspecting Configuration

You can view the currently effective configuration (merged from all sources) using the CLI:

```bash
# Show safe configuration (secrets redacted)
cf config show

# Show all configuration including secrets
cf config show --show-secrets

# Output as JSON for scripts
cf --machine config show
```

## Database Configuration

### PostgreSQL Connection Management

**File**: `cf_cli_database_config.py`

```python
"""
CF-Enhanced CLI Database Configuration
PostgreSQL Integration with DTM API Support
"""

import os
from typing import Any, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False


class DatabaseConfig:
    """Database configuration with PostgreSQL and DTM API integration."""

    def __init__(self):
        # PostgreSQL Configuration (primary authority)
        self.postgres_host = os.getenv("POSTGRES_HOST", "172.25.14.122")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db = os.getenv("POSTGRES_DB", "taskman_v2")
        self.postgres_user = os.getenv("POSTGRES_USER", "contextforge")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "contextforge")

        # Connection Pooling
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))

        # DTM API Configuration
        self.dtm_api_enabled = os.getenv("DTM_API_ENABLED", "true").lower() == "true"
        self.dtm_api_base_url = os.getenv("DTM_API_BASE_URL", "http://localhost:8000")
        self.dtm_api_key = os.getenv("DTM_API_KEY", "")

        # Fallback Configuration
        postgres_required = os.getenv("POSTGRES_REQUIRED", "false").lower() == "true"
        self.use_postgresql = POSTGRESQL_AVAILABLE or postgres_required
        self.sqlite_path = Path(os.getenv("SQLITE_PATH", "db/trackers.sqlite"))


class DatabaseManager:
    """Database connection manager with PostgreSQL/SQLite support."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._postgres_conn: Any | None = None

    def get_connection(self) -> Any:
        """Get database connection (PostgreSQL preferred, SQLite fallback)."""
        if self.config.use_postgresql:
            return self._get_postgres_connection()
        return self._get_sqlite_connection()

    def get_write_connection(self) -> Any:
        """Get authoritative write connection (PostgreSQL only).

        Raises:
            RuntimeError: If PostgreSQL is unavailable.
        """
        pg_conn = self._get_postgres_connection()
        if pg_conn is None:
            raise RuntimeError(
                "PostgreSQL is required for write operations but is unavailable. "
                "Set POSTGRES_HOST/PORT/DB/USER/PASSWORD environment variables."
            )
        return pg_conn

    def _get_postgres_connection(self) -> Any | None:
        """Get PostgreSQL connection with error handling."""
        if not POSTGRESQL_AVAILABLE:
            logger.warning("PostgreSQL driver not available")
            return None

        try:
            if not self._postgres_conn or self._postgres_conn.closed:
                connection_string = (
                    f"host={self.config.postgres_host} "
                    f"port={self.config.postgres_port} "
                    f"dbname={self.config.postgres_db} "
                    f"user={self.config.postgres_user} "
                    f"password={self.config.postgres_password}"
                )
                self._postgres_conn = psycopg2.connect(
                    connection_string,
                    cursor_factory=RealDictCursor
                )
                logger.info("postgres_connected",
                           host=self.config.postgres_host,
                           database=self.config.postgres_db)
            return self._postgres_conn

        except Exception as e:
            logger.error("postgres_connection_failed", error=str(e))
            return None
```

### SQLAlchemy Engine Configuration

```python
# TaskMan-v2/backend-api/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """Dependency for FastAPI database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Environment Configuration

### .env File Structure

**File**: `TaskMan-v2/backend-api/.env.example`

```bash
# TaskMan-v2 Backend API Configuration
# Copy this file to .env and customize values

# ============================================================================
# APPLICATION
# ============================================================================
APP_NAME=TaskMan-v2 Backend API
APP_VERSION=1.0.0
DEBUG=false

# ============================================================================
# API
# ============================================================================
API_V1_PREFIX=/api/v1

# ============================================================================
# DATABASE (PostgreSQL - Primary Authority)
# ============================================================================
DATABASE_URL=postgresql://contextforge:contextforge@172.25.14.122:5432/taskman_v2
DATABASE_ECHO=false

# Connection Pooling
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============================================================================
# CORS ORIGINS
# ============================================================================
# Comma-separated list or JSON array
CORS_ORIGINS=http://localhost:5000,http://localhost:3000,http://taskman-v2-frontend:5000

# ============================================================================
# SERVER
# ============================================================================
HOST=0.0.0.0
PORT=8000
WORKERS=4

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json

# ============================================================================
# SECURITY
# ============================================================================
# WARNING: Change these in production!
SECRET_KEY=taskman-v2-dev-secret-key-change-in-production
JWT_SECRET=jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_METRICS=true
ENABLE_TRACING=true
ENABLE_SWAGGER=true

# ============================================================================
# EXTERNAL SERVICES (Optional)
# ============================================================================
# Uncomment and configure as needed

# Azure Key Vault
# AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret
# AZURE_TENANT_ID=your-tenant-id

# AWS Secrets Manager
# AWS_REGION=us-east-1
# AWS_SECRET_NAME=taskman-v2-secrets

# Redis Cache
# REDIS_URL=redis://localhost:6379/0
# REDIS_PASSWORD=your-redis-password
```

### Environment-Specific Configurations

#### Development (.env.development)

```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_ECHO=true
ENABLE_SWAGGER=true
CORS_ORIGINS=http://localhost:5000,http://localhost:3000
```

#### Staging (.env.staging)

```bash
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@staging-db.internal:5432/taskman_v2
CORS_ORIGINS=https://staging.contextforge.dev
ENABLE_METRICS=true
ENABLE_TRACING=true
```

#### Production (.env.production)

```bash
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=${DATABASE_URL_FROM_SECRET_MANAGER}
SECRET_KEY=${SECRET_KEY_FROM_VAULT}
JWT_SECRET=${JWT_SECRET_FROM_VAULT}
CORS_ORIGINS=https://contextforge.dev,https://app.contextforge.dev
ENABLE_METRICS=true
ENABLE_TRACING=true
WORKERS=8
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20
```

---

## Secret Management

### Principles

**Core Principle**: "Secret refs only; environment variables or SecretManagement; no plaintext credentials persisted."

1. **Never commit secrets** to source control
2. **Use secret managers** in production (Azure Key Vault, AWS Secrets Manager)
3. **Environment variables** for development
4. **Rotate secrets regularly** (90-day policy)
5. **Least privilege access** to secrets

### Azure Key Vault Integration

**Installation**:

```bash
pip install azure-identity azure-keyvault-secrets
```

**Implementation**:

```python
# backend-api/secrets/azure_secrets.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from config import settings


class AzureSecretManager:
    """Azure Key Vault secret management."""

    def __init__(self):
        self.vault_url = settings.azure_key_vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Azure Key Vault."""
        try:
            secret = self.client.get_secret(secret_name)
            logger.info("secret_retrieved", secret_name=secret_name)
            return secret.value
        except Exception as e:
            logger.error("secret_retrieval_failed",
                        secret_name=secret_name,
                        error=str(e))
            raise

    def set_secret(self, secret_name: str, secret_value: str):
        """Store secret in Azure Key Vault."""
        try:
            self.client.set_secret(secret_name, secret_value)
            logger.info("secret_stored", secret_name=secret_name)
        except Exception as e:
            logger.error("secret_storage_failed",
                        secret_name=secret_name,
                        error=str(e))
            raise


# Usage
azure_secrets = AzureSecretManager()
jwt_secret = azure_secrets.get_secret("jwt-secret")
database_password = azure_secrets.get_secret("database-password")
```

### AWS Secrets Manager Integration

```python
# backend-api/secrets/aws_secrets.py
import boto3
import json
from config import settings


class AWSSecretManager:
    """AWS Secrets Manager integration."""

    def __init__(self):
        self.client = boto3.client(
            'secretsmanager',
            region_name=settings.aws_region
        )

    def get_secret(self, secret_name: str) -> dict:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            logger.info("aws_secret_retrieved", secret_name=secret_name)
            return json.loads(secret_string)
        except Exception as e:
            logger.error("aws_secret_retrieval_failed",
                        secret_name=secret_name,
                        error=str(e))
            raise


# Usage
aws_secrets = AWSSecretManager()
secrets = aws_secrets.get_secret("taskman-v2-secrets")
database_url = secrets["database_url"]
jwt_secret = secrets["jwt_secret"]
```

### PowerShell SecretManagement

```powershell
# Install PowerShell SecretManagement
Install-Module Microsoft.PowerShell.SecretManagement
Install-Module SecretManagement.KeePass

# Register vault
Register-SecretVault -Name ContextForgeVault -ModuleName SecretManagement.KeePass `
    -VaultParameters @{ Path = "C:\Secrets\ContextForge.kdbx" }

# Store secret
Set-Secret -Name DatabasePassword -Secret "secure-password" -Vault ContextForgeVault

# Retrieve secret
$dbPassword = Get-Secret -Name DatabasePassword -Vault ContextForgeVault -AsPlainText

# Use in connection string
$connectionString = "Host=172.25.14.122;Database=taskman_v2;Username=contextforge;Password=$dbPassword"
```

---

## Configuration Validation

### JSON Schema Validation

**File**: `config/schemas/settings_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskMan-v2 Configuration Schema",
  "type": "object",
  "required": ["app_name", "database_url", "secret_key"],
  "properties": {
    "app_name": {
      "type": "string",
      "minLength": 1,
      "description": "Application name"
    },
    "database_url": {
      "type": "string",
      "pattern": "^postgresql://",
      "description": "PostgreSQL connection URL"
    },
    "debug": {
      "type": "boolean",
      "default": false
    },
    "port": {
      "type": "integer",
      "minimum": 1024,
      "maximum": 65535,
      "default": 8000
    },
    "log_level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
      "default": "INFO"
    },
    "cors_origins": {
      "oneOf": [
        {"type": "string"},
        {
          "type": "array",
          "items": {"type": "string", "format": "uri"}
        }
      ]
    },
    "db_pool_size": {
      "type": "integer",
      "minimum": 5,
      "maximum": 100,
      "default": 20
    }
  }
}
```

### Pydantic Validation

```python
from pydantic import BaseSettings, validator, Field, HttpUrl
from typing import List, Union


class Settings(BaseSettings):
    """Validated application settings."""

    app_name: str = Field(..., min_length=1)
    database_url: str = Field(..., regex=r'^postgresql://')
    port: int = Field(default=8000, ge=1024, le=65535)
    log_level: str = Field(default="INFO", regex=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    cors_origins: Union[str, List[HttpUrl]]
    db_pool_size: int = Field(default=20, ge=5, le=100)

    @validator('database_url')
    def validate_database_url(cls, v):
        """Ensure PostgreSQL connection URL is valid."""
        if not v.startswith('postgresql://'):
            raise ValueError('database_url must start with postgresql://')
        if '@' not in v or '/' not in v.split('@')[-1]:
            raise ValueError('database_url must include credentials and database name')
        return v

    @validator('log_level', pre=True)
    def uppercase_log_level(cls, v):
        """Convert log level to uppercase."""
        return v.upper() if isinstance(v, str) else v

    @validator('port')
    def validate_port(cls, v):
        """Ensure port is in valid range."""
        if v < 1024:
            raise ValueError('port must be >= 1024 (unprivileged)')
        if v > 65535:
            raise ValueError('port must be <= 65535')
        return v
```

### Startup Validation

```python
# backend-api/main.py
from config import settings
from services.unified_logger import logger


def validate_configuration():
    """Validate configuration at startup."""
    errors = []

    # Database connectivity
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("config_validation", check="database", status="passed")
    except Exception as e:
        errors.append(f"Database connection failed: {e}")
        logger.error("config_validation", check="database", status="failed", error=str(e))

    # Secret key security
    if settings.secret_key == "taskman-v2-dev-secret-key-change-in-production":
        if not settings.debug:
            errors.append("Production mode requires custom SECRET_KEY")
            logger.error("config_validation", check="secret_key", status="failed")

    # JWT configuration
    if settings.jwt_secret == "jwt-secret-change-in-production":
        if not settings.debug:
            errors.append("Production mode requires custom JWT_SECRET")

    # CORS origins
    if "*" in settings.cors_origins and not settings.debug:
        errors.append("Production mode requires explicit CORS origins (no wildcards)")

    if errors:
        for error in errors:
            logger.error("config_validation_failed", error=error)
        raise RuntimeError(f"Configuration validation failed: {'; '.join(errors)}")

    logger.info("config_validation_complete", status="passed")


@app.on_event("startup")
async def startup_event():
    """Run configuration validation at startup."""
    validate_configuration()
```

---

## Feature Flags & Toggles

### Feature Flag Configuration

```python
# config/feature_flags.py
from pydantic import BaseModel
from typing import Dict


class FeatureFlags(BaseModel):
    """Feature flag configuration."""

    # Observability
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_swagger: bool = True

    # Features
    enable_jwt_auth: bool = False  # P0-005 blocker
    enable_websockets: bool = False
    enable_batch_operations: bool = True
    enable_caching: bool = False

    # Experimental
    enable_ai_suggestions: bool = False
    enable_workflow_designer: bool = False


# Global feature flags
feature_flags = FeatureFlags()


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled."""
    return getattr(feature_flags, f"enable_{feature_name}", False)


# Usage
if is_feature_enabled("jwt_auth"):
    from middleware.auth import setup_jwt_middleware
    setup_jwt_middleware(app)
```

### Runtime Feature Toggle

```python
# backend-api/routes/admin.py
from fastapi import APIRouter, Depends
from config.feature_flags import feature_flags, is_feature_enabled
from dependencies.auth import require_permission

router = APIRouter(prefix="/admin/features")


@router.get("/")
async def list_features():
    """List all feature flags and their status."""
    return feature_flags.dict()


@router.post("/{feature_name}/enable")
async def enable_feature(
    feature_name: str,
    user: dict = Depends(require_permission("admin:features"))
):
    """Enable a feature flag at runtime."""
    if hasattr(feature_flags, f"enable_{feature_name}"):
        setattr(feature_flags, f"enable_{feature_name}", True)
        logger.info("feature_enabled", feature=feature_name, user=user["user_id"])
        return {"feature": feature_name, "enabled": True}
    raise HTTPException(status_code=404, detail="Feature not found")


@router.post("/{feature_name}/disable")
async def disable_feature(
    feature_name: str,
    user: dict = Depends(require_permission("admin:features"))
):
    """Disable a feature flag at runtime."""
    if hasattr(feature_flags, f"enable_{feature_name}"):
        setattr(feature_flags, f"enable_{feature_name}", False)
        logger.info("feature_disabled", feature=feature_name, user=user["user_id"])
        return {"feature": feature_name, "enabled": False}
    raise HTTPException(status_code=404, detail="Feature not found")
```

---

## Multi-Environment Strategy

### Environment Detection

```python
# config/environment.py
import os
from enum import Enum


class Environment(str, Enum):
    """Deployment environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


def get_environment() -> Environment:
    """Detect current environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return Environment(env)


def is_production() -> bool:
    """Check if running in production."""
    return get_environment() == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development."""
    return get_environment() == Environment.DEVELOPMENT


# Usage
from config.environment import is_production, is_development

if is_production():
    # Production-specific behavior
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

if is_development():
    # Development-specific behavior
    app.add_middleware(DebugToolbarMiddleware)
```

### Environment-Specific Loading

```python
# config/__init__.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from .environment import get_environment, Environment


class Settings(BaseSettings):
    """Environment-aware settings."""

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def _get_env_file() -> str:
    """Get environment-specific .env file."""
    env = get_environment()
    env_files = {
        Environment.DEVELOPMENT: ".env.development",
        Environment.STAGING: ".env.staging",
        Environment.PRODUCTION: ".env.production",
        Environment.TEST: ".env.test",
    }

    env_file = env_files.get(env, ".env")
    if Path(env_file).exists():
        return env_file

    # Fallback to default .env
    return ".env"


# Load settings
settings = Settings()
```

---

## Configuration Best Practices

### Security Best Practices

1. **Never commit secrets**:
   ```bash
   # .gitignore
   .env
   .env.*
   !.env.example
   secrets/
   *.pem
   *.key
   ```

2. **Use secret managers in production**:
   ```python
   if is_production():
       from secrets.azure_secrets import AzureSecretManager
       secret_manager = AzureSecretManager()
       settings.jwt_secret = secret_manager.get_secret("jwt-secret")
   ```

3. **Rotate secrets regularly**:
   ```python
   # Implement 90-day rotation policy
   def check_secret_age(secret_name: str) -> bool:
       """Check if secret needs rotation."""
       last_rotation = get_secret_metadata(secret_name)["last_rotation"]
       age_days = (datetime.now() - last_rotation).days
       return age_days > 90
   ```

### Development Best Practices

1. **Provide .env.example**:
   - Include all required variables
   - Use placeholder values
   - Document each variable's purpose

2. **Validate on startup**:
   - Fail fast if configuration is invalid
   - Provide clear error messages
   - Log validation results

3. **Use type-safe configuration**:
   - Leverage Pydantic validation
   - Define clear schemas
   - Enforce constraints

4. **Document configuration**:
   - Inline comments in .env.example
   - Configuration guide in README
   - Schema documentation

### Operational Best Practices

1. **Environment separation**:
   - Separate configs for dev/staging/prod
   - Never mix environment secrets
   - Use namespace prefixes (DEV_, PROD_)

2. **Audit configuration changes**:
   ```python
   def log_config_change(key: str, old_value: str, new_value: str):
       """Audit configuration changes."""
       logger.info("config_changed",
                  key=key,
                  old_value="[REDACTED]" if "secret" in key.lower() else old_value,
                  new_value="[REDACTED]" if "secret" in key.lower() else new_value)
   ```

3. **Monitor configuration drift**:
   - Track configuration versions
   - Alert on unexpected changes
   - Regular configuration audits

---

## Configuration CLI Commands

### View Current Configuration

```bash
# TaskMan-v2 backend
python -m config show

# Output:
# ┌─────────────────────────────────────────────────────────────┐
# │ TaskMan-v2 Backend Configuration                            │
# ├─────────────────────────────────────────────────────────────┤
# │ Environment: development                                     │
# │ Database: postgresql://***@172.25.14.122:5432/taskman_v2   │
# │ Log Level: INFO                                             │
# │ CORS Origins: 3 configured                                  │
# │ Features: metrics=true, tracing=true, swagger=true          │
# └─────────────────────────────────────────────────────────────┘
```

### Validate Configuration

```bash
# Validate current configuration
python -m config validate

# Output:
# ✓ Database connection successful
# ✓ Secret key configured
# ✓ JWT secret configured
# ✓ CORS origins valid
# ✗ Redis connection failed (optional)
#
# Configuration validation: PASSED (1 warning)
```

### Export Configuration Schema

```bash
# Export JSON Schema
python -m config schema --output config/schemas/settings_schema.json

# Generate TypeScript types
python -m config schema --format typescript --output frontend/src/types/config.ts
```

---

## TypeScript Configuration (Frontend)

### Vite Configuration

**File**: `TaskMan-v2/frontend/vite.config.ts`

```typescript
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      port: parseInt(env.VITE_PORT || '5000'),
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      }
    }
  }
})
```

### Environment Variables (Frontend)

**File**: `TaskMan-v2/frontend/.env.example`

```bash
# Vite Frontend Configuration
VITE_APP_NAME=TaskMan-v2 Frontend
VITE_APP_VERSION=1.0.0
VITE_API_BASE_URL=http://localhost:8000
VITE_PORT=5000
VITE_ENABLE_DEVTOOLS=true
```

**Usage**:

```typescript
// src/config/env.ts
export const config = {
  appName: import.meta.env.VITE_APP_NAME,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  enableDevTools: import.meta.env.VITE_ENABLE_DEVTOOLS === 'true',
}

// src/api/client.ts
import { config } from '@/config/env'

const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
})
```

---

## CF_CORE CLI Configuration Module

> **Version**: 1.0.0 | **Added**: 2025-01-XX | **Location**: `src/config/`

The CF_CORE project provides a unified **Pydantic-Settings v2** configuration module for all CLI tools. This module implements type-safe, validated settings with environment variable overrides and thread-safe singleton access.

### Architecture Overview

```
src/config/
├── __init__.py          # Public API exports
├── base.py              # BaseAppSettings foundation class
├── cf_settings.py       # CFSettings for cf_cli.py (CF_CLI_* vars)
├── task_settings.py     # TaskSettings for tasks_cli.py (TASK_* vars)
├── db_settings.py       # DBSettings for dbcli.py (DB_* vars)
└── models.py            # Nested configuration models
```

### Settings Classes

| Class | CLI Tool | Env Prefix | Singleton Accessor |
|-------|----------|------------|-------------------|
| `CFSettings` | `cf_cli.py` | `CF_CLI_` | `get_cf_settings()` |
| `TaskSettings` | `tasks_cli.py` | `TASK_` | `get_task_settings()` |
| `DBSettings` | `dbcli.py` | `DB_` | `get_db_settings()` |

### Performance Characteristics

Performance validated via automated benchmarks (CF-195):

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Cold import | ~597ms | N/A | Module loading (one-time) |
| CFSettings first access | ~12ms | <50ms | ✅ PASS |
| TaskSettings first access | ~13ms | <50ms | ✅ PASS |
| DBSettings first access | ~0.5ms | <50ms | ✅ PASS |
| **Total first-access** | **~25ms** | **<100ms** | ✅ **PASS** |
| Cached access (1000x) | 0.03ms | <1ms | ✅ PASS |

The `@lru_cache` singleton pattern provides ~300,000x speedup for subsequent calls.

### CFSettings (cf_cli.py)

**Environment Prefix**: `CF_CLI_`

**Key Configuration Groups**:

```python
from src.config import get_cf_settings

settings = get_cf_settings()

# Logging configuration
settings.logging.level        # CF_CLI_LOGGING__LEVEL (default: INFO)
settings.logging.format       # CF_CLI_LOGGING__FORMAT (default: rich)
settings.logging.log_dir      # CF_CLI_LOGGING__LOG_DIR

# Database configuration
settings.database.host        # CF_CLI_DATABASE__HOST
settings.database.port        # CF_CLI_DATABASE__PORT
settings.database.name        # CF_CLI_DATABASE__NAME
settings.database.user        # CF_CLI_DATABASE__USER
settings.database.password    # CF_CLI_DATABASE__PASSWORD (SecretStr)

# Evidence bundle settings
settings.evidence.enabled     # CF_CLI_EVIDENCE__ENABLED
settings.evidence.path        # CF_CLI_EVIDENCE__PATH
settings.evidence.hash_algorithm  # CF_CLI_EVIDENCE__HASH_ALGORITHM

# Sacred geometry patterns
settings.sacred_geometry.validate_patterns  # CF_CLI_SACRED_GEOMETRY__VALIDATE_PATTERNS
```

**Environment Variable Example**:
```bash
# Nested settings use double underscore
export CF_CLI_LOGGING__LEVEL=DEBUG
export CF_CLI_DATABASE__HOST=172.25.14.122
export CF_CLI_DATABASE__PASSWORD=secure_password
```

### TaskSettings (tasks_cli.py)

**Environment Prefix**: `TASK_`

**Key Configuration Groups**:

```python
from src.config import get_task_settings

settings = get_task_settings()

# Workflow configuration
settings.workflow.default_priority    # TASK_WORKFLOW__DEFAULT_PRIORITY
settings.workflow.auto_assign_sprint  # TASK_WORKFLOW__AUTO_ASSIGN_SPRINT
settings.workflow.allow_orphan_tasks  # TASK_WORKFLOW__ALLOW_ORPHAN_TASKS

# Tracking configuration
settings.tracking.velocity_enabled    # TASK_TRACKING__VELOCITY_ENABLED
settings.tracking.burndown_enabled    # TASK_TRACKING__BURNDOWN_ENABLED
settings.tracking.analytics_backend   # TASK_TRACKING__ANALYTICS_BACKEND
```

### DBSettings (dbcli.py)

**Environment Prefix**: `DB_`

**Key Configuration Groups**:

```python
from src.config import get_db_settings

settings = get_db_settings()

# Connection configuration
settings.connection.host      # DB_CONNECTION__HOST
settings.connection.port      # DB_CONNECTION__PORT
settings.connection.database  # DB_CONNECTION__DATABASE
settings.connection.username  # DB_CONNECTION__USERNAME
settings.connection.password  # DB_CONNECTION__PASSWORD (SecretStr)

# Connection pool settings
settings.pool.min_size        # DB_POOL__MIN_SIZE (default: 5)
settings.pool.max_size        # DB_POOL__MAX_SIZE (default: 20)
settings.pool.timeout         # DB_POOL__TIMEOUT (default: 30)

# SSL configuration
settings.ssl.enabled          # DB_SSL__ENABLED
settings.ssl.verify           # DB_SSL__VERIFY
settings.ssl.cert_path        # DB_SSL__CERT_PATH
```

**SecretStr for Sensitive Values**:
```python
# DBSettings uses Pydantic SecretStr for passwords
password = settings.connection.password.get_secret_value()  # Returns actual value
print(settings.connection.password)  # Shows "**********" (protected)
```

### Usage in CLI Tools

**Pattern for CLI Integration**:

```python
# cf_cli.py example
from src.config import get_cf_settings

def main():
    settings = get_cf_settings()

    # Configure logging from settings
    setup_logging(
        level=settings.logging.level,
        format=settings.logging.format
    )

    # Use database settings
    if settings.database.host:
        db = connect_database(
            host=settings.database.host,
            port=settings.database.port,
            password=settings.database.password.get_secret_value()
        )
```

### Migration from Legacy Patterns

**Before (os.getenv pattern)**:
```python
# Old pattern - avoid
database_host = os.getenv("POSTGRES_HOST", "localhost")
database_port = int(os.getenv("POSTGRES_PORT", "5432"))
log_level = os.getenv("LOG_LEVEL", "INFO")
```

**After (Pydantic Settings)**:
```python
# New pattern - use this
from src.config import get_cf_settings

settings = get_cf_settings()
database_host = settings.database.host
database_port = settings.database.port
log_level = settings.logging.level
```

**Benefits of Migration**:
1. **Type Safety**: All values are validated at load time
2. **IDE Support**: Full autocomplete and type hints
3. **Centralization**: Single source of truth per CLI tool
4. **Testing**: Easy to override via environment variables
5. **Security**: SecretStr prevents accidental logging of passwords
6. **Performance**: Thread-safe singleton with ~0.03ms cached access

### Environment Files

See `.env.example` at repository root for complete environment variable reference:

- **CF CLI Settings**: 67 environment variables (`CF_CLI_*`)
- **Task Settings**: 26 environment variables (`TASK_*`)
- **DB Settings**: 15 environment variables (`DB_*`)
- **Unified Logging**: 4 environment variables

### Testing Coverage

All settings classes maintain **≥90% test coverage**:

| Module | Coverage | Tests |
|--------|----------|-------|
| `src/config/__init__.py` | 100% | Included |
| `src/config/base.py` | 100% | 12 |
| `src/config/cf_settings.py` | 94.12% | 45 |
| `src/config/task_settings.py` | 95.19% | 52 |
| `src/config/db_settings.py` | 90.58% | 38 |
| `src/config/models.py` | 98.55% | 12 |
| **Total** | **94.42%** | **159** |

---

## PowerShell Configuration

### Configuration Module

**File**: `modules/ContextForge.Configuration/ContextForge.Configuration.psm1`

```powershell
# ContextForge Configuration Management Module

class ContextForgeConfig {
    [string]$Environment
    [string]$LogLevel
    [string]$DatabaseHost
    [int]$DatabasePort
    [hashtable]$Features

    ContextForgeConfig() {
        $this.LoadFromEnvironment()
    }

    [void] LoadFromEnvironment() {
        $this.Environment = $env:CF_ENVIRONMENT ?? 'development'
        $this.LogLevel = $env:CF_LOG_LEVEL ?? 'INFO'
        $this.DatabaseHost = $env:POSTGRES_HOST ?? '172.25.14.122'
        $this.DatabasePort = [int]($env:POSTGRES_PORT ?? '5432')

        $this.Features = @{
            Metrics = ($env:ENABLE_METRICS ?? 'true') -eq 'true'
            Tracing = ($env:ENABLE_TRACING ?? 'true') -eq 'true'
        }
    }

    [void] ApplyToEnvironment() {
        $env:CF_ENVIRONMENT = $this.Environment
        $env:CF_LOG_LEVEL = $this.LogLevel
        $env:POSTGRES_HOST = $this.DatabaseHost
        $env:POSTGRES_PORT = $this.DatabasePort
    }
}

function Get-ContextForgeConfig {
    <#
    .SYNOPSIS
    Get ContextForge configuration.
    #>
    [CmdletBinding()]
    param()

    return [ContextForgeConfig]::new()
}

function Set-ContextForgeConfigValue {
    <#
    .SYNOPSIS
    Set configuration value.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Key,

        [Parameter(Mandatory)]
        [string]$Value
    )

    Set-Item -Path "env:$Key" -Value $Value
    Write-Host "✓ Configuration updated: $Key"
}

Export-ModuleMember -Function Get-ContextForgeConfig, Set-ContextForgeConfigValue
```

---

## Configuration Testing

### Unit Tests

```python
# tests/test_config.py
import pytest
from config import Settings
from pydantic import ValidationError


def test_valid_configuration():
    """Test valid configuration loading."""
    settings = Settings(
        app_name="Test App",
        database_url="postgresql://user:pass@localhost:5432/test",
        secret_key="test-secret-key"
    )
    assert settings.app_name == "Test App"
    assert settings.port == 8000  # Default


def test_invalid_database_url():
    """Test database URL validation."""
    with pytest.raises(ValidationError) as exc:
        Settings(
            app_name="Test",
            database_url="sqlite:///test.db",  # Invalid: requires PostgreSQL
            secret_key="test"
        )
    assert "postgresql://" in str(exc.value)


def test_cors_origins_parsing():
    """Test CORS origins parsing."""
    settings = Settings(
        cors_origins="http://localhost:3000,http://localhost:5000"
    )
    assert len(settings.cors_origins) == 2
    assert "http://localhost:3000" in settings.cors_origins


def test_environment_override():
    """Test environment variable override."""
    import os
    os.environ["LOG_LEVEL"] = "DEBUG"
    settings = Settings()
    assert settings.log_level == "DEBUG"
```

### Integration Tests

```python
# tests/integration/test_config_loading.py
def test_load_development_config():
    """Test loading development configuration."""
    os.environ["ENVIRONMENT"] = "development"
    settings = Settings()
    assert settings.debug is True
    assert "localhost" in settings.database_url


def test_load_production_config():
    """Test loading production configuration."""
    os.environ["ENVIRONMENT"] = "production"
    settings = Settings()
    assert settings.debug is False
    assert settings.secret_key != "taskman-v2-dev-secret-key-change-in-production"
```

---

## Troubleshooting

### Common Issues

#### Issue: Configuration Not Loading

**Symptoms**: Default values used instead of .env file values

**Solutions**:
1. Verify .env file location (same directory as main.py)
2. Check file encoding (must be UTF-8)
3. Ensure no BOM (Byte Order Mark) in .env file
4. Verify environment variable names match exactly (case-insensitive)

```bash
# Debug configuration loading
python -c "from config import settings; print(settings.model_dump())"
```

#### Issue: Secret Manager Connection Failed

**Symptoms**: `AzureCredentialError: Failed to authenticate`

**Solutions**:
1. Verify Azure CLI logged in: `az login`
2. Check service principal credentials
3. Verify Key Vault permissions
4. Validate AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID

```python
# Test Azure connection
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
print(credential.get_token("https://vault.azure.net/.default"))
```

#### Issue: Database Connection Failed

**Symptoms**: `OperationalError: could not connect to server`

**Solutions**:
1. Verify PostgreSQL service running
2. Check network connectivity: `Test-NetConnection 172.25.14.122 -Port 5432`
3. Validate credentials
4. Check firewall rules

```bash
# Test PostgreSQL connection
psql -h 172.25.14.122 -p 5432 -U contextforge -d taskman_v2
```

---

## See Also

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview
- [02-Architecture.md](02-Architecture.md) - Architecture details
- [05-Database-Design-Implementation.md](05-Database-Design-Implementation.md) - Database configuration
- [12-Security-Authentication.md](12-Security-Authentication.md) - Security and secret management

### CF_CORE Settings Module

- [src/config/README.md](../src/config/README.md) - Settings module documentation
- [.env.example](../.env.example) - Complete environment variable reference
- [PYDANTIC-SETTINGS-INTEGRATION-PLAN.md](plans/PYDANTIC-SETTINGS-INTEGRATION-PLAN.md) - Migration plan

### External Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- [Azure Key Vault Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme)
- [AWS Secrets Manager Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)
- [PowerShell SecretManagement](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.secretmanagement/)

---

**Document Status**: Complete ✅
**Authoritative**: Yes
**Next Review**: 2025-04-XX (quarterly)
**Maintained By**: ContextForge Configuration Team

---

*"Configuration is the interface between intent and execution."*
