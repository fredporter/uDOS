#!/bin/bash
# Mission/Dashboard Integration for uDOS v1.1.0
# Connects mission data to the Enhanced Analytics Dashboard

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
ANALYTICS_DIR="${UMEM}/analytics"
STATE_DIR="${UMEM}/state"

# Ensure analytics directory exists
mkdir -p "$ANALYTICS_DIR" "$STATE_DIR"

# Generate mission analytics for dashboard
generate_mission_analytics() {
    local missions_count=0
    local active_missions=0
    local total_milestones=0
    local completed_milestones=0
    
    # Count missions
    if [[ -d "${UMEM}/missions" ]]; then
        missions_count=$(find "${UMEM}/missions" -name "*.md" -type f | wc -l | tr -d ' ')
        
        # Count active missions
        for mission_file in "${UMEM}/missions"/*.md; do
            if [[ -f "$mission_file" ]]; then
                local status=$(grep "**Status**:" "$mission_file" | head -1 | sed 's/.*Status\*\*: //' | tr -d '\n\r')
                if [[ "$status" == *"Active"* ]]; then
                    active_missions=$((active_missions + 1))
                fi
            fi
        done
    fi
    
    # Count milestones
    if [[ -d "${UMEM}/milestones" ]]; then
        total_milestones=$(find "${UMEM}/milestones" -name "*.md" -type f | wc -l | tr -d ' ')
        
        # Count completed milestones (simplified check)
        for milestone_file in "${UMEM}/milestones"/*.md; do
            if [[ -f "$milestone_file" ]]; then
                if grep -q "✅.*Complete\|Done\|Achieved" "$milestone_file"; then
                    completed_milestones=$((completed_milestones + 1))
                fi
            fi
        done
    fi
    
    # Calculate completion rate
    local completion_rate=0
    if [[ $total_milestones -gt 0 ]]; then
        completion_rate=$(( (completed_milestones * 100) / total_milestones ))
    fi
    
    # Generate JSON for dashboard
    cat > "${ANALYTICS_DIR}/mission-analytics.json" << EOF
{
    "mission_overview": {
        "total_missions": $missions_count,
        "active_missions": $active_missions,
        "total_milestones": $total_milestones,
        "completed_milestones": $completed_milestones,
        "completion_rate": $completion_rate,
        "last_updated": "$(date -Iseconds)"
    },
    "system_integration": {
        "dashboard_integration": true,
        "mapping_integration": true,
        "analytics_tracking": true,
        "vscode_integration": true
    },
    "recent_activity": []
}
EOF
    
    echo "✅ Mission analytics generated: ${ANALYTICS_DIR}/mission-analytics.json"
}

# Create mission widget for dashboard
create_mission_widget() {
    cat > "${STATE_DIR}/mission-widget.html" << 'EOF'
<!-- Mission Control Widget for uDOS Dashboard -->
<div class="mission-widget" style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 10px;
    color: white;
    min-width: 300px;
">
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <span style="font-size: 24px; margin-right: 10px;">🎯</span>
        <h3 style="margin: 0; font-size: 18px;">Mission Control</h3>
    </div>
    
    <div id="mission-stats" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div class="stat-item">
            <div style="font-size: 24px; font-weight: bold;" id="total-missions">-</div>
            <div style="font-size: 12px; opacity: 0.8;">Total Missions</div>
        </div>
        <div class="stat-item">
            <div style="font-size: 24px; font-weight: bold;" id="active-missions">-</div>
            <div style="font-size: 12px; opacity: 0.8;">Active</div>
        </div>
        <div class="stat-item">
            <div style="font-size: 24px; font-weight: bold;" id="total-milestones">-</div>
            <div style="font-size: 12px; opacity: 0.8;">Milestones</div>
        </div>
        <div class="stat-item">
            <div style="font-size: 24px; font-weight: bold;" id="completion-rate">-</div>
            <div style="font-size: 12px; opacity: 0.8;">Progress</div>
        </div>
    </div>
    
    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
        <div style="font-size: 12px; opacity: 0.8;" id="last-updated">Last updated: -</div>
    </div>
</div>

<script>
// Update mission widget data
function updateMissionWidget() {
    fetch('/Users/agentdigital/uDOS/uMemory/analytics/mission-analytics.json')
        .then(response => response.json())
        .then(data => {
            const overview = data.mission_overview;
            document.getElementById('total-missions').textContent = overview.total_missions;
            document.getElementById('active-missions').textContent = overview.active_missions;
            document.getElementById('total-milestones').textContent = overview.total_milestones;
            document.getElementById('completion-rate').textContent = overview.completion_rate + '%';
            
            const lastUpdated = new Date(overview.last_updated);
            document.getElementById('last-updated').textContent = 
                'Last updated: ' + lastUpdated.toLocaleTimeString();
        })
        .catch(error => {
            console.log('Mission analytics not available:', error);
        });
}

// Update every 10 seconds
updateMissionWidget();
setInterval(updateMissionWidget, 10000);
</script>
EOF
    
    echo "✅ Mission widget created: ${STATE_DIR}/mission-widget.html"
}

# Update dashboard integration
update_dashboard() {
    generate_mission_analytics
    create_mission_widget
    
    # Trigger dashboard refresh if running
    if pgrep -f "dash.sh" > /dev/null; then
        echo "🔄 Dashboard refresh triggered"
        killall -USR1 bash 2>/dev/null || true
    fi
}

# Main execution
case "${1:-update}" in
    "analytics"|"generate")
        generate_mission_analytics
        ;;
    "widget")
        create_mission_widget
        ;;
    "update"|"refresh")
        update_dashboard
        ;;
    *)
        echo "Usage: $0 [analytics|widget|update]"
        echo "  analytics - Generate mission analytics JSON"
        echo "  widget    - Create mission widget HTML"
        echo "  update    - Update dashboard with latest mission data"
        ;;
esac
