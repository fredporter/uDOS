#!/bin/bash
# workflow-manager.sh - User journey workflow management system
# Handles move→milestone→mission→legacy progression with assist mode

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration
SANDBOX_DIR="$UDOS_ROOT/sandbox"
WORKFLOW_DIR="$SANDBOX_DIR/workflow"
MOVES_DIR="$WORKFLOW_DIR/moves"
MILESTONES_DIR="$WORKFLOW_DIR/milestones"
MISSIONS_DIR="$WORKFLOW_DIR/missions"
LEGACY_DIR="$WORKFLOW_DIR/legacy"
ASSIST_DIR="$WORKFLOW_DIR/assist"

# Current state files
CURRENT_MISSION="$WORKFLOW_DIR/current-mission.json"
ASSIST_MODE="$WORKFLOW_DIR/assist-mode.json"
USER_JOURNEY="$WORKFLOW_DIR/user-journey.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# WORKFLOW INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

# Initialize workflow structure
init_workflow() {
    mkdir -p "$MOVES_DIR" "$MILESTONES_DIR" "$MISSIONS_DIR" "$LEGACY_DIR" "$ASSIST_DIR"

    # Initialize user journey if not exists
    if [ ! -f "$USER_JOURNEY" ]; then
        cat > "$USER_JOURNEY" << EOF
{
    "user_id": "$(whoami)",
    "journey_started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "current_stage": "exploring",
    "total_moves": 0,
    "milestones_achieved": 0,
    "missions_completed": 0,
    "legacy_items": 0,
    "assist_mode": "available",
    "journey_map": {
        "exploring": {
            "description": "Learning and experimenting",
            "next_stage": "planning"
        },
        "planning": {
            "description": "Setting goals and missions",
            "next_stage": "executing"
        },
        "executing": {
            "description": "Working on missions",
            "next_stage": "achieving"
        },
        "achieving": {
            "description": "Completing milestones",
            "next_stage": "legacy"
        },
        "legacy": {
            "description": "Creating lasting impact",
            "next_stage": "exploring"
        }
    }
}
EOF
    fi

    log_success "Workflow system initialized"
}

# ═══════════════════════════════════════════════════════════════════════
# MOVE MANAGEMENT (Present Activity)
# ═══════════════════════════════════════════════════════════════════════

# Log a move (current activity)
log_move() {
    local move_type="$1"
    local description="$2"
    local context="${3:-{}}"

    local move_id="move_$(date +%s)_$$"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local move_file="$MOVES_DIR/$move_id.json"

    cat > "$move_file" << EOF
{
    "move_id": "$move_id",
    "type": "$move_type",
    "description": "$description",
    "timestamp": "$timestamp",
    "context": $context,
    "status": "completed",
    "session_id": "$(get_current_session_id)",
    "user_intent": "$(detect_user_intent "$move_type" "$description")",
    "potential_milestone": "$(suggest_milestone "$move_type" "$description")"
}
EOF

    # Update user journey
    update_journey_stats "moves" 1

    # Check if move suggests milestone
    check_milestone_potential "$move_id"

    log_info "Move logged: $move_type - $description"
}

# Check if move should suggest milestone creation
check_milestone_potential() {
    local move_id="$1"
    # Simple milestone suggestion based on move patterns
    # This could be enhanced with AI or more complex logic
    log_info "Move $move_id recorded (milestone potential analysis available)"
}

# Find related mission for milestone
find_related_mission() {
    local milestone_title="$1"
    # Simple mission matching - could be enhanced
    if [ -d "$MISSIONS_DIR" ]; then
        find "$MISSIONS_DIR" -name "*.json" -exec jq -r 'select(.status=="active") | .mission_id' {} \; 2>/dev/null | head -1 || echo "none"
    else
        echo "none"
    fi
}

# Check if milestone completes mission
check_mission_completion() {
    local milestone_id="$1"
    # Simple completion check - could be enhanced with objective tracking
    log_info "Milestone $milestone_id may contribute to mission completion"
}

# Suggest next steps after milestone
suggest_next_steps() {
    local milestone_id="$1"
    local milestone_file="$MILESTONES_DIR/$milestone_id.json"
    if [ -f "$milestone_file" ]; then
        local next_milestone=$(jq -r '.next_suggested_milestone' "$milestone_file")
        if [ "$next_milestone" != "null" ] && [ -n "$next_milestone" ]; then
            log_info "💡 Suggested next milestone: $next_milestone"
        fi
    fi
}

# Generate assist recommendations for mission
generate_mission_assist() {
    local mission_id="$1"
    log_info "📋 Assist recommendations generated for mission: $mission_id"
}

# Summarize value created from mission
summarize_value_created() {
    local mission_data="$1"
    echo "Knowledge and capabilities gained through mission completion"
}

# Extract knowledge gained
extract_knowledge_gained() {
    local mission_data="$1"
    echo "Practical experience and technical understanding"
}

# Identify skills developed
identify_skills_developed() {
    local mission_data="$1"
    echo "Problem-solving, development, and analytical skills"
}

# Suggest future applications
suggest_future_applications() {
    local impact_type="$1"
    case "$impact_type" in
        "knowledge_expansion") echo "Apply learning to new projects and challenges" ;;
        "creation_contribution") echo "Build upon created work for enhanced solutions" ;;
        "improvement_impact") echo "Scale improvements to broader applications" ;;
        "community_benefit") echo "Share knowledge and mentor others" ;;
        *) echo "Continue building expertise and capabilities" ;;
    esac
}

# Get current session ID
get_current_session_id() {
    if [ -f "$SANDBOX_DIR/session/current-session.json" ]; then
        jq -r '.session_id' "$SANDBOX_DIR/session/current-session.json" 2>/dev/null || echo "no_session"
    else
        echo "no_session"
    fi
}

# Detect user intent from move
detect_user_intent() {
    local move_type="$1"
    local description="$2"

    case "$move_type" in
        "create_file"|"edit_file") echo "development" ;;
        "run_test"|"create_test") echo "validation" ;;
        "experiment"|"explore") echo "learning" ;;
        "backup"|"restore") echo "preservation" ;;
        "deploy"|"publish") echo "sharing" ;;
        *) echo "exploration" ;;
    esac
}

# Suggest potential milestone
suggest_milestone() {
    local move_type="$1"
    local description="$2"

    case "$move_type" in
        "create_file") echo "File Creation Mastery" ;;
        "run_test") echo "Testing Proficiency" ;;
        "experiment") echo "Innovation Breakthrough" ;;
        "backup") echo "Data Stewardship" ;;
        *) echo "Progress Marker" ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# MILESTONE MANAGEMENT (Achievements)
# ═══════════════════════════════════════════════════════════════════════

# Create milestone
create_milestone() {
    local title="$1"
    local description="$2"
    local moves_involved="${3:-[]}"

    local milestone_id="milestone_$(date +%s)"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local milestone_file="$MILESTONES_DIR/$milestone_id.json"

    cat > "$milestone_file" << EOF
{
    "milestone_id": "$milestone_id",
    "title": "$title",
    "description": "$description",
    "achieved": "$timestamp",
    "moves_involved": $moves_involved,
    "session_id": "$(get_current_session_id)",
    "significance": "$(calculate_significance "$title")",
    "next_suggested_milestone": "$(suggest_next_milestone "$title")",
    "contributes_to_mission": "$(find_related_mission "$title")"
}
EOF

    # Update user journey
    update_journey_stats "milestones_achieved" 1

    # Check if milestone completes a mission
    check_mission_completion "$milestone_id"

    log_success "Milestone achieved: $title"

    # Suggest next steps
    suggest_next_steps "$milestone_id"
}

# Calculate milestone significance
calculate_significance() {
    local title="$1"
    case "$title" in
        *"First"*|*"Initial"*) echo "foundational" ;;
        *"Master"*|*"Expert"*) echo "expertise" ;;
        *"Complete"*|*"Finish"*) echo "completion" ;;
        *"Innovation"*|*"Breakthrough"*) echo "innovation" ;;
        *) echo "progress" ;;
    esac
}

# Suggest next milestone
suggest_next_milestone() {
    local current="$1"
    case "$current" in
        *"Creation"*) echo "Testing Mastery" ;;
        *"Testing"*) echo "Deployment Success" ;;
        *"Innovation"*) echo "Knowledge Sharing" ;;
        *) echo "Advanced Progress" ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# MISSION MANAGEMENT (Goals & Objectives)
# ═══════════════════════════════════════════════════════════════════════

# Create mission
create_mission() {
    local title="$1"
    local description="$2"
    local objectives="${3:-[]}"
    local timeline="${4:-flexible}"

    local mission_id="mission_$(date +%s)"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local mission_file="$MISSIONS_DIR/$mission_id.json"

    cat > "$mission_file" << EOF
{
    "mission_id": "$mission_id",
    "title": "$title",
    "description": "$description",
    "created": "$timestamp",
    "status": "active",
    "timeline": "$timeline",
    "objectives": $objectives,
    "required_milestones": [],
    "completed_milestones": [],
    "progress_percentage": 0,
    "estimated_completion": "$(calculate_estimated_completion "$timeline")",
    "assist_recommendations": [],
    "legacy_impact": "$(predict_legacy_impact "$title" "$description")"
}
EOF

    # Set as current mission if none active
    if [ ! -f "$CURRENT_MISSION" ] || [ "$(jq -r '.status' "$CURRENT_MISSION" 2>/dev/null)" = "completed" ]; then
        cp "$mission_file" "$CURRENT_MISSION"
    fi

    log_success "Mission created: $title"

    # Generate assist recommendations
    generate_mission_assist "$mission_id"
}

# Calculate estimated completion
calculate_estimated_completion() {
    local timeline="$1"
    case "$timeline" in
        "urgent") date -d "+1 week" +%Y-%m-%d ;;
        "normal") date -d "+1 month" +%Y-%m-%d ;;
        "flexible") date -d "+3 months" +%Y-%m-%d ;;
        *) date -d "+1 month" +%Y-%m-%d ;;
    esac
}

# Predict legacy impact
predict_legacy_impact() {
    local title="$1"
    local description="$2"

    if echo "$description" | grep -qi "learn\|skill\|knowledge"; then
        echo "knowledge_expansion"
    elif echo "$description" | grep -qi "create\|build\|develop"; then
        echo "creation_contribution"
    elif echo "$description" | grep -qi "improve\|optimize\|enhance"; then
        echo "improvement_impact"
    elif echo "$description" | grep -qi "share\|teach\|help"; then
        echo "community_benefit"
    else
        echo "personal_growth"
    fi
}

# Complete mission
complete_mission() {
    local mission_id="$1"
    local completion_notes="${2:-Mission completed successfully}"

    local mission_file="$MISSIONS_DIR/$mission_id.json"
    if [ ! -f "$mission_file" ]; then
        log_error "Mission not found: $mission_id"
        return 1
    fi

    # Update mission status
    local temp_file=$(mktemp)
    jq --arg notes "$completion_notes" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .status = "completed" |
        .completed = $timestamp |
        .completion_notes = $notes |
        .progress_percentage = 100
    ' "$mission_file" > "$temp_file" && mv "$temp_file" "$mission_file"

    # Create legacy item
    create_legacy_from_mission "$mission_id"

    # Update journey stats
    update_journey_stats "missions_completed" 1

    log_success "Mission completed: $(jq -r '.title' "$mission_file")"
}

# ═══════════════════════════════════════════════════════════════════════
# LEGACY MANAGEMENT (Achievements & Impact)
# ═══════════════════════════════════════════════════════════════════════

# Create legacy from completed mission
create_legacy_from_mission() {
    local mission_id="$1"
    local mission_file="$MISSIONS_DIR/$mission_id.json"

    if [ ! -f "$mission_file" ]; then
        log_error "Mission file not found for legacy creation"
        return 1
    fi

    local mission_data=$(cat "$mission_file")
    local legacy_id="legacy_$(date +%s)"
    local legacy_file="$LEGACY_DIR/$legacy_id.json"
    local title=$(echo "$mission_data" | jq -r '.title')
    local impact=$(echo "$mission_data" | jq -r '.legacy_impact')

    # Create austere legacy summary
    cat > "$legacy_file" << EOF
{
    "legacy_id": "$legacy_id",
    "title": "$title",
    "impact_type": "$impact",
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source_mission": "$mission_id",
    "key_achievements": $(echo "$mission_data" | jq '.completed_milestones // []'),
    "value_created": "$(summarize_value_created "$mission_data")",
    "knowledge_gained": "$(extract_knowledge_gained "$mission_data")",
    "skills_developed": "$(identify_skills_developed "$mission_data")",
    "future_applications": "$(suggest_future_applications "$impact")",
    "austerity_summary": "$(create_austerity_summary "$title" "$impact")"
}
EOF

    # Update journey stats
    update_journey_stats "legacy_items" 1

    log_success "Legacy created: $title"
}

# Create austere summary for legacy
create_austerity_summary() {
    local title="$1"
    local impact="$2"

    case "$impact" in
        "knowledge_expansion") echo "Learned: $title. Applied new knowledge. Ready for next challenge." ;;
        "creation_contribution") echo "Built: $title. Created lasting value. Enhanced capabilities." ;;
        "improvement_impact") echo "Improved: $title. Optimized processes. Increased efficiency." ;;
        "community_benefit") echo "Shared: $title. Helped others. Strengthened community." ;;
        *) echo "Accomplished: $title. Gained experience. Progressed forward." ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# ASSIST MODE (AI-Powered Guidance)
# ═══════════════════════════════════════════════════════════════════════

# Enter assist mode
enter_assist_mode() {
    local focus_area="${1:-general}"
    local context="${2:-current_session}"

    cat > "$ASSIST_MODE" << EOF
{
    "mode": "active",
    "activated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "focus_area": "$focus_area",
    "context": "$context",
    "recommendations": [],
    "user_preferences": {
        "suggestion_frequency": "moderate",
        "detail_level": "comprehensive",
        "proactive_alerts": true
    }
}
EOF

    log_success "Assist mode activated (focus: $focus_area)"

    # Generate initial recommendations
    generate_assist_recommendations "$focus_area"
}

# Generate assist recommendations
generate_assist_recommendations() {
    local focus_area="$1"
    local recommendations=()

    # Analyze current state
    local current_moves=$(find "$MOVES_DIR" -name "*.json" -mtime -1 | wc -l)
    local pending_milestones=$(find "$MILESTONES_DIR" -name "*.json" | wc -l)
    local active_missions=$(find "$MISSIONS_DIR" -name "*.json" -exec jq -r 'select(.status=="active") | .mission_id' {} \; | wc -l)

    # Generate context-aware recommendations
    case "$focus_area" in
        "productivity")
            if [ "$current_moves" -lt 3 ]; then
                recommendations+=("Consider setting a daily move target to maintain momentum")
            fi
            if [ "$active_missions" -eq 0 ]; then
                recommendations+=("Create a mission to provide direction for your activities")
            fi
            ;;
        "learning")
            recommendations+=("Document insights from recent experiments")
            recommendations+=("Consider creating a knowledge-sharing milestone")
            ;;
        "development")
            recommendations+=("Set up automated testing for your development work")
            recommendations+=("Create development milestones for skill progression")
            ;;
        *)
            recommendations+=("Review recent moves to identify patterns")
            recommendations+=("Consider creating milestones for significant achievements")
            if [ "$active_missions" -eq 0 ]; then
                recommendations+=("Define a mission to guide your efforts")
            fi
            ;;
    esac

    # Update assist mode with recommendations
    local temp_file=$(mktemp)
    jq --argjson recs "$(printf '%s\n' "${recommendations[@]}" | jq -R . | jq -s .)" '
        .recommendations = $recs |
        .last_updated = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))
    ' "$ASSIST_MODE" > "$temp_file" && mv "$temp_file" "$ASSIST_MODE"

    # Display recommendations
    echo -e "${CYAN}🤖 Assist Recommendations:${NC}"
    printf '%s\n' "${recommendations[@]}" | while read -r rec; do
        echo -e "  ${BLUE}•${NC} $rec"
    done
}

# Exit assist mode
exit_assist_mode() {
    if [ -f "$ASSIST_MODE" ]; then
        local temp_file=$(mktemp)
        jq '.mode = "inactive" | .deactivated = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' "$ASSIST_MODE" > "$temp_file" && mv "$temp_file" "$ASSIST_MODE"
        log_success "Assist mode deactivated"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Update journey statistics
update_journey_stats() {
    local stat_name="$1"
    local increment="$2"

    if [ -f "$USER_JOURNEY" ]; then
        local temp_file=$(mktemp)
        jq --arg stat "$stat_name" --argjson inc "$increment" '
            .[$stat] += $inc |
            .last_updated = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))
        ' "$USER_JOURNEY" > "$temp_file" && mv "$temp_file" "$USER_JOURNEY"
    fi
}

# Show workflow status
show_workflow_status() {
    echo -e "${BOLD}${CYAN}═══ WORKFLOW STATUS ═══${NC}"

    if [ -f "$USER_JOURNEY" ]; then
        local journey_data=$(cat "$USER_JOURNEY")
        local stage=$(echo "$journey_data" | jq -r '.current_stage')
        local moves=$(echo "$journey_data" | jq -r '.total_moves')
        local milestones=$(echo "$journey_data" | jq -r '.milestones_achieved')
        local missions=$(echo "$journey_data" | jq -r '.missions_completed')
        local legacy=$(echo "$journey_data" | jq -r '.legacy_items')

        echo -e "${BLUE}Current Stage:${NC} $stage"
        echo -e "${BLUE}Total Moves:${NC} $moves"
        echo -e "${BLUE}Milestones:${NC} $milestones"
        echo -e "${BLUE}Missions Completed:${NC} $missions"
        echo -e "${BLUE}Legacy Items:${NC} $legacy"
    fi

    # Show active mission
    if [ -f "$CURRENT_MISSION" ]; then
        local mission_title=$(jq -r '.title' "$CURRENT_MISSION")
        local mission_progress=$(jq -r '.progress_percentage' "$CURRENT_MISSION")
        echo -e "${BLUE}Active Mission:${NC} $mission_title ($mission_progress%)"
    fi

    # Show assist mode status
    if [ -f "$ASSIST_MODE" ] && [ "$(jq -r '.mode' "$ASSIST_MODE")" = "active" ]; then
        local focus=$(jq -r '.focus_area' "$ASSIST_MODE")
        echo -e "${BLUE}Assist Mode:${NC} Active (focus: $focus)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

show_help() {
    echo -e "${BOLD}${CYAN}🗺️  Workflow Manager${NC}"
    echo "User journey management: move→milestone→mission→legacy"
    echo ""
    echo "Commands:"
    echo "  move <type> <description>           - Log current activity"
    echo "  milestone <title> <description>     - Create achievement milestone"
    echo "  mission create <title> <desc>       - Create new mission"
    echo "  mission complete <id> [notes]       - Complete mission"
    echo "  legacy list                         - Show legacy achievements"
    echo "  assist enter [focus]                - Enter assist mode"
    echo "  assist exit                         - Exit assist mode"
    echo "  status                              - Show workflow status"
    echo "  init                                - Initialize workflow system"
    echo ""
    echo "Journey Stages: exploring → planning → executing → achieving → legacy"
}

main() {
    local command="${1:-help}"
    shift || true

    # Initialize if needed
    [ ! -d "$WORKFLOW_DIR" ] && init_workflow

    case "$command" in
        move)
            local move_type="$1"
            local description="$2"
            if [ -z "$move_type" ] || [ -z "$description" ]; then
                log_error "Move type and description required"
                exit 1
            fi
            log_move "$move_type" "$description"
            ;;
        milestone)
            local title="$1"
            local description="$2"
            if [ -z "$title" ] || [ -z "$description" ]; then
                log_error "Milestone title and description required"
                exit 1
            fi
            create_milestone "$title" "$description"
            ;;
        mission)
            local action="$1"
            shift || true
            case "$action" in
                create)
                    local title="$1"
                    local description="$2"
                    if [ -z "$title" ] || [ -z "$description" ]; then
                        log_error "Mission title and description required"
                        exit 1
                    fi
                    create_mission "$title" "$description"
                    ;;
                complete)
                    local mission_id="$1"
                    local notes="${2:-Mission completed successfully}"
                    if [ -z "$mission_id" ]; then
                        log_error "Mission ID required"
                        exit 1
                    fi
                    complete_mission "$mission_id" "$notes"
                    ;;
                *)
                    log_error "Unknown mission action: $action"
                    ;;
            esac
            ;;
        legacy)
            local action="${1:-list}"
            case "$action" in
                list)
                    echo -e "${BLUE}🏆 Legacy Achievements:${NC}"
                    find "$LEGACY_DIR" -name "*.json" -exec jq -r '.title + " (" + .impact_type + ")"' {} \; 2>/dev/null | sort
                    ;;
            esac
            ;;
        assist)
            local action="${1:-status}"
            case "$action" in
                enter)
                    local focus="${2:-general}"
                    enter_assist_mode "$focus"
                    ;;
                exit)
                    exit_assist_mode
                    ;;
                status)
                    if [ -f "$ASSIST_MODE" ]; then
                        jq . "$ASSIST_MODE"
                    else
                        echo "Assist mode not active"
                    fi
                    ;;
            esac
            ;;
        status)
            show_workflow_status
            ;;
        init)
            init_workflow
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
