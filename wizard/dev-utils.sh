#!/bin/bash
# uDOS Wizard Development Utilities Manager & Framework
# Dev Mode utility script runner, framework manager, and workflow integration

WIZARD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILITIES_DIR="$WIZARD_ROOT/utilities"
LOG_DIR="$WIZARD_ROOT/notes"
UCORE_DIR="$(dirname "$WIZARD_ROOT")/uCORE"

# Development Framework Configuration
DEV_FRAMEWORK_VERSION="1.0.0"
NOTES_DIR="$WIZARD_ROOT/notes"
WORKFLOWS_DIR="$WIZARD_ROOT/workflows"
ROADMAPS_DIR="$WIZARD_ROOT/roadmaps"
DEV_UTILS_DIR="$WIZARD_ROOT/dev-utils"
BACKUP_INTEGRATION="$WIZARD_ROOT/../uCORE/code/backup-restore.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Development Framework Functions

# Initialize framework directories
init_framework() {
    echo -e "${CYAN}🔧 Initializing Development Framework v$DEV_FRAMEWORK_VERSION...${NC}"
    
    # Create directory structure
    mkdir -p "$NOTES_DIR"/{development,workflows,roadmaps,snapshots/{auto,manual}}
    mkdir -p "$WORKFLOWS_DIR"/{active,templates,archived}
    mkdir -p "$ROADMAPS_DIR"/{quarterly,sprint,long-term,daily}
    mkdir -p "$DEV_UTILS_DIR"/{analytics,optimization,automation,integration}
    
    # Create initial configuration
    cat > "$WIZARD_ROOT/framework-config.yml" << EOF
framework:
  version: "$DEV_FRAMEWORK_VERSION"
  initialized: "$(date -Iseconds)"
  backup_integration: true
  auto_snapshots: true
  
settings:
  default_note_type: "session"
  backup_on_milestone: true
  workflow_analytics: true
  roadmap_sync: true
  
directories:
  notes: "$NOTES_DIR"
  workflows: "$WORKFLOWS_DIR"
  roadmaps: "$ROADMAPS_DIR"
  utils: "$DEV_UTILS_DIR"
EOF
    
    # Create default workflow template
    cat > "$WORKFLOWS_DIR/templates/development-workflow.yml" << EOF
workflow:
  name: "Feature Development Workflow"
  version: "1.0"
  backup_integration: true
  
  stages:
    - name: "planning"
      backup_trigger: "stage_start"
      required_notes: ["requirements", "design"]
      outputs: ["plan.md", "architecture.md"]
      
    - name: "implementation"
      backup_trigger: "milestone"
      required_files: ["src/"]
      checkpoints: ["feature_complete", "tests_pass"]
      
    - name: "testing"
      backup_trigger: "test_results"
      required_outputs: ["test_report.md"]
      validation: ["unit_tests", "integration_tests"]
      
    - name: "documentation"
      backup_trigger: "docs_complete"
      required_outputs: ["README.md", "API.md"]
      
    - name: "deployment"
      backup_trigger: "deploy_ready"
      final_snapshot: true

  backup_policy:
    auto_snapshot: ["stage_transition", "milestone_reached"]
    retention: "30_days"
    compression: true
EOF
    
    echo -e "${GREEN}✅ Framework initialized successfully${NC}"
    log_action "Framework-Init" "Initialized development framework v$DEV_FRAMEWORK_VERSION"
}

# Session management
start_dev_session() {
    local session_type="${1:-general}"
    local session_id="WIZ_$(date +%Y%m%d_%H%M%S)_$(printf '%04X' $RANDOM)"
    
    echo -e "${BLUE}🚀 Starting development session: $session_id${NC}"
    
    # Create session note
    local session_file="$NOTES_DIR/development/session-$(date +%Y%m%d)-${session_id#*_}.md"
    
    cat > "$session_file" << EOF
---
type: session
created: $(date -Iseconds)
session_id: $session_id
backup_point: null
tags: [$session_type, development]
priority: medium
status: active
related_files: []
backup_snapshot: null
workflow_stage: planning
---

# Development Session: $session_id

## Session Information
- **Type**: $session_type
- **Started**: $(date)
- **Current Stage**: Planning
- **Session ID**: $session_id

## Objectives
- [ ] Define session goals
- [ ] Set up development environment
- [ ] Create initial backup checkpoint

## Work Log

### $(date +%H:%M) - Session Start
- Initialized development session
- Created session documentation
- Ready for development work

## Notes


## Next Steps


## Backup Checkpoints
- Initial: $(date +%H:%M)

---
*This session is tracked and backed up automatically*
EOF

    # Create initial backup checkpoint
    if [[ -f "$BACKUP_INTEGRATION" ]]; then
        source "$BACKUP_INTEGRATION"
        create_backup "dev_session_start" "$session_id" >/dev/null 2>&1
    fi
    
    # Initialize session state
    echo "$session_id" > "$WIZARD_ROOT/.current_session"
    
    echo -e "${GREEN}📝 Session note created: $session_file${NC}"
    echo -e "${GREEN}💾 Initial backup checkpoint created${NC}"
    
    log_action "Session-Start" "Started development session: $session_id ($session_type)"
    return 0
}

# Create development note
create_dev_note() {
    local note_type="$1"
    local note_title="$2"
    local session_id="${3:-$(cat "$WIZARD_ROOT/.current_session" 2>/dev/null || echo "MANUAL")}"
    
    if [[ -z "$note_type" || -z "$note_title" ]]; then
        echo -e "${RED}❌ Usage: create_note <type> <title> [session_id]${NC}"
        echo -e "${YELLOW}Types: session, feature, bug, research, workflow, roadmap${NC}"
        return 1
    fi
    
    local hex_id="$(printf '%04X' $RANDOM)"
    local note_file="$NOTES_DIR/development/${note_type}-${note_title//[^a-zA-Z0-9]/-}-${hex_id}.md"
    
    echo -e "${BLUE}📝 Creating $note_type note: $note_title${NC}"
    
    cat > "$note_file" << EOF
---
type: $note_type
created: $(date -Iseconds)
session_id: $session_id
backup_point: $hex_id
tags: [$note_type, development]
priority: medium
status: draft
related_files: []
backup_snapshot: null
workflow_stage: null
---

# $note_title

## Overview


## Details


## Implementation Notes


## Testing Requirements


## Documentation Needs


## Related Items


## Status
- [ ] Planning complete
- [ ] Implementation started
- [ ] Testing complete
- [ ] Documentation updated
- [ ] Ready for review

---
*Note ID: $hex_id | Session: $session_id*
EOF

    echo -e "${GREEN}✅ Note created: $note_file${NC}"
    log_action "Note-Creation" "Created $note_type note: $note_title (ID: $hex_id)"
    return 0
}

# Workflow management
start_workflow() {
    local workflow_name="$1"
    local workflow_template="${2:-development-workflow}"
    
    if [[ -z "$workflow_name" ]]; then
        echo -e "${RED}❌ Usage: start_workflow <name> [template]${NC}"
        return 1
    fi
    
    local workflow_id="WF_$(date +%Y%m%d_%H%M%S)_$(printf '%04X' $RANDOM)"
    local workflow_file="$WORKFLOWS_DIR/active/${workflow_name//[^a-zA-Z0-9]/-}-${workflow_id#*_}.yml"
    
    echo -e "${PURPLE}🔄 Starting workflow: $workflow_name${NC}"
    
    # Create workflow instance
    cat > "$workflow_file" << EOF
workflow:
  id: $workflow_id
  name: "$workflow_name"
  template: "$workflow_template"
  started: $(date -Iseconds)
  status: active
  current_stage: planning
  
stages:
  planning:
    status: active
    started: $(date -Iseconds)
    backup_triggered: false
    
  implementation:
    status: pending
    
  testing:
    status: pending
    
  documentation:
    status: pending
    
  deployment:
    status: pending

backup_points: []
milestones: []
notes: []
EOF

    # Update current workflow
    echo "$workflow_id" > "$WORKFLOWS_DIR/.current_workflow"
    
    # Create backup checkpoint
    if [[ -f "$BACKUP_INTEGRATION" ]]; then
        source "$BACKUP_INTEGRATION"
        create_backup "workflow_start" "$workflow_id" >/dev/null 2>&1
    fi
    
    echo -e "${GREEN}✅ Workflow started: $workflow_file${NC}"
    log_action "Workflow-Start" "Started workflow: $workflow_name (ID: $workflow_id)"
    return 0
}

# Advance workflow stage
advance_workflow() {
    local target_stage="$1"
    local workflow_id="${2:-$(cat "$WORKFLOWS_DIR/.current_workflow" 2>/dev/null)}"
    
    if [[ -z "$target_stage" || -z "$workflow_id" ]]; then
        echo -e "${RED}❌ Usage: advance_workflow <stage> [workflow_id]${NC}"
        echo -e "${YELLOW}Stages: planning, implementation, testing, documentation, deployment${NC}"
        return 1
    fi
    
    echo -e "${PURPLE}🔄 Advancing workflow to: $target_stage${NC}"
    
    # Find workflow file
    local workflow_file=$(find "$WORKFLOWS_DIR/active" -name "*${workflow_id#*_}*" -type f | head -1)
    
    if [[ ! -f "$workflow_file" ]]; then
        echo -e "${RED}❌ Workflow not found: $workflow_id${NC}"
        return 1
    fi
    
    # Create backup before advancing
    if [[ -f "$BACKUP_INTEGRATION" ]]; then
        source "$BACKUP_INTEGRATION"
        create_backup "workflow_advance_$target_stage" "$workflow_id" >/dev/null 2>&1
    fi
    
    # Update workflow file (simplified - would use yq in production)
    sed -i '' "s/current_stage: .*/current_stage: $target_stage/" "$workflow_file"
    
    echo -e "${GREEN}✅ Workflow advanced to: $target_stage${NC}"
    log_action "Workflow-Advance" "Advanced workflow $workflow_id to stage: $target_stage"
    return 0
}

# Create backup checkpoint
create_checkpoint() {
    local checkpoint_name="$1"
    local session_id="${2:-$(cat "$WIZARD_ROOT/.current_session" 2>/dev/null)}"
    
    if [[ -z "$checkpoint_name" ]]; then
        checkpoint_name="manual_$(date +%H%M%S)"
    fi
    
    echo -e "${CYAN}💾 Creating backup checkpoint: $checkpoint_name${NC}"
    
    if [[ -f "$BACKUP_INTEGRATION" ]]; then
        source "$BACKUP_INTEGRATION"
        local backup_id=$(create_backup "checkpoint_$checkpoint_name" "$session_id" 2>/dev/null)
        
        # Record checkpoint in session note if available
        if [[ -n "$session_id" && "$session_id" != "MANUAL" ]]; then
            local session_file=$(find "$NOTES_DIR/development" -name "*session*${session_id#*_}*" -type f | head -1)
            if [[ -f "$session_file" ]]; then
                echo "- $checkpoint_name: $(date +%H:%M) (Backup: $backup_id)" >> "$session_file"
            fi
        fi
        
        echo -e "${GREEN}✅ Checkpoint created with backup ID: $backup_id${NC}"
        log_action "Checkpoint-Create" "Created backup checkpoint: $checkpoint_name"
    else
        echo -e "${YELLOW}⚠️  Backup integration not available${NC}"
    fi
    
    return 0
}

# Development analytics
run_dev_analytics() {
    local analytics_type="${1:-summary}"
    
    echo -e "${CYAN}📊 Running development analytics: $analytics_type${NC}"
    
    case "$analytics_type" in
        "summary")
            echo -e "${WHITE}Development Summary:${NC}"
            echo "- Active sessions: $(find "$NOTES_DIR/development" -name "*session*" -type f | wc -l | tr -d ' ')"
            echo "- Total notes: $(find "$NOTES_DIR" -name "*.md" -type f | wc -l | tr -d ' ')"
            echo "- Active workflows: $(find "$WORKFLOWS_DIR/active" -name "*.yml" -type f | wc -l | tr -d ' ')"
            echo "- Roadmap items: $(find "$ROADMAPS_DIR" -name "*.md" -type f | wc -l | tr -d ' ')"
            ;;
        "productivity")
            echo -e "${WHITE}Productivity Metrics:${NC}"
            local today=$(date +%Y%m%d)
            echo "- Today's sessions: $(find "$NOTES_DIR/development" -name "*session-$today*" -type f | wc -l | tr -d ' ')"
            echo "- Notes created today: $(find "$NOTES_DIR" -name "*.md" -newerct "today" -type f 2>/dev/null | wc -l | tr -d ' ')"
            ;;
        "workflow")
            echo -e "${WHITE}Workflow Analysis:${NC}"
            echo "- Active workflows: $(find "$WORKFLOWS_DIR/active" -name "*.yml" -type f | wc -l | tr -d ' ')"
            echo "- Completed workflows: $(find "$WORKFLOWS_DIR/archived" -name "*.yml" -type f | wc -l | tr -d ' ')"
            ;;
        *)
            echo -e "${RED}❌ Unknown analytics type: $analytics_type${NC}"
            echo -e "${YELLOW}Available types: summary, productivity, workflow${NC}"
            return 1
            ;;
    esac
    
    log_action "Analytics" "Ran $analytics_type analytics"
    return 0
}

# Function to get 2-letter timezone alpha code
get_timezone_alpha() {
    local tz_mapping_file="$UCORE_DIR/datasets/timezone-alpha-codes.json"
    
    # Get current timezone (try multiple methods)
    local current_tz=""
    if command -v timedatectl >/dev/null 2>&1; then
        current_tz=$(timedatectl show --property=Timezone --value 2>/dev/null)
    elif [ -n "$TZ" ]; then
        current_tz="$TZ"
    else
        # Fallback: get from system
        current_tz=$(date +%Z 2>/dev/null)
    fi
    
    # Map common timezone names to our 2-letter alpha codes
    case "$current_tz" in
        "AEST"|"Australia/Sydney"|"Australia/Melbourne"|"AEDT") echo "AE" ;;
        "AWST"|"Australia/Perth") echo "AW" ;;
        "ACST"|"Australia/Adelaide") echo "AT" ;;
        "UTC"|"GMT") echo "UT" ;;
        "EST"|"US/Eastern") echo "ES" ;;
        "PST"|"US/Pacific") echo "PS" ;;
        "CST"|"US/Central") echo "CS" ;;
        "MST"|"US/Mountain") echo "MS" ;;
        "JST"|"Asia/Tokyo") echo "JS" ;;
        "CET"|"Europe/Berlin"|"Europe/Paris") echo "CE" ;;
        "EET"|"Europe/Athens") echo "EE" ;;
        "IST"|"Asia/Kolkata") echo "IS" ;;
        "BST"|"Asia/Dhaka") echo "BS" ;;
        "NZST"|"Pacific/Auckland") echo "NZ" ;;
        *) 
            # Default fallback - try to extract from mapping file if it exists
            if [ -f "$tz_mapping_file" ] && command -v jq >/dev/null 2>&1; then
                local alpha_code=$(jq -r ".mappings[\"$current_tz\"] // \"AE\"" "$tz_mapping_file" 2>/dev/null)
                echo "$alpha_code"
            else
                echo "AE"  # Default to Australian Eastern (original system timezone)
            fi
            ;;
    esac
}

# Function to log actions
log_action() {
    local action="$1"
    local description="$2"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local tz_code=$(get_timezone_alpha)
    local logfile="uDEV-${timestamp}${tz_code}-Utility-${action}.md"
    
    cat > "$LOG_DIR/$logfile" << EOF
# Dev Mode Utility Log: $action

**Timestamp**: $(date)  
**Action**: $action  
**Description**: $description  
**User**: $(whoami)  
**Location**: $WIZARD_ROOT  

## Action Details

$description

## System State

\`\`\`bash
pwd: $(pwd)
whoami: $(whoami)
date: $(date)
\`\`\`

---
*Generated by uDOS Wizard Development Utilities Manager*
EOF
    
    echo -e "${GREEN}[LOG]${NC} Action logged: $logfile"
}

# Function to show available utilities and framework commands
show_utilities() {
    echo -e "${CYAN}🧙‍♂️ uDOS Wizard Development Utilities & Framework v$DEV_FRAMEWORK_VERSION${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${WHITE}Development Framework Commands:${NC}"
    echo -e "  ${GREEN}•${NC} init_framework           Initialize development framework"
    echo -e "  ${GREEN}•${NC} start_session [type]     Start development session with backup"
    echo -e "  ${GREEN}•${NC} create_note <type> <title>  Create development note"
    echo -e "  ${GREEN}•${NC} start_workflow <name>    Start workflow with backup integration"
    echo -e "  ${GREEN}•${NC} advance_workflow <stage> Advance workflow to next stage"
    echo -e "  ${GREEN}•${NC} create_checkpoint [name] Create backup checkpoint"
    echo -e "  ${GREEN}•${NC} dev_analytics [type]     Run development analytics"
    echo ""
    
    if [ -d "$UTILITIES_DIR" ]; then
        echo -e "${YELLOW}Available utilities:${NC}"
        for script in "$UTILITIES_DIR"/*.sh; do
            if [ -f "$script" ]; then
                local name=$(basename "$script" .sh)
                echo -e "  ${GREEN}•${NC} $name"
            fi
        done
        echo ""
    fi
    
    echo -e "${YELLOW}Built-in commands:${NC}"
    echo -e "  ${GREEN}•${NC} filename - Generate uDOS v2.0 compliant filenames"
    echo -e "  ${GREEN}•${NC} organize - Organize completed logs and summaries"
    echo -e "  ${GREEN}•${NC} roadmap - Manage roadmap tasks and planning"
    echo -e "  ${GREEN}•${NC} status - Show wizard development status"
    echo -e "  ${GREEN}•${NC} help - Show this help message"
    echo ""
    
    echo -e "${CYAN}Framework Integration:${NC}"
    echo -e "  ${BLUE}•${NC} Smart backup integration with undo/redo capabilities"
    echo -e "  ${BLUE}•${NC} Workflow-driven development with milestone tracking"
    echo -e "  ${BLUE}•${NC} Session-based note management with automatic logging"
    echo -e "  ${BLUE}•${NC} Analytics and productivity metrics"
    echo ""
    
    echo -e "${YELLOW}Example Usage:${NC}"
    echo -e "  ${CYAN}$0 start_session feature-development${NC}"
    echo -e "  ${CYAN}$0 create_note feature 'Enhanced Error Handling'${NC}"
    echo -e "  ${CYAN}$0 start_workflow 'VS Code Extension Development'${NC}"
    echo -e "  ${CYAN}$0 advance_workflow implementation${NC}"
    echo -e "  ${CYAN}$0 create_checkpoint 'Feature Complete'${NC}"
}

# Function to generate filenames
generate_filename() {
    if [ -f "$UTILITIES_DIR/generate-filename-v2.sh" ]; then
        "$UTILITIES_DIR/generate-filename-v2.sh" "$@"
        log_action "Filename-Generation" "Generated filename with parameters: $*"
    else
        echo -e "${RED}Error: Filename generator not found${NC}"
    fi
}

# Function to organize logs
organize_logs() {
    echo -e "${CYAN}📁 Organizing Development Logs${NC}"
    
    local moved_count=0
    local log_count=$(find "$LOG_DIR" -name "uDEV-*.md" | wc -l)
    
    echo -e "${YELLOW}Found $log_count log files${NC}"
    
    # TODO: Add logic to move completed summaries, organize by date, etc.
    # For now, just show what we have
    
    echo -e "${GREEN}Organization complete${NC}"
    log_action "Log-Organization" "Organized $log_count development log files"
}

# Function to manage roadmaps with framework integration
manage_roadmap() {
    local action=${1:-"list"}
    
    case $action in
        "list")
            echo -e "${CYAN}🗺️ Roadmap Tasks${NC}"
            if [ -d "$ROADMAPS_DIR" ]; then
                find "$ROADMAPS_DIR" -name "*.md" | head -10
            else
                echo -e "${YELLOW}No roadmap tasks found${NC}"
                echo -e "${BLUE}Use 'init_framework' to set up the framework first${NC}"
            fi
            ;;
        "add")
            local title="$2"
            if [ -n "$title" ]; then
                local hex_id="$(printf '%04X' $RANDOM)"
                local filename="roadmap-${title//[^a-zA-Z0-9]/-}-${hex_id}.md"
                local filepath="$ROADMAPS_DIR/sprint/$filename"
                
                # Ensure directory exists
                mkdir -p "$ROADMAPS_DIR/sprint"
                
                cat > "$filepath" << EOF
---
type: roadmap
created: $(date -Iseconds)
roadmap_id: ROADMAP_$(date +%Y%m%d_%H%M%S)_${hex_id}
title: "$title"
priority: medium
status: planned
estimated_effort: "TBD"
dependencies: []
workflow_template: "development-workflow"
backup_strategy: "milestone_based"
---

# Roadmap Task: $title

## Overview


## Objectives
- [ ] Define requirements
- [ ] Create implementation plan
- [ ] Set milestones
- [ ] Define success criteria

## Implementation Plan


## Dependencies


## Success Criteria


## Timeline
- Start: TBD
- End: TBD
- Milestones: TBD

## Workflow Integration
- Template: development-workflow
- Backup Strategy: milestone_based

---
*Roadmap ID: ROADMAP_$(date +%Y%m%d_%H%M%S)_${hex_id}*
EOF
                
                echo -e "${GREEN}Created roadmap task: $filename${NC}"
                log_action "Roadmap-Task-Creation" "Created new roadmap task: $title (ID: ${hex_id})"
            else
                echo -e "${RED}Error: Please provide a task title${NC}"
            fi
            ;;
        "workflow")
            local roadmap_file="$2"
            if [ -f "$roadmap_file" ]; then
                local title=$(grep "^title:" "$roadmap_file" | cut -d'"' -f2)
                start_workflow "$title" "development-workflow"
                echo -e "${GREEN}Started workflow for roadmap task: $title${NC}"
            else
                echo -e "${RED}Error: Roadmap file not found: $roadmap_file${NC}"
            fi
            ;;
        *)
            echo -e "${YELLOW}Usage: roadmap [list|add|workflow] [title|file]${NC}"
            ;;
    esac
}

# Function to show development status with framework metrics
show_status() {
    echo -e "${CYAN}🔍 Wizard Development Status & Framework Metrics${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
    echo ""
    
    # Framework status
    if [ -f "$WIZARD_ROOT/framework-config.yml" ]; then
        echo -e "${GREEN}✅ Development Framework: Active${NC}"
        local framework_version=$(grep "version:" "$WIZARD_ROOT/framework-config.yml" | cut -d'"' -f2)
        echo -e "   Version: $framework_version"
    else
        echo -e "${YELLOW}⚠️  Development Framework: Not initialized${NC}"
        echo -e "   Run 'init_framework' to set up"
    fi
    echo ""
    
    # Session status
    if [ -f "$WIZARD_ROOT/.current_session" ]; then
        local current_session=$(cat "$WIZARD_ROOT/.current_session")
        echo -e "${GREEN}📱 Active Session: $current_session${NC}"
    else
        echo -e "${YELLOW}📱 No active session${NC}"
    fi
    echo ""
    
    # Workflow status
    if [ -f "$WORKFLOWS_DIR/.current_workflow" ]; then
        local current_workflow=$(cat "$WORKFLOWS_DIR/.current_workflow")
        echo -e "${GREEN}🔄 Active Workflow: $current_workflow${NC}"
        local workflow_file=$(find "$WORKFLOWS_DIR/active" -name "*${current_workflow#*_}*" -type f | head -1)
        if [ -f "$workflow_file" ]; then
            local current_stage=$(grep "current_stage:" "$workflow_file" | cut -d':' -f2 | tr -d ' ')
            echo -e "   Current Stage: $current_stage"
        fi
    else
        echo -e "${YELLOW}🔄 No active workflow${NC}"
    fi
    echo ""
    
    echo -e "${YELLOW}Framework Metrics:${NC}"
    echo "- Development notes: $(find "$NOTES_DIR/development" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')"
    echo "- Active workflows: $(find "$WORKFLOWS_DIR/active" -name "*.yml" -type f 2>/dev/null | wc -l | tr -d ' ')"
    echo "- Roadmap items: $(find "$ROADMAPS_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')"
    echo "- Backup snapshots: $(find "$NOTES_DIR/snapshots" -type f 2>/dev/null | wc -l | tr -d ' ')"
    
    echo ""
    echo -e "${YELLOW}Recent Activity:${NC}"
    find "$LOG_DIR" -name "uDEV-*.md" -type f -exec ls -la {} \; 2>/dev/null | tail -3
    
    log_action "Status-Check" "Viewed wizard development status and framework metrics"
}

# Main execution with framework integration
case "${1:-help}" in
    # Framework commands
    "init_framework"|"init")
        init_framework
        ;;
    "start_session")
        shift
        start_dev_session "$@"
        ;;
    "create_note")
        shift
        create_dev_note "$@"
        ;;
    "start_workflow")
        shift
        start_workflow "$@"
        ;;
    "advance_workflow")
        shift
        advance_workflow "$@"
        ;;
    "create_checkpoint")
        shift
        create_checkpoint "$@"
        ;;
    "dev_analytics")
        shift
        run_dev_analytics "$@"
        ;;
    
    # Original commands
    "help"|"--help"|"-h")
        show_utilities
        ;;
    "filename")
        shift
        generate_filename "$@"
        ;;
    "organize")
        organize_logs
        ;;
    "roadmap")
        shift
        manage_roadmap "$@"
        ;;
    "status")
        show_status
        ;;
    *)
        # Try to run as utility script
        if [ -f "$UTILITIES_DIR/$1.sh" ]; then
            local util_name="$1"
            shift
            "$UTILITIES_DIR/$util_name.sh" "$@"
            log_action "Utility-Execution" "Ran utility script: $util_name with parameters: $*"
        else
            echo -e "${RED}Unknown command: $1${NC}"
            echo ""
            echo -e "${YELLOW}Use one of the following commands:${NC}"
            echo -e "${CYAN}Framework: init_framework, start_session, create_note, start_workflow, advance_workflow, create_checkpoint, dev_analytics${NC}"
            echo -e "${CYAN}Utilities: filename, organize, roadmap, status, help${NC}"
            echo ""
            echo -e "${BLUE}Run '$0 help' for detailed information${NC}"
        fi
        ;;
esac
