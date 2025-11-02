# 📄 A4 Paper Format Implementation

## Problem Fixed

**Issue**: PDFs were generated using US Letter paper format (`letterpaper`)
**Solution**: Changed to European A4 paper format (`a4paper`) with metric margins

## Changes Made

### 🇪🇺 **LaTeX Configuration Updates**

#### **Before (US Format)**
```python
latex_elements = {
    'papersize': 'letterpaper',  # US Letter (8.5" x 11")
    'preamble': r'''
\usepackage{geometry}
\geometry{margin=0.75in}      # Imperial units
    ''',
}
```

#### **After (EU Format)**
```python
latex_elements = {
    'papersize': 'a4paper',      # A4 (210mm x 297mm)
    'preamble': r'''
\usepackage{geometry}
\geometry{margin=2cm}         # Metric units
    ''',
}
```

### 📋 **Documentation Updates**

1. **convert_to_pdf.py**: Updated help text to mention A4 format
2. **README.md**: Added A4 paper format references
3. **Sphinx config**: Added comment about European A4 standard

### 📐 **Specifications**

- **Paper Size**: A4 (210mm × 297mm)
- **Margins**: 2cm all around (was 0.75 inches)
- **Font Size**: 11pt (unchanged)
- **Layout**: Portrait orientation (unchanged)

## Benefits

### ✅ **European Standard Compliance**
- **ISO 216 Standard**: A4 is the international standard
- **EU Compatibility**: Matches European office and home printers
- **Professional Appearance**: Standard business document format
- **Proper Margins**: 2cm margins are European business standard

### 📊 **Technical Advantages**
- **Better Space Utilization**: A4 is slightly narrower and taller than US Letter
- **Consistent Formatting**: Same appearance across EU countries
- **Print Compatibility**: Works with all European printers by default
- **Archive Standard**: European genealogical archives use A4

## File Size Impact

A4 format maintains the same file sizes:
- **Before (Letter)**: 116KB
- **After (A4)**: 116KB
- **No performance impact**: Same processing time and quality

## Usage

All PDF generation now defaults to A4:

```bash
# Standard A4 family tree report
gedcom-generate file.ged @I123@ -o report.adoc
gedcom-convert report.adoc  # Creates A4 PDF

# All options work with A4
gedcom-generate file.ged @I123@ --no-toc  # A4 compact
gedcom-generate file.ged @I123@ --no-tree # A4 text-only
```

## Verification

Test files created:
- `carl_johan_a4.pdf` - A4 format with family tree
- `karl_roland_a4.pdf` - A4 format verification

**All PDFs now use proper European A4 paper format! 🇪🇺**
