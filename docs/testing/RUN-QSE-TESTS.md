# Quick Reference: Running QSE Plugin Tests

## Test Files Created ✓

```
tests/test_qse_compliance.py     - 4.6K (8 tests)
tests/test_qse_db.py            - 8.6K (12 tests)
tests/test_qse_evidence.py      - 7.8K (12 tests)
tests/test_qse_gates.py         - 6.7K (10 tests)
tests/test_qse_integration.py   - 7.7K (8 tests)
tests/test_qse_sessions.py      - 4.2K (6 tests)
```

**Total**: 56 tests across 6 files (39.6K total)

---

## Quick Start Commands

### 1. Run All Tests
```bash
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects"
python -m pytest tests/test_qse*.py -v
```

### 2. Run Tests with Coverage
```bash
python -m pytest tests/test_qse*.py \
  --cov=src/cli_plugins/qse_db \
  --cov=src/cli_plugins/plugin_qse \
  --cov-report=term \
  --cov-report=html
```

### 3. Run Individual Test Files
```bash
# Database layer
python -m pytest tests/test_qse_db.py -v

# Evidence manager
python -m pytest tests/test_qse_evidence.py -v

# Quality gates
python -m pytest tests/test_qse_gates.py -v

# Compliance tracker
python -m pytest tests/test_qse_compliance.py -v

# Session manager
python -m pytest tests/test_qse_sessions.py -v

# Integration tests
python -m pytest tests/test_qse_integration.py -v
```

### 4. Run Specific Test
```bash
python -m pytest tests/test_qse_db.py::test_connect_failure -v
```

### 5. Generate Coverage Report
```bash
# Terminal report
python -m pytest tests/test_qse*.py --cov=src/cli_plugins --cov-report=term

# HTML report (opens in browser)
python -m pytest tests/test_qse*.py --cov=src/cli_plugins --cov-report=html
open htmlcov/index.html
```

---

## Expected Coverage Areas

### QSEDBManager (qse_db.py)
- ✓ Connection management (`connect`, `disconnect`)
- ✓ Evidence operations (`collect_evidence`, `list_evidence`, `get_evidence`)
- ✓ Quality gate operations (`define_gate`, `evaluate_gate`, `list_gates`)
- ✓ Session operations (`create_session`, `end_session`, `list_sessions`)
- ✓ Compliance operations (`check_compliance`, `get_compliance_status`)
- ✓ Hash calculation and file validation

### EvidenceManager (plugin_qse.py)
- ✓ Evidence collection with file copying
- ✓ Session directory creation
- ✓ Evidence validation (file exists, hash matches)
- ✓ Evidence listing and filtering

### QualityGateEngine (plugin_qse.py)
- ✓ Gate definition with validation
- ✓ All operators (>=, <=, =, >, <, !=)
- ✓ Gate evaluation (pass/fail)
- ✓ Gate status and history

### ComplianceTracker (plugin_qse.py)
- ✓ Compliance checking
- ✓ Status retrieval
- ✓ Score calculation
- ✓ Deprecation tracking (YAML)

### SessionManager (plugin_qse.py)
- ✓ Session creation (DB + directory)
- ✓ Session ending with summaries
- ✓ Session listing
- ✓ Session metrics

---

## Test Execution Tips

### Faster Execution
```bash
# Run tests in parallel (requires pytest-xdist)
python -m pytest tests/test_qse*.py -n auto

# Run only failed tests
python -m pytest tests/test_qse*.py --lf

# Stop on first failure
python -m pytest tests/test_qse*.py -x
```

### Detailed Output
```bash
# Show print statements
python -m pytest tests/test_qse*.py -s

# Show local variables on failure
python -m pytest tests/test_qse*.py -l

# Show full diff
python -m pytest tests/test_qse*.py -vv
```

### Filter Tests
```bash
# Run only database tests
python -m pytest tests/test_qse_db.py -v

# Run only tests matching pattern
python -m pytest tests/test_qse*.py -k "evidence" -v

# Run only async tests
python -m pytest tests/test_qse*.py -m asyncio -v
```

---

## Troubleshooting

### Database Connection Issues
If integration tests fail with connection errors:
1. Verify PostgreSQL is running at `172.25.14.122:5432`
2. Check credentials: `contextforge/contextforge`
3. Run unit tests only (skip integration):
   ```bash
   python -m pytest tests/test_qse_db.py tests/test_qse_evidence.py tests/test_qse_gates.py tests/test_qse_compliance.py tests/test_qse_sessions.py -v
   ```

### Fixture Issues
If you see fixture not found errors:
1. Ensure you're running from project root
2. Check conftest.py is in tests/ directory
3. Verify pytest is discovering conftest.py:
   ```bash
   python -m pytest --fixtures tests/
   ```

### Import Errors
If you see import errors for src.cli_plugins:
1. Ensure src/ is in Python path
2. Run from project root directory
3. Check if __init__.py exists in src/cli_plugins/

---

## Coverage Goals

**Target**: 80%+ code coverage

**Critical Paths**:
- Database operations: 90%+
- Evidence management: 85%+
- Quality gates: 85%+
- Compliance tracking: 80%+
- Session management: 80%+

**View Coverage**:
```bash
# Generate and open HTML report
python -m pytest tests/test_qse*.py --cov=src/cli_plugins --cov-report=html
# Then open: htmlcov/index.html
```

---

## Next Steps

1. **Run all tests**: Verify all 56 tests pass
2. **Check coverage**: Ensure 80%+ coverage achieved
3. **Fix any failures**: Address failing tests
4. **Document edge cases**: Note any uncovered scenarios
5. **Integrate CI/CD**: Add to automated test pipeline

---

## Test Maintenance

### Adding New Tests
1. Choose appropriate test file based on component
2. Follow naming convention: `test_<component>_<scenario>`
3. Add `@pytest.mark.asyncio` for async tests
4. Use existing fixtures from conftest.py

### Updating Tests
1. Run affected tests after changes
2. Update test data generators if needed
3. Maintain coverage above 80%
4. Update documentation if test structure changes

---

**Quick Command Copy-Paste**:
```bash
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects" && python -m pytest tests/test_qse*.py --cov=src/cli_plugins --cov-report=term --cov-report=html -v
```

This command will:
- Run all 56 QSE tests
- Generate coverage report for src/cli_plugins
- Show results in terminal
- Create HTML coverage report
- Show verbose output
