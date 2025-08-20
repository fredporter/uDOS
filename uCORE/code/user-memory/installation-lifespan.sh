#!/bin/bash
# installation-lifespan.sh - uDOS Installation Lifespan Management
# Manages installation lifecycle according to uDOS core concepts

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
INSTALLATION_LOG="$UMEMORY_DIR/system/installation-lifespan.json"
USER_ROLE_FILE="$UDOS_ROOT/sandbox/user.md"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Ensure system directory exists
mkdir -p "$UMEMORY_DIR/system"

# Installation phases according to uDOS concepts
declare -A INSTALLATION_PHASES=(
    ["initialization"]="Setting up core system and user environment"
    ["role_assignment"]="Determining user role and access level"
    ["environment_setup"]="Configuring role-specific environment"
    ["knowledge_integration"]="Integrating with uKNOWLEDGE and learning systems"
    ["active_operation"]="Normal operational phase"
    ["maintenance"]="System maintenance and optimization"
    ["evolution"]="System evolution and capability expansion"
    ["legacy_preparation"]="Preparing for transition or archival"
    ["archival"]="Moving to legacy status"
)

# Role-based lifespan configurations
declare -A ROLE_LIFESPANS=(
    ["ghost"]="30 days"        # Demo installation - short lifespan
    ["tomb"]="indefinite"      # Archive installation - permanent
    ["drone"]="365 days"       # Automation - long operational life
    ["imp"]="180 days"         # Developer - medium development cycles
    ["sorcerer"]="730 days"    # Advanced user - extended projects
    ["wizard"]="indefinite"    # Full installation - permanent
)

# Initialize installation lifespan tracking
init_installation_lifespan() {
    local user_role="${1:-unknown}"
    local installation_type="${2:-standard}"
    
    echo -e "${CYAN}[LIFESPAN]${NC} Initializing installation lifespan tracking"
    
    # Detect user role if not provided
    if [[ "$user_role" == "unknown" && -f "$USER_ROLE_FILE" ]]; then
        user_role=$(grep -i "role:" "$USER_ROLE_FILE" | cut -d':' -f2 | tr -d ' ' | head -1)
        user_role=${user_role:-"unknown"}
    fi
    
    local installation_id="INST_$(date +%Y%m%d_%H%M%S)_$(printf '%04X' $RANDOM)"
    local lifespan="${ROLE_LIFESPANS[$user_role]:-90 days}"
    
    # Calculate expiration if not indefinite
    local expiration_date="null"
    if [[ "$lifespan" != "indefinite" ]]; then
        local days=$(echo "$lifespan" | grep -o '[0-9]*')
        if command -v date >/dev/null 2>&1; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                expiration_date=$(date -v+${days}d +%Y-%m-%d)
            else
                expiration_date=$(date -d "+${days} days" +%Y-%m-%d)
            fi
        fi
    fi
    
    cat > "$INSTALLATION_LOG" << EOF
{
    "installation_id": "$installation_id",
    "user_role": "$user_role",
    "installation_type": "$installation_type",
    "lifespan": "$lifespan",
    "initialized": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "expiration_date": "$expiration_date",
    "current_phase": "initialization",
    "phase_history": [
        {
            "phase": "initialization",
            "entered": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "description": "Installation lifespan tracking initialized"
        }
    ],
    "milestones": [],
    "maintenance_log": [],
    "extension_requests": [],
    "status": "active"
}
EOF
    
    echo -e "${GREEN}[LIFESPAN]${NC} Installation tracking initialized"
    echo -e "${BLUE}[INFO]${NC} Installation ID: $installation_id"
    echo -e "${BLUE}[INFO]${NC} User Role: $user_role"
    echo -e "${BLUE}[INFO]${NC} Lifespan: $lifespan"
    if [[ "$expiration_date" != "null" ]]; then
        echo -e "${YELLOW}[INFO]${NC} Expiration Date: $expiration_date"
    fi
    
    # Create initial milestone
    add_milestone "installation_initialized" "Installation lifespan tracking system initialized"
}

# Advance to next phase
advance_phase() {
    local target_phase="$1"
    local description="${2:-Advancing to $target_phase phase}"
    
    if [[ ! -f "$INSTALLATION_LOG" ]]; then
        echo -e "${RED}[ERROR]${NC} Installation log not found. Run 'init' first."
        return 1
    fi
    
    if [[ -z "${INSTALLATION_PHASES[$target_phase]}" ]]; then
        echo -e "${RED}[ERROR]${NC} Unknown phase: $target_phase"
        echo -e "${YELLOW}[INFO]${NC} Available phases: ${!INSTALLATION_PHASES[*]}"
        return 1
    fi
    
    echo -e "${CYAN}[LIFESPAN]${NC} Advancing to phase: $target_phase"
    
    # Update installation log
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq --arg phase "$target_phase" \
           --arg desc "$description" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '
           .current_phase = $phase |
           .phase_history += [{
               "phase": $phase,
               "entered": $ts,
               "description": $desc
           }] |
           .last_updated = $ts
           ' \
           "$INSTALLATION_LOG" > "$temp_file" && mv "$temp_file" "$INSTALLATION_LOG"
    fi
    
    echo -e "${GREEN}[LIFESPAN]${NC} Phase advanced to: $target_phase"
    echo -e "${BLUE}[INFO]${NC} ${INSTALLATION_PHASES[$target_phase]}"
    
    # Log milestone for significant phase changes
    case "$target_phase" in
        "active_operation")
            add_milestone "operational_ready" "Installation reached operational status"
            ;;
        "maintenance")
            add_milestone "maintenance_phase" "Installation entered maintenance phase"
            ;;
        "legacy_preparation")
            add_milestone "legacy_preparation" "Installation preparing for legacy transition"
            ;;
        "archival")
            add_milestone "archived" "Installation moved to archival status"
            ;;
    esac
}

# Add milestone
add_milestone() {
    local milestone_type="$1"
    local description="$2"
    
    if [[ ! -f "$INSTALLATION_LOG" ]]; then
        return 1
    fi
    
    echo -e "${PURPLE}[MILESTONE]${NC} Adding milestone: $milestone_type"
    
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq --arg type "$milestone_type" \
           --arg desc "$description" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '
           .milestones += [{
               "type": $type,
               "description": $desc,
               "achieved": $ts
           }]
           ' \
           "$INSTALLATION_LOG" > "$temp_file" && mv "$temp_file" "$INSTALLATION_LOG"
    fi
    
    # Also log to user mission system if available
    if [[ -f "$SCRIPT_DIR/mission-manager.sh" ]]; then
        "$SCRIPT_DIR/mission-manager.sh" milestone "Installation: $milestone_type" "installation_lifespan" "$description"
    fi
}

# Request lifespan extension
request_extension() {
    local extension_days="$1"
    local reason="$2"
    
    if [[ -z "$extension_days" || -z "$reason" ]]; then
        echo -e "${RED}[ERROR]${NC} Extension days and reason required"
        return 1
    fi
    
    echo -e "${CYAN}[LIFESPAN]${NC} Requesting lifespan extension: $extension_days days"
    
    if command -v jq >/dev/null 2>&1 && [[ -f "$INSTALLATION_LOG" ]]; then
        local temp_file=$(mktemp)
        jq --arg days "$extension_days" \
           --arg reason "$reason" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '
           .extension_requests += [{
               "requested_days": $days,
               "reason": $reason,
               "requested": $ts,
               "status": "pending"
           }]
           ' \
           "$INSTALLATION_LOG" > "$temp_file" && mv "$temp_file" "$INSTALLATION_LOG"
    fi
    
    echo -e "${GREEN}[LIFESPAN]${NC} Extension request logged"
    add_milestone "extension_requested" "Requested $extension_days day extension: $reason"
}

# Check installation status
check_status() {
    if [[ ! -f "$INSTALLATION_LOG" ]]; then
        echo -e "${RED}[ERROR]${NC} No installation tracking found"
        return 1
    fi
    
    echo -e "${CYAN}[LIFESPAN]${NC} Installation Status Report"
    echo "==========================================="
    
    if command -v jq >/dev/null 2>&1; then
        local installation_id=$(jq -r '.installation_id' "$INSTALLATION_LOG")
        local user_role=$(jq -r '.user_role' "$INSTALLATION_LOG")
        local current_phase=$(jq -r '.current_phase' "$INSTALLATION_LOG")
        local lifespan=$(jq -r '.lifespan' "$INSTALLATION_LOG")
        local expiration=$(jq -r '.expiration_date' "$INSTALLATION_LOG")
        local status=$(jq -r '.status' "$INSTALLATION_LOG")
        local initialized=$(jq -r '.initialized' "$INSTALLATION_LOG")
        
        echo "Installation ID: $installation_id"
        echo "User Role: $user_role"
        echo "Current Phase: $current_phase"
        echo "Lifespan: $lifespan"
        echo "Status: $status"
        echo "Initialized: $initialized"
        
        if [[ "$expiration" != "null" ]]; then
            echo "Expiration Date: $expiration"
            
            # Calculate days remaining
            if command -v date >/dev/null 2>&1; then
                local current_date=$(date +%Y-%m-%d)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    local days_remaining=$(( ( $(date -j -f "%Y-%m-%d" "$expiration" +%s) - $(date -j -f "%Y-%m-%d" "$current_date" +%s) ) / 86400 ))
                else
                    local days_remaining=$(( ( $(date -d "$expiration" +%s) - $(date -d "$current_date" +%s) ) / 86400 ))
                fi
                
                if [[ $days_remaining -gt 0 ]]; then
                    echo -e "Days Remaining: ${GREEN}$days_remaining${NC}"
                elif [[ $days_remaining -eq 0 ]]; then
                    echo -e "Days Remaining: ${YELLOW}$days_remaining (expires today)${NC}"
                else
                    echo -e "Days Remaining: ${RED}$days_remaining (expired)${NC}"
                fi
            fi
        else
            echo "Expiration Date: Indefinite"
        fi
        
        echo ""
        echo "Phase Description: ${INSTALLATION_PHASES[$current_phase]}"
        
        # Show recent milestones
        local milestone_count=$(jq '.milestones | length' "$INSTALLATION_LOG")
        if [[ $milestone_count -gt 0 ]]; then
            echo ""
            echo "Recent Milestones:"
            jq -r '.milestones[-3:] | .[] | "- \(.type): \(.description) (\(.achieved | split("T")[0]))"' "$INSTALLATION_LOG"
        fi
    else
        echo "jq not available - showing raw log file"
        cat "$INSTALLATION_LOG"
    fi
}

# Perform maintenance
perform_maintenance() {
    local maintenance_type="${1:-routine}"
    local description="${2:-Routine system maintenance}"
    
    echo -e "${CYAN}[MAINTENANCE]${NC} Performing $maintenance_type maintenance"
    
    # Log maintenance activity
    if command -v jq >/dev/null 2>&1 && [[ -f "$INSTALLATION_LOG" ]]; then
        local temp_file=$(mktemp)
        jq --arg type "$maintenance_type" \
           --arg desc "$description" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '
           .maintenance_log += [{
               "type": $type,
               "description": $desc,
               "performed": $ts
           }]
           ' \
           "$INSTALLATION_LOG" > "$temp_file" && mv "$temp_file" "$INSTALLATION_LOG"
    fi
    
    echo -e "${GREEN}[MAINTENANCE]${NC} Maintenance completed: $maintenance_type"
    add_milestone "maintenance_performed" "$description"
}

# Main function
main() {
    case "${1:-help}" in
        "init")
            init_installation_lifespan "$2" "$3"
            ;;
        "phase")
            advance_phase "$2" "$3"
            ;;
        "milestone")
            add_milestone "$2" "$3"
            ;;
        "extend")
            request_extension "$2" "$3"
            ;;
        "status")
            check_status
            ;;
        "maintenance")
            perform_maintenance "$2" "$3"
            ;;
        "help"|*)
            echo "Installation Lifespan Manager v1.0"
            echo "Usage: $0 {init|phase|milestone|extend|status|maintenance|help}"
            echo ""
            echo "Commands:"
            echo "  init [role] [type]                 Initialize lifespan tracking"
            echo "  phase <phase> [description]        Advance to installation phase"
            echo "  milestone <type> <description>     Add milestone"
            echo "  extend <days> <reason>             Request lifespan extension"
            echo "  status                             Show installation status"
            echo "  maintenance [type] [description]   Log maintenance activity"
            echo "  help                               Show this help"
            echo ""
            echo "Installation Phases:"
            for phase in "${!INSTALLATION_PHASES[@]}"; do
                echo "  $phase: ${INSTALLATION_PHASES[$phase]}"
            done
            echo ""
            echo "Role Lifespans:"
            for role in "${!ROLE_LIFESPANS[@]}"; do
                echo "  $role: ${ROLE_LIFESPANS[$role]}"
            done
            echo ""
            echo "Examples:"
            echo "  $0 init wizard full"
            echo "  $0 phase active_operation 'System ready for normal operation'"
            echo "  $0 extend 30 'Extended development project'"
            echo "  $0 status"
            ;;
    esac
}

# Run main function
main "$@"
