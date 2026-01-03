# Pydantic V2 Migration Plan

**Status**: Planned
**Version**: 1.0.0
**Created**: 2025-11-29
**Target Completion**: Sprint 3

---

## Overview

This document outlines the migration plan from Pydantic V1 patterns to Pydantic V2 in the ContextForge codebase. The migration addresses deprecated `@validator`, `@root_validator`, and `class Config` patterns.

---

## Files Requiring Migration

### Priority 1: High-Traffic Files

| File | Line(s) | Pattern | Impact |
|------|---------|---------|--------|
| `cf_cli.py` | 1468, 1480 | `@validator`, `class Config` | Critical - main CLI |
| `python/cf_cli_database_config.py` | 51, 62, 72, 136 | `class Config` (multiple) | High - database config |

### Priority 2: Domain Models

| File | Line(s) | Pattern | Impact |
|------|---------|---------|--------|
| `python/models/*.py` | Various | `class Config` | Medium - data models |
| `cf_core/models/*.py` | Various | `class Config` | Medium - domain models |

### Priority 3: Utility Files

| File | Pattern | Impact |
|------|---------|--------|
| `python/cf_taskman_client.py` | 69 (possible) | Low - API client |
| Other utility scripts | Various | Low |

---

## Migration Patterns

### Pattern 1: `@validator` → `@field_validator`

**Before (V1 - Deprecated):**
```python
from pydantic import BaseModel, validator

class TaskUpdate(BaseModel):
    actual_hours: float | None = None
    
    @validator("actual_hours")
    def validate_actual_hours(cls, v, values):
        if v is not None and v < 0:
            raise ValueError("actual_hours must be non-negative")
        return v
```

**After (V2):**
```python
from pydantic import BaseModel, field_validator, ValidationInfo

class TaskUpdate(BaseModel):
    actual_hours: float | None = None
    
    @field_validator("actual_hours")
    @classmethod
    def validate_actual_hours(cls, v: float | None, info: ValidationInfo) -> float | None:
        if v is not None and v < 0:
            raise ValueError("actual_hours must be non-negative")
        return v
```

**Key Changes:**
1. Import `field_validator` instead of `validator`
2. Add `@classmethod` decorator
3. Use `ValidationInfo` instead of `values` dict
4. Access other field values via `info.data`

---

### Pattern 2: `class Config` → `model_config = ConfigDict(...)`

**Before (V1 - Deprecated):**
```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
```

**After (V2):**
```python
from pydantic import BaseModel, ConfigDict

class DatabaseConfig(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    host: str
    port: int
```

**Key Changes:**
1. Import `ConfigDict` from pydantic
2. Replace `class Config:` with `model_config = ConfigDict(...)`
3. Use keyword arguments instead of class attributes

---

### Pattern 3: `@root_validator` → `@model_validator`

**Before (V1 - Deprecated):**
```python
from pydantic import BaseModel, root_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date
    
    @root_validator
    def validate_date_range(cls, values):
        if values.get("end_date") < values.get("start_date"):
            raise ValueError("end_date must be after start_date")
        return values
```

**After (V2):**
```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date
    
    @model_validator(mode="after")
    def validate_date_range(self) -> "DateRange":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

**Key Changes:**
1. Import `model_validator` instead of `root_validator`
2. Use `mode="after"` (or `mode="before"` for pre-validation)
3. For `mode="after"`, receive `self` not `values`
4. Return `self` for after mode

---

### Pattern 4: Config Option Renames

| V1 Option | V2 Option |
|-----------|-----------|
| `orm_mode = True` | `from_attributes=True` |
| `allow_mutation = False` | `frozen=True` |
| `validate_all = True` | `validate_default=True` |
| `anystr_strip_whitespace` | `str_strip_whitespace` |
| `schema_extra` | `json_schema_extra` |

---

## Specific File Migrations

### cf_cli.py (Lines 1468-1484)

**Current Code:**
```python
@validator("actual_hours")
def validate_actual_hours(cls, v, values):
    # Validation logic
    return v

class Config:
    use_enum_values = True
    validate_assignment = True
```

**Migrated Code:**
```python
from pydantic import field_validator, ValidationInfo, ConfigDict

model_config = ConfigDict(
    use_enum_values=True,
    validate_assignment=True,
)

@field_validator("actual_hours")
@classmethod
def validate_actual_hours(cls, v: float | None, info: ValidationInfo) -> float | None:
    # Validation logic - access other fields via info.data
    return v
```

---

### python/cf_cli_database_config.py

**Migration for each Config class:**

```python
# Before (lines 62, 72, 136)
class SomeModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# After
class SomeModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

---

## Testing Strategy

### Pre-Migration Validation

```bash
# Run full test suite to establish baseline
pytest tests/ -v --tb=short

# Check for Pydantic deprecation warnings
pytest tests/ -v -W error::DeprecationWarning 2>&1 | grep -i pydantic
```

### Post-Migration Validation

```bash
# Run tests with strict deprecation checking
pytest tests/ -v -W error::DeprecationWarning

# Verify no V1 patterns remain
grep -rn "@validator\|@root_validator\|class Config:" --include="*.py" cf_cli.py python/ cf_core/
```

### Migration Checklist

- [ ] Backup original files
- [ ] Migrate `@validator` → `@field_validator`
- [ ] Migrate `@root_validator` → `@model_validator`
- [ ] Migrate `class Config` → `model_config = ConfigDict(...)`
- [ ] Update imports
- [ ] Run type checker: `mypy cf_cli.py python/ --strict`
- [ ] Run test suite: `pytest tests/ -v`
- [ ] Verify no deprecation warnings

---

## Rollback Plan

If migration causes issues:

1. Git revert to pre-migration commit
2. Pin Pydantic to `<2.0.0` in requirements.txt
3. Document specific failures for retry

---

## Timeline

| Phase | Files | Estimated Effort | Target |
|-------|-------|-----------------|--------|
| 1 | `cf_cli.py` | 2 hours | Sprint 3, Day 1 |
| 2 | `cf_cli_database_config.py` | 1 hour | Sprint 3, Day 1 |
| 3 | `python/models/*.py` | 2 hours | Sprint 3, Day 2 |
| 4 | `cf_core/models/*.py` | 2 hours | Sprint 3, Day 2 |
| 5 | Testing & validation | 2 hours | Sprint 3, Day 3 |

**Total Estimated Effort**: 9 hours (2 story points)

---

## Related Documents

- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [docs/09-Development-Guidelines.md](09-Development-Guidelines.md) - Code style standards
- [docs/13-Testing-Validation.md](13-Testing-Validation.md) - Testing requirements

---

**Document Maintainer**: ContextForge Engineering Team  
**Last Updated**: 2025-11-29
