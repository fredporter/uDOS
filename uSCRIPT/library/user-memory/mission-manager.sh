#!/bin/bash
# mission-manager.sh - User Mission Management System
# Manages user missions, objectives, and progress tracking

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
USER_DATA_DIR="$UDOS_ROOT/uMEMORY/user"
MISSIONS_DIR="$USER_DATA_DIR/missions"
MILESTONES_DIR="$USER_DATA_DIR/milestones"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Ensure directories exist
mkdir -p "$MISSIONS_DIR" "$MILESTONES_DIR"

# Show mission dashboard
show_dashboard() {
    echo -e "${CYAN}[DASHBOARD]${NC} Mission & Milestone Dashboard"
    echo "============================================="
    
    # Count missions by status
    local total_missions=0
    local active_missions=0
    local completed_missions=0
    
    if [[ -d "$MISSIONS_DIR" ]]; then
        for mission_file in "$MISSIONS_DIR"/*.md; do
            if [[ -f "$mission_file" ]]; then
                local status=$(grep "status:" "$mission_file" 2>/dev/null | sed 's/status: "\(.*\)"/\1/' || echo "active")
                ((total_missions++))
                if [[ "$status" == "active" ]]; then
                    ((active_missions++))
                elif [[ "$status" == "completed" ]]; then
                    ((completed_missions++))
                fi
            fi
        done
    fi
    
    # Count milestones
    local total_milestones=0
    if [[ -d "$MILESTONES_DIR" ]]; then
        total_milestones=$(ls -1 "$MILESTONES_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    fi
    
    echo "## Summary"
    echo "- **Active Missions**: $active_missions"
    echo "- **Completed Missions**: $completed_missions"
    echo "- **Total Missions**: $total_missions"
    echo "- **Total Milestones**: $total_milestones"
    echo ""
    
    echo "## Active Missions"
    if [[ -d "$MISSIONS_DIR" ]] && [[ -n "$(ls -A "$MISSIONS_DIR" 2>/dev/null)" ]]; then
        for mission_file in "$MISSIONS_DIR"/*.md; do
            if [[ -f "$mission_file" ]]; then
                local name=$(basename "$mission_file" .md | sed 's/^uTASK-[A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9]-//' | sed 's/^mission-//' | sed 's/-20[0-9][0-9][0-9][0-9][0-9][0-9]$//')
                local created=$(date -r "$mission_file" +%Y-%m-%d 2>/dev/null || echo "unknown")
                echo "- [active] $name - Created: $created"
            fi
        done
    else
        echo "No missions found"
    fi
    echo ""
    
    # Show recent milestones
    echo "## Recent Milestones (Last 5)"
    if [[ -d "$MILESTONES_DIR" ]] && [[ -n "$(ls -A "$MILESTONES_DIR" 2>/dev/null)" ]]; then
        for milestone_file in $(ls -t "$MILESTONES_DIR"/*.md 2>/dev/null | head -5); do
            local name=$(basename "$milestone_file" .md | sed 's/^uTASK-[A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9]-//' | sed 's/^milestone-//' | sed 's/-20[0-9][0-9][0-9][0-9][0-9][0-9]$//')
            local achieved=$(date -r "$milestone_file" +%Y-%m-%d 2>/dev/null || echo "unknown")
            echo "- $name - $achieved"
        done
    else
        echo "No milestones found"
    fi
}

# Main function
main() {
    case "${1:-dashboard}" in
        "dashboard")
            show_dashboard
            ;;
        *)
            echo "Usage: $0 {dashboard}"
            ;;
    esac
}

# Run main function
main "$@"
