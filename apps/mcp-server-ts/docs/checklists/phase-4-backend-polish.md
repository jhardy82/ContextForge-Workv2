# Phase 4: Backend API Production Polish

> **Priority**: Low - As time permits
> **Scope**: `backend-api/` directory
> **Prerequisites**: Phases 1-3 complete, MCP server Phase 4 complete

---

## Completed (MCP Server Scope)

- [x] **4.1**: Document Sacred Geometry Validation Rules
  - Created `docs/sacred-geometry-guide.md`
  - Enhanced JSDoc in `src/core/types.ts`
  - Updated README with documentation links
  - Version bumped to 0.1.1

- [x] **4.4**: Registry Submission - *Skipped per user request*

---

## Task 4.2: Convert JSON Fields to JSONB

**Estimated effort**: 4-6 hours
**Impact**: Query performance improvement for JSON field operations

### Checklist

- [ ] **4.2.1**: Identify JSON columns in PostgreSQL schema
  - Run: `\d+ tasks` in psql to find JSON columns
  - Check: `phases`, `execution_trace_log`, `metadata` fields
  - Document: List all JSON columns across tables

- [ ] **4.2.2**: Create Alembic migration
  ```bash
  cd backend-api
  alembic revision --autogenerate -m "convert_json_to_jsonb"
  ```
  - Modify migration to use `ALTER COLUMN ... TYPE JSONB`
  - Include index creation for JSONB fields

- [ ] **4.2.3**: Update SQLAlchemy models
  - Change `JSON` to `JSONB` in model definitions
  - File: `backend-api/app/models/*.py`

- [ ] **4.2.4**: Test migration with rollback
  ```bash
  alembic upgrade head
  alembic downgrade -1
  alembic upgrade head
  ```

- [ ] **4.2.5**: Verify query performance
  - Test GIN index queries on JSONB fields
  - Benchmark before/after for JSON containment queries

---

## Task 4.3: Upgrade mypy to Strict Mode

**Estimated effort**: 8-16 hours
**Impact**: Improved type safety, catch more bugs at compile time

### Checklist

- [ ] **4.3.1**: Review current mypy configuration
  - File: `backend-api/pyproject.toml`
  - Note current settings and ignored errors

- [ ] **4.3.2**: Run mypy with strict flag
  ```bash
  cd backend-api
  uv run mypy src/ --strict 2>&1 | tee mypy-strict-report.txt
  ```
  - Count total errors
  - Categorize by error type

- [ ] **4.3.3**: Fix annotations by module (incremental)
  - Start with: `src/models/` (data structures)
  - Then: `src/repositories/` (data access)
  - Then: `src/services/` (business logic)
  - Finally: `src/api/` (route handlers)

- [ ] **4.3.4**: Add missing type stubs
  ```bash
  uv add types-requests types-python-dateutil  # etc.
  ```
  - Check for stubs: `mypy --install-types`

- [ ] **4.3.5**: Enable strict mode in config
  ```toml
  [tool.mypy]
  strict = true
  ```

- [ ] **4.3.6**: Verify all tests pass
  ```bash
  uv run pytest
  uv run mypy src/
  ```

---

## Success Criteria

- [ ] All JSON columns converted to JSONB with GIN indexes
- [ ] mypy strict mode enabled with zero errors
- [ ] All existing tests continue to pass
- [ ] No performance regressions

---

## Notes

- These tasks are **low priority** and can be done incrementally
- Task 4.2 (JSONB) is a straightforward migration with clear benefits
- Task 4.3 (mypy strict) is more time-consuming but improves code quality
- Both tasks are independent and can be done in any order
