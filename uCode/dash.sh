#!/bin/bash
# uDOS Beta v1.7.1
# 📊 dash.sh — Dashboard creator, refresher and viewer

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
DASHBOARD="${UMEM}/state/dashboard.md"
STATS="${UMEM}/state/stats.md"
TODAY="$(date +%Y-%m-%d)"
MOVESFILE="${UMEM}/moves/moves-${TODAY}.md"

# Helpers
log() { echo "[dash] $1"; }

header() {
  echo "# 📊 uDOS Dashboard" > "$DASHBOARD"
  echo "_Last updated: $(date '+%Y-%m-%d %H:%M:%S')_" >> "$DASHBOARD"
  echo "" >> "$DASHBOARD"
}

section() {
  echo "## $1" >> "$DASHBOARD"
  echo "" >> "$DASHBOARD"
}

render_stats() {
  section "Stats"
  if [[ -f "$STATS" ]]; then
    cat "$STATS" >> "$DASHBOARD"
  else
    echo "_No stats available yet._" >> "$DASHBOARD"
  fi
  echo "" >> "$DASHBOARD"
}

render_moves() {
  section "Today's Moves"
  if [[ -f "$MOVESFILE" ]]; then
    grep "^-" "$MOVESFILE" >> "$DASHBOARD"
  else
    echo "_No moves logged today._" >> "$DASHBOARD"
  fi
  echo "" >> "$DASHBOARD"
}

open_dashboard() {
  if command -v bat &> /dev/null; then
    bat "$DASHBOARD"
  elif command -v less &> /dev/null; then
    less "$DASHBOARD"
  else
    cat "$DASHBOARD"
  fi
}

# Command parser
case "$1" in
  new|build)
    log "Building dashboard..."
    header
    render_stats
    render_moves
    log "Dashboard updated → $DASHBOARD"
    ;;
  show|view)
    log "Opening dashboard..."
    open_dashboard
    ;;
  sync)
    log "Refreshing dashboard (sync mode)..."
    "$0" build
    ;;
  *)
    echo "Usage:"
    echo "  ./dash.sh build        # Generate new dashboard markdown"
    echo "  ./dash.sh sync         # Same as build (used by cron/tools)"
    echo "  ./dash.sh show         # View dashboard in terminal"
    ;;
esac