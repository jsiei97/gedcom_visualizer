#!/usr/bin/env python3
"""Script 2: Generate AsciiDoc document for a given individual ID.

This script creates a human-readable AsciiDoc document with information about
an individual from a GEDCOM file, including their personal data, family relationships,
and genealogical context.
"""

import sys
import argparse
from pathlib import Path
from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement


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


def get_individual_by_id(gedcom_parser, individual_id):
    """Get an individual by their ID.
    
    Args:
        gedcom_parser: Parsed GEDCOM data
        individual_id: ID of the individual (e.g., '@I1@')
        
    Returns:
        IndividualElement object or None if not found
    """
    # Ensure ID has @ symbols
    if not individual_id.startswith('@'):
        individual_id = f'@{individual_id}@'
    
    element_dict = gedcom_parser.get_element_dictionary()
    element = element_dict.get(individual_id)
    if isinstance(element, IndividualElement):
        return element
    return None


def get_family_info(gedcom_parser, individual):
    """Get family information for an individual.
    
    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: IndividualElement object
        
    Returns:
        Dictionary with parents, spouses, and children
    """
    result = {
        'parents': [],
        'spouses': [],
        'children': []
    }
    
    # Get parents
    parents = gedcom_parser.get_parents(individual)
    for parent in parents:
        if parent.get_gender() == 'M':
            result['parents'].append(('Father', parent))
        elif parent.get_gender() == 'F':
            result['parents'].append(('Mother', parent))
        else:
            result['parents'].append(('Parent', parent))
    
    # Get families (as spouse)
    families = gedcom_parser.get_families(individual)
    individual_pointer = individual.get_pointer()
    
    for family in families:
        # Get family members (includes individual, spouse, and children)
        members = gedcom_parser.get_family_members(family)
        
        for member in members:
            member_pointer = member.get_pointer()
            
            # Skip the individual themselves
            if member_pointer == individual_pointer:
                continue
            
            # Check if this is a spouse (adult) or child
            # A simple heuristic: if they have the same family as spouse families, they're a spouse
            member_families = gedcom_parser.get_families(member)
            is_spouse = family in member_families
            
            if is_spouse:
                if member not in result['spouses']:
                    result['spouses'].append(member)
            else:
                if member not in result['children']:
                    result['children'].append(member)
    
    return result


def format_name(individual):
    """Format individual's name.
    
    Args:
        individual: IndividualElement object
        
    Returns:
        Formatted name string
    """
    name = individual.get_name()
    if name:
        return f"{name[0]} {name[1] if len(name) > 1 else ''}".strip()
    return "Unknown"


def generate_asciidoc(gedcom_parser, individual, output_file=None):
    """Generate AsciiDoc document for an individual.
    
    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: IndividualElement object
        output_file: Optional output file path (defaults to stdout)
    """
    name = format_name(individual)
    pointer = individual.get_pointer()
    
    # Start building the AsciiDoc content
    lines = []
    lines.append(f"= {name}")
    lines.append(":toc:")
    lines.append(":toc-title: Table of Contents")
    lines.append(":numbered:")
    lines.append("")
    lines.append("== Personal Information")
    lines.append("")
    lines.append(f"*ID:* {pointer}")
    lines.append("")
    lines.append(f"*Full Name:* {name}")
    lines.append("")
    
    # Gender
    gender = individual.get_gender()
    if gender:
        lines.append(f"*Gender:* {gender}")
        lines.append("")
    
    # Birth information
    birth_data = individual.get_birth_data()
    if birth_data:
        lines.append("=== Birth")
        lines.append("")
        if birth_data[0]:
            lines.append(f"*Date:* {birth_data[0]}")
        if birth_data[1]:
            lines.append(f"*Place:* {birth_data[1]}")
        lines.append("")
    
    # Death information
    death_data = individual.get_death_data()
    if death_data and (death_data[0] or death_data[1]):
        lines.append("=== Death")
        lines.append("")
        if death_data[0]:
            lines.append(f"*Date:* {death_data[0]}")
        if death_data[1]:
            lines.append(f"*Place:* {death_data[1]}")
        lines.append("")
    
    # Family information
    family_info = get_family_info(gedcom_parser, individual)
    
    if family_info['parents']:
        lines.append("== Parents")
        lines.append("")
        for relation, parent in family_info['parents']:
            parent_name = format_name(parent)
            parent_id = parent.get_pointer()
            lines.append(f"* *{relation}:* {parent_name} ({parent_id})")
            
            parent_birth = parent.get_birth_data()
            if parent_birth and parent_birth[0]:
                lines.append(f"** Born: {parent_birth[0]}")
            
            parent_death = parent.get_death_data()
            if parent_death and parent_death[0]:
                lines.append(f"** Died: {parent_death[0]}")
        lines.append("")
    
    if family_info['spouses']:
        lines.append("== Spouse(s)")
        lines.append("")
        for spouse in family_info['spouses']:
            spouse_name = format_name(spouse)
            spouse_id = spouse.get_pointer()
            lines.append(f"* *{spouse_name}* ({spouse_id})")
            
            spouse_birth = spouse.get_birth_data()
            if spouse_birth and spouse_birth[0]:
                lines.append(f"** Born: {spouse_birth[0]}")
            
            spouse_death = spouse.get_death_data()
            if spouse_death and spouse_death[0]:
                lines.append(f"** Died: {spouse_death[0]}")
        lines.append("")
    
    if family_info['children']:
        lines.append("== Children")
        lines.append("")
        for child in family_info['children']:
            child_name = format_name(child)
            child_id = child.get_pointer()
            lines.append(f"* *{child_name}* ({child_id})")
            
            child_birth = child.get_birth_data()
            if child_birth and child_birth[0]:
                lines.append(f"** Born: {child_birth[0]}")
        lines.append("")
    
    # Add a footer
    lines.append("== Document Information")
    lines.append("")
    lines.append("This document was automatically generated from a GEDCOM file using the GEDCOM Visualizer tool.")
    lines.append("")
    
    # Write to file or stdout
    content = '\n'.join(lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"AsciiDoc document written to: {output_file}")
    else:
        print(content)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate AsciiDoc document for an individual from a GEDCOM file'
    )
    parser.add_argument(
        'gedcom_file',
        help='Path to the GEDCOM file'
    )
    parser.add_argument(
        'individual_id',
        help='ID of the individual (e.g., @I1@ or I1)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)',
        metavar='FILE'
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
    
    # Get individual
    individual = get_individual_by_id(gedcom_parser, args.individual_id)
    if not individual:
        print(f"Error: Individual with ID '{args.individual_id}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Generate AsciiDoc
    try:
        generate_asciidoc(gedcom_parser, individual, args.output)
    except Exception as e:
        print(f"Error generating AsciiDoc: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
