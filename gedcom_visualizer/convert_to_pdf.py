#!/usr/bin/env python3
"""Script 3: Convert AsciiDoc to PDF using Sphinx.

This script sets up a Sphinx project and converts an AsciiDoc document to
PDF format.
"""

import sys
import argparse
import os
import re
import shutil
import subprocess
import tempfile


def create_sphinx_config(source_dir, title="GEDCOM Document"):
    """Create Sphinx configuration file.

    Args:
        source_dir: Directory where Sphinx configuration will be created
        title: Title for the document
    """
    conf_content = f"""# Configuration file for Sphinx documentation builder
# Configured for European A4 paper standard

import os
import sys

# Project information
project = '{title}'
copyright = '2025, GEDCOM Visualizer'
author = 'GEDCOM Visualizer'
release = '1.0'

# General configuration
extensions = ['sphinx.ext.graphviz']

# The suffix of source filenames
source_suffix = {{
    '.rst': 'restructuredtext',
}}

# The master document
master_doc = 'index'

# List of patterns to ignore
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_rtd_theme'

# LaTeX output options for PDF - compact layout, A4 paper
latex_engine = 'pdflatex'
latex_elements = {{
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r'''
\\usepackage{{geometry}}
\\geometry{{margin=2cm}}
\\setcounter{{tocdepth}}{{3}}
\\setcounter{{secnumdepth}}{{3}}
    ''',
    'figure_align': 'htbp',
    'fncychap': '',
}}

# LaTeX documents
latex_documents = [
    (master_doc, 'document.tex', project, author, 'manual'),
]
"""

    conf_path = os.path.join(source_dir, "conf.py")
    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(conf_content)


def convert_asciidoc_to_rst(asciidoc_file, rst_file):
    """Convert AsciiDoc to ReStructuredText format.

    Args:
        asciidoc_file: Path to input AsciiDoc file
        rst_file: Path to output RST file
    """
    # Read AsciiDoc content
    with open(asciidoc_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    rst_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip AsciiDoc attributes
        if line.startswith(":") and line.endswith(":") and i < 5:
            i += 1
            continue

        # Convert title (= Title)
        if line.startswith("= "):
            title = line[2:].strip()
            rst_lines.append(title)
            rst_lines.append("=" * len(title))
            rst_lines.append("")

        # Convert section headers (== Section)
        elif line.startswith("== "):
            section = line[3:].strip()
            rst_lines.append(section)
            rst_lines.append("-" * len(section))
            rst_lines.append("")

        # Convert subsection headers (=== Subsection)
        elif line.startswith("=== "):
            subsection = line[4:].strip()
            rst_lines.append(subsection)
            rst_lines.append("~" * len(subsection))
            rst_lines.append("")

        # Convert sub-subsection headers (==== Sub-subsection)
        elif line.startswith("==== "):
            subsubsection = line[5:].strip()
            rst_lines.append(subsubsection)
            rst_lines.append("^" * len(subsubsection))
            rst_lines.append("")

        # Convert paragraph headers (===== Paragraph)
        elif line.startswith("===== "):
            paragraph = line[6:].strip()
            rst_lines.append(paragraph)
            rst_lines.append('"' * len(paragraph))
            rst_lines.append("")

        # Convert list items (*)
        elif line.startswith("* "):
            # Convert list markers and any bold text within
            converted = line.replace("* ", "- ", 1)
            converted = re.sub(r"\*([^\*]+?)\*", r"**\1**", converted)
            rst_lines.append(converted)

        # Convert nested list items (**)
        elif line.startswith("** "):
            # Convert list markers and any bold text within
            converted = line.replace("** ", "  - ", 1)
            converted = re.sub(r"\*([^\*]+?)\*", r"**\1**", converted)
            rst_lines.append(converted)

        # Convert AsciiDoc graphviz block to RST
        elif line.startswith("[graphviz"):
            # Start of graphviz block - parse the directive
            match = re.match(r'\[graphviz,\s*"([^"]*)",\s*([^\]]*)\]', line)
            if match:
                name = match.group(1)
                # Start RST graphviz directive
                rst_lines.append(".. graphviz::")
                rst_lines.append(f"   :name: {name}")
                rst_lines.append("   :align: center")
                rst_lines.append("")
                i += 1
                # Skip the opening ---- line
                if i < len(lines) and lines[i].strip() == "----":
                    i += 1
                # Copy DOT content until closing ----
                while i < len(lines) and lines[i].strip() != "----":
                    rst_lines.append("   " + lines[i].rstrip())
                    i += 1
                # Skip the closing ---- line (i will be incremented at end of loop)
                rst_lines.append("")
            else:
                rst_lines.append(line)

        # Convert AsciiDoc image directive to RST
        elif line.startswith("image::"):
            # Parse AsciiDoc image syntax: image::filename[alt text, options]
            match = re.match(r"image::([^\[]+)\[([^\]]*)\]", line)
            if match:
                filename = match.group(1)
                alt_and_options = match.group(2)

                # Extract alt text (first part before comma)
                alt_text = (
                    alt_and_options.split(",")[0].strip()
                    if alt_and_options
                    else "Image"
                )

                # Convert to RST image directive
                rst_lines.append(f".. image:: {filename}")
                rst_lines.append(f"   :alt: {alt_text}")
                rst_lines.append("   :align: center")
                rst_lines.append("")
            else:
                rst_lines.append(line)

        # Convert bold text (*text* to **text**) in other lines
        elif "*" in line:
            # Match and convert AsciiDoc bold syntax *word* to RST **word**
            converted = re.sub(r"\*([^\*]+?)\*", r"**\1**", line)
            rst_lines.append(converted)

        # Keep other lines as is
        else:
            rst_lines.append(line)

        i += 1

    # Write RST content
    with open(rst_file, "w", encoding="utf-8") as f:
        f.write("\n".join(rst_lines))


def build_pdf(sphinx_source_dir, output_dir):
    """Build PDF using Sphinx.

    Args:
        sphinx_source_dir: Directory containing Sphinx source files
        output_dir: Directory where PDF will be generated

    Returns:
        Path to generated PDF file or None if build failed
    """
    build_dir = os.path.join(output_dir, "_build")

    # Run sphinx-build to generate LaTeX
    latex_dir = os.path.join(build_dir, "latex")
    cmd = [
        "sphinx-build",
        "-b",
        "latex",
        "-q",  # Quiet mode
        sphinx_source_dir,
        latex_dir,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=False, check=False)
        if result.returncode != 0:
            # Try to decode stderr safely
            try:
                stderr_text = result.stderr.decode("utf-8", errors="replace")
            except (UnicodeDecodeError, AttributeError):
                stderr_text = str(result.stderr)
            print(f"Error building LaTeX: {stderr_text}", file=sys.stderr)
            return None
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Error running sphinx-build: {e}", file=sys.stderr)
        return None

    # Run pdflatex to generate PDF
    try:
        # Change to latex directory
        original_dir = os.getcwd()
        os.chdir(latex_dir)

        # Run pdflatex twice for proper references
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "document.tex"],
                capture_output=True,
                text=False,  # Handle binary output to avoid encoding issues
                check=False,
            )

        os.chdir(original_dir)

        pdf_path = os.path.join(latex_dir, "document.pdf")
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            print("Error: PDF file was not generated", file=sys.stderr)
            return None

    except FileNotFoundError:
        print(
            "Error: pdflatex not found. Please install texlive or a "
            "similar LaTeX distribution.",
            file=sys.stderr,
        )
        return None
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Error running pdflatex: {e}", file=sys.stderr)
        return None


def copy_referenced_images(asciidoc_file, source_dir, dest_dir):
    """Copy image files referenced in AsciiDoc to destination directory.

    Args:
        asciidoc_file: Path to AsciiDoc file
        source_dir: Directory where images are located
        dest_dir: Directory where images should be copied
    """
    try:
        with open(asciidoc_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all image:: references
        image_pattern = r"image::([^\[]+)\["
        matches = re.findall(image_pattern, content)

        for image_filename in matches:
            image_filename = image_filename.strip()
            source_path = os.path.join(source_dir, image_filename)
            dest_path = os.path.join(dest_dir, image_filename)

            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                print(f"Copied image: {image_filename}")
            else:
                print(f"Warning: Image file not found: {source_path}")

    except Exception as e:
        print(f"Warning: Error copying images: {e}")


def convert_asciidoc_to_pdf(asciidoc_file, output_file=None, title=None):
    """Convert AsciiDoc file to PDF.

    Args:
        asciidoc_file: Path to input AsciiDoc file
        output_file: Path to output PDF file (optional)
        title: Document title (optional, extracted from file if not provided)

    Returns:
        Path to generated PDF file or None if conversion failed
    """
    # Create temporary directory for Sphinx
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract title from AsciiDoc if not provided
        if not title:
            with open(asciidoc_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("= "):
                        title = line[2:].strip()
                        break
            if not title:
                title = "GEDCOM Document"

        # Create Sphinx configuration
        create_sphinx_config(temp_dir, title)

        # Convert AsciiDoc to RST
        rst_file = os.path.join(temp_dir, "index.rst")
        convert_asciidoc_to_rst(asciidoc_file, rst_file)

        # Copy any referenced image files to the Sphinx source directory
        asciidoc_dir = os.path.dirname(os.path.abspath(asciidoc_file))
        copy_referenced_images(asciidoc_file, asciidoc_dir, temp_dir)

        # Build PDF
        pdf_path = build_pdf(temp_dir, temp_dir)

        if pdf_path:
            # Copy PDF to output location
            if output_file:
                shutil.copy(pdf_path, output_file)
                return output_file
            else:
                # Copy to current directory with default name
                default_output = "family_tree.pdf"
                shutil.copy(pdf_path, default_output)
                return default_output

        return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert AsciiDoc to PDF using Sphinx (A4 paper format)"
    )
    parser.add_argument(
        "asciidoc_file",
        nargs="?",
        default="family_tree.adoc",
        help="Path to the AsciiDoc file (default: auto-detect .adoc file)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file path (default: matches input filename)",
        default="family_tree.pdf",
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Document title (default: extracted from file)",
        default=None,
    )

    args = parser.parse_args()

    # Validate input file exists, or find .adoc file if default is missing
    input_file = args.asciidoc_file
    if not os.path.exists(input_file):
        if input_file == "family_tree.adoc":
            # Look for any .adoc file in current directory
            adoc_files = [f for f in os.listdir(".") if f.endswith(".adoc")]
            if len(adoc_files) == 1:
                input_file = adoc_files[0]
                print(f"Using found AsciiDoc file: {input_file}")
            elif len(adoc_files) > 1:
                print(f"Multiple .adoc files found: {', '.join(adoc_files)}")
                print("Please specify which file to convert.", file=sys.stderr)
                sys.exit(1)
            else:
                print("Error: No .adoc files found", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: File '{input_file}' not found", file=sys.stderr)
            sys.exit(1)

    # Convert to PDF
    print(f"Converting {input_file} to PDF...")

    # Use matching output filename if using default
    output_file = args.output
    if args.output == "family_tree.pdf" and input_file != "family_tree.adoc":
        # Generate matching output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.pdf"

    result = convert_asciidoc_to_pdf(input_file, output_file, args.title)

    if result:
        print(f"PDF successfully generated: {result}")
    else:
        print("Error: Failed to generate PDF", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
