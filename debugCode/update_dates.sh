#!/bin/bash

# Replace the birth_year extraction blocks with a simple call to format_dates_for_dot

# For parent sections
sed -i '/parent_birth = parent\.get_birth_data()/,/birth_year = f"\\\\nb\. {date_str\[:4\]}"/c\
            dates_info = format_dates_for_dot(parent)' gedcom_visualizer/generate_asciidoc.py

# Replace the label format for parents
sed -i 's/\\n({parent_id}){birth_year}/{dates_info}/g' gedcom_visualizer/generate_asciidoc.py

# For spouse sections
sed -i '/spouse_birth = spouse\.get_birth_data()/,/birth_year = f"\\\\nb\. {date_str\[:4:\]}"/c\
            dates_info = format_dates_for_dot(spouse)' gedcom_visualizer/generate_asciidoc.py

# Replace the label format for spouses
sed -i 's/\\n({spouse_id}){birth_year}/{dates_info}/g' gedcom_visualizer/generate_asciidoc.py

# For child sections
sed -i '/child_birth = child\.get_birth_data()/,/birth_year = f"\\\\nb\. {date_str\[:4\]}"/c\
            dates_info = format_dates_for_dot(child)' gedcom_visualizer/generate_asciidoc.py

# Replace the label format for children
sed -i 's/\\n({child_id}){birth_year}/{dates_info}/g' gedcom_visualizer/generate_asciidoc.py
