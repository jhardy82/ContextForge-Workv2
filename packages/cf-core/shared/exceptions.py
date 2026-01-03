"""
Custom Exceptions for CF Core

Domain-specific exceptions that provide better error context than generic exceptions.
"""


class NotFoundException(Exception):
    """
    Raised when a requested entity is not found in the repository.

    This exception indicates the entity ID was valid but no matching entity exists.
    Distinct from validation errors (invalid ID format) or permission errors.
    """

    def __init__(self, entity_type: str, entity_id: str):
        """
        Initialize NotFoundException with entity details.

        Args:
            entity_type: Type of entity that wasn't found (e.g., "Task", "Sprint")
            entity_id: ID of the entity that wasn't found

        Example:
            raise NotFoundException("Task", "T-abc123")
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID '{entity_id}' not found")
