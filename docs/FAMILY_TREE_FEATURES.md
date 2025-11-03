# 🌳 Family Tree Visualization Features

## Overview

The GEDCOM Visualizer now includes **visual family tree diagrams** that make genealogy documents much more readable and engaging. The family trees are automatically generated using Graphviz and integrated into your PDF reports.

## Features Added

### ✨ Visual Family Tree Diagrams
- **Main person in center** (highlighted in green)
- **Parents above** (yellow background) with parent relationships
- **Spouse to the side** (pink background) with marriage connection
- **Children below** (cyan background) with parent-child relationships
- **Birth years displayed** for each person when available
- **Professional styling** with rounded boxes and color coding

### 🎨 Visual Design
- **Color-coded relationships**:
  - 🟢 Main person: Light green with bold border
  - 🟡 Parents: Light yellow
  - 🩷 Spouse: Light pink
  - 🔵 Children: Light cyan
- **Clean typography** with Arial font
- **Relationship labels** on connecting lines
- **Orthogonal layout** with proper spacing

### ⚙️ Command-Line Options
- **Default mode**: Includes family tree diagram
- **Text-only mode**: Use `--no-tree` flag to disable diagrams

## Usage Examples

### Generate with Family Tree (Default)
```bash
gedcom-generate MyHeritage_export_2025-11-02.ged @I500001@ -o report.adoc
gedcom-convert report.adoc  # Creates report.pdf with family tree
```

### Generate Text-Only Report
```bash
gedcom-generate MyHeritage_export_2025-11-02.ged @I500001@ -o report.adoc --no-tree
```

### Complete Workflow
```bash
# 1. Find the person you want
gedcom-list MyHeritage_export_2025-11-02.ged | grep "Carl Johan"

# 2. Generate report with family tree
gedcom-generate MyHeritage_export_2025-11-02.ged @I500001@ -o carl_johan.adoc

# 3. Convert to PDF
gedcom-convert carl_johan.adoc
```

## Files Generated

When you generate a family tree report, you'll get:
- `person_name.adoc` - AsciiDoc source file
- `person_name_family_tree.dot` - Graphviz source file
- `person_name_family_tree.png` - Family tree diagram
- `person_name.pdf` - Final PDF report (after conversion)

## Technical Details

### Dependencies
- **Graphviz**: Automatically installed in the development environment
- **Python libraries**: All handled by the existing setup

### File Structure
The family tree diagrams are generated as PNG images and embedded in the AsciiDoc documents using the `image::` directive. This ensures they render properly in both HTML and PDF outputs.

### Compatibility
- Works with **MyHeritage GEDCOM exports**
- Handles **format violations** robustly
- **Fallback modes** for problematic files
- **Unicode support** for international names

## Examples Output

### Before (Text-Only)
```
== Parents
* Father: Karl Roland Simonsson (@I500003@)
** Born: 26 FEB 1948
* Mother: Ingrid Monica Carlsson (@I500002@)
** Born: 8 MAY 1952
```

### After (With Family Tree)
```
== Family Tree Diagram
[Visual diagram showing Karl Roland and Ingrid Monica above Carl Johan,
 Cecilia Katharina to the side, and Carl John + Ellen Inga below]

== Parents
[Same text content as before, but now supplemented by visual diagram]
```

## Benefits

1. **📊 Visual Understanding**: Family relationships are immediately clear
2. **🎯 Focus Point**: Main person is visually emphasized
3. **📱 Multi-generational**: Shows 3 generations in one view
4. **🏃‍♂️ Quick Navigation**: Easy to spot family connections
5. **📄 Professional Output**: Publication-ready genealogy reports
6. **🔧 Flexible**: Can be disabled for text-only preferences

## Future Enhancements

Potential improvements for future versions:
- Extended family trees (grandparents, siblings)
- Interactive SVG diagrams
- Multiple layout options (horizontal, radial)
- Photo integration
- Custom color themes
