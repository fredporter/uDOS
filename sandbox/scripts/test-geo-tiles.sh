#!/bin/bash
# Test geographic tile files with uDATA parser
# Location: sandbox/scripts/ (user test scripts)

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

log_info "🗺️  Testing Geographic Tile Files"
echo "=================================="

# Check if directory exists
if [ ! -d "$GEO_TILES_DIR" ]; then
    log_error "Geographic tiles directory not found: $GEO_TILES_DIR"
    exit 1
fi

# Test a few sample files
sample_files=(
    "uTILE-00EN20-Los-Angeles-County.json"
    "uTILE-00HO35-New-York-City.json"
    "uTILE-00MK60-Earth.json"
)

for filename in "${sample_files[@]}"; do
    file="$GEO_TILES_DIR/$filename"
    if [ -f "$file" ]; then
        log_info "Testing: $filename"

        # Test JSON validity first
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            log_success "✓ Valid JSON: $filename"
        else
            log_error "✗ Invalid JSON: $filename"
            continue
        fi

        # Test file info using uCORE tools
        log_info "Getting file info using uCORE tools..."
        if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" --info "$file" 2>/dev/null | head -10; then
            log_success "✓ File info retrieved: $filename"
        else
            log_warning "⚠ Could not get file info: $filename"
        fi

        echo "---"
    else
        log_warning "File not found: $filename"
    fi
done

# Count all files
total_files=$(ls "$GEO_TILES_DIR"/*.json 2>/dev/null | wc -l)
log_info "Total tile files found: $total_files"

log_success "Geographic tile testing complete"
