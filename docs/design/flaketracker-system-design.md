# FlakeTracker System Design

**Phase**: 2 O1 | **Version**: 1.0.0
**Author**: Reliability Engineer (FlakeTracker Persona)
**Date**: 2025-11-25
**Status**: DESIGN COMPLETE - Ready for Implementation

---

## Executive Summary

FlakeTracker is a SQLite-based system for systematic flake detection and quarantine management. It targets the Phase 2 O1 requirement of achieving <5% flake rate with automated quarantine for tests exceeding 20% flake rate.

### Key Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Overall Flake Rate | <5% | Rolling 100-run window |
| Quarantine Threshold | >20% | Per-test flake rate |
| Reintegration Threshold | <5% over 100 runs | Quarantine environment |
| Confidence Minimum | 30 samples | Statistical significance |

---

## 1. SQLite Schema Design

### 1.1 Entity-Relationship Overview

```
┌─────────────────┐       ┌────────────────────┐
│  test_identity  │───1:N─│  execution_history │
└────────┬────────┘       └────────────────────┘
         │
         │1:1
         ▼
┌─────────────────┐       ┌────────────────────┐
│  flake_metrics  │       │ quarantine_status  │
└─────────────────┘       └────────────────────┘
         ▲                         │
         │         1:N             │
         └─────────────────────────┘
```

### 1.2 DDL Statements

```sql
-- =============================================================================
-- FlakeTracker Schema v1.0.0
-- Target: SQLite 3.35+ (for RETURNING clause support)
-- =============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- -----------------------------------------------------------------------------
-- TABLE: test_identity
-- Purpose: Master registry of all tracked tests with decomposed identity
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS test_identity (
    test_id         TEXT PRIMARY KEY,           -- SHA-256 hash of nodeid for stability
    nodeid          TEXT UNIQUE NOT NULL,       -- Full pytest nodeid (e.g., tests/test_foo.py::TestClass::test_method)
    file_path       TEXT NOT NULL,              -- Relative path from project root
    module_name     TEXT NOT NULL,              -- Python module name (dots notation)
    class_name      TEXT,                       -- Test class name (NULL if not in class)
    function_name   TEXT NOT NULL,              -- Test function/method name
    parametrize_id  TEXT,                       -- Parametrize suffix (e.g., [param1-param2])
    first_seen      TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen       TEXT NOT NULL DEFAULT (datetime('now')),
    is_active       INTEGER NOT NULL DEFAULT 1  -- Soft delete flag
);

CREATE INDEX IF NOT EXISTS idx_test_identity_file
    ON test_identity(file_path);
CREATE INDEX IF NOT EXISTS idx_test_identity_function
    ON test_identity(function_name);
CREATE INDEX IF NOT EXISTS idx_test_identity_class
    ON test_identity(class_name) WHERE class_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_test_identity_active
    ON test_identity(is_active) WHERE is_active = 1;

-- -----------------------------------------------------------------------------
-- TABLE: execution_history
-- Purpose: Per-run execution records with full context
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS execution_history (
    execution_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id         TEXT NOT NULL REFERENCES test_identity(test_id) ON DELETE CASCADE,

    -- Outcome information
    outcome         TEXT NOT NULL CHECK (outcome IN ('passed', 'failed', 'error', 'skipped', 'xfailed', 'xpassed')),
    duration_ms     REAL NOT NULL,              -- Execution duration in milliseconds

    -- Timing and context
    timestamp       TEXT NOT NULL DEFAULT (datetime('now')),
    worker_id       TEXT DEFAULT 'master',      -- xdist worker ID (gw0, gw1, etc.)

    -- Environment context
    os_platform     TEXT NOT NULL,              -- sys.platform value
    python_version  TEXT NOT NULL,              -- e.g., '3.11.5'

    -- Source control context
    git_commit      TEXT,                       -- Full SHA
    git_branch      TEXT,                       -- Branch name

    -- CI/CD context
    ci_run_id       TEXT,                       -- GitHub Actions run ID or equivalent
    ci_job_name     TEXT,                       -- Job name within the run

    -- Rerun tracking (for pytest-rerunfailures integration)
    rerun_of        INTEGER REFERENCES execution_history(execution_id),
    rerun_attempt   INTEGER DEFAULT 0,          -- 0 = first run, 1+ = rerun attempt

    -- Failure details (populated only on failure/error)
    exception_type  TEXT,                       -- Exception class name
    exception_msg   TEXT,                       -- Truncated message (max 500 chars)
    traceback_hash  TEXT                        -- Hash of full traceback for deduplication
);

CREATE INDEX IF NOT EXISTS idx_exec_history_test_time
    ON execution_history(test_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_exec_history_outcome
    ON execution_history(outcome);
CREATE INDEX IF NOT EXISTS idx_exec_history_worker
    ON execution_history(worker_id);
CREATE INDEX IF NOT EXISTS idx_exec_history_platform
    ON execution_history(os_platform);
CREATE INDEX IF NOT EXISTS idx_exec_history_rerun
    ON execution_history(rerun_of) WHERE rerun_of IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_exec_history_ci
    ON execution_history(ci_run_id) WHERE ci_run_id IS NOT NULL;

-- -----------------------------------------------------------------------------
-- TABLE: flake_metrics
-- Purpose: Aggregated flake metrics (materialized view pattern)
-- Updated via trigger or scheduled job after each test run
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flake_metrics (
    test_id             TEXT PRIMARY KEY REFERENCES test_identity(test_id) ON DELETE CASCADE,

    -- Window statistics
    window_size         INTEGER NOT NULL DEFAULT 100,   -- Number of runs in analysis window
    window_runs         INTEGER NOT NULL DEFAULT 0,     -- Actual runs available

    -- Outcome counts within window
    pass_count          INTEGER NOT NULL DEFAULT 0,
    fail_count          INTEGER NOT NULL DEFAULT 0,
    error_count         INTEGER NOT NULL DEFAULT 0,
    skip_count          INTEGER NOT NULL DEFAULT 0,

    -- Flake-specific metrics
    flake_count         INTEGER NOT NULL DEFAULT 0,     -- Failed then passed on rerun
    flake_rate          REAL NOT NULL DEFAULT 0.0,      -- Percentage (0.0 - 100.0)
    stability_score     REAL NOT NULL DEFAULT 100.0,    -- 100 - flake_rate (for sorting)

    -- Duration statistics
    avg_duration_ms     REAL,
    min_duration_ms     REAL,
    max_duration_ms     REAL,
    stddev_duration_ms  REAL,
    p50_duration_ms     REAL,
    p95_duration_ms     REAL,

    -- Confidence and timing
    confidence_level    TEXT NOT NULL DEFAULT 'low'
                        CHECK (confidence_level IN ('low', 'medium', 'high')),
    last_updated        TEXT NOT NULL DEFAULT (datetime('now')),
    last_pass           TEXT,                           -- Timestamp of most recent pass
    last_failure        TEXT,                           -- Timestamp of most recent failure

    -- Trend indicators
    trend_direction     TEXT CHECK (trend_direction IN ('improving', 'stable', 'degrading')),
    trend_delta         REAL                            -- Change in flake_rate vs previous window
);

CREATE INDEX IF NOT EXISTS idx_flake_metrics_rate
    ON flake_metrics(flake_rate DESC);
CREATE INDEX IF NOT EXISTS idx_flake_metrics_confidence
    ON flake_metrics(confidence_level);
CREATE INDEX IF NOT EXISTS idx_flake_metrics_stability
    ON flake_metrics(stability_score);

-- -----------------------------------------------------------------------------
-- TABLE: quarantine_status
-- Purpose: Track active and historical quarantine records
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quarantine_status (
    quarantine_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id                 TEXT NOT NULL REFERENCES test_identity(test_id) ON DELETE CASCADE,

    -- Quarantine entry
    quarantine_date         TEXT NOT NULL DEFAULT (datetime('now')),
    quarantine_reason       TEXT NOT NULL,              -- Human-readable reason
    flake_rate_at_quarantine REAL NOT NULL,             -- Flake rate when quarantined
    triggered_by            TEXT NOT NULL DEFAULT 'auto'
                            CHECK (triggered_by IN ('auto', 'manual', 'ci_failure')),

    -- Review scheduling
    review_date             TEXT NOT NULL,              -- Next scheduled review
    review_cadence_days     INTEGER NOT NULL DEFAULT 14,
    review_count            INTEGER NOT NULL DEFAULT 0, -- Times reviewed

    -- Release tracking
    release_date            TEXT,                       -- When released (NULL if still active)
    release_reason          TEXT,                       -- Reason for release
    flake_rate_at_release   REAL,                       -- Flake rate when released

    -- Status management
    status                  TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'under_review', 'released', 'permanent', 'escalated')),

    -- Metadata
    notes                   TEXT,                       -- Free-form notes
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_quarantine_status_active
    ON quarantine_status(status) WHERE status IN ('active', 'under_review');
CREATE INDEX IF NOT EXISTS idx_quarantine_review_date
    ON quarantine_status(review_date) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_quarantine_test
    ON quarantine_status(test_id);

-- Ensure only one active quarantine per test
CREATE UNIQUE INDEX IF NOT EXISTS idx_quarantine_unique_active
    ON quarantine_status(test_id) WHERE status IN ('active', 'under_review');

-- -----------------------------------------------------------------------------
-- TABLE: flake_events (Audit log for individual flake occurrences)
-- Purpose: Detailed record of each flake event for root cause analysis
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flake_events (
    event_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id             TEXT NOT NULL REFERENCES test_identity(test_id),

    -- Event details
    first_execution_id  INTEGER NOT NULL REFERENCES execution_history(execution_id),
    rerun_execution_id  INTEGER NOT NULL REFERENCES execution_history(execution_id),

    -- Context at time of flake
    timestamp           TEXT NOT NULL DEFAULT (datetime('now')),
    os_platform         TEXT NOT NULL,
    worker_id           TEXT,
    git_commit          TEXT,

    -- Analysis fields
    suspected_cause     TEXT CHECK (suspected_cause IN (
        'timing', 'race_condition', 'resource_contention',
        'network', 'filesystem', 'random_seed', 'order_dependent',
        'worker_specific', 'platform_specific', 'unknown'
    )),

    -- Pattern tracking
    pattern_hash        TEXT,                   -- Hash of exception + traceback pattern
    similar_event_count INTEGER DEFAULT 1       -- Count of similar events
);

CREATE INDEX IF NOT EXISTS idx_flake_events_test
    ON flake_events(test_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_flake_events_cause
    ON flake_events(suspected_cause);
CREATE INDEX IF NOT EXISTS idx_flake_events_pattern
    ON flake_events(pattern_hash);

-- -----------------------------------------------------------------------------
-- VIEWS: Convenience views for common queries
-- -----------------------------------------------------------------------------

-- View: Active quarantine summary
CREATE VIEW IF NOT EXISTS v_active_quarantine AS
SELECT
    qs.quarantine_id,
    ti.nodeid,
    ti.file_path,
    ti.function_name,
    qs.quarantine_date,
    qs.flake_rate_at_quarantine,
    qs.review_date,
    qs.status,
    fm.flake_rate AS current_flake_rate,
    fm.window_runs,
    CASE
        WHEN fm.flake_rate < 5.0 AND fm.window_runs >= 100 THEN 'eligible_release'
        WHEN julianday('now') > julianday(qs.review_date) THEN 'review_overdue'
        ELSE 'monitoring'
    END AS action_needed
FROM quarantine_status qs
JOIN test_identity ti ON qs.test_id = ti.test_id
LEFT JOIN flake_metrics fm ON qs.test_id = fm.test_id
WHERE qs.status IN ('active', 'under_review');

-- View: Tests needing quarantine (flake_rate > 20%, not already quarantined)
CREATE VIEW IF NOT EXISTS v_quarantine_candidates AS
SELECT
    ti.test_id,
    ti.nodeid,
    ti.file_path,
    fm.flake_rate,
    fm.flake_count,
    fm.window_runs,
    fm.confidence_level,
    fm.last_failure
FROM flake_metrics fm
JOIN test_identity ti ON fm.test_id = ti.test_id
LEFT JOIN quarantine_status qs ON fm.test_id = qs.test_id
    AND qs.status IN ('active', 'under_review')
WHERE fm.flake_rate > 20.0
  AND fm.confidence_level IN ('medium', 'high')
  AND fm.window_runs >= 30
  AND qs.quarantine_id IS NULL;

-- View: Reintegration candidates (flake_rate < 5% in quarantine)
CREATE VIEW IF NOT EXISTS v_reintegration_candidates AS
SELECT
    qs.quarantine_id,
    ti.nodeid,
    ti.file_path,
    qs.quarantine_date,
    qs.flake_rate_at_quarantine,
    fm.flake_rate AS current_flake_rate,
    fm.window_runs,
    julianday('now') - julianday(qs.quarantine_date) AS days_in_quarantine
FROM quarantine_status qs
JOIN test_identity ti ON qs.test_id = ti.test_id
JOIN flake_metrics fm ON qs.test_id = fm.test_id
WHERE qs.status = 'active'
  AND fm.flake_rate < 5.0
  AND fm.window_runs >= 100;

-- View: Overall flake rate summary
CREATE VIEW IF NOT EXISTS v_flake_summary AS
SELECT
    COUNT(*) AS total_tests,
    SUM(CASE WHEN fm.flake_rate > 0 THEN 1 ELSE 0 END) AS flaky_tests,
    SUM(CASE WHEN fm.flake_rate > 20 THEN 1 ELSE 0 END) AS high_flake_tests,
    AVG(fm.flake_rate) AS avg_flake_rate,
    SUM(fm.flake_count) AS total_flake_events,
    SUM(fm.window_runs) AS total_executions
FROM flake_metrics fm
JOIN test_identity ti ON fm.test_id = ti.test_id
WHERE ti.is_active = 1;

-- -----------------------------------------------------------------------------
-- TRIGGERS: Automatic timestamp updates
-- -----------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_quarantine_updated
AFTER UPDATE ON quarantine_status
BEGIN
    UPDATE quarantine_status
    SET updated_at = datetime('now')
    WHERE quarantine_id = NEW.quarantine_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_test_identity_seen
AFTER INSERT ON execution_history
BEGIN
    UPDATE test_identity
    SET last_seen = datetime('now')
    WHERE test_id = NEW.test_id;
END;
```

---

## 2. Flake Rate Calculation Algorithm

### 2.1 Core Algorithm (Pseudocode)

```python
def calculate_flake_metrics(test_id: str, window_size: int = 100) -> FlakeMetrics:
    """
    Calculate flake metrics using rolling window analysis.

    Algorithm:
    1. Fetch last N executions for test
    2. Identify flaky runs (failed -> passed on rerun)
    3. Calculate flake rate with confidence bounds
    4. Detect broken vs flaky distinction
    5. Return metrics with confidence level
    """

    # Step 1: Fetch execution window
    executions = fetch_recent_executions(test_id, limit=window_size)
    actual_runs = len(executions)

    # Step 2: Determine confidence level
    if actual_runs >= 30:
        confidence = 'high'
    elif actual_runs >= 10:
        confidence = 'medium'
    else:
        confidence = 'low'  # Not actionable

    # Step 3: Count outcomes
    outcomes = {
        'passed': 0,
        'failed': 0,
        'error': 0,
        'skipped': 0,
        'flaky': 0  # Failed then passed on rerun
    }

    for exec in executions:
        outcomes[exec.outcome] += 1

        # Check if this is a rerun that passed after failure
        if exec.rerun_of is not None and exec.outcome == 'passed':
            parent = get_execution(exec.rerun_of)
            if parent.outcome in ('failed', 'error'):
                outcomes['flaky'] += 1

    # Step 4: Calculate rates
    total_attempts = outcomes['passed'] + outcomes['failed'] + outcomes['error']
    if total_attempts == 0:
        return FlakeMetrics(flake_rate=0.0, confidence='low')

    fail_rate = (outcomes['failed'] + outcomes['error']) / total_attempts * 100

    # Step 5: Broken vs Flaky distinction
    if fail_rate > 90:
        # Test is broken, not flaky - different handling
        return FlakeMetrics(
            flake_rate=0.0,  # Not counted as flaky
            is_broken=True,
            fail_rate=fail_rate,
            confidence=confidence
        )

    # Step 6: Calculate flake rate
    flake_rate = (outcomes['flaky'] / actual_runs) * 100

    # Step 7: Statistical validation (Wilson score interval)
    lower_bound, upper_bound = wilson_score_interval(
        successes=outcomes['flaky'],
        total=actual_runs,
        confidence=0.95
    )

    return FlakeMetrics(
        test_id=test_id,
        window_runs=actual_runs,
        pass_count=outcomes['passed'],
        fail_count=outcomes['failed'],
        error_count=outcomes['error'],
        flake_count=outcomes['flaky'],
        flake_rate=flake_rate,
        flake_rate_lower=lower_bound * 100,
        flake_rate_upper=upper_bound * 100,
        stability_score=100 - flake_rate,
        confidence_level=confidence,
        is_broken=False
    )


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Calculate Wilson score confidence interval for binomial proportion.

    More accurate than normal approximation for small samples.
    """
    from scipy import stats

    if total == 0:
        return (0.0, 0.0)

    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p_hat = successes / total

    denominator = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt(p_hat * (1 - p_hat) / total + z**2 / (4 * total**2)) / denominator

    return (max(0, center - spread), min(1, center + spread))
```

### 2.2 False Positive Prevention Logic

```python
def should_quarantine(metrics: FlakeMetrics) -> tuple[bool, str]:
    """
    Determine if a test should be quarantined with reason.

    Returns:
        (should_quarantine: bool, reason: str)
    """

    # Rule 1: Never act on low confidence data
    if metrics.confidence_level == 'low':
        return (False, "Insufficient data (< 10 runs)")

    # Rule 2: Don't quarantine broken tests (fix them instead)
    if metrics.is_broken:
        return (False, f"Test is broken (fail_rate={metrics.fail_rate:.1f}%), not flaky")

    # Rule 3: Check threshold
    if metrics.flake_rate <= 20.0:
        return (False, f"Flake rate {metrics.flake_rate:.1f}% below 20% threshold")

    # Rule 4: Check confidence interval doesn't cross threshold
    if metrics.flake_rate_lower <= 20.0:
        return (False, f"Confidence interval [{metrics.flake_rate_lower:.1f}%, {metrics.flake_rate_upper:.1f}%] crosses threshold")

    # Rule 5: Check for worker/platform specificity
    platform_analysis = analyze_platform_distribution(metrics.test_id)
    if platform_analysis.is_platform_specific:
        return (False, f"Failures specific to {platform_analysis.specific_platform}, not general flakiness")

    worker_analysis = analyze_worker_distribution(metrics.test_id)
    if worker_analysis.is_worker_specific:
        return (False, f"Failures specific to worker {worker_analysis.specific_worker}, not general flakiness")

    # Passed all checks - quarantine recommended
    return (True, f"Flake rate {metrics.flake_rate:.1f}% exceeds 20% threshold with {metrics.confidence_level} confidence")
```

### 2.3 Aggregation Update Query

```sql
-- Stored procedure equivalent: Update flake_metrics for a specific test
-- Call after each test run batch or on schedule

WITH recent_executions AS (
    SELECT
        eh.*,
        ROW_NUMBER() OVER (PARTITION BY eh.test_id ORDER BY eh.timestamp DESC) AS rn
    FROM execution_history eh
    WHERE eh.test_id = :test_id
),
window_data AS (
    SELECT
        test_id,
        COUNT(*) AS window_runs,
        SUM(CASE WHEN outcome = 'passed' THEN 1 ELSE 0 END) AS pass_count,
        SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END) AS fail_count,
        SUM(CASE WHEN outcome = 'error' THEN 1 ELSE 0 END) AS error_count,
        SUM(CASE WHEN outcome = 'skipped' THEN 1 ELSE 0 END) AS skip_count,
        AVG(duration_ms) AS avg_duration_ms,
        MIN(duration_ms) AS min_duration_ms,
        MAX(duration_ms) AS max_duration_ms,
        MAX(CASE WHEN outcome = 'passed' THEN timestamp END) AS last_pass,
        MAX(CASE WHEN outcome IN ('failed', 'error') THEN timestamp END) AS last_failure
    FROM recent_executions
    WHERE rn <= :window_size
    GROUP BY test_id
),
flake_data AS (
    SELECT
        re.test_id,
        COUNT(*) AS flake_count
    FROM recent_executions re
    JOIN execution_history parent ON re.rerun_of = parent.execution_id
    WHERE re.rn <= :window_size
      AND re.outcome = 'passed'
      AND parent.outcome IN ('failed', 'error')
    GROUP BY re.test_id
)
INSERT OR REPLACE INTO flake_metrics (
    test_id, window_size, window_runs, pass_count, fail_count, error_count, skip_count,
    flake_count, flake_rate, stability_score, avg_duration_ms, min_duration_ms, max_duration_ms,
    confidence_level, last_updated, last_pass, last_failure
)
SELECT
    wd.test_id,
    :window_size,
    wd.window_runs,
    wd.pass_count,
    wd.fail_count,
    wd.error_count,
    wd.skip_count,
    COALESCE(fd.flake_count, 0),
    CASE WHEN wd.window_runs > 0
         THEN (COALESCE(fd.flake_count, 0) * 100.0 / wd.window_runs)
         ELSE 0.0 END,
    CASE WHEN wd.window_runs > 0
         THEN (100.0 - (COALESCE(fd.flake_count, 0) * 100.0 / wd.window_runs))
         ELSE 100.0 END,
    wd.avg_duration_ms,
    wd.min_duration_ms,
    wd.max_duration_ms,
    CASE
        WHEN wd.window_runs >= 30 THEN 'high'
        WHEN wd.window_runs >= 10 THEN 'medium'
        ELSE 'low'
    END,
    datetime('now'),
    wd.last_pass,
    wd.last_failure
FROM window_data wd
LEFT JOIN flake_data fd ON wd.test_id = fd.test_id;
```

---

## 3. Quarantine Threshold Logic

### 3.1 Entry Criteria (Pseudocode)

```python
QUARANTINE_THRESHOLD = 20.0  # Percentage
MINIMUM_CONFIDENCE = 'medium'
MINIMUM_RUNS = 30

def evaluate_quarantine_candidates() -> list[QuarantineAction]:
    """
    Evaluate all tests and return list of quarantine actions.

    Entry Criteria:
    1. flake_rate > 20%
    2. confidence_level IN ('medium', 'high')
    3. window_runs >= 30
    4. Not already in active quarantine
    5. Not broken (fail_rate < 90%)
    """

    candidates = query_quarantine_candidates()  # Uses v_quarantine_candidates view
    actions = []

    for candidate in candidates:
        should_q, reason = should_quarantine(candidate.metrics)

        if should_q:
            actions.append(QuarantineAction(
                test_id=candidate.test_id,
                action='quarantine',
                reason=reason,
                flake_rate=candidate.metrics.flake_rate,
                review_date=calculate_review_date(candidate.metrics.flake_rate),
                marker='@pytest.mark.flaky_quarantine'
            ))

    return actions


def calculate_review_date(flake_rate: float) -> datetime:
    """
    Calculate review date based on severity.

    - High flake (>50%): Weekly review
    - Medium flake (20-50%): Bi-weekly review
    """
    if flake_rate > 50.0:
        return datetime.now() + timedelta(days=7)
    else:
        return datetime.now() + timedelta(days=14)
```

### 3.2 Reintegration Criteria (Pseudocode)

```python
REINTEGRATION_THRESHOLD = 5.0  # Percentage
REINTEGRATION_RUNS = 100
MINIMUM_QUARANTINE_DAYS = 7

def evaluate_reintegration_candidates() -> list[ReintegrationAction]:
    """
    Evaluate quarantined tests for potential release.

    Release Criteria:
    1. flake_rate < 5% in quarantine environment
    2. window_runs >= 100 (all in quarantine)
    3. Minimum 7 days in quarantine
    4. Manual approval required
    """

    candidates = query_reintegration_candidates()  # Uses v_reintegration_candidates view
    actions = []

    for candidate in candidates:
        days_in_quarantine = candidate.days_in_quarantine

        if days_in_quarantine < MINIMUM_QUARANTINE_DAYS:
            continue

        actions.append(ReintegrationAction(
            quarantine_id=candidate.quarantine_id,
            test_id=candidate.test_id,
            action='recommend_release',
            current_flake_rate=candidate.current_flake_rate,
            days_in_quarantine=days_in_quarantine,
            requires_approval=True,
            recommendation=f"Flake rate improved from {candidate.flake_rate_at_quarantine:.1f}% to {candidate.current_flake_rate:.1f}%"
        ))

    return actions
```

### 3.3 Status Transition State Machine

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────┐    ┌────────┐    ┌──────────────┐    ┌──────────┐
│ (none)  │───▶│ active │───▶│ under_review │───▶│ released │
└─────────┘    └────────┘    └──────────────┘    └──────────┘
     │              │              │                   │
     │              │              │                   │
     │              ▼              ▼                   │
     │         ┌───────────┐      │                   │
     │         │ escalated │◀─────┘                   │
     │         └───────────┘                          │
     │              │                                 │
     │              ▼                                 │
     │         ┌───────────┐                          │
     └────────▶│ permanent │◀─────────────────────────┘
               └───────────┘

Transitions:
- (none) → active: flake_rate > 20%, auto or manual
- active → under_review: review_date reached OR flake_rate < 5%
- under_review → released: manual approval + flake_rate < 5%
- under_review → active: review failed (flake_rate still > 5%)
- active → escalated: 3+ failed reviews
- escalated → permanent: manual decision (unfixable)
- released → active: re-quarantine if flake_rate rises again
- any → permanent: manual decision
```

---

## 4. pytest Hook Implementation Outline

### 4.1 conftest.py Integration

```python
# conftest.py - FlakeTracker pytest integration

import pytest
import hashlib
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import FlakeTracker (implementation separate)
from flaketracker import FlakeTrackerDB, ExecutionRecord, TestIdentity


# Global tracker instance
_tracker: Optional[FlakeTrackerDB] = None


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers and initialize FlakeTracker."""

    # Register markers
    config.addinivalue_line(
        "markers",
        "flaky_quarantine: Test is quarantined due to high flake rate (>20%)"
    )
    config.addinivalue_line(
        "markers",
        "flaky(reruns=N): Mark test as known flaky with rerun count"
    )

    # Initialize tracker
    global _tracker
    db_path = Path(config.rootdir) / "artifacts" / "flake_tracker.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _tracker = FlakeTrackerDB(db_path)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """
    Dynamic marker injection for quarantined tests.

    This hook runs during collection and applies @pytest.mark.flaky_quarantine
    to tests that are in active quarantine status.
    """
    global _tracker
    if _tracker is None:
        return

    # Get all actively quarantined test IDs
    quarantined_ids = _tracker.get_quarantined_test_ids()

    for item in items:
        test_id = _generate_test_id(item.nodeid)

        if test_id in quarantined_ids:
            # Apply quarantine marker
            item.add_marker(pytest.mark.flaky_quarantine)

            # Optionally skip in CI main pipeline
            if config.getoption("--skip-quarantine", default=False):
                item.add_marker(pytest.mark.skip(
                    reason=f"Test quarantined (flake_rate > 20%)"
                ))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    Record test execution results to FlakeTracker.

    This hook fires for each phase (setup, call, teardown) of test execution.
    We only record the 'call' phase for actual test results.
    """
    outcome = yield
    report = outcome.get_result()

    # Only record call phase results
    if report.when != "call":
        return

    global _tracker
    if _tracker is None:
        return

    # Extract test identity
    test_identity = _extract_test_identity(item)

    # Determine outcome
    if report.passed:
        outcome_str = "passed"
    elif report.failed:
        outcome_str = "failed"
    elif report.skipped:
        outcome_str = "skipped"
    else:
        outcome_str = "error"

    # Extract worker ID (for xdist)
    worker_id = getattr(item.config, "workerinput", {}).get("workerid", "master")

    # Extract exception info if failed
    exception_type = None
    exception_msg = None
    if report.failed and call.excinfo:
        exception_type = call.excinfo.typename
        exception_msg = str(call.excinfo.value)[:500]  # Truncate

    # Check if this is a rerun (pytest-rerunfailures integration)
    rerun_attempt = getattr(item, "execution_count", 0)
    rerun_of = getattr(item, "_flaketracker_previous_execution_id", None)

    # Record execution
    execution_id = _tracker.record_execution(ExecutionRecord(
        test_id=test_identity.test_id,
        outcome=outcome_str,
        duration_ms=report.duration * 1000,
        timestamp=datetime.now().isoformat(),
        worker_id=worker_id,
        os_platform=sys.platform,
        python_version=platform.python_version(),
        git_commit=_get_git_commit(),
        git_branch=_get_git_branch(),
        ci_run_id=_get_ci_run_id(),
        rerun_of=rerun_of,
        rerun_attempt=rerun_attempt,
        exception_type=exception_type,
        exception_msg=exception_msg
    ))

    # Store execution ID for potential rerun tracking
    item._flaketracker_previous_execution_id = execution_id

    # If this was a flaky event (failed then passed), record it
    if rerun_of is not None and outcome_str == "passed":
        parent_outcome = _tracker.get_execution_outcome(rerun_of)
        if parent_outcome in ("failed", "error"):
            _tracker.record_flake_event(
                test_id=test_identity.test_id,
                first_execution_id=rerun_of,
                rerun_execution_id=execution_id,
                os_platform=sys.platform,
                worker_id=worker_id,
                git_commit=_get_git_commit()
            )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """
    Update aggregated metrics after test session completes.
    """
    global _tracker
    if _tracker is None:
        return

    # Update flake_metrics for all tests that ran in this session
    _tracker.update_all_metrics()

    # Generate delta report for CI
    _tracker.generate_delta_report(
        output_path=Path(session.config.rootdir) / "artifacts" / "flake.reduction.delta.json"
    )

    # Close database connection
    _tracker.close()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add FlakeTracker CLI options."""
    group = parser.getgroup("flaketracker")
    group.addoption(
        "--skip-quarantine",
        action="store_true",
        default=False,
        help="Skip quarantined tests in main CI pipeline"
    )
    group.addoption(
        "--flaketracker-db",
        action="store",
        default="artifacts/flake_tracker.db",
        help="Path to FlakeTracker SQLite database"
    )


# Helper functions

def _generate_test_id(nodeid: str) -> str:
    """Generate stable test ID from nodeid."""
    return hashlib.sha256(nodeid.encode()).hexdigest()[:16]


def _extract_test_identity(item: pytest.Item) -> TestIdentity:
    """Extract test identity components from pytest item."""
    nodeid = item.nodeid

    # Parse nodeid: tests/test_foo.py::TestClass::test_method[param]
    parts = nodeid.split("::")
    file_path = parts[0]

    # Determine module name
    module_name = file_path.replace("/", ".").replace("\\", ".").rstrip(".py")

    # Extract class and function
    class_name = None
    function_name = parts[-1]
    parametrize_id = None

    # Check for parametrize suffix
    if "[" in function_name:
        function_name, parametrize_id = function_name.split("[", 1)
        parametrize_id = "[" + parametrize_id

    # Check for class
    if len(parts) == 3:
        class_name = parts[1]

    return TestIdentity(
        test_id=_generate_test_id(nodeid),
        nodeid=nodeid,
        file_path=file_path,
        module_name=module_name,
        class_name=class_name,
        function_name=function_name,
        parametrize_id=parametrize_id
    )


def _get_git_commit() -> Optional[str]:
    """Get current git commit SHA."""
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None


def _get_git_branch() -> Optional[str]:
    """Get current git branch name."""
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None


def _get_ci_run_id() -> Optional[str]:
    """Get CI run ID from environment."""
    import os
    # GitHub Actions
    if os.getenv("GITHUB_RUN_ID"):
        return f"gh-{os.getenv('GITHUB_RUN_ID')}"
    # Azure DevOps
    if os.getenv("BUILD_BUILDID"):
        return f"azdo-{os.getenv('BUILD_BUILDID')}"
    return None
```

### 4.2 pytest-rerunfailures Integration

```python
# Additional hook for tracking reruns with pytest-rerunfailures

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item) -> None:
    """
    Track rerun attempts for pytest-rerunfailures integration.

    pytest-rerunfailures uses execution_count attribute to track reruns.
    We use this to link rerun executions in FlakeTracker.
    """
    # Initialize execution count if not present
    if not hasattr(item, "execution_count"):
        item.execution_count = 0
    else:
        item.execution_count += 1


# pytest.ini configuration for rerunfailures
"""
[pytest]
# Enable single rerun for flake detection (not hiding)
reruns = 1
reruns_delay = 0.5

# Only rerun on specific failure types
only_rerun = AssertionError ConnectionError TimeoutError

# Don't rerun on these (likely genuine failures)
rerun_except = KeyError TypeError ValueError
"""
```

---

## 5. flake.reduction.delta.json Schema

### 5.1 JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://contextforge.io/schemas/flake.reduction.delta.v1.json",
  "title": "Flake Reduction Delta Report",
  "description": "Tracks flake rate changes between CI runs for Phase 2 O1 validation",
  "type": "object",
  "required": ["metadata", "summary", "tests"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["schema_version", "generated_at", "current_run", "baseline_run"],
      "properties": {
        "schema_version": {
          "type": "string",
          "const": "1.0.0"
        },
        "generated_at": {
          "type": "string",
          "format": "date-time"
        },
        "current_run": {
          "type": "object",
          "required": ["ci_run_id", "git_commit", "timestamp"],
          "properties": {
            "ci_run_id": { "type": "string" },
            "git_commit": { "type": "string" },
            "git_branch": { "type": "string" },
            "timestamp": { "type": "string", "format": "date-time" }
          }
        },
        "baseline_run": {
          "type": "object",
          "required": ["ci_run_id", "git_commit", "timestamp"],
          "properties": {
            "ci_run_id": { "type": "string" },
            "git_commit": { "type": "string" },
            "git_branch": { "type": "string" },
            "timestamp": { "type": "string", "format": "date-time" }
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["overall_flake_rate", "target_flake_rate", "target_met", "delta"],
      "properties": {
        "overall_flake_rate": {
          "type": "object",
          "required": ["current", "baseline"],
          "properties": {
            "current": { "type": "number", "minimum": 0, "maximum": 100 },
            "baseline": { "type": "number", "minimum": 0, "maximum": 100 },
            "delta": { "type": "number" },
            "delta_percent": { "type": "number" }
          }
        },
        "target_flake_rate": {
          "type": "number",
          "const": 5.0,
          "description": "Phase 2 O1 target: <5%"
        },
        "target_met": {
          "type": "boolean"
        },
        "delta": {
          "type": "object",
          "properties": {
            "improved_tests": { "type": "integer", "minimum": 0 },
            "degraded_tests": { "type": "integer", "minimum": 0 },
            "new_flaky_tests": { "type": "integer", "minimum": 0 },
            "stabilized_tests": { "type": "integer", "minimum": 0 }
          }
        },
        "quarantine_stats": {
          "type": "object",
          "properties": {
            "active_quarantine_count": { "type": "integer", "minimum": 0 },
            "newly_quarantined": { "type": "integer", "minimum": 0 },
            "released_from_quarantine": { "type": "integer", "minimum": 0 },
            "pending_review": { "type": "integer", "minimum": 0 }
          }
        }
      }
    },
    "tests": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["test_id", "nodeid", "current_metrics", "baseline_metrics", "status"],
        "properties": {
          "test_id": { "type": "string" },
          "nodeid": { "type": "string" },
          "file_path": { "type": "string" },
          "function_name": { "type": "string" },
          "class_name": { "type": ["string", "null"] },
          "current_metrics": {
            "type": "object",
            "properties": {
              "flake_rate": { "type": "number" },
              "flake_count": { "type": "integer" },
              "window_runs": { "type": "integer" },
              "pass_count": { "type": "integer" },
              "fail_count": { "type": "integer" },
              "confidence_level": {
                "type": "string",
                "enum": ["low", "medium", "high"]
              }
            }
          },
          "baseline_metrics": {
            "type": "object",
            "properties": {
              "flake_rate": { "type": "number" },
              "flake_count": { "type": "integer" },
              "window_runs": { "type": "integer" }
            }
          },
          "delta": {
            "type": "object",
            "properties": {
              "flake_rate_change": { "type": "number" },
              "trend": {
                "type": "string",
                "enum": ["improved", "stable", "degraded", "new_flaky", "stabilized"]
              }
            }
          },
          "status": {
            "type": "string",
            "enum": ["stable", "flaky", "quarantined", "broken", "new"]
          },
          "quarantine_info": {
            "type": ["object", "null"],
            "properties": {
              "quarantine_date": { "type": "string", "format": "date-time" },
              "review_date": { "type": "string", "format": "date-time" },
              "days_in_quarantine": { "type": "integer" }
            }
          }
        }
      }
    },
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["priority", "action", "target"],
        "properties": {
          "priority": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"]
          },
          "action": {
            "type": "string",
            "enum": ["quarantine", "investigate", "review", "release", "fix"]
          },
          "target": { "type": "string" },
          "reason": { "type": "string" },
          "test_ids": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### 5.2 Example Output

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "generated_at": "2025-11-25T14:30:00Z",
    "current_run": {
      "ci_run_id": "gh-12345678",
      "git_commit": "abc123def456",
      "git_branch": "main",
      "timestamp": "2025-11-25T14:25:00Z"
    },
    "baseline_run": {
      "ci_run_id": "gh-12345600",
      "git_commit": "789xyz012",
      "git_branch": "main",
      "timestamp": "2025-11-24T14:25:00Z"
    }
  },
  "summary": {
    "overall_flake_rate": {
      "current": 3.2,
      "baseline": 8.5,
      "delta": -5.3,
      "delta_percent": -62.4
    },
    "target_flake_rate": 5.0,
    "target_met": true,
    "delta": {
      "improved_tests": 12,
      "degraded_tests": 2,
      "new_flaky_tests": 1,
      "stabilized_tests": 5
    },
    "quarantine_stats": {
      "active_quarantine_count": 3,
      "newly_quarantined": 1,
      "released_from_quarantine": 2,
      "pending_review": 1
    }
  },
  "tests": [
    {
      "test_id": "a1b2c3d4e5f6",
      "nodeid": "tests/test_api.py::TestUserAPI::test_create_user",
      "file_path": "tests/test_api.py",
      "function_name": "test_create_user",
      "class_name": "TestUserAPI",
      "current_metrics": {
        "flake_rate": 2.0,
        "flake_count": 2,
        "window_runs": 100,
        "pass_count": 98,
        "fail_count": 2,
        "confidence_level": "high"
      },
      "baseline_metrics": {
        "flake_rate": 25.0,
        "flake_count": 25,
        "window_runs": 100
      },
      "delta": {
        "flake_rate_change": -23.0,
        "trend": "improved"
      },
      "status": "stable",
      "quarantine_info": null
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "investigate",
      "target": "tests/test_database.py::test_concurrent_writes",
      "reason": "New flaky test detected (15% flake rate)",
      "test_ids": ["x1y2z3"]
    }
  ]
}
```

---

## 6. CI/CD Integration Points

### 6.1 GitHub Actions Workflow Integration

```yaml
# .github/workflows/test-with-flaketracker.yml
name: Tests with FlakeTracker

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 4 * * *'  # Daily quarantine review

jobs:
  # Main test job - skips quarantined tests
  test-main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Download FlakeTracker DB (artifact)
        uses: dawidd6/action-download-artifact@v3
        with:
          name: flake_tracker_db
          path: artifacts/
        continue-on-error: true  # First run won't have DB

      - name: Run tests (skip quarantined)
        run: |
          pytest \
            --skip-quarantine \
            --reruns 1 \
            --json-report \
            --json-report-file=artifacts/test_results.json \
            -v

      - name: Upload FlakeTracker DB
        uses: actions/upload-artifact@v4
        with:
          name: flake_tracker_db
          path: artifacts/flake_tracker.db
          retention-days: 90

      - name: Upload flake delta report
        uses: actions/upload-artifact@v4
        with:
          name: flake_reduction_delta
          path: artifacts/flake.reduction.delta.json

  # Quarantine job - runs only quarantined tests with high reruns
  test-quarantine:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Download FlakeTracker DB
        uses: dawidd6/action-download-artifact@v3
        with:
          name: flake_tracker_db
          path: artifacts/

      - name: Run quarantined tests
        run: |
          pytest \
            -m flaky_quarantine \
            --reruns 5 \
            --reruns-delay 2 \
            --json-report \
            --json-report-file=artifacts/quarantine_results.json \
            -v

      - name: Update FlakeTracker metrics
        run: python scripts/flake_tracker.py update-metrics

      - name: Generate quarantine report
        run: |
          python scripts/flake_tracker.py report \
            --output artifacts/quarantine_report.html

      - name: Check for reintegration candidates
        run: python scripts/flake_tracker.py check-reintegration
```

### 6.2 Integration Summary

| Component | Integration Point | Data Flow |
|-----------|------------------|-----------|
| pytest | `pytest_runtest_makereport` hook | Execution → FlakeTracker DB |
| pytest-rerunfailures | `@pytest.mark.flaky` + `--reruns` | Flake detection |
| pytest-xdist | `worker_id` capture | Parallel execution tracking |
| GitHub Actions | Artifact persistence | DB state across runs |
| CI Pipeline | `--skip-quarantine` flag | Production isolation |
| Quarantine Job | `-m flaky_quarantine` | Isolated flake testing |

---

## 7. Implementation Checklist (For Reference Only)

> **Note**: This document is DESIGN ONLY. Implementation is out of scope.

- [ ] Create SQLite schema migration script
- [ ] Implement `FlakeTrackerDB` class with CRUD operations
- [ ] Implement pytest hooks in `conftest.py`
- [ ] Create `flake_tracker.py` CLI tool
- [ ] Integrate with existing CI/CD pipeline
- [ ] Add JSON schema validation for delta reports
- [ ] Create quarantine review dashboard (optional)
- [ ] Document runbook for manual quarantine operations

---

## 8. References

- [pytest-rerunfailures documentation](https://github.com/pytest-dev/pytest-rerunfailures)
- [pytest hooks reference](https://docs.pytest.org/en/stable/reference/reference.html#hooks)
- [TPR-Phase2-Technical-Research.md](../../TPR-Phase2-Technical-Research.md) - Section 6
- [Wilson Score Interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval)

---

**END OF DESIGN DOCUMENT**
