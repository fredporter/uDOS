#!/bin/bash
# user-memory-manager.sh - Master User Memory Management System
# Integrates all user memory components: moves, missions, milestones, legacy, installation

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
USER_DATA_DIR="$UDOS_ROOT/uMEMORY/user"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

# Component scripts
MOVE_LOGGER="$SCRIPT_DIR/user-move-logger.sh"
MISSION_MANAGER="$SCRIPT_DIR/mission-manager.sh"
LIFESPAN_MANAGER="$SCRIPT_DIR/installation-lifespan.sh"

# Initialize complete user memory system
init_user_memory_system() {
    echo -e "${WHITE}🧠 Initializing uDOS User Memory System${NC}"
    echo -e "${WHITE}═══════════════════════════════════════${NC}"
    echo ""
    
    # Initialize move logging
    if [[ -f "$MOVE_LOGGER" ]]; then
        echo -e "${CYAN}📍 Initializing Move Logging System...${NC}"
        "$MOVE_LOGGER" init
        echo ""
    fi
    
    # Initialize installation lifespan
    if [[ -f "$LIFESPAN_MANAGER" ]]; then
        echo -e "${PURPLE}⏳ Initializing Installation Lifespan...${NC}"
        "$LIFESPAN_MANAGER" init wizard full
        echo ""
    fi
    
    # Create welcome mission
    if [[ -f "$MISSION_MANAGER" ]]; then
        echo -e "${BLUE}🎯 Creating Welcome Mission...${NC}"
        "$MISSION_MANAGER" create "Welcome to uDOS" tutorial high
        echo ""
    fi
    
    # Log initialization
    if [[ -f "$MOVE_LOGGER" ]]; then
        "$MOVE_LOGGER" log "system_initialization" "User memory system initialized" "uMEMORY/user/" "Complete system setup"
    fi
    
    echo -e "${GREEN}✅ User Memory System Initialization Complete${NC}"
    echo ""
    show_system_overview
}

# Show comprehensive system overview
show_system_overview() {
    echo -e "${WHITE}🧠 uDOS User Memory System Overview${NC}"
    echo -e "${WHITE}═══════════════════════════════════════${NC}"
    echo ""
    
    # Directory status
    echo -e "${CYAN}📁 Directory Structure:${NC}"
    echo "- /moves/      $(ls -1 "$USER_DATA_DIR/moves" 2>/dev/null | wc -l | tr -d ' ') files"
    echo "- /missions/   $(ls -1 "$USER_DATA_DIR/missions" 2>/dev/null | wc -l | tr -d ' ') files"
    echo "- /milestones/ $(ls -1 "$USER_DATA_DIR/milestones" 2>/dev/null | wc -l | tr -d ' ') files"
    echo "- /legacy/     $(ls -1 "$USER_DATA_DIR/legacy" 2>/dev/null | wc -l | tr -d ' ') files"
    echo "- /explicit/   $(ls -1 "$USER_DATA_DIR/explicit" 2>/dev/null | wc -l | tr -d ' ') files"
    echo ""
    
    # Installation status
    if [[ -f "$LIFESPAN_MANAGER" ]]; then
        echo -e "${PURPLE}⏳ Installation Status:${NC}"
        "$LIFESPAN_MANAGER" status | grep -E "(User Role|Current Phase|Lifespan|Days Remaining)" || echo "Not initialized"
        echo ""
    fi
    
    # Mission status
    if [[ -f "$MISSION_MANAGER" ]]; then
        echo -e "${BLUE}🎯 Mission Status:${NC}"
        "$MISSION_MANAGER" dashboard | grep -E "(Active Missions|Completed Missions|Total Milestones)" || echo "No missions found"
        echo ""
    fi
    
    # Move logging status
    if [[ -f "$MOVE_LOGGER" ]]; then
        echo -e "${CYAN}📍 Move Tracking:${NC}"
        "$MOVE_LOGGER" stats | grep -E "(Today's Moves|Session Log)" || echo "Not initialized"
        echo ""
    fi
    
    # Integration with core systems
    echo -e "${YELLOW}🔗 Core System Integration:${NC}"
    local core_session_log="$UDOS_ROOT/uMEMORY/system/session-moves.json"
    if [[ -f "$core_session_log" ]]; then
        local core_moves=$(jq '.moves | length' "$core_session_log" 2>/dev/null || echo 0)
        echo "- Core session moves: $core_moves"
    else
        echo "- Core session moves: Not available"
    fi
    
    local installation_log="$UDOS_ROOT/uMEMORY/system/installation-lifespan.json"
    if [[ -f "$installation_log" ]]; then
        echo "- Installation tracking: Active"
    else
        echo "- Installation tracking: Not initialized"
    fi
    echo ""
}

# Quick mission creation
quick_mission() {
    local mission_name="$1"
    local mission_type="${2:-general}"
    
    if [[ -z "$mission_name" ]]; then
        echo -e "${RED}[ERROR]${NC} Mission name required"
        echo "Usage: $0 mission <name> [type]"
        return 1
    fi
    
    if [[ -f "$MISSION_MANAGER" ]]; then
        "$MISSION_MANAGER" create "$mission_name" "$mission_type" medium
    else
        echo -e "${RED}[ERROR]${NC} Mission manager not available"
    fi
}

# Quick milestone creation
quick_milestone() {
    local milestone_name="$1"
    local description="${2:-Achievement unlocked}"
    
    if [[ -z "$milestone_name" ]]; then
        echo -e "${RED}[ERROR]${NC} Milestone name required"
        echo "Usage: $0 milestone <name> [description]"
        return 1
    fi
    
    if [[ -f "$MISSION_MANAGER" ]]; then
        "$MISSION_MANAGER" milestone "$milestone_name" achievement "$description"
    else
        echo -e "${RED}[ERROR]${NC} Mission manager not available"
    fi
}

# Log user move
quick_move() {
    local move_type="$1"
    local description="$2"
    local location="${3:-uMEMORY/user/}"
    
    if [[ -z "$move_type" || -z "$description" ]]; then
        echo -e "${RED}[ERROR]${NC} Move type and description required"
        echo "Usage: $0 move <type> <description> [location]"
        return 1
    fi
    
    if [[ -f "$MOVE_LOGGER" ]]; then
        "$MOVE_LOGGER" log "$move_type" "$description" "$location"
    else
        echo -e "${RED}[ERROR]${NC} Move logger not available"
    fi
}

# Generate uHEX code
generate_uhex() {
    openssl rand -hex 4 | tr '[:lower:]' '[:upper:]' 2>/dev/null || printf "%08X" $((RANDOM * RANDOM))
}

# Create legacy archive
create_legacy_archive() {
    local archive_name="$1"
    local source_path="$2"
    
    if [[ -z "$archive_name" || -z "$source_path" ]]; then
        echo -e "${RED}[ERROR]${NC} Archive name and source path required"
        echo "Usage: $0 legacy <name> <source_path>"
        return 1
    fi
    
    local legacy_dir="$USER_DATA_DIR/legacy"
    local uhex_code=$(generate_uhex)
    local archive_file="$legacy_dir/uDOC-${uhex_code}-${archive_name//[^a-zA-Z0-9]/-}.md"
    
    echo -e "${CYAN}[LEGACY]${NC} Creating legacy archive: $archive_name"
    
    cat > "$archive_file" << EOF
---
archive_name: "$archive_name"
source_path: "$source_path"
archived: $(date -Iseconds)
archive_type: user_legacy
archived_by: $(whoami)
original_size: $(du -sh "$source_path" 2>/dev/null | cut -f1 || echo "unknown")
---

# Legacy Archive: $archive_name

## Archive Information
- **Source**: $source_path
- **Archived**: $(date)
- **Type**: User Legacy Archive
- **Archived By**: $(whoami)

## Original Content Description


## Archive Reason


## Restoration Notes


## Related Items


---
*Archived by uDOS User Memory Manager v1.0*
EOF
    
    echo -e "${GREEN}[LEGACY]${NC} Legacy archive created: $archive_file"
    
    # Log the legacy creation
    if [[ -f "$MOVE_LOGGER" ]]; then
        "$MOVE_LOGGER" log "legacy_creation" "Created legacy archive: $archive_name" "legacy/" "Source: $source_path"
    fi
}

# Generate comprehensive report
generate_report() {
    local uhex_code=$(generate_uhex)
    local report_file="$USER_DATA_DIR/uDOC-${uhex_code}-user-memory-report-$(date +%Y%m%d).md"
    
    echo -e "${CYAN}[REPORT]${NC} Generating comprehensive user memory report"
    
    cat > "$report_file" << EOF
# uDOS User Memory System Report
*Generated: $(date)*

## System Overview

$(show_system_overview)

## Detailed Status

### Move Logging
$(if [[ -f "$MOVE_LOGGER" ]]; then "$MOVE_LOGGER" stats; else echo "Not available"; fi)

### Mission Management
$(if [[ -f "$MISSION_MANAGER" ]]; then "$MISSION_MANAGER" dashboard; else echo "Not available"; fi)

### Installation Lifespan
$(if [[ -f "$LIFESPAN_MANAGER" ]]; then "$LIFESPAN_MANAGER" status; else echo "Not available"; fi)

## File Inventory

### Moves Directory
$(ls -la "$USER_DATA_DIR/moves/" 2>/dev/null || echo "Empty or not found")

### Missions Directory
$(ls -la "$USER_DATA_DIR/missions/" 2>/dev/null || echo "Empty or not found")

### Milestones Directory
$(ls -la "$USER_DATA_DIR/milestones/" 2>/dev/null || echo "Empty or not found")

### Legacy Directory
$(ls -la "$USER_DATA_DIR/legacy/" 2>/dev/null || echo "Empty or not found")

---
*Report generated by uDOS User Memory Manager v1.0*
EOF
    
    echo -e "${GREEN}[REPORT]${NC} Report created: $report_file"
}

# Maintenance operations
perform_maintenance() {
    echo -e "${CYAN}[MAINTENANCE]${NC} Performing user memory system maintenance"
    
    # Generate daily summaries
    if [[ -f "$MOVE_LOGGER" ]]; then
        "$MOVE_LOGGER" summary
    fi
    
    # Update installation lifespan
    if [[ -f "$LIFESPAN_MANAGER" ]]; then
        "$LIFESPAN_MANAGER" maintenance routine "Daily maintenance of user memory system"
    fi
    
    # Clean up old temporary files
    find "$USER_DATA_DIR" -name "*.tmp" -mtime +7 -delete 2>/dev/null || true
    
    echo -e "${GREEN}[MAINTENANCE]${NC} Maintenance completed"
}

# Main function
main() {
    case "${1:-help}" in
        "init")
            init_user_memory_system
            ;;
        "overview"|"status")
            show_system_overview
            ;;
        "mission")
            quick_mission "$2" "$3"
            ;;
        "milestone")
            quick_milestone "$2" "$3"
            ;;
        "move")
            quick_move "$2" "$3" "$4"
            ;;
        "legacy")
            create_legacy_archive "$2" "$3"
            ;;
        "report")
            generate_report
            ;;
        "maintenance")
            perform_maintenance
            ;;
        "help"|*)
            echo -e "${WHITE}uDOS User Memory Manager v1.0${NC}"
            echo "Usage: $0 {init|overview|mission|milestone|move|legacy|report|maintenance|help}"
            echo ""
            echo -e "${YELLOW}Commands:${NC}"
            echo "  init                              Initialize complete user memory system"
            echo "  overview                          Show system overview and status"
            echo "  mission <name> [type]             Create quick mission"
            echo "  milestone <name> [description]    Create quick milestone"
            echo "  move <type> <description> [loc]   Log user move"
            echo "  legacy <name> <source_path>       Create legacy archive"
            echo "  report                            Generate comprehensive report"
            echo "  maintenance                       Perform system maintenance"
            echo "  help                              Show this help"
            echo ""
            echo -e "${YELLOW}Examples:${NC}"
            echo "  $0 init"
            echo "  $0 mission 'Learn uScript' learning"
            echo "  $0 milestone 'First Script' 'Created first uScript template'"
            echo "  $0 move navigation 'Opened VS Code' 'wizard/vscode/'"
            echo "  $0 legacy 'Old Projects' '/path/to/old/projects'"
            echo "  $0 overview"
            echo ""
            echo -e "${CYAN}Component Scripts:${NC}"
            echo "  Move Logger:       $MOVE_LOGGER"
            echo "  Mission Manager:   $MISSION_MANAGER"
            echo "  Lifespan Manager:  $LIFESPAN_MANAGER"
            ;;
    esac
}

# Run main function
main "$@"
