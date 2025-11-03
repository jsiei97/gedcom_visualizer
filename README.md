# GEDCOM Visualizer

**A comprehensive Python toolkit for creating beautiful, professional genealogy documents from GEDCOM files.**

GEDCOM Visualizer transforms raw genealogical data into polished, readable documents with visual family trees, cross-referenced relationships, and detailed biographical information. Perfect for family historians, genealogists, and researchers who want to create professional-quality family documentation.

> **Note**: This project serves as an evaluation of AI-assisted development using GitHub Copilot, demonstrating how modern coding assistants can enhance productivity in genealogical software development. Please use with care.

> **✨ Fully functional and production-ready** - Successfully processes MyHeritage exports and standard GEDCOM files with comprehensive error handling and robust parsing.

## What This Project Does

🔍 **Parse GEDCOM Files**: Robust parsing of GEDCOM genealogy files with support for various formats including MyHeritage exports

📊 **Generate Visual Family Trees**: Create horizontal family tree diagrams showing relationships between parents, spouses, and children

📖 **Create Comprehensive Documents**: Generate detailed individual profiles with:
- Personal information and life events
- Family relationships with cross-reference navigation
- Birth and death dates in ISO format (YYYY-MM-DD)
- Residence history, sources, and metadata
- Smart name handling (married names, maiden names)

🎨 **Professional PDF Output**: Convert documents to A4 PDFs with:
- Clickable cross-references between family members
- Embedded family tree diagrams
- Clean, European-standard formatting
- Unicode support for international names

## Key Features

- **Smart Name Display**: Shows married names prominently with maiden names indicated (e.g., "Anna Valfrida Carlsson (born Nilsson)")
- **Cross-Reference Navigation**: Click between family members in PDF documents
- **Flexible Date Formatting**: Converts various date formats to ISO standard (YYYY-MM-DD)
- **Visual Family Trees**: Graphviz-generated diagrams with proper relationship positioning
- **Comprehensive Biographical Data**: Life events, residences, sources, and record information
- **Customizable Output**: Command-line options to include/exclude sections as needed

## Core Tools

1. **`gedcom-list`** - Browse and search individuals in GEDCOM files
2. **`gedcom-generate`** - Create comprehensive AsciiDoc documents for individuals
3. **`gedcom-convert`** - Transform AsciiDoc documents into professional A4 PDFs

## Quick Example

```bash
# Find people in your GEDCOM file
gedcom-list family.ged --search "Smith"

# Generate a complete family document
gedcom-generate family.ged @I500033@ --generations 2

# Convert to professional PDF
gedcom-convert albin_johansson_karlsson.adoc
```

**Output includes:**
- Personal information with dates in ISO format (1890-03-29)
- Visual family tree diagrams showing relationships
- Cross-referenced family relationships (clickable in PDF)
- Comprehensive biographical information
- Professional A4 formatting suitable for printing

## Development Environment

### 🚀 Primary Environment: VS Code Development Container (Recommended)

**This project is designed to work seamlessly with VS Code and devcontainers.** This is the primary and recommended development environment.

#### Why VS Code + Devcontainer?

- **Zero Setup**: All dependencies (Python, LaTeX, Graphviz) are automatically configured
- **Consistent Environment**: Same setup works across Windows, macOS, and Linux
- **Integrated Development**: Built-in debugging, testing, and task automation
- **Immediate Productivity**: Start coding within minutes of cloning the repository

#### Quick Start

1. **Prerequisites**:
   - [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - Docker Desktop or Podman installed

2. **One-Click Setup**:
   ```bash
   git clone https://github.com/jsiei97/gedcom_visualizer.git
   cd gedcom_visualizer
   code .
   ```
   - Click "Reopen in Container" when prompted, or
   - Press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

3. **Start Using**:
   ```bash
   # Inside VS Code's integrated terminal
   gedcom-list examples/sample.ged
   gedcom-generate examples/sample.ged @I1@ -o sample.adoc
   gedcom-convert sample.adoc -o sample.pdf
   ```

#### What You Get

- **Full Python environment** with all genealogy libraries
- **LaTeX/TeXLive** for professional PDF generation
- **Graphviz** for family tree visualization
- **Pre-configured debugging** and code formatting
- **Integrated testing** with automated workflows

See [`.devcontainer/README.md`](.devcontainer/README.md) for advanced configuration options.

### Alternative: Traditional Container Setup (Ubuntu/Linux)

**Alternative approach** for users who prefer traditional containerization on Ubuntu 24.04 using Podman and DistroBox. The container includes all necessary dependencies (Python, LaTeX, Graphviz, and required libraries).

#### Prerequisites

- Ubuntu 24.04 LTS
- Podman installed: `sudo apt-get install podman`
- DistroBox installed: Follow instructions at https://github.com/89luca89/distrobox

#### Step 1: Build the Container

Build the container image using the provided script:

```bash
./build-container.sh
```

This script uses Podman to build a container image named `gedcom-visualizer:latest` with all dependencies pre-installed.

#### Step 2: Create and Start the DistroBox Container

Use the provided script to create a DistroBox container:

```bash
./run-distrobox.sh
```

This script will:
- Check if the container image exists (and build it if necessary)
- Create a DistroBox container named `gedcom-viz`
- Set up the environment for running the tools

To enter the container after creation:

```bash
distrobox enter gedcom-viz
```

#### Mounting GEDCOM Files

Your home directory is automatically mounted inside the DistroBox container,
so you can access your GEDCOM files directly.
Place your GEDCOM files anywhere in your home directory and access them
from within the container using the same paths.

For example, if your GEDCOM file is at `~/Documents/family.ged` on your host system,
you can access it at `~/Documents/family.ged` inside the container.

## Usage

### Using VS Code Devcontainer (Recommended)

Open the project in VS Code with the devcontainer, then use the integrated terminal:

```bash
# All commands work directly in VS Code's terminal
gedcom-list ~/Documents/family.ged
gedcom-generate ~/Documents/family.ged @I1@ -o output.adoc
gedcom-convert output.adoc -o output.pdf
```

### Using Traditional Container

If using the alternative DistroBox setup, enter the container first:

```bash
distrobox enter gedcom-viz
# Then run the commands as shown above
```

## Command Reference

The package provides three convenient command-line tools:

### Script 1: List and Search GEDCOM File

List all individuals in a GEDCOM file:

```bash
gedcom-list ~/Documents/family.ged
```

Search for individuals by name:

```bash
gedcom-list ~/Documents/family.ged --search "Smith"
```

This script helps you find the ID of an individual to use with other scripts.

### Script 2: Generate AsciiDoc Document

Generate a human-readable AsciiDoc document for a specific individual:

```bash
gedcom-generate ~/Documents/family.ged @I1@ -o output.adoc
```

The document includes:
- Personal information with personalized chapter titles using married names when available (e.g., "Simonsson Personal Information")
- Smart name handling: shows married names as primary with maiden names indicated (e.g., "Ingrid Monica Simonsson (née Carlsson)")
- Comprehensive biographical data (birth, death, residence history, life events)
- Family tree diagram with proper spouse positioning
- Parents, spouse(s), and children relationships
- Source references and data quality information
- Contact information and record metadata

### Script 3: Convert to PDF

Convert an AsciiDoc document to PDF format:

```bash
gedcom-convert output.adoc -o output.pdf
```

### Complete Workflow Example

Here's a complete example workflow inside the container:

```bash
# Enter the container
distrobox enter gedcom-viz

# 1. List all individuals to find the ID
gedcom-list ~/Documents/family.ged

# 2. Search for a specific person
gedcom-list ~/Documents/family.ged --search "John"

# 3. Generate AsciiDoc for John Smith (@I1@)
gedcom-generate ~/Documents/family.ged @I1@ -o ~/Documents/john_smith.adoc

# 4. Convert to PDF
gedcom-convert ~/Documents/john_smith.adoc -o ~/Documents/john_smith.pdf

# The PDF is now available at ~/Documents/john_smith.pdf
# You can access it from your host system at the same path
```

### Using the Sample GEDCOM File

A sample GEDCOM file is provided in the `examples/` directory for testing.
The project files are available at `/workspace/` inside the container:

```bash
# Inside the container
gedcom-list /workspace/examples/sample.ged
gedcom-generate /workspace/examples/sample.ged @I1@ -o /tmp/sample.adoc
gedcom-convert /tmp/sample.adoc -o /tmp/sample.pdf
```

## Project Structure

```
gedcom_visualizer/
├── .devcontainer/              # 🚀 VS Code devcontainer configuration
│   ├── devcontainer.json      # Container settings and features
│   └── README.md              # Devcontainer documentation
├── gedcom_visualizer/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── list_search.py         # Script 1: List and search
│   ├── generate_asciidoc.py   # Script 2: Generate AsciiDoc
│   └── convert_to_pdf.py      # Script 3: Convert to PDF
├── examples/                   # Example files
│   └── sample.ged             # Sample GEDCOM file
├── .vscode/                    # VS Code workspace configuration
├── Dockerfile                 # Container definition (alternative setup)
├── build-container.sh         # Script to build container (alternative)
├── run-distrobox.sh          # Script to set up DistroBox (alternative)
├── cleanup.sh                # Script to clean temporary files
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
└── README.md                  # This file
```

## Cleanup

Use the cleanup script to remove temporary files generated during development:

```bash
# Interactive cleanup (asks for confirmation)
./cleanup.sh

# Force cleanup (removes files without asking)
./cleanup.sh --force

# Or use the short form
./cleanup.sh -f
```

The cleanup script removes:
- `*.adoc` - AsciiDoc source files
- `*.pdf` - Generated PDF files
- `*.dot` - Graphviz DOT files
- `*.png` - Family tree images
- LaTeX temporary files (`*.aux`, `*.log`, etc.)

## Command Line Options

### gedcom-list

```
usage: gedcom-list [-h] [-s TERM] gedcom_file

positional arguments:
  gedcom_file           Path to the GEDCOM file

optional arguments:
  -h, --help            Show help message
  -s TERM, --search TERM
                        Search for individuals by name
```

### gedcom-generate

```
usage: gedcom-generate [-h] [-o FILE] gedcom_file individual_id

positional arguments:
  gedcom_file           Path to the GEDCOM file
  individual_id         ID of the individual (e.g., @I1@ or I1)

optional arguments:
  -h, --help            Show help message
  -o FILE, --output FILE
                        Output file path (default: stdout)
```

### gedcom-convert

```
usage: gedcom-convert [-h] [-o OUTPUT] [-t TITLE] asciidoc_file

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

### System Dependencies
- **Graphviz** - Graph visualization software (for family tree diagrams)
- **LaTeX/TeXLive** - Document preparation system (for PDF generation)

### Python Dependencies
- **python-gedcom** - GEDCOM file parsing library
- **sphinx** - Documentation generator (used for PDF conversion)
- **sphinx-rtd-theme** - Read the Docs theme for Sphinx

All dependencies are automatically installed in the development container environment.

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
