#!/bin/bash
# uCORE Geographic System Engine v1.0.4.1
# Integrated geographic data processing with uMEMORY/system/geo

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════
# CORE CONFIGURATION & PATHS
# ═══════════════════════════════════════════════════════════════════════

# System paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
GEO_SYSTEM="$SCRIPT_DIR"
GEO_DATA="$UDOS_ROOT/uMEMORY/system/geo"
GEO_CACHE="$SCRIPT_DIR/../cache"

# Ensure required directories exist
mkdir -p "$GEO_CACHE"

# Data directories
MAPS_DATA="$GEO_DATA/maps"
TILES_DATA="$GEO_DATA/tiles"
CULTURAL_DATA="$GEO_DATA/cultural"
DOCS_DATA="$GEO_DATA/documentation"

# System configuration
export UDOS_GEO_VERSION="1.0.4.1"
export UDOS_GEO_ENGINE="geo-core"
export UDOS_GEO_DATA_PATH="$GEO_DATA"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_debug() { echo -e "${CYAN}🔍 $1${NC}"; }

# ═══════════════════════════════════════════════════════════════════════
# DATA VALIDATION & DISCOVERY
# ═══════════════════════════════════════════════════════════════════════

validate_geo_data() {
    log_info "Validating geographic data system..."

    local errors=0

    # Check main data directory
    if [ ! -d "$GEO_DATA" ]; then
        log_error "Geographic data directory not found: $GEO_DATA"
        ((errors++))
    else
        log_success "Geographic data directory found"
    fi

    # Check subdirectories
    for dir in maps tiles cultural documentation; do
        if [ ! -d "$GEO_DATA/$dir" ]; then
            log_warning "Missing data directory: $dir"
            ((errors++))
        else
            file_count=$(find "$GEO_DATA/$dir" -name "*.json" -o -name "*.md" | wc -l)
            log_success "Found $dir directory with $file_count files"
        fi
    done

    # Check for key datasets
    local key_files=(
        "$MAPS_DATA/uDATA-E7172B38-Global-Geographic-Master.json"
        "$CULTURAL_DATA/uDATA-E7172940-Cultural-Reference.json"
        "$MAPS_DATA/uDATA-uMAP-00MK60-Earth.json"
    )

    for file in "${key_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Key dataset found: $(basename "$file")"
        else
            log_error "Missing key dataset: $(basename "$file")"
            ((errors++))
        fi
    done

    if [ $errors -eq 0 ]; then
        log_success "Geographic data validation complete - all systems ready"
        return 0
    else
        log_error "Geographic data validation failed with $errors errors"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# MAP & TILE DATA PROCESSING
# ═══════════════════════════════════════════════════════════════════════

load_map_data() {
    local map_id="$1"
    local map_file=""

    log_debug "Loading map data for ID: $map_id"

    # Find the map file with wildcard matching
    map_file=$(ls "$MAPS_DATA/uDATA-uMAP-${map_id}"-*.json 2>/dev/null | head -1)

    if [ -n "$map_file" ] && [ -f "$map_file" ]; then
        log_success "Map loaded: $(basename "$map_file")"
        echo "$map_file"
        return 0
    else
        log_error "Map not found for ID: $map_id"
        return 1
    fi
}

load_tile_data() {
    local tile_id="$1"
    local tile_file=""

    log_debug "Loading tile data for ID: $tile_id"

    # Find the tile file with wildcard matching
    tile_file=$(ls "$TILES_DATA/uDATA-uTILE-${tile_id}"-*.json 2>/dev/null | head -1)

    if [ -n "$tile_file" ] && [ -f "$tile_file" ]; then
        log_success "Tile loaded: $(basename "$tile_file")"
        echo "$tile_file"
        return 0
    else
        log_error "Tile not found for ID: $tile_id"
        return 1
    fi
}

get_global_master_data() {
    local master_file="$MAPS_DATA/uDATA-E7172B38-Global-Geographic-Master.json"

    if [ -f "$master_file" ]; then
        log_success "Global geographic master data loaded" >&2
        echo "$master_file"
        return 0
    else
        log_error "Global geographic master data not found" >&2
        return 1
    fi
}

get_cultural_data() {
    local cultural_file="$CULTURAL_DATA/uDATA-E7172940-Cultural-Reference.json"

    if [ -f "$cultural_file" ]; then
        log_success "Cultural reference data loaded" >&2
        echo "$cultural_file"
        return 0
    else
        log_error "Cultural reference data not found" >&2
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# GEOGRAPHIC QUERIES & OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

query_cities() {
    local region="${1:-all}"
    local master_file

    if ! master_file=$(get_global_master_data); then
        return 1
    fi

    log_info "Querying cities for region: $region"

    if [ "$region" = "all" ]; then
        MASTER_FILE="$master_file" python3 - << 'EOF'
import json
import sys
import os

master_file = os.environ.get('MASTER_FILE')
try:
    with open(master_file, 'r') as f:
        data = json.load(f)
    cities = data.get('cities', [])
    print(f"Found {len(cities)} cities worldwide")
    for city in cities[:10]:  # Show first 10
        print(f"  • {city['city']}, {city['country']} ({city['tile']})")
    if len(cities) > 10:
        print(f"  ... and {len(cities) - 10} more cities")
except Exception as e:
    print(f"Error querying cities: {e}")
EOF
    else
        MASTER_FILE="$master_file" REGION="$region" python3 - << 'EOF'
import json
import sys
import os

master_file = os.environ.get('MASTER_FILE')
region = os.environ.get('REGION')
try:
    with open(master_file, 'r') as f:
        data = json.load(f)
    cities = data.get('cities', [])
    region_cities = [city for city in cities if city.get('region', '').lower() == region.lower()]
    print(f"Found {len(region_cities)} cities in {region}")
    for city in region_cities:
        print(f"  • {city['city']}, {city['country']} ({city['tile']})")
except Exception as e:
    print(f"Error querying cities: {e}")
EOF
    fi
}

query_currencies() {
    local cultural_file

    if ! cultural_file=$(get_cultural_data); then
        return 1
    fi

    log_info "Querying currency data"

    python3 << EOF
import json
try:
    with open('$cultural_file', 'r') as f:
        data = json.load(f)
    currencies = data.get('currencies', [])
    print(f"Found {len(currencies)} currencies")
    for currency in currencies[:15]:  # Show first 15
        print(f"  • {currency['code']} - {currency['name']} ({currency['symbol']})")
    if len(currencies) > 15:
        print(f"  ... and {len(currencies) - 15} more currencies")
except Exception as e:
    print(f"Error querying currencies: {e}")
EOF
}

query_languages() {
    local cultural_file

    if ! cultural_file=$(get_cultural_data); then
        return 1
    fi

    log_info "Querying language data"

    python3 << EOF
import json
try:
    with open('$cultural_file', 'r') as f:
        data = json.load(f)
    languages = data.get('languages', [])
    print(f"Found {len(languages)} languages")
    for language in languages[:15]:  # Show first 15
        speakers = language.get('speakers', 0)
        if speakers > 1000000:
            speakers_str = f"{speakers // 1000000}M speakers"
        else:
            speakers_str = f"{speakers} speakers"
        print(f"  • {language['name']} ({language['code']}) - {speakers_str}")
    if len(languages) > 15:
        print(f"  ... and {len(languages) - 15} more languages")
except Exception as e:
    print(f"Error querying languages: {e}")
EOF
}

list_available_maps() {
    log_info "Available continental and regional maps:"

    if [ -d "$MAPS_DATA" ]; then
        for map_file in "$MAPS_DATA"/uDATA-uMAP-*.json; do
            if [ -f "$map_file" ]; then
                map_name=$(python3 -c "
import json
try:
    with open('$map_file', 'r') as f:
        data = json.load(f)
    metadata = data.get('metadata', {})
    print(metadata.get('name', 'Unknown Map'))
except:
    print('$(basename "$map_file" .json)')"
                )
                map_id=$(basename "$map_file" | sed 's/uDATA-uMAP-//' | sed 's/-.*//')
                echo "  📍 $map_id - $map_name"
            fi
        done
    fi
}

list_available_tiles() {
    log_info "Available metropolitan tiles:"

    if [ -d "$TILES_DATA" ]; then
        local count=0
        for tile_file in "$TILES_DATA"/uDATA-uTILE-*.json; do
            if [ -f "$tile_file" ] && [ $count -lt 15 ]; then
                tile_name=$(python3 -c "
import json
try:
    with open('$tile_file', 'r') as f:
        data = json.load(f)
    metadata = data.get('metadata', {})
    print(metadata.get('name', 'Unknown Tile'))
except:
    print('$(basename "$tile_file" .json)')"
                )
                tile_id=$(basename "$tile_file" | sed 's/uDATA-uTILE-//' | sed 's/-.*//')
                echo "  🗺️  $tile_id - $tile_name"
                ((count++))
            fi
        done

        total_tiles=$(find "$TILES_DATA" -name "uDATA-uTILE-*.json" | wc -l)
        if [ $total_tiles -gt 15 ]; then
            echo "  ... and $((total_tiles - 15)) more tiles"
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# SYSTEM STATUS & INFORMATION
# ═══════════════════════════════════════════════════════════════════════

show_system_status() {
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    echo -e "${PURPLE}🌍 uDOS Geographic System Status v1.0.4.1${NC}"
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    echo ""

    # System information
    echo -e "${CYAN}📊 System Information:${NC}"
    echo "   Version: $UDOS_GEO_VERSION"
    echo "   Engine: $UDOS_GEO_ENGINE"
    echo "   Data Path: $UDOS_GEO_DATA_PATH"
    echo ""

    # Data statistics
    echo -e "${CYAN}📈 Data Statistics:${NC}"
    if [ -d "$MAPS_DATA" ]; then
        map_count=$(find "$MAPS_DATA" -name "*.json" | wc -l)
        echo "   Maps: $map_count continental/regional datasets"
    fi

    if [ -d "$TILES_DATA" ]; then
        tile_count=$(find "$TILES_DATA" -name "*.json" | wc -l)
        echo "   Tiles: $tile_count metropolitan areas"
    fi

    if [ -d "$CULTURAL_DATA" ]; then
        cultural_count=$(find "$CULTURAL_DATA" -name "*.json" | wc -l)
        echo "   Cultural: $cultural_count reference datasets"
    fi

    echo ""

    # System health
    echo -e "${CYAN}🏥 System Health:${NC}"
    if validate_geo_data >/dev/null 2>&1; then
        echo "   Status: ✅ All systems operational"
    else
        echo "   Status: ⚠️  Some issues detected"
    fi

    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

show_help() {
    echo -e "${BLUE}uDOS Geographic System Engine v1.0.4.1${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  status              Show system status and statistics"
    echo "  validate            Validate geographic data integrity"
    echo "  cities [region]     Query cities (all, or by region)"
    echo "  currencies          List available currencies"
    echo "  languages           List available languages"
    echo "  maps                List available maps"
    echo "  tiles               List available tiles"
    echo "  load-map <id>       Load specific map by ID"
    echo "  load-tile <id>      Load specific tile by ID"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 cities europe"
    echo "  $0 load-map 00MK60"
    echo "  $0 load-tile 00EN20"
    echo ""
    echo "Data Integration:"
    echo "  Geographic data: $GEO_DATA"
    echo "  Maps: $MAPS_DATA"
    echo "  Tiles: $TILES_DATA"
    echo "  Cultural: $CULTURAL_DATA"
    echo ""
}

main() {
    local command="${1:-help}"

    case "$command" in
        "status")
            show_system_status
            ;;
        "validate")
            validate_geo_data
            ;;
        "cities")
            query_cities "${2:-all}"
            ;;
        "currencies")
            query_currencies
            ;;
        "languages")
            query_languages
            ;;
        "maps")
            list_available_maps
            ;;
        "tiles")
            list_available_tiles
            ;;
        "load-map")
            if [ -n "${2:-}" ]; then
                load_map_data "$2"
            else
                log_error "Map ID required. Usage: $0 load-map <id>"
                return 1
            fi
            ;;
        "load-tile")
            if [ -n "${2:-}" ]; then
                load_tile_data "$2"
            else
                log_error "Tile ID required. Usage: $0 load-tile <id>"
                return 1
            fi
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
