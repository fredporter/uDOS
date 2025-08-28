#!/bin/bash
# uDOS Development Mode Startup Script
# Creates fresh development environment with git integration and copilot workflow optimization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEV_ROOT="$UDOS_ROOT/dev"
DEV_REPO_DIR="$DEV_ROOT/fresh-repo"
DEV_ARCHIVE_DIR="$DEV_ROOT/archive"
REPO_URL="https://github.com/fredporter/uDOS.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Dev mode banner
show_dev_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "██████╗ ███████╗██╗   ██╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗"
    echo "██╔══██╗██╔════╝██║   ██║    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝"
    echo "██║  ██║█████╗  ██║   ██║    ██╔████╔██║██║   ██║██║  ██║█████╗  "
    echo "██║  ██║██╔══╝  ╚██╗ ██╔╝    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  "
    echo "██████╔╝███████╗ ╚████╔╝     ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗"
    echo "╚═════╝ ╚══════╝  ╚═══╝      ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${YELLOW}uDOS Development Environment Initialization${NC}"
    echo -e "${BLUE}Universal Device Operating System - Dev Mode v1.0.4.1${NC}"
    echo ""
}

# Logging function
log_dev() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$DEV_ROOT/logs/dev-session-$(date '+%Y%m%d').log"

    mkdir -p "$(dirname "$log_file")"

    case "$level" in
        "INFO")  echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "DEV") echo -e "${MAGENTA}🧠 $message${NC}" ;;
    esac

    echo "[$timestamp] [$level] $message" >> "$log_file"
}

# Check if we're in wizard role with dev access
check_dev_permissions() {
    local current_role_file="$UDOS_ROOT/sandbox/current-role.conf"
    local current_role="GUEST"

    if [[ -f "$current_role_file" ]]; then
        current_role=$(grep "CURRENT_ROLE=" "$current_role_file" | cut -d'"' -f2 2>/dev/null || echo "GUEST")
    fi

    if [[ "$current_role" != "WIZARD" ]]; then
        log_dev "ERROR" "Development mode requires WIZARD role. Current role: $current_role"
        echo ""
        echo -e "${YELLOW}To access development mode:${NC}"
        echo "1. Switch to WIZARD role: [ROLE|ACTIVATE*WIZARD]"
        echo "2. Enable dev mode: [ROLE|DEV-MODE*ENABLE]"
        echo "3. Restart development environment"
        exit 1
    fi

    log_dev "SUCCESS" "WIZARD role confirmed - Development access granted"
}

# Create development directory structure
setup_dev_structure() {
    log_dev "INFO" "Setting up development directory structure..."

    mkdir -p "$DEV_ROOT"/{fresh-repo,archive,logs,workspace,migration}
    mkdir -p "$DEV_ROOT/workspace"/{active,staging,testing}

    # Create dev session info
    cat > "$DEV_ROOT/session-info.json" << EOF
{
    "session_id": "DEV-$(date +%Y%m%d-%H%M%S)",
    "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "role": "WIZARD",
    "repo_url": "$REPO_URL",
    "dev_mode": true,
    "workspace": "$DEV_ROOT"
}
EOF

    log_dev "SUCCESS" "Development structure created"
}

# Pull fresh repository copy
pull_fresh_repo() {
    log_dev "INFO" "Pulling fresh repository copy..."

    # Clean existing fresh repo if it exists
    if [[ -d "$DEV_REPO_DIR" ]]; then
        log_dev "WARNING" "Removing existing fresh repo copy"
        rm -rf "$DEV_REPO_DIR"
    fi

    # Clone fresh copy
    log_dev "INFO" "Cloning repository: $REPO_URL"
    if git clone "$REPO_URL" "$DEV_REPO_DIR" 2>/dev/null; then
        log_dev "SUCCESS" "Fresh repository copy available at: $DEV_REPO_DIR"
    else
        log_dev "WARNING" "Git clone failed - creating local copy instead"

        # Create local copy excluding dev directory to avoid recursion
        cp -r "$UDOS_ROOT" "$DEV_REPO_DIR"
        rm -rf "$DEV_REPO_DIR/dev"
        mkdir -p "$DEV_REPO_DIR/dev"

        log_dev "SUCCESS" "Local repository copy created"
    fi
}

# Update repository structure documentation
update_repo_structure() {
    log_dev "INFO" "Updating repository structure with TREE DEV command..."

    # Generate tree structure from fresh repo
    local tree_output="$DEV_ROOT/workspace/repo-structure-new.txt"

    if command -v tree >/dev/null 2>&1; then
        # Use tree command if available
        tree -a -I '.git|node_modules|__pycache__|*.pyc|.DS_Store' "$DEV_REPO_DIR" > "$tree_output"
    else
        # Fallback to find command
        (cd "$DEV_REPO_DIR" && find . -type f -not -path './.git/*' -not -path './node_modules/*' -not -name '*.pyc' -not -name '.DS_Store' | sort) > "$tree_output"
    fi

    # Update main repo structure file
    if [[ -f "$tree_output" ]]; then
        cp "$tree_output" "$UDOS_ROOT/repo_structure.txt"
        log_dev "SUCCESS" "Repository structure updated"
    else
        log_dev "WARNING" "Could not generate repository structure"
    fi
}

# Initialize copilot development context
setup_copilot_context() {
    log_dev "INFO" "Setting up copilot development context..."

    # Create copilot session file
    cat > "$DEV_ROOT/copilot/dev-session-context.md" << EOF
# uDOS Development Session Context

## Session Information
- **Session ID**: $(cat "$DEV_ROOT/session-info.json" | grep session_id | cut -d'"' -f4)
- **Started**: $(date)
- **Mode**: Development (WIZARD + DEV)
- **Fresh Repo**: $DEV_REPO_DIR
- **Workspace**: $DEV_ROOT/workspace

## Development Workflow
1. **Fresh Base**: Clean repository copy in /dev/fresh-repo
2. **Active Development**: Work in /dev/workspace/active
3. **Testing**: Use /dev/workspace/testing for validation
4. **Staging**: Prepare changes in /dev/workspace/staging
5. **Migration**: Approved changes moved to root system
6. **Git Integration**: Automated commits with summary notes

## Copilot Instructions
- Update repo_structure.txt using TREE DEV after changes
- Commit with descriptive messages based on development progress
- Review copilot instructions every few development rounds
- Focus on core uDOS concepts, avoid bloating
- Use /docs for development reference and context

## Reference Documentation
- /docs/USER-CODE-MANUAL.md - Complete command reference
- /docs/VARIABLE-SYSTEM.md - Variable management system
- /docs/ARCHITECTURE.md - System architecture
- /dev/docs/ - Development-specific documentation

## Current Development Focus
- Variable system implementation
- STORY-based input collection
- uSCRIPT integration enhancements
- Command syntax standardization

## Development Session Log
Session started: $(date)

EOF

    # Update copilot instructions with development context
    cat >> "$DEV_ROOT/copilot/dev-session-context.md" << EOF
## Active Development Guidelines

### Git Workflow
1. Work in /dev/workspace/active for current development
2. Test changes in /dev/workspace/testing
3. Stage approved changes in /dev/workspace/staging
4. Migrate to root system when validated
5. Auto-commit with descriptive messages
6. Update repo_structure.txt after significant changes

### Documentation References
- Always reference /docs for system understanding
- Update documentation as part of development process
- Maintain consistency with established patterns
- Keep copilot instructions current and focused

### Development Principles
- Lean, clean, orderly implementation
- Consistent with uDOS architectural patterns
- Future-expandable design
- Clear separation of concerns
- Role-based access control awareness

EOF

    log_dev "SUCCESS" "Copilot development context initialized"
}

# Create development workspace
create_dev_workspace() {
    log_dev "INFO" "Creating development workspace..."

    # Copy key components to workspace for active development
    mkdir -p "$DEV_ROOT/workspace/active"/{uCORE,uSCRIPT,docs,sandbox}

    # Copy current state to workspace
    if [[ -d "$UDOS_ROOT/uCORE" ]]; then
        cp -r "$UDOS_ROOT/uCORE"/* "$DEV_ROOT/workspace/active/uCORE/" 2>/dev/null || true
    fi

    if [[ -d "$UDOS_ROOT/uSCRIPT" ]]; then
        cp -r "$UDOS_ROOT/uSCRIPT"/* "$DEV_ROOT/workspace/active/uSCRIPT/" 2>/dev/null || true
    fi

    if [[ -d "$UDOS_ROOT/docs" ]]; then
        cp -r "$UDOS_ROOT/docs"/* "$DEV_ROOT/workspace/active/docs/" 2>/dev/null || true
    fi

    # Create workspace configuration
    cat > "$DEV_ROOT/workspace/workspace-config.json" << EOF
{
    "workspace_id": "DEV-WORKSPACE-$(date +%Y%m%d-%H%M%S)",
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "base_repo": "$DEV_REPO_DIR",
    "active_workspace": "$DEV_ROOT/workspace/active",
    "testing_workspace": "$DEV_ROOT/workspace/testing",
    "staging_workspace": "$DEV_ROOT/workspace/staging",
    "migration_ready": false,
    "git_integration": true
}
EOF

    log_dev "SUCCESS" "Development workspace created"
}

# Create migration script
create_migration_script() {
    log_dev "INFO" "Creating migration script..."

    cat > "$DEV_ROOT/migration/migrate-to-root.sh" << 'EOF'
#!/bin/bash
# Migrate approved development changes to root system

set -euo pipefail

DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UDOS_ROOT="$(cd "$DEV_ROOT/.." && pwd)"
STAGING_DIR="$DEV_ROOT/workspace/staging"
BACKUP_DIR="$DEV_ROOT/archive/pre-migration-$(date +%Y%m%d-%H%M%S)"

echo "🔄 Starting migration of approved changes..."

# Create backup of current state
mkdir -p "$BACKUP_DIR"
cp -r "$UDOS_ROOT"/{uCORE,uSCRIPT,docs} "$BACKUP_DIR/" 2>/dev/null || true

# Migrate staged changes
if [[ -d "$STAGING_DIR" ]]; then
    echo "📦 Migrating staged changes to root system..."

    # Migrate core components
    if [[ -d "$STAGING_DIR/uCORE" ]]; then
        cp -r "$STAGING_DIR/uCORE"/* "$UDOS_ROOT/uCORE/" 2>/dev/null || true
    fi

    if [[ -d "$STAGING_DIR/uSCRIPT" ]]; then
        cp -r "$STAGING_DIR/uSCRIPT"/* "$UDOS_ROOT/uSCRIPT/" 2>/dev/null || true
    fi

    if [[ -d "$STAGING_DIR/docs" ]]; then
        cp -r "$STAGING_DIR/docs"/* "$UDOS_ROOT/docs/" 2>/dev/null || true
    fi

    echo "✅ Migration completed"
    echo "📋 Backup available at: $BACKUP_DIR"
else
    echo "⚠️  No staged changes found for migration"
fi
EOF

    chmod +x "$DEV_ROOT/migration/migrate-to-root.sh"

    log_dev "SUCCESS" "Migration script created"
}

# Create git automation script
create_git_automation() {
    log_dev "INFO" "Creating git automation script..."

    cat > "$DEV_ROOT/scripts/auto-git.sh" << 'EOF'
#!/bin/bash
# Automated git operations for development workflow

set -euo pipefail

DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UDOS_ROOT="$(cd "$DEV_ROOT/.." && pwd)"

commit_with_summary() {
    local summary_message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cd "$UDOS_ROOT"

    # Update repo structure
    "$DEV_ROOT/scripts/update-tree.sh"

    # Add all changes
    git add .

    # Create commit with summary
    git commit -m "🔧 Dev Update: $summary_message

Development session: $(date '+%Y%m%d-%H%M%S')
Timestamp: $timestamp

Changes include:
- Updated repository structure
- Development progress checkpoint
- Automated commit from dev workflow

Generated by uDOS Development Mode
"

    echo "✅ Committed with message: $summary_message"
}

push_to_git() {
    cd "$UDOS_ROOT"

    if git push origin main; then
        echo "✅ Successfully pushed to remote repository"
    else
        echo "⚠️  Failed to push to remote repository"
        return 1
    fi
}

# Main execution
case "${1:-}" in
    "commit")
        commit_with_summary "${2:-Development progress update}"
        ;;
    "push")
        push_to_git
        ;;
    "commit-push")
        commit_with_summary "${2:-Development progress update}"
        push_to_git
        ;;
    *)
        echo "Usage: auto-git.sh {commit|push|commit-push} [message]"
        ;;
esac
EOF

    chmod +x "$DEV_ROOT/scripts/auto-git.sh"

    # Create tree update script
    mkdir -p "$DEV_ROOT/scripts"
    cat > "$DEV_ROOT/scripts/update-tree.sh" << 'EOF'
#!/bin/bash
# Update repository structure using TREE DEV command

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TREE_FILE="$UDOS_ROOT/repo_structure.txt"

echo "🌳 Updating repository structure..."

if command -v tree >/dev/null 2>&1; then
    tree -a -I '.git|node_modules|__pycache__|*.pyc|.DS_Store|venv' "$UDOS_ROOT" > "$TREE_FILE"
else
    (cd "$UDOS_ROOT" && find . -type f -not -path './.git/*' -not -path './node_modules/*' -not -path './venv/*' -not -name '*.pyc' -not -name '.DS_Store' | sort) > "$TREE_FILE"
fi

echo "✅ Repository structure updated: $TREE_FILE"
EOF

    chmod +x "$DEV_ROOT/scripts/update-tree.sh"

    log_dev "SUCCESS" "Git automation scripts created"
}

# Create development commands integration
create_dev_commands() {
    log_dev "INFO" "Creating development command integration..."

    cat > "$DEV_ROOT/scripts/dev-commands.sh" << 'EOF'
#!/bin/bash
# Development mode command integration

set -euo pipefail

DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

dev_status() {
    echo "🧠 uDOS Development Mode Status"
    echo "════════════════════════════════"
    echo "Session: $(cat "$DEV_ROOT/session-info.json" | grep session_id | cut -d'"' -f4)"
    echo "Started: $(cat "$DEV_ROOT/session-info.json" | grep started | cut -d'"' -f4)"
    echo "Fresh Repo: $DEV_ROOT/fresh-repo"
    echo "Workspace: $DEV_ROOT/workspace"
    echo ""

    if [[ -d "$DEV_ROOT/workspace/staging" ]] && [[ -n "$(ls -A "$DEV_ROOT/workspace/staging" 2>/dev/null)" ]]; then
        echo "📦 Staged changes ready for migration"
    else
        echo "📝 No staged changes"
    fi
}

dev_commit() {
    local message="${1:-Development checkpoint}"
    "$DEV_ROOT/scripts/auto-git.sh" commit-push "$message"
}

dev_migrate() {
    "$DEV_ROOT/migration/migrate-to-root.sh"
}

dev_tree() {
    "$DEV_ROOT/scripts/update-tree.sh"
}

# Command dispatcher
case "${1:-status}" in
    "status") dev_status ;;
    "commit") dev_commit "${2:-}" ;;
    "migrate") dev_migrate ;;
    "tree") dev_tree ;;
    *)
        echo "Dev commands: status, commit [message], migrate, tree"
        ;;
esac
EOF

    chmod +x "$DEV_ROOT/scripts/dev-commands.sh"

    log_dev "SUCCESS" "Development commands created"
}

# Main execution
main() {
    show_dev_banner

    log_dev "INFO" "Starting uDOS Development Mode initialization..."

    # Check permissions
    check_dev_permissions

    # Setup development environment
    setup_dev_structure
    pull_fresh_repo
    update_repo_structure
    setup_copilot_context
    create_dev_workspace
    create_migration_script
    create_git_automation
    create_dev_commands

    echo ""
    log_dev "SUCCESS" "Development Mode initialized successfully!"
    echo ""
    echo -e "${BOLD}${GREEN}🚀 Development Environment Ready${NC}"
    echo ""
    echo -e "${CYAN}Available Commands:${NC}"
    echo "  $DEV_ROOT/scripts/dev-commands.sh status    - Show dev status"
    echo "  $DEV_ROOT/scripts/dev-commands.sh commit    - Commit and push changes"
    echo "  $DEV_ROOT/scripts/dev-commands.sh migrate   - Migrate staged changes"
    echo "  $DEV_ROOT/scripts/dev-commands.sh tree      - Update repo structure"
    echo ""
    echo -e "${CYAN}Development Workflow:${NC}"
    echo "  1. Work in: $DEV_ROOT/workspace/active"
    echo "  2. Test in: $DEV_ROOT/workspace/testing"
    echo "  3. Stage in: $DEV_ROOT/workspace/staging"
    echo "  4. Migrate approved changes to root"
    echo "  5. Auto-commit with descriptive messages"
    echo ""
    echo -e "${YELLOW}Fresh Repository Copy:${NC} $DEV_REPO_DIR"
    echo -e "${YELLOW}Development Logs:${NC} $DEV_ROOT/logs/"
    echo ""

    # Create initial commit for dev mode startup
    "$DEV_ROOT/scripts/auto-git.sh" commit "🚀 Development Mode initialized - Fresh dev environment ready"
}

# Execute main function
main "$@"
