#!/usr/bin/env python3
"""Utilities for handling GEDCOM files with format issues.

This module provides functions to preprocess and load GEDCOM files that may have
formatting violations, particularly those exported from MyHeritage and other
genealogy software that don't strictly follow GEDCOM 5.5 format.
"""

import re
import tempfile
from pathlib import Path
from gedcom.parser import Parser


def preprocess_gedcom_file(file_path):
    """Preprocess a GEDCOM file to fix common formatting issues.
    
    This function fixes:
    - Lines that don't start with level numbers
    - Improper line breaks in continuation text
    - Missing CONC/CONT for multi-line content
    - Invalid characters and encoding issues
    - Level violations (lines that jump too many levels)
    
    Args:
        file_path: Path to the original GEDCOM file
        
    Returns:
        Path to the preprocessed temporary file
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    processed_lines = []
    current_level = 0
    last_valid_level = 0
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip('\n\r')
        original_line = line
        
        # Skip empty lines
        if not line.strip():
            processed_lines.append(line)
            i += 1
            continue
        
        # Check if line starts with a level number (0-9 followed by space)
        level_match = re.match(r'^(\d+)\s', line)
        
        if level_match:
            level = int(level_match.group(1))
            
            # Check for level violations (jumping more than 1 level up)
            if level > last_valid_level + 1:
                # This violates GEDCOM format - adjust the level
                corrected_level = last_valid_level + 1
                line = re.sub(r'^\d+', str(corrected_level), line)
                level = corrected_level
            
            # Update tracking variables
            current_level = level
            last_valid_level = level
            
            # Check for problematic content that spans multiple lines
            # Look ahead to see if next lines should be CONC
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                
                # If next line doesn't start with level and isn't empty, 
                # it's likely continuation content
                if next_line and not re.match(r'^\d+\s', next_line):
                    # Collect all continuation lines
                    continuation_lines = []
                    j = i + 1
                    while j < len(lines):
                        cont_line = lines[j].strip()
                        if not cont_line:
                            j += 1
                            continue
                        if re.match(r'^\d+\s', cont_line):
                            break
                        continuation_lines.append(cont_line)
                        j += 1
                    
                    # Add the main line
                    processed_lines.append(line)
                    
                    # Add continuation lines as CONC
                    for cont_line in continuation_lines:
                        # Clean up the continuation line content
                        cleaned_content = cont_line.strip()
                        if cleaned_content:
                            processed_lines.append(f"{level + 1} CONC {cleaned_content}")
                    
                    # Skip the continuation lines we just processed
                    i = j
                    continue
            
            # Regular line processing
            processed_lines.append(line)
            
        else:
            # This line doesn't start with a level number - it's likely a continuation
            # that got improperly split. Make it a proper CONC line
            
            if processed_lines and line.strip():
                # Use the last known level + 1 for CONC lines
                conc_level = last_valid_level + 1
                cleaned_content = line.strip()
                
                # Check if this looks like it should be part of the previous CONC
                prev_line = processed_lines[-1] if processed_lines else ""
                if "CONC" in prev_line and not cleaned_content.startswith(('http', 'https', '<')):
                    # Merge with previous CONC line
                    processed_lines[-1] = prev_line + " " + cleaned_content
                else:
                    # Add as new CONC line
                    processed_lines.append(f"{conc_level} CONC {cleaned_content}")
            elif line.strip():
                # No previous line context, make it a level 1 CONC
                processed_lines.append(f"1 CONC {line.strip()}")
        
        i += 1
    
    # Write to a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8')
    for line in processed_lines:
        temp_file.write(line + '\n')
    temp_file.close()
    
    return temp_file.name


def parse_gedcom_lenient(file_path):
    """Parse a GEDCOM file with lenient error handling.
    
    This method manually parses the GEDCOM structure and is more tolerant
    of format violations than the standard parser.
    
    Args:
        file_path: Path to the GEDCOM file
        
    Returns:
        Parser object with parsed GEDCOM data
    """
    from gedcom.element.element import Element
    from gedcom.element.individual import IndividualElement
    from gedcom.element.family import FamilyElement
    
    # Create a new parser and manually build the structure
    parser = Parser()
    
    # Read file and build elements manually
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    elements = {}
    current_stack = []
    root_element = Element(0, "", "HEAD", "", "")
    elements["HEAD"] = root_element
    parser._Parser__root_element = root_element
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Try to parse the line
        try:
            # Match GEDCOM line format: LEVEL TAG [VALUE] or LEVEL POINTER TAG [VALUE]
            match = re.match(r'^(\d+)\s+(@[^@]*@\s+)?(\w+)(\s+(.*))?$', line)
            if not match:
                continue  # Skip malformed lines
                
            level = int(match.group(1))
            pointer = match.group(2).strip() if match.group(2) else ""
            tag = match.group(3)
            value = match.group(5) if match.group(5) else ""
            
            # Create element based on tag type
            if tag == "INDI":
                element = IndividualElement(level, pointer, tag, value, "")
            elif tag == "FAM":
                element = FamilyElement(level, pointer, tag, value, "")
            else:
                element = Element(level, pointer, tag, value, "")
            
            # Add to parser structure
            if pointer:
                elements[pointer] = element
                
            # Handle hierarchy - find parent
            while current_stack and current_stack[-1].get_level() >= level:
                current_stack.pop()
                
            if current_stack:
                parent = current_stack[-1]
                parent.add_child_element(element)
                element.set_parent_element(parent)
            else:
                root_element.add_child_element(element)
                element.set_parent_element(root_element)
                
            current_stack.append(element)
            
        except Exception as e:
            # Skip problematic lines but continue parsing
            continue
    
    return parser


def load_gedcom_robust(file_path, verbose=False):
    """Load and parse a GEDCOM file with robust error handling.
    
    This function tries multiple parsing strategies in order of preference:
    1. Preprocess and parse with standard parser
    2. Parse original file with standard parser  
    3. Use lenient manual parser
    
    Args:
        file_path: Path to the GEDCOM file
        verbose: Whether to print status messages
        
    Returns:
        Parser object with parsed GEDCOM data
        
    Raises:
        Exception: If all parsing methods fail
    """
    if verbose:
        print("Loading and preprocessing GEDCOM file...")
    
    # Method 1: Try preprocessing the file to fix formatting issues
    try:
        preprocessed_file = preprocess_gedcom_file(file_path)
        
        gedcom_parser = Parser()
        gedcom_parser.parse_file(preprocessed_file)
        
        # Clean up the temporary file
        Path(preprocessed_file).unlink()
        
        if verbose:
            print("GEDCOM file loaded successfully with preprocessing!")
        
        return gedcom_parser
        
    except Exception as e:
        if verbose:
            print(f"Warning: Preprocessing failed ({e}), trying original file...")
        
        # Method 2: Try the original file with standard parser
        try:
            gedcom_parser = Parser()
            gedcom_parser.parse_file(file_path)
            
            if verbose:
                print("GEDCOM file loaded successfully with standard parser!")
            
            return gedcom_parser
            
        except Exception as original_error:
            if verbose:
                print(f"Warning: Standard parsing failed ({original_error}), trying lenient parser...")
            
            # Method 3: Try lenient manual parsing
            try:
                gedcom_parser = parse_gedcom_lenient(file_path)
                
                if verbose:
                    print("GEDCOM file loaded successfully with lenient parser!")
                
                return gedcom_parser
                
            except Exception as lenient_error:
                # All methods failed
                raise Exception(
                    f"Failed to parse GEDCOM file with all methods. "
                    f"Preprocessing error: {e}. "
                    f"Standard parsing error: {original_error}. "
                    f"Lenient parsing error: {lenient_error}"
                )


def validate_gedcom_format(file_path, max_lines_to_check=1000):
    """Validate GEDCOM format and report common issues.
    
    Args:
        file_path: Path to the GEDCOM file
        max_lines_to_check: Maximum number of lines to analyze
        
    Returns:
        Dict with validation results and issues found
    """
    issues = []
    line_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if line_count >= max_lines_to_check:
                    break
                
                line_count += 1
                line = line.rstrip('\n\r')
                
                if line.strip():  # Skip empty lines
                    # Check if line starts with level number
                    if not re.match(r'^\d+\s', line):
                        issues.append({
                            'line': line_num,
                            'type': 'invalid_format',
                            'description': 'Line does not start with level number',
                            'content': line[:50] + '...' if len(line) > 50 else line
                        })
    
    except Exception as e:
        issues.append({
            'line': 0,
            'type': 'read_error',
            'description': f'Error reading file: {e}',
            'content': ''
        })
    
    return {
        'is_valid': len(issues) == 0,
        'lines_checked': line_count,
        'issues_found': len(issues),
        'issues': issues
    }
