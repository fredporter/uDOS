#!/bin/bash
# Dev Mode Integration for uDOS Command System
# Extends uCORE with development workflow commands

set -euo pipefail

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIZARD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UDOS_ROOT="$(cd "$WIZARD_ROOT/.." && pwd)"

# Load utilities
source "$SCRIPT_DIR/dev-mode-detection.sh"
source "$SCRIPT_DIR/uhex-generator.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🔍 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_dev() { echo -e "${PURPLE}🛠️  $1${NC}"; }

# Development log function
dev_log() {
    local message="$1"
    local session_id="${UDOS_DEV_SESSION:-}"
    
    if [[ -n "$session_id" && -f "$WIZARD_ROOT/.dev-session-$session_id" ]]; then
        source "$WIZARD_ROOT/.dev-session-$session_id"
        echo "### $(date +"%H:%M") - $message" >> "$SESSION_FILE"
        log_dev "Logged: $message"
    else
        log_warning "No active development session for logging"
    fi
}

# Create development task
create_dev_task() {
    local task_name="$1"
    local description="${2:-}"
    local uhex="$(generate_uhex)"
    local date_part="$(date +%Y%m%d)"
    local task_file="$WIZARD_ROOT/notes/uTASK-${uhex}-${date_part}-${task_name}.md"
    
    log_info "Creating development task: $task_name"
    
    cat > "$task_file" << EOF
# uTASK-${uhex}-${date_part}-${task_name}
**Created:** $(date +"%Y-%m-%d %H:%M")  
**Task ID:** ${uhex}  
**Type:** Development Task  
**Status:** Open  
**Location:** wizard/notes/

---

## 🎯 TASK OVERVIEW

### Task Name
${task_name}

### Description
${description:-Task description to be added}

### Priority
- [ ] High
- [ ] Medium  
- [ ] Low

### Status
- [x] Open
- [ ] In Progress
- [ ] Review
- [ ] Completed
- [ ] Closed

---

## 📋 TASK DETAILS

### Requirements
- [ ] 

### Acceptance Criteria
- [ ] 

### Dependencies
- [ ] 

---

## 📝 PROGRESS LOG

### $(date +"%H:%M") - Task Created
- Task initialized
- Requirements to be defined

### Progress Updates
<!-- Add progress updates here -->

---

## 🔧 IMPLEMENTATION NOTES

### Technical Approach
<!-- Document technical approach -->

### Code Changes
<!-- Record code changes -->

### Testing
<!-- Document testing approach -->

---

## 🔗 RELATED ITEMS

### Related Tasks
- [ ] 

### Related Sessions
- [ ] 

### Related Documentation
- [ ] 

---

*Task managed by uDOS Dev Mode Framework*
EOF
    
    log_success "Task created: $task_file"
    echo "$uhex"
}

# Create development roadmap
create_dev_roadmap() {
    local roadmap_name="$1"
    local period="${2:-Q4-2025}"
    local uhex="$(generate_uhex)"
    local date_part="$(date +%Y%m%d)"
    local roadmap_file="$WIZARD_ROOT/notes/uROAD-${uhex}-${date_part}-${roadmap_name}.md"
    
    log_info "Creating development roadmap: $roadmap_name"
    
    cat > "$roadmap_file" << EOF
# uROAD-${uhex}-${date_part}-${roadmap_name}
**Created:** $(date +"%Y-%m-%d %H:%M")  
**Roadmap ID:** ${uhex}  
**Type:** Development Roadmap  
**Period:** ${period}  
**Location:** wizard/notes/

---

## 🗺️ ROADMAP OVERVIEW

### Roadmap Name
${roadmap_name}

### Time Period
${period}

### Overall Objectives
- [ ] 

---

## 🎯 MILESTONES

### Phase 1: Foundation
**Target:** TBD  
**Status:** Planning

- [ ] Milestone 1
- [ ] Milestone 2
- [ ] Milestone 3

### Phase 2: Implementation  
**Target:** TBD  
**Status:** Planning

- [ ] Milestone 1
- [ ] Milestone 2
- [ ] Milestone 3

### Phase 3: Enhancement
**Target:** TBD  
**Status:** Planning

- [ ] Milestone 1
- [ ] Milestone 2
- [ ] Milestone 3

---

## 📊 PROGRESS TRACKING

### Completed
- [ ] 

### In Progress
- [ ] 

### Planned
- [ ] 

### Deferred
- [ ] 

---

## 🔄 UPDATES LOG

### $(date +"%H:%M") - Roadmap Created
- Roadmap initialized
- Milestones to be defined

### Progress Updates
<!-- Add progress updates here -->

---

*Roadmap managed by uDOS Dev Mode Framework*
EOF
    
    log_success "Roadmap created: $roadmap_file"
    echo "$uhex"
}

# Search development notes
search_dev_notes() {
    local query="$1"
    local note_type="${2:-all}"
    
    log_info "Searching development notes for: $query"
    
    local search_pattern="$WIZARD_ROOT/notes/"
    case "$note_type" in
        dev|session) search_pattern="${search_pattern}uDEV-*.md" ;;
        log) search_pattern="${search_pattern}uLOG-*.md" ;;
        doc) search_pattern="${search_pattern}uDOC-*.md" ;;
        task) search_pattern="${search_pattern}uTASK-*.md" ;;
        roadmap) search_pattern="${search_pattern}uROAD-*.md" ;;
        *) search_pattern="${search_pattern}*.md" ;;
    esac
    
    if command -v grep >/dev/null 2>&1; then
        grep -l "$query" $search_pattern 2>/dev/null | while read file; do
            local uhex="$(extract_uhex "$(basename "$file")" 2>/dev/null || echo "unknown")"
            echo "Found in: $(basename "$file") (ID: $uhex)"
            grep -n "$query" "$file" | head -3 | sed 's/^/  /'
            echo
        done
    else
        log_warning "grep not available for search"
    fi
}

# Organize development files
organize_dev_files() {
    log_info "Organizing development files..."
    
    local moved_count=0
    
    # Find files in wizard root that should be in notes/
    find "$WIZARD_ROOT" -maxdepth 1 -name "*.md" -not -name "README.md" | while read file; do
        local basename="$(basename "$file")"
        
        # Skip if already properly named with uHEX
        if [[ "$basename" =~ ^u[A-Z]+-[0-9a-f]{8}- ]]; then
            continue
        fi
        
        # Generate proper filename
        local filename_no_ext="${basename%.md}"
        local new_filename="$(generate_filename "uDEV" "$filename_no_ext" "md")"
        local new_path="$WIZARD_ROOT/notes/$new_filename"
        
        mv "$file" "$new_path"
        log_success "Organized: $basename -> $new_filename"
        ((moved_count++))
    done
    
    log_success "Organized $moved_count files"
}

# Show development summary
show_dev_summary() {
    log_info "Development Summary"
    
    echo
    echo "📊 Development Statistics:"
    
    # Count files by type
    local dev_count="$(ls "$WIZARD_ROOT"/notes/uDEV-*.md 2>/dev/null | wc -l | tr -d ' ')"
    local log_count="$(ls "$WIZARD_ROOT"/notes/uLOG-*.md 2>/dev/null | wc -l | tr -d ' ')"
    local doc_count="$(ls "$WIZARD_ROOT"/notes/uDOC-*.md 2>/dev/null | wc -l | tr -d ' ')"
    local task_count="$(ls "$WIZARD_ROOT"/notes/uTASK-*.md 2>/dev/null | wc -l | tr -d ' ')"
    local roadmap_count="$(ls "$WIZARD_ROOT"/notes/uROAD-*.md 2>/dev/null | wc -l | tr -d ' ')"
    
    echo "   Development Sessions: $dev_count"
    echo "   Implementation Logs: $log_count"
    echo "   Documentation: $doc_count"
    echo "   Tasks: $task_count"
    echo "   Roadmaps: $roadmap_count"
    
    # Show recent files
    echo
    echo "📝 Recent Development Files:"
    ls -t "$WIZARD_ROOT"/notes/*.md 2>/dev/null | head -5 | while read file; do
        local basename="$(basename "$file")"
        local uhex="$(extract_uhex "$basename" 2>/dev/null || echo "unknown")"
        echo "   $basename (ID: $uhex)"
    done
    
    # Show active sessions
    echo
    if ls "$WIZARD_ROOT"/.dev-session-* >/dev/null 2>&1; then
        echo "🔄 Active Sessions:"
        for session_file in "$WIZARD_ROOT"/.dev-session-*; do
            if [[ -f "$session_file" ]]; then
                source "$session_file"
                echo "   $SESSION_ID: $SESSION_NAME ($STATUS)"
            fi
        done
    fi
}

# Help function
show_help() {
    cat << 'EOF'
uDOS Development Mode Integration

Usage:
  dev-integration.sh status                    - Show development mode status
  dev-integration.sh init [session-name]      - Initialize development session
  dev-integration.sh close [session-id]       - Close development session
  dev-integration.sh log "message"            - Add message to development log
  dev-integration.sh task "name" ["desc"]     - Create development task
  dev-integration.sh roadmap "name" [period]  - Create development roadmap
  dev-integration.sh search "query" [type]    - Search development notes
  dev-integration.sh organize                 - Organize development files
  dev-integration.sh summary                  - Show development summary
  dev-integration.sh help                     - Show this help

Note Types for Search:
  dev, session  - Development session files
  log          - Implementation logs
  doc          - Documentation files
  task         - Task files
  roadmap      - Roadmap files
  all          - All files (default)

Examples:
  dev-integration.sh init "Architecture-Review"
  dev-integration.sh log "Implemented new command routing"
  dev-integration.sh task "Fix-Status-Command" "Update status paths"
  dev-integration.sh search "virtual environment" log
  dev-integration.sh roadmap "v1.4-Development" "Q1-2026"

This integrates with the uDOS command system for development workflows.
EOF
}

# Main command processing
main() {
    case "${1:-status}" in
        status)
            check_dev_status
            ;;
        init)
            init_dev_session "${2:-Development-Session}"
            ;;
        close)
            close_dev_session "${2:-}"
            ;;
        log)
            if [[ -z "${2:-}" ]]; then
                log_error "Log message required"
                exit 1
            fi
            dev_log "$2"
            ;;
        task)
            if [[ -z "${2:-}" ]]; then
                log_error "Task name required"
                exit 1
            fi
            create_dev_task "$2" "${3:-}"
            ;;
        roadmap)
            if [[ -z "${2:-}" ]]; then
                log_error "Roadmap name required"
                exit 1
            fi
            create_dev_roadmap "$2" "${3:-Q4-2025}"
            ;;
        search)
            if [[ -z "${2:-}" ]]; then
                log_error "Search query required"
                exit 1
            fi
            search_dev_notes "$2" "${3:-all}"
            ;;
        organize)
            organize_dev_files
            ;;
        summary)
            show_dev_summary
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use 'dev-integration.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
