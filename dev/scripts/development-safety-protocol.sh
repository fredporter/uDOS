#!/bin/bash

# Emergency Development Safety Protocol
# Implements auto-commit, backup, and safety checks for uDOS development

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Development safety configuration
DEV_BRANCH="dev-session-$(date +%Y%m%d)"
AUTO_COMMIT_INTERVAL=1800  # 30 minutes
BACKUP_INTERVAL=900        # 15 minutes
SAFETY_CHECK_INTERVAL=300  # 5 minutes

# Safety check function
perform_safety_check() {
    echo -e "${BLUE}🛡️  Performing development safety check...${NC}"
    
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
        
        # Auto-commit if changes are substantial
        local change_count=$(git diff --stat | wc -l)
        if [ "$change_count" -gt 10 ]; then
            echo -e "${GREEN}💾 Auto-committing substantial changes...${NC}"
            git add .
            git commit -m "🤖 Auto-commit: Development session $(date '+%Y-%m-%d %H:%M:%S')" || true
        fi
    fi
    
    # Create backup
    create_development_backup
    
    echo -e "${GREEN}✅ Safety check complete${NC}"
}

# Auto-commit function
auto_commit_changes() {
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo -e "${GREEN}🤖 Auto-commit triggered${NC}"
        git add .
        git commit -m "🤖 Auto-commit: $(date '+%Y-%m-%d %H:%M:%S') - Development session backup" || true
    fi
}

# Development backup function
create_development_backup() {
    local backup_dir="$UDOS_ROOT/dev/backups/auto"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="dev-backup-$timestamp.tar.gz"
    
    mkdir -p "$backup_dir"
    
    # Create comprehensive backup excluding .git and node_modules
    tar -czf "$backup_dir/$backup_file" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='*.log' \
        -C "$UDOS_ROOT" \
        uCORE uMEMORY uNETWORK uSCRIPT sandbox dev *.md *.sh *.json VERSION || true
    
    echo -e "${GREEN}📦 Development backup created: $backup_file${NC}"
    
    # Keep only last 10 backups
    cd "$backup_dir"
    ls -t dev-backup-*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
}

# Setup development branch
setup_dev_branch() {
    echo -e "${BLUE}🌿 Setting up development branch: $DEV_BRANCH${NC}"
    
    # Create and switch to development branch
    if ! git branch | grep -q "$DEV_BRANCH"; then
        git checkout -b "$DEV_BRANCH" || true
        echo -e "${GREEN}✅ Created development branch: $DEV_BRANCH${NC}"
    else
        git checkout "$DEV_BRANCH" || true
        echo -e "${GREEN}✅ Switched to development branch: $DEV_BRANCH${NC}"
    fi
}

# Install git hooks for safety
install_git_hooks() {
    local hooks_dir="$UDOS_ROOT/.git/hooks"
    
    # Pre-commit hook
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash
# uDOS Development Safety Pre-commit Hook

echo "🛡️  uDOS Development Safety Check..."

# Check for large uncommitted changes
change_count=$(git diff --cached --stat | wc -l)
if [ "$change_count" -gt 100 ]; then
    echo "⚠️  Large commit detected ($change_count files changed)"
    echo "Consider breaking this into smaller commits"
fi

# Auto-backup before commit
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="./dev/backups/pre-commit"
mkdir -p "$backup_dir"

tar -czf "$backup_dir/pre-commit-backup-$timestamp.tar.gz" \
    --exclude='.git' \
    --exclude='node_modules' \
    uCORE uMEMORY uNETWORK uSCRIPT sandbox 2>/dev/null || true

echo "✅ Pre-commit backup created"
EOF

    chmod +x "$hooks_dir/pre-commit"
    
    # Post-commit hook
    cat > "$hooks_dir/post-commit" << 'EOF'
#!/bin/bash
# uDOS Development Safety Post-commit Hook

echo "✅ Commit completed - triggering safety backup"

# Create post-commit backup
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="./dev/backups/post-commit" 
mkdir -p "$backup_dir"

tar -czf "$backup_dir/post-commit-backup-$timestamp.tar.gz" \
    --exclude='.git' \
    --exclude='node_modules' \
    uCORE uMEMORY uNETWORK uSCRIPT sandbox 2>/dev/null || true

# Keep only last 5 post-commit backups
cd "$backup_dir"
ls -t post-commit-backup-*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
EOF

    chmod +x "$hooks_dir/post-commit"
    
    echo -e "${GREEN}✅ Git safety hooks installed${NC}"
}

# Background safety monitor
start_safety_monitor() {
    local monitor_script="$UDOS_ROOT/dev/scripts/safety-monitor-daemon.sh"
    
    cat > "$monitor_script" << EOF
#!/bin/bash
# Background safety monitor for uDOS development

UDOS_ROOT="$UDOS_ROOT"
PID_FILE="\$UDOS_ROOT/dev/safety-monitor.pid"

# Check if already running
if [[ -f "\$PID_FILE" ]] && kill -0 "\$(cat "\$PID_FILE")" 2>/dev/null; then
    echo "Safety monitor already running (PID: \$(cat "\$PID_FILE"))"
    exit 0
fi

# Store PID
echo \$\$ > "\$PID_FILE"

echo "🛡️  Starting uDOS Development Safety Monitor (PID: \$\$)"

while true; do
    # Auto-commit check every 30 minutes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        change_count=\$(git diff --stat | wc -l)
        if [ "\$change_count" -gt 5 ]; then
            echo "\$(date): Auto-committing \$change_count changes"
            git add . 2>/dev/null || true
            git commit -m "🤖 Auto-commit: \$(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
        fi
    fi
    
    # Create backup every 15 minutes
    timestamp=\$(date +%Y%m%d_%H%M%S)
    backup_dir="\$UDOS_ROOT/dev/backups/auto"
    mkdir -p "\$backup_dir"
    
    tar -czf "\$backup_dir/safety-backup-\$timestamp.tar.gz" \\
        --exclude='.git' \\
        --exclude='node_modules' \\
        -C "\$UDOS_ROOT" \\
        uCORE uMEMORY uNETWORK uSCRIPT sandbox dev 2>/dev/null || true
    
    # Keep only last 20 auto-backups
    cd "\$backup_dir"
    ls -t safety-backup-*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null || true
    
    sleep $BACKUP_INTERVAL
done
EOF

    chmod +x "$monitor_script"
    
    # Start in background
    nohup "$monitor_script" > "$UDOS_ROOT/dev/safety-monitor.log" 2>&1 &
    
    echo -e "${GREEN}🛡️  Safety monitor started in background${NC}"
}

# Stop safety monitor
stop_safety_monitor() {
    local pid_file="$UDOS_ROOT/dev/safety-monitor.pid"
    
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$pid_file"
            echo -e "${GREEN}🛑 Safety monitor stopped${NC}"
        else
            rm -f "$pid_file"
            echo -e "${YELLOW}⚠️  Safety monitor was not running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Safety monitor PID file not found${NC}"
    fi
}

# Main safety protocol implementation
implement_safety_protocol() {
    echo "┌─────────────────────────────────────────┐"
    echo "│     🛡️  uDOS Development Safety Protocol │"
    echo "│              Emergency Fix               │"
    echo "└─────────────────────────────────────────┘"
    echo ""
    
    # Create backup directories
    mkdir -p "$UDOS_ROOT/dev/backups/auto"
    mkdir -p "$UDOS_ROOT/dev/backups/pre-commit"
    mkdir -p "$UDOS_ROOT/dev/backups/post-commit"
    mkdir -p "$UDOS_ROOT/dev/backups/manual"
    
    # Setup development branch
    setup_dev_branch
    
    # Create immediate backup of current state
    echo -e "${BLUE}📦 Creating emergency backup of current state...${NC}"
    create_development_backup
    
    # Install git hooks
    install_git_hooks
    
    # Start safety monitor
    start_safety_monitor
    
    # Initial safety check
    perform_safety_check
    
    echo ""
    echo -e "${GREEN}✅ Development Safety Protocol Active${NC}"
    echo ""
    echo "🛡️  Safety Features Enabled:"
    echo "  • Auto-commit every 30 minutes"
    echo "  • Auto-backup every 15 minutes"  
    echo "  • Pre/post-commit hooks"
    echo "  • Development branch isolation"
    echo "  • Background safety monitoring"
    echo ""
    echo "📁 Backup Locations:"
    echo "  • Auto backups: dev/backups/auto/"
    echo "  • Commit backups: dev/backups/pre-commit/ & post-commit/"
    echo "  • Manual backups: dev/backups/manual/"
    echo ""
}

# Show safety status
show_safety_status() {
    echo "🛡️  uDOS Development Safety Status"
    echo "─────────────────────────────────────"
    
    # Git status
    echo -n "Git Branch: "
    git branch --show-current 2>/dev/null || echo "Unknown"
    
    echo -n "Uncommitted Changes: "
    if git diff --quiet && git diff --cached --quiet; then
        echo -e "${GREEN}None${NC}"
    else
        local changes=$(git diff --stat | wc -l)
        echo -e "${YELLOW}$changes files${NC}"
    fi
    
    # Safety monitor status
    echo -n "Safety Monitor: "
    local pid_file="$UDOS_ROOT/dev/safety-monitor.pid"
    if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo -e "${GREEN}Running (PID: $(cat "$pid_file"))${NC}"
    else
        echo -e "${RED}Not Running${NC}"
    fi
    
    # Backup count
    local auto_backups=$(ls "$UDOS_ROOT/dev/backups/auto/"*.tar.gz 2>/dev/null | wc -l)
    echo "Auto Backups: $auto_backups"
    
    # Last backup
    local last_backup=$(ls -t "$UDOS_ROOT/dev/backups/auto/"*.tar.gz 2>/dev/null | head -1)
    if [[ -n "$last_backup" ]]; then
        echo "Last Backup: $(basename "$last_backup")"
    fi
}

# Manual backup function
create_manual_backup() {
    local name="${1:-manual}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$UDOS_ROOT/dev/backups/manual"
    local backup_file="$name-backup-$timestamp.tar.gz"
    
    mkdir -p "$backup_dir"
    
    tar -czf "$backup_dir/$backup_file" \
        --exclude='.git' \
        --exclude='node_modules' \
        -C "$UDOS_ROOT" \
        uCORE uMEMORY uNETWORK uSCRIPT sandbox dev *.md *.sh *.json VERSION || true
    
    echo -e "${GREEN}📦 Manual backup created: $backup_file${NC}"
}

# Help function
show_help() {
    echo "uDOS Development Safety Protocol v1.0"
    echo ""
    echo "Usage: $0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  implement    - Implement full safety protocol (emergency fix)"
    echo "  status       - Show current safety status"
    echo "  check        - Perform manual safety check"
    echo "  backup [name] - Create manual backup"
    echo "  start-monitor - Start background safety monitor"
    echo "  stop-monitor  - Stop background safety monitor"
    echo "  commit       - Manual commit with safety checks"
    echo "  help         - Show this help"
}

# Manual commit with safety
safe_commit() {
    local message="${1:-Manual commit: $(date '+%Y-%m-%d %H:%M:%S')}"
    
    echo -e "${BLUE}🛡️  Safe commit process...${NC}"
    
    # Create backup before commit
    create_manual_backup "pre-commit"
    
    # Add and commit
    git add .
    git commit -m "$message"
    
    echo -e "${GREEN}✅ Safe commit completed${NC}"
}

# Command handling
case "${1:-help}" in
    "implement")
        implement_safety_protocol
        ;;
    "status")
        show_safety_status
        ;;
    "check")
        perform_safety_check
        ;;
    "backup")
        create_manual_backup "${2:-manual}"
        ;;
    "start-monitor")
        start_safety_monitor
        ;;
    "stop-monitor")
        stop_safety_monitor
        ;;
    "commit")
        safe_commit "${2:-}"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
