"""
Text cleaning and sanitization utilities.

Provides comprehensive text cleaning functions for removing unwanted characters,
normalizing whitespace, and sanitizing text for various use cases.
"""

import re
import string
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from re import Pattern


class CleaningMode(Enum):
    """Text cleaning modes."""
    BASIC = "basic"           # Remove control chars, normalize whitespace
    AGGRESSIVE = "aggressive" # Remove all non-printable, normalize heavily
    PRESERVE = "preserve"     # Minimal cleaning, preserve formatting
    SANITIZE = "sanitize"     # Remove potentially dangerous characters

@dataclass
class CleaningOptions:
    """Configuration options for text cleaning."""
    # Whitespace handling
    normalize_whitespace: bool = True
    remove_leading_whitespace: bool = True
    remove_trailing_whitespace: bool = True
    collapse_multiple_spaces: bool = True
    normalize_line_endings: bool = True

    # Character removal
    remove_control_chars: bool = True
    remove_non_printable: bool = False
    remove_zero_width: bool = True
    remove_rtl_marks: bool = False

    # Custom filtering
    allowed_chars: set[str] | None = None
    forbidden_chars: set[str] | None = None
    preserve_newlines: bool = True
    preserve_tabs: bool = False

    # Encoding handling
    fix_mojibake: bool = False
    normalize_unicode: bool = True
    target_encoding: str = "utf-8"

class TextCleaner:
    """
    Comprehensive text cleaning and sanitization utilities.

    Features:
    - Multiple cleaning modes (basic, aggressive, preserve, sanitize)
    - Configurable character filtering
    - Unicode normalization integration
    - Whitespace handling
    - Performance optimization for batch processing
    """

    # Common character sets for filtering
    CONTROL_CHARS = set(chr(i) for i in range(0, 32)) - {'\n', '\r', '\t'}
    ZERO_WIDTH_CHARS = {'\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060'}
    RTL_MARKS = {'\u200E', '\u200F', '\u202A', '\u202B', '\u202C', '\u202D', '\u202E'}
    PRINTABLE_ASCII = set(string.printable)

    def __init__(self, default_options: CleaningOptions | None = None):
        """
        Initialize text cleaner with default options.

        Args:
            default_options: Default cleaning options
        """
        self.default_options = default_options or CleaningOptions()
        self._compiled_patterns: dict[str, Pattern] = {}
        self._precompile_patterns()

    def _precompile_patterns(self):
        """Precompile regex patterns for better performance."""
        self._compiled_patterns = {
            'multiple_spaces': re.compile(r' {2,}'),
            'leading_trailing_spaces': re.compile(r'^[ \t]+|[ \t]+$', re.MULTILINE),
            'normalize_newlines': re.compile(r'\r\n|\r'),
            'control_chars': re.compile(r'[\x00-\x1f\x7f-\x9f]'),
            'non_printable': re.compile(r'[^\x20-\x7e\s]'),
            'zero_width': re.compile(f'[{"".join(self.ZERO_WIDTH_CHARS)}]'),
            'rtl_marks': re.compile(f'[{"".join(self.RTL_MARKS)}]'),
        }

    def clean(
        self,
        text: str,
        mode: CleaningMode = CleaningMode.BASIC,
        options: CleaningOptions | None = None
    ) -> str:
        """
        Clean text according to specified mode and options.

        Args:
            text: Input text to clean
            mode: Cleaning mode
            options: Custom cleaning options (overrides defaults)

        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            text = str(text)

        # Use provided options or defaults
        opts = options or self._get_mode_options(mode)

        # Apply cleaning steps in order
        result = text

        # Unicode normalization (if enabled)
        if opts.normalize_unicode:
            result = unicodedata.normalize('NFC', result)

        # Fix mojibake (if enabled)
        if opts.fix_mojibake:
            result = self._fix_mojibake(result)

        # Character filtering
        if opts.remove_control_chars:
            result = self._remove_control_chars(result, opts)

        if opts.remove_non_printable:
            result = self._remove_non_printable(result, opts)

        if opts.remove_zero_width:
            result = self._remove_zero_width_chars(result)

        if opts.remove_rtl_marks:
            result = self._remove_rtl_marks(result)

        # Custom character filtering
        if opts.forbidden_chars:
            result = self._remove_forbidden_chars(result, opts.forbidden_chars)

        if opts.allowed_chars:
            result = self._keep_only_allowed_chars(result, opts.allowed_chars)

        # Whitespace handling
        if opts.normalize_line_endings:
            result = self._normalize_line_endings(result)

        if opts.collapse_multiple_spaces:
            result = self._collapse_multiple_spaces(result)

        if opts.remove_leading_whitespace or opts.remove_trailing_whitespace:
            result = self._trim_whitespace(result, opts)

        return result

    def clean_batch(
        self,
        texts: list[str],
        mode: CleaningMode = CleaningMode.BASIC,
        options: CleaningOptions | None = None
    ) -> list[str]:
        """
        Clean multiple texts efficiently.

        Args:
            texts: List of texts to clean
            mode: Cleaning mode
            options: Custom cleaning options

        Returns:
            List of cleaned texts
        """
        return [self.clean(text, mode, options) for text in texts]

    def _get_mode_options(self, mode: CleaningMode) -> CleaningOptions:
        """Get predefined options for cleaning mode."""
        if mode == CleaningMode.BASIC:
            return CleaningOptions(
                normalize_whitespace=True,
                remove_control_chars=True,
                remove_zero_width=True,
                preserve_newlines=True,
                preserve_tabs=False
            )
        elif mode == CleaningMode.AGGRESSIVE:
            return CleaningOptions(
                normalize_whitespace=True,
                remove_control_chars=True,
                remove_non_printable=True,
                remove_zero_width=True,
                remove_rtl_marks=True,
                preserve_newlines=True,
                preserve_tabs=False
            )
        elif mode == CleaningMode.PRESERVE:
            return CleaningOptions(
                normalize_whitespace=False,
                remove_control_chars=False,
                remove_zero_width=False,
                preserve_newlines=True,
                preserve_tabs=True
            )
        elif mode == CleaningMode.SANITIZE:
            return CleaningOptions(
                normalize_whitespace=True,
                remove_control_chars=True,
                remove_non_printable=False,
                remove_zero_width=True,
                remove_rtl_marks=True,
                preserve_newlines=True,
                preserve_tabs=False,
                forbidden_chars={'<', '>', '&', '"', "'", '\x00'}
            )
        else:
            return self.default_options

    def _remove_control_chars(self, text: str, options: CleaningOptions) -> str:
        """Remove control characters, preserving specified ones."""
        preserved = set()
        if options.preserve_newlines:
            preserved.update({'\n', '\r'})
        if options.preserve_tabs:
            preserved.add('\t')

        result = []
        for char in text:
            if char in self.CONTROL_CHARS and char not in preserved:
                continue
            result.append(char)
        return ''.join(result)

    def _remove_non_printable(self, text: str, options: CleaningOptions) -> str:
        """Remove non-printable characters."""
        preserved = set()
        if options.preserve_newlines:
            preserved.update({'\n', '\r'})
        if options.preserve_tabs:
            preserved.add('\t')

        result = []
        for char in text:
            if (char in self.PRINTABLE_ASCII or
                char in preserved or
                unicodedata.category(char).startswith('L')):  # Letters are usually safe
                result.append(char)
        return ''.join(result)

    def _remove_zero_width_chars(self, text: str) -> str:
        """Remove zero-width characters."""
        return self._compiled_patterns['zero_width'].sub('', text)

    def _remove_rtl_marks(self, text: str) -> str:
        """Remove RTL/LTR override marks."""
        return self._compiled_patterns['rtl_marks'].sub('', text)

    def _remove_forbidden_chars(self, text: str, forbidden: set[str]) -> str:
        """Remove forbidden characters."""
        return ''.join(char for char in text if char not in forbidden)

    def _keep_only_allowed_chars(self, text: str, allowed: set[str]) -> str:
        """Keep only allowed characters."""
        return ''.join(char for char in text if char in allowed)

    def _normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to Unix style."""
        return self._compiled_patterns['normalize_newlines'].sub('\n', text)

    def _collapse_multiple_spaces(self, text: str) -> str:
        """Collapse multiple consecutive spaces to single space."""
        return self._compiled_patterns['multiple_spaces'].sub(' ', text)

    def _trim_whitespace(self, text: str, options: CleaningOptions) -> str:
        """Trim leading and/or trailing whitespace."""
        if options.remove_leading_whitespace and options.remove_trailing_whitespace:
            return text.strip()
        elif options.remove_leading_whitespace:
            return text.lstrip()
        elif options.remove_trailing_whitespace:
            return text.rstrip()
        return text

    def _fix_mojibake(self, text: str) -> str:
        """
        Attempt to fix mojibake (encoding corruption).

        This is a basic implementation - complex mojibake might need
        specialized libraries like ftfy.
        """
        # Common mojibake patterns and fixes
        mojibake_fixes = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã±': 'ñ', 'Ã¼': 'ü', 'Â°': '°', 'â€™': "'", 'â€œ': '"',
            'â€�': '"', 'â€"': '–', 'â€•': '—', 'â€¦': '…'
        }

        result = text
        for wrong, correct in mojibake_fixes.items():
            result = result.replace(wrong, correct)

        return result

# Convenience functions

def clean_text(
    text: str,
    mode: CleaningMode = CleaningMode.BASIC
) -> str:
    """
    Clean text using specified mode (simple interface).

    Args:
        text: Text to clean
        mode: Cleaning mode

    Returns:
        Cleaned text
    """
    cleaner = TextCleaner()
    return cleaner.clean(text, mode)

def remove_control_chars(text: str, preserve_newlines: bool = True) -> str:
    """
    Remove control characters from text.

    Args:
        text: Input text
        preserve_newlines: Whether to preserve newline characters

    Returns:
        Text with control characters removed
    """
    options = CleaningOptions(
        remove_control_chars=True,
        preserve_newlines=preserve_newlines,
        normalize_whitespace=False
    )
    cleaner = TextCleaner()
    return cleaner.clean(text, CleaningMode.BASIC, options)

def normalize_whitespace(
    text: str,
    collapse_spaces: bool = True,
    normalize_newlines: bool = True
) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Input text
        collapse_spaces: Whether to collapse multiple spaces
        normalize_newlines: Whether to normalize line endings

    Returns:
        Text with normalized whitespace
    """
    options = CleaningOptions(
        normalize_whitespace=True,
        collapse_multiple_spaces=collapse_spaces,
        normalize_line_endings=normalize_newlines,
        remove_control_chars=False
    )
    cleaner = TextCleaner()
    return cleaner.clean(text, CleaningMode.PRESERVE, options)

def sanitize_for_filename(text: str, replacement: str = '_') -> str:
    """
    Sanitize text for use as filename.

    Args:
        text: Input text
        replacement: Character to replace invalid chars with

    Returns:
        Filename-safe text
    """
    # Characters not allowed in filenames
    invalid_chars = {'<', '>', ':', '"', '/', '\\', '|', '?', '*'}

    result = []
    for char in text:
        if char in invalid_chars or ord(char) < 32:
            result.append(replacement)
        else:
            result.append(char)

    # Remove multiple consecutive replacements
    filename = ''.join(result)
    while replacement + replacement in filename:
        filename = filename.replace(replacement + replacement, replacement)

    return filename.strip(replacement)

def extract_printable_text(text: str) -> str:
    """
    Extract only printable text, removing everything else.

    Args:
        text: Input text

    Returns:
        Only printable characters
    """
    return clean_text(text, CleaningMode.AGGRESSIVE)
