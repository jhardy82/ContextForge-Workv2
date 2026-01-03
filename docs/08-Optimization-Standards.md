# Optimization Standards

**Version**: 1.0.0
**Created**: 2025-11-11
**Status**: Active

---

## Purpose

This document establishes ContextForge performance optimization standards, profiling methodologies, and benchmarking practices. It provides actionable guidance for measuring, analyzing, and improving system performance while maintaining alignment with Sacred Geometry patterns and COF principles.

**Key Objectives**:
- Define performance profiling and benchmarking standards
- Establish data-driven optimization workflows
- Integrate DuckDB velocity tracking for realistic planning
- Ensure reproducible performance measurement
- Align optimization patterns with Sacred Geometry

---

## Table of Contents

1. [Philosophy & Principles](#philosophy--principles)
2. [Performance Targets](#performance-targets)
3. [Profiling Standards](#profiling-standards)
4. [Benchmarking Framework](#benchmarking-framework)
5. [DuckDB Velocity Integration](#duckdb-velocity-integration)
6. [Optimization Workflows](#optimization-workflows)
7. [Sacred Geometry Patterns](#sacred-geometry-patterns)
8. [Evidence & Reporting](#evidence--reporting)
9. [Best Practices](#best-practices)

---

## Philosophy & Principles

### Golden Ratio Optimization

**Principle**: Optimize for the **vital few** (20%) that deliver **80% impact**

The Golden Ratio (φ = 1.618) guides optimization prioritization:

```text
┌────────────────────────────────────────────┐
│  Optimization Impact Distribution          │
├────────────────────────────────────────────┤
│  20% of code paths → 80% of runtime        │
│  Focus profiling on hot paths              │
│  Measure before optimizing                 │
│  Apply φ ratio to effort allocation        │
└────────────────────────────────────────────┘
```

**Application**:
1. **Profile first** - Identify the critical 20%
2. **Optimize selectively** - Focus effort on high-impact areas
3. **Measure improvement** - Validate 80% impact achieved
4. **Avoid premature optimization** - Don't optimize the trivial 80%

---

### Sacred Geometry Spiral (Iterative Refinement)

**Pattern**: Performance optimization follows iterative spiral cycles

```text
    Measure → Profile → Optimize → Validate
       ↓                              ↑
       └──────────── Iterate ─────────┘
```

**Cycle Phases**:
1. **Measure** - Establish baseline metrics
2. **Profile** - Identify bottlenecks
3. **Optimize** - Apply targeted improvements
4. **Validate** - Confirm impact with benchmarks
5. **Repeat** - Continue until targets met

---

### UCL Compliance (Reproducibility)

**Universal Context Law Requirements**:

All performance work must maintain:
- **Evidence bundles** with profiling data and benchmark results
- **Reproducible measurements** via automation
- **SHA-256 hashing** of profiling outputs for integrity
- **Unified logging** of all optimization activities

**Example**:
```python
# Log optimization context
ulog("optimization_cycle", "baseline_measurement", "INFO",
     metric="api_p95_latency",
     baseline_ms=450,
     target_ms=200,
     evidence_bundle="EB-PERF-20251111-001.tar.gz")
```

---

## Performance Targets

### API Response Times (FastAPI Backend)

| Percentile | Target | Measurement |
|------------|--------|-------------|
| **p50 (Median)** | <100ms | 50% of requests |
| **p95** | <200ms | 95% of requests |
| **p99** | <500ms | 99% of requests |
| **p99.9** | <1000ms | 99.9% of requests |

**Critical Endpoints**:
- `GET /api/v1/tasks` - List tasks: <150ms p95
- `POST /api/v1/tasks` - Create task: <200ms p95
- `GET /api/v1/tasks/{id}` - Get task: <50ms p95
- `PUT /api/v1/tasks/{id}` - Update task: <100ms p95

**Measurement Tool**: Locust load testing + Prometheus metrics

---

### Database Query Performance (PostgreSQL)

| Query Type | Target | Optimization Strategy |
|------------|--------|----------------------|
| **Single row lookup** | <5ms | Indexed primary key |
| **Filter queries** | <20ms | Composite indexes |
| **Aggregations** | <100ms | Materialized views |
| **Complex joins** | <200ms | Query optimization |

**Example Optimization**:
```sql
-- Before: Full table scan (450ms)
SELECT * FROM tasks WHERE status = 'in_progress';

-- After: Index scan (8ms)
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Measurement**: PostgreSQL `EXPLAIN ANALYZE` and `pg_stat_statements`

---

### CLI Cold Start Time

| CLI Tool | Target | Current | Status |
|----------|--------|---------|--------|
| **cf_cli.py** | <500ms | ~850ms | ⚠️ Needs optimization |
| **tasks_cli.py** | <300ms | ~420ms | ⚠️ Needs optimization |
| **Unified cf_core** | <400ms | N/A | 🎯 Target for consolidation |

**Optimization Strategies**:
1. Lazy import heavy dependencies (Pydantic, Rich, DuckDB)
2. Cache compiled regex and config parsing
3. Reduce module initialization overhead
4. Profile with `python -X importtime`

---

### Frontend Performance (React)

| Metric | Target | Tool |
|--------|--------|------|
| **First Contentful Paint** | <1.5s | Lighthouse |
| **Largest Contentful Paint** | <2.5s | Lighthouse |
| **Time to Interactive** | <3.5s | Lighthouse |
| **Cumulative Layout Shift** | <0.1 | Lighthouse |

**React-Specific**:
- Component render time: <16ms (60fps)
- Bundle size: <250KB gzipped
- Code splitting: Lazy load routes

---

## Profiling Standards

### Python Profiling Tools

#### 1. cProfile (CPU Profiling)

**Use Case**: Identify function-level CPU hotspots

**Usage**:
```bash
# Profile script execution
python -m cProfile -o profile.stats cf_cli.py list

# Analyze with pstats
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(20)"
```

**Output Example**:
```text
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    2.450    2.450 cf_cli.py:1(<module>)
      150    0.230    0.002    1.800    0.012 unified_logger.py:45(ulog)
       45    0.680    0.015    0.680    0.015 {built-in method psycopg2._psycopg.connect}
```

**Sacred Geometry Application**: Focus on top 20% of cumtime (Golden Ratio)

---

#### 2. line_profiler (Line-by-Line Analysis)

**Use Case**: Pinpoint exact lines causing slowdowns

**Installation**:
```bash
pip install line_profiler
```

**Usage**:
```python
# Add @profile decorator to target function
@profile
def process_tasks(task_ids):
    for task_id in task_ids:
        task = get_task(task_id)  # Hot path?
        validate_task(task)       # Hot path?
        store_task(task)          # Hot path?
```

**Run**:
```bash
kernprof -l -v cf_cli.py
```

**Output**:
```text
Line #  Hits   Time    Per Hit  % Time  Line Contents
=======================================================
    12     100   8500     85.0    42.5   task = get_task(task_id)
    13     100   4200     42.0    21.0   validate_task(task)
    14     100   7300     73.0    36.5   store_task(task)
```

**Optimization Target**: Lines with >10% total time

---

#### 3. memory_profiler (Memory Usage)

**Use Case**: Track memory consumption and detect leaks

**Installation**:
```bash
pip install memory_profiler
```

**Usage**:
```python
from memory_profiler import profile

@profile
def load_large_dataset():
    data = []
    for i in range(100000):
        data.append({"id": i, "payload": "x" * 1000})
    return data
```

**Run**:
```bash
python -m memory_profiler cf_cli.py
```

**Output**:
```text
Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    10     50.2 MiB     50.2 MiB           1   @profile
    11     50.2 MiB      0.0 MiB           1   def load_large_dataset():
    12     50.2 MiB      0.0 MiB           1       data = []
    13    145.8 MiB     95.6 MiB      100001       for i in range(100000):
    14    145.8 MiB      0.0 MiB      100000           data.append(...)
```

**Red Flags**: Increments >50MB without deallocation

---

#### 4. py-spy (Production Sampling Profiler)

**Use Case**: Profile running production processes without overhead

**Installation**:
```bash
pip install py-spy
```

**Usage**:
```bash
# Attach to running process
py-spy top --pid 12345

# Generate flamegraph
py-spy record -o profile.svg --pid 12345 --duration 60
```

**Advantages**:
- No code changes required
- Minimal performance impact (<1%)
- Works with production systems

---

### PowerShell Profiling

#### Measure-Command (Simple Timing)

```powershell
# Time a script block
$duration = Measure-Command {
    Import-Module ContextForge.Spectre
    Initialize-ContextForgeSpectre
}

Write-Host "Initialization took $($duration.TotalMilliseconds)ms"
logger.info("module_load_time", duration_ms=$duration.TotalMilliseconds)
```

---

#### Profiler Module (Advanced)

```powershell
# Enable profiling
$profile = Start-PSProfile

# Run target code
Import-Module MyModule
Invoke-MyFunction

# Analyze results
$results = Stop-PSProfile -Profiler $profile
$results | Sort-Object Duration -Descending | Select-Object -First 10
```

---

### Database Query Profiling

#### PostgreSQL EXPLAIN ANALYZE

```sql
-- Analyze query execution plan
EXPLAIN ANALYZE
SELECT t.*, s.name AS sprint_name
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id
WHERE t.status = 'in_progress'
  AND t.priority >= 3
ORDER BY t.created_at DESC
LIMIT 20;
```

**Output Analysis**:
```text
Limit  (cost=0.43..45.67 rows=20 width=512) (actual time=0.045..0.892 rows=20 loops=1)
  ->  Nested Loop Left Join  (cost=0.43..2045.67 rows=905 width=512) (actual time=0.044..0.889 rows=20 loops=1)
        ->  Index Scan using idx_tasks_status_priority on tasks t  (cost=0.29..1234.56 rows=905 width=480)
              Index Cond: ((status = 'in_progress') AND (priority >= 3))
        ->  Index Scan using sprints_pkey on sprints s  (cost=0.14..0.89 rows=1 width=32)
Planning Time: 0.345 ms
Execution Time: 0.923 ms  ✅ Meets <20ms target
```

**Red Flags**:
- Seq Scan on large tables
- actual time >> estimated cost
- High loop counts in nested loops

---

## Benchmarking Framework

### pytest-benchmark (Python)

**Installation**:
```bash
pip install pytest-benchmark
```

**Usage**:
```python
# tests/benchmarks/test_task_operations.py
import pytest
from cf_cli.tasks import TaskManager

@pytest.fixture
def task_manager():
    return TaskManager(db_url="postgresql://localhost/taskman_v2")

def test_list_tasks_performance(benchmark, task_manager):
    """Benchmark task listing operation."""
    result = benchmark(task_manager.list_tasks, status="in_progress")

    # Assertions on result
    assert len(result) > 0

    # Performance assertion
    assert benchmark.stats['mean'] < 0.150  # <150ms mean

def test_create_task_performance(benchmark, task_manager):
    """Benchmark task creation."""
    task_data = {
        "title": "Benchmark test task",
        "description": "Performance testing",
        "priority": 3,
        "status": "todo"
    }

    result = benchmark(task_manager.create_task, **task_data)
    assert result['id']
    assert benchmark.stats['mean'] < 0.200  # <200ms mean
```

**Run Benchmarks**:
```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only

# Compare against baseline
pytest tests/benchmarks/ --benchmark-compare=0001

# Generate report
pytest tests/benchmarks/ --benchmark-autosave --benchmark-save-data
```

**Output**:
```text
--------------------------------------------------------------------------------------- benchmark: 2 tests ---------------------------------------------------------------------------------------
Name (time in ms)                          Min                 Max                Mean            StdDev              Median               IQR            Outliers     OPS            Rounds  Iterations
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_create_task_performance           125.4892 (1.0)      198.7621 (1.0)      142.3456 (1.0)     15.2341 (1.0)      138.9012 (1.0)      12.4567 (1.0)          2;3  7.0254 (1.0)          10           1
test_list_tasks_performance             89.2341 (1.41)     156.8923 (1.27)     102.4567 (1.39)    12.8934 (1.18)      98.7654 (1.41)      10.2345 (1.22)         1;2  9.7602 (0.72)         10           1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

---

### Locust Load Testing (API)

**Installation**:
```bash
pip install locust
```

**Configuration** (`locustfile.py`):
```python
from locust import HttpUser, task, between

class TaskManUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user think time

    def on_start(self):
        """Login and get auth token."""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        self.token = response.json()["access_token"]

    @task(3)  # Weight: 3x more frequent than create
    def list_tasks(self):
        """GET /api/v1/tasks"""
        self.client.get(
            "/api/v1/tasks?status=in_progress",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def create_task(self):
        """POST /api/v1/tasks"""
        self.client.post(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "title": "Load test task",
                "priority": 3,
                "status": "todo"
            }
        )

    @task(2)
    def get_task_detail(self):
        """GET /api/v1/tasks/{id}"""
        # Assume task_id from previous list response
        self.client.get(
            f"/api/v1/tasks/TASK-TEST-001",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Run Load Test**:
```bash
# Web UI mode
locust -f locustfile.py --host=http://localhost:8000

# Headless mode (CI/CD)
locust -f locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless \
       --csv=results/load_test --html=results/report.html
```

**Metrics Collected**:
- Request count and failure rate
- Response time percentiles (p50, p95, p99)
- Requests per second (RPS)
- Concurrent users supported

---

### Lighthouse (Frontend)

**Installation**:
```bash
npm install -g lighthouse
```

**Run Audit**:
```bash
# Full audit
lighthouse http://localhost:5000 \
          --output html \
          --output-path ./reports/lighthouse-report.html \
          --chrome-flags="--headless"

# Performance-only
lighthouse http://localhost:5000 \
          --only-categories=performance \
          --output json \
          --output-path ./reports/perf.json
```

**CI/CD Integration**:
```yaml
# .github/workflows/performance.yml
- name: Run Lighthouse
  uses: treosh/lighthouse-ci-action@v9
  with:
    urls: |
      http://localhost:5000
      http://localhost:5000/tasks
    budgetPath: ./lighthouse-budget.json
    uploadArtifacts: true
```

**Budget File** (`lighthouse-budget.json`):
```json
[
  {
    "path": "/*",
    "timings": [
      {
        "metric": "first-contentful-paint",
        "budget": 1500
      },
      {
        "metric": "largest-contentful-paint",
        "budget": 2500
      },
      {
        "metric": "interactive",
        "budget": 3500
      }
    ],
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 250
      },
      {
        "resourceType": "total",
        "budget": 500
      }
    ]
  }
]
```

---

## DuckDB Velocity Integration

### Velocity-Driven Planning

**Philosophy**: Use **proven velocity data** to generate realistic optimization timelines

**Baseline** (as of 2025-11-10):
- **Velocity Rate**: 0.23 hours per story point
- **Data Source**: 14 story points, 3.25 actual hours, 3 completed tasks
- **Confidence**: Medium (60-90%)

---

### Optimization Story Pointing

**Story Point Guidelines** (Fibonacci):

| Story Points | Complexity | Example Optimization |
|--------------|------------|---------------------|
| **1** | Trivial | Add database index, enable caching flag |
| **2** | Simple | Optimize single function, reduce loop complexity |
| **3** | Medium | Refactor module structure, implement memoization |
| **5** | Complex | Database query redesign, async processing |
| **8** | Very Complex | API architecture refactor, introduce CDN |
| **13** | Epic | Complete CLI consolidation, migrate database |

---

### Time Estimation Formula

```python
# python/velocity/velocity_tracker.py

def predict_optimization_time(story_points: int, complexity_multiplier: float = 1.0):
    """
    Predict optimization completion time using DuckDB velocity data.

    Args:
        story_points: Fibonacci estimate (1, 2, 3, 5, 8, 13)
        complexity_multiplier: Adjustment factor (0.8-1.5)
            - 0.8: Similar work recently completed
            - 1.0: Standard complexity
            - 1.2: Novel approach or technology
            - 1.5: High risk, unproven technique

    Returns:
        dict with estimated_hours, estimated_days, confidence_percentage
    """
    BASELINE_HOURS_PER_POINT = 0.23  # From DuckDB velocity.duckdb

    estimated_hours = story_points * BASELINE_HOURS_PER_POINT * complexity_multiplier
    estimated_days = estimated_hours / 8  # Assuming 8-hour workday

    # Confidence decreases with complexity and story points
    base_confidence = 85  # Medium confidence baseline
    confidence_penalty = (story_points - 3) * 5  # Larger tasks = lower confidence
    complexity_penalty = (complexity_multiplier - 1.0) * 20

    confidence = max(40, base_confidence - confidence_penalty - complexity_penalty)

    return {
        "estimated_hours": round(estimated_hours, 1),
        "estimated_days": round(estimated_days, 1),
        "confidence_percentage": int(confidence),
        "base_hours_per_point": BASELINE_HOURS_PER_POINT,
        "complexity_multiplier": complexity_multiplier
    }
```

**Example Usage**:
```python
# Estimate: Optimize API list endpoint (5 points, standard complexity)
result = predict_optimization_time(story_points=5, complexity_multiplier=1.0)
# Output: {'estimated_hours': 1.2, 'estimated_days': 0.1, 'confidence_percentage': 75}

# Estimate: CLI consolidation Phase 2 (13 points, high complexity)
result = predict_optimization_time(story_points=13, complexity_multiplier=1.3)
# Output: {'estimated_hours': 3.9, 'estimated_days': 0.5, 'confidence_percentage': 40}
```

---

### Recording Optimization Velocity

**After completing optimization work**:

```bash
# Record session in DuckDB
python -m velocity.velocity_tracker record \
  --task-id "OPT-API-P95-001" \
  --story-points 5 \
  --actual-hours 1.1 \
  --lines-changed 230 \
  --files-modified 4 \
  --complexity-score 2
```

**Effect**: Updates velocity baseline for future predictions

---

## Optimization Workflows

### UTMW Approach (Understand → Trust → Measure → Validate → Work)

#### Phase 1: Understand (Baseline)

**Objective**: Establish current performance baseline

**Actions**:
1. Run profiling tools (cProfile, line_profiler)
2. Execute benchmarks (pytest-benchmark, Locust)
3. Collect metrics (Prometheus, database query stats)
4. Document baseline in evidence bundle

**Example**:
```bash
# Profile current API performance
python -m cProfile -o baseline.stats backend-api/main.py

# Run benchmarks
pytest tests/benchmarks/ --benchmark-autosave --benchmark-save-data

# Load test
locust -f locustfile.py --users 50 --spawn-rate 5 --run-time 3m --headless --csv=baseline

# Evidence bundle
tar -czf EB-PERF-BASELINE-20251111.tar.gz baseline.stats .benchmarks/ baseline_*.csv
sha256sum EB-PERF-BASELINE-20251111.tar.gz > EB-PERF-BASELINE-20251111.sha256
```

---

#### Phase 2: Trust (Identify Hot Paths)

**Objective**: Identify the critical 20% to optimize (Golden Ratio)

**Analysis**:
```python
import pstats

# Load profiling data
stats = pstats.Stats('baseline.stats')
stats.sort_stats('cumtime')

# Identify top 20% of cumulative time
stats.print_stats(0.20)  # Top 20% of functions
```

**Output**:
```text
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      150    0.230    0.002    1.800    0.012 unified_logger.py:45(ulog)
       45    0.680    0.015    0.680    0.015 {psycopg2.connect}
       12    0.050    0.004    0.450    0.038 tasks.py:89(list_tasks)
```

**Decision**: Focus on `psycopg2.connect` (680ms) and `list_tasks` (450ms)

---

#### Phase 3: Measure (Story Point Estimation)

**Objective**: Estimate optimization effort using DuckDB velocity

**Task Breakdown**:

| Task | Story Points | Complexity | Est. Hours | Priority |
|------|--------------|------------|------------|----------|
| Connection pooling (psycopg2) | 3 | 1.0 | 0.7h | P0 |
| Add index on tasks.status | 1 | 0.8 | 0.2h | P0 |
| Optimize list_tasks query | 5 | 1.2 | 1.4h | P1 |

**Total Estimate**: 2.3 hours (velocity-adjusted)

---

#### Phase 4: Validate (Apply & Benchmark)

**Objective**: Apply optimizations and validate improvements

**Optimization 1: Connection Pooling**
```python
# Before
conn = psycopg2.connect(DATABASE_URL)

# After
from psycopg2.pool import ThreadedConnectionPool

pool = ThreadedConnectionPool(5, 20, DATABASE_URL)
conn = pool.getconn()
```

**Benchmark**:
```bash
pytest tests/benchmarks/test_connection_perf.py --benchmark-compare=baseline
```

**Result**:
```text
Name                              Min (before)    Min (after)    Improvement
test_connection_acquire           680.0ms         12.5ms         54.4x faster  ✅
```

---

**Optimization 2: Database Index**
```sql
CREATE INDEX CONCURRENTLY idx_tasks_status ON tasks(status);
```

**Benchmark**:
```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'in_progress';
-- Before: Seq Scan (450ms)
-- After: Index Scan (8ms)  ✅ 56x faster
```

---

#### Phase 5: Work (Record Velocity)

**Objective**: Capture actual completion data for future estimates

```bash
# Record completed optimization
python -m velocity.velocity_tracker record \
  --task-id "OPT-CONNECTION-POOL" \
  --story-points 3 \
  --actual-hours 0.8 \
  --lines-changed 45 \
  --files-modified 2 \
  --complexity-score 2

# Updated velocity: 0.23 → 0.24 hrs/point (14 → 17 points, 3.25 → 4.05 hours)
```

---

### Continuous Optimization Loop

```text
┌─────────────────────────────────────────────────────┐
│  1. Monitor Production Metrics (Prometheus/Grafana) │
│     - API latency, database query time, error rate   │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  2. Trigger Alerts (SLO Violations)                  │
│     - p95 latency > 200ms for 5 minutes              │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  3. Create Optimization Ticket                       │
│     - Priority based on impact (P0 for user-facing)  │
│     - Estimate story points using velocity data      │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  4. Execute UTMW Workflow                            │
│     - Understand → Trust → Measure → Validate → Work│
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  5. Validate & Record Velocity                       │
│     - Confirm metrics improvement                    │
│     - Update DuckDB with actual completion data      │
└────────────────┬────────────────────────────────────┘
                 ↓
                Loop
```

---

## Sacred Geometry Patterns

### Triangle (Stable Foundation)

**Application**: Establish reliable performance baselines

**Requirements**:
- Automated benchmarking in CI/CD
- Historical trend tracking (30-day rolling window)
- Reproducible profiling methodology

**Example**:
```yaml
# .github/workflows/performance.yml
name: Performance Baseline
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday 2am

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - name: Run benchmarks
        run: pytest tests/benchmarks/ --benchmark-autosave

      - name: Upload baseline
        uses: actions/upload-artifact@v3
        with:
          name: performance-baseline
          path: .benchmarks/
```

---

### Spiral (Iterative Enhancement)

**Application**: Progressive optimization through cycles

**Cycle Structure**:
1. **Iteration 1**: Quick wins (1-2 point tasks, <1 hour)
2. **Iteration 2**: Medium complexity (3-5 points, 1-2 hours)
3. **Iteration 3**: Architectural changes (8-13 points, 2-4 hours)

**Velocity Tracking**: Each iteration refines velocity baseline

---

### Golden Ratio (20/80 Focus)

**Application**: Pareto principle for optimization prioritization

**Process**:
1. Profile entire codebase
2. Sort functions by cumulative time
3. Select top 20% (φ ratio)
4. Optimize only those functions
5. Expect 80% total improvement

**Validation**: Re-profile and confirm 80% improvement achieved

---

### Fractal (Modular Reuse)

**Application**: Reusable optimization patterns across services

**Pattern Library**:
- **Connection Pooling**: Apply to all database clients
- **Caching Layer**: Redis/Memcached for all read-heavy APIs
- **Query Optimization**: Index strategy templates
- **Async Processing**: Celery task queue pattern

**Example**:
```python
# Fractal pattern: Connection pool module
# cf_core/infrastructure/db_pool.py

class ConnectionPool:
    """Reusable connection pooling pattern."""

    def __init__(self, db_url: str, min_conn: int = 5, max_conn: int = 20):
        self.pool = ThreadedConnectionPool(min_conn, max_conn, db_url)

    def get_connection(self):
        return self.pool.getconn()

    def release_connection(self, conn):
        self.pool.putconn(conn)

# Reuse across cf_cli, TaskMan-v2, QSE framework
```

---

## Evidence & Reporting

### Evidence Bundle Structure

```text
EB-PERF-{TASK_ID}-{TIMESTAMP}.tar.gz
├── baseline/
│   ├── profile.stats           # cProfile output
│   ├── memory.log              # memory_profiler output
│   ├── benchmark_results.json  # pytest-benchmark
│   └── load_test_baseline.csv  # Locust results
├── optimized/
│   ├── profile.stats
│   ├── benchmark_results.json
│   └── load_test_optimized.csv
├── comparison/
│   └── improvement_report.md   # Summary of improvements
└── metadata.yaml               # Task info, velocity data
```

**SHA-256 Integrity**:
```bash
sha256sum EB-PERF-OPT-API-001-20251111.tar.gz > EB-PERF-OPT-API-001-20251111.sha256
```

---

### Optimization Report Template

```markdown
# Optimization Report: {Task ID}

**Date**: 2025-11-11
**Engineer**: Context Forge Team
**Task**: OPT-API-P95-001 - Reduce API p95 latency

## Baseline Metrics

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| API p95 latency | 450ms | <200ms | ❌ Exceeds target |
| Database query time | 380ms | <100ms | ❌ Exceeds target |
| Connection acquisition | 680ms | <50ms | ❌ Exceeds target |

## Story Points & Velocity

- **Estimated Story Points**: 5
- **Complexity Multiplier**: 1.0
- **Predicted Hours**: 1.2h (using 0.23 hrs/point baseline)
- **Actual Hours**: 1.1h
- **Variance**: -0.1h (8% under estimate) ✅

## Optimizations Applied

### 1. Connection Pooling (3 story points)
- **Change**: Implemented ThreadedConnectionPool (5-20 connections)
- **Files Modified**: `backend-api/database.py`, `backend-api/config.py`
- **Lines Changed**: 45
- **Improvement**: 680ms → 12.5ms (54.4x faster)

### 2. Database Index (1 story point)
- **Change**: `CREATE INDEX idx_tasks_status ON tasks(status)`
- **Query Improvement**: 450ms → 8ms (56x faster)

### 3. Query Optimization (1 story point)
- **Change**: Removed N+1 query pattern in `list_tasks()`
- **Improvement**: 3 queries → 1 query with JOIN

## Post-Optimization Metrics

| Metric | Baseline | Optimized | Improvement | Target Met |
|--------|----------|-----------|-------------|------------|
| API p95 latency | 450ms | 78ms | 5.8x faster | ✅ |
| Database query time | 380ms | 12ms | 31.7x faster | ✅ |
| Connection acquisition | 680ms | 12.5ms | 54.4x faster | ✅ |

## Evidence Bundle

- **Path**: `EB-PERF-OPT-API-001-20251111.tar.gz`
- **SHA-256**: `a3f2c8d9...` (see .sha256 file)
- **Size**: 2.4 MB

## Velocity Update

- **Previous Baseline**: 0.23 hrs/point (14 points, 3.25 hours)
- **Updated Baseline**: 0.23 hrs/point (19 points, 4.35 hours)
- **Confidence**: Medium → High (70%)

## Recommendations

1. Apply connection pooling pattern to all database clients (Fractal reuse)
2. Review all queries for index opportunities (automated analysis)
3. Establish p95 latency SLO monitoring in Prometheus
```

---

## Best Practices

### 1. Always Measure First

**Principle**: "Premature optimization is the root of all evil" - Donald Knuth

**Workflow**:
```bash
# Step 1: Profile before changing code
python -m cProfile -o before.stats cf_cli.py

# Step 2: Make optimization
# ... code changes ...

# Step 3: Profile after changes
python -m cProfile -o after.stats cf_cli.py

# Step 4: Compare results
python -c "
import pstats
before = pstats.Stats('before.stats')
after = pstats.Stats('after.stats')
# Compare cumtime for target function
"
```

---

### 2. Use Production-Like Data

**Principle**: Benchmarks with toy data are misleading

**Best Practices**:
- Load test with 10,000+ tasks (realistic database size)
- Use actual user query patterns (extracted from logs)
- Test with production hardware specs

**Example**:
```python
# Generate production-like test data
import random
from datetime import datetime, timedelta

def generate_realistic_tasks(count=10000):
    statuses = ["todo", "in_progress", "completed", "blocked"]
    priorities = [1, 2, 3, 4, 5]

    for i in range(count):
        yield {
            "id": f"TASK-{i:06d}",
            "title": f"Task {i}",
            "status": random.choice(statuses),
            "priority": random.choice(priorities),
            "created_at": datetime.now() - timedelta(days=random.randint(0, 365))
        }
```

---

### 3. Automate Regression Detection

**Principle**: Performance regressions should fail CI/CD

**pytest-benchmark CI Integration**:
```yaml
# .github/workflows/performance.yml
- name: Run benchmarks
  run: |
    pytest tests/benchmarks/ \
      --benchmark-compare=origin/main \
      --benchmark-compare-fail=mean:10%  # Fail if >10% slower
```

---

### 4. Log All Optimization Work

**Principle**: UCL requires evidence for all context changes

**Implementation**:
```python
# Log optimization context
from python.unified_logger import ulog

ulog("optimization_start", "api_latency_reduction", "INFO",
     task_id="OPT-API-P95-001",
     baseline_p95_ms=450,
     target_p95_ms=200,
     story_points=5,
     estimated_hours=1.2)

# ... perform optimization ...

ulog("optimization_complete", "api_latency_reduction", "INFO",
     task_id="OPT-API-P95-001",
     optimized_p95_ms=78,
     improvement_factor=5.8,
     actual_hours=1.1,
     evidence_bundle="EB-PERF-OPT-API-001-20251111.tar.gz")
```

---

### 5. Share Optimization Patterns (Fractal Reuse)

**Principle**: Successful optimizations should be reusable modules

**Pattern Library** (`cf_core/optimization/patterns/`):
```text
patterns/
├── connection_pooling.py      # Database connection pools
├── caching_layer.py           # Redis/Memcached integration
├── query_optimization.py      # Common SQL patterns
├── async_processing.py        # Celery task queue setup
└── rate_limiting.py           # API rate limiting
```

**Documentation**: Each pattern includes:
- Use case description
- Before/after examples
- Benchmark results
- Integration guide

---

## Related Documents

- **[03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md)** - UCL compliance and evidence requirements
- **[05-Database-Design-Implementation.md](05-Database-Design-Implementation.md)** - Database optimization strategies
- **[09-Development-Guidelines.md](09-Development-Guidelines.md)** - Code quality standards
- **[13-Testing-Validation.md](13-Testing-Validation.md)** - Performance testing integration
- **[15-Future-Roadmap.md](15-Future-Roadmap.md)** - P1-009 Performance Optimization Initiative
- **[DuckDB-Velocity-Tracker.md](DuckDB-Velocity-Tracker.md)** - Velocity tracking system documentation

---

**For professional philosophy guidance, see [ContextForge Work Codex](Codex/CODEX.md)**
