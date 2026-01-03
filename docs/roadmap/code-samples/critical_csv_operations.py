"""
Critical CSV Operations - Fixed Implementation

This module provides the corrected CSV operations that fix the critical data integrity
issues in the original dbcli.py implementation.

USAGE:
    from code_samples.critical_csv_operations import CSVOperations

    csv_ops = CSVOperations("./trackers/csv")
    tasks = csv_ops.load_entities("tasks")
    csv_ops.save_entities("tasks", tasks)
"""

import csv
import logging
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


class CSVOperations:
    """
    Production-ready CSV operations with atomic writes, error handling, and backup.

    This class replaces the broken CSV operations in the original dbcli.py with
    robust, transaction-safe implementations.
    """

    def __init__(self, csv_root: Path):
        """
        Initialize CSV operations handler.

        Args:
            csv_root: Root directory for CSV files
        """
        self.csv_root = Path(csv_root)
        self.csv_root.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Default schema definitions
        self.schemas = {
            "tasks": [
                "id",
                "project_id",
                "sprint_id",
                "title",
                "summary",
                "status",
                "priority",
                "severity",
                "assignees",
                "estimate_points",
                "actual_hours",
                "created_at",
                "updated_at",
                "depends_on",
                "blocks",
                "labels",
                "risk_notes",
                "last_health",
                "last_heartbeat_utc",
                "audit_tag",
                "notes",
                "correlation_hint",
                "schema_version",
                "batch_id",
                "task_sequence",
                "critical_path",
                "risk_level",
                "mitigation_status",
                "target_date",
                "done_date",
                "content_hash",
                "eff_priority",
                "work_type",
                "verification_requirements",
                "validation_state",
                "origin_source",
                "load_group",
                "context_objects",
                "context_dimensions",
                "geometry_shape",
                "shape_stage",
                "aar_count",
                "last_aar_utc",
                "misstep_count",
                "last_misstep_utc",
                "evidence_required",
                "evidence_emitted",
                "execution_trace_log",
            ],
            "sprints": [
                "id",
                "project_id",
                "title",
                "start_date",
                "end_date",
                "status",
                "goal",
                "risk_summary",
                "created_at",
                "updated_at",
                "audit_tag",
                "schema_version",
                "batch_id",
                "sprint_sequence",
                "committed_points",
                "capacity_points",
                "carried_over_points",
                "task_count_expected",
                "total_estimate_points_expected",
                "validation_state",
                "origin_source",
                "load_group",
                "context_objects",
                "context_dimensions",
                "geometry_shape",
                "sprint_aar_count",
                "last_aar_utc",
                "misstep_count",
                "last_misstep_utc",
                "evidence_required_tasks",
                "evidence_emitted_tasks",
                "execution_trace_log",
            ],
            "projects": [
                "id",
                "title",
                "description",
                "owner",
                "status",
                "kpi_primary",
                "kpi_secondary",
                "risk_top",
                "mitigation_top",
                "start_date",
                "end_date",
                "created_at",
                "updated_at",
                "notes",
                "risk_level",
                "mitigation_status",
                "schema_version",
                "audit_tag",
            ],
        }

    @contextmanager
    def atomic_write(self, file_path: Path):
        """
        Context manager for atomic file writes.

        Writes to a temporary file first, then atomically renames to target.
        Includes automatic backup and rollback on failure.

        Args:
            file_path: Target file path

        Yields:
            Path to temporary file for writing
        """
        temp_file = file_path.with_suffix(".tmp")
        backup_file = file_path.with_suffix(".backup")

        try:
            # Create backup if original exists
            if file_path.exists():
                shutil.copy2(file_path, backup_file)
                self.logger.debug(f"Created backup: {backup_file}")

            yield temp_file

            # Atomic rename (safe on most filesystems)
            temp_file.replace(file_path)
            self.logger.debug(f"Atomic write completed: {file_path}")

            # Remove backup on success
            if backup_file.exists():
                backup_file.unlink()

        except Exception as e:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

            # Restore from backup if needed
            if backup_file.exists() and not file_path.exists():
                shutil.copy2(backup_file, file_path)
                self.logger.warning(f"Restored from backup due to write failure: {e}")

            raise

    def load_entities(self, entity_type: str) -> list[dict[str, Any]]:
        """
        Load entities from CSV file with comprehensive error handling.

        Args:
            entity_type: Type of entity (tasks, sprints, projects)

        Returns:
            List of entity dictionaries

        Raises:
            ValueError: If entity_type is invalid
            IOError: If file cannot be read
        """
        if entity_type not in self.schemas:
            raise ValueError(f"Unknown entity type: {entity_type}")

        csv_file = self.csv_root / f"{entity_type}.csv"
        entities = []

        if not csv_file.exists():
            self.logger.info(f"CSV file does not exist, returning empty list: {csv_file}")
            return entities

        try:
            with open(csv_file, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                entities = [dict(row) for row in reader]

            self.logger.info(f"Loaded {len(entities)} {entity_type} from {csv_file}")

        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error reading {csv_file}: {e}")
            raise OSError(f"File encoding error: {e}")

        except csv.Error as e:
            self.logger.error(f"CSV parsing error in {csv_file}: {e}")
            raise OSError(f"CSV format error: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error loading {csv_file}: {e}")
            raise OSError(f"Failed to load {entity_type}: {e}")

        return entities

    def save_entities(self, entity_type: str, entities: list[dict[str, Any]]) -> None:
        """
        Save entities to CSV file with atomic operations and validation.

        Args:
            entity_type: Type of entity (tasks, sprints, projects)
            entities: List of entity dictionaries to save

        Raises:
            ValueError: If entity_type is invalid or data is malformed
            IOError: If file cannot be written
        """
        if entity_type not in self.schemas:
            raise ValueError(f"Unknown entity type: {entity_type}")

        csv_file = self.csv_root / f"{entity_type}.csv"

        # Determine headers
        if entities:
            # Use union of entity keys and schema to handle missing fields
            entity_headers = set()
            for entity in entities:
                entity_headers.update(entity.keys())

            # Ensure schema fields are included
            schema_headers = set(self.schemas[entity_type])
            headers = list(schema_headers.union(entity_headers))

            # Validate critical fields exist
            if entity_type == "tasks" and "id" not in entity_headers:
                raise ValueError("Tasks must have 'id' field")

        else:
            # Use schema defaults for empty entity list
            headers = self.schemas[entity_type]

        try:
            with self.atomic_write(csv_file) as temp_file:
                with open(temp_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()

                    for entity in entities:
                        # Ensure all fields are present with empty string defaults
                        normalized_entity = {
                            header: str(entity.get(header, "")) for header in headers
                        }
                        writer.writerow(normalized_entity)

            self.logger.info(f"Saved {len(entities)} {entity_type} to {csv_file}")

        except OSError as e:
            self.logger.error(f"IO error saving {csv_file}: {e}")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error saving {csv_file}: {e}")
            raise OSError(f"Failed to save {entity_type}: {e}")

    def ensure_file_exists(self, entity_type: str) -> None:
        """
        Ensure CSV file exists with proper headers.

        Args:
            entity_type: Type of entity (tasks, sprints, projects)
        """
        if entity_type not in self.schemas:
            raise ValueError(f"Unknown entity type: {entity_type}")

        csv_file = self.csv_root / f"{entity_type}.csv"

        if not csv_file.exists():
            headers = self.schemas[entity_type]

            try:
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

                self.logger.info(f"Created {entity_type}.csv with headers")

            except Exception as e:
                self.logger.error(f"Failed to create {csv_file}: {e}")
                raise OSError(f"Cannot create {entity_type} file: {e}")

    def backup_all_files(self, backup_suffix: str | None = None) -> list[Path]:
        """
        Create backups of all CSV files.

        Args:
            backup_suffix: Optional suffix for backup files (default: timestamp)

        Returns:
            List of backup file paths created
        """
        if backup_suffix is None:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_files = []

        for entity_type in self.schemas:
            csv_file = self.csv_root / f"{entity_type}.csv"

            if csv_file.exists():
                backup_file = self.csv_root / f"{entity_type}.csv.backup_{backup_suffix}"

                try:
                    shutil.copy2(csv_file, backup_file)
                    backup_files.append(backup_file)
                    self.logger.info(f"Created backup: {backup_file}")

                except Exception as e:
                    self.logger.error(f"Failed to backup {csv_file}: {e}")

        return backup_files

    def validate_file_integrity(self, entity_type: str) -> dict[str, Any]:
        """
        Validate CSV file integrity and structure.

        Args:
            entity_type: Type of entity to validate

        Returns:
            Dictionary with validation results
        """
        csv_file = self.csv_root / f"{entity_type}.csv"

        result = {
            "entity_type": entity_type,
            "file_path": str(csv_file),
            "exists": csv_file.exists(),
            "readable": False,
            "valid_structure": False,
            "record_count": 0,
            "missing_headers": [],
            "extra_headers": [],
            "errors": [],
        }

        if not result["exists"]:
            result["errors"].append("File does not exist")
            return result

        try:
            # Test readability
            entities = self.load_entities(entity_type)
            result["readable"] = True
            result["record_count"] = len(entities)

            # Check structure if file has content
            if entities:
                entity_headers = set(entities[0].keys())
                schema_headers = set(self.schemas[entity_type])

                result["missing_headers"] = list(schema_headers - entity_headers)
                result["extra_headers"] = list(entity_headers - schema_headers)
                result["valid_structure"] = len(result["missing_headers"]) == 0
            else:
                result["valid_structure"] = True  # Empty file is valid

        except Exception as e:
            result["errors"].append(str(e))

        return result


# Example usage and testing
def main():
    """Example usage of the CSVOperations class"""

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize CSV operations
    csv_ops = CSVOperations("./test_data")

    # Ensure files exist
    csv_ops.ensure_file_exists("tasks")

    # Create some test data
    test_tasks = [
        {
            "id": "T-20250827-test001",
            "title": "Test Task 1",
            "summary": "First test task",
            "status": "planned",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "schema_version": "2.0",
        },
        {
            "id": "T-20250827-test002",
            "title": "Test Task 2",
            "summary": "Second test task",
            "status": "active",
            "priority": "high",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "schema_version": "2.0",
        },
    ]

    # Save test data
    print("Saving test tasks...")
    csv_ops.save_entities("tasks", test_tasks)

    # Load and verify
    print("Loading tasks...")
    loaded_tasks = csv_ops.load_entities("tasks")
    print(f"Loaded {len(loaded_tasks)} tasks")

    for task in loaded_tasks:
        print(f"  {task['id']}: {task['title']} ({task['status']})")

    # Validate integrity
    print("Validating file integrity...")
    validation = csv_ops.validate_file_integrity("tasks")
    print(f"Validation result: {validation}")

    # Create backup
    print("Creating backup...")
    backups = csv_ops.backup_all_files()
    print(f"Created {len(backups)} backup files")


if __name__ == "__main__":
    main()
