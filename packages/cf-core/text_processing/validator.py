"""
Text validation and consistency checking utilities.

Provides comprehensive text validation functions for checking text quality,
consistency, and identifying potential issues.
"""

import logging
import re
import unicodedata
from dataclasses import dataclass

# Import statements removed - using builtin types
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    """Categories of validation issues."""
    ENCODING = "encoding"
    UNICODE = "unicode"
    WHITESPACE = "whitespace"
    CONSISTENCY = "consistency"
    CONTENT = "content"
    FORMAT = "format"

@dataclass
class ValidationIssue:
    """A single validation issue found in text."""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    position: int | None = None
    length: int | None = None
    suggestion: str | None = None

@dataclass
class ValidationResult:
    """Result of text validation."""
    text: str
    is_valid: bool
    issues: list[ValidationIssue]
    score: float  # 0.0 (worst) to 1.0 (perfect)
    statistics: dict[str, int | float]

class TextValidator:
    """
    Comprehensive text validation and consistency checking.

    Features:
    - Unicode and encoding validation
    - Consistency checking across texts
    - Content quality assessment
    - Customizable validation rules
    - Batch processing with progress tracking
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.

        Args:
            strict_mode: Whether to use strict validation rules
        """
        self.strict_mode = strict_mode
        self._validation_rules: list = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Set up default validation rules."""
        # Unicode validation rules
        self._validation_rules.extend([
            self._check_unicode_normalization,
            self._check_combining_characters,
            self._check_control_characters,
            self._check_zero_width_characters,
            self._check_bidi_characters,
        ])

        # Content validation rules
        self._validation_rules.extend([
            self._check_whitespace_consistency,
            self._check_line_ending_consistency,
            self._check_encoding_issues,
        ])

        if self.strict_mode:
            self._validation_rules.extend([
                self._check_non_ascii_characters,
                self._check_mixed_scripts,
                self._check_suspicious_patterns,
            ])

    def validate(self, text: str) -> ValidationResult:
        """
        Validate text and return detailed results.

        Args:
            text: Text to validate

        Returns:
            ValidationResult with issues and statistics
        """
        if not isinstance(text, str):
            text = str(text)

        issues = []
        statistics = self._calculate_statistics(text)

        # Run all validation rules
        for rule in self._validation_rules:
            try:
                rule_issues = rule(text)
                issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Validation rule failed: {e}")
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation rule failed: {e}"
                ))

        # Calculate validation score
        score = self._calculate_score(text, issues)
        is_valid = (score >= 0.8 and
                   not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues))

        return ValidationResult(
            text=text,
            is_valid=is_valid,
            issues=issues,
            score=score,
            statistics=statistics
        )

    def validate_batch(self, texts: list[str]) -> list[ValidationResult]:
        """
        Validate multiple texts.

        Args:
            texts: List of texts to validate

        Returns:
            List of ValidationResult objects
        """
        return [self.validate(text) for text in texts]

    def check_consistency(self, texts: list[str]) -> ValidationResult:
        """
        Check consistency across multiple texts.

        Args:
            texts: List of texts to check for consistency

        Returns:
            ValidationResult for consistency issues
        """
        if not texts:
            return ValidationResult(
                text="",
                is_valid=True,
                issues=[],
                score=1.0,
                statistics={}
            )

        issues = []

        # Check encoding consistency
        encodings = set()
        for text in texts:
            try:
                # Try to detect encoding characteristics
                if any(ord(c) > 127 for c in text):
                    encodings.add("non-ascii")
                else:
                    encodings.add("ascii")
            except Exception:
                encodings.add("unknown")

        if len(encodings) > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.ENCODING,
                severity=ValidationSeverity.WARNING,
                message=f"Inconsistent encoding patterns detected: {encodings}"
            ))

        # Check normalization consistency
        norm_forms = set()
        for text in texts:
            # Check if text changes with normalization
            nfc = unicodedata.normalize('NFC', text)
            if text == nfc:
                norm_forms.add('NFC')
            else:
                norm_forms.add('mixed')

        if len(norm_forms) > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.UNICODE,
                severity=ValidationSeverity.WARNING,
                message="Inconsistent Unicode normalization across texts"
            ))

        # Check line ending consistency
        line_endings = set()
        for text in texts:
            if '\r\n' in text:
                line_endings.add('CRLF')
            elif '\r' in text:
                line_endings.add('CR')
            elif '\n' in text:
                line_endings.add('LF')

        if len(line_endings) > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.WHITESPACE,
                severity=ValidationSeverity.INFO,
                message=f"Mixed line endings: {line_endings}"
            ))

        # Calculate overall consistency score
        combined_text = '\n'.join(texts)
        score = 1.0 - (len(issues) * 0.1)  # Reduce score for each issue

        return ValidationResult(
            text=combined_text,
            is_valid=len(issues) == 0,
            issues=issues,
            score=max(0.0, score),
            statistics={"texts_checked": len(texts), "total_length": len(combined_text)}
        )

    def _calculate_statistics(self, text: str) -> dict[str, int | float]:
        """Calculate text statistics."""
        stats = {
            "length": len(text),
            "byte_length": len(text.encode('utf-8')),
            "line_count": text.count('\n') + (1 if text and not text.endswith('\n') else 0),
            "word_count": len(text.split()),
            "char_categories": {},
            "non_ascii_chars": sum(1 for c in text if ord(c) > 127),
            "control_chars": sum(1 for c in text if unicodedata.category(c).startswith('C')),
            "combining_chars": sum(1 for c in text if unicodedata.combining(c)),
        }

        # Character category distribution
        categories = {}
        for char in text:
            cat = unicodedata.category(char)
            categories[cat] = categories.get(cat, 0) + 1
        stats["char_categories"] = categories

        return stats

    def _calculate_score(self, text: str, issues: list[ValidationIssue]) -> float:
        """Calculate validation score based on text quality and issues."""
        base_score = 1.0

        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.5
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.2
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 0.02

        return max(0.0, base_score)

    # Validation rule methods

    def _check_unicode_normalization(self, text: str) -> list[ValidationIssue]:
        """Check if text is properly Unicode normalized."""
        issues = []

        nfc = unicodedata.normalize('NFC', text)
        if text != nfc:
            issues.append(ValidationIssue(
                category=ValidationCategory.UNICODE,
                severity=ValidationSeverity.WARNING,
                message="Text is not in NFC normalized form",
                suggestion="Apply Unicode NFC normalization"
            ))

        return issues

    def _check_combining_characters(self, text: str) -> list[ValidationIssue]:
        """Check for potentially problematic combining characters."""
        issues = []

        combining_count = sum(1 for c in text if unicodedata.combining(c))
        if combining_count > len(text) * 0.1:  # More than 10% combining chars
            issues.append(ValidationIssue(
                category=ValidationCategory.UNICODE,
                severity=ValidationSeverity.WARNING,
                message=f"High number of combining characters: {combining_count}",
                suggestion="Review text for potential display issues"
            ))

        return issues

    def _check_control_characters(self, text: str) -> list[ValidationIssue]:
        """Check for control characters."""
        issues = []

        control_chars = []
        for i, char in enumerate(text):
            if unicodedata.category(char).startswith('C') and char not in '\n\r\t':
                control_chars.append((i, char, ord(char)))

        if control_chars:
            for pos, _, code in control_chars[:5]:  # Report first 5
                issues.append(ValidationIssue(
                    category=ValidationCategory.UNICODE,
                    severity=ValidationSeverity.ERROR,
                    message=f"Control character found: U+{code:04X} at position {pos}",
                    position=pos,
                    length=1,
                    suggestion="Remove control characters"
                ))

        return issues

    def _check_zero_width_characters(self, text: str) -> list[ValidationIssue]:
        """Check for zero-width characters."""
        issues = []

        zero_width_chars = {'\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060'}
        found_chars = []

        for i, char in enumerate(text):
            if char in zero_width_chars:
                found_chars.append((i, char))

        if found_chars:
            char_names = {c: unicodedata.name(c, f'U+{ord(c):04X}') for _, c in found_chars}
            issues.append(ValidationIssue(
                category=ValidationCategory.UNICODE,
                severity=ValidationSeverity.WARNING,
                message=f"Zero-width characters found: {set(char_names.values())}",
                suggestion="Consider removing zero-width characters"
            ))

        return issues

    def _check_bidi_characters(self, text: str) -> list[ValidationIssue]:
        """Check for bidirectional text issues."""
        issues = []

        bidi_override_chars = {'\u202A', '\u202B', '\u202C', '\u202D', '\u202E'}
        rtl_chars = []

        for i, char in enumerate(text):
            if char in bidi_override_chars:
                rtl_chars.append((i, char))

        if rtl_chars:
            issues.append(ValidationIssue(
                category=ValidationCategory.UNICODE,
                severity=ValidationSeverity.WARNING,
                message="Bidirectional override characters found",
                suggestion="Review for potential text display issues"
            ))

        return issues

    def _check_whitespace_consistency(self, text: str) -> list[ValidationIssue]:
        """Check for whitespace consistency issues."""
        issues = []

        # Check for mixed tabs and spaces
        has_tabs = '\t' in text
        has_spaces = '  ' in text  # Multiple spaces (likely indentation)

        if has_tabs and has_spaces:
            issues.append(ValidationIssue(
                category=ValidationCategory.WHITESPACE,
                severity=ValidationSeverity.INFO,
                message="Mixed tabs and spaces detected",
                suggestion="Use consistent indentation"
            ))

        # Check for trailing whitespace
        lines_with_trailing = []
        for i, line in enumerate(text.split('\n')):
            if line.endswith(' ') or line.endswith('\t'):
                lines_with_trailing.append(i + 1)

        if lines_with_trailing:
            issues.append(ValidationIssue(
                category=ValidationCategory.WHITESPACE,
                severity=ValidationSeverity.INFO,
                message=f"Trailing whitespace on lines: {lines_with_trailing[:5]}",
                suggestion="Remove trailing whitespace"
            ))

        return issues

    def _check_line_ending_consistency(self, text: str) -> list[ValidationIssue]:
        """Check for consistent line endings."""
        issues = []

        has_crlf = '\r\n' in text
        has_lf = text.replace('\r\n', '').count('\n') > 0
        has_cr = text.replace('\r\n', '').count('\r') > 0

        ending_types = sum([has_crlf, has_lf, has_cr])

        if ending_types > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.WHITESPACE,
                severity=ValidationSeverity.WARNING,
                message="Mixed line endings detected",
                suggestion="Normalize to consistent line endings"
            ))

        return issues

    def _check_encoding_issues(self, text: str) -> list[ValidationIssue]:
        """Check for potential encoding issues."""
        issues = []

        # Check for common mojibake patterns
        mojibake_patterns = [
            'Ã¡', 'Ã©', 'Ã­', 'Ã³', 'Ãº', 'Ã±', 'Ã¼',  # Latin chars as UTF-8 in Latin-1
            'â€™', 'â€œ', 'â€�', 'â€"', 'â€"',  # Smart quotes as UTF-8 in Latin-1
        ]

        for pattern in mojibake_patterns:
            if pattern in text:
                issues.append(ValidationIssue(
                    category=ValidationCategory.ENCODING,
                    severity=ValidationSeverity.ERROR,
                    message=f"Potential mojibake detected: '{pattern}'",
                    suggestion="Check text encoding and re-decode properly"
                ))
                break  # Don't spam with multiple mojibake issues

        return issues

    def _check_non_ascii_characters(self, text: str) -> list[ValidationIssue]:
        """Check for non-ASCII characters (strict mode)."""
        issues = []

        non_ascii_count = sum(1 for c in text if ord(c) > 127)
        if non_ascii_count > 0:
            percentage = (non_ascii_count / len(text)) * 100 if text else 0
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.INFO,
                message=f"{non_ascii_count} non-ASCII characters ({percentage:.1f}%)",
                suggestion="Consider ASCII-only content if required"
            ))

        return issues

    def _check_mixed_scripts(self, text: str) -> list[ValidationIssue]:
        """Check for mixed writing scripts (strict mode)."""
        issues = []

        scripts = set()
        for char in text:
            if unicodedata.category(char).startswith('L'):  # Letter categories
                name = unicodedata.name(char, '')
                script = name.split()[0] if name else 'Unknown'
                scripts.add(script)

        if len(scripts) > 2:  # Allow Latin + one other script
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.INFO,
                message=f"Multiple scripts detected: {len(scripts)} scripts",
                suggestion="Consider script consistency for readability"
            ))

        return issues

    def _check_suspicious_patterns(self, text: str) -> list[ValidationIssue]:
        """Check for suspicious patterns (strict mode)."""
        issues = []

        # Check for repeated characters (possible data corruption)
        repeated_pattern = re.compile(r'(.)\1{10,}')  # 10+ repeated chars
        matches = repeated_pattern.findall(text)

        if matches:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.WARNING,
                message=f"Suspicious repeated characters: {set(matches)}",
                suggestion="Check for data corruption or formatting issues"
            ))

        return issues

# Convenience functions

def validate_text(text: str, strict_mode: bool = False) -> ValidationResult:
    """
    Validate text (simple interface).

    Args:
        text: Text to validate
        strict_mode: Whether to use strict validation

    Returns:
        ValidationResult
    """
    validator = TextValidator(strict_mode)
    return validator.validate(text)

def check_consistency(texts: list[str]) -> ValidationResult:
    """
    Check consistency across texts (simple interface).

    Args:
        texts: List of texts to check

    Returns:
        ValidationResult for consistency
    """
    validator = TextValidator()
    return validator.check_consistency(texts)
