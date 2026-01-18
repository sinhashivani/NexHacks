"""
Test script to find the correct way to parse the CSV file
"""

import csv
import json

def parse_csv_line_manual(line):
    """Manually parse a CSV line handling quoted fields with commas"""
    fields = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                # Escaped quote ("")
                current_field += '"'
                i += 2
            elif in_quotes and i + 1 < len(line) and line[i + 1] == ',':
                # End of quoted field
                in_quotes = False
                fields.append(current_field)
                current_field = ""
                i += 2  # Skip quote and comma
            else:
                # Start or end of quotes
                in_quotes = not in_quotes
                i += 1
        elif char == ',' and not in_quotes:
            # Field separator
            fields.append(current_field.strip())
            current_field = ""
            i += 1
        else:
            current_field += char
            i += 1
    
    # Add last field
    if current_field:
        fields.append(current_field.strip())
    
    return fields

# Test with actual CSV line
csv_path = 'data/polymarket_events_by_tags.csv'

print("Testing CSV parsing methods...")
print("=" * 60)

with open(csv_path, 'r', encoding='utf-8') as f:
    # Read header
    header_line = f.readline()
    print(f"Header line: {repr(header_line[:150])}")
    
    # Parse header
    header = parse_csv_line_manual(header_line.strip())
    print(f"Parsed header ({len(header)} fields): {[h.strip()[:30] for h in header]}")
    
    # Read first data row
    data_line = f.readline()
    print(f"\nFirst data line (first 200 chars): {repr(data_line[:200])}")
    
    # Try standard csv.reader
    print("\n--- Method 1: Standard csv.reader ---")
    f.seek(0)
    next(f)  # Skip header
    reader = csv.reader(f, quotechar='"', skipinitialspace=True)
    row1 = next(reader)
    print(f"Fields: {len(row1)}")
    print(f"Field 0 (event_title): {repr(row1[0][:50]) if len(row1) > 0 else 'MISSING'}")
    print(f"Field 2 (clob_token_ids): {repr(row1[2][:100]) if len(row1) > 2 else 'MISSING'}")
    if len(row1) > 3:
        print(f"Extra fields detected! Field 3: {repr(row1[3][:50])}")
        print(f"Field 4: {repr(row1[4][:50]) if len(row1) > 4 else 'N/A'}")
    
    # Try manual parser
    print("\n--- Method 2: Manual parser ---")
    f.seek(0)
    next(f)  # Skip header
    data_line = f.readline()
    row2 = parse_csv_line_manual(data_line.strip())
    print(f"Fields: {len(row2)}")
    print(f"Field 0 (event_title): {repr(row2[0][:50]) if len(row2) > 0 else 'MISSING'}")
    print(f"Field 2 (clob_token_ids): {repr(row2[2][:100]) if len(row2) > 2 else 'MISSING'}")
    
    # Try csv.reader with different settings
    print("\n--- Method 3: csv.reader with escapechar ---")
    f.seek(0)
    next(f)  # Skip header
    reader3 = csv.reader(f, quotechar='"', escapechar='\\', skipinitialspace=True)
    row3 = next(reader3)
    print(f"Fields: {len(row3)}")
    print(f"Field 0 (event_title): {repr(row3[0][:50]) if len(row3) > 0 else 'MISSING'}")
    print(f"Field 2 (clob_token_ids): {repr(row3[2][:100]) if len(row3) > 2 else 'MISSING'}")

print("\n" + "=" * 60)
print("Recommendation: Use the method that produces 3 fields correctly")
