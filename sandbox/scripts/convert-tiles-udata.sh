#!/bin/bash
# Convert geographic tile JSON files to uDATA minified format
# Location: sandbox/scripts/ (user processing scripts)

set -euo pipefail

# Simple logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Geographic tiles directory
GEO_TILES_DIR="$UDOS_ROOT/uMEMORY/system/geo/tiles"

log_info "🔄 Converting Geographic Tiles to uDATA Minified Format"
echo "====================================================="

cd "$GEO_TILES_DIR"

# Trash directory for original files
trash_dir="$UDOS_ROOT/trash"
if [ ! -d "$trash_dir" ]; then
    mkdir -p "$trash_dir"
    log_info "Created trash directory: $trash_dir"
fi

# Counter for processing
total_files=$(ls -1 uTILE-*.json | wc -l)
current_file=0
converted_count=0
failed_count=0

# Convert each uTILE JSON file to uDATA format
for file in uTILE-*.json; do
    if [ -f "$file" ]; then
        ((current_file++))
        basename="${file%.json}"
        temp_output="${basename}_temp.json"

        log_info "[$current_file/$total_files] Converting: $file"

        # Move original file to trash with timestamp
        timestamp=$(date +"%Y%m%d-%H%M%S")
        trash_filename="${basename}_original_${timestamp}.json"
        mv "$file" "$trash_dir/$trash_filename"

        # Use enhanced uCORE conversion tool
        if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" "$trash_dir/$trash_filename" "$temp_output"; then
            # Move converted version to original location
            mv "$temp_output" "$file"
            log_success "✓ Converted: $file"
            ((converted_count++))

            # Validate the conversion
            if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" --validate "$file" >/dev/null 2>&1; then
                log_success "✓ Validated: $file"
            else
                log_warning "⚠ Validation issues: $file"
            fi
        else
            log_error "✗ Conversion failed: $file"
            ((failed_count++))
            # Clean up temp file if it exists
            [ -f "$temp_output" ] && rm -f "$temp_output"
        fi

        echo "---"
    fi
done

# Show final results
echo
log_info "📊 Conversion Summary:"
log_info "• Total files processed: $total_files"
log_info "• Successfully converted: $converted_count"
log_info "• Failed conversions: $failed_count"
log_info "• Original files moved to: $trash_dir/"

echo
log_info "📋 Sample of converted files:"
ls -la uTILE-*.json | head -5

log_success "Geographic tiles uDATA conversion complete!"
