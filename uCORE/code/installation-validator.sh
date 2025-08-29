#!/bin/bash

# uDOS Installation Validation System
# Validates uMEMORY/installation.md and repairs if needed

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Installation file path
INSTALL_FILE="$UDOS_ROOT/uMEMORY/installation.md"
VERSION_FILE="$UDOS_ROOT/VERSION"

# Generate installation ID
generate_install_id() {
    local date_part
    date_part=$(date +%Y%m%d)
    local random_part
    random_part=$(printf "%04d" $((RANDOM % 10000)))
    echo "uDOS-${date_part}-${random_part}"
}

# Detect platform
detect_platform() {
    local platform
    platform=$(uname -s)
    local arch
    arch=$(uname -m)
    echo "$platform ($arch)"
}

# Get current version
get_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        grep '^VERSION=' "$VERSION_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d '\n\r' || echo "v1.0.5.1"
    else
        echo "v1.0.5.1"
    fi
}

# Validate installation.md format
validate_install_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Installation file missing: $file${NC}"
        return 1
    fi
    
    # Check required fields in key=value format
    local required_fields=("INSTALL_ID" "VERSION" "TYPE" "CREATED" "PLATFORM")
    local missing_fields=()
    
    for field in "${required_fields[@]}"; do
        if ! grep -q "^${field}=" "$file"; then
            missing_fields+=("$field")
        fi
    done
    
    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        echo -e "${RED}❌ Missing required fields: ${missing_fields[*]}${NC}"
        return 1
    fi
    
    # Validate Installation ID format
    local install_id
    install_id=$(grep "^INSTALL_ID=" "$file" | cut -d'=' -f2)
    
    if [[ ! "$install_id" =~ ^uDOS-[0-9]{8}-[0-9]{4}$ ]]; then
        echo -e "${RED}❌ Invalid Installation ID format: $install_id${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Installation file format valid${NC}"
    return 0
}

# Extract installation data
get_install_data() {
    local file="$1"
    local field="$2"
    
    grep "^${field}=" "$file" 2>/dev/null | cut -d'=' -f2 || echo ""
}

# Create installation.md
create_install_file() {
    local file="$1"
    local install_id
    install_id=$(generate_install_id)
    local platform
    platform=$(detect_platform)
    local version
    version=$(get_version)
    local created
    created=$(date -Iseconds)
    
    echo -e "${BLUE}🔧 Creating installation profile...${NC}"
    
    mkdir -p "$(dirname "$file")"
    
    cat > "$file" << EOF
INSTALL_ID=$install_id
VERSION=$version
TYPE=enterprise-dev
CREATED=$created
UPDATED=$created
PLATFORM=$platform
STATUS=Active
MODE=enterprise-dev
SECURITY=enterprise-dev
MULTI_USER=true
DEFAULT_ROLE=KNIGHT
NETWORK_MODE=public
SHARING_ENABLED=true
REMOTE_ACCESS=true
DEV_SERVER=true
FEATURES=Toast,Browser,Terminal,Session
EOF

    echo -e "${GREEN}✅ Installation profile created: $install_id${NC}"
    echo -e "${BLUE}📁 File: $file${NC}"
}

# Show installation info
show_install_info() {
    local file="$1"
    
    echo "🏗️ uDOS Installation Information"
    echo "════════════════════════════════════════════════════════════"
    echo "Installation ID: $(get_install_data "$file" "INSTALL_ID")"
    echo "Version:         $(get_install_data "$file" "VERSION")"
    echo "Type:            $(get_install_data "$file" "TYPE")"
    echo "Platform:        $(get_install_data "$file" "PLATFORM")"
    echo "Created:         $(get_install_data "$file" "CREATED")"
    echo "Updated:         $(get_install_data "$file" "UPDATED")"
    echo ""
}

# Main function
main() {
    local action="${1:-validate}"
    
    case "$action" in
        "validate")
            echo "🔍 Validating installation configuration..."
            if validate_install_file "$INSTALL_FILE"; then
                show_install_info "$INSTALL_FILE"
                return 0
            else
                echo ""
                echo "🚨 Installation configuration invalid or missing"
                echo "🔧 Auto-repairing installation profile..."
                create_install_file "$INSTALL_FILE"
                return 0
            fi
            ;;
        "repair")
            echo "🔧 Repairing installation configuration..."
            create_install_file "$INSTALL_FILE"
            ;;
        "info")
            if validate_install_file "$INSTALL_FILE"; then
                show_install_info "$INSTALL_FILE"
            else
                echo "❌ Installation file invalid or missing"
                return 1
            fi
            ;;
        "help")
            echo "uDOS Installation Validation System"
            echo ""
            echo "Usage: $0 [action]"
            echo ""
            echo "Actions:"
            echo "  validate  - Validate installation.md format (default)"
            echo "  repair    - Force repair/recreate installation.md"
            echo "  info      - Show installation information"
            echo "  help      - Show this help"
            ;;
        *)
            echo "❌ Unknown action: $action"
            echo "Use '$0 help' for available actions"
            return 1
            ;;
    esac
}

# Run main function
main "$@"
