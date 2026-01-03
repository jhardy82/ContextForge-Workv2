"""
Command-line interface for Unicode text processing utilities.

Provides batch text processing capabilities through command-line interface
with support for normalization, cleaning, and validation operations.
"""

import argparse
import json

# Using builtin types and | union syntax
import logging
import sys
from pathlib import Path

from cf_core.errors.codes import ExitCode

from .cleaner import CleaningMode, CleaningOptions, TextCleaner, clean_text
from .normalizer import (
    NormalizationForm,
    UnicodeNormalizer,
    analyze_text_properties,
    normalize_text,
)
from .validator import TextValidator, check_consistency, validate_text

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def normalize_command(args):
    """Handle normalize command."""
    normalizer = UnicodeNormalizer(NormalizationForm[args.form])

    if args.file:
        # Process file
        result = normalizer.normalize_file(args.file, args.output, encoding=args.encoding)

        if args.json:
            print(json.dumps({
                "file": str(args.file),
                "form": result.form.value,
                "changed": result.changed,
                "character_count": result.character_count,
                "processing_time_ms": result.processing_time_ms,
                "issues": result.issues
            }, indent=2))
        else:
            status = "CHANGED" if result.changed else "NO CHANGE"
            print(f"Normalized {args.file} ({result.form.value}): {status}")
            if result.issues:
                print(f"Issues found: {len(result.issues)}")
                for issue in result.issues[:3]:
                    print(f"  - {issue}")

    elif args.text:
        # Process text directly
        result = normalizer.normalize(args.text)

        if args.json:
            print(json.dumps({
                "original": result.original_text,
                "normalized": result.normalized_text,
                "form": result.form.value,
                "changed": result.changed,
                "issues": result.issues
            }, indent=2))
        else:
            if result.changed:
                print("NORMALIZED:")
                print(result.normalized_text)
            else:
                print("NO CHANGES NEEDED")

    else:
        # Read from stdin
        text = sys.stdin.read()
        result = normalizer.normalize(text)

        if args.json:
            print(json.dumps({
                "normalized": result.normalized_text,
                "form": result.form.value,
                "changed": result.changed,
                "issues": result.issues
            }, indent=2))
        else:
            print(result.normalized_text)

def clean_command(args):
    """Handle clean command."""
    cleaner = TextCleaner()
    mode = CleaningMode[args.mode.upper()]

    # Build custom options if specified
    options = None
    if args.remove_control or args.normalize_whitespace or args.forbidden_chars:
        options = CleaningOptions(
            remove_control_chars=args.remove_control,
            normalize_whitespace=args.normalize_whitespace,
            forbidden_chars=set(args.forbidden_chars) if args.forbidden_chars else None
        )

    if args.file:
        # Process file
        input_path = Path(args.file)
        with input_path.open('r', encoding=args.encoding) as f:
            text = f.read()

        cleaned = cleaner.clean(text, mode, options)

        if args.output:
            output_path = Path(args.output)
            with output_path.open('w', encoding=args.encoding) as f:
                f.write(cleaned)
            print(f"Cleaned text written to {args.output}")
        else:
            print(cleaned)

    elif args.text:
        # Process text directly
        cleaned = cleaner.clean(args.text, mode, options)
        print(cleaned)

    else:
        # Read from stdin
        text = sys.stdin.read()
        cleaned = cleaner.clean(text, mode, options)
        print(cleaned)

def validate_command(args):
    """Handle validate command."""
    validator = TextValidator(strict_mode=args.strict)

    if args.consistency:
        # Check consistency across multiple files/texts
        texts = []

        if args.files:
            for file_path in args.files:
                with Path(file_path).open('r', encoding=args.encoding) as f:
                    texts.append(f.read())
        elif args.texts:
            texts = args.texts
        else:
            # Read multiple texts from stdin (separated by double newlines)
            stdin_content = sys.stdin.read()
            texts = stdin_content.split('\n\n')

        result = validator.check_consistency(texts)

    else:
        # Validate single text
        if args.file:
            with Path(args.file).open('r', encoding=args.encoding) as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            text = sys.stdin.read()

        result = validator.validate(text)

    # Output results
    if args.json:
        output = {
            "is_valid": result.is_valid,
            "score": result.score,
            "statistics": result.statistics,
            "issues": [
                {
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "position": issue.position,
                    "length": issue.length,
                    "suggestion": issue.suggestion
                }
                for issue in result.issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"Validation: {status} (score: {result.score:.2f})")

        if result.issues:
            print(f"\nIssues found ({len(result.issues)}):")
            for issue in result.issues:
                severity_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨"
                }[issue.severity.value]

                print(f"  {severity_icon} {issue.message}")
                if issue.suggestion:
                    print(f"    💡 {issue.suggestion}")

def analyze_command(args):
    """Handle analyze command."""
    if args.file:
        with Path(args.file).open('r', encoding=args.encoding) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    analysis = analyze_text_properties(text)

    if args.json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        print("Text Analysis:")
        print(f"  Length: {analysis['length']} characters")
        print(f"  UTF-8 bytes: {analysis['byte_length_utf8']}")
        print(f"  UTF-16 bytes: {analysis['byte_length_utf16']}")
        print(f"  Has combining chars: {analysis['has_combining_chars']}")
        print(f"  Has non-BMP chars: {analysis['has_non_bmp_chars']}")

        print("\nCharacter Categories:")
        for category, count in sorted(analysis['character_categories'].items()):
            print(f"  {category}: {count}")

        print("\nNormalization Forms:")
        for form, normalized in analysis['normalization_forms'].items():
            changed = "DIFFERENT" if normalized != text else "SAME"
            print(f"  {form}: {changed}")

def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Unicode text processing utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normalize text file to NFC
  python -m cf_core.text_processing normalize --file input.txt --form NFC

  # Clean text from stdin
  echo "messy   text" | python -m cf_core.text_processing clean --mode basic

  # Validate text file
  python -m cf_core.text_processing validate --file document.txt --strict

  # Analyze text properties
  python -m cf_core.text_processing analyze --text "Hello 世界!"

  # Check consistency across files
  python -m cf_core.text_processing validate --consistency --files file1.txt file2.txt
        """
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--encoding', default='utf-8',
                       help='File encoding (default: utf-8)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Normalize command
    normalize_parser = subparsers.add_parser('normalize',
                                           help='Normalize Unicode text')
    normalize_parser.add_argument('--form', choices=['NFC', 'NFD', 'NFKC', 'NFKD'],
                                 default='NFC', help='Normalization form')
    normalize_parser.add_argument('--file', type=Path, help='Input file path')
    normalize_parser.add_argument('--output', type=Path, help='Output file path')
    normalize_parser.add_argument('--text', help='Text to normalize directly')
    normalize_parser.add_argument('--json', action='store_true',
                                 help='Output in JSON format')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean and sanitize text')
    clean_parser.add_argument('--mode', choices=['basic', 'aggressive', 'preserve', 'sanitize'],
                             default='basic', help='Cleaning mode')
    clean_parser.add_argument('--file', type=Path, help='Input file path')
    clean_parser.add_argument('--output', type=Path, help='Output file path')
    clean_parser.add_argument('--text', help='Text to clean directly')
    clean_parser.add_argument('--remove-control', action='store_true',
                             help='Remove control characters')
    clean_parser.add_argument('--normalize-whitespace', action='store_true',
                             help='Normalize whitespace')
    clean_parser.add_argument('--forbidden-chars', nargs='+',
                             help='Characters to remove from text')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate text quality')
    validate_parser.add_argument('--file', type=Path, help='Input file path')
    validate_parser.add_argument('--text', help='Text to validate directly')
    validate_parser.add_argument('--strict', action='store_true',
                                help='Use strict validation rules')
    validate_parser.add_argument('--json', action='store_true',
                                help='Output in JSON format')
    validate_parser.add_argument('--consistency', action='store_true',
                                help='Check consistency across multiple texts')
    validate_parser.add_argument('--files', nargs='+', type=Path,
                                help='Multiple files for consistency check')
    validate_parser.add_argument('--texts', nargs='+',
                                help='Multiple texts for consistency check')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze text properties')
    analyze_parser.add_argument('--file', type=Path, help='Input file path')
    analyze_parser.add_argument('--text', help='Text to analyze directly')
    analyze_parser.add_argument('--json', action='store_true',
                               help='Output in JSON format')

    return parser

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        return ExitCode.USAGE_ERROR

    try:
        if args.command == 'normalize':
            normalize_command(args)
        elif args.command == 'clean':
            clean_command(args)
        elif args.command == 'validate':
            validate_command(args)
        elif args.command == 'analyze':
            analyze_command(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return ExitCode.USAGE_ERROR

    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return ExitCode.GENERAL_ERROR

    return ExitCode.SUCCESS

if __name__ == '__main__':
    sys.exit(main())
