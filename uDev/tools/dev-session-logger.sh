#!/bin/bash

# uDOS Development Session Logger
# Automatically logs development activities in uLOG v1.3 format

set -e

# Configuration
DEV_LOGS_DIR="/Users/agentdigital/uDOS/uDEV/logs"
TIMEZONE_CODE="28"
CURRENT_DATE=$(date +%Y%m%d-%H%M)
SESSION_ID="SS$(date +%m%d)"

# Ensure logs directory exists
mkdir -p "$DEV_LOGS_DIR"

# Session log file
SESSION_LOG="$DEV_LOGS_DIR/uLOG-$CURRENT_DATE-$TIMEZONE_CODE-00$SESSION_ID.md"

# Function to log development activity
log_dev_activity() {
    local activity_type="$1"
    local description="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    cat >> "$SESSION_LOG" << EOF

### [$timestamp] $activity_type

$description

EOF
}

# Function to start development session
start_dev_session() {
    local session_title="$1"
    local objectives="$2"
    
    cat > "$SESSION_LOG" << EOF
# uLOG Development Session

**Session ID**: $SESSION_ID  
**Started**: $(date "+%Y-%m-%d %H:%M:%S AEDT")  
**Timezone**: $TIMEZONE_CODE (Australian Eastern Time)  
**Environment**: uDEV Wizard User Mode  
**Title**: $session_title

## 🎯 Session Objectives

$objectives

## 🔄 Activity Log

### [$(date "+%Y-%m-%d %H:%M:%S")] SESSION_START

Development session initiated in uDEV environment.
- Working directory: $(pwd)
- Git branch: $(git branch --show-current 2>/dev/null || echo "N/A")
- VS Code workspace: Active

EOF

    echo "🚀 Development session started: $SESSION_LOG"
    echo "📝 Use 'log_dev_activity' to record progress"
}

# Function to end development session
end_dev_session() {
    local summary="$1"
    
    cat >> "$SESSION_LOG" << EOF

### [$(date "+%Y-%m-%d %H:%M:%S")] SESSION_END

$summary

## 📊 Session Summary

**Duration**: Started $(head -5 "$SESSION_LOG" | grep "Started:" | cut -d: -f2-)  
**Completed**: $(date "+%Y-%m-%d %H:%M:%S AEDT")  
**Status**: COMPLETE  

### Files Modified
$(git diff --name-only 2>/dev/null | sed 's/^/- /' || echo "- No git changes detected")

### Next Actions
- Archive session log to summaries if significant
- Update related tasks in sandbox/tasks/
- Commit changes to version control

---

*uDOS Development Session Log - Wizard User Mode*
EOF

    echo "✅ Development session ended: $SESSION_LOG"
}

# Main script logic
case "${1:-help}" in
    "start")
        start_dev_session "${2:-Development Session}" "${3:-General development activities}"
        ;;
    "log")
        log_dev_activity "${2:-ACTIVITY}" "${3:-Development activity logged}"
        ;;
    "end")
        end_dev_session "${2:-Session completed successfully}"
        ;;
    "help"|*)
        cat << EOF
🧙‍♂️ uDOS Development Session Logger

Usage:
  $0 start "Session Title" "Objectives"
  $0 log "ACTIVITY_TYPE" "Description"
  $0 end "Summary"

Examples:
  $0 start "Feature Development" "Implement new ASSIST mode enhancements"
  $0 log "CODE_CHANGE" "Updated timezone mapper script"
  $0 log "TEST_RESULT" "All validation tests passing"
  $0 end "Successfully implemented timezone integration"

Current session log: $SESSION_LOG
EOF
        ;;
esac
