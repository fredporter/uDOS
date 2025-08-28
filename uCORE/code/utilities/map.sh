#!/bin/bash
# uCORE Map Utility - Simple Geographic Operations
# Handles basic uMAP and uTILE operations for uCORE compatibility

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Geographic data directories
GEO_DATA="$UDOS_ROOT/uMEMORY/system/geo"
MAPS_DATA="$GEO_DATA/maps"
TILES_DATA="$GEO_DATA/tiles"

# List available maps
list_maps() {
    log_info "Available uMAP files:"

    if [ -d "$MAPS_DATA" ]; then
        for map_file in "$MAPS_DATA"/uDATA-uMAP-*.json; do
            if [ -f "$map_file" ]; then
                local map_name=$(basename "$map_file" .json)
                local map_id=$(echo "$map_name" | sed 's/uDATA-uMAP-//' | sed 's/-.*//')
                local description=$(echo "$map_name" | sed 's/uDATA-uMAP-[^-]*-//' | tr '-' ' ')
                echo "  🗺️  $map_id - $description"
            fi
        done
    else
        log_warning "Maps directory not found: $MAPS_DATA"
    fi
}

# List available tiles
list_tiles() {
    log_info "Available uTILE files:"

    if [ -d "$TILES_DATA" ]; then
        for tile_file in "$TILES_DATA"/uDATA-uTILE-*.json; do
            if [ -f "$tile_file" ]; then
                local tile_name=$(basename "$tile_file" .json)
                local tile_id=$(echo "$tile_name" | sed 's/uDATA-uTILE-//' | sed 's/-.*//')
                local description=$(echo "$tile_name" | sed 's/uDATA-uTILE-[^-]*-//' | tr '-' ' ')
                echo "  🏙️  $tile_id - $description"
            fi
        done
    else
        log_warning "Tiles directory not found: $TILES_DATA"
    fi
}

# Show map information
show_map() {
    local map_id="$1"
    local map_file="$MAPS_DATA/uDATA-uMAP-$map_id"*

    # Find the actual file (handle wildcards)
    local actual_file=$(ls $map_file 2>/dev/null | head -1)

    if [ -f "$actual_file" ]; then
        log_info "Map information for $map_id:"

        if command -v jq >/dev/null 2>&1; then
            echo "  Name: $(jq -r '.metadata.name // "Unknown"' "$actual_file")"
            echo "  Description: $(jq -r '.metadata.description // "No description"' "$actual_file")"
            echo "  Type: $(jq -r '.metadata.type // "Unknown"' "$actual_file")"
            echo "  Created: $(jq -r '.metadata.created // "Unknown"' "$actual_file")"
            echo "  Entries: $(jq -r '.data | length' "$actual_file")"
        else
            echo "  File: $(basename "$actual_file")"
            echo "  Size: $(wc -l < "$actual_file") lines"
        fi
    else
        log_error "Map not found: $map_id"
        return 1
    fi
}

# Show tile information
show_tile() {
    local tile_id="$1"
    local tile_file="$TILES_DATA/uDATA-uTILE-$tile_id"*

    # Find the actual file (handle wildcards)
    local actual_file=$(ls $tile_file 2>/dev/null | head -1)

    if [ -f "$actual_file" ]; then
        log_info "Tile information for $tile_id:"

        if command -v jq >/dev/null 2>&1; then
            echo "  Name: $(jq -r '.metadata.name // "Unknown"' "$actual_file")"
            echo "  Description: $(jq -r '.metadata.description // "No description"' "$actual_file")"
            echo "  Region: $(jq -r '.metadata.region // "Unknown"' "$actual_file")"
            echo "  Created: $(jq -r '.metadata.created // "Unknown"' "$actual_file")"
            echo "  Locations: $(jq -r '.data | length' "$actual_file")"
        else
            echo "  File: $(basename "$actual_file")"
            echo "  Size: $(wc -l < "$actual_file") lines"
        fi
    else
        log_error "Tile not found: $tile_id"
        return 1
    fi
}

# Find location in maps and tiles
find_location() {
    local query="$1"
    local found=false

    log_info "Searching for: $query"

    # Search in maps
    if [ -d "$MAPS_DATA" ]; then
        for map_file in "$MAPS_DATA"/uDATA-uMAP-*.json; do
            if [ -f "$map_file" ]; then
                if grep -qi "$query" "$map_file" 2>/dev/null; then
                    local map_name=$(basename "$map_file" .json | sed 's/uDATA-uMAP-//')
                    echo "  🗺️  Found in map: $map_name"
                    found=true
                fi
            fi
        done
    fi

    # Search in tiles
    if [ -d "$TILES_DATA" ]; then
        for tile_file in "$TILES_DATA"/uDATA-uTILE-*.json; do
            if [ -f "$tile_file" ]; then
                if grep -qi "$query" "$tile_file" 2>/dev/null; then
                    local tile_name=$(basename "$tile_file" .json | sed 's/uDATA-uTILE-//')
                    echo "  🏙️  Found in tile: $tile_name"
                    found=true
                fi
            fi
        done
    fi

    if [ "$found" == false ]; then
        log_warning "Location not found: $query"
    fi
}

# Initialize geographic system
init_geo() {
    log_info "Initializing geographic system..."

    # Create directories
    mkdir -p "$GEO_DATA"/{maps,tiles,cultural}

    # Check for geographic engines
    local geo_engine="$UDOS_ROOT/uCORE/geo/engines/geo-core-engine.sh"
    if [ -x "$geo_engine" ]; then
        log_info "Geographic engines available"
        "$geo_engine" status 2>/dev/null || true
    else
        log_warning "Geographic engines not found"
    fi

    log_success "Geographic system initialized"
}

# Show statistics
show_stats() {
    log_info "Geographic system statistics:"

    local map_count=0
    local tile_count=0

    if [ -d "$MAPS_DATA" ]; then
        map_count=$(find "$MAPS_DATA" -name "uDATA-uMAP-*.json" | wc -l | tr -d ' ')
    fi

    if [ -d "$TILES_DATA" ]; then
        tile_count=$(find "$TILES_DATA" -name "uDATA-uTILE-*.json" | wc -l | tr -d ' ')
    fi

    echo "  Maps: $map_count datasets"
    echo "  Tiles: $tile_count metropolitan areas"
    echo "  Data path: $GEO_DATA"
}

# Show usage
show_usage() {
    echo "Usage: map <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list maps              List available uMAP files"
    echo "  list tiles             List available uTILE files"
    echo "  show map <id>          Show map information"
    echo "  show tile <id>         Show tile information"
    echo "  find <location>        Find location in maps/tiles"
    echo "  init                   Initialize geographic system"
    echo "  stats                  Show system statistics"
    echo ""
    echo "Examples:"
    echo "  map list maps"
    echo "  map show map 000000"
    echo "  map show tile 00EN20"
    echo "  map find 'Los Angeles'"
    echo "  map stats"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_usage
        return 1
    fi

    case "$1" in
        help|--help|-h)
            show_usage
            ;;
        list)
            case "${2:-}" in
                maps)
                    list_maps
                    ;;
                tiles)
                    list_tiles
                    ;;
                *)
                    log_error "list requires 'maps' or 'tiles'"
                    return 1
                    ;;
            esac
            ;;
        show)
            case "${2:-}" in
                map)
                    if [ $# -lt 3 ]; then
                        log_error "show map requires map ID"
                        return 1
                    fi
                    show_map "$3"
                    ;;
                tile)
                    if [ $# -lt 3 ]; then
                        log_error "show tile requires tile ID"
                        return 1
                    fi
                    show_tile "$3"
                    ;;
                *)
                    log_error "show requires 'map' or 'tile'"
                    return 1
                    ;;
            esac
            ;;
        find)
            if [ $# -lt 2 ]; then
                log_error "find requires location query"
                return 1
            fi
            find_location "$2"
            ;;
        init)
            init_geo
            ;;
        stats)
            show_stats
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            return 1
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
