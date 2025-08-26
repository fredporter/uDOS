#!/bin/bash
# Process and rename geographic data files
# Remove uDATA- prefixes and organize files
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

# Geographic data directory
GEO_MAPS_DIR="$UDOS_ROOT/uMEMORY/system/geo/maps"

log_info "🔄 Processing Geographic Data Files"
echo "==================================="

cd "$GEO_MAPS_DIR"

# Rename files to remove uDATA- prefix
for file in uDATA-*.json; do
    if [ -f "$file" ]; then
        # Extract clean name
        clean_name="${file#uDATA-}"

        # Handle special cases
        if [[ "$clean_name" == uMAP-* ]]; then
            # Keep uMAP- prefix for proper naming
            clean_name="$clean_name"
        elif [[ "$clean_name" == E7172B38-Global-Geographic-Master.json ]]; then
            # Rename master file to proper uMAP format
            clean_name="uMAP-000000-Global-Geographic-Master.json"
        fi

        log_info "Renaming: $file → $clean_name"

        # Perform rename
        if mv "$file" "$clean_name"; then
            log_success "✓ Renamed: $clean_name"
        else
            log_error "✗ Failed to rename: $file"
        fi
    fi
done

# List final results
log_info "Final geographic data files:"
ls -la *.json

log_success "Geographic data processing complete"
