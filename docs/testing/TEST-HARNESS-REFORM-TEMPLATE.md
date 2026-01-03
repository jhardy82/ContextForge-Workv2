---
post_title: "Harness-to-pytest Refactor Template"
author1: "James Hardy"
post_slug: "test-harness-reform-template"
microsoft_alias: "jameshardy"
featured_image: ""
categories: ["Testing", "Quality", "Python"]
tags: ["pytest", "refactor", "fixtures", "parametrize", "quality-gates"]
ai_note: "Drafted with AI assistance; reviewed by engineer"
summary: "Reusable template to convert script-style or harness-structured tests into idiomatic pytest: fixtures, parametrization, assertions, artifact handling via tmp_path, and skip/xfail policies."
post_date: "2025-11-28"
---

## Purpose

Provide a concise, repeatable pattern to convert monolithic or script-style test harnesses (e.g., a `main()` + accumulators + `sys.exit`) into idiomatic pytest with:
- Isolated test functions
- Fixtures for setup/teardown and artifact handling
- Granular assertions (no aggregator dicts)
- Parametrization for scenarios
- Proper use of `pytest.skip` / `pytest.xfail`

## Preconditions

- Pytest 8.x configured; strict marker registration enabled
- `pytest.ini` registers any custom markers used by converted tests
- Avoid global mutable state; prefer fixtures and local variables

## Core Template

### 1) Module Structure

- Imports at top (no side-effect execution)
- No `main()`; no `sys.exit()`; no module-level execution
- Use fixtures and functions only

```python
# tests/unit/example_module_test.py
import json
import pytest

@pytest.fixture
def input_data():
    return {"a": 1, "b": 2}

@pytest.fixture
def artifact_path(tmp_path):
    p = tmp_path / "artifact.json"
    yield p
    # optional: read/validate after test if needed

@pytest.mark.unit
@pytest.mark.parametrize("multiplier,expected", [(1, 3), (2, 6)])
def test_compute_sum(input_data, multiplier, expected):
    result = input_data["a"] + input_data["b"]
    assert result * multiplier == expected

@pytest.mark.unit
def test_write_artifact(input_data, artifact_path):
    artifact_path.write_text(json.dumps(input_data))
    loaded = json.loads(artifact_path.read_text())
    assert loaded == input_data
```

### 2) Skip/Xfail Policies

Use explicit, scoped guards instead of `sys.exit`:

```python
import importlib
import pytest

@pytest.mark.unit
def test_optional_dep_behavior():
    if importlib.util.find_spec("sqlite3") is None:
        pytest.skip("sqlite3 not available")
    # proceed with assertions
```

- Prefer `skip` for missing optional deps or environment constraints
- Use `xfail` when a known bug is tracked and under fix, include `reason` and optional `strict=False`

### 3) Artifact Handling

- Write artifacts only via `tmp_path`/`tmp_path_factory`
- Do not write into repo paths
- Validate artifacts within the same test or a dedicated verification test

### 4) Refactor Checklist

- Remove `main()` and any procedural runners
- Delete `sys.exit(...)` (replace with `pytest.skip/xfail/assert`)
- Split large orchestrations into discrete, testable functions
- Replace accumulator dicts/reports with per-test assertions
- Move file I/O to fixtures using `tmp_path`
- Register any new markers in `pytest.ini`
- Keep each test < 200ms where possible; mark `@pytest.mark.slow` otherwise

## Exemplar Conversion: Achievement Engine

Original symptoms:
- Monolithic class with methods `test_1..test_5`
- Aggregator dict for results and a final recommendation report
- Procedural `main()` calling methods and `sys.exit(code)`

Converted pattern:

```python
# tests/unit/test_achievement_engine.py
import json
import pytest

@pytest.fixture
def engine():
    # Replace with real engine construction or a lightweight stub
    class Engine:
        def calc_score(self, x, y):
            return x + y
        def recommend(self, score):
            return "pass" if score >= 5 else "improve"
    return Engine()

@pytest.fixture
def report_path(tmp_path):
    return tmp_path / "report.json"

@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected", [(2,3,5), (1,1,2)])
def test_calc_score(engine, x, y, expected):
    assert engine.calc_score(x, y) == expected

@pytest.mark.unit
def test_recommend_pass(engine):
    assert engine.recommend(5) == "pass"

@pytest.mark.unit
def test_write_report(engine, report_path):
    score = engine.calc_score(2, 3)
    rec = engine.recommend(score)
    payload = {"score": score, "recommendation": rec}
    report_path.write_text(json.dumps(payload))
    loaded = json.loads(report_path.read_text())
    assert loaded["score"] == 5
    assert loaded["recommendation"] == "pass"
```

## Validation Commands

```powershell
# Collect-only (PowerShell)
pytest --collect-only -q 2>&1 | Select-Object -Last 10

# Run a single module
pytest tests/unit/test_achievement_engine.py -q

# Smoke lane with current temporary exclusions
pytest tests/ -m "unit and not slow" --maxfail=10 `
  --ignore=tests/cf_core/config `
  --ignore=tests/cf_core/models `
  --ignore=tests/cf_core/unit `
  --ignore=tests/unit/temp_duckdb_sqlite_test.py -v --tb=short
```

## Notes & Best Practices

- Keep tests independent; no cross-test shared state
- Prefer parametrization over loops in tests
- Fast feedback first: prioritize unit tests; defer slow/integration behind markers
- Use descriptive assertion messages when complex
- Update documentation as conversions proceed; track reductions in collection errors

## References

- `docs/AAR-QSE-Framework-Complete-20250926.yaml` — test framework decisions
- `docs/AAR-QSE-CF-CLI-COMPREHENSIVE-TESTING-COMPLETE.20251003-0146.md` — CLI testing practices
- `docs/AAR-Phase6-Code-Quality-Excellence-Complete.yaml` — quality gates & metrics
- `docs/AAR-TaskManV2-Phase2-Placeholders-Complete.md` — placeholder/module stub handling
