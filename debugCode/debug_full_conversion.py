#!/usr/bin/env python3

import sys
import re

sys.path.insert(0, "/workspace/gedcom_visualizer")

from convert_to_pdf import convert_asciidoc_to_rst

# Create a temporary file with just the problematic lines
test_content = """= Test Document

== Section with Cross-References [[sec1]]

* *Father:* <<I500035,Johannes Carlsson>> (@I500035@)
* *Mother:* <<I500036,Maria Carlsson (born Hansdotter)>> (@I500036@)

Some normal text here.

=== Another section

* *<<I500035,Johannes Carlsson>> (@I500035@)*
"""

with open("/workspace/test_conversion_debug.adoc", "w") as f:
    f.write(test_content)

# Convert it
print("Converting test file...")
convert_asciidoc_to_rst(
    "/workspace/test_conversion_debug.adoc", "/workspace/test_conversion_debug.rst"
)

print("\n=== Original AsciiDoc ===")
print(test_content)

print("\n=== Converted RST ===")
with open("/workspace/test_conversion_debug.rst", "r") as f:
    converted = f.read()
    print(converted)

# Check if cross-references were converted
if ":ref:" in converted:
    print("\n✓ Cross-references were converted!")
else:
    print("\n✗ Cross-references were NOT converted!")

if "<<" in converted:
    print("✗ Raw AsciiDoc cross-references still present!")
