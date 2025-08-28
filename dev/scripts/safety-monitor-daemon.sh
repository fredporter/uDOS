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
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="$UDOS_ROOT/dev/backups/auto"
    mkdir -p "$backup_dir"
    
    tar -czf "$backup_dir/safety-backup-$timestamp.tar.gz" \
        --exclude='.git' \
        --exclude='node_modules' \
        -C "$UDOS_ROOT" \
        uCORE uMEMORY uNETWORK uSCRIPT sandbox dev 2>/dev/null || true
    
    # Keep only last 20 auto-backups
    cd "$backup_dir"
    ls -t safety-backup-*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null || true
    
    sleep 900
done
