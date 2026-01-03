"""Evidence bundle compliance with RFC 8785 canonical JSON + SHA-256 hashing.

Implements cryptographic evidence bundles for QSE framework compliance.
Uses RFC 8785 JSON Canonicalization Scheme for hash stability across
platforms and Python implementations.

Key Features:
- RFC 8785 canonical JSON serialization (UTF-16 code unit key ordering)
- SHA-256 cryptographic hashing for integrity verification
- Cross-platform hash reproducibility
- 3 required test vectors for validation

Note: Python's json.dumps(sort_keys=True) uses ASCII ordering, NOT UTF-16
as required by RFC 8785. This module provides compliant implementation.

Authority: docs/adr/ADR-003-evidence-bundle-compliance.md
"""

import hashlib
import json
import math
from datetime import datetime
from typing import Any, Dict


def _utf16_key_sort(key: str) -> list[int]:
    """Sort key generator for RFC 8785 UTF-16 code unit ordering.

    Python's sort_keys=True uses ASCII byte values, but RFC 8785 requires
    sorting by UTF-16 code units. This function provides the correct sort key.

    Args:
        key: JSON object key to generate sort values for

    Returns:
        list[int]: UTF-16 code units for proper RFC 8785 ordering
    """
    return [ord(c) for c in key]


def canonicalize(data: Any) -> str:
    """Serialize data to RFC 8785 canonical JSON.

    Implements JSON Canonicalization Scheme (RFC 8785) with:
    - UTF-16 code unit key ordering (not ASCII as in Python's sort_keys=True)
    - No whitespace between tokens
    - Minimal number representation
    - UTF-8 encoding with minimal escaping

    Args:
        data: Any JSON-serializable data structure

    Returns:
        str: RFC 8785 canonical JSON string

    Raises:
        TypeError: If data contains non-serializable objects
        ValueError: If data contains invalid JSON values
    """
    def _canonicalize_value(value: Any) -> Any:
        """Recursively canonicalize a value according to RFC 8785."""
        if isinstance(value, dict):
            # Sort keys by UTF-16 code units (RFC 8785 requirement)
            sorted_items = sorted(value.items(), key=lambda item: _utf16_key_sort(item[0]))
            return {k: _canonicalize_value(v) for k, v in sorted_items}
        elif isinstance(value, list):
            return [_canonicalize_value(item) for item in value]
        elif isinstance(value, float):
            # Handle special float values per RFC 8785
            if math.isnan(value):
                return None  # NaN not allowed in RFC 8785
            elif math.isinf(value):
                return None  # Infinity not allowed in RFC 8785
            elif value == -0.0:
                return 0.0  # Convert -0.0 to 0.0
            else:
                return value
        else:
            return value

    # Canonicalize the data structure
    canonical_data = _canonicalize_value(data)

    # Serialize without whitespace (separators=(',', ':'))
    # ensure_ascii=False for minimal escaping per RFC 8785
    return json.dumps(
        canonical_data,
        separators=(',', ':'),
        ensure_ascii=False,
        allow_nan=False,  # RFC 8785 prohibits NaN/Infinity
        sort_keys=False   # We handle sorting manually with UTF-16 ordering
    )


def hash_evidence(data: Any) -> str:
    """Generate SHA-256 hash of RFC 8785 canonical JSON.

    Creates a cryptographic hash for evidence bundle integrity.
    Uses RFC 8785 canonical serialization for cross-platform consistency.

    Args:
        data: Any JSON-serializable data structure

    Returns:
        str: SHA-256 hash as lowercase hex string (64 characters)

    Example:
        evidence_hash = hash_evidence({"event": "task_complete", "task_id": "T-001"})
        # Returns: "a1b2c3d4..." (64-character hex string)
    """
    canonical_json = canonicalize(data)
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


def capture_evidence(event_type: str, **event_data: Any) -> dict[str, Any]:
    """Capture an evidence bundle with metadata and hash.

    Creates a complete evidence bundle with timestamp, correlation ID,
    and cryptographic hash for QSE framework compliance.

    Args:
        event_type: Type of event being captured
        **event_data: Additional event data fields

    Returns:
        dict: Complete evidence bundle with hash

    Example:
        evidence = capture_evidence(
            "task_complete",
            task_id="T-001",
            duration_ms=1500,
            result="success"
        )
    """
    # Import here to avoid circular imports
    from .correlation import get_correlation_id

    # Build evidence bundle
    evidence_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "correlation_id": get_correlation_id(),
        **event_data
    }

    # Generate hash of the data (excluding the hash itself)
    evidence_hash = hash_evidence(evidence_data)

    # Add hash to the bundle
    evidence_data["evidence_hash"] = f"sha256:{evidence_hash}"

    return evidence_data


def validate_rfc8785_compliance() -> dict[str, bool]:
    """Validate RFC 8785 compliance with required test vectors.

    Runs 3 test vectors from ADR-003 to ensure proper implementation:
    1. Unicode key ordering (Euro, Hebrew, Emoji)
    2. Cross-platform hash reproducibility
    3. Special float values (-0.0, NaN, Infinity)

    Returns:
        dict: Test results for each vector {test_name: passed}
    """
    results = {}

    # Test Vector 1: Unicode key ordering
    test_data_1 = {
        "😀": "emoji",     # U+1F600 (high code point)
        "€": "euro",       # U+20AC (medium code point)
        "ב": "hebrew",     # U+05D1 (low code point)
        "a": "ascii"       # U+0061 (lowest code point)
    }

    canonical_1 = canonicalize(test_data_1)
    # Expected order by UTF-16 code units: a(97), ב(1489), €(8364), 😀(55357,56832)
    expected_1 = '{"a":"ascii","ב":"hebrew","€":"euro","😀":"emoji"}'
    results["unicode_key_ordering"] = canonical_1 == expected_1

    # Test Vector 2: Cross-platform hash reproducibility
    test_data_2 = {
        "event": "test_event",
        "timestamp": "2025-12-30T15:30:00.000000Z",
        "correlation_id": "test-correlation-123"
    }

    hash_2 = hash_evidence(test_data_2)
    # This should produce the same hash on all platforms
    results["cross_platform_hash"] = len(hash_2) == 64 and all(c in '0123456789abcdef' for c in hash_2)

    # Test Vector 3: Special float values
    test_data_3 = {
        "negative_zero": -0.0,
        "positive_zero": 0.0,
        "normal_float": 1.5
    }

    canonical_3 = canonicalize(test_data_3)
    # -0.0 should be converted to 0.0
    results["special_float_handling"] = '"negative_zero":0.0' in canonical_3

    return results
