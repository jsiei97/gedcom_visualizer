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
import html
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
        Dictionary with parents, spouses, children, and siblings
    """
    result = {"parents": [], "spouses": [], "children": [], "siblings": []}

    # Get parents
    parents = gedcom_parser.get_parents(individual)
    for parent in parents:
        if parent.get_gender() == "M":
            result["parents"].append(("Father", parent))
        elif parent.get_gender() == "F":
            result["parents"].append(("Mother", parent))
        else:
            result["parents"].append(("Parent", parent))

    # Get siblings - find other children of the same parents
    individual_pointer = individual.get_pointer()
    element_dict = gedcom_parser.get_element_dictionary()

    # Get all families where parents are spouses to find siblings
    for relation, parent_individual in result["parents"]:
        parent_families = gedcom_parser.get_families(parent_individual)
        for family in parent_families:
            family_elements = family.get_child_elements()
            for element in family_elements:
                if element.get_tag() == "CHIL":
                    sibling_pointer = element.get_value()
                    # Skip the individual themselves
                    if sibling_pointer != individual_pointer:
                        sibling = element_dict.get(sibling_pointer)
                        if sibling and sibling not in result["siblings"]:
                            result["siblings"].append(sibling)

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


def format_name_with_maiden_married(individual):
    """Format individual's name including both maiden and married names when available.

    Args:
        individual: IndividualElement object

    Returns:
        Formatted name string with maiden/married information
    """
    name_parts = individual.get_name()
    if not name_parts or not name_parts[0]:
        return "Unknown"

    given_name = name_parts[0]
    birth_surname = name_parts[1] if len(name_parts) > 1 and name_parts[1] else ""

    # Check for married name
    married_name = None
    for element in individual.get_child_elements():
        if element.get_tag() == "NAME":
            for name_element in element.get_child_elements():
                if name_element.get_tag() == "_MARNM" and name_element.get_value():
                    married_name = name_element.get_value().strip()
                    break
            if married_name:
                break

    # Format the name based on what information we have
    if married_name and birth_surname and married_name != birth_surname:
        # Both maiden and married names - use married name as primary, show maiden in parentheses
        return f"{given_name} {married_name} (born {birth_surname})"
    elif married_name:
        # Only married name available
        return f"{given_name} {married_name}"
    elif birth_surname:
        # Only birth surname available
        return f"{given_name} {birth_surname}"
    else:
        # Only given name available
        return given_name


def clean_html_source_text(text):
    """Clean HTML-encoded text from GEDCOM sources for better readability.

    Args:
        text: HTML-encoded text string

    Returns:
        Cleaned text with HTML entities decoded and line breaks properly formatted
    """
    if not text:
        return text

    # Handle double-encoded HTML entities (common in GEDCOM exports)
    # First pass: decode &amp;lt; to &lt; etc.
    cleaned = html.unescape(text)

    # Second pass: decode remaining entities like &lt; to < etc.
    cleaned = html.unescape(cleaned)

    # Replace HTML line breaks with AsciiDoc line break syntax
    cleaned = cleaned.replace("<br>", " +\n** ")  # Create proper AsciiDoc sub-bullets
    cleaned = cleaned.replace("<BR>", " +\n** ")
    cleaned = cleaned.replace("<br/>", " +\n** ")
    cleaned = cleaned.replace("<BR/>", " +\n** ")

    # Clean up any remaining HTML tags (simple approach)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    # Clean up multiple spaces and normalize whitespace, but preserve the line structure we created
    lines = cleaned.split("\n")
    cleaned_lines = []
    for line in lines:
        line = re.sub(r"\s+", " ", line.strip())
        if line:
            cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)

    return cleaned


def format_dates_for_dot(individual):
    """Format birth and death dates for DOT diagram labels in ISO format.

    Args:
        individual: Individual element from GEDCOM

    Returns:
        Formatted date string for DOT label (e.g., "\\nb. 1890-03-29\\nd. 1979-09-12")
    """
    dates_info = ""

    # Get birth date
    birth_data = individual.get_birth_data()
    if birth_data and birth_data[0]:
        birth_str = birth_data[0].strip()
        # Try to convert to ISO format YYYY-MM-DD
        iso_birth = convert_to_iso_date(birth_str)
        if iso_birth:
            dates_info += f"\\nb. {iso_birth}"

    # Get death date
    death_data = individual.get_death_data()
    if death_data and death_data[0]:
        death_str = death_data[0].strip()
        # Try to convert to ISO format YYYY-MM-DD
        iso_death = convert_to_iso_date(death_str)
        if iso_death:
            dates_info += f"\\nd. {iso_death}"

    return dates_info


def convert_to_iso_date(date_str):
    """Convert various date formats to ISO format YYYY-MM-DD.

    Args:
        date_str: Date string in various formats

    Returns:
        ISO formatted date string or None if can't be parsed
    """
    import re

    # Remove extra whitespace
    date_str = date_str.strip()

    # Pattern for DD MMM YYYY (e.g., "29 MAR 1890")
    pattern1 = r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})"
    match1 = re.match(pattern1, date_str)
    if match1:
        day, month_abbr, year = match1.groups()
        month_map = {
            "JAN": "01",
            "FEB": "02",
            "MAR": "03",
            "APR": "04",
            "MAY": "05",
            "JUN": "06",
            "JUL": "07",
            "AUG": "08",
            "SEP": "09",
            "OCT": "10",
            "NOV": "11",
            "DEC": "12",
        }
        if month_abbr in month_map:
            return f"{year}-{month_map[month_abbr]}-{day.zfill(2)}"

    # Pattern for YYYY-MM-DD (already ISO format)
    pattern2 = r"(\d{4})-(\d{1,2})-(\d{1,2})"
    match2 = re.match(pattern2, date_str)
    if match2:
        year, month, day = match2.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Pattern for just year YYYY
    pattern3 = r"^(\d{4})$"
    match3 = re.match(pattern3, date_str)
    if match3:
        return match3.group(1)  # Return just the year

    # If no pattern matches, return None
    return None


def create_family_tree_dot_content(gedcom_parser, individual):
    """Create Graphviz DOT content for a family tree diagram.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Main individual (center of tree)

    Returns:
        String containing DOT content for the family tree
    """
    family_info = get_family_info(gedcom_parser, individual)
    main_name = format_name_with_maiden_married(individual)
    main_id = individual.get_pointer()

    # Create DOT content for Graphviz
    dot_content = []
    dot_content.append("digraph FamilyTree {")
    dot_content.append("    rankdir=LR;")
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
    main_dates_info = format_dates_for_dot(individual)
    dot_content.append(
        f'    "{main_id}" [label="{main_name}{main_dates_info}", fillcolor="#90EE90", fontsize=12, penwidth=3];'
    )
    dot_content.append("")

    # Add parents (above)
    if family_info["parents"]:
        dot_content.append("    // Parents")
        for relation, parent in family_info["parents"]:
            parent_name = format_name_with_maiden_married(parent)
            parent_id = parent.get_pointer()
            dates_info = format_dates_for_dot(parent)

            dot_content.append(
                f'    "{parent_id}" [label="{parent_name}{dates_info}", fillcolor="#FFFFE0"];'
            )
            dot_content.append(
                f'    "{parent_id}" -> "{main_id}" [label="{relation.lower()}"];'
            )
        dot_content.append("")

    # Add spouse (to the side, same rank as main person)
    if family_info["spouses"]:
        dot_content.append("    // Spouse(s) - positioned at same level as main person")
        spouse_ids = []
        for i, spouse in enumerate(family_info["spouses"]):
            spouse_name = format_name_with_maiden_married(spouse)
            spouse_id = spouse.get_pointer()
            spouse_ids.append(spouse_id)
            dates_info = format_dates_for_dot(spouse)

            dot_content.append(
                f'    "{spouse_id}" [label="{spouse_name}{dates_info}", fillcolor="#FFB6C1"];'
            )
            dot_content.append(
                f'    "{main_id}" -> "{spouse_id}" [label="married", style=dashed, dir=none];'
            )

        # Force main person and spouse(s) to be at the same rank (horizontal level)
        if spouse_ids:
            spouse_list = '"; "'.join(spouse_ids)
            dot_content.append(f'    {{ rank=same; "{main_id}"; "{spouse_list}"; }}')
        dot_content.append("")
    # Add children (below)
    if family_info["children"]:
        dot_content.append("    // Children")
        for child in family_info["children"]:
            child_name = format_name_with_maiden_married(child)
            child_id = child.get_pointer()
            dates_info = format_dates_for_dot(child)

            dot_content.append(
                f'    "{child_id}" [label="{child_name}{dates_info}", fillcolor="#E0FFFF"];'
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
    main_name = format_name_with_maiden_married(individual)

    # Generate DOT content using our dedicated function
    dot_content = create_family_tree_dot_content(gedcom_parser, individual)

    # Clean filename
    clean_main_name = re.sub(r"[^a-zA-Z0-9_]", "_", main_name.lower())
    dot_file = Path(output_dir) / f"{clean_main_name}_family_tree.dot"
    png_file = Path(output_dir) / f"{clean_main_name}_family_tree.png"

    try:
        # Write DOT file
        with open(dot_file, "w", encoding="utf-8") as f:
            f.write(dot_content)

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


def get_comprehensive_biographical_info(gedcom_parser, individual):
    """Extract comprehensive biographical information from GEDCOM.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Individual element

    Returns:
        Dictionary with comprehensive biographical information
    """
    bio_info = {
        "life_events": [],
        "residences": [],
        "contact": {},
        "sources": [],
        "metadata": {},
    }

    element_dict = gedcom_parser.get_element_dictionary()
    child_elements = individual.get_child_elements()

    # Extract comprehensive life events
    for element in child_elements:
        tag = element.get_tag()

        # Major life events
        if tag in [
            "BIRT",
            "DEAT",
            "BURI",
            "MARR",
            "DIV",
            "OCCU",
            "EDUC",
            "RELI",
            "NATU",
            "EMIG",
            "IMMI",
        ]:
            event = {"type": tag, "date": None, "place": None, "details": {}}

            # Extract details from sub-elements
            for sub_element in element.get_child_elements():
                sub_tag = sub_element.get_tag()
                sub_value = sub_element.get_value()

                if sub_tag == "DATE":
                    event["date"] = sub_value
                elif sub_tag == "PLAC":
                    event["place"] = sub_value
                else:
                    event["details"][sub_tag] = sub_value

            bio_info["life_events"].append(event)

        # Residence information (separate from life events for better organization)
        elif tag == "RESI":
            residence = {"date": None, "address": None, "place": None, "contact": {}}

            for sub_element in element.get_child_elements():
                sub_tag = sub_element.get_tag()
                sub_value = sub_element.get_value()

                if sub_tag == "DATE":
                    residence["date"] = sub_value
                elif sub_tag == "ADDR":
                    residence["address"] = sub_value
                elif sub_tag == "PLAC":
                    residence["place"] = sub_value
                elif sub_tag == "EMAIL":
                    # Fix double @ symbols that might be used for escaping
                    email = sub_value.replace("@@", "@")
                    residence["contact"]["email"] = email
                    bio_info["contact"]["email"] = email  # Also store in main contact
                elif sub_tag == "PHON":
                    residence["contact"]["phone"] = sub_value
                    bio_info["contact"]["phone"] = sub_value

            # Only add if there's meaningful residence data
            if (
                residence["date"]
                or residence["address"]
                or residence["place"]
                or residence["contact"]
            ):
                bio_info["residences"].append(residence)

        # Source information
        elif tag == "SOUR":
            source_id = element.get_value()
            source_info = {
                "id": source_id,
                "title": None,
                "author": None,
                "quality": None,
                "event": None,
                "notes": [],
                "data_text": None,
            }

            # Get source details from the element
            for sub_element in element.get_child_elements():
                if sub_element.get_tag() == "NOTE":
                    source_info["notes"].append(sub_element.get_value())
                elif sub_element.get_tag() == "QUAY":
                    source_info["quality"] = sub_element.get_value()
                elif sub_element.get_tag() == "EVEN":
                    source_info["event"] = sub_element.get_value()
                elif sub_element.get_tag() == "DATA":
                    for data_sub in sub_element.get_child_elements():
                        if data_sub.get_tag() == "TEXT":
                            source_info["data_text"] = data_sub.get_value()

            # Get additional source record information
            source_element = element_dict.get(source_id)
            if source_element:
                for child in source_element.get_child_elements():
                    if child.get_tag() == "AUTH":
                        source_info["author"] = child.get_value()
                    elif child.get_tag() == "TITL":
                        source_info["title"] = child.get_value()
                    elif child.get_tag() == "TEXT":
                        source_info["description"] = child.get_value()

            bio_info["sources"].append(source_info)

        # Metadata
        elif tag == "_UPD":
            bio_info["metadata"]["last_updated"] = element.get_value()
        elif tag == "RIN":
            bio_info["metadata"]["record_id"] = element.get_value()
        elif tag == "_UID":
            bio_info["metadata"]["unique_id"] = element.get_value()

    return bio_info


def collect_ancestors_recursive(
    gedcom_parser, individual, max_generations, current_generation=1, visited=None
):
    """Recursively collect ancestors up to the specified number of generations.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Individual element to start from
        max_generations: Maximum number of generations to collect (0 = unlimited)
        current_generation: Current generation level (1-based)
        visited: Set of already visited individual IDs to prevent infinite loops

    Returns:
        List of tuples: (individual, generation_level)
    """
    if visited is None:
        visited = set()

    result = []
    individual_id = individual.get_pointer()

    # Avoid infinite loops
    if individual_id in visited:
        return result

    visited.add(individual_id)
    result.append((individual, current_generation))

    # If we've reached the max generations limit, stop (unless max_generations is 0 for unlimited)
    if max_generations > 0 and current_generation >= max_generations:
        return result

    # Get parents and recurse
    family_info = get_family_info(gedcom_parser, individual)
    for relation, parent in family_info["parents"]:
        parent_ancestors = collect_ancestors_recursive(
            gedcom_parser, parent, max_generations, current_generation + 1, visited
        )
        result.extend(parent_ancestors)

    return result


def generate_cross_reference_link(person_id, person_name, chapter_individuals):
    """Generate a cross-reference link if the person has a chapter, otherwise just show the name.

    Args:
        person_id: The GEDCOM ID of the person (e.g., @I500005@)
        person_name: The formatted name of the person
        chapter_individuals: Set of individual IDs that have their own chapters

    Returns:
        String with either a clickable link or plain text name (no ID tags)
    """
    if person_id in chapter_individuals:
        # Create a clickable cross-reference link with clean anchor ID
        clean_id = person_id.replace("@", "")
        return f"<<{clean_id},{person_name}>>"
    else:
        # Just show the name without ID
        return f"{person_name}"


def generate_individual_content(
    gedcom_parser, individual, is_main_person=True, chapter_individuals=None
):
    """Generate AsciiDoc content for a single individual.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Individual element to generate content for
        is_main_person: Whether this is the main person (affects chapter level)
        chapter_individuals: Set of individual IDs that have their own chapters

    Returns:
        List of content lines for the individual
    """
    if chapter_individuals is None:
        chapter_individuals = set()
    lines = []

    # Use full married name for chapter title, matching the document title approach
    chapter_name = format_name_with_maiden_married(individual)
    # For chapter title, we want just the name without the "(born ...)" part
    if " (born " in chapter_name:
        chapter_name = chapter_name.split(" (born ")[0]

    # Set chapter title using the full name - main person uses ==, parents use ==
    if is_main_person:
        chapter_title = f"== {chapter_name} - Personal Information"
    else:
        chapter_title = f"== {chapter_name} - Personal Information"

    pointer = individual.get_pointer()

    # Add anchor label for cross-referencing (remove @ symbols for valid anchors)
    clean_id = pointer.replace("@", "")
    # Use proper anchor syntax at the end of the chapter title
    lines.append(f"{chapter_title} [[{clean_id}]]")
    lines.append("")
    # Use enhanced name formatting that shows maiden/married names
    enhanced_name = format_name_with_maiden_married(individual)
    lines.append(f"*Full Name:* {enhanced_name}")
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
        lines.append("=== Family Tree Diagram")
        lines.append("")

        # Check if we should use external PNG or embed DOT content (default)
        if getattr(generate_asciidoc, "_external_png", False):
            # For parents, we don't generate separate PNG files to avoid complexity
            # Just show a note that tree is available in main chapter
            if not is_main_person:
                lines.append("_See main family tree diagram in the first chapter._")
                lines.append("")
            else:
                # Generate PNG file (legacy method) only for main person
                if hasattr(generate_asciidoc, "_output_dir"):
                    output_dir = generate_asciidoc._output_dir
                else:
                    output_dir = Path.cwd()

                family_tree_image = create_family_tree_diagram(
                    gedcom_parser, individual, output_dir
                )
                if family_tree_image:
                    lines.append(
                        f'image::{family_tree_image.name}[Family Tree, align="center"]'
                    )
                lines.append("")
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
    if (
        family_info["parents"]
        or family_info["spouses"]
        or family_info["children"]
        or family_info["siblings"]
    ):
        lines.append("=== Family Relationships")
        lines.append("")

        if family_info["parents"]:
            lines.append("==== Parents")
            lines.append("")
            for relation, parent in family_info["parents"]:
                parent_name = format_name_with_maiden_married(parent)
                parent_id = parent.get_pointer()
                parent_link = generate_cross_reference_link(
                    parent_id, parent_name, chapter_individuals
                )
                lines.append(f"* *{relation}:* {parent_link}")

                parent_birth = parent.get_birth_data()
                if parent_birth and parent_birth[0]:
                    lines.append(f"** Born: {parent_birth[0]}")

                parent_death = parent.get_death_data()
                if parent_death and parent_death[0]:
                    lines.append(f"** Died: {parent_death[0]}")
            lines.append("")

        if family_info["siblings"]:
            lines.append("==== Brothers and Sisters")
            lines.append("")
            for sibling in family_info["siblings"]:
                sibling_name = format_name_with_maiden_married(sibling)
                sibling_id = sibling.get_pointer()

                # Determine relationship based on gender
                gender = sibling.get_gender()
                if gender == "M":
                    relation = "Brother"
                elif gender == "F":
                    relation = "Sister"
                else:
                    relation = "Sibling"

                sibling_link = generate_cross_reference_link(
                    sibling_id, sibling_name, chapter_individuals
                )
                lines.append(f"* *{relation}:* {sibling_link}")

                sibling_birth = sibling.get_birth_data()
                if sibling_birth and sibling_birth[0]:
                    lines.append(f"** Born: {sibling_birth[0]}")

                sibling_death = sibling.get_death_data()
                if sibling_death and sibling_death[0]:
                    lines.append(f"** Died: {sibling_death[0]}")
            lines.append("")

        if family_info["spouses"]:
            lines.append("==== Spouse(s)")
            lines.append("")
            for spouse in family_info["spouses"]:
                spouse_name = format_name_with_maiden_married(spouse)
                spouse_id = spouse.get_pointer()
                spouse_link = generate_cross_reference_link(
                    spouse_id, spouse_name, chapter_individuals
                )
                lines.append(f"* {spouse_link}")

                spouse_birth = spouse.get_birth_data()
                if spouse_birth and spouse_birth[0]:
                    lines.append(f"** Born: {spouse_birth[0]}")

                spouse_death = spouse.get_death_data()
                if spouse_death and spouse_death[0]:
                    lines.append(f"** Died: {spouse_death[0]}")
            lines.append("")

        if family_info["children"]:
            lines.append("==== Children")
            lines.append("")
            for child in family_info["children"]:
                child_name = format_name_with_maiden_married(child)
                child_id = child.get_pointer()
                child_link = generate_cross_reference_link(
                    child_id, child_name, chapter_individuals
                )
                lines.append(f"* {child_link}")

                child_birth = child.get_birth_data()
                if child_birth and child_birth[0]:
                    lines.append(f"** Born: {child_birth[0]}")
            lines.append("")

    # Add comprehensive biographical information section
    bio_info = get_comprehensive_biographical_info(gedcom_parser, individual)

    # Check if we have any additional biographical information to show
    has_bio_info = (
        bio_info["life_events"]
        or bio_info["residences"]
        or bio_info["contact"]
        or bio_info["sources"]
        or bio_info["metadata"]
    )

    # Only show Additional Information section if not disabled and we have info
    if has_bio_info and not getattr(generate_asciidoc, "_no_additional_info", False):
        lines.append("=== Additional Information")
        lines.append("")

        # Life events (beyond basic birth/death already shown)
        significant_events = [
            event for event in bio_info["life_events"] if event["type"] not in ["BIRT"]
        ]  # Birth already shown in Personal Information

        if significant_events:
            lines.append("==== Life Events")
            lines.append("")

            event_names = {
                "DEAT": "Death",
                "BURI": "Burial",
                "MARR": "Marriage",
                "DIV": "Divorce",
                "OCCU": "Occupation",
                "EDUC": "Education",
                "RELI": "Religion",
                "NATU": "Naturalization",
                "EMIG": "Emigration",
                "IMMI": "Immigration",
            }

            for event in significant_events:
                event_name = event_names.get(event["type"], event["type"])
                lines.append(f"*{event_name}:*")

                if event["date"]:
                    lines.append(f"** Date: {event['date']}")
                if event["place"]:
                    lines.append(f"** Place: {event['place']}")

                # Add any other details
                for detail_key, detail_value in event["details"].items():
                    if detail_key not in ["DATE", "PLAC"] and detail_value:
                        lines.append(f"** {detail_key}: {detail_value}")

                lines.append("")

        # Residence history
        if bio_info["residences"]:
            lines.append("==== Residence History")
            lines.append("")

            for i, residence in enumerate(bio_info["residences"], 1):
                if len(bio_info["residences"]) > 1:
                    lines.append(f"*Residence {i}:*")
                else:
                    lines.append("*Residence:*")

                if residence["date"]:
                    lines.append(f"** Period: {residence['date']}")
                if residence["address"]:
                    lines.append(f"** Address: {residence['address']}")
                if residence["place"]:
                    lines.append(f"** Place: {residence['place']}")

                # Contact info for this residence
                if residence["contact"]:
                    if residence["contact"].get("email"):
                        lines.append(f"** Email: {residence['contact']['email']}")
                    if residence["contact"].get("phone"):
                        lines.append(f"** Phone: {residence['contact']['phone']}")

                lines.append("")

        # Contact information (if not already covered in residences)
        standalone_contact = {
            k: v
            for k, v in bio_info["contact"].items()
            if not any(r["contact"].get(k) for r in bio_info["residences"])
        }

        if standalone_contact:
            lines.append("==== Contact Information")
            lines.append("")
            for contact_type, contact_value in standalone_contact.items():
                if contact_type == "email":
                    lines.append(f"* *Email:* {contact_value}")
                elif contact_type == "phone":
                    lines.append(f"* *Phone:* {contact_value}")
            lines.append("")

        # Source information
        if bio_info["sources"]:
            lines.append("==== Sources and References")
            lines.append("")
            for i, source in enumerate(bio_info["sources"], 1):
                if source.get("title") or source.get("author"):
                    lines.append(f"*Source {i}:*")
                    if source.get("title"):
                        lines.append(f"** Title: {source['title']}")
                    if source.get("author"):
                        lines.append(f"** Author: {source['author']}")
                    if source.get("quality"):
                        quality_desc = {
                            "0": "Unreliable evidence",
                            "1": "Questionable reliability",
                            "2": "Secondary evidence",
                            "3": "Direct and primary evidence",
                        }
                        quality_text = quality_desc.get(
                            source["quality"], f"Quality level {source['quality']}"
                        )
                        lines.append(f"** Quality: {quality_text}")
                    if source.get("event"):
                        lines.append(f"** Event Type: {source['event']}")
                    if source.get("data_text"):
                        cleaned_details = clean_html_source_text(source["data_text"])
                        lines.append(f"** Details: {cleaned_details}")
                    if source["notes"]:
                        lines.append(f"** Notes: {', '.join(source['notes'])}")
                    lines.append("")

        # Metadata
        if bio_info["metadata"]:
            lines.append("==== Record Information")
            lines.append("")
            if bio_info["metadata"].get("last_updated"):
                lines.append(
                    f"* *Last Updated:* {bio_info['metadata']['last_updated']}"
                )
            if bio_info["metadata"].get("record_id"):
                lines.append(f"* *Record ID:* {bio_info['metadata']['record_id']}")
            lines.append("")

    return lines


def generate_asciidoc(gedcom_parser, individual, output_file=None, generations=4):
    """Generate AsciiDoc format genealogy document for an individual.

    Args:
        gedcom_parser: Parsed GEDCOM data
        individual: Individual element to generate document for
        output_file: Optional output file path (defaults to family_tree.adoc)
        generations: Number of generations to include (1=main only, 2=+parents, etc.)
    """
    # Use enhanced name formatting for document title (prioritizes married names)
    document_title_name = format_name_with_maiden_married(individual)
    # For document title, we want just the name without the "(born ...)" part
    if " (born " in document_title_name:
        document_title_name = document_title_name.split(" (born ")[0]

    pointer = individual.get_pointer()

    # Store output directory for helper function if using external PNG
    if output_file:
        generate_asciidoc._output_dir = Path(output_file).parent
    else:
        generate_asciidoc._output_dir = Path.cwd()

    # Start building the AsciiDoc content
    lines = []
    lines.append(f"= {document_title_name}")

    # Add table of contents unless disabled
    if not getattr(generate_asciidoc, "_no_toc", False):
        lines.append(":toc:")
        lines.append(":toc-title: Table of Contents")
        lines.append(":numbered:")
    else:
        lines.append(":numbered:")

    lines.append("")

    # Collect all ancestors up to the specified number of generations
    all_ancestors = collect_ancestors_recursive(gedcom_parser, individual, generations)

    # Create a set of all individual IDs that will have chapters for cross-referencing
    chapter_individuals = {person.get_pointer() for person, _ in all_ancestors}

    # Generate content for each person, starting with the main person
    for i, (person, generation_level) in enumerate(all_ancestors):
        if i > 0:  # Add spacing between chapters (except before the first one)
            lines.append("")

        is_main_person = generation_level == 1
        person_content = generate_individual_content(
            gedcom_parser,
            person,
            is_main_person=is_main_person,
            chapter_individuals=chapter_individuals,
        )
        lines.extend(person_content)

    # Add a footer - made less prominent
    lines.append("")
    lines.append("== Document Information")
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
    parser.add_argument(
        "--no-additional-info",
        action="store_true",
        help="Disable Additional Information section (life events, residences, sources, etc.)",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=4,
        help="Number of generations to include (1=main person only, 2=+parents, 3=+grandparents, 4=+great-grandparents, etc. Default: 4, 0=all available)",
        metavar="N",
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
        generate_asciidoc._no_additional_info = args.no_additional_info
        generate_asciidoc(gedcom_parser, individual, args.output, args.generations)
    except (OSError, IOError) as e:
        print(f"Error generating AsciiDoc: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
