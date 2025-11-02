# Examples and Quick Start Guide

This directory contains example files and a quick start guide for using the GEDCOM Visualizer tools.

## Sample GEDCOM File

The `sample.ged` file contains a small family tree with the following individuals:

- **John Smith** (@I1@) - Born 1950, Died 2020
- **Mary Johnson** (@I2@) - Born 1952, Spouse of John
- **Robert Smith** (@I3@) - Born 1975, Child of John and Mary
- **Sarah Smith** (@I4@) - Born 1978, Child of John and Mary
- **James Smith** (@I5@) - Born 1920, Died 1995, Father of John
- **Elizabeth Brown** (@I6@) - Born 1925, Died 2010, Mother of John

## Quick Start

### 1. List All Individuals

```bash
python3 ../gedcom_visualizer/list_search.py sample.ged
```

This will display all individuals in the GEDCOM file with their basic information.

### 2. Search for a Specific Person

```bash
python3 ../gedcom_visualizer/list_search.py sample.ged --search "John"
```

This will find all individuals whose names contain "John".

### 3. Generate a Document for John Smith

```bash
python3 ../gedcom_visualizer/generate_asciidoc.py sample.ged @I1@ -o john_smith.adoc
```

This creates an AsciiDoc document with John Smith's information.

### 4. Convert to PDF

```bash
python3 ../gedcom_visualizer/convert_to_pdf.py john_smith.adoc -o john_smith.pdf
```

This converts the AsciiDoc document to a PDF file.

## Complete Workflow

Here's a complete example workflow:

```bash
# Navigate to the examples directory
cd examples

# Step 1: Find the person you're interested in
python3 ../gedcom_visualizer/list_search.py sample.ged --search "Sarah"

# Step 2: Generate AsciiDoc for Sarah Smith (@I4@)
python3 ../gedcom_visualizer/generate_asciidoc.py sample.ged @I4@ -o sarah_smith.adoc

# Step 3: Convert to PDF
python3 ../gedcom_visualizer/convert_to_pdf.py sarah_smith.adoc -o sarah_smith.pdf

# View the generated AsciiDoc
cat sarah_smith.adoc

# The PDF is now ready: sarah_smith.pdf
```

## Using Your Own GEDCOM Files

To use your own GEDCOM files, simply replace `sample.ged` with the path to your file:

```bash
python3 ../gedcom_visualizer/list_search.py /path/to/your/family.ged
```

## Tips

1. **Finding IDs**: Use the list or search command first to find the correct ID for the person you want to document.

2. **ID Format**: IDs can be specified with or without the `@` symbols. Both `@I1@` and `I1` will work.

3. **Output to Console**: Omit the `-o` flag to print the AsciiDoc content to the console instead of a file.

4. **Batch Processing**: You can create documents for multiple people by running the scripts in a loop:

```bash
for id in I1 I2 I3 I4; do
    python3 ../gedcom_visualizer/generate_asciidoc.py sample.ged @${id}@ -o person_${id}.adoc
    python3 ../gedcom_visualizer/convert_to_pdf.py person_${id}.adoc -o person_${id}.pdf
done
```

## Troubleshooting

### PDF Generation Fails

If PDF generation fails, ensure you have LaTeX installed:

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex
```

### Individual Not Found

Make sure you're using the correct ID format. Check the output of the list command to verify the ID exists in your GEDCOM file.

### Invalid GEDCOM File

Ensure your GEDCOM file follows the standard GEDCOM format. The python-gedcom library supports GEDCOM 5.5.1.
