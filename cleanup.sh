#!/bin/bash

# GEDCOM Visualizer Cleanup Script
# Removes temporary files generated during development and testing

set -e

echo "🧹 GEDCOM Visualizer Cleanup"
echo "=========================================="

# Define file patterns to clean up
PATTERNS=(
    "*.adoc"           # AsciiDoc source files
    "*.pdf"            # Generated PDF files
    "*.dot"            # Graphviz DOT files
    "*.png"            # Family tree PNG images
    "*_family_tree.*"  # Any family tree files
    "*.log"            # LaTeX log files
    "*.aux"            # LaTeX auxiliary files
    "*.toc"            # Table of contents files
    "*.out"            # LaTeX outline files
    "*.fdb_latexmk"    # LaTeX make database
    "*.fls"            # LaTeX file list
    "*.synctex.gz"     # SyncTeX files
)

# Count files before cleanup
total_files=0
for pattern in "${PATTERNS[@]}"; do
    if ls ${pattern} >/dev/null 2>&1; then
        count=$(ls -1 ${pattern} 2>/dev/null | wc -l)
        total_files=$((total_files + count))
    fi
done

if [[ $total_files -eq 0 ]]; then
    echo "✅ No temporary files found - workspace is already clean!"
    exit 0
fi

echo "📁 Found $total_files temporary files to clean up"
echo ""

# Show what will be removed (if files exist)
echo "🔍 Files to be removed:"
for pattern in "${PATTERNS[@]}"; do
    if ls ${pattern} >/dev/null 2>&1; then
        echo "   $pattern:"
        ls -1 ${pattern} 2>/dev/null | sed 's/^/      /'
    fi
done

echo ""

# Ask for confirmation unless --force flag is used
if [[ "$1" != "--force" && "$1" != "-f" ]]; then
    read -p "❓ Remove these files? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled"
        exit 0
    fi
fi

# Remove files
echo "🗑️  Removing temporary files..."
removed_count=0

for pattern in "${PATTERNS[@]}"; do
    if ls ${pattern} >/dev/null 2>&1; then
        count=$(ls -1 ${pattern} 2>/dev/null | wc -l)
        rm -f ${pattern}
        removed_count=$((removed_count + count))
        echo "   ✅ Removed $count ${pattern} files"
    fi
done

echo ""
echo "🎉 Cleanup complete!"
echo "   📊 Removed $removed_count temporary files"
echo "   ✨ Workspace is now clean"
