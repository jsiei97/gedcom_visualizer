# GEDCOM Visualizer

A collection of Python scripts for parsing and visualizing GEDCOM genealogy files. This project provides tools to extract, format, and present genealogical data in human-readable formats.

## Features

The project consists of three main scripts:

1. **List and Search** (`list_search.py`) - Browse and search individuals in a GEDCOM file
2. **Generate AsciiDoc** (`generate_asciidoc.py`) - Create formatted documents for individuals
3. **Convert to PDF** (`convert_to_pdf.py`) - Transform AsciiDoc documents into PDF format

## Development Environment Options

### Option 1: VS Code Development Container (Recommended)

The easiest way to get started is using the VS Code Development Container:

1. **Prerequisites**:
   - VS Code with the Dev Containers extension
   - Docker or Podman installed

2. **Setup**:
   - Open the project in VS Code
   - Click "Reopen in Container" when prompted, or
   - Press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

3. **Benefits**:
   - Automatic setup of all dependencies
   - Pre-configured debugging and tasks
   - Consistent environment across all developers
   - No need to manually install Python packages

See [`.devcontainer/README.md`](.devcontainer/README.md) for detailed instructions.

### Option 2: Traditional Container Setup (Ubuntu 24.04)

This tool is designed to run inside a container on Ubuntu 24.04 using Podman and DistroBox. The container includes all necessary dependencies (Python, LaTeX, and required libraries).

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

Your home directory is automatically mounted inside the DistroBox container, so you can access your GEDCOM files directly. Place your GEDCOM files anywhere in your home directory and access them from within the container using the same paths.

For example, if your GEDCOM file is at `~/Documents/family.ged` on your host system, you can access it at `~/Documents/family.ged` inside the container.

## Usage Inside the Container

**Important:** All Python scripts should be executed inside the container environment. After entering the container with `distrobox enter gedcom-viz`, you can use the following commands.

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
- Personal information (name, birth, death)
- Parents
- Spouse(s)
- Children

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

A sample GEDCOM file is provided in the `examples/` directory for testing. The project files are available at `/workspace/` inside the container:

```bash
# Inside the container
gedcom-list /workspace/examples/sample.ged
gedcom-generate /workspace/examples/sample.ged @I1@ -o /tmp/sample.adoc
gedcom-convert /tmp/sample.adoc -o /tmp/sample.pdf
```

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
├── Dockerfile                 # Container definition
├── build-container.sh         # Script to build the container
├── run-distrobox.sh          # Script to set up DistroBox
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
└── README.md                  # This file
```

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

- **python-gedcom** - GEDCOM file parsing library
- **sphinx** - Documentation generator (used for PDF conversion)
- **sphinx-rtd-theme** - Read the Docs theme for Sphinx

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
