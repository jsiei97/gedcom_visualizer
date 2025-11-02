# GEDCOM Visualizer

A collection of Python scripts for parsing and visualizing GEDCOM genealogy files. This project provides tools to extract, format, and present genealogical data in human-readable formats.

## Features

The project consists of three main scripts:

1. **List and Search** (`list_search.py`) - Browse and search individuals in a GEDCOM file
2. **Generate AsciiDoc** (`generate_asciidoc.py`) - Create formatted documents for individuals
3. **Convert to PDF** (`convert_to_pdf.py`) - Transform AsciiDoc documents into PDF format

## Installation

### Prerequisites

- Python 3.8 or higher
- LaTeX distribution (for PDF generation)

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Install LaTeX (for PDF generation)

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Download and install MiKTeX from https://miktex.org/

## Usage

### Script 1: List and Search GEDCOM File

List all individuals in a GEDCOM file:

```bash
python3 gedcom_visualizer/list_search.py examples/sample.ged
```

Search for individuals by name:

```bash
python3 gedcom_visualizer/list_search.py examples/sample.ged --search "Smith"
```

This script helps you find the ID of an individual to use with other scripts.

### Script 2: Generate AsciiDoc Document

Generate a human-readable AsciiDoc document for a specific individual:

```bash
python3 gedcom_visualizer/generate_asciidoc.py examples/sample.ged @I1@ -o output.adoc
```

The document includes:
- Personal information (name, birth, death)
- Parents
- Spouse(s)
- Children

### Script 3: Convert to PDF

Convert an AsciiDoc document to PDF format:

```bash
python3 gedcom_visualizer/convert_to_pdf.py output.adoc -o output.pdf
```

### Complete Workflow Example

```bash
# 1. List all individuals to find the ID
python3 gedcom_visualizer/list_search.py examples/sample.ged

# 2. Generate AsciiDoc for John Smith (@I1@)
python3 gedcom_visualizer/generate_asciidoc.py examples/sample.ged @I1@ -o john_smith.adoc

# 3. Convert to PDF
python3 gedcom_visualizer/convert_to_pdf.py john_smith.adoc -o john_smith.pdf
```

## Sample GEDCOM File

A sample GEDCOM file is provided in the `examples/` directory for testing and demonstration purposes.

## Project Structure

```
gedcom_visualizer/
├── gedcom_visualizer/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── list_search.py         # Script 1: List and search
│   ├── generate_asciidoc.py   # Script 2: Generate AsciiDoc
│   └── convert_to_pdf.py      # Script 3: Convert to PDF
├── examples/                   # Example files
│   └── sample.ged             # Sample GEDCOM file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Command Line Options

### list_search.py

```
usage: list_search.py [-h] [-s TERM] gedcom_file

positional arguments:
  gedcom_file           Path to the GEDCOM file

optional arguments:
  -h, --help            Show help message
  -s TERM, --search TERM
                        Search for individuals by name
```

### generate_asciidoc.py

```
usage: generate_asciidoc.py [-h] [-o FILE] gedcom_file individual_id

positional arguments:
  gedcom_file           Path to the GEDCOM file
  individual_id         ID of the individual (e.g., @I1@ or I1)

optional arguments:
  -h, --help            Show help message
  -o FILE, --output FILE
                        Output file path (default: stdout)
```

### convert_to_pdf.py

```
usage: convert_to_pdf.py [-h] [-o OUTPUT] [-t TITLE] asciidoc_file

positional arguments:
  asciidoc_file         Path to the AsciiDoc file

optional arguments:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output PDF file path (default: output.pdf)
  -t TITLE, --title TITLE
                        Document title (default: extracted from file)
```

## Dependencies

- **python-gedcom** - GEDCOM file parsing library
- **sphinx** - Documentation generator (used for PDF conversion)
- **sphinx-rtd-theme** - Read the Docs theme for Sphinx

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
