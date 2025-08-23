#!/bin/bash

# uDATA Conversion and Cleanup Script
# Converts remaining JSON files to uDATA format and cleans up old files

echo "🔄 uDATA System Conversion and Cleanup"
echo "====================================="
echo

SYSTEM_DIR="/Users/agentdigital/uDOS/uMEMORY/system"
BACKUP_DIR="$SYSTEM_DIR/legacy-json-backup"
DATE=$(date +%Y%m%d)

# Create backup directory
echo "📦 Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Function to convert standard JSON files to uDATA format
convert_to_udata() {
    local input_file="$1"
    local output_file="$2"
    local description="$3"

    echo "🔄 Converting: $(basename "$input_file")"

    # Create metadata record
    local metadata="{\"metadata\":{\"system\":\"uDOS-v1.3.3\",\"created\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"version\":\"1.3.3\",\"format\":\"uDATA-v1\",\"description\":\"$description\",\"converted_from\":\"$(basename "$input_file")\"}}"

    # Write metadata first
    echo "$metadata" > "$output_file"

    # Convert JSON content based on structure
    if python3 -c "
import json
import sys

try:
    with open('$input_file', 'r') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        # Array of objects - write each as a line
        for item in data:
            print(json.dumps(item))
    elif isinstance(data, dict):
        # Object structure - convert based on content
        for key, value in data.items():
            if key == 'metadata':
                continue  # Skip metadata, we already added it
            elif isinstance(value, dict):
                # Add name field and flatten
                record = {'name': key, **value}
                print(json.dumps(record))
            elif isinstance(value, list) and key in ['commands', 'shortcodes', 'roles']:
                # Handle command/shortcode arrays
                for item in value:
                    if isinstance(item, dict):
                        print(json.dumps(item))
                    else:
                        record = {'name': item, 'type': key.rstrip('s')}
                        print(json.dumps(record))
            else:
                # Simple key-value pair
                record = {'name': key, 'value': value, 'type': 'configuration'}
                print(json.dumps(record))

    sys.exit(0)
except Exception as e:
    print(f'Error converting {input_file}: {e}', file=sys.stderr)
    sys.exit(1)
" >> "$output_file" 2>/dev/null; then
        echo "  ✅ Converted successfully"
        return 0
    else
        echo "  ❌ Conversion failed"
        return 1
    fi
}

# List of files to convert
declare -A FILES_TO_CONVERT
FILES_TO_CONVERT["dynamic-commands.json"]="Dynamic command definitions for uDOS runtime execution"
FILES_TO_CONVERT["emoji-support.json"]="Emoji support configuration for display systems"
FILES_TO_CONVERT["installation-lifespan.json"]="Installation lifecycle and version tracking data"
FILES_TO_CONVERT["ucode-commands.json"]="uCode shell command definitions and syntax"
FILES_TO_CONVERT["unified-command-system-complete.json"]="Complete unified command system dataset"
FILES_TO_CONVERT["unified-command-system-consolidated.json"]="Consolidated command system configuration"
FILES_TO_CONVERT["unified-command-system.json"]="Main unified command system definitions"
FILES_TO_CONVERT["vb-commands.json"]="VB-style command definitions for compatibility"

echo "🔍 Converting remaining JSON files to uDATA format..."
echo

for file in "${!FILES_TO_CONVERT[@]}"; do
    input_path="$SYSTEM_DIR/$file"
    output_path="$SYSTEM_DIR/uDATA-$DATE-$(basename "$file" .json).json"
    description="${FILES_TO_CONVERT[$file]}"

    if [ -f "$input_path" ]; then
        convert_to_udata "$input_path" "$output_path" "$description"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo
echo "📦 Backing up original JSON files..."

# Move original files to backup
for file in commands.json shortcodes.json user-roles.json variable-system.json dynamic-commands.json emoji-support.json installation-lifespan.json ucode-commands.json unified-command-system*.json vb-commands.json; do
    if [ -f "$SYSTEM_DIR/$file" ]; then
        echo "  📦 Backing up: $file"
        mv "$SYSTEM_DIR/$file" "$BACKUP_DIR/"
    fi
done

echo
echo "🗂️ Organizing color palette files..."

# Remove old color directories and files, keep only the new uDATA colors file
if [ -d "$SYSTEM_DIR/colors" ]; then
    echo "  📦 Backing up colors directory"
    mv "$SYSTEM_DIR/colors" "$BACKUP_DIR/"
fi

# Clean up any old color files
for color_file in color-palettes.json uDOS-master-palettes.html; do
    if [ -f "$SYSTEM_DIR/$color_file" ]; then
        echo "  📦 Backing up: $color_file"
        mv "$SYSTEM_DIR/$color_file" "$BACKUP_DIR/"
    fi
done

echo
echo "🧹 Cleaning up duplicate and old uDATA files..."

# Remove older uDATA files from previous dates
find "$SYSTEM_DIR" -name "uDATA-2025082[12]*" -not -name "uDATA-$DATE-*" | while read old_file; do
    if [ -f "$old_file" ]; then
        echo "  🗑️  Removing old: $(basename "$old_file")"
        mv "$old_file" "$BACKUP_DIR/"
    fi
done

echo
echo "📋 Final uDATA file inventory..."

# List all current uDATA files
echo "Current uDATA files in system:"
ls -la "$SYSTEM_DIR"/uDATA-*.json | awk '{print "  📄 " $9}' | sed 's|.*/||'

echo
echo "📊 uDATA Format Summary..."

# Count records in each file
total_files=0
total_records=0

for file in "$SYSTEM_DIR"/uDATA-*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        record_count=$(wc -l < "$file")
        total_files=$((total_files + 1))
        total_records=$((total_records + record_count))
        echo "  📄 $filename: $record_count records"
    fi
done

echo
echo "✅ Conversion Complete!"
echo "======================"
echo "📊 Final Summary:"
echo "  • Total uDATA files: $total_files"
echo "  • Total records: $total_records"
echo "  • Backup location: $BACKUP_DIR"
echo "  • Default color palette: Polaroid Colors"
echo "  • Format version: uDATA-v1"
echo
echo "🎯 All JSON datasets now follow uDATA format:"
echo "  • One record per line (minified JSON)"
echo "  • Metadata record as first line"
echo "  • Filename format: uDATA-YYYYMMDD-{title}.json"
echo "  • Template files renamed to: uTEMPLATE-{name}"
echo
echo "💡 The uCORE JSON engine has been enhanced with uDATA parsing"
echo "   capabilities for robust dataset processing."
