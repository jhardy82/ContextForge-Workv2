"""
Unicode normalization utilities for consistent text processing.

Provides comprehensive Unicode normalization with support for all standard forms
(NFC, NFD, NFKC, NFKD) and performance optimization for batch processing.
"""

import logging
import time
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class NormalizationForm(Enum):
    """Unicode normalization forms."""
    NFC = "NFC"    # Canonical Decomposition, followed by Canonical Composition
    NFD = "NFD"    # Canonical Decomposition
    NFKC = "NFKC"  # Compatibility Decomposition, followed by Canonical Composition
    NFKD = "NFKD"  # Compatibility Decomposition

@dataclass
class NormalizationResult:
    """Result of Unicode normalization operation."""
    original_text: str
    normalized_text: str
    form: NormalizationForm
    changed: bool
    character_count: int
    byte_count_before: int
    byte_count_after: int
    processing_time_ms: float
    issues: list[str]

class UnicodeNormalizer:
    """
    High-performance Unicode text normalizer with comprehensive form support.

    Features:
    - All standard normalization forms (NFC, NFD, NFKC, NFKD)
    - Batch processing optimization
    - Detailed result reporting
    - Issue detection and reporting
    """

    def __init__(self, default_form: NormalizationForm = NormalizationForm.NFC):
        """
        Initialize normalizer with default form.

        Args:
            default_form: Default normalization form to use
        """
        self.default_form = default_form
        self._stats = {
            "total_processed": 0,
            "total_changed": 0,
            "total_time_ms": 0.0,
        }

    def normalize(
        self,
        text: str,
        form: NormalizationForm | None = None,
        detect_issues: bool = True
    ) -> NormalizationResult:
        """
        Normalize Unicode text using specified form.

        Args:
            text: Input text to normalize
            form: Normalization form (uses default if None)
            detect_issues: Whether to detect and report Unicode issues

        Returns:
            NormalizationResult with detailed information
        """
        start_time = time.perf_counter()

        if form is None:
            form = self.default_form

        # Convert input to string if needed
        if not isinstance(text, str):
            text = str(text)

        # Store original metrics
        byte_count_before = len(text.encode('utf-8'))

        # Perform normalization
        normalized = unicodedata.normalize(form.value, text)

        # Calculate metrics
        byte_count_after = len(normalized.encode('utf-8'))
        changed = text != normalized
        character_count = len(normalized)
        processing_time = (time.perf_counter() - start_time) * 1000

        # Detect issues if requested
        issues = []
        if detect_issues:
            issues = self._detect_issues(text, normalized, form)

        # Update stats
        self._stats["total_processed"] += 1
        if changed:
            self._stats["total_changed"] += 1
        self._stats["total_time_ms"] += processing_time

        return NormalizationResult(
            original_text=text,
            normalized_text=normalized,
            form=form,
            changed=changed,
            character_count=character_count,
            byte_count_before=byte_count_before,
            byte_count_after=byte_count_after,
            processing_time_ms=processing_time,
            issues=issues
        )

    def normalize_batch(
        self,
        texts: list[str],
        form: NormalizationForm | None = None,
        detect_issues: bool = True,
        progress_callback: Callable | None = None
    ) -> list[NormalizationResult]:
        """
        Normalize multiple texts with progress tracking.

        Args:
            texts: List of texts to normalize
            form: Normalization form (uses default if None)
            detect_issues: Whether to detect issues
            progress_callback: Function called with (current, total) progress

        Returns:
            List of NormalizationResult objects
        """
        results = []
        total = len(texts)

        for i, text in enumerate(texts):
            result = self.normalize(text, form, detect_issues)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total)

        logger.info(f"Normalized {total} texts, {sum(1 for r in results if r.changed)} changed")

        return results

    def normalize_file(
        self,
        file_path: str | Path,
        output_path: str | Path | None = None,
        form: NormalizationForm | None = None,
        encoding: str = "utf-8"
    ) -> NormalizationResult:
        """
        Normalize text in a file.

        Args:
            file_path: Path to input file
            output_path: Path to output file (overwrites input if None)
            form: Normalization form
            encoding: File encoding

        Returns:
            NormalizationResult for the file content
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        with file_path.open('r', encoding=encoding) as f:
            content = f.read()

        # Normalize content
        result = self.normalize(content, form)

        # Write to output file if content changed or output path specified
        if result.changed or output_path:
            output_path = Path(output_path) if output_path else file_path
            with output_path.open('w', encoding=encoding) as f:
                f.write(result.normalized_text)

        logger.info(f"Normalized file {file_path} -> {output_path if output_path else 'in-place'}")

        return result

    def _detect_issues(self, original: str, normalized: str, form: NormalizationForm) -> list[str]:
        """
        Detect potential Unicode normalization issues.

        Args:
            original: Original text
            normalized: Normalized text
            form: Normalization form used

        Returns:
            List of issue descriptions
        """
        issues = []

        # Check for length changes that might indicate problems
        if len(original) != len(normalized):
            issues.append(f"Length changed: {len(original)} -> {len(normalized)}")

        # Check for byte size changes
        orig_bytes = len(original.encode('utf-8'))
        norm_bytes = len(normalized.encode('utf-8'))
        if orig_bytes != norm_bytes:
            byte_change = ((norm_bytes - orig_bytes) / orig_bytes) * 100
            issues.append(f"Byte size changed: {orig_bytes} -> {norm_bytes} ({byte_change:+.1f}%)")

        # Check for specific problematic patterns
        if any(ord(c) > 0x10000 for c in normalized):
            issues.append("Contains characters outside Basic Multilingual Plane")

        # Check for RTL marks that might cause display issues
        rtl_chars = ['\u200E', '\u200F', '\u202A', '\u202B', '\u202C', '\u202D', '\u202E']
        if any(char in normalized for char in rtl_chars):
            issues.append("Contains RTL/LTR override characters")

        # Check for zero-width characters that might be problematic
        zero_width = ['\u200B', '\u200C', '\u200D', '\uFEFF']
        if any(char in normalized for char in zero_width):
            issues.append("Contains zero-width characters")

        return issues

    def get_stats(self) -> dict[str, int | float]:
        """Get processing statistics."""
        stats = self._stats.copy()
        if stats["total_processed"] > 0:
            stats["avg_time_ms"] = stats["total_time_ms"] / stats["total_processed"]
            stats["change_rate"] = (stats["total_changed"] / stats["total_processed"]) * 100
        else:
            stats["avg_time_ms"] = 0.0
            stats["change_rate"] = 0.0

        return stats

    def reset_stats(self):
        """Reset processing statistics."""
        self._stats = {
            "total_processed": 0,
            "total_changed": 0,
            "total_time_ms": 0.0,
        }

# Convenience functions for common operations

def normalize_text(
    text: str,
    form: NormalizationForm = NormalizationForm.NFC
) -> str:
    """
    Normalize text using specified form (simple interface).

    Args:
        text: Text to normalize
        form: Normalization form

    Returns:
        Normalized text string
    """
    normalizer = UnicodeNormalizer(form)
    result = normalizer.normalize(text)
    return result.normalized_text

def normalize_batch(
    texts: list[str],
    form: NormalizationForm = NormalizationForm.NFC
) -> list[str]:
    """
    Normalize multiple texts (simple interface).

    Args:
        texts: List of texts to normalize
        form: Normalization form

    Returns:
        List of normalized text strings
    """
    normalizer = UnicodeNormalizer(form)
    results = normalizer.normalize_batch(texts)
    return [result.normalized_text for result in results]

def compare_normalization_forms(text: str) -> dict[str, str]:
    """
    Compare text across all normalization forms.

    Args:
        text: Input text

    Returns:
        Dictionary mapping form names to normalized text
    """
    results = {}
    for form in NormalizationForm:
        results[form.name] = normalize_text(text, form)
    return results

def analyze_text_properties(text: str) -> dict[str, any]:
    """
    Analyze Unicode properties of text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with text analysis results
    """
    return {
        "length": len(text),
        "byte_length_utf8": len(text.encode('utf-8')),
        "byte_length_utf16": len(text.encode('utf-16')),
        "character_categories": _analyze_character_categories(text),
        "normalization_forms": compare_normalization_forms(text),
        "has_combining_chars": any(unicodedata.combining(c) for c in text),
        "has_non_bmp_chars": any(ord(c) > 0x10000 for c in text),
        "bidirectional_class": _analyze_bidirectional(text),
    }

def _analyze_character_categories(text: str) -> dict[str, int]:
    """Analyze Unicode character categories in text."""
    categories = {}
    for char in text:
        category = unicodedata.category(char)
        categories[category] = categories.get(category, 0) + 1
    return categories

def _analyze_bidirectional(text: str) -> dict[str, int]:
    """Analyze bidirectional text properties."""
    bidi_classes = {}
    for char in text:
        bidi_class = unicodedata.bidirectional(char)
        bidi_classes[bidi_class] = bidi_classes.get(bidi_class, 0) + 1
    return bidi_classes
