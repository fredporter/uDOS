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
GOALS_DIR="$WORKFLOW_DIR/goals"
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
    mkdir -p "$MOVES_DIR" "$GOALS_DIR" "$MILESTONES_DIR" "$MISSIONS_DIR" "$LEGACY_DIR" "$ASSIST_DIR"

    # Initialize user journey if not exists
    if [ ! -f "$USER_JOURNEY" ]; then
        cat > "$USER_JOURNEY" << EOF
{
    "user_id": "$(whoami)",
    "journey_started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "current_stage": "exploring",
    "total_moves": 0,
    "goals_created": 0,
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
# GOAL MANAGEMENT (Aspirations & Intentions)
# ═══════════════════════════════════════════════════════════════════════

# Create goal
create_goal() {
    local title="$1"
    local description="$2"
    local goal_type="${3:-exploration}"
    local timeframe="${4:-1 month}"
    local priority="${5:-medium}"

    local goal_id="goal_$(date +%s)"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local goal_file="$GOALS_DIR/$goal_id.json"

    cat > "$goal_file" << EOF
{
    "goal_id": "$goal_id",
    "title": "$title",
    "description": "$description",
    "goal_type": "$goal_type",
    "created": "$timestamp",
    "status": "active",
    "priority": "$priority",
    "timeframe": "$timeframe",
    "progress_percentage": 0,
    "related_moves": [],
    "milestones_created": [],
    "session_id": "$(get_current_session_id)",
    "motivation": "$(suggest_motivation "$goal_type" "$title")",
    "success_indicators": [],
    "potential_milestones": "$(suggest_goal_milestones "$goal_type" "$title")",
    "estimated_completion": "$(calculate_goal_completion "$timeframe")"
}
EOF

    # Update user journey
    update_journey_stats "goals_created" 1

    log_success "Goal created: $title"

    # Suggest first moves toward goal
    suggest_goal_moves "$goal_id"
}

# Update goal progress
update_goal() {
    local goal_id="$1"
    local field="$2"
    local value="$3"

    local goal_file="$GOALS_DIR/$goal_id.json"
    if [ ! -f "$goal_file" ]; then
        log_error "Goal not found: $goal_id"
        return 1
    fi

    local temp_file=$(mktemp)
    jq --arg field "$field" --arg value "$value" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .[$field] = $value |
        .last_updated = $timestamp
    ' "$goal_file" > "$temp_file" && mv "$temp_file" "$goal_file"

    log_success "Goal updated: $field = $value"
}

# Convert goal to milestone
convert_goal_to_milestone() {
    local goal_id="$1"
    local milestone_title="$2"
    local milestone_description="$3"

    local goal_file="$GOALS_DIR/$goal_id.json"
    if [ ! -f "$goal_file" ]; then
        log_error "Goal not found: $goal_id"
        return 1
    fi

    # Create milestone from goal
    create_milestone "$milestone_title" "$milestone_description" "[]"

    # Update goal with milestone link
    local milestone_id="milestone_$(date +%s)"
    local temp_file=$(mktemp)
    jq --arg milestone_id "$milestone_id" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .milestones_created += [$milestone_id] |
        .last_milestone_created = $timestamp |
        .progress_percentage = (.progress_percentage + 25 | if . > 100 then 100 else . end)
    ' "$goal_file" > "$temp_file" && mv "$temp_file" "$goal_file"

    log_success "Goal converted to milestone: $milestone_title"
}

# Link goal to move
link_goal_to_move() {
    local goal_id="$1"
    local move_id="$2"

    local goal_file="$GOALS_DIR/$goal_id.json"
    if [ ! -f "$goal_file" ]; then
        log_error "Goal not found: $goal_id"
        return 1
    fi

    local temp_file=$(mktemp)
    jq --arg move_id "$move_id" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .related_moves += [$move_id] |
        .last_move_related = $timestamp
    ' "$goal_file" > "$temp_file" && mv "$temp_file" "$goal_file"

    log_info "Goal linked to move: $move_id"
}

# List active goals
list_goals() {
    echo -e "${BLUE}🎯 Active Goals:${NC}"
    if [ -d "$GOALS_DIR" ]; then
        find "$GOALS_DIR" -name "*.json" -exec jq -r 'select(.status=="active") | "  " + .title + " (" + .goal_type + ", " + (.progress_percentage|tostring) + "% complete)"' {} \; 2>/dev/null | sort
    else
        echo "  No goals found"
    fi
}

# Suggest motivation for goal type
suggest_motivation() {
    local goal_type="$1"
    local title="$2"

    case "$goal_type" in
        "learning") echo "Expand knowledge and capabilities" ;;
        "creation") echo "Build something meaningful and useful" ;;
        "improvement") echo "Enhance existing skills or processes" ;;
        "exploration") echo "Discover new possibilities and approaches" ;;
        "mastery") echo "Achieve deep expertise and proficiency" ;;
        *) echo "Personal growth and development" ;;
    esac
}

# Suggest potential milestones for goal
suggest_goal_milestones() {
    local goal_type="$1"
    local title="$2"

    case "$goal_type" in
        "learning") echo "[\"First Understanding\", \"Practical Application\", \"Teaching Others\"]" ;;
        "creation") echo "[\"Planning Complete\", \"Prototype Built\", \"Final Version\"]" ;;
        "improvement") echo "[\"Current State Analyzed\", \"Solution Implemented\", \"Results Measured\"]" ;;
        "exploration") echo "[\"Initial Research\", \"First Experiment\", \"Insights Documented\"]" ;;
        "mastery") echo "[\"Foundation Solid\", \"Advanced Techniques\", \"Expert Level\"]" ;;
        *) echo "[\"First Step\", \"Halfway Point\", \"Goal Achievement\"]" ;;
    esac
}

# Calculate estimated completion date
calculate_goal_completion() {
    local timeframe="$1"
    case "$timeframe" in
        "1-2 weeks") date -d "+2 weeks" +%Y-%m-%d ;;
        "1 month") date -d "+1 month" +%Y-%m-%d ;;
        "2-3 months") date -d "+3 months" +%Y-%m-%d ;;
        "6 months") date -d "+6 months" +%Y-%m-%d ;;
        "1 year") date -d "+1 year" +%Y-%m-%d ;;
        *) date -d "+1 month" +%Y-%m-%d ;;
    esac
}

# Suggest first moves toward goal
suggest_goal_moves() {
    local goal_id="$1"
    log_info "💡 Consider these first moves toward your goal:"
    log_info "  - Research and planning"
    log_info "  - Identify resources needed"
    log_info "  - Take a small first step"
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
    local quest_type="${3:-exploring}"
    local move_budget="${4:-50}"

    local mission_id="quest_$(date +%s)"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local mission_file="$MISSIONS_DIR/$mission_id.json"

    cat > "$mission_file" << EOF
{
    "mission_id": "$mission_id",
    "title": "$title",
    "description": "$description",
    "quest_type": "$quest_type",
    "created": "$timestamp",
    "status": "active",
    "move_budget": $move_budget,
    "moves_used": 0,
    "moves_remaining": $move_budget,
    "objectives": [],
    "completed_milestones": [],
    "progress_percentage": 0,
    "difficulty": "$(calculate_quest_difficulty "$quest_type" "$move_budget")",
    "fun_factor": 8,
    "experience_points": 0,
    "quest_phase": "preparation",
    "personal_rewards": [],
    "skill_unlocks": [],
    "legacy_impact": "$(predict_legacy_impact "$title" "$description")"
}
EOF

    # Set as current mission if none active
    if [ ! -f "$CURRENT_MISSION" ] || [ "$(jq -r '.status' "$CURRENT_MISSION" 2>/dev/null)" = "completed" ]; then
        cp "$mission_file" "$CURRENT_MISSION"
    fi

    log_success "Quest created: $title (Budget: $move_budget moves)"

    # Generate quest recommendations
    generate_quest_recommendations "$mission_id"
}

# Calculate quest difficulty based on type and move budget
calculate_quest_difficulty() {
    local quest_type="$1"
    local move_budget="$2"

    if (( move_budget <= 25 )); then
        echo "easy"
    elif (( move_budget <= 75 )); then
        case "$quest_type" in
            "learning"|"exploring") echo "moderate" ;;
            "building"|"creating") echo "challenging" ;;
            "mastering") echo "challenging" ;;
            *) echo "moderate" ;;
        esac
    else
        echo "legendary"
    fi
}

# Generate quest recommendations
generate_quest_recommendations() {
    local quest_id="$1"
    log_info "🎮 Quest recommendations generated for: $quest_id"
    log_info "  - Break into smaller objectives"
    log_info "  - Set up progress tracking"
    log_info "  - Plan daily move allocations"
}

# Update quest with move tracking
update_quest_moves() {
    local quest_id="$1"
    local moves_to_add="${2:-1}"

    local mission_file="$MISSIONS_DIR/$quest_id.json"
    if [ ! -f "$mission_file" ]; then
        log_error "Quest not found: $quest_id"
        return 1
    fi

    local temp_file=$(mktemp)
    jq --arg moves "$moves_to_add" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .moves_used = (.moves_used + ($moves | tonumber)) |
        .moves_remaining = (.move_budget - .moves_used) |
        .progress_percentage = ((.moves_used / .move_budget) * 100 | floor) |
        .last_move_update = $timestamp
    ' "$mission_file" > "$temp_file" && mv "$temp_file" "$mission_file"

    # Update current mission if this is the active quest
    if [ -f "$CURRENT_MISSION" ]; then
        local current_id=$(jq -r '.mission_id' "$CURRENT_MISSION")
        if [ "$current_id" = "$quest_id" ]; then
            cp "$mission_file" "$CURRENT_MISSION"
        fi
    fi

    local moves_used=$(jq -r '.moves_used' "$mission_file")
    local moves_remaining=$(jq -r '.moves_remaining' "$mission_file")
    local progress=$(jq -r '.progress_percentage' "$mission_file")

    log_info "Quest updated: $moves_used moves used, $moves_remaining remaining ($progress% complete)"
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

# Complete quest
complete_mission() {
    local mission_id="$1"
    local completion_notes="${2:-Quest completed successfully}"

    local mission_file="$MISSIONS_DIR/$mission_id.json"
    if [ ! -f "$mission_file" ]; then
        log_error "Quest not found: $mission_id"
        return 1
    fi

    # Calculate experience points and efficiency
    local move_budget=$(jq -r '.move_budget' "$mission_file")
    local moves_used=$(jq -r '.moves_used' "$mission_file")
    local difficulty=$(jq -r '.difficulty' "$mission_file")

    # Calculate completion efficiency
    local efficiency=100
    if (( moves_used > 0 )); then
        efficiency=$(( (move_budget * 100) / moves_used ))
        if (( efficiency > 100 )); then
            efficiency=100
        fi
    fi

    # Calculate experience points based on difficulty and efficiency
    local base_xp=50
    case "$difficulty" in
        "easy") base_xp=30 ;;
        "moderate") base_xp=50 ;;
        "challenging") base_xp=80 ;;
        "legendary") base_xp=150 ;;
    esac

    local bonus_xp=0
    if (( efficiency >= 90 )); then
        bonus_xp=25  # Efficient completion bonus
    elif (( efficiency >= 75 )); then
        bonus_xp=15
    fi

    local total_xp=$((base_xp + bonus_xp))

    # Update quest status
    local temp_file=$(mktemp)
    jq --arg notes "$completion_notes" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       --arg total_xp "$total_xp" \
       --arg efficiency "$efficiency" '
        .status = "completed" |
        .completed = $timestamp |
        .completion_notes = $notes |
        .progress_percentage = 100 |
        .experience_points = ($total_xp | tonumber) |
        .completion_efficiency = ($efficiency | tonumber)
    ' "$mission_file" > "$temp_file" && mv "$temp_file" "$mission_file"

    # Create legacy item
    create_legacy_from_mission "$mission_id"

    # Update journey stats
    update_journey_stats "missions_completed" 1

    log_success "Quest completed: $(jq -r '.title' "$mission_file")"
    log_info "Experience gained: $total_xp XP (Efficiency: $efficiency%)"
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
        local goals=$(echo "$journey_data" | jq -r '.goals_created // 0')
        local milestones=$(echo "$journey_data" | jq -r '.milestones_achieved')
        local missions=$(echo "$journey_data" | jq -r '.missions_completed')
        local legacy=$(echo "$journey_data" | jq -r '.legacy_items')

        echo -e "${BLUE}Current Stage:${NC} $stage"
        echo -e "${BLUE}Total Moves:${NC} $moves"
        echo -e "${BLUE}Goals Created:${NC} $goals"
        echo -e "${BLUE}Milestones:${NC} $milestones"
        echo -e "${BLUE}Missions Completed:${NC} $missions"
        echo -e "${BLUE}Legacy Items:${NC} $legacy"
    fi

    # Show active quest
    if [ -f "$CURRENT_MISSION" ]; then
        local mission_title=$(jq -r '.title' "$CURRENT_MISSION")
        local mission_progress=$(jq -r '.progress_percentage' "$CURRENT_MISSION")
        local moves_used=$(jq -r '.moves_used // 0' "$CURRENT_MISSION")
        local move_budget=$(jq -r '.move_budget // 0' "$CURRENT_MISSION")
        echo -e "${BLUE}Active Quest:${NC} $mission_title ($mission_progress% - $moves_used/$move_budget moves)"
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
    echo "User journey management: move→goal→milestone→quest→legacy"
    echo ""
    echo "Commands:"
    echo "  move <type> <description>           - Log current activity"
    echo "  goal create <title> <description>   - Create aspirational goal"
    echo "  goal update <id> <field> <value>    - Update goal progress"
    echo "  goal convert <id> <milestone_title> - Convert goal to milestone"
    echo "  goal list                           - List active goals"
    echo "  milestone <title> <description>     - Create achievement milestone"
    echo "  mission create <title> <desc>       - Create new quest"
    echo "  mission update <id> [moves]         - Add moves to quest (default: 1)"
    echo "  mission complete <id> [notes]       - Complete quest"
    echo "  legacy list                         - Show legacy achievements"
    echo "  assist enter [focus]                - Enter assist mode"
    echo "  assist exit                         - Exit assist mode"
    echo "  status                              - Show workflow status"
    echo "  init                                - Initialize workflow system"
    echo ""
    echo "Journey Stages: exploring → planning → executing → achieving → legacy"
    echo "Journey Flow: Move → Goal → Milestone → Quest → Legacy"
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
        goal)
            local action="$1"
            shift || true
            case "$action" in
                create)
                    local title="$1"
                    local description="$2"
                    local goal_type="${3:-exploration}"
                    local timeframe="${4:-1 month}"
                    local priority="${5:-medium}"
                    if [ -z "$title" ] || [ -z "$description" ]; then
                        log_error "Goal title and description required"
                        exit 1
                    fi
                    create_goal "$title" "$description" "$goal_type" "$timeframe" "$priority"
                    ;;
                update)
                    local goal_id="$1"
                    local field="$2"
                    local value="$3"
                    if [ -z "$goal_id" ] || [ -z "$field" ] || [ -z "$value" ]; then
                        log_error "Goal ID, field, and value required"
                        exit 1
                    fi
                    update_goal "$goal_id" "$field" "$value"
                    ;;
                convert)
                    local goal_id="$1"
                    local milestone_title="$2"
                    local milestone_description="${3:-Milestone from goal}"
                    if [ -z "$goal_id" ] || [ -z "$milestone_title" ]; then
                        log_error "Goal ID and milestone title required"
                        exit 1
                    fi
                    convert_goal_to_milestone "$goal_id" "$milestone_title" "$milestone_description"
                    ;;
                list)
                    list_goals
                    ;;
                *)
                    log_error "Unknown goal action: $action"
                    log_info "Available actions: create, update, convert, list"
                    ;;
            esac
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
                        log_error "Quest title and description required"
                        exit 1
                    fi
                    create_mission "$title" "$description"
                    ;;
                update)
                    local quest_id="$1"
                    local moves="${2:-1}"
                    if [ -z "$quest_id" ]; then
                        log_error "Quest ID required"
                        exit 1
                    fi
                    update_quest_moves "$quest_id" "$moves"
                    ;;
                complete)
                    local mission_id="$1"
                    local notes="${2:-Quest completed successfully}"
                    if [ -z "$mission_id" ]; then
                        log_error "Quest ID required"
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
