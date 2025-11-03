#!/usr/bin/env python3

import sys

sys.path.insert(0, "/workspace/gedcom_visualizer")

from convert_to_pdf import convert_asciidoc_to_rst

# Convert our genealogy file and print the RST
# Convert our genealogy file and print the RST
convert_asciidoc_to_rst(
    "/workspace/tage_georg_reinhold.adoc", "/workspace/debug_output_genealogy.rst"
)

print("=== Sample from Original AsciiDoc ===")
with open("/workspace/tage_georg_reinhold.adoc", "r") as f:
    lines = f.readlines()
    # Find lines with cross-references and show context
    for i, line in enumerate(lines):
        if "<<I500" in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            print(f"Lines {start+1}-{end}:")
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{lines[j].rstrip()}")
            print()
            break

print("\n=== Sample from Converted RST ===")
with open("/workspace/debug_output_genealogy.rst", "r") as f:
    lines = f.readlines()
    # Find lines with cross-references and show context
    for i, line in enumerate(lines):
        if ":ref:" in line:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            print(f"Lines {start+1}-{end}:")
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{lines[j].rstrip()}")
            print()
            break
