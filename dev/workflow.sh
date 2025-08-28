#!/bin/bash
# dev/workflow.sh - Development workflow interface
# Provides access to workflow manager for development activities

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source logging
source "$UDOS_ROOT/uCORE/code/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if workflow manager exists
WORKFLOW_MANAGER="$UDOS_ROOT/uCORE/code/workflow-manager.sh"

if [ ! -f "$WORKFLOW_MANAGER" ]; then
    log_error "Workflow manager not found at: $WORKFLOW_MANAGER"
    exit 1
fi

# Development-specific workflow functions

# ASSIST mode for development
assist_mode() {
    local action="${1:-status}"

    case "$action" in
        enter)
            echo -e "${CYAN}🧠 Entering ASSIST Mode for Development${NC}"
            "$WORKFLOW_MANAGER" assist enter development
            ;;
        exit)
            echo -e "${CYAN}👤 Exiting ASSIST Mode${NC}"
            "$WORKFLOW_MANAGER" assist exit
            ;;
        finalize)
            echo -e "${CYAN}📋 Finalizing Development Session${NC}"
            generate_session_summary
            auto_commit_changes
            ;;
        analyze)
            echo -e "${CYAN}🔍 Analyzing Development Context${NC}"
            analyze_development_context
            ;;
        next)
            echo -e "${CYAN}🎯 Recommending Next Development Task${NC}"
            recommend_next_task
            ;;
        *)
            "$WORKFLOW_MANAGER" assist "$action"
            ;;
    esac
}

# Generate session summary for development
generate_session_summary() {
    log_info "Generating development session summary..."

    local timestamp=$(date '+%Y%m%d-%H%M%S%Z')
    local session_file="$UDOS_ROOT/sandbox/logs/session-finalization-${timestamp}.md"

    cat > "$session_file" << EOF
# Session Finalization - $(date '+%d %B %Y') $(date '+%I:%M %p %Z')

## Session Summary
Development session focused on startup/setup system analysis and fixes.

## Key Achievements
- Identified corrupted configuration files (installation.md, user.md)
- Created missing dev/workflow.sh interface script
- Analyzed workflow manager integration issues
- Reviewed ASSIST mode implementation

## Files Modified
- Added: dev/workflow.sh (development workflow interface)
- Identified: uMEMORY/user/installation.md (needs regeneration)
- Identified: sandbox/user.md (needs regeneration)

## Next Development Priority
Fix startup/setup system by regenerating user and installation profiles with proper variable processing.

## Technical Notes
- Variable system integration with GET/SET commands needs completion
- ASSIST mode requires proper session finalization automation
- Startup banner system integration needs testing
EOF

    log_success "Session summary generated: $session_file"
}

# Auto-commit development changes
auto_commit_changes() {
    log_info "Auto-committing development changes..."

    cd "$UDOS_ROOT"

    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log_warning "No changes to commit"
        return 0
    fi

    # Generate commit message from session
    local commit_msg="Session: $(date '+%d %B %Y') - Startup/Setup System Analysis & Fixes

Key Changes:
- Added dev/workflow.sh development interface
- Identified corrupted configuration files
- Analyzed ASSIST mode integration issues

Files Modified:
- Added: dev/workflow.sh

Next Recommended Actions:
- Regenerate user and installation profiles
- Fix variable system integration
- Test startup banner system"

    git add -A
    git commit -m "$commit_msg"

    log_success "Changes committed to git"
}

# Analyze current development context
analyze_development_context() {
    echo -e "${YELLOW}📊 Development Context Analysis:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Current branch and status
    echo "🌿 Git Status:"
    echo "  Branch: $(git branch --show-current)"
    echo "  Modified files: $(git diff --name-only | wc -l | tr -d ' ')"
    echo "  Staged files: $(git diff --cached --name-only | wc -l | tr -d ' ')"

    # Configuration status
    echo ""
    echo "⚙️ Configuration Status:"
    # Check main installation profile
    if [ -f "$UDOS_ROOT/uMEMORY/installation.md" ]; then
        if grep -q "Commands: DEFINE, SET, GET" "$UDOS_ROOT/uMEMORY/installation.md"; then
            echo "  Installation Profile: ❌ CORRUPTED (contains placeholder text)"
        else
            echo "  Installation Profile: ✅ Valid"
        fi
    else
        echo "  Installation Profile: ❌ Missing"
    fi

    # Check for corrupted user installation file
    if [ -f "$UDOS_ROOT/uMEMORY/user/installation.md" ]; then
        if grep -q "Commands: DEFINE, SET, GET" "$UDOS_ROOT/uMEMORY/user/installation.md"; then
            echo "  Legacy Installation File: ❌ CORRUPTED (needs cleanup)"
        fi
    fi

    if [ -f "$UDOS_ROOT/sandbox/user.md" ]; then
        if grep -q "Commands: DEFINE, SET, GET" "$UDOS_ROOT/sandbox/user.md"; then
            echo "  User Profile: ❌ CORRUPTED (contains placeholder text)"
        else
            echo "  User Profile: ✅ Valid"
        fi
    else
        echo "  User Profile: ❌ Missing"
    fi

    # Current role
    if [ -f "$UDOS_ROOT/sandbox/current-role.conf" ]; then
        local current_role=$(grep "ROLE=" "$UDOS_ROOT/sandbox/current-role.conf" | cut -d'"' -f2)
        echo "  Current Role: $current_role"
    fi

    # Development environment
    echo ""
    echo "🔧 Development Environment:"
    echo "  Workflow Manager: $([ -f "$WORKFLOW_MANAGER" ] && echo "✅ Available" || echo "❌ Missing")"
    echo "  ASSIST Mode: $([ -f "$UDOS_ROOT/sandbox/workflow/assist-mode.json" ] && echo "✅ Available" || echo "❌ Not configured")"
    echo "  VS Code Tasks: $([ -f "$UDOS_ROOT/.vscode/tasks.json" ] && echo "✅ Configured" || echo "❌ Missing")"
}

# Recommend next development task
recommend_next_task() {
    echo -e "${YELLOW}🎯 Next Development Task Recommendations:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check for critical issues first
    local critical_issues=0

    if [ -f "$UDOS_ROOT/uMEMORY/user/installation.md" ] && grep -q "Commands: DEFINE, SET, GET" "$UDOS_ROOT/uMEMORY/user/installation.md"; then
        echo "🚨 CRITICAL: Clean up corrupted legacy installation file"
        echo "   Action: Move uMEMORY/user/installation.md to trash"
        critical_issues=$((critical_issues + 1))
    fi

    if [ -f "$UDOS_ROOT/sandbox/user.md" ] && grep -q "Commands: DEFINE, SET, GET" "$UDOS_ROOT/sandbox/user.md"; then
        echo "🚨 CRITICAL: Fix corrupted user profile"
        echo "   Action: Run user setup to regenerate profile"
        critical_issues=$((critical_issues + 1))
    fi

    if [ $critical_issues -gt 0 ]; then
        echo ""
        echo "🔧 Recommended Fix Command:"
        echo "   ./uCORE/code/utilities/setup.sh"
        echo ""
        echo "📋 Priority: Fix configuration corruption before continuing development"
    else
        echo "✅ No critical issues detected"
        echo ""
        echo "📈 Development Priorities:"
        echo "1. Complete variable system integration (GET/SET commands)"
        echo "2. Test startup banner system integration"
        echo "3. Implement session finalization automation"
        echo "4. Enhance ASSIST mode recommendations"
    fi
}

# List development roadmaps
list_roadmaps() {
    echo -e "${CYAN}📋 Current Development Roadmaps:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local roadmap_dir="$UDOS_ROOT/docs/roadmaps/current"
    if [ -d "$roadmap_dir" ]; then
        find "$roadmap_dir" -name "*.md" | while read -r roadmap; do
            local basename=$(basename "$roadmap" .md)
            echo "📄 $basename"
        done
    else
        echo "❌ No roadmaps directory found"
    fi
}

# View recent development logs
view_logs() {
    echo -e "${CYAN}📝 Recent Development Logs:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local logs_dir="$UDOS_ROOT/sandbox/logs"
    if [ -d "$logs_dir" ]; then
        find "$logs_dir" -name "session-finalization-*.md" -mtime -7 | sort -r | head -5 | while read -r log_file; do
            local basename=$(basename "$log_file")
            echo "📄 $basename"
        done
    else
        echo "❌ No logs directory found"
    fi
}

# Interactive development workflow
interactive() {
    echo -e "${CYAN}🤖 Interactive Development Workflow${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Available commands:"
    echo "1. analyze  - Analyze current development context"
    echo "2. assist   - Enter ASSIST mode for development"
    echo "3. next     - Get next task recommendations"
    echo "4. roadmaps - List current roadmaps"
    echo "5. logs     - View recent development logs"
    echo "6. status   - Show workflow status"
    echo "7. exit     - Exit interactive mode"
    echo ""

    while true; do
        echo -n "dev> "
        read -r command

        case "$command" in
            analyze)
                analyze_development_context
                ;;
            assist)
                assist_mode enter
                ;;
            next)
                recommend_next_task
                ;;
            roadmaps)
                list_roadmaps
                ;;
            logs)
                view_logs
                ;;
            status)
                "$WORKFLOW_MANAGER" status
                ;;
            exit|quit)
                echo "Exiting interactive mode"
                break
                ;;
            *)
                echo "Unknown command: $command"
                ;;
        esac
        echo ""
    done
}

# Main command interface
main() {
    local command="${1:-help}"

    case "$command" in
        assist)
            local action="${2:-status}"
            assist_mode "$action"
            ;;
        analyze)
            analyze_development_context
            ;;
        next)
            recommend_next_task
            ;;
        roadmaps|list)
            list_roadmaps
            ;;
        logs)
            view_logs
            ;;
        interactive)
            interactive
            ;;
        status)
            "$WORKFLOW_MANAGER" status
            ;;
        help)
            echo -e "${CYAN}🛠️  Development Workflow Interface${NC}"
            echo "Provides development-focused workflow management"
            echo ""
            echo "Commands:"
            echo "  assist [enter|exit|analyze|next]  - ASSIST mode management"
            echo "  analyze                           - Analyze development context"
            echo "  next                             - Get next task recommendations"
            echo "  roadmaps                         - List current roadmaps"
            echo "  logs                             - View recent development logs"
            echo "  interactive                      - Interactive workflow mode"
            echo "  status                           - Show workflow status"
            echo ""
            echo "Examples:"
            echo "  ./dev/workflow.sh assist enter    # Enter ASSIST mode"
            echo "  ./dev/workflow.sh analyze          # Analyze current context"
            echo "  ./dev/workflow.sh next             # Get recommendations"
            ;;
        *)
            # Pass through to workflow manager
            "$WORKFLOW_MANAGER" "$@"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
