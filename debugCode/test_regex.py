#!/usr/bin/env python3

import re

# Test the regex conversion
test_line = "* *Father:* <<I500035,Johannes Carlsson>> (@I500035@)"
print(f"Original: {test_line}")

# Apply the regex from the conversion function
converted = re.sub(r"<<([^,>]+),([^>]+)>>", r":ref:`\2 <\1>`", test_line)
print(f"Converted: {converted}")

# Test multiple patterns
test_cases = [
    "<<I500035,Johannes Carlsson>>",
    "This refers to <<ch1,Chapter One>>.",
    "Multiple <<link1,First>> and <<link2,Second>> references",
]

for test in test_cases:
    print(f"\nOriginal: {test}")
    converted = re.sub(r"<<([^,>]+),([^>]+)>>", r":ref:`\2 <\1>`", test)
    print(f"Converted: {converted}")
