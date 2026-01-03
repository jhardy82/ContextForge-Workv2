# Backend API Configuration - Quick Reference

**Status**: ✅ Production-Ready | **Coverage**: 100% | **Tests**: 39 passing

---

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Generate secure secrets
python -c "import secrets; print('APP_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('APP_JWT_SECRET=' + secrets.token_urlsafe(32))"

# 3. Edit .env with generated secrets
# Update APP_DATABASE__* settings if needed

# 4. Run tests
pytest

# 5. Verify configuration
python -c "from taskman_api.config import get_settings; print(get_settings())"
```

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `src/taskman_api/config.py` | 243 | Pydantic Settings v2 configuration |
| `src/taskman_api/__init__.py` | 13 | Package exports |
| `tests/conftest.py` | 154 | Shared test fixtures |
| `tests/unit/test_config.py` | 416 | Configuration validation tests |
| `tests/unit/test_fixtures.py` | 117 | Fixture validation tests |
| `.env.example` | 138 | Development template |
| `.env.test` | 64 | Testing environment |
| `.env.production.example` | 255 | Production template |
| `README.md` | 32 | Project documentation |

**Total**: 1,432 lines of production-ready code

---

## Environment Variables

### Required

```bash
APP_ENVIRONMENT=development|testing|staging|production
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5432
APP_DATABASE__USER=taskman
APP_DATABASE__PASSWORD=secure_password
APP_DATABASE__DATABASE=taskman_dev
APP_SECRET_KEY=min-32-characters
APP_JWT_SECRET=min-32-characters
```

### Optional

```bash
APP_REDIS__URL=redis://localhost:6379
APP_REDIS__TIMEOUT=5
APP_REDIS__DB=0
```

---

## Usage Patterns

### Basic Configuration Access

```python
from taskman_api.config import get_settings

settings = get_settings()  # Cached singleton
db_url = settings.database.connection_string
```

### FastAPI Integration

```python
from fastapi import Depends, FastAPI
from taskman_api.config import Settings, get_settings

app = FastAPI()

@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug,
    }
```

### Testing with Fixtures

```python
def test_feature(test_settings: Settings):
    """Use test_settings fixture for isolated testing."""
    assert test_settings.environment == "testing"
    assert test_settings.database.port == 5433  # Isolated port
```

---

## Test Suite

**Coverage**: 100% (62 statements, 6 branches)

### Test Classes

- `TestDatabaseConfig` (7 tests) - Validation, connection strings, defaults
- `TestRedisConfig` (5 tests) - URL patterns, timeouts, DB numbers
- `TestSettings` (11 tests) - Environment validation, security guards
- `TestGetSettings` (2 tests) - Caching behavior
- `TestDatabaseConfigFixture` (2 tests) - Fixture validation
- `TestRedisConfigFixture` (1 test) - Fixture validation
- `TestSettingsFixture` (3 tests) - Complete settings fixtures
- `TestMinimalSettingsFixture` (1 test) - Minimal configuration
- `TestProductionLikeFixture` (3 tests) - Production simulation
- `TestCacheClearFixture` (2 tests) - Cache clearing
- `TestEnvironmentIsolation` (2 tests) - Environment isolation

**Total**: 39 tests, all passing

### Run Tests

```bash
# All tests with coverage
pytest

# Unit tests only
pytest tests/unit/ -v

# With coverage report
pytest --cov=taskman_api --cov-report=html

# Fast fail on first error
pytest -x

# Verbose output
pytest -v --tb=short
```

---

## Code Quality

### Linting (Ruff)

```bash
# Check code
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

### Type Checking (MyPy)

```bash
# Type check config module
mypy src/taskman_api/config.py --strict

# Type check all
mypy src/
```

### Security Scanning (Bandit)

```bash
bandit -r src/
```

---

## Configuration Isolation

### Port Allocation

| Service | Development | Testing | Production |
|---------|-------------|---------|------------|
| PostgreSQL | 5432 | 5433 | 5432 |
| Redis | 6379 (DB 0) | 6379 (DB 15) | 6379 (DB 0) |
| Backend API | 3000 | 3000 | 3000 |

### Environment Separation

- **Development**: `.env` (git-ignored, local only)
- **Testing**: `.env.test` (version-controlled, test-safe values)
- **Production**: `.env.production` (git-ignored, AWS Secrets Manager)

---

## Security Features

### Secret Masking

```python
>>> password = SecretStr("my_password")
>>> print(password)
SecretStr('**********')

>>> password.get_secret_value()  # Explicit retrieval only
'my_password'
```

### Production Guards

Production environment automatically rejects secrets containing:
- `INSECURE`
- `CHANGE_ME`
- `your-secret`
- `test-key`
- `dev-key`

### Validation

- ✅ Minimum 32 characters for all secrets
- ✅ Port range validation (1-65535)
- ✅ Redis timeout validation (1-60 seconds)
- ✅ Redis DB number validation (0-15)
- ✅ Environment literal type checking
- ✅ URL pattern validation
- ✅ Required field validation
- ✅ Extra field rejection (`extra='forbid'`)

---

## Performance

### Caching

`@lru_cache` provides **~100x performance improvement**:

```python
# First call: loads .env + validates
settings1 = get_settings()  # ~5-10ms

# Subsequent calls: cached
settings2 = get_settings()  # ~0.05ms
assert settings1 is settings2  # Same object
```

### Clear Cache (Testing Only)

```python
get_settings.cache_clear()
```

---

## Troubleshooting

### Configuration Validation Errors

```bash
# Check configuration
python -c "from taskman_api.config import get_settings; get_settings()"
```

**Common Errors**:

1. **"String should have at least 32 characters"**
   - Solution: Generate secure keys with `secrets.token_urlsafe(32)`

2. **"Input should be 'development', 'testing', 'staging', or 'production'"**
   - Solution: Use valid environment name in `APP_ENVIRONMENT`

3. **"must be changed from default in production"**
   - Solution: Generate unique secrets for production environment

### Database Connection Issues

```bash
# Test connection
python -c "
from taskman_api.config import get_settings
settings = get_settings()
print(settings.database.connection_string)
"

# Verify PostgreSQL is running
psql -h localhost -p 5432 -U taskman -d taskman_dev -c 'SELECT 1'
```

### Redis Connection Issues

```bash
# Test connection
redis-cli -h localhost -p 6379 ping
# Expected: PONG

# Check specific database
redis-cli -h localhost -p 6379 -n 0 ping
```

---

## Integration Checklist

### Before Backend API Implementation

- [x] Configuration module created
- [x] 100% test coverage achieved
- [x] Type checking passes (mypy --strict)
- [x] Linting passes (ruff check)
- [x] Environment files created
- [x] Fixtures validated
- [x] Security guards tested
- [x] Production templates documented

### For FastAPI Integration

- [ ] Update `main.py` to import `get_settings`
- [ ] Add startup validation event
- [ ] Configure dependency injection
- [ ] Add health check endpoint
- [ ] Test database connection on startup
- [ ] Log configuration on startup

### For Docker Integration

- [ ] Add `.env` to `.dockerignore`
- [ ] Configure `docker-compose.yml` with env_file
- [ ] Override hostnames for Docker network
- [ ] Add health checks for services
- [ ] Test container startup

---

## Next Steps

1. **Phase 2: TypeScript MCP Configuration** (2-3 hours)
   - Update `mcp-server-ts/src/config/schema.ts` with Zod
   - Change port from 3001 → 3000
   - Write Vitest tests

2. **Phase 3: Environment Files** (1-2 hours)
   - Update `.gitignore` with `.env` entries
   - Update root README with configuration docs
   - Create docker-compose.yml

3. **Backend API Implementation** (24-32 hours)
   - Integrate configuration module
   - Implement 22 REST endpoints
   - Write 50+ integration tests

---

## Documentation References

- **Full Implementation**: `CONFIGURATION-PHASE-1-COMPLETE.md`
- **Research Summary**: `../CONFIGURATION-RESEARCH-SUMMARY.md`
- **Strategy Document**: `../CONFIGURATION-STRATEGY.md`
- **Pydantic Settings Docs**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **12-Factor App**: https://12factor.net/config

---

**"Type-Safe Configuration: Validate Early, Fail Fast, Cache Forever"**
