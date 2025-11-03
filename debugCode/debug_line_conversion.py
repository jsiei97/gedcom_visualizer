#!/usr/bin/env python3

import sys

sys.path.insert(0, "/workspace/gedcom_visualizer")

import re


# Simulate the conversion function with debug output
def debug_convert_line(line):
    """Debug version of line conversion."""
    converted = line
    original = line

    # Convert AsciiDoc bold syntax *word* to RST **word**
    if "*" in converted:
        converted = re.sub(r"\*([^\*]+?)\*", r"**\1**", converted)

    # Convert AsciiDoc cross-references <<anchor,text>> to RST :ref:`text <anchor>`
    if "<<" in converted:
        print(f"  Found cross-reference in: {converted.strip()}")
        converted = re.sub(r"<<([^,>]+),([^>]+)>>", r":ref:`\2 <\1>`", converted)
        print(f"  Converted to: {converted.strip()}")

    return converted


# Test with some lines from the genealogy file
test_lines = [
    "* *Father:* <<I500035,Johannes Carlsson>> (@I500035@)",
    "** Born: 22 DEC 1862",
    "* *Mother:* <<I500036,Maria Carlsson (born Hansdotter)>> (@I500036@)",
    "Some normal text without cross-references",
    "* *<<I500035,Johannes Carlsson>> (@I500035@)*",
]

print("Testing line conversion with debug output:")
for i, line in enumerate(test_lines, 1):
    print(f"\nLine {i}: {line}")
    result = debug_convert_line(line)
    if result != line:
        print(f"  Changed to: {result}")
