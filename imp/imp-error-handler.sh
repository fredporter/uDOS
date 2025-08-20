#!/bin/bash

# 👹 Imp Creative Error Handler
# File: imp-error-handler.sh
# Purpose: Creative error handling for Imp development environment
# Level: 60/100 - Creative Development Authority
# uHEX: E8012017 - Imp Creative Error Handler

set -euo pipefail

# Configuration
IMP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREATIVE_LOGS_DIR="$IMP_ROOT/creative-logs"
INNOVATION_ERRORS_DIR="$IMP_ROOT/innovation-errors"
PROJECT_SESSION_DIR="$IMP_ROOT/project-sessions"

# Ensure workshop directories exist
mkdir -p "$CREATIVE_LOGS_DIR" "$INNOVATION_ERRORS_DIR" "$PROJECT_SESSION_DIR"

# Date and time in the workshop
TODAY="$(date +%Y%m%d)"
NOW="$(date +%H%M%S)"
TIMESTAMP="$(date +%Y-%m-%dT%H:%M:%SZ)"

# Imp color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
MAGENTA='\033[1;35m'
ORANGE='\033[0;33m'
NC='\033[0m'

# Creative symbols for imp context
IMP_SYMBOLS=(
    "👹" "🎨" "✨" "💡" "🔥" "⚡" "🌟" "🎭" "🎪" "🎨"
    "🖌️" "🎵" "🎬" "📝" "🖼️" "🎪" "🎢" "🎡" "🎠" "🎯"
)

# Generate imp-themed log prefixes
get_creative_symbol() {
    local context="$1"
    case "$context" in
        "error") echo "🔥" ;;
        "warning") echo "⚠️" ;;
        "info") echo "💡" ;;
        "success") echo "✨" ;;
        "creative") echo "🎨" ;;
        "innovation") echo "⚡" ;;
        "project") echo "🎯" ;;
        *) echo "${IMP_SYMBOLS[$((RANDOM % ${#IMP_SYMBOLS[@]}))]}" ;;
    esac
}

# Creative logging functions with imp theming
log_creative_info() {
    local symbol=$(get_creative_symbol "info")
    echo -e "${CYAN}$symbol $1${NC}"
    creative_log "INFO" "$1" "inspiration"
}

log_creative_success() {
    local symbol=$(get_creative_symbol "success")
    echo -e "${GREEN}$symbol $1${NC}"
    creative_log "SUCCESS" "$1" "achievement"
}

log_creative_warning() {
    local symbol=$(get_creative_symbol "warning")
    echo -e "${YELLOW}$symbol $1${NC}"
    creative_log "WARNING" "$1" "concern"
}

log_creative_error() {
    local symbol=$(get_creative_symbol "error")
    echo -e "${RED}$symbol $1${NC}"
    creative_log "ERROR" "$1" "obstacle" true
}

log_innovation_activity() {
    local symbol=$(get_creative_symbol "innovation")
    echo -e "${PURPLE}$symbol $1${NC}"
    creative_log "INNOVATION" "$1" "breakthrough"
}

log_project_status() {
    local symbol=$(get_creative_symbol "project")
    echo -e "${MAGENTA}$symbol $1${NC}"
    creative_log "PROJECT" "$1" "creation"
}

# Core creative logging function
creative_log() {
    local level="$1"
    local message="$2"
    local workshop="${3:-creative}"
    local is_error="${4:-false}"
    
    local log_file="$CREATIVE_LOGS_DIR/imp-creative-$TODAY.log"
    local session_id="${PROJECT_SESSION_ID:-$(generate_project_session)}"
    
    # Create creative log entry
    cat >> "$log_file" << EOF
[$TIMESTAMP] [$level] [$workshop] [👹 $session_id]
Creative Record: $message
Innovation State: $(get_innovation_info)
Project Context: $(get_project_state)
Workshop Status: $(get_workshop_context)
Creative Flow: $(get_creative_flow_info)
Resource Pool: $(get_resource_pool)
---
EOF

    # Transform errors into learning opportunities
    if [[ "$is_error" == "true" ]]; then
        transform_creative_error "$message" "$workshop" "$level"
    fi
    
    # Update creative analytics
    update_creative_analytics "$level" "$workshop"
}

# Enhanced error transformation for imp workshop
transform_creative_error() {
    local error_message="$1"
    local workshop="${2:-unknown}"
    local level="${3:-ERROR}"
    
    local error_file="$INNOVATION_ERRORS_DIR/imp-innovation-$TODAY.log"
    local error_id="IMP_${TODAY}_${NOW}_$(printf "%04X" $RANDOM)"
    
    cat >> "$error_file" << EOF
👹 CREATIVE ERROR TRANSFORMATION - $error_id
═══════════════════════════════════════════════════════════════
Transformation Time: $TIMESTAMP
Challenge Level: $level
Workshop Area: $workshop
Project Session: ${PROJECT_SESSION_ID:-unknown}
Innovation State: $(get_innovation_info)
Creative Environment: $(get_creative_environment)
Development Safety: MAINTAINED

Error as Learning Opportunity:
$error_message

Project State:
$(get_project_state)

Workshop Context:
$(get_workshop_context)

Creative Protection:
$(get_creative_protection)

Innovation Strategy:
$(generate_innovation_strategy "$error_message" "$workshop")

═══════════════════════════════════════════════════════════════
EOF

    # Create creative notification for workshop management
    create_creative_notification "$error_id" "$error_message" "$workshop"
}

# Project session management
generate_project_session() {
    local session_id="IMP_${TODAY}_${NOW}_$(printf "%04X" $RANDOM)"
    export PROJECT_SESSION_ID="$session_id"
    
    # Create project session file
    cat > "$PROJECT_SESSION_DIR/project-session-$session_id.json" << EOF
{
    "session_id": "$session_id",
    "creation_time": "$TIMESTAMP",
    "workshop": "imp",
    "access_level": "creative",
    "development_type": "innovative",
    "project_state": "active",
    "creative_safety": "enabled",
    "sandbox_mode": true,
    "session_scope": {
        "access": "personal-projects",
        "modifications": "creative-sandbox",
        "experimentation": "encouraged"
    },
    "creative_activities": []
}
EOF
    
    echo "$session_id"
}

# Imp workshop information gathering
get_innovation_info() {
    echo "PID:$$ Creative:${IMP_CREATIVE_MODE:-true} Sandbox:${IMP_SANDBOX_MODE:-active}"
}

get_project_state() {
    cat << EOF
Project Session: ${PROJECT_SESSION_ID:-inactive}
Creative Mode: ${IMP_CREATIVE_MODE:-true}
Innovation Level: ${IMP_INNOVATION_LEVEL:-standard}
Sandbox Active: ${IMP_SANDBOX_MODE:-true}
Environment: ${IMP_ENVIRONMENT:-development}
EOF
}

get_workshop_context() {
    cat << EOF
Working Project: $(pwd)
Current Script: $(basename "${0:-unknown}")
Creative Mode: ${IMP_CREATIVE_MODE:-true}
Experimental Mode: ${IMP_EXPERIMENTAL_MODE:-true}
Sandbox Protected: ${IMP_SANDBOX_PROTECTED:-true}
EOF
}

get_creative_environment() {
    cat << EOF
IMP_ROOT: $IMP_ROOT
CREATIVE_MODE: ${IMP_CREATIVE_MODE:-true}
INNOVATION_LEVEL: ${IMP_INNOVATION_LEVEL:-standard}
SANDBOX_MODE: ${IMP_SANDBOX_MODE:-active}
SESSION_TYPE: ${IMP_SESSION_TYPE:-creative}
PATH: $PATH
EOF
}

get_creative_flow_info() {
    echo "Flow:${IMP_CREATIVE_FLOW:-active} Innovation:${IMP_INNOVATION_LEVEL:-standard} Sandbox:${IMP_SANDBOX_PROTECTED:-true}"
}

get_creative_protection() {
    cat << EOF
✓ Sandbox isolation - creative experiments protected
✓ Personal project space - no system interference
✓ Version control - creative history preserved
✓ Template access - creative building blocks available
✓ Innovation tracking - creative progress monitored
✓ Safe experimentation - creative freedom with safety
EOF
}

get_resource_pool() {
    if command -v find >/dev/null 2>&1; then
        local template_count=$(find . -name "*.template" 2>/dev/null | wc -l | tr -d ' ')
        echo "Resources: $template_count templates available"
    else
        echo "Resources: creative"
    fi
}

# Creative analytics and reporting
update_creative_analytics() {
    local level="$1"
    local workshop="$2"
    
    local analytics_file="$CREATIVE_LOGS_DIR/imp-analytics-$TODAY.json"
    
    # Initialize creative analytics if it doesn't exist
    if [[ ! -f "$analytics_file" ]]; then
        cat > "$analytics_file" << EOF
{
    "date": "$TODAY",
    "project_session": "${PROJECT_SESSION_ID:-unknown}",
    "creative_levels": {},
    "workshop_areas": {},
    "innovation_metrics": {
        "templates_created": 0,
        "projects_started": 0,
        "creative_experiments": 0,
        "innovation_breakthroughs": 0
    },
    "development_metrics": {
        "scripts_written": 0,
        "templates_customized": 0,
        "creative_solutions": 0
    }
}
EOF
    fi
    
    # Update analytics using jq if available
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq ".creative_levels[\"$level\"] += 1 | .workshop_areas[\"$workshop\"] += 1" "$analytics_file" > "$temp_file" && mv "$temp_file" "$analytics_file"
    fi
}

# Innovation strategy for errors
generate_innovation_strategy() {
    local error_message="$1"
    local workshop="$2"
    
    cat << EOF
🎨 Error transformed into creative challenge
💡 Learning opportunity identified
👹 Creative problem-solving activated
✨ Innovation pathway established
🔥 Creative energy redirected
⚡ Experimental approach encouraged
🌟 Creative breakthrough potential
EOF
}

# Creative notification system
create_creative_notification() {
    local error_id="$1"
    local error_message="$2"
    local workshop="$3"
    
    # Create workshop management notification
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"Creative challenge encountered - innovation opportunity\" with title \"👹 Imp Workshop\" subtitle \"Creative transformation\"" 2>/dev/null || true
    fi
    
    # Log to system for creative administrators
    if command -v logger >/dev/null 2>&1; then
        logger -t "uDOS-Imp-Creative" "Creative error transformed: $error_id [$workshop]"
    fi
}

# Creative activity tracking
track_creative_activity() {
    local activity_type="$1"
    local description="$2"
    local innovative="${3:-true}"
    
    local session_file="$PROJECT_SESSION_DIR/project-session-${PROJECT_SESSION_ID}.json"
    
    if [[ -f "$session_file" ]] && command -v jq >/dev/null 2>&1 ]]; then
        local activity_entry=$(cat << EOF
{
    "timestamp": "$TIMESTAMP",
    "type": "$activity_type",
    "description": "$description",
    "innovative": $innovative,
    "creative": true
}
EOF
        )
        
        local temp_file=$(mktemp)
        jq ".creative_activities += [$activity_entry]" "$session_file" > "$temp_file" && mv "$temp_file" "$session_file"
    fi
    
    log_innovation_activity "Creative Activity: $activity_type - $description"
}

# Main creative command interface
main() {
    case "${1:-help}" in
        "ignite")
            log_creative_info "Igniting Imp Creative Error Handler"
            generate_project_session >/dev/null
            log_creative_success "Creative workshop ignited with session: $PROJECT_SESSION_ID"
            ;;
        "log")
            if [[ $# -lt 3 ]]; then
                log_creative_error "Usage: $0 log <level> <message> [workshop]"
                exit 1
            fi
            creative_log "$2" "$3" "${4:-creative}"
            ;;
        "error")
            if [[ $# -lt 2 ]]; then
                log_creative_error "Usage: $0 error <message> [workshop]"
                exit 1
            fi
            log_creative_error "$2"
            transform_creative_error "$2" "${3:-creative}" "ERROR"
            ;;
        "create")
            if [[ $# -lt 3 ]]; then
                log_creative_error "Usage: $0 create <type> <description>"
                exit 1
            fi
            track_creative_activity "$2" "$3" true
            ;;
        "session")
            if [[ -n "${PROJECT_SESSION_ID:-}" ]]; then
                echo "Current project session: $PROJECT_SESSION_ID"
                if [[ -f "$PROJECT_SESSION_DIR/project-session-$PROJECT_SESSION_ID.json" ]]; then
                    echo "Session details:"
                    cat "$PROJECT_SESSION_DIR/project-session-$PROJECT_SESSION_ID.json" | jq '.' 2>/dev/null || cat "$PROJECT_SESSION_DIR/project-session-$PROJECT_SESSION_ID.json"
                fi
            else
                echo "No active project session"
            fi
            ;;
        "analytics")
            local analytics_file="$CREATIVE_LOGS_DIR/imp-analytics-$TODAY.json"
            if [[ -f "$analytics_file" ]]; then
                echo "👹 Imp Creative Analytics - $TODAY"
                cat "$analytics_file" | jq '.' 2>/dev/null || cat "$analytics_file"
            else
                log_creative_warning "No creative analytics available for today"
            fi
            ;;
        "help"|*)
            show_creative_usage
            ;;
    esac
}

show_creative_usage() {
    cat << EOF
👹 Imp Creative Error Handler v1.3
═══════════════════════════════════════════════════════════════

🎨 Creative error handling for the Imp development environment

Usage: $0 [command] [options]

Commands:
  ignite                            Ignite creative workshop
  log <level> <message> [workshop]  Log creative message
  error <message> [workshop]        Transform error into opportunity
  create <type> <description>       Track creative activity
  session                          Show current project session
  analytics                        Show creative analytics
  help                             Show this creative guidance

Creative Levels:
  INFO, SUCCESS, WARNING, ERROR, INNOVATION, PROJECT

Creative Workshops:
  creative, innovation, project, template, experimental

Examples:
  $0 ignite
  $0 log INFO "New template created" "template"
  $0 error "Compilation failed" "project"
  $0 create "template" "Custom automation script template"

Environment Variables:
  IMP_CREATIVE_MODE=true            Enable creative mode (always true)
  IMP_INNOVATION_LEVEL=standard     Innovation experimentation level
  IMP_SANDBOX_MODE=active           Creative sandbox protection

Creative Features:
  🎨 Creative problem transformation
  💡 Innovation opportunity identification
  👹 Experimental environment safety
  ✨ Template and script development
  🔥 Creative energy channeling
  ⚡ Rapid prototyping support

Files Created:
  imp/creative-logs/imp-creative-YYYYMMDD.log        Daily creative log
  imp/innovation-errors/imp-innovation-YYYYMMDD.log  Error transformations
  imp/creative-logs/imp-analytics-YYYYMMDD.json      Creative analytics
  imp/project-sessions/project-session-ID.json       Session tracking

👹 Creative Development Authority - Level 60 Access
uHEX: E8012017 - Imp Creative Error Handler
EOF
}

# Initialize project session if not already ignited
if [[ -z "${PROJECT_SESSION_ID:-}" ]]; then
    generate_project_session >/dev/null
fi

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
