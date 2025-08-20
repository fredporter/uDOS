#!/bin/bash
# TILE Location Mapping System
# Advanced coordinate-to-tile conversion and spatial indexing

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════
# TILE LOCATION SYSTEM CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
CORE_MAPS="$UMEMORY/core"
MAP_ENGINE="$SCRIPT_DIR/umap-engine.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Logging
log_info() { echo -e "${CYAN}📍 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${BOLD}${BLUE}🗺️  $1${NC}"; }

# ═══════════════════════════════════════════════════════════════════════
# COORDINATE CONVERSION SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Convert address to coordinates (requires external geocoding)
address_to_coords() {
    local address="$1"
    
    # For now, return example coordinates
    # In production, this would use a geocoding service
    log_warning "Geocoding not implemented - using example coordinates"
    echo "40.7589 -73.9851"  # Manhattan, NYC
}

# Convert coordinates to readable location
coords_to_location() {
    local lat="$1"
    local lon="$2"
    
    # Reverse geocoding (simplified)
    local continent ocean city
    continent=$(determine_continent_detailed "$lat" "$lon")
    ocean=$(determine_ocean_detailed "$lat" "$lon")
    
    if [ "$continent" != "Ocean" ]; then
        echo "$continent region at ${lat}°N, ${lon}°E"
    else
        echo "$ocean at ${lat}°N, ${lon}°E"
    fi
}

# Determine continent with more detail
determine_continent_detailed() {
    local lat="$1"
    local lon="$2"
    
    # More detailed continent boundaries
    if (( $(echo "$lon >= -170 && $lon <= -30" | bc -l) )); then
        if (( $(echo "$lat >= 15" | bc -l) )); then
            echo "North America"
        elif (( $(echo "$lat >= -55" | bc -l) )); then
            echo "South America"
        else
            echo "Southern Ocean"
        fi
    elif (( $(echo "$lon >= -30 && $lon <= 40" | bc -l) )); then
        if (( $(echo "$lat >= 35" | bc -l) )); then
            echo "Europe"
        elif (( $(echo "$lat >= -35" | bc -l) )); then
            echo "Africa"
        else
            echo "Southern Ocean"
        fi
    elif (( $(echo "$lon >= 40 && $lon <= 180" | bc -l) )); then
        if (( $(echo "$lat >= 10" | bc -l) )); then
            echo "Asia"
        elif (( $(echo "$lat >= -50 && $lon >= 110" | bc -l) )); then
            echo "Oceania"
        else
            echo "Indian Ocean"
        fi
    elif (( $(echo "$lat <= -60" | bc -l) )); then
        echo "Antarctica"
    else
        echo "Ocean"
    fi
}

# Determine ocean with more detail
determine_ocean_detailed() {
    local lat="$1"
    local lon="$2"
    
    if (( $(echo "$lon >= -100 && $lon <= -30" | bc -l) )); then
        echo "Atlantic Ocean"
    elif (( $(echo "$lon >= -30 && $lon <= 20" | bc -l) )); then
        echo "Atlantic Ocean"
    elif (( $(echo "$lon >= 20 && $lon <= 150" | bc -l) )); then
        echo "Indian Ocean"
    elif (( $(echo "$lon >= 150 || $lon <= -100" | bc -l) )); then
        echo "Pacific Ocean"
    elif (( $(echo "$lat >= 66" | bc -l) )); then
        echo "Arctic Ocean"
    elif (( $(echo "$lat <= -60" | bc -l) )); then
        echo "Southern Ocean"
    else
        echo "Unknown Ocean"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# SPATIAL INDEXING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Create spatial index for fast tile lookup
create_spatial_index() {
    local index_file="$CORE_MAPS/spatial-index.json"
    local temp_file="$UMEMORY/system/temp/spatial-temp.json"
    
    mkdir -p "$(dirname "$temp_file")"
    
    log_info "Building spatial index..."
    
    # Initialize spatial index structure
    cat > "$index_file" << 'EOF'
{
    "metadata": {
        "type": "spatial_index",
        "version": "1.0.0",
        "created": null,
        "grid_size": {
            "width": 120,
            "height": 60
        },
        "index_type": "quadtree"
    },
    "grid_cells": {},
    "quadtree": {
        "root": {
            "bounds": {
                "north": 90,
                "south": -90,
                "east": 180,
                "west": -180
            },
            "tiles": [],
            "subdivisions": []
        }
    },
    "hash_index": {}
}
EOF

    log_success "Spatial index created"
}

# Add tile to spatial index
add_tile_to_index() {
    local tile_id="$1"
    local lat="$2"
    local lon="$3"
    
    local index_file="$CORE_MAPS/spatial-index.json"
    
    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        local temp_file="$UMEMORY/system/temp/spatial-temp.json"
        
        # Calculate grid cell
        local grid_x grid_y
        grid_x=$(echo "scale=0; ($lon + 180) * 120 / 360" | bc -l)
        grid_y=$(echo "scale=0; ($lat + 90) * 60 / 180" | bc -l)
        local grid_key="${grid_x}_${grid_y}"
        
        # Calculate geohash
        local geohash
        geohash=$(calculate_geohash "$lat" "$lon" 8)
        
        jq --arg tile_id "$tile_id" \
           --arg lat "$lat" \
           --arg lon "$lon" \
           --arg grid_key "$grid_key" \
           --arg geohash "$geohash" \
           '.grid_cells[$grid_key] += [$tile_id] |
            .hash_index[$geohash] += [$tile_id] |
            .metadata.modified = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' \
           "$index_file" > "$temp_file" && mv "$temp_file" "$index_file"
        
        log_info "Added $tile_id to spatial index (grid: $grid_key, hash: $geohash)"
    fi
}

# Calculate simple geohash
calculate_geohash() {
    local lat="$1"
    local lon="$2"
    local precision="${3:-8}"
    
    # Simplified geohash calculation
    local lat_scaled lon_scaled
    lat_scaled=$(echo "scale=0; ($lat + 90) * 1000" | bc -l)
    lon_scaled=$(echo "scale=0; ($lon + 180) * 1000" | bc -l)
    
    # Create hash from scaled coordinates
    local hash
    hash=$(echo "${lat_scaled}${lon_scaled}" | md5sum | cut -c1-"$precision")
    echo "$hash"
}

# Find nearby tiles
find_nearby_tiles() {
    local lat="$1"
    local lon="$2"
    local radius_km="${3:-10}"
    
    local index_file="$CORE_MAPS/spatial-index.json"
    
    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        # Convert radius to degrees (approximate)
        local radius_deg
        radius_deg=$(echo "scale=6; $radius_km / 111" | bc -l)
        
        # Calculate bounding box
        local north south east west
        north=$(echo "scale=6; $lat + $radius_deg" | bc -l)
        south=$(echo "scale=6; $lat - $radius_deg" | bc -l)
        east=$(echo "scale=6; $lon + $radius_deg" | bc -l)
        west=$(echo "scale=6; $lon - $radius_deg" | bc -l)
        
        log_info "Searching for tiles near ($lat, $lon) within ${radius_km}km"
        log_info "Bounding box: N:$north, S:$south, E:$east, W:$west"
        
        # Find grid cells in bounding box
        for lat_grid in $(seq $(echo "scale=0; ($south + 90) * 60 / 180" | bc -l) $(echo "scale=0; ($north + 90) * 60 / 180" | bc -l)); do
            for lon_grid in $(seq $(echo "scale=0; ($west + 180) * 120 / 360" | bc -l) $(echo "scale=0; ($east + 180) * 120 / 360" | bc -l)); do
                local grid_key="${lon_grid}_${lat_grid}"
                jq -r --arg grid_key "$grid_key" \
                   '.grid_cells[$grid_key][]? // empty' \
                   "$index_file"
            done
        done | sort -u
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# TILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

# Get or create tile at location
get_or_create_tile() {
    local lat="$1"
    local lon="$2"
    local depth="${3:-1}"
    local tile_type="${4:-surface}"
    local description="${5:-Auto-generated tile}"
    
    # First try to find existing tile
    local existing_tiles
    existing_tiles=$(find_tiles_at_coords "$lat" "$lon")
    
    if [ -n "$existing_tiles" ]; then
        echo "$existing_tiles" | head -1
        log_info "Found existing tile at ($lat, $lon)"
    else
        # Create new tile
        local tile_id
        tile_id=$("$MAP_ENGINE" create-tile "$lat" "$lon" "$depth" "$tile_type" "$description")
        
        # Add to spatial index
        add_tile_to_index "$tile_id" "$lat" "$lon"
        
        echo "$tile_id"
        log_success "Created new tile: $tile_id"
    fi
}

# Find tiles at exact coordinates
find_tiles_at_coords() {
    local lat="$1"
    local lon="$2"
    
    "$MAP_ENGINE" find-tile "$lat" "$lon"
}

# Get tile information
get_tile_info() {
    local tile_id="$1"
    local tile_file="$CORE_MAPS/tiles/${tile_id}.json"
    
    if [ -f "$tile_file" ]; then
        cat "$tile_file"
    else
        log_error "Tile not found: $tile_id"
        return 1
    fi
}

# Update tile metadata
update_tile_metadata() {
    local tile_id="$1"
    local key="$2"
    local value="$3"
    
    local tile_file="$CORE_MAPS/tiles/${tile_id}.json"
    
    if [ -f "$tile_file" ] && command -v jq >/dev/null 2>&1; then
        local temp_file="$UMEMORY/system/temp/tile-temp.json"
        
        jq --arg key "$key" \
           --arg value "$value" \
           '.metadata[$key] = $value |
            .temporal.modified = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' \
           "$tile_file" > "$temp_file" && mv "$temp_file" "$tile_file"
        
        log_success "Updated $tile_id metadata: $key = $value"
    else
        log_error "Cannot update tile metadata"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# COORDINATE UTILITIES
# ═══════════════════════════════════════════════════════════════════════

# Calculate distance between two points (Haversine formula)
calculate_distance() {
    local lat1="$1"
    local lon1="$2"
    local lat2="$3"
    local lon2="$4"
    
    # Convert to radians
    local lat1_rad lat2_rad lon1_rad lon2_rad
    lat1_rad=$(echo "scale=10; $lat1 * 3.14159265359 / 180" | bc -l)
    lat2_rad=$(echo "scale=10; $lat2 * 3.14159265359 / 180" | bc -l)
    lon1_rad=$(echo "scale=10; $lon1 * 3.14159265359 / 180" | bc -l)
    lon2_rad=$(echo "scale=10; $lon2 * 3.14159265359 / 180" | bc -l)
    
    # Haversine formula
    local dlat dlon a c
    dlat=$(echo "scale=10; $lat2_rad - $lat1_rad" | bc -l)
    dlon=$(echo "scale=10; $lon2_rad - $lon1_rad" | bc -l)
    
    # Simplified distance calculation (approximate)
    local distance_km
    distance_km=$(echo "scale=2; sqrt(($dlat * $dlat + $dlon * $dlon)) * 6371" | bc -l)
    echo "$distance_km"
}

# Convert decimal degrees to DMS (Degrees, Minutes, Seconds)
dd_to_dms() {
    local decimal="$1"
    local direction="$2"  # N/S for latitude, E/W for longitude
    
    local abs_decimal degrees minutes seconds
    abs_decimal=$(echo "${decimal#-}" | bc -l)
    degrees=$(echo "scale=0; $abs_decimal / 1" | bc -l)
    minutes=$(echo "scale=0; ($abs_decimal - $degrees) * 60 / 1" | bc -l)
    seconds=$(echo "scale=2; (($abs_decimal - $degrees) * 60 - $minutes) * 60" | bc -l)
    
    # Determine direction
    local dir
    if (( $(echo "$decimal >= 0" | bc -l) )); then
        dir=$(echo "$direction" | cut -c1)
    else
        dir=$(echo "$direction" | cut -c2)
    fi
    
    echo "${degrees}° ${minutes}' ${seconds}\" ${dir}"
}

# Validate coordinate format
validate_coord_format() {
    local lat="$1"
    local lon="$2"
    
    # Check if numeric
    if ! [[ "$lat" =~ ^-?[0-9]+\.?[0-9]*$ ]] || ! [[ "$lon" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
        return 1
    fi
    
    # Check ranges
    if (( $(echo "$lat < -90 || $lat > 90" | bc -l) )); then
        return 1
    fi
    
    if (( $(echo "$lon < -180 || $lon > 180" | bc -l) )); then
        return 1
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  locate <lat> <lon>              Get or create tile at coordinates"
    echo "  find <lat> <lon> [radius_km]    Find tiles near coordinates"
    echo "  address <address>               Get tile for address (requires geocoding)"
    echo "  distance <lat1> <lon1> <lat2> <lon2>  Calculate distance"
    echo "  convert <lat> <lon>             Convert coordinates to DMS format"
    echo "  nearby <lat> <lon> [radius]     Find nearby tiles"
    echo "  info <tile_id>                  Get tile information"
    echo "  update <tile_id> <key> <value>  Update tile metadata"
    echo "  index                           Create spatial index"
    echo "  help                            Show this help"
    echo
    echo "Examples:"
    echo "  $0 locate 40.7589 -73.9851"
    echo "  $0 find 51.5074 -0.1278 5"
    echo "  $0 distance 40.7589 -73.9851 51.5074 -0.1278"
    echo "  $0 convert 40.7589 -73.9851"
    echo "  $0 nearby 40.7589 -73.9851 10"
}

# Print header
print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                 📍 TILE Location Mapping System                 ║"
    echo "║              Advanced Coordinate-to-Tile Conversion             ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Main command processor
main() {
    case "${1:-help}" in
        locate)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            
            if ! validate_coord_format "$2" "$3"; then
                log_error "Invalid coordinates: $2, $3"
                exit 1
            fi
            
            local location
            location=$(coords_to_location "$2" "$3")
            log_info "Location: $location"
            
            get_or_create_tile "$2" "$3" "${4:-1}" "${5:-surface}" "$location"
            ;;
            
        find)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            
            if ! validate_coord_format "$2" "$3"; then
                log_error "Invalid coordinates: $2, $3"
                exit 1
            fi
            
            find_tiles_at_coords "$2" "$3"
            ;;
            
        address)
            if [ $# -lt 2 ]; then
                log_error "Address required"
                show_usage
                exit 1
            fi
            
            local coords
            coords=$(address_to_coords "$2")
            read -r lat lon <<< "$coords"
            
            log_info "Coordinates for '$2': $lat, $lon"
            get_or_create_tile "$lat" "$lon" 1 surface "$2"
            ;;
            
        distance)
            if [ $# -lt 5 ]; then
                log_error "Two coordinate pairs required"
                show_usage
                exit 1
            fi
            
            local distance
            distance=$(calculate_distance "$2" "$3" "$4" "$5")
            echo "Distance: ${distance} km"
            ;;
            
        convert)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            
            echo "Decimal: $2, $3"
            echo "DMS: $(dd_to_dms "$2" "NS"), $(dd_to_dms "$3" "EW")"
            ;;
            
        nearby)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            
            find_nearby_tiles "$2" "$3" "${4:-10}"
            ;;
            
        info)
            if [ $# -lt 2 ]; then
                log_error "Tile ID required"
                show_usage
                exit 1
            fi
            
            get_tile_info "$2"
            ;;
            
        update)
            if [ $# -lt 4 ]; then
                log_error "Tile ID, key, and value required"
                show_usage
                exit 1
            fi
            
            update_tile_metadata "$2" "$3" "$4"
            ;;
            
        index)
            create_spatial_index
            ;;
            
        help|--help|-h)
            show_usage
            ;;
            
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
print_header
main "$@"
