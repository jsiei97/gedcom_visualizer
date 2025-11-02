#!/usr/bin/env python3
"""Script 3: Convert AsciiDoc to PDF using Sphinx.

This script sets up a Sphinx project and converts an AsciiDoc document to PDF format.
"""

import sys
import argparse
import os
import shutil
import subprocess
from pathlib import Path
import tempfile


def create_sphinx_config(source_dir, title="GEDCOM Document"):
    """Create Sphinx configuration file.
    
    Args:
        source_dir: Directory where Sphinx configuration will be created
        title: Title for the document
    """
    conf_content = f"""# Configuration file for Sphinx documentation builder

import os
import sys

# Project information
project = '{title}'
copyright = '2025, GEDCOM Visualizer'
author = 'GEDCOM Visualizer'
release = '1.0'

# General configuration
extensions = []

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

# LaTeX output options for PDF
latex_engine = 'pdflatex'
latex_elements = {{
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}}

# LaTeX documents
latex_documents = [
    (master_doc, 'document.tex', project, author, 'manual'),
]
"""
    
    conf_path = os.path.join(source_dir, 'conf.py')
    with open(conf_path, 'w') as f:
        f.write(conf_content)


def convert_asciidoc_to_rst(asciidoc_file, rst_file):
    """Convert AsciiDoc to ReStructuredText format.
    
    Args:
        asciidoc_file: Path to input AsciiDoc file
        rst_file: Path to output RST file
    """
    # Read AsciiDoc content
    with open(asciidoc_file, 'r') as f:
        lines = f.readlines()
    
    rst_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Skip AsciiDoc attributes
        if line.startswith(':') and line.endswith(':') and i < 5:
            i += 1
            continue
        
        # Convert title (= Title)
        if line.startswith('= '):
            title = line[2:].strip()
            rst_lines.append(title)
            rst_lines.append('=' * len(title))
            rst_lines.append('')
        
        # Convert section headers (== Section)
        elif line.startswith('== '):
            section = line[3:].strip()
            rst_lines.append(section)
            rst_lines.append('-' * len(section))
            rst_lines.append('')
        
        # Convert subsection headers (=== Subsection)
        elif line.startswith('=== '):
            subsection = line[4:].strip()
            rst_lines.append(subsection)
            rst_lines.append('~' * len(subsection))
            rst_lines.append('')
        
        # Convert bold text (*text*)
        elif '*' in line and not line.startswith('*'):
            # Simple conversion of *text* to **text**
            converted = line.replace('*', '**')
            rst_lines.append(converted)
        
        # Convert list items (*)
        elif line.startswith('* '):
            rst_lines.append(line.replace('* ', '- ', 1))
        
        # Convert nested list items (**)
        elif line.startswith('** '):
            rst_lines.append(line.replace('** ', '  - ', 1))
        
        # Keep other lines as is
        else:
            rst_lines.append(line)
        
        i += 1
    
    # Write RST content
    with open(rst_file, 'w') as f:
        f.write('\n'.join(rst_lines))


def build_pdf(sphinx_source_dir, output_dir):
    """Build PDF using Sphinx.
    
    Args:
        sphinx_source_dir: Directory containing Sphinx source files
        output_dir: Directory where PDF will be generated
        
    Returns:
        Path to generated PDF file or None if build failed
    """
    build_dir = os.path.join(output_dir, '_build')
    
    # Run sphinx-build to generate LaTeX
    latex_dir = os.path.join(build_dir, 'latex')
    cmd = [
        'sphinx-build',
        '-b', 'latex',
        '-q',  # Quiet mode
        sphinx_source_dir,
        latex_dir
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error building LaTeX: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
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
                ['pdflatex', '-interaction=nonstopmode', 'document.tex'],
                capture_output=True,
                text=True
            )
        
        os.chdir(original_dir)
        
        pdf_path = os.path.join(latex_dir, 'document.pdf')
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            print("Error: PDF file was not generated", file=sys.stderr)
            return None
            
    except FileNotFoundError:
        print("Error: pdflatex not found. Please install texlive or a similar LaTeX distribution.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running pdflatex: {e}", file=sys.stderr)
        return None


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
            with open(asciidoc_file, 'r') as f:
                for line in f:
                    if line.startswith('= '):
                        title = line[2:].strip()
                        break
            if not title:
                title = "GEDCOM Document"
        
        # Create Sphinx configuration
        create_sphinx_config(temp_dir, title)
        
        # Convert AsciiDoc to RST
        rst_file = os.path.join(temp_dir, 'index.rst')
        convert_asciidoc_to_rst(asciidoc_file, rst_file)
        
        # Build PDF
        pdf_path = build_pdf(temp_dir, temp_dir)
        
        if pdf_path:
            # Copy PDF to output location
            if output_file:
                shutil.copy(pdf_path, output_file)
                return output_file
            else:
                # Copy to current directory with default name
                default_output = 'output.pdf'
                shutil.copy(pdf_path, default_output)
                return default_output
        
        return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert AsciiDoc to PDF using Sphinx'
    )
    parser.add_argument(
        'asciidoc_file',
        help='Path to the AsciiDoc file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (default: output.pdf)',
        default='output.pdf'
    )
    parser.add_argument(
        '-t', '--title',
        help='Document title (default: extracted from file)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.asciidoc_file):
        print(f"Error: File '{args.asciidoc_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Convert to PDF
    print(f"Converting {args.asciidoc_file} to PDF...")
    result = convert_asciidoc_to_pdf(args.asciidoc_file, args.output, args.title)
    
    if result:
        print(f"PDF successfully generated: {result}")
    else:
        print("Error: Failed to generate PDF", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
