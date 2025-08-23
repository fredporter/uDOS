#!/bin/bash

# uDATA Format Validation and Testing Script
# Tests the new uDATA format files and validates JSON parsing

echo "🧪 uDATA Format Testing and Validation"
echo "======================================"
echo

# Function to test JSON parsing line by line
test_udata_parsing() {
    local file="$1"
    local filename=$(basename "$file")
    local line_count=0
    local valid_count=0
    local error_count=0

    echo "📄 Testing: $filename"

    while IFS= read -r line; do
        line_count=$((line_count + 1))

        # Skip empty lines
        if [[ -z "${line// }" ]]; then
            continue
        fi

        # Test if the line is valid JSON
        if echo "$line" | python3 -m json.tool > /dev/null 2>&1; then
            valid_count=$((valid_count + 1))
            echo "  ✅ Line $line_count: Valid JSON"
        else
            error_count=$((error_count + 1))
            echo "  ❌ Line $line_count: Invalid JSON"
            echo "     Content: ${line:0:100}..."
        fi
    done < "$file"

    echo "  📊 Results: $valid_count valid, $error_count errors, $line_count total lines"
    echo
}

# Function to extract metadata from uDATA files
extract_metadata() {
    local file="$1"
    local filename=$(basename "$file")

    echo "📋 Metadata for: $filename"

    # Get first line (should be metadata)
    local first_line=$(head -n 1 "$file")

    if echo "$first_line" | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    if 'metadata' in data:
        metadata = data['metadata']
        print(f\"  📦 System: {metadata.get('system', 'Unknown')}\")
        print(f\"  📅 Version: {metadata.get('version', 'Unknown')}\")
        print(f\"  📝 Format: {metadata.get('format', 'Unknown')}\")
        print(f\"  📄 Description: {metadata.get('description', 'No description')}\")
    else:
        print('  ⚠️  No metadata found in first line')
except Exception as e:
    print(f'  ❌ Error parsing metadata: {e}')
" 2>/dev/null; then
        :
    else
        echo "  ❌ Failed to parse metadata"
    fi
    echo
}

# Function to count records by type
count_record_types() {
    local file="$1"
    local filename=$(basename "$file")

    echo "📊 Record Types in: $filename"

    python3 -c "
import json
import sys
from collections import defaultdict

type_counts = defaultdict(int)
total_records = 0

try:
    with open('$file', 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                total_records += 1

                # Determine record type
                if 'metadata' in record:
                    record_type = 'metadata'
                elif 'command' in record:
                    record_type = 'command'
                elif 'role' in record:
                    record_type = 'user_role'
                elif 'name' in record and 'colors' in record:
                    record_type = 'color_palette'
                elif 'type' in record:
                    record_type = record['type']
                else:
                    record_type = 'unknown'

                type_counts[record_type] += 1

            except json.JSONDecodeError as e:
                print(f'  ❌ JSON error on line {line_num}: {e}')

    print(f'  📦 Total records: {total_records}')
    for record_type, count in sorted(type_counts.items()):
        print(f'  📋 {record_type}: {count}')

except Exception as e:
    print(f'  ❌ Error processing file: {e}')
"
    echo
}

# Main testing loop
echo "🔍 Scanning for uDATA files..."
udata_files=($(find /Users/agentdigital/uDOS/uMEMORY/system -name "uDATA-*.json" 2>/dev/null))

if [ ${#udata_files[@]} -eq 0 ]; then
    echo "❌ No uDATA files found!"
    echo "Expected files with pattern: uDATA-YYYYMMDD-*.json"
    exit 1
fi

echo "Found ${#udata_files[@]} uDATA files:"
for file in "${udata_files[@]}"; do
    echo "  📄 $(basename "$file")"
done
echo

# Test each file
for file in "${udata_files[@]}"; do
    echo "🧪 Testing: $(basename "$file")"
    echo "----------------------------------------"

    # Test JSON parsing
    test_udata_parsing "$file"

    # Extract metadata
    extract_metadata "$file"

    # Count record types
    count_record_types "$file"

    echo "----------------------------------------"
    echo
done

# Test color palette default
echo "🎨 Testing Color Palette Default..."
echo "===================================="

colors_file="/Users/agentdigital/uDOS/uMEMORY/system/uDATA-20250823-colours.json"
if [ -f "$colors_file" ]; then
    echo "📄 Checking default palette in: $(basename "$colors_file")"

    python3 -c "
import json
try:
    with open('$colors_file', 'r') as f:
        first_line = f.readline().strip()
        metadata = json.loads(first_line)

        if 'default_palette' in metadata:
            default = metadata['default_palette']
            print(f'  ✅ Default palette set to: {default}')

            if default == 'polaroid_colors':
                print('  🎯 Correct! Polaroid Colors is set as default')
            else:
                print(f'  ⚠️  Expected: polaroid_colors, Found: {default}')
        else:
            print('  ❌ No default_palette specified in metadata')

except Exception as e:
    print(f'  ❌ Error checking default palette: {e}')
"
else
    echo "❌ Colors file not found!"
fi

echo
echo "✅ uDATA Testing Complete!"
echo "=========================="
echo "📋 Summary:"
echo "  • Validated JSON line-by-line parsing"
echo "  • Extracted metadata from all files"
echo "  • Counted record types"
echo "  • Verified color palette default"
echo
echo "💡 Note: uDATA format maintains JSON compatibility while using"
echo "   one record per line for efficient processing."
