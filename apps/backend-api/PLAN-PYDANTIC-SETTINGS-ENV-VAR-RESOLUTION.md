# Pydantic Settings Environment Variable Resolution Plan

**Created**: 2025-12-29
**Status**: PLAN READY
**Issue**: 8 config tests failing due to environment variable conflicts
**Root Cause**: `.env` file uses non-prefixed vars, `Settings` class expects `APP_` prefix with `extra="forbid"`

---

## Problem Analysis

### Current State

**`.env` file format** (legacy/simple):
```dotenv
DATABASE_URL=postgresql://contextforge:contextforge@localhost:5434/taskman_v2
API_HOST=0.0.0.0
API_PORT=3001
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

**Settings class expects** (Pydantic v2 nested):
```python
model_config = SettingsConfigDict(
    env_prefix="APP_",
    env_nested_delimiter="__",
    extra="forbid",
)
# Expected: APP_DATABASE__HOST, APP_DATABASE__PORT, etc.
```

### Why Tests Fail

Pydantic Settings v2 reads ALL environment variables matching the prefix, then validates. With `extra="forbid"`, any env var that doesn't map to a defined field causes a validation error.

The `.env` file contains:
- `DATABASE_URL` → Not defined in Settings (no `APP_` prefix)
- `API_HOST` → Not defined in Settings
- `API_PORT` → Not defined in Settings
- `LOG_LEVEL` → Not defined in Settings

But Pydantic sees these as "extra" fields and rejects them.

---

## Resolution Options

### Option A: Migrate `.env` to `APP_` Prefix (Recommended)

**Effort**: 30 min | **Risk**: Low | **Breaking**: Yes (requires downstream updates)

Update `.env` to use proper prefix and nesting:

```dotenv
# TaskMan-v2 Backend API Environment Configuration

# Application
APP_ENVIRONMENT=development
APP_APP_NAME=TaskMan API

# Database (nested with __)
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5434
APP_DATABASE__USER=contextforge
APP_DATABASE__PASSWORD=contextforge
APP_DATABASE__DATABASE=taskman_v2
APP_DATABASE__ECHO_SQL=false
APP_DATABASE__POOL_SIZE=10

# Security
APP_SECRET_KEY=INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION_123
APP_JWT_SECRET=INSECURE_DEV_JWT_CHANGE_IN_PRODUCTION_123

# Redis (optional)
# APP_REDIS__URL=redis://localhost:6379
# APP_REDIS__DB=0

# Logging (if needed - add to Settings class)
# APP_LOG_LEVEL=DEBUG
```

**Pros**:
- Follows Pydantic v2 best practices
- Type-safe nested configuration
- Clear namespacing prevents conflicts

**Cons**:
- Requires updating all deployments
- Legacy scripts using `DATABASE_URL` break

---

### Option B: Change Settings to `extra="ignore"` (Quick Fix)

**Effort**: 5 min | **Risk**: Medium | **Breaking**: No

```python
model_config = SettingsConfigDict(
    env_prefix="APP_",
    env_nested_delimiter="__",
    extra="ignore",  # Changed from "forbid"
)
```

**Pros**:
- Minimal code change
- Backward compatible

**Cons**:
- Silent failures for typos in env var names
- Loses strict validation
- Doesn't solve the `DATABASE_URL` usage problem

---

### Option C: Hybrid Approach - Add Legacy Fields (Balanced)

**Effort**: 1 hr | **Risk**: Low | **Breaking**: No

Add optional fields for legacy env vars, with computed properties that prefer Settings values:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="ignore",  # Allow legacy vars
    )

    # New: Legacy compatibility fields (no prefix)
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    api_host: str | None = Field(default=None, alias="API_HOST")
    api_port: int | None = Field(default=None, alias="API_PORT")
    log_level: str | None = Field(default=None, alias="LOG_LEVEL")

    # Existing nested config
    database: DatabaseConfig = Field(...)

    @computed_field
    @property
    def effective_database_url(self) -> str:
        """Prefer nested config, fallback to DATABASE_URL."""
        if self.database:
            return self.database.connection_string
        return self.database_url or ""
```

**Pros**:
- Backward compatible with existing `.env`
- Gradual migration path
- Explicit about legacy support

**Cons**:
- More complex code
- Two ways to configure same thing

---

### Option D: Separate Settings Class for Tests

**Effort**: 30 min | **Risk**: Low | **Breaking**: No

Create a test-specific settings class that doesn't conflict:

```python
# In conftest.py
@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove conflicting env vars for tests."""
    for var in ["DATABASE_URL", "API_HOST", "API_PORT", "LOG_LEVEL"]:
        monkeypatch.delenv(var, raising=False)
```

**Pros**:
- Tests isolated from system env
- No production code changes

**Cons**:
- Doesn't fix actual `.env` file issues
- Masks the real problem

---

## Recommended Implementation: Option A

### Step 1: Update `.env` File

```dotenv
# TaskMan-v2 Backend API Environment Configuration
# Updated: 2025-12-29 to use Pydantic v2 nested format

# Application Settings
APP_ENVIRONMENT=development
APP_APP_NAME=TaskMan API

# Database Configuration (PostgreSQL)
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5434
APP_DATABASE__USER=contextforge
APP_DATABASE__PASSWORD=contextforge
APP_DATABASE__DATABASE=taskman_v2
APP_DATABASE__ECHO_SQL=false
APP_DATABASE__POOL_SIZE=10
APP_DATABASE__MAX_OVERFLOW=5

# Security (CHANGE IN PRODUCTION!)
APP_SECRET_KEY=INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION_123
APP_JWT_SECRET=INSECURE_DEV_JWT_CHANGE_IN_PRODUCTION_123

# Redis (optional - uncomment to enable)
# APP_REDIS__URL=redis://localhost:6379
# APP_REDIS__DB=0
```

### Step 2: Update `.env.example`

Create/update `.env.example` with the new format for documentation.

### Step 3: Add Optional LOG_LEVEL Field

If log level configuration is needed, add to Settings:

```python
log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
    default="INFO",
    description="Application log level",
)
```

### Step 4: Update Tests

The tests should work after `.env` migration. Verify:

```bash
pytest tests/unit/test_config.py -v
```

### Step 5: Update Documentation

Update README and deployment docs with new env var format.

### Step 6: Update `Invoke-TaskManStack.ps1`

Check if the stack startup script sets environment variables.

---

## Migration Checklist

- [ ] Backup current `.env` file
- [ ] Update `.env` to `APP_` prefix format
- [ ] Create/update `.env.example`
- [ ] Add `log_level` field if needed
- [ ] Run config tests: `pytest tests/unit/test_config.py`
- [ ] Run full test suite: `pytest`
- [ ] Update `Invoke-TaskManStack.ps1` if needed
- [ ] Update Docker Compose env vars if applicable
- [ ] Update README.md with new configuration format
- [ ] Commit changes

---

## Test Fix Preview

After implementing Option A, the test errors should resolve:

| Test | Before | After |
|------|--------|-------|
| `test_valid_settings_development` | ❌ extra_forbidden | ✅ PASS |
| `test_valid_settings_production` | ❌ extra_forbidden | ✅ PASS |
| `test_development_allows_insecure_secrets` | ❌ extra_forbidden | ✅ PASS |
| `test_optional_redis_config` | ❌ extra_forbidden | ✅ PASS |
| `test_with_redis_config` | ❌ extra_forbidden | ✅ PASS |
| `test_environment_helpers` | ❌ extra_forbidden | ✅ PASS |
| `test_settings_cached` | ❌ extra_forbidden | ✅ PASS |
| `test_cache_clear` | ❌ extra_forbidden | ✅ PASS |

---

## Estimated Effort

| Task | Time |
|------|------|
| Update `.env` file | 10 min |
| Create `.env.example` | 5 min |
| Add `log_level` field (optional) | 10 min |
| Test verification | 5 min |
| Documentation updates | 15 min |
| **Total** | **45 min** |

---

**Prepared by**: Cognitive Architect
**Approval Required**: Before modifying production configurations
