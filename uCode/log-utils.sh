#!/bin/bash
# uDOS Logging Utilities
# Provides consistent logging functions for system vs user logs

# Set up paths
UHOME="${UHOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
UDEV="$UHOME/uDev"
UMEM="$UHOME/uMemory"

# System logging (goes to uDev)
log_system() {
    local level="$1"
    local message="$2"
    local log_file="$UDEV/logs/system/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$log_file"
}

log_error() {
    local message="$1"
    local source="${2:-unknown}"
    local log_file="$UDEV/logs/errors/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] [$source] $message" >> "$log_file"
    echo -e "\033[0;31m❌ ERROR: $message\033[0m" >&2
}

log_warning() {
    local message="$1"
    local source="${2:-unknown}"
    local log_file="$UDEV/logs/system/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] [$source] $message" >> "$log_file"
    echo -e "\033[1;33m⚠️ WARNING: $message\033[0m" >&2
}

log_debug() {
    local message="$1"
    local source="${2:-unknown}"
    
    # Only log debug if DEBUG environment variable is set
    if [[ "${DEBUG:-}" == "true" ]]; then
        local log_file="$UDEV/logs/debug/$(date +%Y%m%d).log"
        mkdir -p "$(dirname "$log_file")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] [$source] $message" >> "$log_file"
        echo -e "\033[0;36m🔍 DEBUG: $message\033[0m" >&2
    fi
}

log_session() {
    local session_id="$1"
    local event="$2"
    local log_file="$UDEV/logs/sessions/${session_id}.log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$log_file"
}

log_device() {
    local device="$1"
    local event="$2"
    local log_file="$UDEV/logs/devices/$(date +%Y%m%d)-${device}.log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$log_file"
}

# Script execution logging
log_script_start() {
    local script_name="$1"
    local script_type="${2:-unknown}"
    local log_file="$UDEV/logs/scripts/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [START] [$script_type] $script_name" >> "$log_file"
}

log_script_end() {
    local script_name="$1"
    local exit_code="${2:-0}"
    local duration="${3:-unknown}"
    local log_file="$UDEV/logs/scripts/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    local status="SUCCESS"
    [[ "$exit_code" != "0" ]] && status="FAILED"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [END] [$status] $script_name (exit: $exit_code, duration: ${duration}s)" >> "$log_file"
}

# Performance logging
log_performance() {
    local operation="$1"
    local duration="$2"
    local details="${3:-}"
    local log_file="$UDEV/logs/performance/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $operation: ${duration}s $details" >> "$log_file"
}

# Cleanup old logs (keep last 30 days)
cleanup_logs() {
    local days_to_keep="${1:-30}"
    
    find "$UDEV/logs" -name "*.log" -mtime +$days_to_keep -delete 2>/dev/null || true
    log_system "INFO" "Log cleanup completed (kept last $days_to_keep days)"
}

# Helper function to get user location (from identity or default)
get_user_location() {
    local identity_file="$UHOME/sandbox/identity.md"
    if [[ -f "$identity_file" ]] && grep -q "Location:" "$identity_file"; then
        # Extract location and convert to tile code format
        local location=$(grep "Location:" "$identity_file" | cut -d':' -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
        # Convert common locations to tile codes
        case "$location" in
            earth|default) echo "E001" ;;
            downtown|city|urban) echo "U001" ;;
            suburban|suburbs) echo "S001" ;;
            rural|country) echo "R001" ;;
            *) echo "E001" ;;  # Default tile code
        esac
    else
        echo "E001"  # Default Earth tile code
    fi
}

# Helper function to get standardized 3-letter timezone
get_timezone_code() {
    local tz=$(date +%Z)
    # Convert to standard 3-letter codes
    case "$tz" in
        AEST|AEDT) echo "AET" ;;  # Australian Eastern
        AWST|AWDT) echo "AWE" ;;  # Australian Western  
        ACST|ACDT) echo "ACE" ;;  # Australian Central
        EST|EDT) echo "EST" ;;    # Eastern Standard Time
        CST|CDT) echo "CST" ;;    # Central Standard Time
        MST|MDT) echo "MST" ;;    # Mountain Standard Time
        PST|PDT) echo "PST" ;;    # Pacific Standard Time
        UTC|GMT) echo "UTC" ;;    # Coordinated Universal Time
        BST|GMT) echo "GMT" ;;    # Greenwich Mean Time / British Summer Time
        CET|CEST) echo "CET" ;;   # Central European Time
        JST) echo "JST" ;;        # Japan Standard Time
        *) echo "UTC" ;;          # Default to UTC for unknown timezones
    esac
}

# User logging (flat structure in uMemory)  
log_move() {
    local message="$1"
    local daily_log="$UMEM/move-log-$(date +%Y-%m-%d).md"
    
    # Check message length (160 character limit for daily log)
    if [[ ${#message} -le 160 ]]; then
        # Short move: add to daily log
        echo "$(date '+%H:%M:%S'): $message" >> "$daily_log"
    else
        # Long move: create individual file with extended naming
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local location=$(get_user_location)
        local timezone=$(get_timezone_code)
        local move_file="$UMEM/move-${timestamp}-${location}-${timezone}.md"
        
        echo "# 🚀 Move - $(date '+%Y-%m-%d %H:%M:%S')" > "$move_file"
        echo "" >> "$move_file"
        echo "**📍 Tile Code:** \`$location\`" >> "$move_file"
        echo "**⏰ Timezone:** \`$timezone\`" >> "$move_file"
        echo "" >> "$move_file"
        echo "## Movement Details" >> "$move_file"
        echo "" >> "$move_file"
        echo "$message" >> "$move_file"
        echo "" >> "$move_file"
        echo "---" >> "$move_file"
        echo "*This move contributes to milestone progress and mission completion.*" >> "$move_file"
        
        # Also add a reference in daily log
        echo "$(date '+%H:%M:%S'): [Extended] See move-${timestamp}-${location}-${timezone}.md" >> "$daily_log"
    fi
}

log_mission() {
    local mission_id="$1"
    local event="$2"
    
    # Check if this is a complex/long mission (over 160 chars)
    if [[ ${#event} -gt 160 ]]; then
        # Extended mission file with location/timezone
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local location=$(get_user_location)
        local timezone=$(get_timezone_code)
        local mission_file="$UMEM/mission-${mission_id}-${timestamp}-${location}-${timezone}.md"
        
        echo "# 🎯 Mission: $mission_id" > "$mission_file"
        echo "" >> "$mission_file"
        echo "**📅 Created:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$mission_file"
        echo "**📍 Tile Code:** \`$location\`" >> "$mission_file"
        echo "**⏰ Timezone:** \`$timezone\`" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "## Mission Overview" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "$event" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "## Progress Tracking" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "- [ ] Planning Phase" >> "$mission_file"
        echo "- [ ] Execution Phase" >> "$mission_file"
        echo "- [ ] Review Phase" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "## Related Milestones" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "*Milestones achieved during this mission will be linked here.*" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "---" >> "$mission_file"
        echo "*Upon completion, valuable missions may be preserved as device legacy.*" >> "$mission_file"
    else
        # Simple mission file (can be used multiple times)
        local mission_file="$UMEM/mission-${mission_id}.md"
        
        if [[ ! -f "$mission_file" ]]; then
            echo "# 🎯 Mission: $mission_id" > "$mission_file"
            echo "" >> "$mission_file"
            echo "**📅 Created:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$mission_file"
            echo "" >> "$mission_file"
            echo "## Progress Log" >> "$mission_file"
            echo "" >> "$mission_file"
        fi
        echo "- **$(date '+%H:%M:%S'):** $event" >> "$mission_file"
    fi
}

log_milestone() {
    local milestone="$1"
    local description="$2"
    
    # Check if this is a complex/long milestone (over 160 chars total)
    local total_length=$((${#milestone} + ${#description}))
    if [[ $total_length -gt 160 ]]; then
        # Extended milestone file with location/timezone
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local location=$(get_user_location)
        local timezone=$(get_timezone_code)
        local milestone_file="$UMEM/milestone-${timestamp}-${location}-${timezone}.md"
        
        echo "# 🏆 Milestone: $milestone" > "$milestone_file"
        echo "" >> "$milestone_file"
        echo "**📅 Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$milestone_file"
        echo "**📍 Tile Code:** \`$location\`" >> "$milestone_file"
        echo "**⏰ Timezone:** \`$timezone\`" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "## Achievement Details" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "$description" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "## Contributing Moves" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "*Individual moves that contributed to this milestone:*" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "## Mission Impact" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "*This milestone contributes to mission completion:*" >> "$milestone_file"
        echo "" >> "$milestone_file"
        echo "---" >> "$milestone_file"
        echo "*Milestones are composed of individual moves and contribute to overall mission success.*" >> "$milestone_file"
        
        # Also add to monthly milestones log as reference
        local monthly_log="$UMEM/milestones-$(date +%Y-%m).md"
        if [[ ! -f "$monthly_log" ]]; then
            echo "# Milestones - $(date '+%B %Y')" > "$monthly_log"
            echo "" >> "$monthly_log"
        fi
        echo "## 🏆 $(date '+%Y-%m-%d') - $milestone [Extended]" >> "$monthly_log"
        echo "" >> "$monthly_log"
        echo "**📎 Reference:** See [milestone-${timestamp}-${location}-${timezone}.md](./milestone-${timestamp}-${location}-${timezone}.md)" >> "$monthly_log"
        echo "" >> "$monthly_log"
    else
        # Simple milestone in monthly log (can be used multiple times)
        local monthly_log="$UMEM/milestones-$(date +%Y-%m).md"
        if [[ ! -f "$monthly_log" ]]; then
            echo "# 🏆 Milestones - $(date '+%B %Y')" > "$monthly_log"
            echo "" >> "$monthly_log"
            echo "*Milestones are achievements composed of individual moves that contribute to mission completion.*" >> "$monthly_log"
            echo "" >> "$monthly_log"
        fi
        echo "## 🏆 $(date '+%Y-%m-%d') - $milestone" >> "$monthly_log"
        echo "" >> "$monthly_log"
        echo "$description" >> "$monthly_log"
        echo "" >> "$monthly_log"
    fi
}

# Mission completion and device legacy creation
log_mission_completion() {
    local mission_id="$1"
    local completion_summary="$2"
    local preserve_as_legacy="${3:-false}"
    
    local mission_file="$UMEM/mission-${mission_id}.md"
    
    if [[ -f "$mission_file" ]]; then
        # Mark mission as completed
        echo "" >> "$mission_file"
        echo "---" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "## ✅ Mission Completed" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "**📅 Completion Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "### Summary" >> "$mission_file"
        echo "" >> "$mission_file"
        echo "$completion_summary" >> "$mission_file"
        echo "" >> "$mission_file"
        
        # If marked for legacy preservation
        if [[ "$preserve_as_legacy" == "true" ]]; then
            local timestamp=$(date +%Y%m%d-%H%M%S)
            local location=$(get_user_location)
            local timezone=$(get_timezone_code)
            local legacy_file="$UMEM/legacy/legacy-${mission_id}-${timestamp}-${location}-${timezone}.md"
            
            mkdir -p "$UMEM/legacy"
            
            # Create enhanced legacy format
            echo "# 💎 Device Legacy: $mission_id" > "$legacy_file"
            echo "" >> "$legacy_file"
            echo "**📅 Preserved:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$legacy_file"
            echo "**📍 Tile Code:** \`$location\`" >> "$legacy_file"
            echo "**⏰ Timezone:** \`$timezone\`" >> "$legacy_file"
            echo "**🎯 Original Mission:** \`$mission_id\`" >> "$legacy_file"
            echo "" >> "$legacy_file"
            echo "## Legacy Value" >> "$legacy_file"
            echo "" >> "$legacy_file"
            echo "This completed mission has been preserved as device legacy for future reference and learning." >> "$legacy_file"
            echo "" >> "$legacy_file"
            echo "## Mission Archive" >> "$legacy_file"
            echo "" >> "$legacy_file"
            
            # Copy original mission content
            cat "$mission_file" >> "$legacy_file"
            
            # Add legacy reference to mission file
            echo "" >> "$mission_file"
            echo "**💎 Preserved as Legacy:** [legacy-${mission_id}-${timestamp}-${location}-${timezone}.md](./legacy/legacy-${mission_id}-${timestamp}-${location}-${timezone}.md)" >> "$mission_file"
            
            echo "Mission $mission_id completed and preserved as legacy: legacy-${mission_id}-${timestamp}-${location}-${timezone}.md"
        else
            echo "Mission $mission_id completed successfully."
        fi
    else
        echo "Warning: Mission file $mission_file not found."
    fi
}
