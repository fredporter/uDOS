#!/bin/bash
# Dev Mode Detection and Session Management
# Automatically detects VS Code/AI development sessions

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🔍 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_dev() { echo -e "${PURPLE}🛠️  $1${NC}"; }

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIZARD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UDOS_ROOT="$(cd "$WIZARD_ROOT/.." && pwd)"

# Dev mode detection
detect_dev_mode() {
    local dev_mode_score=0
    local detection_reasons=()
    
    # Check for VS Code environment
    if [[ -n "${VSCODE_PID:-}" || -n "${TERM_PROGRAM:-}" && "${TERM_PROGRAM}" == "vscode" ]]; then
        ((dev_mode_score += 3))
        detection_reasons+=("VS Code environment detected")
    fi
    
    # Check for AI assistant indicators
    if command -v code >/dev/null 2>&1; then
        local vscode_extensions="$(code --list-extensions 2>/dev/null || echo "")"
        if echo "$vscode_extensions" | grep -q "github.copilot\|anthropic.claude"; then
            ((dev_mode_score += 2))
            detection_reasons+=("AI assistant extension detected")
        fi
    elif [[ -d "$HOME/.vscode/extensions" ]]; then
        if find "$HOME/.vscode/extensions" -name "*copilot*" -o -name "*claude*" | head -1 | grep -q .; then
            ((dev_mode_score += 1))
            detection_reasons+=("AI assistant extension found in extensions dir")
        fi
    fi
    
    # Check for active development indicators
    if [[ -f "$UDOS_ROOT/.git/config" ]]; then
        ((dev_mode_score += 1))
        detection_reasons+=("Git repository detected")
    fi
    
    # Check for recent file modifications
    if find "$UDOS_ROOT" -name "*.sh" -o -name "*.md" -newer "$UDOS_ROOT/.git/COMMIT_EDITMSG" 2>/dev/null | head -1 | grep -q .; then
        ((dev_mode_score += 1))
        detection_reasons+=("Recent file modifications detected")
    fi
    
    # Check for wizard directory usage
    if [[ "$PWD" == *"/wizard"* || "$PWD" == "$WIZARD_ROOT"* ]]; then
        ((dev_mode_score += 2))
        detection_reasons+=("Working in wizard directory")
    fi
    
    # Check for development patterns
    if ps aux | grep -v grep | grep -q "code\|claude\|copilot"; then
        ((dev_mode_score += 1))
        detection_reasons+=("Development tools running")
    fi
    
    # Determine dev mode status
    local dev_mode_active="false"
    if [[ $dev_mode_score -ge 3 ]]; then
        dev_mode_active="true"
    fi
    
    echo "DEV_MODE_ACTIVE=$dev_mode_active"
    echo "DEV_MODE_SCORE=$dev_mode_score"
    echo "DEV_MODE_REASONS=${detection_reasons[*]}"
}

# Initialize development session
init_dev_session() {
    local session_name="${1:-Development-Session}"
    local session_id="$(date +"%Y%m%d%H%M%S" | md5sum | cut -c1-8)"
    local session_date="$(date +%Y%m%d)"
    local session_file="$WIZARD_ROOT/notes/uDEV-${session_date}-${session_name}.md"
    
    log_info "Initializing development session..."
    
    # Create session file
    cat > "$session_file" << EOF
# uDEV-${session_date}-${session_name}
**Created:** $(date +"%Y-%m-%d %H:%M")  
**Session ID:** ${session_id}  
**Date:** ${session_date}  
**Type:** Development Session  
**Environment:** VS Code + AI Assistant  
**Location:** wizard/notes/

---

## 🎯 SESSION OBJECTIVES

### Primary Goals
- [ ] 

### Secondary Goals
- [ ] 

---

## 📝 DEVELOPMENT LOG

### $(date +"%H:%M") - Session Start
- Initialized development session
- Environment: $(detect_dev_mode | grep REASONS | cut -d= -f2)

### Progress Notes
<!-- Add development progress notes here -->

---

## 🔧 TECHNICAL DECISIONS

### Architecture Changes
<!-- Document architectural decisions made during this session -->

### Implementation Notes
<!-- Record implementation details and code changes -->

---

## 🐛 ISSUES & SOLUTIONS

### Issues Encountered
<!-- Document problems encountered -->

### Solutions Implemented
<!-- Record how issues were resolved -->

---

## 🎯 NEXT STEPS

### Immediate Tasks
- [ ] 

### Future Considerations
- [ ] 

---

## 📊 SESSION METRICS

- **Duration:** [To be updated on session close]
- **Files Modified:** [Auto-tracked]
- **Commands Executed:** [Auto-tracked]
- **Git Commits:** [Auto-tracked]

---

*Session managed by uDOS Dev Mode Framework*
EOF
    
    # Set environment variables
    export UDOS_DEV_MODE="true"
    export UDOS_DEV_SESSION="$session_id"
    export UDOS_DEV_SESSION_FILE="$session_file"
    export UDOS_DEV_ROOT="$WIZARD_ROOT"
    export UDOS_DEV_NOTES="$WIZARD_ROOT/notes"
    
    # Create session state file
    cat > "$WIZARD_ROOT/.dev-session-${session_id}" << EOF
SESSION_ID="$session_id"
SESSION_NAME="$session_name"
SESSION_FILE="$session_file"
SESSION_START="$(date +%s)"
SESSION_DATE="$(date +"%Y-%m-%d %H:%M")"
ENVIRONMENT="VS Code + AI Assistant"
STATUS="Active"
EOF
    
    log_success "Development session initialized: $session_id"
    log_info "Session file: $session_file"
    log_dev "Use 'dev_mode.sh status' to check session status"
    
    echo "$session_id"
}

# Check development session status
check_dev_status() {
    log_info "Development Mode Status Check"
    
    # Detect current dev mode
    local detection_output="$(detect_dev_mode)"
    local dev_mode_active="$(echo "$detection_output" | grep DEV_MODE_ACTIVE | cut -d= -f2)"
    local dev_mode_score="$(echo "$detection_output" | grep DEV_MODE_SCORE | cut -d= -f2)"
    local dev_mode_reasons="$(echo "$detection_output" | grep DEV_MODE_REASONS | cut -d= -f2-)"
    
    echo
    echo "🔍 Detection Results:"
    echo "   Active: $dev_mode_active"
    echo "   Score: $dev_mode_score/8"
    echo "   Reasons: $dev_mode_reasons"
    
    # Check for active sessions
    echo
    echo "📝 Active Sessions:"
    if ls "$WIZARD_ROOT"/.dev-session-* >/dev/null 2>&1; then
        for session_file in "$WIZARD_ROOT"/.dev-session-*; do
            if [[ -f "$session_file" ]]; then
                source "$session_file"
                echo "   Session: $SESSION_ID ($SESSION_NAME)"
                echo "   Started: $SESSION_DATE"
                echo "   Status: $STATUS"
                echo "   File: $SESSION_FILE"
            fi
        done
    else
        echo "   No active sessions found"
    fi
    
    # Environment info
    echo
    echo "🌍 Environment:"
    echo "   Working Directory: $PWD"
    echo "   Wizard Root: $WIZARD_ROOT"
    echo "   uDOS Root: $UDOS_ROOT"
    echo "   VS Code: ${VSCODE_PID:+Active}"
    echo "   Terminal: ${TERM_PROGRAM:-Unknown}"
}

# Close development session
close_dev_session() {
    local session_id="${1:-}"
    
    if [[ -z "$session_id" ]]; then
        # Find active session
        if [[ -n "${UDOS_DEV_SESSION:-}" ]]; then
            session_id="$UDOS_DEV_SESSION"
        else
            log_error "No session ID provided and no active session found"
            return 1
        fi
    fi
    
    local session_state_file="$WIZARD_ROOT/.dev-session-${session_id}"
    
    if [[ ! -f "$session_state_file" ]]; then
        log_error "Session not found: $session_id"
        return 1
    fi
    
    # Load session info
    source "$session_state_file"
    
    log_info "Closing development session: $session_id"
    
    # Calculate session duration
    local session_end="$(date +%s)"
    local duration=$((session_end - SESSION_START))
    local duration_formatted="$(date -u -d @$duration +"%H:%M:%S" 2>/dev/null || echo "${duration}s")"
    
    # Update session file with closure info
    if [[ -f "$SESSION_FILE" ]]; then
        cat >> "$SESSION_FILE" << EOF

---

## 📊 SESSION CLOSURE

**Session Closed:** $(date +"%Y-%m-%d %H:%M")  
**Duration:** $duration_formatted  
**Total Time:** ${duration} seconds

### Final Metrics
- **Session ID:** $session_id
- **Duration:** $duration_formatted
- **Files in Session:** $(find "$WIZARD_ROOT/notes" -name "*${session_id}*" | wc -l)

*Session closed automatically by Dev Mode Framework*
EOF
    fi
    
    # Update session state
    sed -i '' 's/STATUS=Active/STATUS=Closed/' "$session_state_file" 2>/dev/null || \
    sed -i 's/STATUS=Active/STATUS=Closed/' "$session_state_file"
    
    # Clean up environment
    unset UDOS_DEV_MODE UDOS_DEV_SESSION UDOS_DEV_SESSION_FILE
    
    log_success "Session closed: $session_id (Duration: $duration_formatted)"
}

# Main command processing
main() {
    case "${1:-detect}" in
        detect)
            detect_dev_mode
            ;;
        init)
            init_dev_session "${2:-Development-Session}"
            ;;
        status)
            check_dev_status
            ;;
        close)
            close_dev_session "${2:-}"
            ;;
        help|--help|-h)
            cat << 'EOF'
Dev Mode Detection and Session Management

Usage:
  dev-mode-detection.sh detect          - Detect development mode
  dev-mode-detection.sh init [name]     - Initialize development session
  dev-mode-detection.sh status          - Check development mode status
  dev-mode-detection.sh close [id]      - Close development session
  dev-mode-detection.sh help            - Show this help

Development mode is automatically detected based on:
- VS Code environment
- AI assistant presence
- Git repository activity
- File modification patterns
- Working directory location

Session files are created in wizard/notes/ with uHEX naming convention.
EOF
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use 'dev-mode-detection.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
