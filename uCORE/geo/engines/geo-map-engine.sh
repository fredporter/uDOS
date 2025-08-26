#!/bin/bash
# uMAP Core Engine - Earth Tile Location Mapping System
#!/bin/bash
# uCORE Geographic Map Engine v1.0.4.1
# uDOS v1.0.4.1 - Advanced Geospatial Framework

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════
# CORE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

# Paths - Updated for v1.0.4.1 geo system
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
GEO_DATA="$UMEMORY/system/geo"
MAPS_DATA="$GEO_DATA/maps"
TILES_DATA="$GEO_DATA/tiles"
CULTURAL_DATA="$GEO_DATA/cultural"
TILE_CACHE="$SCRIPT_DIR/../cache"
TEMP_DIR="$TILE_CACHE/temp"

# MAP-00 Configuration
MAP_ID="00"
MAP_NAME="Planet Earth"
GRID_WIDTH=120
GRID_HEIGHT=60
MAX_DEPTH=1000
COORDINATE_SYSTEM="WGS84"
BASE_PROJECTION="mercator"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Logging functions
log_info() { echo -e "${CYAN}🗺️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${BOLD}${BLUE}🌍 $1${NC}"; }

# ═══════════════════════════════════════════════════════════════════════
# TILE GRID SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Generate tile ID from coordinates
generate_tile_id() {
    local lat="$1"
    local lon="$2"
    local depth="${3:-1}"

    # Validate coordinates
    if ! validate_coordinates "$lat" "$lon"; then
        log_error "Invalid coordinates: $lat, $lon"
        return 1
    fi

    # Convert lat/lon to grid coordinates
    local grid_x grid_y
    grid_x=$(lat_lon_to_grid_x "$lon")
    grid_y=$(lat_lon_to_grid_y "$lat")

    # Generate two-letter code
    local letter_code
    letter_code=$(grid_to_letters "$grid_x" "$grid_y")

    # Generate two-digit code
    local digit_code
    digit_code=$(printf "%02d" $((grid_x % 100)))

    # Format: 00 + AA + 99 + depth
    echo "${MAP_ID}${letter_code}${digit_code}-${depth}m"
}

# Convert longitude to grid X coordinate
lat_lon_to_grid_x() {
    local lon="$1"
    # Longitude: -180 to +180 → Grid: 0 to 119
    local grid_x
    grid_x=$(echo "scale=0; ($lon + 180) * $GRID_WIDTH / 360" | bc -l)
    echo "$grid_x"
}

# Convert latitude to grid Y coordinate
lat_lon_to_grid_y() {
    local lat="$1"
    # Latitude: -90 to +90 → Grid: 0 to 59
    local grid_y
    grid_y=$(echo "scale=0; ($lat + 90) * $GRID_HEIGHT / 180" | bc -l)
    echo "$grid_y"
}

# Convert grid coordinates to letter codes
grid_to_letters() {
    local grid_x="$1"
    local grid_y="$2"

    # First letter: A-Z based on longitude bands
    local first_letter_idx=$((grid_x / 5))
    first_letter_idx=$((first_letter_idx % 26))
    local first_letter
    first_letter=$(printf \\$(printf '%03o' $((65 + first_letter_idx))))

    # Second letter: A-Z based on latitude bands
    local second_letter_idx=$((grid_y / 3))
    second_letter_idx=$((second_letter_idx % 26))
    local second_letter
    second_letter=$(printf \\$(printf '%03o' $((65 + second_letter_idx))))

    echo "${first_letter}${second_letter}"
}

# Validate coordinates
validate_coordinates() {
    local lat="$1"
    local lon="$2"

    # Check latitude range: -90 to +90
    if (( $(echo "$lat < -90 || $lat > 90" | bc -l) )); then
        return 1
    fi

    # Check longitude range: -180 to +180
    if (( $(echo "$lon < -180 || $lon > 180" | bc -l) )); then
        return 1
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════
# TILE CREATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Create new tile
create_tile() {
    local lat="$1"
    local lon="$2"
    local depth="${3:-1}"
    local tile_type="${4:-surface}"
    local description="${5:-Automatically generated tile}"

    local tile_id
    tile_id=$(generate_tile_id "$lat" "$lon" "$depth")

    local tile_file="$CORE_MAPS/tiles/${tile_id}.json"

    # Ensure tiles directory exists
    mkdir -p "$(dirname "$tile_file")"

    # Generate tile bounds
    local bounds
    bounds=$(calculate_tile_bounds "$lat" "$lon")

    # Get geographic context
    local geo_context
    geo_context=$(get_geographic_context "$lat" "$lon")

    # Create tile JSON
    cat > "$tile_file" << EOF
{
    "metadata": {
        "tile_id": "$tile_id",
        "map_id": "$MAP_ID",
        "coordinates": {
            "latitude": $lat,
            "longitude": $lon,
            "depth": "${depth}m"
        },
        "bounds": $bounds,
        "type": "$tile_type",
        "description": "$description",
        "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "version": "1.0.0",
        "coordinate_system": "$COORDINATE_SYSTEM",
        "projection": "$BASE_PROJECTION"
    },
    "geography": $geo_context,
    "layers": {
        "surface": {
            "enabled": true,
            "opacity": 1.0,
            "data_sources": [],
            "features": []
        },
        "subsurface": {
            "enabled": $([ "$depth" -gt 1 ] && echo "true" || echo "false"),
            "depth_range": "1m-${depth}m",
            "data_sources": [],
            "features": []
        }
    },
    "temporal": {
        "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "modified": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "accessed": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "version_history": []
    },
    "access_control": {
        "read": ["dev", "wizard", "sorcerer", "ghost", "imp"],
        "write": ["dev", "wizard"],
        "create_derived": ["wizard", "sorcerer"]
    },
    "extensions": {
        "custom_properties": {},
        "external_links": [],
        "related_tiles": []
    }
}
EOF

    # Update tile index
    update_tile_index "$tile_id" "$lat" "$lon" "$depth" "$tile_type"

    log_success "Created tile: $tile_id at ($lat, $lon, ${depth}m)"
    echo "$tile_id"
}

# Calculate tile bounds
calculate_tile_bounds() {
    local center_lat="$1"
    local center_lon="$2"

    # Calculate tile size (degrees)
    local lat_size lon_size
    lat_size=$(echo "scale=6; 180.0 / $GRID_HEIGHT" | bc -l)
    lon_size=$(echo "scale=6; 360.0 / $GRID_WIDTH" | bc -l)

    # Calculate bounds
    local north south east west
    north=$(echo "scale=6; $center_lat + $lat_size / 2" | bc -l)
    south=$(echo "scale=6; $center_lat - $lat_size / 2" | bc -l)
    east=$(echo "scale=6; $center_lon + $lon_size / 2" | bc -l)
    west=$(echo "scale=6; $center_lon - $lon_size / 2" | bc -l)

    cat << EOF
{
    "north": $north,
    "south": $south,
    "east": $east,
    "west": $west,
    "center": {
        "latitude": $center_lat,
        "longitude": $center_lon
    }
}
EOF
}

# Get geographic context for location
get_geographic_context() {
    local lat="$1"
    local lon="$2"

    # Determine hemisphere
    local ns_hemisphere ew_hemisphere
    ns_hemisphere=$([ "$(echo "$lat >= 0" | bc -l)" -eq 1 ] && echo "Northern" || echo "Southern")
    ew_hemisphere=$([ "$(echo "$lon >= 0" | bc -l)" -eq 1 ] && echo "Eastern" || echo "Western")

    # Determine general region
    local continent ocean_basin
    continent=$(determine_continent "$lat" "$lon")
    ocean_basin=$(determine_ocean_basin "$lat" "$lon")

    # Determine climate zone
    local climate_zone
    climate_zone=$(determine_climate_zone "$lat" "$lon")

    cat << EOF
{
    "hemispheres": {
        "north_south": "$ns_hemisphere",
        "east_west": "$ew_hemisphere"
    },
    "continent": "$continent",
    "ocean_basin": "$ocean_basin",
    "climate_zone": "$climate_zone",
    "timezone_estimate": "$(estimate_timezone "$lon")",
    "elevation_estimate": "sea_level",
    "terrain_type": "unknown",
    "population_density": "unknown",
    "land_use": "unknown"
}
EOF
}

# Determine continent from coordinates
determine_continent() {
    local lat="$1"
    local lon="$2"

    # Simplified continent determination
    if (( $(echo "$lon >= -170 && $lon <= -30" | bc -l) )); then
        if (( $(echo "$lat >= 7" | bc -l) )); then
            echo "North America"
        else
            echo "South America"
        fi
    elif (( $(echo "$lon >= -30 && $lon <= 70" | bc -l) )); then
        if (( $(echo "$lat >= 35" | bc -l) )); then
            echo "Europe"
        else
            echo "Africa"
        fi
    elif (( $(echo "$lon >= 70 && $lon <= 170" | bc -l) )); then
        echo "Asia"
    elif (( $(echo "$lon >= 110 && $lon <= 180 && $lat >= -50 && $lat <= -10" | bc -l) )); then
        echo "Oceania"
    elif (( $(echo "$lat <= -60" | bc -l) )); then
        echo "Antarctica"
    else
        echo "Ocean"
    fi
}

# Determine ocean basin
determine_ocean_basin() {
    local lat="$1"
    local lon="$2"

    # Simplified ocean basin determination
    if (( $(echo "$lon >= -170 && $lon <= -30" | bc -l) )); then
        if (( $(echo "$lat >= 0" | bc -l) )); then
            echo "North Atlantic"
        else
            echo "South Atlantic"
        fi
    elif (( $(echo "$lon >= -30 && $lon <= 20" | bc -l) )); then
        echo "Atlantic"
    elif (( $(echo "$lon >= 20 && $lon <= 150" | bc -l) )); then
        echo "Indian Ocean"
    elif (( $(echo "$lon >= 150 || $lon <= -170" | bc -l) )); then
        if (( $(echo "$lat >= 0" | bc -l) )); then
            echo "North Pacific"
        else
            echo "South Pacific"
        fi
    else
        echo "Arctic Ocean"
    fi
}

# Determine climate zone (simplified Köppen)
determine_climate_zone() {
    local lat="$1"
    local lon="$2"

    local abs_lat
    abs_lat=$(echo "${lat#-}" | bc -l)

    if (( $(echo "$abs_lat >= 66.5" | bc -l) )); then
        echo "Polar"
    elif (( $(echo "$abs_lat >= 60" | bc -l) )); then
        echo "Subarctic"
    elif (( $(echo "$abs_lat >= 40" | bc -l) )); then
        echo "Continental"
    elif (( $(echo "$abs_lat >= 30" | bc -l) )); then
        echo "Subtropical"
    elif (( $(echo "$abs_lat >= 23.5" | bc -l) )); then
        echo "Tropical"
    else
        echo "Equatorial"
    fi
}

# Estimate timezone from longitude
estimate_timezone() {
    local lon="$1"
    local utc_offset
    utc_offset=$(echo "scale=1; $lon / 15" | bc -l)

    # Round to nearest hour
    utc_offset=$(echo "scale=0; ($utc_offset + 0.5) / 1" | bc -l)

    if [ "$utc_offset" -eq 0 ]; then
        echo "UTC"
    elif [ "$utc_offset" -gt 0 ]; then
        echo "UTC+$utc_offset"
    else
        echo "UTC$utc_offset"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# TILE INDEX SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Initialize tile index
init_tile_index() {
    local index_file="$CORE_MAPS/tile-index.json"

    if [ ! -f "$index_file" ]; then
        cat > "$index_file" << 'EOF'
{
    "metadata": {
        "map_id": "00",
        "name": "Planet Earth Tile Index",
        "version": "1.0.0",
        "created": null,
        "modified": null,
        "total_tiles": 0,
        "grid_dimensions": {
            "width": 120,
            "height": 60
        }
    },
    "spatial_index": {},
    "tile_registry": {},
    "statistics": {
        "tiles_by_depth": {},
        "tiles_by_type": {},
        "tiles_by_continent": {}
    }
}
EOF
        log_info "Initialized tile index"
    fi
}

# Update tile index
update_tile_index() {
    local tile_id="$1"
    local lat="$2"
    local lon="$3"
    local depth="$4"
    local tile_type="$5"

    local index_file="$CORE_MAPS/tile-index.json"
    local temp_file="$TEMP_DIR/tile-index-temp.json"

    mkdir -p "$TEMP_DIR"

    # Update index using jq
    if command -v jq >/dev/null 2>&1; then
        jq --arg id "$tile_id" \
           --arg lat "$lat" \
           --arg lon "$lon" \
           --arg depth "$depth" \
           --arg type "$tile_type" \
           '.metadata.modified = (now | strftime("%Y-%m-%dT%H:%M:%SZ")) |
            .metadata.total_tiles += 1 |
            .tile_registry[$id] = {
                "coordinates": {
                    "latitude": ($lat | tonumber),
                    "longitude": ($lon | tonumber),
                    "depth": $depth
                },
                "type": $type,
                "created": (now | strftime("%Y-%m-%dT%H:%M:%SZ"))
            } |
            .statistics.tiles_by_depth[$depth] += 1 |
            .statistics.tiles_by_type[$type] += 1' \
           "$index_file" > "$temp_file" && mv "$temp_file" "$index_file"
    else
        log_warning "jq not available - index update skipped"
    fi
}

# Find tiles by coordinates
find_tiles_by_coords() {
    local lat="$1"
    local lon="$2"
    local radius="${3:-0.1}"  # degrees

    local index_file="$CORE_MAPS/tile-index.json"

    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        jq --arg lat "$lat" \
           --arg lon "$lon" \
           --arg radius "$radius" \
           '.tile_registry | to_entries[] | select(
               ((.value.coordinates.latitude - ($lat | tonumber)) | fabs) <= ($radius | tonumber) and
               ((.value.coordinates.longitude - ($lon | tonumber)) | fabs) <= ($radius | tonumber)
           ) | .key' \
           "$index_file" | tr -d '"'
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# SUBSET MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Create MAP-00 subset
create_map_subset() {
    local subset_name="$1"
    local bounds="$2"  # "north,south,east,west"
    local description="$3"
    local subset_type="${4:-regional}"

    local subset_id="${MAP_ID}-${subset_name}"
    local subset_file="$CORE_MAPS/subsets/${subset_id}.json"

    mkdir -p "$(dirname "$subset_file")"

    # Parse bounds
    IFS=',' read -r north south east west <<< "$bounds"

    # Validate bounds
    if ! validate_coordinates "$north" "$east" || ! validate_coordinates "$south" "$west"; then
        log_error "Invalid bounds: $bounds"
        return 1
    fi

    # Find tiles within bounds
    local tiles_in_bounds
    tiles_in_bounds=$(find_tiles_in_bounds "$north" "$south" "$east" "$west")

    cat > "$subset_file" << EOF
{
    "metadata": {
        "subset_id": "$subset_id",
        "parent_map": "$MAP_ID",
        "name": "$subset_name",
        "description": "$description",
        "type": "$subset_type",
        "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "version": "1.0.0"
    },
    "bounds": {
        "north": $north,
        "south": $south,
        "east": $east,
        "west": $west
    },
    "tiles": [
        $tiles_in_bounds
    ],
    "properties": {
        "area_km2": $(calculate_area "$north" "$south" "$east" "$west"),
        "center": {
            "latitude": $(echo "scale=6; ($north + $south) / 2" | bc -l),
            "longitude": $(echo "scale=6; ($east + $west) / 2" | bc -l)
        }
    },
    "access_control": {
        "read": ["dev", "wizard", "sorcerer", "ghost", "imp"],
        "write": ["dev", "wizard"],
        "create_derived": ["wizard", "sorcerer"]
    }
}
EOF

    # Link to uMEMORY/core
    create_memory_link "$subset_id" "$subset_file"

    log_success "Created MAP subset: $subset_id"
    echo "$subset_id"
}

# Find tiles within bounds
find_tiles_in_bounds() {
    local north="$1"
    local south="$2"
    local east="$3"
    local west="$4"

    local index_file="$CORE_MAPS/tile-index.json"

    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        jq --arg north "$north" \
           --arg south "$south" \
           --arg east "$east" \
           --arg west "$west" \
           '.tile_registry | to_entries[] | select(
               .value.coordinates.latitude <= ($north | tonumber) and
               .value.coordinates.latitude >= ($south | tonumber) and
               .value.coordinates.longitude <= ($east | tonumber) and
               .value.coordinates.longitude >= ($west | tonumber)
           ) | "\"" + .key + "\""' \
           "$index_file" | paste -sd ','
    fi
}

# Calculate approximate area
calculate_area() {
    local north="$1"
    local south="$2"
    local east="$3"
    local west="$4"

    # Simplified area calculation (rectangular approximation)
    local lat_diff lon_diff area
    lat_diff=$(echo "scale=6; $north - $south" | bc -l)
    lon_diff=$(echo "scale=6; $east - $west" | bc -l)

    # Convert to approximate km² (very rough)
    area=$(echo "scale=0; $lat_diff * $lon_diff * 12321" | bc -l)
    echo "$area"
}

# ═══════════════════════════════════════════════════════════════════════
# MEMORY LINKING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Create memory link in uMEMORY/core
create_memory_link() {
    local resource_id="$1"
    local source_file="$2"

    local link_file="$UMEMORY/core/${resource_id}.link"

    cat > "$link_file" << EOF
{
    "link_type": "map_resource",
    "resource_id": "$resource_id",
    "source_file": "$source_file",
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "access_method": "file_reference",
    "description": "MAP-00 system resource link"
}
EOF

    log_info "Created memory link: $resource_id"
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  init                    Initialize MAP-00 system"
    echo "  create-tile <lat> <lon> [depth] [type] [description]"
    echo "  find-tile <lat> <lon>   Find tile at coordinates"
    echo "  create-subset <name> <bounds> <description> [type]"
    echo "  list-tiles              List all tiles"
    echo "  stats                   Show system statistics"
    echo "  help                    Show this help"
    echo
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 create-tile 40.7589 -73.9851 1 surface \"Manhattan, NYC\""
    echo "  $0 find-tile 51.5074 -0.1278"
    echo "  $0 create-subset \"Europe\" \"71,35,-25,45\" \"European continent\""
    echo "  $0 list-tiles"
}

# Print header
print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🌍 uMAP Core Engine                        ║"
    echo "║                 Tile Location Mapping System              ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Initialize system
init_system() {
    log_header "Initializing MAP-00 System"

    # Create directories
    mkdir -p "$CORE_MAPS"/{tiles,subsets}
    mkdir -p "$TILE_CACHE"
    mkdir -p "$TEMP_DIR"

    # Initialize tile index
    init_tile_index

    # Update map-00-earth.json with current timestamp
    local map_file="$CORE_MAPS/map-00-earth.json"
    if [ -f "$map_file" ] && command -v jq >/dev/null 2>&1; then
        local temp_file="$TEMP_DIR/map-00-temp.json"
        jq '.metadata.modified = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' \
           "$map_file" > "$temp_file" && mv "$temp_file" "$map_file"
    fi

    log_success "MAP-00 system initialized"
}

# List all tiles
list_tiles() {
    local index_file="$CORE_MAPS/tile-index.json"

    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        echo -e "${BOLD}MAP-00 Tiles:${NC}"
        jq -r '.tile_registry | to_entries[] |
               "\(.key): \(.value.coordinates.latitude), \(.value.coordinates.longitude) (\(.value.type))"' \
               "$index_file"
    else
        log_warning "No tile index found or jq not available"
    fi
}

# Show statistics
show_stats() {
    local index_file="$CORE_MAPS/tile-index.json"

    if [ -f "$index_file" ] && command -v jq >/dev/null 2>&1; then
        echo -e "${BOLD}MAP-00 Statistics:${NC}"
        echo -e "${CYAN}Total Tiles:${NC} $(jq -r '.metadata.total_tiles' "$index_file")"
        echo -e "${CYAN}Last Modified:${NC} $(jq -r '.metadata.modified' "$index_file")"
        echo
        echo -e "${BOLD}Tiles by Type:${NC}"
        jq -r '.statistics.tiles_by_type | to_entries[] | "  \(.key): \(.value)"' "$index_file"
        echo
        echo -e "${BOLD}Tiles by Depth:${NC}"
        jq -r '.statistics.tiles_by_depth | to_entries[] | "  \(.key): \(.value)"' "$index_file"
    else
        log_warning "No statistics available"
    fi
}

# Main command processor
main() {
    case "${1:-help}" in
        init)
            init_system
            ;;
        create-tile)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            create_tile "$2" "$3" "${4:-1}" "${5:-surface}" "${6:-Automatically generated tile}"
            ;;
        find-tile)
            if [ $# -lt 3 ]; then
                log_error "Latitude and longitude required"
                show_usage
                exit 1
            fi
            find_tiles_by_coords "$2" "$3" "${4:-0.1}"
            ;;
        create-subset)
            if [ $# -lt 4 ]; then
                log_error "Name, bounds, and description required"
                show_usage
                exit 1
            fi
            create_map_subset "$2" "$3" "$4" "${5:-regional}"
            ;;
        list-tiles)
            list_tiles
            ;;
        stats)
            show_stats
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
