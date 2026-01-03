"""Performance validation script for ActionList schema migration.

Tests query performance after migration to ensure:
- Get by ID: P50 < 5ms
- List queries: P50 < 20ms
- Containment queries (task_ids): P50 < 20ms
- FK join queries: P50 < 50ms

Usage:
    python validate_action_list_performance.py --connection-string postgresql://user:pass@host:port/db
"""

import argparse
import asyncio
import statistics
import time
from typing import Any

import asyncpg


async def measure_query(conn: asyncpg.Connection, query: str, params: dict[str, Any] | None = None) -> float:
    """Execute query and measure execution time in milliseconds."""
    start = time.perf_counter()
    await conn.fetch(query, *(params.values() if params else []))
    end = time.perf_counter()
    return (end - start) * 1000  # Convert to ms


async def validate_performance(connection_string: str) -> dict[str, dict[str, float]]:
    """Run performance validation tests and return metrics."""
    conn = await asyncpg.connect(connection_string)

    try:
        # Ensure test data exists
        await conn.execute(
            """
            INSERT INTO action_lists (id, name, status, task_ids, owner, priority)
            VALUES
                ('AL-TEST-001', 'Test List 1', 'active', ARRAY['TASK-001', 'TASK-002'], 'testuser', 'high'),
                ('AL-TEST-002', 'Test List 2', 'active', ARRAY['TASK-003'], 'testuser', 'medium'),
                ('AL-TEST-003', 'Test List 3', 'completed', ARRAY['TASK-001', 'TASK-004'], 'testuser', 'low')
            ON CONFLICT (id) DO NOTHING
            """
        )

        results = {}

        # Test 1: Get by ID (should use primary key index)
        print("Testing: Get by ID (P50 < 5ms target)...")
        timings = []
        for _ in range(100):
            t = await measure_query(conn, "SELECT * FROM action_lists WHERE id = $1", {"id": "AL-TEST-001"})
            timings.append(t)
        results["get_by_id"] = {
            "p50": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],
            "p99": statistics.quantiles(timings, n=100)[98],
            "target_p50": 5.0,
        }
        print(f"  ✅ P50: {results['get_by_id']['p50']:.2f}ms, P95: {results['get_by_id']['p95']:.2f}ms")

        # Test 2: List by status (should use ix_action_lists_status)
        print("Testing: List by status (P50 < 20ms target)...")
        timings = []
        for _ in range(100):
            t = await measure_query(conn, "SELECT * FROM action_lists WHERE status = $1", {"status": "active"})
            timings.append(t)
        results["list_by_status"] = {
            "p50": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],
            "p99": statistics.quantiles(timings, n=100)[98],
            "target_p50": 20.0,
        }
        print(f"  ✅ P50: {results['list_by_status']['p50']:.2f}ms, P95: {results['list_by_status']['p95']:.2f}ms")

        # Test 3: Containment query (should use GIN index ix_action_lists_task_ids)
        print("Testing: Task containment query (P50 < 20ms target)...")
        timings = []
        for _ in range(100):
            t = await measure_query(
                conn, "SELECT * FROM action_lists WHERE $1 = ANY(task_ids)", {"task_id": "TASK-001"}
            )
            timings.append(t)
        results["task_containment"] = {
            "p50": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],
            "p99": statistics.quantiles(timings, n=100)[98],
            "target_p50": 20.0,
        }
        print(f"  ✅ P50: {results['task_containment']['p50']:.2f}ms, P95: {results['task_containment']['p95']:.2f}ms")

        # Test 4: Composite index query (status + priority)
        print("Testing: Status + priority query (P50 < 20ms target)...")
        timings = []
        for _ in range(100):
            t = await measure_query(
                conn,
                "SELECT * FROM action_lists WHERE status = $1 AND priority = $2",
                {"status": "active", "priority": "high"},
            )
            timings.append(t)
        results["status_priority"] = {
            "p50": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],
            "p99": statistics.quantiles(timings, n=100)[98],
            "target_p50": 20.0,
        }
        print(f"  ✅ P50: {results['status_priority']['p50']:.2f}ms, P95: {results['status_priority']['p95']:.2f}ms")

        # Test 5: Foreign key join query
        print("Testing: FK join query (P50 < 50ms target)...")
        timings = []
        for _ in range(100):
            t = await measure_query(
                conn,
                """
                SELECT al.*, p.title as project_title
                FROM action_lists al
                LEFT JOIN projects p ON al.project_id = p.id
                WHERE al.status = $1
                """,
                {"status": "active"},
            )
            timings.append(t)
        results["fk_join"] = {
            "p50": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],
            "p99": statistics.quantiles(timings, n=100)[98],
            "target_p50": 50.0,
        }
        print(f"  ✅ P50: {results['fk_join']['p50']:.2f}ms, P95: {results['fk_join']['p95']:.2f}ms")

        # Test 6: Verify indexes exist
        print("\nVerifying indexes...")
        indexes = await conn.fetch(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'action_lists'
            ORDER BY indexname
            """
        )
        print(f"  Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"    - {idx['indexname']}")

        # Cleanup test data
        await conn.execute("DELETE FROM action_lists WHERE id LIKE 'AL-TEST-%'")

        return results

    finally:
        await conn.close()


def check_performance_gates(results: dict[str, dict[str, float]]) -> bool:
    """Check if all performance targets are met."""
    print("\n" + "=" * 60)
    print("PERFORMANCE VALIDATION RESULTS")
    print("=" * 60)

    all_passed = True
    for test_name, metrics in results.items():
        p50 = metrics["p50"]
        target = metrics["target_p50"]
        passed = p50 < target
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"\n{test_name}:")
        print(f"  P50: {p50:.2f}ms (target: <{target}ms) {status}")
        print(f"  P95: {metrics['p95']:.2f}ms")
        print(f"  P99: {metrics['p99']:.2f}ms")

        if not passed:
            all_passed = False
            print("  ⚠️  Performance degradation detected!")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL PERFORMANCE GATES PASSED")
    else:
        print("❌ SOME PERFORMANCE GATES FAILED")
    print("=" * 60)

    return all_passed


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate ActionList schema migration performance")
    parser.add_argument(
        "--connection-string",
        default="postgresql://contextforge:contextforge@172.25.14.122:5432/taskman_v2",
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()

    print("Starting performance validation...")
    print(f"Connection: {args.connection_string}")
    print()

    try:
        results = await validate_performance(args.connection_string)
        passed = check_performance_gates(results)
        exit(0 if passed else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(2)


if __name__ == "__main__":
    asyncio.run(main())
