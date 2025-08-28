#!/bin/bash
# Background safety monitor for uDOS development

UDOS_ROOT="/Users/fredbook/uDOS"
PID_FILE="$UDOS_ROOT/dev/safety-monitor.pid"

# Check if already running
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Safety monitor already running (PID: $(cat "$PID_FILE"))"
    exit 0
fi

# Store PID
echo $$ > "$PID_FILE"

echo "🛡️  Starting uDOS Development Safety Monitor (PID: $$)"

while true; do
    # Auto-commit check every 30 minutes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        change_count=$(git diff --stat | wc -l)
        if [ "$change_count" -gt 5 ]; then
            echo "$(date): Auto-committing $change_count changes"
            git add . 2>/dev/null || true
            git commit -m "🤖 Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
        fi
    fi
    
    # Create backup every 15 minutes
    # Use session-based backup for safety monitoring
    if [ -f "$UDOS_ROOT/dev/scripts/session-backup-system.sh" ]; then
        "$UDOS_ROOT/dev/scripts/session-backup-system.sh" snapshot "auto-$(date +%H%M%S)"
    fi
    
    sleep 900
done
