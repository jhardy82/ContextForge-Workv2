"""
Performance Validator Agent

Validates performance and scalability of task operations.
"""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from cf_core.shared.result import Result
from cf_core.validation.base_agent import BaseValidationAgent


class PerformanceValidatorAgent(BaseValidationAgent):
    """Validates performance characteristics"""

    # Performance thresholds
    THRESHOLDS = {
        "create_100_tasks": 5.0,  # 5 seconds
        "list_1000_tasks": 1.0,  # 1 second
        "update_task": 0.1,  # 100ms
        "query_filtered": 0.5,  # 500ms
        "concurrent_creates": 10.0,  # 10 seconds for 10 concurrent
    }

    def validate(self) -> Result[dict[str, Any]]:
        """Execute all performance validation tests"""
        try:
            self._benchmark_create_operations()
            self._benchmark_read_operations()
            self._benchmark_update_operations()
            self._benchmark_query_performance()
            self._benchmark_concurrent_operations()

            report = self._generate_report()
            self._emit_evidence(report)

            return Result.success(report)
        except Exception as e:
            return Result.failure(f"Performance validation failed: {e}")

    def _benchmark_create_operations(self):
        """Benchmark task creation"""
        num_tasks = 100
        start_time = time.time()

        conn = self._get_connection()
        try:
            for i in range(num_tasks):
                task_id = f"T-PERF-{uuid.uuid4().hex[:8]}"
                conn.execute(
                    """
                    INSERT INTO tasks (id, title, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, f"Performance Test {i}", "new", self._utc_now(), self._utc_now()),
                )
            conn.commit()
        finally:
            conn.close()

        duration = time.time() - start_time
        threshold = self.THRESHOLDS["create_100_tasks"]

        self._record_test_result(
            test_name="benchmark_create_100_tasks",
            passed=duration < threshold,
            expected=f"< {threshold}s",
            actual=f"{duration:.3f}s",
            severity="normal" if duration < threshold else "warning",
            details=f"Created {num_tasks} tasks in {duration:.3f} seconds",
        )

    def _benchmark_read_operations(self):
        """Benchmark task listing"""
        # First ensure we have tasks to read
        task_count = self._get_task_count()

        if task_count < 100:
            # Create some test tasks
            conn = self._get_connection()
            try:
                for i in range(100):
                    task_id = f"T-READ-{uuid.uuid4().hex[:8]}"
                    conn.execute(
                        """
                        INSERT INTO tasks (id, title, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (task_id, f"Read Test {i}", "new", self._utc_now(), self._utc_now()),
                    )
                conn.commit()
            finally:
                conn.close()

        # Benchmark list operation
        start_time = time.time()
        rows = self._execute_query("""
            SELECT * FROM tasks WHERE deleted_at IS NULL LIMIT 1000
        """)
        duration = time.time() - start_time

        threshold = self.THRESHOLDS["list_1000_tasks"]

        self._record_test_result(
            test_name="benchmark_list_1000_tasks",
            passed=duration < threshold,
            expected=f"< {threshold}s",
            actual=f"{duration:.3f}s",
            severity="normal" if duration < threshold else "warning",
            details=f"Listed {len(rows)} tasks in {duration:.3f} seconds",
        )

    def _benchmark_update_operations(self):
        """Benchmark task updates"""
        # Create test task
        task_id = f"T-UPD-{uuid.uuid4().hex[:8]}"
        conn = self._get_connection()

        try:
            conn.execute(
                """
                INSERT INTO tasks (id, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, "Update Benchmark", "new", self._utc_now(), self._utc_now()),
            )
            conn.commit()

            # Benchmark update
            start_time = time.time()
            conn.execute(
                """
                UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?
                """,
                ("in_progress", self._utc_now(), task_id),
            )
            conn.commit()
            duration = time.time() - start_time

            threshold = self.THRESHOLDS["update_task"]

            self._record_test_result(
                test_name="benchmark_update_task",
                passed=duration < threshold,
                expected=f"< {threshold}s",
                actual=f"{duration:.3f}s",
                severity="normal" if duration < threshold else "warning",
                details=f"Updated task in {duration:.3f} seconds",
            )
        finally:
            conn.close()

    def _benchmark_query_performance(self):
        """Benchmark filtered queries"""
        start_time = time.time()
        rows = self._execute_query("""
            SELECT * FROM tasks
            WHERE status = 'new'
              AND deleted_at IS NULL
        """)
        duration = time.time() - start_time

        threshold = self.THRESHOLDS["query_filtered"]

        self._record_test_result(
            test_name="benchmark_query_filtered",
            passed=duration < threshold,
            expected=f"< {threshold}s",
            actual=f"{duration:.3f}s",
            severity="normal" if duration < threshold else "warning",
            details=f"Filtered query returned {len(rows)} tasks in {duration:.3f} seconds",
        )

    def _benchmark_concurrent_operations(self):
        """Benchmark concurrent task operations"""
        num_concurrent = 10

        def create_task(index):
            """Create a task (runs in thread)"""
            task_id = f"T-CONC-{uuid.uuid4().hex[:8]}"
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                    INSERT INTO tasks (id, title, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, f"Concurrent Test {index}", "new", self._utc_now(), self._utc_now()),
                )
                conn.commit()
                return True
            except Exception:
                return False
            finally:
                conn.close()

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(create_task, i) for i in range(num_concurrent)]
            results = [f.result() for f in as_completed(futures)]

        duration = time.time() - start_time
        threshold = self.THRESHOLDS["concurrent_creates"]
        success_count = sum(1 for r in results if r)

        self._record_test_result(
            test_name="benchmark_concurrent_creates",
            passed=duration < threshold and success_count == num_concurrent,
            expected=f"< {threshold}s, {num_concurrent} successful",
            actual=f"{duration:.3f}s, {success_count} successful",
            severity="normal" if duration < threshold else "warning",
            details=f"{success_count}/{num_concurrent} concurrent creates in {duration:.3f} seconds",
        )
