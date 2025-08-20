#!/bin/bash
# uDOS Shortcode Management Module v1.3
# Advanced shortcode browser, execution engine, and builder system

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Rainbow colors for special shortcodes
RAINBOW_RED='\033[1;31m'
RAINBOW_YELLOW='\033[1;33m'
RAINBOW_GREEN='\033[1;32m'
RAINBOW_CYAN='\033[1;36m'
RAINBOW_BLUE='\033[1;34m'
RAINBOW_PURPLE='\033[1;35m'

# Shortcode categories
CATEGORIES=("memory" "mission" "package" "log" "dash" "editor" "games" "system" "all")

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Browse shortcodes by category
browse_shortcodes() {
    local category="${1:-all}"
    
    echo -e "\n${YELLOW}🔧 Shortcode Browser${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case "$category" in
        memory|MEMORY)
            echo -e "${CYAN}🧠 MEMORY SHORTCUTS:${NC}"
            echo "  [MEM|LIST] - LIST ALL MEMORY FILES"
            echo "  [MEM|VIEW|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - VIEW SPECIFIC FILE"
            echo "  [MEM|SEARCH|TERM] - SEARCH MEMORY"
            echo "  [MEM|EDIT|FILE-YYYYMMDD-LOCATION-HHMMSS.md] - EDIT MEMORY FILE"
            echo "  [MEM|CREATE|TOPIC] - CREATE NEW MEMORY FILE"
            echo "  [MEM|RECENT] - SHOW RECENT MEMORY FILES"
            ;;
        mission|MISSION)
            echo -e "${PURPLE}🎯 MISSION SHORTCUTS:${NC}"
            echo "  [MISSION|LIST] - LIST ALL MISSIONS"
            echo "  [MISSION|CREATE|NAME] - CREATE NEW MISSION"
            echo "  [MISSION|COMPLETE|NAME] - COMPLETE MISSION"
            echo "  [MISSION|EDIT|NAME] - EDIT EXISTING MISSION"
            echo "  [MISSION|STATUS] - SHOW MISSION STATUS"
            echo "  [MISSION|ARCHIVE] - ARCHIVE COMPLETED MISSIONS"
            ;;
        package|PACKAGE)
            echo -e "${GREEN}📦 PACKAGE SHORTCUTS:${NC}"
            echo "  [PACK|LIST] - SHOW AVAILABLE PACKAGES"
            echo "  [PACK|INSTALL|NAME] - INSTALL PACKAGE"
            echo "  [PACK|INFO|NAME] - PACKAGE INFORMATION"
            echo "  [PACK|UPDATE|NAME] - UPDATE PACKAGE"
            echo "  [PACK|REMOVE|NAME] - REMOVE PACKAGE"
            echo "  [PACK|SEARCH|TERM] - SEARCH PACKAGES"
            ;;
        log|LOG)
            echo -e "${YELLOW}📝 LOGGING SHORTCUTS:${NC}"
            echo "  [LOG|REPORT] - GENERATE DAILY REPORT"
            echo "  [LOG|STATS] - SHOW STATISTICS"
            echo "  [LOG|MOVE|COMMAND] - LOG A COMMAND"
            echo "  [LOG|SESSION] - LOG SESSION ACTIVITY"
            echo "  [LOG|ERROR] - VIEW ERROR LOGS"
            echo "  [LOG|CLEAR] - CLEAR OLD LOGS"
            ;;
        dash|DASH)
            echo -e "${BLUE}📊 DASHBOARD SHORTCUTS:${NC}"
            echo "  [DASH|LIVE] - LIVE DASHBOARD MODE"
            echo "  [DASH|MEMORY] - MEMORY USAGE DASHBOARD"
            echo "  [DASH|SYSTEM] - SYSTEM STATUS DASHBOARD"
            echo "  [DASH|PROJECT] - PROJECT OVERVIEW DASHBOARD"
            echo "  [DASH|CUSTOM|NAME] - CUSTOM DASHBOARD"
            ;;
        editor|EDITOR)
            echo -e "${RAINBOW_GREEN}📝 EDITOR INTEGRATION:${NC}"
            echo "  [EDIT|MARKDOWN|FILE] - OPEN MARKDOWN IN EDITOR"
            echo "  [EDIT|USCRIPT|FILE] - OPEN USCRIPT IN EDITOR"
            echo "  [EDIT|CONFIG] - EDIT SYSTEM CONFIGURATION"
            echo "  [NEW|MARKDOWN] - CREATE NEW MARKDOWN FILE"
            echo "  [NEW|USCRIPT] - CREATE NEW USCRIPT FILE"
            echo ""
            echo -e "${RAINBOW_GREEN}🌐 WEB EDITOR:${NC}"
            echo "  [WEB|EDIT|file.md] - EDIT MARKDOWN IN WEB BROWSER"
            echo "  [WEB|SERVER] - START WEB EDITOR SERVER"
            echo "  [WEB|NEW|filename] - CREATE NEW FILE IN WEB EDITOR"
            echo ""
            echo -e "${RAINBOW_GREEN}🎨 ASCII ART GENERATION:${NC}"
            echo "  [ASCII|TEXT|Hello World] - GENERATE ASCII TEXT"
            echo "  [ASCII|LOGO|uDOS] - GENERATE SYSTEM LOGO"
            echo "  [ASCII|BANNER|Title|Subtitle] - GENERATE BANNER"
            echo "  [ASCII|IMAGE|path/to/image.jpg] - CONVERT IMAGE TO ASCII"
            ;;
        games|GAMES)
            echo -e "${RAINBOW_PURPLE}🎮 GAMES & ENTERTAINMENT:${NC}"
            echo "  [GAME|ADVENTURE] - START TEXT ADVENTURE"
            echo "  [GAME|PUZZLE] - PUZZLE CHALLENGES"
            echo "  [GAME|TRIVIA] - uDOS TRIVIA GAME"
            echo "  [GAME|SCORES] - VIEW HIGH SCORES"
            echo "  [GAME|HELP] - GAME HELP AND TUTORIALS"
            ;;
        system|SYSTEM)
            echo -e "${RAINBOW_CYAN}⚙️ SYSTEM SHORTCUTS:${NC}"
            echo "  [SYS|INFO] - SYSTEM INFORMATION"
            echo "  [SYS|BACKUP] - SYSTEM BACKUP"
            echo "  [SYS|RESTORE] - SYSTEM RESTORE"
            echo "  [SYS|UPDATE] - SYSTEM UPDATE"
            echo "  [SYS|CLEANUP] - SYSTEM CLEANUP"
            echo "  [SYS|RESET] - SYSTEM RESET"
            ;;
        all|*)
            echo -e "${BOLD}📋 All Available Shortcode Categories:${NC}"
            echo ""
            browse_shortcodes "memory"
            echo ""
            browse_shortcodes "mission"
            echo ""
            browse_shortcodes "package"
            echo ""
            browse_shortcodes "log"
            echo ""
            browse_shortcodes "dash"
            echo ""
            browse_shortcodes "editor"
            echo ""
            browse_shortcodes "games"
            echo ""
            browse_shortcodes "system"
            ;;
    esac
    
    echo ""
    echo -e "${BOLD}Usage:${NC} Type shortcode exactly as shown, e.g., ${CYAN}[MEM|LIST]${NC}"
    echo -e "${BOLD}Help:${NC} Use ${CYAN}shortcode help${NC} for more information"
}

# Execute a shortcode
execute_shortcode() {
    local shortcode="$1"
    
    # Remove brackets if present
    shortcode=$(echo "$shortcode" | sed 's/^\[//; s/\]$//')
    
    # Split shortcode into components
    IFS='|' read -ra PARTS <<< "$shortcode"
    local category="${PARTS[0]:-}"
    local action="${PARTS[1]:-}"
    local param="${PARTS[2]:-}"
    local param2="${PARTS[3]:-}"
    
    log_info "Executing shortcode: [$shortcode]"
    
    case "$category" in
        MEM|MEMORY)
            execute_memory_shortcode "$action" "$param" "$param2"
            ;;
        MISSION)
            execute_mission_shortcode "$action" "$param" "$param2"
            ;;
        PACK|PACKAGE)
            execute_package_shortcode "$action" "$param" "$param2"
            ;;
        LOG)
            execute_log_shortcode "$action" "$param" "$param2"
            ;;
        DASH|DASHBOARD)
            execute_dash_shortcode "$action" "$param" "$param2"
            ;;
        EDIT|EDITOR|NEW)
            execute_editor_shortcode "$category" "$action" "$param"
            ;;
        WEB)
            execute_web_shortcode "$action" "$param" "$param2"
            ;;
        ASCII)
            execute_ascii_shortcode "$action" "$param" "$param2"
            ;;
        GAME|GAMES)
            execute_game_shortcode "$action" "$param" "$param2"
            ;;
        SYS|SYSTEM)
            execute_system_shortcode "$action" "$param" "$param2"
            ;;
        *)
            log_error "Unknown shortcode category: $category"
            echo "Use 'shortcode browse' to see available categories"
            return 1
            ;;
    esac
}

# Memory shortcode execution
execute_memory_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        LIST)
            log_info "Listing memory files..."
            find "$UMEMORY" -name "*.md" -type f | head -20 | while read file; do
                echo "  $(basename "$file")"
            done
            ;;
        VIEW)
            if [[ -n "$param" ]]; then
                local file="$UMEMORY/$param"
                if [[ -f "$file" ]]; then
                    log_info "Viewing: $param"
                    cat "$file"
                else
                    log_error "Memory file not found: $param"
                fi
            else
                log_error "Memory file name required"
            fi
            ;;
        SEARCH)
            if [[ -n "$param" ]]; then
                log_info "Searching memory for: $param"
                grep -r "$param" "$UMEMORY"/*.md 2>/dev/null || log_warning "No matches found"
            else
                log_error "Search term required"
            fi
            ;;
        CREATE)
            if [[ -n "$param" ]]; then
                local timestamp=$(date +%Y%m%d-%H%M%S)
                local filename="FILE-${timestamp}-${param}-001.md"
                local filepath="$UMEMORY/$filename"
                
                cat > "$filepath" << EOF
# 🧠 Memory: $param

**Created**: $(date "+%Y-%m-%d %H:%M:%S")  
**Topic**: $param  
**Type**: User Created

## Content

[Add your content here]

## Notes

- Note 1
- Note 2

---

*Created via shortcode*
EOF
                log_success "Memory file created: $filename"
            else
                log_error "Topic name required"
            fi
            ;;
        RECENT)
            log_info "Recent memory files:"
            find "$UMEMORY" -name "*.md" -type f -mtime -7 | sort -r | head -10 | while read file; do
                echo "  $(basename "$file")"
            done
            ;;
        *)
            log_error "Unknown memory action: $action"
            ;;
    esac
}

# Mission shortcode execution
execute_mission_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        LIST)
            log_info "Active missions:"
            find "$UMEMORY" -name "*-mission.md" -type f | while read file; do
                echo "  $(basename "$file")"
            done
            ;;
        CREATE)
            if [[ -n "$param" ]]; then
                # Generate uHEX code
                local uhex_code=$(openssl rand -hex 4 | tr '[:lower:]' '[:upper:]' 2>/dev/null || printf "%08X" $((RANDOM * RANDOM)))
                local clean_param="${param//[^a-zA-Z0-9]/-}"
                local filename="uTASK-${uhex_code}-${clean_param}.md"
                local missions_dir="$UMEMORY/user/missions"
                mkdir -p "$missions_dir"
                local filepath="$missions_dir/$filename"
                
                cat > "$filepath" << EOF
---
mission_id: "uTASK-${uhex_code}"
title: "$param"
type: "user_created"
priority: "medium"
status: "active"
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
---

# 🎯 Mission: $param

**Created**: $(date "+%Y-%m-%d %H:%M:%S")  
**Status**: Active  
**Priority**: Medium  
**Type**: User Created  
**Mission ID**: uTASK-${uhex_code}

## Objective

[Describe mission objective here]

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Progress

*Mission started*

## Notes

[Add mission notes here]

---

**Status**: Active 🎯  
**Mission ID**: uTASK-${uhex_code}
EOF
                log_success "Mission created: $filename"
            else
                log_error "Mission name required"
            fi
            ;;
        STATUS)
            log_info "Mission status overview:"
            local total=$(find "$UMEMORY" -name "*-mission.md" | wc -l)
            local completed=$(grep -l "Status.*Complete" "$UMEMORY"/*-mission.md 2>/dev/null | wc -l)
            local active=$((total - completed))
            echo "  Active: $active"
            echo "  Completed: $completed"
            echo "  Total: $total"
            ;;
        *)
            log_error "Unknown mission action: $action"
            ;;
    esac
}

# Package shortcode execution (stub)
execute_package_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        LIST)
            log_info "Available packages:"
            echo "  [Package system not yet implemented]"
            ;;
        *)
            log_warning "Package system not yet implemented"
            ;;
    esac
}

# Log shortcode execution (stub)
execute_log_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        REPORT)
            log_info "Generating daily report..."
            echo "  [Log reporting not yet implemented]"
            ;;
        STATS)
            log_info "System statistics:"
            echo "  [Statistics not yet implemented]"
            ;;
        *)
            log_warning "Log system not yet implemented"
            ;;
    esac
}

# Dashboard shortcode execution (stub)
execute_dash_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        LIVE)
            log_info "Starting live dashboard..."
            echo "  [Dashboard system not yet implemented]"
            ;;
        *)
            log_warning "Dashboard system not yet implemented"
            ;;
    esac
}

# Editor shortcode execution (stub)
execute_editor_shortcode() {
    local category="$1"
    local action="$2"
    local param="$3"
    
    case "$category" in
        EDIT)
            log_info "Opening editor for: $param"
            echo "  [Editor integration not yet implemented]"
            ;;
        NEW)
            log_info "Creating new $action file"
            echo "  [File creation not yet implemented]"
            ;;
        *)
            log_warning "Editor integration not yet implemented"
            ;;
    esac
}

# Web editor shortcode execution (stub)
execute_web_shortcode() {
    local action="$1"
    local param="$2"
    
    log_warning "Web editor not yet implemented"
}

# ASCII art shortcode execution (stub)  
execute_ascii_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        TEXT)
            if [[ -n "$param" ]]; then
                log_info "Generating ASCII text for: $param"
                # Simple ASCII text generation
                echo ""
                echo "$param" | fold -w 40
                echo ""
            else
                log_error "Text parameter required"
            fi
            ;;
        *)
            log_warning "ASCII generation not yet fully implemented"
            ;;
    esac
}

# Game shortcode execution (stub)
execute_game_shortcode() {
    local action="$1"
    local param="$2"
    
    log_warning "Game system not yet implemented"
}

# System shortcode execution (stub)
execute_system_shortcode() {
    local action="$1"
    local param="$2"
    
    case "$action" in
        INFO)
            log_info "System information:"
            echo "  uDOS Version: v1.3"
            echo "  System: $(uname -s)"
            echo "  User: $(whoami)"
            echo "  Date: $(date)"
            ;;
        BACKUP)
            log_info "Starting system backup..."
            # Call the smart backup system
            if [[ -x "$UDOS_ROOT/uCORE/code/smart-backup.sh" ]]; then
                "$UDOS_ROOT/uCORE/code/smart-backup.sh"
            else
                log_warning "Backup system not available"
            fi
            ;;
        *)
            log_warning "System action not yet implemented: $action"
            ;;
    esac
}

# Interactive shortcode builder
build_shortcode() {
    echo -e "\n${YELLOW}🔨 Shortcode Builder${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo "Select a category:"
    local i=1
    for category in "${CATEGORIES[@]}"; do
        if [[ "$category" != "all" ]]; then
            echo "  $i. $category"
            ((i++))
        fi
    done
    echo ""
    
    read -p "Enter category number: " choice
    
    # Convert choice to category name
    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#CATEGORIES[@]}-1 )); then
        local selected_category="${CATEGORIES[$((choice-1))]}"
        echo ""
        echo -e "Building shortcode for: ${CYAN}$selected_category${NC}"
        echo ""
        
        # Show available actions for the category
        case "$selected_category" in
            memory)
                echo "Available actions: LIST, VIEW, SEARCH, CREATE, RECENT"
                ;;
            mission)
                echo "Available actions: LIST, CREATE, STATUS, COMPLETE, EDIT"
                ;;
            *)
                echo "Available actions: LIST, INFO, STATUS"
                ;;
        esac
        
        read -p "Enter action: " action
        read -p "Enter parameter (optional): " param
        
        local shortcode="[${selected_category^^}|${action^^}"
        if [[ -n "$param" ]]; then
            shortcode="${shortcode}|${param}"
        fi
        shortcode="${shortcode}]"
        
        echo ""
        echo -e "Generated shortcode: ${GREEN}$shortcode${NC}"
        echo ""
        read -p "Execute this shortcode? (y/N): " execute
        
        if [[ "$execute" =~ ^[Yy] ]]; then
            execute_shortcode "$shortcode"
        fi
    else
        log_error "Invalid selection"
    fi
}

# Show shortcode help
show_shortcode_help() {
    echo -e "\n${YELLOW}🔧 Shortcode System Help${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BOLD}Usage:${NC}"
    echo "  shortcode browse [category]     - Browse available shortcodes"
    echo "  shortcode execute [shortcode]   - Execute a shortcode"
    echo "  shortcode build                 - Interactive shortcode builder"
    echo "  shortcode help                  - Show this help"
    echo ""
    echo -e "${BOLD}Categories:${NC}"
    echo "  memory, mission, package, log, dash, editor, games, system"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  shortcode browse memory"
    echo "  shortcode execute '[MEM|LIST]'"
    echo "  shortcode build"
    echo ""
    echo -e "${BOLD}Shortcode Format:${NC}"
    echo "  [CATEGORY|ACTION|PARAM1|PARAM2]"
    echo ""
}

# Main function dispatcher
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        browse)
            browse_shortcodes "$1"
            ;;
        execute)
            if [[ -n "$1" ]]; then
                execute_shortcode "$1"
            else
                log_error "Shortcode required for execution"
                echo "Example: shortcode execute '[MEM|LIST]'"
            fi
            ;;
        build)
            build_shortcode
            ;;
        help|--help|-h)
            show_shortcode_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_shortcode_help
            ;;
    esac
}

# If script is executed directly, run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
