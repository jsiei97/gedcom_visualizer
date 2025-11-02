#!/usr/bin/env python3
"""Script 1: List and search a GEDCOM file to select an ID for the main character.

This script allows users to:
- List all individuals in a GEDCOM file
- Search for individuals by name
- Display basic information to help select the right ID
"""

import sys
import argparse
from pathlib import Path
from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement


def load_gedcom(file_path):
    """Load and parse a GEDCOM file.
    
    Args:
        file_path: Path to the GEDCOM file
        
    Returns:
        Parser object with parsed GEDCOM data
    """
    gedcom_parser = Parser()
    gedcom_parser.parse_file(file_path)
    return gedcom_parser


def format_individual(individual):
    """Format individual information for display.
    
    Args:
        individual: IndividualElement object
        
    Returns:
        Formatted string with individual information
    """
    name = individual.get_name()
    pointer = individual.get_pointer()
    birth_data = individual.get_birth_data()
    death_data = individual.get_death_data()
    
    info = f"ID: {pointer}\n"
    info += f"  Name: {name[0] if name else 'Unknown'} {name[1] if len(name) > 1 else ''}\n"
    
    if birth_data:
        birth_date = birth_data[0] if birth_data[0] else 'Unknown'
        birth_place = birth_data[1] if birth_data[1] else 'Unknown'
        info += f"  Birth: {birth_date} at {birth_place}\n"
    
    if death_data:
        death_date = death_data[0] if death_data[0] else 'Unknown'
        death_place = death_data[1] if death_data[1] else 'Unknown'
        info += f"  Death: {death_date} at {death_place}\n"
    
    return info


def list_all_individuals(gedcom_parser):
    """List all individuals in the GEDCOM file.
    
    Args:
        gedcom_parser: Parsed GEDCOM data
    """
    individuals = gedcom_parser.get_root_child_elements()
    individual_elements = [elem for elem in individuals if isinstance(elem, IndividualElement)]
    
    print(f"Found {len(individual_elements)} individuals in the GEDCOM file:\n")
    print("=" * 70)
    
    for individual in individual_elements:
        print(format_individual(individual))
        print("-" * 70)


def search_individuals(gedcom_parser, search_term):
    """Search for individuals by name.
    
    Args:
        gedcom_parser: Parsed GEDCOM data
        search_term: String to search for in names (case-insensitive)
    """
    individuals = gedcom_parser.get_root_child_elements()
    individual_elements = [elem for elem in individuals if isinstance(elem, IndividualElement)]
    
    search_term_lower = search_term.lower()
    matches = []
    
    for individual in individual_elements:
        name = individual.get_name()
        if name:
            full_name = f"{name[0]} {name[1] if len(name) > 1 else ''}".lower()
            if search_term_lower in full_name:
                matches.append(individual)
    
    if matches:
        print(f"Found {len(matches)} match(es) for '{search_term}':\n")
        print("=" * 70)
        
        for individual in matches:
            print(format_individual(individual))
            print("-" * 70)
    else:
        print(f"No matches found for '{search_term}'")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='List and search individuals in a GEDCOM file'
    )
    parser.add_argument(
        'gedcom_file',
        help='Path to the GEDCOM file'
    )
    parser.add_argument(
        '-s', '--search',
        help='Search for individuals by name',
        metavar='TERM'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    gedcom_path = Path(args.gedcom_file)
    if not gedcom_path.exists():
        print(f"Error: File '{args.gedcom_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Load GEDCOM file
    try:
        gedcom_parser = load_gedcom(args.gedcom_file)
    except Exception as e:
        print(f"Error parsing GEDCOM file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # List or search
    if args.search:
        search_individuals(gedcom_parser, args.search)
    else:
        list_all_individuals(gedcom_parser)


if __name__ == '__main__':
    main()
