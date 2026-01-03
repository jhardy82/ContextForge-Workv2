"""
Unicode normalization and text processing utilities for ContextForge Work.

This module provides comprehensive Unicode text processing capabilities including:
- Unicode normalization (NFC, NFD, NFKC, NFKD)
- Text cleaning and sanitization
- Text validation and consistency checking
- Performance-optimized batch processing
"""

from .cleaner import (
                      CleaningMode,
                      CleaningOptions,
                      TextCleaner,
                      clean_text,
                      normalize_whitespace,
                      remove_control_chars,
)
from .normalizer import (
                      NormalizationForm,
                      NormalizationResult,
                      UnicodeNormalizer,
                      normalize_batch,
                      normalize_text,
)
from .validator import (
                      TextValidator,
                      ValidationCategory,
                      ValidationIssue,
                      ValidationResult,
                      ValidationSeverity,
                      check_consistency,
                      validate_text,
)

__version__ = "1.0.0"
__all__ = [
    # Normalization
    "UnicodeNormalizer",
    "normalize_text",
    "normalize_batch",
    "NormalizationForm",
    "NormalizationResult",
    # Cleaning
    "TextCleaner",
    "clean_text",
    "remove_control_chars",
    "normalize_whitespace",
    "CleaningOptions",
    "CleaningMode",
    # Validation
    "TextValidator",
    "validate_text",
    "check_consistency",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationCategory",
]
