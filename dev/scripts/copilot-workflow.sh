#!/bin/bash
# Copilot Development Workflow Automation
# Handles automated git management, repo structure updates, and copilot instruction optimization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEV_ROOT="$UDOS_ROOT/dev"
COPILOT_DIR="$DEV_ROOT/copilot"

# Configuration
WORKFLOW_LOG="$DEV_ROOT/logs/copilot-workflow.log"
INSTRUCTION_FILE="$COPILOT_DIR/instructions/copilot-instructions.md"
CONTEXT_FILE="$COPILOT_DIR/context/development-context.md"
PROGRESS_FILE="$DEV_ROOT/progress-tracking.json"

# Logging function
log_workflow() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$WORKFLOW_LOG"
}

# Update repository structure using TREE DEV command
update_repo_structure() {
    log_workflow "🌳 Updating repository structure with TREE DEV command"

    local tree_file="$UDOS_ROOT/repo_structure.txt"
    local temp_tree="/tmp/udos-tree-$$.txt"

    # Generate comprehensive tree structure
    if command -v tree >/dev/null 2>&1; then
        tree -a -L 4 -I '.git|node_modules|__pycache__|*.pyc|.DS_Store|venv|*.log' "$UDOS_ROOT" > "$temp_tree"
    else
        # Fallback to find command with structure
        (cd "$UDOS_ROOT" && find . -type d -not -path './.git/*' -not -path './node_modules/*' -not -path './venv/*' | head -100 | sort) > "$temp_tree"
    fi

    # Update main tree file
    cp "$temp_tree" "$tree_file"
    rm -f "$temp_tree"

    log_workflow "✅ Repository structure updated: $tree_file"
}

# Analyze development progress and create summary
analyze_progress() {
    log_workflow "🔍 Analyzing development progress"

    # Count recent changes
    local files_changed=$(git diff --name-only HEAD~1 2>/dev/null | wc -l | tr -d ' ')
    local commits_today=$(git log --since="1 day ago" --oneline | wc -l | tr -d ' ')

    # Create progress summary
    cat > "$PROGRESS_FILE" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "session_date": "$(date +%Y-%m-%d)",
    "files_changed_last_commit": $files_changed,
    "commits_today": $commits_today,
    "development_phase": "active",
    "copilot_workflow_active": true,
    "last_tree_update": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "recent_focus": [
        "Variable system implementation",
        "Development workflow automation",
        "Command integration",
        "Documentation updates"
    ]
}
EOF

    log_workflow "📊 Progress analysis complete: $files_changed files changed, $commits_today commits today"
}

# Create intelligent commit message based on changes
create_commit_message() {
    local custom_message="${1:-}"

    if [[ -n "$custom_message" ]]; then
        echo "$custom_message"
        return
    fi

    # Analyze changes for intelligent commit message
    local changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
    local message_parts=()

    # Check for specific types of changes
    if echo "$changed_files" | grep -q "docs/"; then
        message_parts+=("📝 Documentation updates")
    fi

    if echo "$changed_files" | grep -q "uCORE/"; then
        message_parts+=("🔧 Core system enhancements")
    fi

    if echo "$changed_files" | grep -q "uSCRIPT/"; then
        message_parts+=("🐍 Script system improvements")
    fi

    if echo "$changed_files" | grep -q "dev/"; then
        message_parts+=("🚀 Development workflow updates")
    fi

    if echo "$changed_files" | grep -q "repo_structure.txt"; then
        message_parts+=("🌳 Repository structure update")
    fi

    # Create commit message
    if [[ ${#message_parts[@]} -gt 0 ]]; then
        local commit_msg="${message_parts[0]}"
        if [[ ${#message_parts[@]} -gt 1 ]]; then
            commit_msg+=" and ${message_parts[1]}"
        fi
        if [[ ${#message_parts[@]} -gt 2 ]]; then
            commit_msg+=" + $(( ${#message_parts[@]} - 2 )) more"
        fi
        echo "$commit_msg"
    else
        echo "🔄 Development progress update"
    fi
}

# Automated git commit with analysis
auto_commit() {
    local custom_message="${1:-}"

    log_workflow "📦 Starting automated commit process"

    # Update repository structure first
    update_repo_structure

    # Analyze progress
    analyze_progress

    # Stage all changes
    git add .

    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log_workflow "ℹ️  No changes to commit"
        return 0
    fi

    # Create intelligent commit message
    local commit_message
    commit_message=$(create_commit_message "$custom_message")

    # Create detailed commit message
    local detailed_message="$commit_message

Development Session: $(date '+%Y%m%d-%H%M%S')
Progress Checkpoint: $(date '+%Y-%m-%d %H:%M:%S')

Automated by uDOS Copilot Workflow
Repository structure updated via TREE DEV command

$(if [[ -f "$PROGRESS_FILE" ]]; then
    echo "Changes summary:"
    echo "- Files modified: $(jq -r '.files_changed_last_commit' "$PROGRESS_FILE" 2>/dev/null || echo "unknown")"
    echo "- Session focus: $(jq -r '.recent_focus[]' "$PROGRESS_FILE" 2>/dev/null | head -2 | sed 's/^/  • /' || echo "  • General development")"
fi)
"

    # Commit changes
    if git commit -m "$detailed_message"; then
        log_workflow "✅ Committed successfully: $commit_message"
        return 0
    else
        log_workflow "❌ Commit failed"
        return 1
    fi
}

# Push to remote repository
push_to_remote() {
    log_workflow "🚀 Pushing to remote repository"

    if git push origin main; then
        log_workflow "✅ Successfully pushed to remote"
        return 0
    else
        log_workflow "❌ Failed to push to remote"
        return 1
    fi
}

# Review and update copilot instructions
review_copilot_instructions() {
    local force_review="${1:-false}"
    local last_review_file="$COPILOT_DIR/.last-instruction-review"
    local review_interval=5 # Review every 5 development rounds

    # Check if review is needed
    local rounds_since_review=0
    if [[ -f "$last_review_file" ]]; then
        rounds_since_review=$(cat "$last_review_file" 2>/dev/null || echo "0")
    fi

    rounds_since_review=$((rounds_since_review + 1))
    echo "$rounds_since_review" > "$last_review_file"

    if [[ "$force_review" == "true" ]] || [[ $rounds_since_review -ge $review_interval ]]; then
        log_workflow "🧠 Reviewing copilot instructions (round $rounds_since_review)"

        # Create instruction review
        cat > "$COPILOT_DIR/instruction-review-$(date +%Y%m%d).md" << EOF
# Copilot Instruction Review - $(date)

## Development Progress Review
- **Rounds since last review**: $rounds_since_review
- **Current focus**: Variable system, dev workflow automation
- **Recent achievements**:
  - Implemented comprehensive variable system
  - Created STORY-based input collection
  - Automated development workflow with git integration

## Instruction Optimization Recommendations

### Keep Core (Established Patterns)
- uDOS v1.0.4.1 architecture principles
- 8-role system (Ghost → Wizard)
- Command syntax: [COMMAND|ACTION*PARAMETER]
- Variable syntax: \$VARIABLE format
- uCORE → uSCRIPT → uNETWORK compatibility

### Focus Areas for Efficiency
- **Lean Development**: Avoid over-engineering, maintain simplicity
- **Core Concepts**: Treat foundational uDOS patterns as 'given'
- **Documentation Reference**: Always use /docs for context
- **Automated Workflow**: Trust the git automation, focus on development

### Proposed Updates
1. **Streamline Responses**: Assume understanding of core uDOS concepts
2. **Focus on Implementation**: Less explanation, more targeted solutions
3. **Trust the System**: Leverage established patterns rather than recreating
4. **Progressive Development**: Build incrementally on solid foundations

## Next Development Cycle
- Continue variable system refinement
- Focus on user experience improvements
- Maintain lean, clean development approach
- Regular automated commits with descriptive messages

EOF

        # Reset counter
        echo "0" > "$last_review_file"
        log_workflow "📋 Instruction review completed - reset to round 0"
    else
        log_workflow "📝 Instruction review not due (round $rounds_since_review/$review_interval)"
    fi
}

# Complete development workflow
complete_workflow() {
    local commit_message="${1:-}"

    log_workflow "🔄 Starting complete copilot development workflow"

    # Review instructions periodically
    review_copilot_instructions

    # Automated commit and push
    if auto_commit "$commit_message"; then
        if push_to_remote; then
            log_workflow "✅ Complete workflow successful"
            return 0
        else
            log_workflow "⚠️  Committed locally but failed to push"
            return 1
        fi
    else
        log_workflow "❌ Workflow failed at commit stage"
        return 1
    fi
}

# Main command dispatcher
main() {
    mkdir -p "$DEV_ROOT/logs" "$COPILOT_DIR"/{instructions,context}

    case "${1:-workflow}" in
        "commit")
            auto_commit "${2:-}"
            ;;
        "push")
            push_to_remote
            ;;
        "tree")
            update_repo_structure
            ;;
        "analyze")
            analyze_progress
            ;;
        "review")
            review_copilot_instructions "true"
            ;;
        "workflow")
            complete_workflow "${2:-}"
            ;;
        *)
            echo "Copilot Workflow Commands:"
            echo "  commit [message]  - Auto-commit with intelligent message"
            echo "  push             - Push to remote repository"
            echo "  tree             - Update repository structure"
            echo "  analyze          - Analyze development progress"
            echo "  review           - Force review of copilot instructions"
            echo "  workflow [msg]   - Complete workflow (commit + push)"
            ;;
    esac
}

# Execute main with all arguments
main "$@"
