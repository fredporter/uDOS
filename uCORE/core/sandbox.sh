#!/bin/bash
# sandbox.sh - Unified sandbox development environment
# Central command for all sandbox operations: dev, testing, experiments, session management

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source core functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration
SANDBOX_DIR="$UDOS_ROOT/sandbox"
SESSION_MANAGER="$SCRIPT_DIR/session-manager.sh"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-restore.sh"
WORKFLOW_MANAGER="$SCRIPT_DIR/workflow-manager.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# SANDBOX COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════

# Handle DEV commands
handle_dev_command() {
    local action="${1:-list}"
    shift || true

    case "$action" in
        CREATE)
            local filename="$1"
            local template="${2:-script}"
            if [ -z "$filename" ]; then
                log_error "Filename required for DEV CREATE"
                exit 1
            fi
            "$SESSION_MANAGER" create "$filename" "$template"
            ;;
        LIST)
            echo -e "${BLUE}📁 Development Files:${NC}"
            if [ -d "$SANDBOX_DIR/dev" ]; then
                find "$SANDBOX_DIR/dev" -type f -exec basename {} \; | sort
            else
                echo "No development files found"
            fi
            ;;
        EDIT)
            local filename="$1"
            if [ -z "$filename" ]; then
                log_error "Filename required for DEV EDIT"
                exit 1
            fi
            local filepath="$SANDBOX_DIR/dev/$filename"
            if [ -f "$filepath" ]; then
                ${EDITOR:-nano} "$filepath"
            else
                log_error "File not found: $filepath"
            fi
            ;;
        RUN)
            local filename="$1"
            if [ -z "$filename" ]; then
                log_error "Filename required for DEV RUN"
                exit 1
            fi
            local filepath="$SANDBOX_DIR/dev/$filename"
            if [ -f "$filepath" ]; then
                log_info "Running development file: $filename"
                bash "$filepath"
            else
                log_error "File not found: $filepath"
            fi
            ;;
        CLEAN)
            echo -e "${BLUE}🧹 Cleaning development files...${NC}"
            read -p "Remove all files in /sandbox/dev? (y/N): " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                rm -rf "$SANDBOX_DIR/dev"/*
                log_success "Development files cleaned"
            fi
            ;;
        *)
            show_dev_help
            ;;
    esac
}

# Handle TEST commands
handle_test_command() {
    local action="${1:-list}"
    shift || true

    case "$action" in
        CREATE)
            local testname="$1"
            if [ -z "$testname" ]; then
                log_error "Test name required for TEST CREATE"
                exit 1
            fi
            "$SESSION_MANAGER" create "test-$testname.sh" "test"
            ;;
        RUN)
            local testname="$1"
            if [ -z "$testname" ]; then
                echo -e "${BLUE}🧪 Running all tests...${NC}"
                for test_file in "$SANDBOX_DIR/dev"/test-*.sh; do
                    if [ -f "$test_file" ]; then
                        echo -e "${CYAN}Running: $(basename "$test_file")${NC}"
                        bash "$test_file"
                    fi
                done
            else
                local test_file="$SANDBOX_DIR/dev/test-$testname.sh"
                if [ -f "$test_file" ]; then
                    log_info "Running test: $testname"
                    bash "$test_file"
                else
                    log_error "Test not found: $test_file"
                fi
            fi
            ;;
        LIST)
            echo -e "${BLUE}🧪 Test Files:${NC}"
            find "$SANDBOX_DIR/dev" -name "test-*.sh" -type f -exec basename {} \; 2>/dev/null | sort || echo "No test files found"
            ;;
        *)
            show_test_help
            ;;
    esac
}

# Handle EXPERIMENT commands
handle_experiment_command() {
    local action="${1:-list}"
    shift || true

    case "$action" in
        CREATE)
            local expname="$1"
            if [ -z "$expname" ]; then
                log_error "Experiment name required for EXPERIMENT CREATE"
                exit 1
            fi
            "$SESSION_MANAGER" create "exp-$expname.sh" "experiment"
            ;;
        RUN)
            local expname="$1"
            if [ -z "$expname" ]; then
                log_error "Experiment name required for EXPERIMENT RUN"
                exit 1
            fi
            local exp_file="$SANDBOX_DIR/dev/exp-$expname.sh"
            if [ -f "$exp_file" ]; then
                log_info "Running experiment: $expname"
                bash "$exp_file"
            else
                log_error "Experiment not found: $exp_file"
            fi
            ;;
        LIST)
            echo -e "${BLUE}🔬 Experiment Files:${NC}"
            find "$SANDBOX_DIR/dev" -name "exp-*.sh" -type f -exec basename {} \; 2>/dev/null | sort || echo "No experiment files found"
            ;;
        *)
            show_experiment_help
            ;;
    esac
}

# Handle SESSION commands
handle_session_command() {
    local action="${1:-status}"
    shift || true

    case "$action" in
        START)
            "$SESSION_MANAGER" start
            ;;
        END)
            "$SESSION_MANAGER" end
            ;;
        STATUS)
            "$SESSION_MANAGER" status
            ;;
        SAVE)
            log_info "Creating session save point..."
            "$BACKUP_SCRIPT" backup session "Session save point via sandbox"
            ;;
        UNDO)
            "$BACKUP_SCRIPT" undo
            ;;
        REDO)
            "$BACKUP_SCRIPT" redo
            ;;
        HISTORY)
            "$SESSION_MANAGER" status
            echo ""
            "$BACKUP_SCRIPT" history
            ;;
        *)
            show_session_help
            ;;
    esac
}

# Handle WORKFLOW commands (move→milestone→mission→legacy)
handle_workflow_command() {
    local action="${1:-status}"
    shift || true

    case "$action" in
        MOVE)
            local move_type="$1"
            local description="$2"
            if [ -z "$move_type" ] || [ -z "$description" ]; then
                log_error "Move type and description required for WORKFLOW MOVE"
                exit 1
            fi
            "$WORKFLOW_MANAGER" move "$move_type" "$description"
            ;;
        GOAL)
            local sub_action="$1"
            shift || true
            case "$sub_action" in
                CREATE)
                    local title="$1"
                    local description="$2"
                    local goal_type="${3:-exploration}"
                    if [ -z "$title" ] || [ -z "$description" ]; then
                        log_error "Goal title and description required"
                        exit 1
                    fi
                    "$WORKFLOW_MANAGER" goal create "$title" "$description" "$goal_type"
                    ;;
                UPDATE)
                    local goal_id="$1"
                    local field="$2"
                    local value="$3"
                    if [ -z "$goal_id" ] || [ -z "$field" ] || [ -z "$value" ]; then
                        log_error "Goal ID, field, and value required"
                        exit 1
                    fi
                    "$WORKFLOW_MANAGER" goal update "$goal_id" "$field" "$value"
                    ;;
                CONVERT)
                    local goal_id="$1"
                    local milestone_title="$2"
                    if [ -z "$goal_id" ] || [ -z "$milestone_title" ]; then
                        log_error "Goal ID and milestone title required"
                        exit 1
                    fi
                    "$WORKFLOW_MANAGER" goal convert "$goal_id" "$milestone_title"
                    ;;
                LIST)
                    "$WORKFLOW_MANAGER" goal list
                    ;;
                *)
                    echo -e "${BLUE}🎯 GOAL Command Help${NC}"
                    echo "  GOAL CREATE <title> <description> [type] - Create new goal"
                    echo "  GOAL UPDATE <id> <field> <value>         - Update goal"
                    echo "  GOAL CONVERT <id> <milestone_title>      - Convert to milestone"
                    echo "  GOAL LIST                                - List active goals"
                    ;;
            esac
            ;;
        MILESTONE)
            local title="$1"
            local description="$2"
            if [ -z "$title" ] || [ -z "$description" ]; then
                log_error "Milestone title and description required for WORKFLOW MILESTONE"
                exit 1
            fi
            "$WORKFLOW_MANAGER" milestone "$title" "$description"
            ;;
        MISSION)
            local sub_action="$1"
            shift || true
            case "$sub_action" in
                CREATE)
                    local title="$1"
                    local description="$2"
                    if [ -z "$title" ] || [ -z "$description" ]; then
                        log_error "Mission title and description required"
                        exit 1
                    fi
                    "$WORKFLOW_MANAGER" mission create "$title" "$description"
                    ;;
                COMPLETE)
                    local mission_id="$1"
                    local notes="${2:-Mission completed via sandbox}"
                    if [ -z "$mission_id" ]; then
                        log_error "Mission ID required"
                        exit 1
                    fi
                    "$WORKFLOW_MANAGER" mission complete "$mission_id" "$notes"
                    ;;
                LIST)
                    echo -e "${BLUE}🎯 Active Missions:${NC}"
                    find "$SANDBOX_DIR/workflow/missions" -name "*.json" -exec jq -r 'select(.status=="active") | .title + " (ID: " + .mission_id + ")"' {} \; 2>/dev/null | sort
                    ;;
                *)
                    echo -e "${BLUE}🎯 MISSION Command Help${NC}"
                    echo "Actions:"
                    echo "  CREATE <title> <description>  - Create new mission"
                    echo "  COMPLETE <id> [notes]         - Complete mission"
                    echo "  LIST                          - List active missions"
                    ;;
            esac
            ;;
        LEGACY)
            echo -e "${BLUE}🏆 Legacy Achievements:${NC}"
            "$WORKFLOW_MANAGER" legacy list
            ;;
        ASSIST)
            local sub_action="${1:-status}"
            shift || true
            case "$sub_action" in
                ENTER)
                    local focus="${1:-general}"
                    "$WORKFLOW_MANAGER" assist enter "$focus"
                    ;;
                EXIT)
                    "$WORKFLOW_MANAGER" assist exit
                    ;;
                STATUS)
                    "$WORKFLOW_MANAGER" assist status
                    ;;
                *)
                    echo -e "${BLUE}🤖 ASSIST Command Help${NC}"
                    echo "Actions:"
                    echo "  ENTER [focus]                 - Enter assist mode"
                    echo "  EXIT                          - Exit assist mode"
                    echo "  STATUS                        - Show assist status"
                    ;;
            esac
            ;;
        STATUS)
            "$WORKFLOW_MANAGER" status
            ;;
        INIT)
            "$WORKFLOW_MANAGER" init
            ;;
        *)
            show_workflow_help
            ;;
    esac
}

# Handle SANDBOX commands (meta-commands)
handle_sandbox_command() {
    local action="${1:-status}"
    shift || true

    case "$action" in
        STATUS)
            show_sandbox_status
            ;;
        INIT)
            init_sandbox_environment
            ;;
        CLEAN)
            clean_sandbox_environment
            ;;
        ARCHIVE)
            "$SESSION_MANAGER" archive
            ;;
        BACKUP)
            "$BACKUP_SCRIPT" backup manual "Sandbox backup"
            ;;
        *)
            show_sandbox_help
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Show overall sandbox status
show_sandbox_status() {
    echo -e "${BOLD}${CYAN}═══ SANDBOX STATUS ═══${NC}"

    # Session status
    "$SESSION_MANAGER" status 2>/dev/null || echo -e "${YELLOW}No active session${NC}"
    echo ""

    # Workflow status
    if [ -f "$WORKFLOW_MANAGER" ]; then
        "$WORKFLOW_MANAGER" status 2>/dev/null || true
        echo ""
    fi

    # File counts
    local dev_count=$(find "$SANDBOX_DIR/dev" -type f 2>/dev/null | wc -l | xargs)
    local test_count=$(find "$SANDBOX_DIR/dev" -name "test-*.sh" -type f 2>/dev/null | wc -l | xargs)
    local exp_count=$(find "$SANDBOX_DIR/dev" -name "exp-*.sh" -type f 2>/dev/null | wc -l | xargs)
    local temp_count=$(find "$SANDBOX_DIR/temp" -type f 2>/dev/null | wc -l | xargs)

    echo -e "${BLUE}📊 File Counts:${NC}"
    echo -e "  Development files: $dev_count"
    echo -e "  Test files: $test_count"
    echo -e "  Experiment files: $exp_count"
    echo -e "  Temp files: $temp_count"
    echo ""

    # Recent activity
    if [ -f "$SANDBOX_DIR/session/logs/session-$(date +%Y%m%d_)*.log" ]; then
        echo -e "${BLUE}📝 Recent Activity:${NC}"
        find "$SANDBOX_DIR/session/logs" -name "session-$(date +%Y%m%d)_*.log" -type f -exec tail -3 {} \; 2>/dev/null | head -10
    fi
}# Initialize sandbox environment
init_sandbox_environment() {
    log_info "Initializing sandbox environment..."

    # Create directory structure
    mkdir -p "$SANDBOX_DIR/dev"
    mkdir -p "$SANDBOX_DIR/temp"
    mkdir -p "$SANDBOX_DIR/session/logs"
    mkdir -p "$SANDBOX_DIR/session/moves"
    mkdir -p "$SANDBOX_DIR/session/undo-stack"
    mkdir -p "$SANDBOX_DIR/session/archive"
    mkdir -p "$SANDBOX_DIR/experiments"
    mkdir -p "$SANDBOX_DIR/tests"
    mkdir -p "$SANDBOX_DIR/scripts"

    # Create README
    cat > "$SANDBOX_DIR/README.md" << 'EOF'
# uDOS Sandbox Environment

This is your development workspace for uDOS. All development, testing, and experimentation should happen here.

## Structure

- `dev/` - Development files, scripts being worked on
- `temp/` - Temporary files (auto-cleaned)
- `session/` - Session management and logging
- `experiments/` - Experimental features and tests
- `tests/` - Test scripts and validation
- `scripts/` - User scripts and utilities

## Session Management

The sandbox uses session-based development:
- Session data tracked in real-time
- Undo/redo based on session moves
- Daily summaries compiled at session end
- Final summaries archived to uMEMORY

## Commands

Use the sandbox command for all operations:
- `sandbox DEV CREATE <file>` - Create development file
- `sandbox TEST CREATE <name>` - Create test
- `sandbox EXPERIMENT CREATE <name>` - Create experiment
- `sandbox SESSION START/END` - Manage sessions
- `sandbox STATUS` - Show current status

All work is logged and can be undone/redone within the current session.
EOF

    log_success "Sandbox environment initialized"
}

# Clean sandbox environment
clean_sandbox_environment() {
    echo -e "${YELLOW}⚠️  This will clean up the sandbox environment${NC}"
    echo "The following will be cleaned:"
    echo "  • Temp files"
    echo "  • Old session logs (>3 days)"
    echo "  • Completed experiments"
    echo ""
    read -p "Continue? (y/N): " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        # Clean temp files
        rm -rf "$SANDBOX_DIR/temp"/*

        # Clean old session files
        find "$SANDBOX_DIR/session/logs" -name "session-*.log" -mtime +3 -delete 2>/dev/null || true
        find "$SANDBOX_DIR/session/archive" -name "*" -mtime +7 -delete 2>/dev/null || true

        # Clean completed experiments (ask for each)
        for exp_file in "$SANDBOX_DIR/dev"/exp-*.sh; do
            if [ -f "$exp_file" ]; then
                echo -n "Remove experiment $(basename "$exp_file")? (y/N): "
                read exp_confirm
                if [ "$exp_confirm" = "y" ] || [ "$exp_confirm" = "Y" ]; then
                    rm "$exp_file"
                fi
            fi
        done

        log_success "Sandbox cleaned"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# HELP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

show_main_help() {
    echo -e "${BOLD}${CYAN}🏖️  uDOS Sandbox Environment${NC}"
    echo "Session-based development workspace with workflow management"
    echo ""
    echo "Commands:"
    echo "  DEV <action>               - Development file management"
    echo "  TEST <action>              - Test creation and execution"
    echo "  EXPERIMENT <action>        - Experimental feature development"
    echo "  SESSION <action>           - Session management and undo/redo"
    echo "  WORKFLOW <action>          - User journey workflow (move→milestone→mission→legacy)"
    echo "  SANDBOX <action>           - Sandbox environment control"
    echo ""
    echo "Quick Actions:"
    echo "  sandbox STATUS             - Show overall status"
    echo "  sandbox DEV CREATE <file>  - Create development file"
    echo "  sandbox TEST RUN          - Run all tests"
    echo "  sandbox SESSION START     - Start development session"
    echo "  sandbox WORKFLOW STATUS    - Show workflow progress"
    echo "  sandbox WORKFLOW ASSIST ENTER - Enter assist mode"
    echo ""
    echo "Type 'sandbox <command> help' for specific command help"
}

show_dev_help() {
    echo -e "${BLUE}🛠️  DEV Command Help${NC}"
    echo "Actions:"
    echo "  CREATE <file> [template]   - Create development file (script/experiment/test)"
    echo "  LIST                       - List development files"
    echo "  EDIT <file>                - Edit development file"
    echo "  RUN <file>                 - Run development file"
    echo "  CLEAN                      - Clean all development files"
}

show_test_help() {
    echo -e "${BLUE}🧪 TEST Command Help${NC}"
    echo "Actions:"
    echo "  CREATE <name>              - Create test file"
    echo "  RUN [name]                 - Run test (or all tests if no name)"
    echo "  LIST                       - List test files"
}

show_experiment_help() {
    echo -e "${BLUE}🔬 EXPERIMENT Command Help${NC}"
    echo "Actions:"
    echo "  CREATE <name>              - Create experiment file"
    echo "  RUN <name>                 - Run experiment"
    echo "  LIST                       - List experiment files"
}

show_session_help() {
    echo -e "${BLUE}🎯 SESSION Command Help${NC}"
    echo "Actions:"
    echo "  START                      - Start new development session"
    echo "  END                        - End current session"
    echo "  STATUS                     - Show session status"
    echo "  SAVE                       - Create session save point"
    echo "  UNDO                       - Undo last operation"
    echo "  REDO                       - Redo operation"
    echo "  HISTORY                    - Show session history"
}

show_workflow_help() {
    echo -e "${BLUE}🗺️  WORKFLOW Command Help${NC}"
    echo "User journey management: move→goal→milestone→mission→legacy"
    echo ""
    echo "Actions:"
    echo "  MOVE <type> <description>          - Log current activity"
    echo "  GOAL CREATE <title> <description>  - Create aspirational goal"
    echo "  GOAL UPDATE <id> <field> <value>   - Update goal progress"
    echo "  GOAL CONVERT <id> <milestone>      - Convert goal to milestone"
    echo "  GOAL LIST                          - List active goals"
    echo "  MILESTONE <title> <description>    - Create achievement milestone"
    echo "  MISSION CREATE <title> <desc>      - Create new mission"
    echo "  MISSION COMPLETE <id> [notes]      - Complete mission"
    echo "  MISSION LIST                       - List active missions"
    echo "  LEGACY                             - Show legacy achievements"
    echo "  ASSIST ENTER [focus]               - Enter assist mode"
    echo "  ASSIST EXIT                        - Exit assist mode"
    echo "  STATUS                             - Show workflow status"
    echo "  INIT                               - Initialize workflow system"
    echo ""
    echo "Examples:"
    echo "  sandbox WORKFLOW MOVE development 'Created user login system'"
    echo "  sandbox WORKFLOW GOAL CREATE 'Learn Python' 'Master automation scripting'"
    echo "  sandbox WORKFLOW MILESTONE 'First App' 'Completed first application'"
    echo "  sandbox WORKFLOW MISSION CREATE 'Learn Python' 'Master Python basics'"
    echo "  sandbox WORKFLOW ASSIST ENTER productivity"
}

show_sandbox_help() {
    echo -e "${BLUE}🏖️  SANDBOX Command Help${NC}"
    echo "Actions:"
    echo "  STATUS                     - Show sandbox overview"
    echo "  INIT                       - Initialize sandbox environment"
    echo "  CLEAN                      - Clean sandbox environment"
    echo "  ARCHIVE                    - Archive daily summaries"
    echo "  BACKUP                     - Create sandbox backup"
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        DEV)
            handle_dev_command "$@"
            ;;
        TEST)
            handle_test_command "$@"
            ;;
        EXPERIMENT)
            handle_experiment_command "$@"
            ;;
        SESSION)
            handle_session_command "$@"
            ;;
        WORKFLOW)
            handle_workflow_command "$@"
            ;;
        SANDBOX)
            handle_sandbox_command "$@"
            ;;
        STATUS)
            show_sandbox_status
            ;;
        help|--help|-h)
            show_main_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_main_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
