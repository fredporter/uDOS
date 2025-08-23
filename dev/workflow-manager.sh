#!/bin/bash

# uDOS Enhanced Workflow Manager v1.3.3
# Supports Assist Mode (AI-driven) and Command Mode (user-driven)
# Location: /Users/agentdigital/uDOS/dev/workflow-manager.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
DEV_DIR="$SCRIPT_DIR"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
CURRENT_ROLE_CONF="$UDOS_ROOT/sandbox/current-role.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Mode detection
MODE="COMMAND"  # Default mode (IO - user driven)
ASSIST_MODE_FILE="$DEV_DIR/.assist-mode"

# Initialize logging
LOG_DIR="$UMEMORY_DIR/log/daily"
ERROR_LOG="$UMEMORY_DIR/log/errors"
DEBUG_LOG="$UMEMORY_DIR/log/debug"

# Get current role
get_current_role() {
    if [[ -f "$CURRENT_ROLE_CONF" ]]; then
        grep "CURRENT_ROLE=" "$CURRENT_ROLE_CONF" | cut -d'=' -f2 | tr -d '"'
    else
        echo "wizard"
    fi
}

CURRENT_ROLE=$(get_current_role)

# Logging functions
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local role_log_dir=""

    case "$level" in
        "ERROR")
            role_log_dir="$ERROR_LOG/$CURRENT_ROLE"
            ;;
        "DEBUG")
            role_log_dir="$DEBUG_LOG/$CURRENT_ROLE"
            ;;
        *)
            role_log_dir="$LOG_DIR/$CURRENT_ROLE"
            ;;
    esac

    mkdir -p "$role_log_dir"
    echo "[$timestamp] [$level] [WORKFLOW] $message" >> "$role_log_dir/workflow-$(date '+%Y%m%d').log"
}

# Enhanced display functions
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}                uDOS Enhanced Workflow Manager v1.3.3         ${CYAN}║${NC}"
    echo -e "${CYAN}║${WHITE}        Assist Mode (OI) • Command Mode (IO) • Role-Based     ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Current Role:${NC} ${WHITE}$CURRENT_ROLE${NC} | ${BLUE}Mode:${NC} ${WHITE}$MODE${NC}"
    echo ""
}

print_separator() {
    echo -e "${CYAN}────────────────────────────────────────────────────────────────${NC}"
}

# Mode detection and switching
detect_mode() {
    if [[ -f "$ASSIST_MODE_FILE" ]]; then
        MODE="ASSIST"
    else
        MODE="COMMAND"
    fi
}

# Assist Mode functions (AI-driven)
enter_assist_mode() {
    echo -e "${PURPLE}🤖 Entering ASSIST MODE (OI - AI Driven)${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$ASSIST_MODE_FILE"
    MODE="ASSIST"
    log_message "INFO" "Entered ASSIST mode"

    # Check past context and recommend actions
    analyze_context_and_recommend
}

exit_assist_mode() {
    echo -e "${GREEN}👤 Entering COMMAND MODE (IO - User Driven)${NC}"
    rm -f "$ASSIST_MODE_FILE"
    MODE="COMMAND"
    log_message "INFO" "Entered COMMAND mode"
}

# Context analysis for Assist Mode
analyze_context_and_recommend() {
    echo -e "${YELLOW}🔍 Analyzing past context and future roadmaps...${NC}"

    # Check recent activity
    local recent_logs=$(find "$LOG_DIR/$CURRENT_ROLE" -name "*.log" -mtime -7 2>/dev/null | head -5)
    local active_roadmaps=$(find "$DEV_DIR/roadmaps" -name "*.md" -type f | grep -v COMPLETE | head -3)

    echo -e "${BLUE}📊 Recent Activity Analysis:${NC}"
    if [[ -n "$recent_logs" ]]; then
        echo "$recent_logs" | while read -r log_file; do
            if [[ -f "$log_file" ]]; then
                local last_entry=$(tail -1 "$log_file" 2>/dev/null || echo "No entries")
                echo "  • $(basename "$log_file"): $last_entry"
            fi
        done
    else
        echo "  • No recent activity found"
    fi

    echo ""
    echo -e "${BLUE}🗺️ Active Roadmaps:${NC}"
    if [[ -n "$active_roadmaps" ]]; then
        echo "$active_roadmaps" | while read -r roadmap; do
            local title=$(head -1 "$roadmap" 2>/dev/null | sed 's/^# //' || echo "Untitled")
            echo "  • $(basename "$roadmap"): $title"
        done
    else
        echo "  • No active roadmaps found"
    fi

    echo ""
    echo -e "${PURPLE}🎯 AI Recommendations:${NC}"
    generate_recommendations
}

# AI-style recommendations
generate_recommendations() {
    local recommendations=(
        "Review and update incomplete roadmaps based on recent activity"
        "Consolidate recent log entries into milestone achievements"
        "Check for pending tasks in active workflows"
        "Update role-specific configurations based on usage patterns"
        "Create backup of recent development work"
        "Analyze error logs for systematic improvements"
        "Review and organize recent dev tools usage"
        "Plan next development sprint based on roadmap priorities"
    )

    # Pick 3 random recommendations
    for i in {1..3}; do
        local rand_index=$((RANDOM % ${#recommendations[@]}))
        echo "  $i. ${recommendations[$rand_index]}"
    done

    echo ""
    echo -e "${CYAN}💡 Tip: Use 'workflow assist execute [number]' to auto-execute recommendations${NC}"
}

# Workflow management functions
list_roadmaps() {
    echo -e "${BLUE}📋 Available Roadmaps:${NC}"
    echo ""

    local roadmaps_dir="$DEV_DIR/roadmaps"
    local count=1

    find "$roadmaps_dir" -name "*.md" -type f | sort | while read -r roadmap; do
        local title=$(head -1 "$roadmap" 2>/dev/null | sed 's/^# //' || echo "Untitled")
        local status="ACTIVE"

        if [[ "$roadmap" == *"COMPLETE"* ]]; then
            status="${GREEN}COMPLETE${NC}"
        elif [[ "$roadmap" == *"uTASK"* ]]; then
            status="${YELLOW}TASK${NC}"
        fi

        echo -e "  ${WHITE}$count.${NC} $(basename "$roadmap")"
        echo -e "     Title: $title"
        echo -e "     Status: $status"
        echo ""
        count=$((count + 1))
    done
}

list_active_workflows() {
    echo -e "${BLUE}⚡ Active Workflows:${NC}"
    echo ""

    local active_dir="$DEV_DIR/active"
    if [[ -d "$active_dir" ]] && [[ -n $(ls -A "$active_dir" 2>/dev/null) ]]; then
        ls -la "$active_dir"
    else
        echo "  No active workflows found"
    fi
}

# Briefings management functions
list_briefings() {
    echo -e "${PURPLE}🧠 Available Briefings:${NC}"
    echo ""

    local briefings_dir="$DEV_DIR/briefings"

    if [[ ! -d "$briefings_dir" ]]; then
        echo "  📂 Briefings directory not found: $briefings_dir"
        return 1
    fi

    local count=1
    find "$briefings_dir" -name "*.md" -type f | sort | while read -r briefing; do
        local title=$(head -1 "$briefing" 2>/dev/null | sed 's/^# //' || echo "Untitled")
        local modified=$(date -r "$briefing" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "unknown")
        local size=$(wc -l < "$briefing" 2>/dev/null | tr -d ' ')

        echo -e "  ${WHITE}$count.${NC} $(basename "$briefing")"
        echo -e "     Title: $title"
        echo -e "     Modified: $modified ($size lines)"
        echo ""
        count=$((count + 1))
    done
}

show_current_briefing() {
    echo -e "${PURPLE}📖 Current Session Briefing:${NC}"
    echo ""

    local briefings_dir="$DEV_DIR/briefings"
    local current_briefing=""

    # Find the most recent briefing file
    current_briefing=$(find "$briefings_dir" -name "uBRIEF-*.md" 2>/dev/null | head -1)

    if [[ -n "$current_briefing" && -f "$current_briefing" ]]; then
        echo -e "  📄 ${WHITE}$(basename "$current_briefing")${NC}"
        echo -e "  📅 Modified: $(date -r "$current_briefing" "+%Y-%m-%d %H:%M")"
        echo -e "  📊 Size: $(wc -l < "$current_briefing" | tr -d ' ') lines"
        echo ""
        echo -e "${YELLOW}Preview:${NC}"
        head -5 "$current_briefing" | sed 's/^/  /'
        echo ""
    else
        echo "  ❌ No current briefing found"
        echo "  💡 Run './dev/scripts/briefings-cleanup.sh' to organize briefings"
        echo ""
    fi
}

update_briefing_context() {
    echo -e "${PURPLE}🔄 Updating Briefing Context:${NC}"
    echo ""

    local briefings_dir="$DEV_DIR/briefings"
    local current_briefing=""
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    # Find current briefing
    current_briefing=$(find "$briefings_dir" -name "uBRIEF-*.md" 2>/dev/null | head -1)

    if [[ -n "$current_briefing" && -f "$current_briefing" ]]; then
        echo -e "  📝 Updating: ${WHITE}$(basename "$current_briefing")${NC}"

        # Add current session context
        cat >> "$current_briefing" << EOF

## Session Update - $timestamp

### Current Context
- **Role**: $CURRENT_ROLE
- **Mode**: $MODE
- **Active Session**: $(date "+%Y-%m-%d")

### Recent Activity
$(tail -5 "$LOG_DIR/$CURRENT_ROLE/workflow-$(date '+%Y%m%d').log" 2>/dev/null | sed 's/^/- /' || echo "- No recent activity logged")

### System Status
- **Briefings**: $(find "$briefings_dir" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files
- **Roadmaps**: $(find "$DEV_DIR/roadmaps" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files
- **Dev Notes**: $(find "$DEV_DIR/notes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files

---
EOF

        echo -e "  ✅ Briefing updated with current context"
        log_message "INFO" "Updated briefing context: $(basename "$current_briefing")"
    else
        echo -e "  ❌ No briefing found to update"
        echo -e "  💡 Create a briefing first or run cleanup script"
    fi

    echo ""
}

# Development utilities
run_dev_tool() {
    local tool="$1"
    echo -e "${YELLOW}🔧 Running development tool: $tool${NC}"

    case "$tool" in
        "check-umemory")
            "$DEV_DIR/scripts/check-umemory-reorganization.sh"
            ;;
        "convert-json")
            "$DEV_DIR/scripts/convert-to-udata.sh"
            ;;
        "test-parser")
            "$DEV_DIR/scripts/test-json-parser.sh"
            ;;
        "setup-local")
            "$DEV_DIR/scripts/setup-local.sh"
            ;;
        *)
            echo "Unknown tool: $tool"
            echo "Available tools: check-umemory, convert-json, test-parser, setup-local"
            ;;
    esac
}

# Main menu for Command Mode
show_command_menu() {
    echo -e "${WHITE}Command Mode Menu:${NC}"
    echo "  1. List roadmaps"
    echo "  2. List active workflows"
    echo "  3. Run development tool"
    echo "  4. Enter Assist Mode"
    echo "  5. View recent logs"
    echo "  6. Exit"
    echo ""
    echo -n "Select option: "
}

# Assist Mode menu
show_assist_menu() {
    echo -e "${PURPLE}Assist Mode Menu:${NC}"
    echo "  1. Analyze context and recommend"
    echo "  2. Execute recommendation"
    echo "  3. Review roadmaps"
    echo "  4. Auto-organize workflows"
    echo "  5. Exit Assist Mode"
    echo ""
    echo -n "AI recommends option: "
}

# View recent logs
view_recent_logs() {
    echo -e "${BLUE}📝 Recent Logs for Role: $CURRENT_ROLE${NC}"
    echo ""

    local role_log_dir="$LOG_DIR/$CURRENT_ROLE"
    if [[ -d "$role_log_dir" ]]; then
        find "$role_log_dir" -name "*.log" -mtime -7 | sort | while read -r log_file; do
            echo -e "${YELLOW}$(basename "$log_file"):${NC}"
            tail -5 "$log_file" 2>/dev/null || echo "  No entries"
            echo ""
        done
    else
        echo "  No logs found for role: $CURRENT_ROLE"
    fi
}

# Main execution
main() {
    detect_mode
    print_header

    case "${1:-}" in
        "assist")
            case "${2:-}" in
                "enter")
                    enter_assist_mode
                    ;;
                "exit")
                    exit_assist_mode
                    ;;
                "analyze")
                    analyze_context_and_recommend
                    ;;
                *)
                    echo "Usage: workflow assist [enter|exit|analyze]"
                    ;;
            esac
            ;;
        "list")
            case "${2:-}" in
                "roadmaps")
                    list_roadmaps
                    ;;
                "briefings")
                    list_briefings
                    ;;
                "active")
                    list_active_workflows
                    ;;
                *)
                    echo "Usage: workflow list [roadmaps|briefings|active]"
                    ;;
            esac
            ;;
        "briefings")
            case "${2:-}" in
                "list")
                    list_briefings
                    ;;
                "current")
                    show_current_briefing
                    ;;
                "update")
                    update_briefing_context
                    ;;
                "cleanup")
                    "$DEV_DIR/scripts/briefings-cleanup.sh"
                    ;;
                *)
                    echo "Usage: workflow briefings [list|current|update|cleanup]"
                    ;;
            esac
            ;;
        "roadmaps")
            case "${2:-}" in
                "list")
                    list_roadmaps
                    ;;
                "cleanup")
                    "$DEV_DIR/scripts/roadmaps-cleanup.sh"
                    ;;
                *)
                    echo "Usage: workflow roadmaps [list|cleanup]"
                    ;;
            esac
            ;;
        "cleanup")
            case "${2:-}" in
                "all")
                    echo -e "${YELLOW}🧹 Running all cleanup scripts...${NC}"
                    "$DEV_DIR/scripts/notes-cleanup.sh"
                    "$DEV_DIR/scripts/briefings-cleanup.sh"
                    "$DEV_DIR/scripts/roadmaps-cleanup.sh"
                    ;;
                "notes")
                    "$DEV_DIR/scripts/notes-cleanup.sh"
                    ;;
                "briefings")
                    "$DEV_DIR/scripts/briefings-cleanup.sh"
                    ;;
                "roadmaps")
                    "$DEV_DIR/scripts/roadmaps-cleanup.sh"
                    ;;
                *)
                    echo "Usage: workflow cleanup [all|notes|briefings|roadmaps]"
                    ;;
            esac
            ;;
        "tool")
            run_dev_tool "${2:-}"
            ;;
        "logs")
            view_recent_logs
            ;;
        "interactive"|"")
            # Interactive mode
            if [[ "$MODE" == "ASSIST" ]]; then
                while true; do
                    show_assist_menu
                    read -r choice
                    case "$choice" in
                        1) analyze_context_and_recommend ;;
                        2) echo "Feature coming soon: Auto-execute recommendations" ;;
                        3) list_roadmaps ;;
                        4) echo "Feature coming soon: Auto-organize workflows" ;;
                        5) exit_assist_mode; break ;;
                        *) echo "Invalid option" ;;
                    esac
                    echo ""
                    print_separator
                    echo ""
                done
            else
                while true; do
                    show_command_menu
                    read -r choice
                    case "$choice" in
                        1) list_roadmaps ;;
                        2) list_active_workflows ;;
                        3) echo -n "Enter tool name: "; read -r tool; run_dev_tool "$tool" ;;
                        4) enter_assist_mode ;;
                        5) view_recent_logs ;;
                        6) break ;;
                        *) echo "Invalid option" ;;
                    esac
                    echo ""
                    print_separator
                    echo ""
                done
            fi
            ;;
        *)
            echo "Usage: workflow [assist|list|briefings|roadmaps|cleanup|tool|logs|interactive]"
            echo ""
            echo "Commands:"
            echo "  assist enter     - Enter AI-driven Assist Mode (OI)"
            echo "  assist exit      - Exit to user-driven Command Mode (IO)"
            echo "  assist analyze   - Analyze context and get recommendations"
            echo "  list roadmaps    - List available roadmaps"
            echo "  list briefings   - List available briefings"
            echo "  list active      - List active workflows"
            echo "  briefings list   - List all briefings"
            echo "  briefings current - Show current session briefing"
            echo "  briefings update - Update briefing with current context"
            echo "  briefings cleanup - Run briefings cleanup script"
            echo "  roadmaps list    - List all roadmaps"
            echo "  roadmaps cleanup - Run roadmaps cleanup script"
            echo "  cleanup all      - Run all cleanup scripts"
            echo "  cleanup notes    - Run notes cleanup script"
            echo "  cleanup briefings - Run briefings cleanup script"
            echo "  cleanup roadmaps - Run roadmaps cleanup script"
            echo "  tool <name>      - Run development tool"
            echo "  logs             - View recent logs"
            echo "  interactive      - Start interactive mode"
            ;;
    esac

    log_message "INFO" "Workflow manager executed with args: $*"
}

# Execute main function with all arguments
main "$@"
