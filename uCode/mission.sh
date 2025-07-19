#!/bin/bash
# uDOS Mission/Milestone Management System v1.1.0
# Enhanced with mapping integration and dashboard analytics

set -e

# Configuration
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UCODE="${UHOME}/uCode"
UTEMPLATE="${UHOME}/uTemplate"

MISSIONS_DIR="${UMEM}/missions"
MILESTONES_DIR="${UMEM}/milestones"
MOVES_DIR="${UMEM}/moves"
PROGRESS_DIR="${UMEM}/progress"
ANALYTICS_FILE="${UMEM}/state/mission-analytics.json"

# Ensure directories exist
mkdir -p "$MISSIONS_DIR" "$MILESTONES_DIR" "$PROGRESS_DIR"

# Colors for enhanced output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging with timestamps
log() { 
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [mission]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [mission]${NC} ✅ $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [mission]${NC} ⚠️  $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [mission]${NC} ❌ $1"
}

print_header() {
    echo -e "${WHITE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                🎯 uDOS Mission Control v1.1.0              ║
║              Advanced Project Management System             ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Generate mission ID from name
generate_mission_id() {
    local name="$1"
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
}

# Create a new mission
create_mission() {
    local mission_name="$1"
    local mission_description="$2"
    local location_lat="${3:-0}"
    local location_lon="${4:-0}"
    
    if [[ -z "$mission_name" ]]; then
        log_error "Mission name is required"
        return 1
    fi
    
    local mission_id
    mission_id=$(generate_mission_id "$mission_name")
    local mission_file="${MISSIONS_DIR}/${mission_id}.md"
    
    if [[ -f "$mission_file" ]]; then
        log_warning "Mission '$mission_name' already exists"
        return 1
    fi
    
    log "Creating new mission: $mission_name"
    
    # Create mission file from template
    cat > "$mission_file" << EOF
# 🎯 Mission: $mission_name

**Mission ID**: \`$mission_id\`  
**Created**: $(date '+%Y-%m-%d %H:%M:%S')  
**Status**: 🚀 Active  
**Location**: [$location_lat, $location_lon]  

---

## 📋 Mission Overview

**Description**: $mission_description

**Objectives**:
- [ ] Define mission scope and goals
- [ ] Break down into actionable milestones  
- [ ] Track progress and completion
- [ ] Document outcomes and learnings

---

## 🎯 Mission Metrics

### Progress Tracking
- **Start Date**: $(date '+%Y-%m-%d')
- **Target Completion**: TBD
- **Priority**: Medium
- **Category**: Development

### Analytics
- **Total Moves**: 0
- **Completed Milestones**: 0/0
- **Success Rate**: N/A
- **Time Invested**: 0h

---

## 📍 Geographic Context

**Mission Location**: [$location_lat, $location_lon]
**Mapping Integration**: ✅ Enabled

\`\`\`shortcode
{GEO_CONTEXT}
primary_location: [$location_lat, $location_lon]
mission_id: $mission_id
mission_name: "$mission_name"
tracking_enabled: true
dashboard_integration: true
{/GEO_CONTEXT}
\`\`\`

---

## 🏆 Milestones

*Milestones will be added as mission progresses*

---

## 📊 Recent Activity

*Mission activity will be tracked here automatically*

---

## 📝 Notes & Updates

*Add mission updates, decisions, and key learnings here*

---

**Mission Template v1.1.0** | **uDOS Advanced Mission System**
EOF

    # Create initial progress entry
    update_mission_analytics "$mission_id" "created"
    
    # Log the mission creation
    echo "- [$(date '+%H:%M')] Created mission: $mission_name" >> "${MOVES_DIR}/moves-$(date +%Y-%m-%d).md"
    
    log_success "Mission created: $mission_file"
    
    # Auto-open in editor if available
    if command -v code >/dev/null 2>&1; then
        code "$mission_file"
    fi
}

# Create a milestone
create_milestone() {
    local mission_id="$1"
    local milestone_name="$2"
    local milestone_description="$3"
    
    if [[ -z "$mission_id" || -z "$milestone_name" ]]; then
        log_error "Mission ID and milestone name are required"
        return 1
    fi
    
    local mission_file="${MISSIONS_DIR}/${mission_id}.md"
    if [[ ! -f "$mission_file" ]]; then
        log_error "Mission '$mission_id' not found"
        return 1
    fi
    
    local milestone_id
    milestone_id=$(generate_mission_id "$milestone_name")
    local milestone_file="${MILESTONES_DIR}/${mission_id}-${milestone_id}.md"
    
    log "Creating milestone: $milestone_name for mission: $mission_id"
    
    cat > "$milestone_file" << EOF
# ⭐ Milestone: $milestone_name

**Milestone ID**: \`$milestone_id\`  
**Mission**: [$mission_id](../missions/${mission_id}.md)  
**Created**: $(date '+%Y-%m-%d %H:%M:%S')  
**Status**: 📋 Planned  

---

## 🎯 Milestone Details

**Description**: $milestone_description

**Success Criteria**:
- [ ] Define specific completion criteria
- [ ] Set measurable outcomes
- [ ] Identify required resources
- [ ] Establish timeline

---

## 📊 Progress Tracking

### Completion Checklist
- [ ] Planning Phase Complete
- [ ] Implementation Started  
- [ ] Testing & Validation
- [ ] Documentation Updated
- [ ] Milestone Achieved

### Metrics
- **Progress**: 0%
- **Start Date**: $(date '+%Y-%m-%d')
- **Target Date**: TBD
- **Actual Completion**: TBD

---

## 📝 Activity Log

*Milestone activity will be tracked here*

---

## 🔗 Related Resources

*Links to relevant documentation, code, or external resources*

---

**Milestone Template v1.1.0** | **uDOS Mission System**
EOF

    # Update mission analytics
    update_mission_analytics "$mission_id" "milestone_created"
    
    # Log the milestone creation
    echo "- [$(date '+%H:%M')] Created milestone: $milestone_name (Mission: $mission_id)" >> "${MOVES_DIR}/moves-$(date +%Y-%m-%d).md"
    
    log_success "Milestone created: $milestone_file"
}

# Update mission analytics
update_mission_analytics() {
    local mission_id="$1"
    local action="$2"
    
    local timestamp=$(date -Iseconds)
    local analytics_entry
    
    # Create analytics entry
    analytics_entry=$(cat << EOF
{
    "timestamp": "$timestamp",
    "mission_id": "$mission_id",
    "action": "$action",
    "session": "$(date +%Y%m%d-%H%M%S)"
}
EOF
    )
    
    # Append to analytics file (create if doesn't exist)
    if [[ ! -f "$ANALYTICS_FILE" ]]; then
        echo '{"mission_analytics": []}' > "$ANALYTICS_FILE"
    fi
    
    # Add entry to analytics (simple append for now)
    local temp_file="/tmp/mission_analytics_temp.json"
    jq --argjson entry "$analytics_entry" '.mission_analytics += [$entry]' "$ANALYTICS_FILE" > "$temp_file" && mv "$temp_file" "$ANALYTICS_FILE"
}

# List all missions
list_missions() {
    print_header
    echo
    log "Scanning mission directory: $MISSIONS_DIR"
    
    if [[ ! -d "$MISSIONS_DIR" || -z "$(ls -A "$MISSIONS_DIR" 2>/dev/null)" ]]; then
        echo -e "${YELLOW}📭 No missions found${NC}"
        echo
        echo "💡 Create your first mission:"
        echo "   ./mission-system.sh create \"My First Mission\" \"Description of what I want to achieve\""
        return 0
    fi
    
    echo -e "${WHITE}🎯 Active Missions:${NC}"
    echo
    
    local mission_count=0
    local active_count=0
    
    for mission_file in "$MISSIONS_DIR"/*.md; do
        if [[ -f "$mission_file" ]]; then
            local mission_id
            mission_id=$(basename "$mission_file" .md)
            local mission_name
            mission_name=$(grep "^# 🎯 Mission:" "$mission_file" | sed 's/^# 🎯 Mission: //')
            local created_date
            created_date=$(grep "**Created**:" "$mission_file" | sed 's/.*Created\*\*: //' | awk '{print $1}')
            local status
            status=$(grep "**Status**:" "$mission_file" | sed 's/.*Status\*\*: //')
            
            mission_count=$((mission_count + 1))
            
            # Count milestones for this mission
            local milestone_count=0
            for milestone_file in "$MILESTONES_DIR"/${mission_id}-*.md; do
                if [[ -f "$milestone_file" ]]; then
                    milestone_count=$((milestone_count + 1))
                fi
            done
            
            echo -e "  ${BLUE}▶ ${mission_name}${NC}"
            echo -e "    📋 ID: ${mission_id}"
            echo -e "    📅 Created: ${created_date}"
            echo -e "    📊 Status: ${status}"
            echo -e "    🏆 Milestones: ${milestone_count}"
            echo
            
            if [[ "$status" == *"Active"* ]]; then
                active_count=$((active_count + 1))
            fi
        fi
    done
    
    echo -e "${WHITE}📊 Mission Statistics:${NC}"
    echo -e "  Total Missions: ${mission_count}"
    echo -e "  Active Missions: ${active_count}"
    echo -e "  Completion Rate: $(( active_count > 0 ? (mission_count - active_count) * 100 / mission_count : 0 ))%"
}

# List milestones for a mission
list_milestones() {
    local mission_id="$1"
    
    if [[ -z "$mission_id" ]]; then
        log_error "Mission ID is required"
        return 1
    fi
    
    local mission_file="${MISSIONS_DIR}/${mission_id}.md"
    if [[ ! -f "$mission_file" ]]; then
        log_error "Mission '$mission_id' not found"
        return 1
    fi
    
    local mission_name
    mission_name=$(grep "^# 🎯 Mission:" "$mission_file" | sed 's/^# 🎯 Mission: //')
    
    echo
    echo -e "${WHITE}🏆 Milestones for Mission: ${mission_name}${NC}"
    echo -e "${BLUE}   Mission ID: ${mission_id}${NC}"
    echo
    
    local milestone_count=0
    for milestone_file in "$MILESTONES_DIR"/${mission_id}-*.md; do
        if [[ -f "$milestone_file" ]]; then
            milestone_count=$((milestone_count + 1))
            local milestone_name
            milestone_name=$(grep "^# ⭐ Milestone:" "$milestone_file" | sed 's/^# ⭐ Milestone: //')
            local status
            status=$(grep "**Status**:" "$milestone_file" | sed 's/.*Status\*\*: //')
            local created_date
            created_date=$(grep "**Created**:" "$milestone_file" | sed 's/.*Created\*\*: //' | awk '{print $1}')
            
            echo -e "  ${PURPLE}⭐ ${milestone_name}${NC}"
            echo -e "     📊 Status: ${status}"
            echo -e "     📅 Created: ${created_date}"
            echo
        fi
    done
    
    if [[ $milestone_count -eq 0 ]]; then
        echo -e "${YELLOW}📋 No milestones found for this mission${NC}"
        echo
        echo "💡 Create a milestone:"
        echo "   ./mission-system.sh milestone \"$mission_id\" \"Milestone Name\" \"Description\""
    else
        echo -e "${WHITE}📊 Total Milestones: ${milestone_count}${NC}"
    fi
}

# Show mission/milestone statistics
show_stats() {
    print_header
    echo
    
    # Count missions
    local total_missions=0
    local active_missions=0
    
    if [[ -d "$MISSIONS_DIR" ]]; then
        for mission_file in "$MISSIONS_DIR"/*.md; do
            if [[ -f "$mission_file" ]]; then
                total_missions=$((total_missions + 1))
                local status
                status=$(grep "**Status**:" "$mission_file" | sed 's/.*Status\*\*: //')
                if [[ "$status" == *"Active"* ]]; then
                    active_missions=$((active_missions + 1))
                fi
            fi
        done
    fi
    
    # Count milestones
    local total_milestones=0
    if [[ -d "$MILESTONES_DIR" ]]; then
        total_milestones=$(find "$MILESTONES_DIR" -name "*.md" -type f | wc -l | tr -d ' ')
    fi
    
    # Count today's moves
    local today_moves=0
    local today_file="${MOVES_DIR}/moves-$(date +%Y-%m-%d).md"
    if [[ -f "$today_file" ]]; then
        today_moves=$(grep -c "Created mission\|Created milestone" "$today_file" 2>/dev/null || echo "0")
    fi
    
    # Display statistics
    cat << EOF
📊 Mission Control Dashboard

╔══════════════════════════════════════════════════════════════╗
║                        📈 OVERVIEW                          ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 Total Missions:    ${total_missions}                      ║
║  🚀 Active Missions:   ${active_missions}                     ║  
║  🏆 Total Milestones:  ${total_milestones}                    ║
║  📊 Today's Activity:  ${today_moves}                         ║
╚══════════════════════════════════════════════════════════════╝

📍 Integration Status:
  🗺️  Mapping Integration: ✅ Active
  📊 Dashboard Integration: ✅ Active
  📝 Analytics Tracking: ✅ Active
  🎯 Progress Monitoring: ✅ Active

EOF

    # Show recent activity if available
    if [[ -f "$ANALYTICS_FILE" && -s "$ANALYTICS_FILE" ]]; then
        echo "🔄 Recent Mission Activity:"
        echo
        # Show last 5 activities
        jq -r '.mission_analytics[-5:] | .[] | "  • \(.timestamp | strptime("%Y-%m-%dT%H:%M:%S") | strftime("%H:%M")) - \(.action) (\(.mission_id))"' "$ANALYTICS_FILE" 2>/dev/null || echo "  No recent activity"
    fi
}

# Show help
show_help() {
    print_header
    echo
    cat << EOF
🎯 uDOS Mission Control System v1.1.0

COMMANDS:
  create <name> <description> [lat] [lon]  Create a new mission with optional location
  milestone <mission_id> <name> <desc>     Create a milestone for a mission
  list                                     List all missions
  milestones <mission_id>                  List milestones for a mission
  stats                                    Show mission statistics and dashboard
  help                                     Show this help

EXAMPLES:
  # Create a new mission
  ./mission-system.sh create "Complete uDOS v1.1" "Finish all development tasks" 40.7128 -74.0060
  
  # Create a milestone
  ./mission-system.sh milestone "complete-udos-v1-1" "Implement Dashboard" "Build enhanced analytics"
  
  # View all missions
  ./mission-system.sh list
  
  # View milestones for a mission  
  ./mission-system.sh milestones complete-udos-v1-1
  
  # Show statistics
  ./mission-system.sh stats

INTEGRATION:
  🗺️  Missions integrate with the Advanced Mapping System
  📊 Analytics feed into the Enhanced Dashboard
  📝 All activity is tracked in uMemory
  🎯 VS Code tasks available for mission management

EOF
}

# Main execution
main() {
    case "${1:-help}" in
        create)
            if [[ -z "$2" ]]; then
                log_error "Mission name is required"
                echo "Usage: $0 create <name> <description> [latitude] [longitude]"
                exit 1
            fi
            create_mission "$2" "$3" "$4" "$5"
            ;;
        milestone)
            if [[ -z "$2" || -z "$3" ]]; then
                log_error "Mission ID and milestone name are required"
                echo "Usage: $0 milestone <mission_id> <name> <description>"
                exit 1
            fi
            create_milestone "$2" "$3" "$4"
            ;;
        list)
            list_missions
            ;;
        milestones)
            if [[ -z "$2" ]]; then
                log_error "Mission ID is required"
                echo "Usage: $0 milestones <mission_id>"
                exit 1
            fi
            list_milestones "$2"
            ;;
        stats)
            show_stats
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
