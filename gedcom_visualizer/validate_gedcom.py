#!/usr/bin/env python3
"""GEDCOM validation utility.

This script validates GEDCOM files and reports common formatting issues,
particularly useful for files exported from MyHeritage and other genealogy
software that may not strictly follow GEDCOM 5.5 format.
"""

import sys
import argparse
from pathlib import Path
from .gedcom_utils import validate_gedcom_format, load_gedcom_robust


def main():
    """Main entry point for the GEDCOM validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate GEDCOM files and report formatting issues"
    )
    parser.add_argument("gedcom_file", help="Path to the GEDCOM file")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=1000,
        help="Maximum number of lines to check (default: 1000)",
    )
    parser.add_argument(
        "--test-parse",
        action="store_true",
        help="Also test if the file can be parsed successfully",
    )

    args = parser.parse_args()

    # Validate file exists
    gedcom_path = Path(args.gedcom_file)
    if not gedcom_path.exists():
        print(f"Error: File '{args.gedcom_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Validate GEDCOM format
    print(f"Validating GEDCOM file: {args.gedcom_file}")
    print(f"Checking up to {args.max_lines} lines...")
    print("=" * 60)

    validation_result = validate_gedcom_format(args.gedcom_file, args.max_lines)

    print(f"Lines checked: {validation_result['lines_checked']}")
    print(f"Issues found: {validation_result['issues_found']}")

    if validation_result["is_valid"]:
        print("✅ No format issues detected!")
    else:
        print("❌ Format issues detected:")
        print()

        for issue in validation_result["issues"]:
            print(f"Line {issue['line']}: {issue['description']}")
            if issue["content"]:
                print(f"  Content: {issue['content']}")
            print()

    # Test parsing if requested
    if args.test_parse:
        print("=" * 60)
        print("Testing GEDCOM parsing...")

        try:
            gedcom_parser = load_gedcom_robust(args.gedcom_file, verbose=True)

            # Get some basic statistics
            individuals = [
                elem
                for elem in gedcom_parser.get_root_child_elements()
                if elem.get_tag() == "INDI"
            ]
            families = [
                elem
                for elem in gedcom_parser.get_root_child_elements()
                if elem.get_tag() == "FAM"
            ]

            print("✅ Parsing successful!")
            print(f"  Individuals found: {len(individuals)}")
            print(f"  Families found: {len(families)}")

        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            sys.exit(1)

    # Exit with appropriate code
    if not validation_result["is_valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
