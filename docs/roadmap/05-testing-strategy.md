# Testing Strategy: Comprehensive Quality Assurance

## 🎯 Testing Philosophy

Implement a comprehensive testing strategy that ensures data integrity, performance, and user experience while supporting rapid development and continuous deployment.

## 📋 Testing Pyramid

### Unit Tests (70% of test coverage)
**Purpose**: Validate individual components in isolation
**Target Coverage**: 85% of code
**Execution Time**: <30 seconds total

### Integration Tests (20% of test coverage)
**Purpose**: Validate component interactions and data flow
**Target Coverage**: All critical workflows
**Execution Time**: <2 minutes total

### End-to-End Tests (10% of test coverage)
**Purpose**: Validate complete user workflows
**Target Coverage**: Happy path and critical error scenarios
**Execution Time**: <5 minutes total

## 🔧 Test Implementation Framework

### Testing Tools & Frameworks

```python
# test requirements
pytest==7.4.0                    # Primary testing framework
pytest-cov==4.1.0               # Coverage reporting
pytest-mock==3.11.1             # Mocking utilities
pytest-asyncio==0.21.1          # Async testing support
pytest-benchmark==4.0.0         # Performance benchmarking
hypothesis==6.82.0               # Property-based testing
factory-boy==3.3.0              # Test data generation
freezegun==1.2.2                # Date/time mocking
responses==0.23.3               # HTTP mocking
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=dbcli
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
    --benchmark-only
    --benchmark-sort=mean
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Tests that take longer than 1 second
    critical: Tests for critical functionality
```

## 🧪 Unit Testing Strategy

### Data Layer Unit Tests

#### Repository Tests

```python
# tests/unit/data/repositories/test_task_repository.py
import pytest
from unittest.mock import Mock, patch
from dbcli.data.repositories.task_repo import TaskRepository
from dbcli.data.models.task import Task

class TestTaskRepository:
    """Test task repository operations"""

    @pytest.fixture
    def mock_csv_handler(self):
        """Mock CSV handler for isolated testing"""
        return Mock()

    @pytest.fixture
    def mock_validator(self):
        """Mock validator for isolated testing"""
        return Mock()

    @pytest.fixture
    def task_repo(self, mock_csv_handler, mock_validator):
        """Task repository with mocked dependencies"""
        return TaskRepository(mock_csv_handler, mock_validator)

    def test_find_by_id_existing_task(self, task_repo, mock_csv_handler):
        """Test finding an existing task by ID"""
        # Given
        mock_tasks = [
            {"id": "T-001", "title": "Test Task 1"},
            {"id": "T-002", "title": "Test Task 2"}
        ]
        mock_csv_handler.load_entities.return_value = mock_tasks

        # When
        result = task_repo.find_by_id("T-001")

        # Then
        assert result is not None
        assert result["id"] == "T-001"
        assert result["title"] == "Test Task 1"
        mock_csv_handler.load_entities.assert_called_once_with("tasks")

    def test_find_by_id_nonexistent_task(self, task_repo, mock_csv_handler):
        """Test finding a non-existent task by ID"""
        # Given
        mock_csv_handler.load_entities.return_value = []

        # When
        result = task_repo.find_by_id("T-999")

        # Then
        assert result is None

    def test_save_new_task(self, task_repo, mock_csv_handler, mock_validator):
        """Test saving a new task"""
        # Given
        new_task = {"id": "T-003", "title": "New Task"}
        existing_tasks = [{"id": "T-001", "title": "Existing Task"}]
        mock_csv_handler.load_entities.return_value = existing_tasks

        # When
        task_repo.save(new_task)

        # Then
        mock_validator.validate.assert_called_once_with(new_task)
        expected_tasks = existing_tasks + [new_task]
        mock_csv_handler.save_entities.assert_called_once_with("tasks", expected_tasks)

    def test_save_update_existing_task(self, task_repo, mock_csv_handler, mock_validator):
        """Test updating an existing task"""
        # Given
        updated_task = {"id": "T-001", "title": "Updated Task"}
        existing_tasks = [{"id": "T-001", "title": "Original Task"}]
        mock_csv_handler.load_entities.return_value = existing_tasks

        # When
        task_repo.save(updated_task)

        # Then
        mock_validator.validate.assert_called_once_with(updated_task)
        expected_tasks = [updated_task]
        mock_csv_handler.save_entities.assert_called_once_with("tasks", expected_tasks)

    def test_delete_existing_task(self, task_repo, mock_csv_handler):
        """Test deleting an existing task"""
        # Given
        existing_tasks = [
            {"id": "T-001", "title": "Task 1"},
            {"id": "T-002", "title": "Task 2"}
        ]
        mock_csv_handler.load_entities.return_value = existing_tasks

        # When
        result = task_repo.delete("T-001")

        # Then
        assert result is True
        expected_tasks = [{"id": "T-002", "title": "Task 2"}]
        mock_csv_handler.save_entities.assert_called_once_with("tasks", expected_tasks)

    def test_delete_nonexistent_task(self, task_repo, mock_csv_handler):
        """Test deleting a non-existent task"""
        # Given
        existing_tasks = [{"id": "T-001", "title": "Task 1"}]
        mock_csv_handler.load_entities.return_value = existing_tasks

        # When
        result = task_repo.delete("T-999")

        # Then
        assert result is False
        mock_csv_handler.save_entities.assert_not_called()
```

#### Model Validation Tests

```python
# tests/unit/data/models/test_task.py
import pytest
from datetime import datetime
from dbcli.data.models.task import Task

class TestTaskModel:
    """Test Task model validation and behavior"""

    def test_task_creation_with_valid_data(self):
        """Test creating a task with valid data"""
        # Given/When
        task = Task(
            title="Test Task",
            summary="Test summary",
            status="planned",
            priority="high"
        )

        # Then
        assert task.title == "Test Task"
        assert task.summary == "Test summary"
        assert task.status == "planned"
        assert task.priority == "high"
        assert isinstance(task.created_at, datetime)
        assert task.schema_version == "2.0"

    def test_task_creation_with_empty_title_raises_error(self):
        """Test that empty title raises validation error"""
        # Given/When/Then
        with pytest.raises(ValueError, match="Title is required"):
            Task(title="")

    def test_task_creation_with_invalid_status_raises_error(self):
        """Test that invalid status raises validation error"""
        # Given/When/Then
        with pytest.raises(ValueError, match="Invalid status"):
            Task(title="Test", status="invalid_status")

    def test_task_to_dict_conversion(self):
        """Test converting task to dictionary for CSV storage"""
        # Given
        task = Task(title="Test Task", status="active")

        # When
        task_dict = task.to_dict()

        # Then
        assert isinstance(task_dict, dict)
        assert task_dict["title"] == "Test Task"
        assert task_dict["status"] == "active"
        assert "created_at" in task_dict
        assert isinstance(task_dict["created_at"], str)  # ISO format

    @pytest.mark.parametrize("status", ["planned", "active", "blocked", "review", "done", "closed"])
    def test_task_valid_statuses(self, status):
        """Test all valid task statuses"""
        # Given/When
        task = Task(title="Test", status=status)

        # Then
        assert task.status == status

    @pytest.mark.parametrize("priority", ["low", "medium", "high", "critical"])
    def test_task_valid_priorities(self, priority):
        """Test all valid task priorities"""
        # Given/When
        task = Task(title="Test", priority=priority)

        # Then
        assert task.priority == priority
```

### Service Layer Unit Tests

#### Business Logic Tests

```python
# tests/unit/services/test_task_service.py
import pytest
from unittest.mock import Mock, patch
from dbcli.services.task_service import TaskService
from dbcli.core.exceptions import TaskNotFoundError

class TestTaskService:
    """Test task service business logic"""

    @pytest.fixture
    def mock_task_repo(self):
        """Mock task repository"""
        return Mock()

    @pytest.fixture
    def task_service(self, mock_task_repo):
        """Task service with mocked dependencies"""
        return TaskService(mock_task_repo)

    def test_create_task_success(self, task_service, mock_task_repo):
        """Test successful task creation"""
        # Given
        task_data = {
            "title": "New Task",
            "summary": "Test summary",
            "status": "planned"
        }

        # When
        result = task_service.create_task(task_data)

        # Then
        assert result.title == "New Task"
        mock_task_repo.save.assert_called_once()

    def test_create_task_with_duplicate_check(self, task_service, mock_task_repo):
        """Test task creation with duplicate checking"""
        # Given
        task_data = {
            "title": "Duplicate Task",
            "check_duplicates": True
        }

        with patch.object(task_service, 'find_similar_tasks') as mock_similar:
            mock_similar.return_value = [{"title": "Similar Task"}]

            # When
            result = task_service.create_task(task_data)

            # Then
            mock_similar.assert_called_once_with("Duplicate Task")
            assert result is not None

    def test_update_task_success(self, task_service, mock_task_repo):
        """Test successful task update"""
        # Given
        existing_task = {"id": "T-001", "title": "Original", "status": "planned"}
        updates = {"title": "Updated", "status": "active"}
        mock_task_repo.find_by_id.return_value = existing_task

        # When
        result = task_service.update_task("T-001", updates)

        # Then
        assert result.title == "Updated"
        assert result.status == "active"
        mock_task_repo.save.assert_called_once()

    def test_update_nonexistent_task_raises_error(self, task_service, mock_task_repo):
        """Test updating non-existent task raises error"""
        # Given
        mock_task_repo.find_by_id.return_value = None

        # When/Then
        with pytest.raises(TaskNotFoundError):
            task_service.update_task("T-999", {"title": "Updated"})
```

## 🔄 Integration Testing Strategy

### Data Flow Integration Tests

```python
# tests/integration/test_task_workflow.py
import pytest
import tempfile
from pathlib import Path
from dbcli.data.repositories.task_repo import TaskRepository
from dbcli.data.storage.csv_handler import CSVHandler
from dbcli.services.task_service import TaskService

class TestTaskWorkflow:
    """Test complete task workflow integration"""

    @pytest.fixture
    def temp_csv_dir(self):
        """Temporary directory for CSV files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def csv_handler(self, temp_csv_dir):
        """CSV handler with temporary directory"""
        return CSVHandler(temp_csv_dir)

    @pytest.fixture
    def task_repo(self, csv_handler):
        """Task repository with real CSV handler"""
        from dbcli.data.validation.validators import TaskValidator
        validator = TaskValidator()
        return TaskRepository(csv_handler, validator)

    @pytest.fixture
    def task_service(self, task_repo):
        """Task service with real dependencies"""
        return TaskService(task_repo)

    def test_complete_task_lifecycle(self, task_service, temp_csv_dir):
        """Test complete task creation, update, and deletion"""
        # Create task
        task = task_service.create_task({
            "title": "Integration Test Task",
            "summary": "Test complete workflow",
            "status": "planned",
            "priority": "medium"
        })

        # Verify task was created
        assert task.id is not None
        assert task.title == "Integration Test Task"

        # Verify file was created
        csv_file = temp_csv_dir / "tasks.csv"
        assert csv_file.exists()

        # Update task
        updated_task = task_service.update_task(task.id, {
            "status": "active",
            "priority": "high"
        })

        # Verify updates
        assert updated_task.status == "active"
        assert updated_task.priority == "high"

        # Verify persistence
        loaded_task = task_service.get_task(task.id)
        assert loaded_task.status == "active"
        assert loaded_task.priority == "high"

    def test_concurrent_task_operations(self, task_service):
        """Test handling concurrent operations"""
        import threading

        results = []
        errors = []

        def create_task(index):
            try:
                task = task_service.create_task({
                    "title": f"Concurrent Task {index}",
                    "status": "planned"
                })
                results.append(task.id)
            except Exception as e:
                errors.append(e)

        # Create multiple tasks concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert len(set(results)) == 10  # All unique IDs
```

### Database Integrity Tests

```python
# tests/integration/test_data_integrity.py
import pytest
from dbcli.data.storage.csv_handler import CSVHandler

class TestDataIntegrity:
    """Test data integrity and transaction safety"""

    def test_atomic_write_operations(self, temp_csv_dir):
        """Test that write operations are atomic"""
        csv_handler = CSVHandler(temp_csv_dir)

        # Create initial data
        tasks = [{"id": "T-001", "title": "Task 1"}]
        csv_handler.save_entities("tasks", tasks)

        # Simulate write failure
        with patch('builtins.open', side_effect=IOError("Simulated failure")):
            with pytest.raises(IOError):
                csv_handler.save_entities("tasks", [{"id": "T-002", "title": "Task 2"}])

        # Verify original data is intact
        loaded_tasks = csv_handler.load_entities("tasks")
        assert len(loaded_tasks) == 1
        assert loaded_tasks[0]["id"] == "T-001"

    def test_backup_and_recovery(self, temp_csv_dir):
        """Test backup creation and recovery"""
        csv_handler = CSVHandler(temp_csv_dir)

        # Create initial data
        original_tasks = [{"id": "T-001", "title": "Original Task"}]
        csv_handler.save_entities("tasks", original_tasks)

        # Verify backup was created
        backup_files = list(temp_csv_dir.glob("*.backup"))
        # Implementation-specific verification

        # Test recovery mechanism
        # Implementation-specific recovery test
```

## 🏃‍♂️ End-to-End Testing Strategy

### CLI Command Tests

```python
# tests/e2e/test_cli_commands.py
import pytest
from typer.testing import CliRunner
from dbcli.main import app

class TestCLICommands:
    """Test complete CLI command workflows"""

    @pytest.fixture
    def runner(self):
        """CLI test runner"""
        return CliRunner()

    def test_task_creation_workflow(self, runner, temp_csv_dir):
        """Test complete task creation via CLI"""
        # Test task creation
        result = runner.invoke(app, [
            "task", "create",
            "Test CLI Task",
            "--description", "Created via CLI",
            "--status", "planned",
            "--priority", "medium",
            "--csv-root", str(temp_csv_dir)
        ])

        assert result.exit_code == 0
        assert "Created task" in result.stdout

        # Extract task ID from output
        task_id = None  # Parse from output

        # Test task listing
        result = runner.invoke(app, [
            "task", "list",
            "--csv-root", str(temp_csv_dir)
        ])

        assert result.exit_code == 0
        assert "Test CLI Task" in result.stdout

        # Test task details
        result = runner.invoke(app, [
            "task", "show", task_id,
            "--csv-root", str(temp_csv_dir)
        ])

        assert result.exit_code == 0
        assert "Test CLI Task" in result.stdout
        assert "Created via CLI" in result.stdout

    def test_error_handling_workflow(self, runner, temp_csv_dir):
        """Test error handling in CLI commands"""
        # Test invalid task creation
        result = runner.invoke(app, [
            "task", "create", "",  # Empty title
            "--csv-root", str(temp_csv_dir)
        ])

        assert result.exit_code != 0
        assert "error" in result.stdout.lower()

        # Test non-existent task
        result = runner.invoke(app, [
            "task", "show", "T-NONEXISTENT",
            "--csv-root", str(temp_csv_dir)
        ])

        assert result.exit_code != 0
        assert "not found" in result.stdout.lower()
```

## 📊 Performance Testing Strategy

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest
from dbcli.services.task_service import TaskService

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.benchmark
    def test_task_creation_performance(self, benchmark, task_service):
        """Benchmark task creation performance"""

        def create_task():
            return task_service.create_task({
                "title": "Benchmark Task",
                "status": "planned"
            })

        result = benchmark(create_task)
        assert result.id is not None

    @pytest.mark.benchmark
    def test_bulk_task_query_performance(self, benchmark, task_service):
        """Benchmark bulk query performance"""

        # Setup: Create 1000 tasks
        for i in range(1000):
            task_service.create_task({
                "title": f"Task {i}",
                "status": "planned" if i % 2 == 0 else "active"
            })

        def query_tasks():
            return task_service.list_tasks(status="planned", limit=100)

        result = benchmark(query_tasks)
        assert len(result) <= 100

    @pytest.mark.slow
    def test_large_dataset_performance(self, task_service):
        """Test performance with large datasets"""

        # Create 10,000 tasks
        import time
        start_time = time.time()

        for i in range(10000):
            task_service.create_task({
                "title": f"Large Dataset Task {i}",
                "status": "planned"
            })

        creation_time = time.time() - start_time

        # Query performance
        start_time = time.time()
        results = task_service.list_tasks(limit=1000)
        query_time = time.time() - start_time

        # Assertions
        assert creation_time < 60  # Should complete in under 1 minute
        assert query_time < 5      # Should query in under 5 seconds
        assert len(results) <= 1000
```

## 🛡️ Security Testing Strategy

### Data Validation Security Tests

```python
# tests/security/test_data_validation.py
import pytest
from dbcli.services.task_service import TaskService

class TestSecurityValidation:
    """Test security aspects of data validation"""

    def test_csv_injection_prevention(self, task_service):
        """Test prevention of CSV injection attacks"""
        malicious_inputs = [
            "=cmd|' /C calc'!A0",
            "@SUM(1+1)*cmd|' /C calc'!A0",
            "+cmd|' /C calc'!A0",
            "-cmd|' /C calc'!A0",
            '=1+1+cmd|"/C calc"',
        ]

        for malicious_input in malicious_inputs:
            # Should either sanitize or reject
            try:
                task = task_service.create_task({
                    "title": malicious_input,
                    "status": "planned"
                })
                # If creation succeeds, verify sanitization
                assert not task.title.startswith(('=', '+', '-', '@'))
            except ValueError:
                # Rejection is also acceptable
                pass

    def test_path_traversal_prevention(self, csv_handler):
        """Test prevention of path traversal attacks"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "../../../../../../../../etc/shadow",
        ]

        for malicious_path in malicious_paths:
            with pytest.raises(ValueError):
                csv_handler.load_entities(malicious_path)

    def test_large_input_handling(self, task_service):
        """Test handling of excessively large inputs"""
        large_title = "A" * 10000  # 10KB title

        with pytest.raises(ValueError, match="too long"):
            task_service.create_task({
                "title": large_title,
                "status": "planned"
            })
```

## 📈 Test Metrics & Reporting

### Coverage Requirements
- **Unit Tests**: 85% line coverage minimum
- **Integration Tests**: 100% of critical workflows
- **E2E Tests**: 100% of user-facing commands
- **Performance Tests**: All operations under load

### Quality Gates

```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: |
          pytest tests/unit --cov=dbcli --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration

      - name: Run performance benchmarks
        run: |
          pytest tests/performance --benchmark-only

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Test Data Management

```python
# tests/fixtures/factories.py
import factory
from datetime import datetime
from dbcli.data.models.task import Task

class TaskFactory(factory.Factory):
    """Factory for creating test tasks"""

    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Test Task {n}")
    summary = factory.Faker('text', max_nb_chars=100)
    status = factory.Faker('random_element', elements=['planned', 'active', 'done'])
    priority = factory.Faker('random_element', elements=['low', 'medium', 'high'])
    created_at = factory.Faker('date_time_this_year')

# Usage in tests
def test_with_multiple_tasks():
    tasks = TaskFactory.create_batch(10)
    # Test with realistic data
```

---

**Testing Strategy Version**: 1.0
**Last Updated**: August 27, 2025
**Coverage Target**: 85% minimum
**Execution Time**: <10 minutes for full suite
