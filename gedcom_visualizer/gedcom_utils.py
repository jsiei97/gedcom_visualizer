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
    
    Args:
        file_path: Path to the original GEDCOM file
        
    Returns:
        Path to the preprocessed temporary file
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    processed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip('\n\r')
        
        # Check if line starts with a level number (0-9 followed by space)
        if re.match(r'^\d+\s', line):
            # This is a properly formatted GEDCOM line
            processed_lines.append(line)
        elif line.strip() == '':
            # Empty line - keep as is
            processed_lines.append(line)
        else:
            # This line doesn't start with a level number - it's likely a continuation
            # that got improperly split. Try to merge it with the previous line or
            # make it a proper CONC line
            
            if processed_lines and line.strip():
                # Get the level of the previous line
                prev_line = processed_lines[-1]
                level_match = re.match(r'^(\d+)\s', prev_line)
                
                if level_match:
                    level = int(level_match.group(1))
                    
                    # If the previous line was a CONC line, merge this content
                    if 'CONC' in prev_line:
                        processed_lines[-1] = prev_line + ' ' + line.strip()
                    else:
                        # Add as a new CONC line with the same level
                        processed_lines.append(f"{level} CONC {line.strip()}")
                else:
                    # Fallback: make it a level 4 CONC line
                    processed_lines.append(f"4 CONC {line.strip()}")
            elif line.strip():
                # No previous line to reference, make it a level 4 CONC
                processed_lines.append(f"4 CONC {line.strip()}")
            else:
                # Empty line
                processed_lines.append(line)
        
        i += 1
    
    # Write to a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8')
    for line in processed_lines:
        temp_file.write(line + '\n')
    temp_file.close()
    
    return temp_file.name


def load_gedcom_robust(file_path, verbose=False):
    """Load and parse a GEDCOM file with robust error handling.
    
    This function first attempts to preprocess the GEDCOM file to fix common
    formatting issues before parsing. If preprocessing fails, it falls back
    to parsing the original file.
    
    Args:
        file_path: Path to the GEDCOM file
        verbose: Whether to print status messages
        
    Returns:
        Parser object with parsed GEDCOM data
        
    Raises:
        Exception: If both preprocessing and direct parsing fail
    """
    if verbose:
        print("Loading and preprocessing GEDCOM file...")
    
    # First, try preprocessing the file to fix formatting issues
    try:
        preprocessed_file = preprocess_gedcom_file(file_path)
        
        gedcom_parser = Parser()
        gedcom_parser.parse_file(preprocessed_file)
        
        # Clean up the temporary file
        Path(preprocessed_file).unlink()
        
        if verbose:
            print("GEDCOM file loaded successfully!")
        
        return gedcom_parser
        
    except Exception as e:
        # If preprocessing fails, try the original file
        if verbose:
            print(f"Warning: Preprocessing failed ({e}), trying original file...")
        
        try:
            gedcom_parser = Parser()
            gedcom_parser.parse_file(file_path)
            
            if verbose:
                print("GEDCOM file loaded successfully!")
            
            return gedcom_parser
            
        except Exception as original_error:
            # Both methods failed
            raise Exception(
                f"Failed to parse GEDCOM file. "
                f"Preprocessing error: {e}. "
                f"Direct parsing error: {original_error}"
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
