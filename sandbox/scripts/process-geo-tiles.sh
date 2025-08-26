#!/bin/bash
# Process and rename geographic tile files
# Remove uDATA- prefixes and keep uTILE- naming
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

log_info "🔄 Processing Geographic Tile Files"
echo "===================================="

cd "$GEO_TILES_DIR"

# Rename files to remove uDATA- prefix, keep uTILE-
for file in uDATA-*.json; do
    if [ -f "$file" ]; then
        # Extract clean name by removing uDATA- prefix
        clean_name="${file#uDATA-}"

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
log_info "Final geographic tile files:"
ls -la *.json | head -10
echo "..."
total_count=$(ls -1 *.json | wc -l)
log_info "Total tile files: $total_count"

log_success "Geographic tile processing complete"
