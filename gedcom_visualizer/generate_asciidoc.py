#!/usr/bin/env python3
"""Script 2: Generate AsciiDoc document for a given individual ID.

This script creates a human-readable AsciiDoc document with information about
an individual from a GEDCOM file, including their personal data, family
relationships, and genealogical context.
"""

import sys
import argparse
import re
import subprocess
from pathlib import Path
from gedcom.element.individual import IndividualElement
from .gedcom_utils import load_gedcom_robust


def load_gedcom(file_path):
    """Load and parse a GEDCOM file with robust error handling.

    Args:
        file_path: Path to the GEDCOM file

    Returns:
        Parser object with parsed GEDCOM data
    """
    return load_gedcom_robust(file_path, verbose=True)


def get_individual_by_id(gedcom_parser, individual_id):
    """Get an individual by their ID.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual_id: ID of the individual (e.g., '@I1@')

    Returns:
        IndividualElement object or None if not found
    """
    # Ensure ID has @ symbols
    if not individual_id.startswith("@"):
        individual_id = f"@{individual_id}@"

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
    result = {"parents": [], "spouses": [], "children": []}

    # Get parents
    parents = gedcom_parser.get_parents(individual)
    for parent in parents:
        if parent.get_gender() == "M":
            result["parents"].append(("Father", parent))
        elif parent.get_gender() == "F":
            result["parents"].append(("Mother", parent))
        else:
            result["parents"].append(("Parent", parent))

    # Get families (as spouse)
    families = gedcom_parser.get_families(individual)
    individual_pointer = individual.get_pointer()
    element_dict = gedcom_parser.get_element_dictionary()

    for family in families:
        # Get family structure elements (HUSB, WIFE, CHIL tags)
        family_elements = family.get_child_elements()

        for element in family_elements:
            tag = element.get_tag()
            pointer = element.get_value()

            # Skip the individual themselves
            if pointer == individual_pointer:
                continue

            # Add spouses (HUSB or WIFE tags)
            if tag in ("HUSB", "WIFE"):
                spouse = element_dict.get(pointer)
                if spouse and spouse not in result["spouses"]:
                    result["spouses"].append(spouse)

            # Add children (CHIL tag)
            elif tag == "CHIL":
                child = element_dict.get(pointer)
                if child and child not in result["children"]:
                    result["children"].append(child)

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


def create_family_tree_dot_content(gedcom_parser, individual):
    """Create Graphviz DOT content for a family tree diagram.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Main individual (center of tree)

    Returns:
        String containing DOT content for the family tree
    """
    family_info = get_family_info(gedcom_parser, individual)
    main_name = format_name(individual)
    main_id = individual.get_pointer()

    # Create DOT content for Graphviz
    dot_content = []
    dot_content.append("digraph FamilyTree {")
    dot_content.append("    rankdir=TB;")
    dot_content.append("    bgcolor=white;")
    dot_content.append(
        '    node [shape=box, style="filled,rounded", fillcolor=lightblue, fontname="Arial", fontsize=10, margin=0.1];'
    )
    dot_content.append(
        '    edge [color=gray, fontname="Arial", fontsize=9, penwidth=2];'
    )
    dot_content.append("    graph [splines=ortho, nodesep=0.8, ranksep=1.2];")
    dot_content.append("")

    # Define the main person (center)
    dot_content.append(
        f'    "{main_id}" [label="{main_name}\\n({main_id})", fillcolor="#90EE90", fontsize=12, penwidth=3];'
    )
    dot_content.append("")

    # Add parents (above)
    if family_info["parents"]:
        dot_content.append("    // Parents")
        for relation, parent in family_info["parents"]:
            parent_name = format_name(parent)
            parent_id = parent.get_pointer()
            parent_birth = parent.get_birth_data()
            birth_year = ""
            if parent_birth and parent_birth[0]:
                # Extract year from date - get last 4 digits which should be year
                date_str = parent_birth[0].strip()
                if len(date_str) >= 4:
                    # Look for 4-digit year at the end
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{parent_id}" [label="{parent_name}\\n({parent_id}){birth_year}", fillcolor="#FFFFE0"];'
            )
            dot_content.append(
                f'    "{parent_id}" -> "{main_id}" [label="{relation.lower()}"];'
            )
        dot_content.append("")

    # Add spouse (to the side)
    if family_info["spouses"]:
        dot_content.append("    // Spouse(s)")
        for i, spouse in enumerate(family_info["spouses"]):
            spouse_name = format_name(spouse)
            spouse_id = spouse.get_pointer()
            spouse_birth = spouse.get_birth_data()
            birth_year = ""
            if spouse_birth and spouse_birth[0]:
                date_str = spouse_birth[0].strip()
                if len(date_str) >= 4:
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{spouse_id}" [label="{spouse_name}\\n({spouse_id}){birth_year}", fillcolor="#FFB6C1"];'
            )
            dot_content.append(
                f'    "{main_id}" -> "{spouse_id}" [label="married", style=dashed, dir=none];'
            )
        dot_content.append("")

    # Add children (below)
    if family_info["children"]:
        dot_content.append("    // Children")
        for child in family_info["children"]:
            child_name = format_name(child)
            child_id = child.get_pointer()
            child_birth = child.get_birth_data()
            birth_year = ""
            if child_birth and child_birth[0]:
                date_str = child_birth[0].strip()
                if len(date_str) >= 4:
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{child_id}" [label="{child_name}\\n({child_id}){birth_year}", fillcolor="#E0FFFF"];'
            )
            dot_content.append(f'    "{main_id}" -> "{child_id}" [label="parent"];')
        dot_content.append("")

    dot_content.append("}")

    return "\n".join(dot_content)


def create_family_tree_diagram(gedcom_parser, individual, output_dir):
    """Create a Graphviz family tree diagram.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Main individual (center of tree)
        output_dir: Directory to save the diagram

    Returns:
        Path to the generated PNG file
    """
    family_info = get_family_info(gedcom_parser, individual)
    main_name = format_name(individual)
    main_id = individual.get_pointer()

    # Create DOT content for Graphviz
    dot_content = []
    dot_content.append("digraph FamilyTree {")
    dot_content.append("    rankdir=TB;")
    dot_content.append("    bgcolor=white;")
    dot_content.append(
        '    node [shape=box, style="filled,rounded", fillcolor=lightblue, fontname="Arial", fontsize=10, margin=0.1];'
    )
    dot_content.append(
        '    edge [color=gray, fontname="Arial", fontsize=9, penwidth=2];'
    )
    dot_content.append("    graph [splines=ortho, nodesep=0.8, ranksep=1.2];")
    dot_content.append("")

    # Define the main person (center)
    dot_content.append(
        f'    "{main_id}" [label="{main_name}\\n({main_id})", fillcolor="#90EE90", fontsize=12, penwidth=3];'
    )
    dot_content.append("")

    # Add parents (above)
    if family_info["parents"]:
        dot_content.append("    // Parents")
        for relation, parent in family_info["parents"]:
            parent_name = format_name(parent)
            parent_id = parent.get_pointer()
            parent_birth = parent.get_birth_data()
            birth_year = ""
            if parent_birth and parent_birth[0]:
                # Extract year from date - get last 4 digits which should be year
                date_str = parent_birth[0].strip()
                if len(date_str) >= 4:
                    # Look for 4-digit year at the end
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{parent_id}" [label="{parent_name}\\n({parent_id}){birth_year}", fillcolor="#FFFFE0"];'
            )
            dot_content.append(
                f'    "{parent_id}" -> "{main_id}" [label="{relation.lower()}"];'
            )
        dot_content.append("")

    # Add spouse (to the side)
    if family_info["spouses"]:
        dot_content.append("    // Spouse(s)")
        for i, spouse in enumerate(family_info["spouses"]):
            spouse_name = format_name(spouse)
            spouse_id = spouse.get_pointer()
            spouse_birth = spouse.get_birth_data()
            birth_year = ""
            if spouse_birth and spouse_birth[0]:
                date_str = spouse_birth[0].strip()
                if len(date_str) >= 4:
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{spouse_id}" [label="{spouse_name}\\n({spouse_id}){birth_year}", fillcolor="#FFB6C1"];'
            )
            dot_content.append(
                f'    "{main_id}" -> "{spouse_id}" [label="married", style=dashed, dir=none];'
            )
        dot_content.append("")

    # Add children (below)
    if family_info["children"]:
        dot_content.append("    // Children")
        for child in family_info["children"]:
            child_name = format_name(child)
            child_id = child.get_pointer()
            child_birth = child.get_birth_data()
            birth_year = ""
            if child_birth and child_birth[0]:
                date_str = child_birth[0].strip()
                if len(date_str) >= 4:
                    if date_str[-4:].isdigit():
                        birth_year = f"\\nb. {date_str[-4:]}"
                    elif len(date_str) >= 4 and date_str[:4].isdigit():
                        birth_year = f"\\nb. {date_str[:4]}"

            dot_content.append(
                f'    "{child_id}" [label="{child_name}\\n({child_id}){birth_year}", fillcolor="#E0FFFF"];'
            )
            dot_content.append(f'    "{main_id}" -> "{child_id}" [label="parent"];')
        dot_content.append("")

    dot_content.append("}")

    # Write DOT file and generate PNG
    dot_file = (
        Path(output_dir) / f"{main_name.lower().replace(' ', '_')}_family_tree.dot"
    )
    png_file = (
        Path(output_dir) / f"{main_name.lower().replace(' ', '_')}_family_tree.png"
    )

    # Clean filename
    clean_main_name = re.sub(r"[^a-zA-Z0-9_]", "_", main_name.lower())
    dot_file = Path(output_dir) / f"{clean_main_name}_family_tree.dot"
    png_file = Path(output_dir) / f"{clean_main_name}_family_tree.png"

    try:
        # Write DOT file
        with open(dot_file, "w", encoding="utf-8") as f:
            f.write("\n".join(dot_content))

        # Generate PNG using Graphviz
        subprocess.run(
            ["dot", "-Tpng", str(dot_file), "-o", str(png_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        if png_file.exists():
            print(f"Family tree diagram generated: {png_file}")
            return png_file
        else:
            print("Warning: PNG file was not created")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error generating family tree diagram: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error creating family tree diagram: {e}")
        return None


def generate_asciidoc(gedcom_parser, individual, output_file=None):
    """Generate AsciiDoc format genealogy document for an individual.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Individual element to generate document for
        output_file: Optional output file path (defaults to family_tree.adoc)
    """
    name = format_name(individual)
    pointer = individual.get_pointer()

    # Start building the AsciiDoc content
    lines = []
    lines.append(f"= {name}")

    # Add table of contents unless disabled
    if not getattr(generate_asciidoc, "_no_toc", False):
        lines.append(":toc:")
        lines.append(":toc-title: Table of Contents")
        lines.append(":numbered:")
    else:
        lines.append(":numbered:")

    lines.append("")
    lines.append("== Personal Information")
    lines.append("")
    lines.append(f"*Full Name:* {name}")
    lines.append("")
    lines.append(f"*ID:* {pointer}")
    lines.append("")

    # Gender
    gender = individual.get_gender()
    if gender:
        lines.append(f"*Gender:* {gender}")
        lines.append("")

    # Birth information
    birth_data = individual.get_birth_data()
    if birth_data and (birth_data[0] or birth_data[1]):
        if birth_data[0]:
            lines.append(f"*Birth Date:* {birth_data[0]}")
        if birth_data[1]:
            lines.append(f"*Birth Place:* {birth_data[1]}")
        lines.append("")

    # Death information
    death_data = individual.get_death_data()
    if death_data and (death_data[0] or death_data[1]):
        if death_data[0]:
            lines.append(f"*Death Date:* {death_data[0]}")
        if death_data[1]:
            lines.append(f"*Death Place:* {death_data[1]}")
        lines.append("")

    # Generate family tree diagram (if not disabled)
    if not getattr(generate_asciidoc, "_no_tree", False):
        lines.append("== Family Tree Diagram")
        lines.append("")

        # Check if we should use external PNG or embed DOT content (default)
        if getattr(generate_asciidoc, "_external_png", False):
            # Generate PNG file (legacy method)
            if output_file:
                output_dir = Path(output_file).parent
            else:
                output_dir = Path.cwd()

            family_tree_image = create_family_tree_diagram(
                gedcom_parser, individual, output_dir
            )
            if family_tree_image:
                lines.append(
                    f'image::{family_tree_image.name}[Family Tree, align="center"]'
                )
        else:
            # Embed DOT content directly in AsciiDoc (default)
            dot_content = create_family_tree_dot_content(gedcom_parser, individual)
            lines.append('[graphviz, "family-tree", png]')
            lines.append("----")
            lines.append(dot_content)
            lines.append("----")

        lines.append("")

    # Family information - consolidated into one section
    family_info = get_family_info(gedcom_parser, individual)

    # Only create Family Information section if there are family members
    if family_info["parents"] or family_info["spouses"] or family_info["children"]:
        lines.append("== Family Information")
        lines.append("")

        if family_info["parents"]:
            lines.append("=== Parents")
            lines.append("")
            for relation, parent in family_info["parents"]:
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

        if family_info["spouses"]:
            lines.append("=== Spouse(s)")
            lines.append("")
            for spouse in family_info["spouses"]:
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

        if family_info["children"]:
            lines.append("=== Children")
            lines.append("")
            for child in family_info["children"]:
                child_name = format_name(child)
                child_id = child.get_pointer()
                lines.append(f"* *{child_name}* ({child_id})")

                child_birth = child.get_birth_data()
                if child_birth and child_birth[0]:
                    lines.append(f"** Born: {child_birth[0]}")
            lines.append("")

    # Add a footer - made less prominent
    lines.append("=== Document Information")
    lines.append("")
    lines.append(
        "This document was automatically generated from a GEDCOM file "
        "using the GEDCOM Visualizer tool."
    )
    lines.append("")

    # Write to file or stdout
    content = "\n".join(lines)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"AsciiDoc document written to: {output_file}")
    else:
        # Generate default filename based on individual's name
        name = individual.get_name()
        if name and name[0]:
            # Clean the name for use as filename
            clean_name = re.sub(r"[^\w\s-]", "", name[0].strip())
            clean_name = re.sub(r"\s+", "_", clean_name).lower()
            default_output = f"{clean_name}.adoc"
        else:
            default_output = "family_tree.adoc"

        with open(default_output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"AsciiDoc document written to: {default_output}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate AsciiDoc document for an individual from a " "GEDCOM file"
    )
    parser.add_argument("gedcom_file", help="Path to the GEDCOM file")
    parser.add_argument("individual_id", help="ID of the individual (e.g., @I1@ or I1)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: individual_name.adoc)",
        metavar="FILE",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Disable family tree diagram generation (text-only)",
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Disable table of contents for more compact layout",
    )
    parser.add_argument(
        "--external-png",
        action="store_true",
        help="Generate external PNG files instead of embedding DOT content (legacy mode)",
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
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error parsing GEDCOM file: {e}", file=sys.stderr)
        sys.exit(1)

    # Get individual
    individual = get_individual_by_id(gedcom_parser, args.individual_id)
    if not individual:
        print(
            f"Error: Individual with ID '{args.individual_id}' not found",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate AsciiDoc
    try:
        # Set the flags if specified
        generate_asciidoc._no_tree = args.no_tree
        generate_asciidoc._no_toc = args.no_toc
        generate_asciidoc._external_png = args.external_png
        generate_asciidoc(gedcom_parser, individual, args.output)
    except (OSError, IOError) as e:
        print(f"Error generating AsciiDoc: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
