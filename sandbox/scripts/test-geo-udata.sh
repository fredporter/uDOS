#!/bin/bash
# Test geographic data files with uDATA parser
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

# Geographic data directory
GEO_MAPS_DIR="$UDOS_ROOT/uMEMORY/system/geo/maps"

log_info "🗺️  Testing Geographic uDATA Files"
echo "================================="

# Check if directory exists
if [ ! -d "$GEO_MAPS_DIR" ]; then
    log_error "Geographic maps directory not found: $GEO_MAPS_DIR"
    exit 1
fi

# Process each geographic file
for file in "$GEO_MAPS_DIR"/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        log_info "Testing: $filename"

        # Test JSON validity first
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            log_success "✓ Valid JSON: $filename"
        else
            log_error "✗ Invalid JSON: $filename"
            continue
        fi

        # Test uDATA info using uCORE tools
        log_info "Getting file info using uCORE tools..."
        if bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" --info "$file" 2>/dev/null; then
            log_success "✓ File info retrieved: $filename"
        else
            log_warning "⚠ Could not get file info: $filename"
        fi

        echo "---"
    fi
done

log_success "Geographic data testing complete"
