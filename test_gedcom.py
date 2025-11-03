#!/usr/bin/env python3
"""Quick test script to verify GEDCOM parsing functionality."""

import sys
from pathlib import Path
from gedcom_visualizer.gedcom_utils import load_gedcom_robust, validate_gedcom_format


def test_gedcom_parsing(gedcom_file):
    """Test GEDCOM file parsing with various methods."""
    print(f"Testing GEDCOM file: {gedcom_file}")
    print("=" * 60)
    
    # Check if file exists
    if not Path(gedcom_file).exists():
        print(f"Error: File '{gedcom_file}' not found")
        return False
    
    # First, validate the format
    print("1. Validating GEDCOM format...")
    validation = validate_gedcom_format(gedcom_file, max_lines_to_check=500)
    print(f"   Lines checked: {validation['lines_checked']}")
    print(f"   Issues found: {validation['issues_found']}")
    
    if validation['issues']:
        print("   Sample issues:")
        for issue in validation['issues'][:3]:  # Show first 3 issues
            print(f"     Line {issue['line']}: {issue['description']}")
            print(f"       Content: {issue['content']}")
    
    print()
    
    # Try to parse the file
    print("2. Attempting to parse GEDCOM file...")
    try:
        parser = load_gedcom_robust(gedcom_file, verbose=True)
        
        # Get some basic statistics
        individuals = parser.get_root_child_elements()
        from gedcom.element.individual import IndividualElement
        individual_count = len([elem for elem in individuals if isinstance(elem, IndividualElement)])
        
        print(f"✅ Successfully parsed GEDCOM file!")
        print(f"   Found {individual_count} individuals")
        
        # Show first few individuals as a test
        if individual_count > 0:
            print("\n   Sample individuals:")
            count = 0
            for elem in individuals:
                if isinstance(elem, IndividualElement) and count < 3:
                    name = elem.get_name()
                    pointer = elem.get_pointer()
                    display_name = f"{name[0] if name else 'Unknown'} {name[1] if len(name) > 1 else ''}".strip()
                    print(f"     {pointer}: {display_name}")
                    count += 1
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to parse GEDCOM file: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python test_gedcom.py <gedcom_file>")
        print("Example: python test_gedcom.py MyHeritage_export_2025-11-02.ged")
        sys.exit(1)
    
    gedcom_file = sys.argv[1]
    success = test_gedcom_parsing(gedcom_file)
    
    if success:
        print("\n🎉 GEDCOM parsing test completed successfully!")
        print("You can now use the other tools in this project:")
        print(f"  - List all: python -m gedcom_visualizer.list_search {gedcom_file}")
        print(f"  - Search: python -m gedcom_visualizer.list_search {gedcom_file} -s 'Johan'")
    else:
        print("\n⚠️  GEDCOM parsing test failed. Check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
