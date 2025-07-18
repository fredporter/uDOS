#!/bin/bash
# uDOS Beta v1.7.1
# 📘 log.sh — Centralized logging for moves, stats, and errors

# Config
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
SANDBOX="${UHOME}/sandbox"
TODAY="$(date +%Y-%m-%d)"
NOW="$(date +%H:%M:%S)"
LOGFILE="${UMEM}/moves/moves-${TODAY}.md"
STATSFILE="${UMEM}/state/stats.md"
ERRORFILE="${UMEM}/state/errors.log"

# Helpers
log_header() {
  echo "# 📘 Move Log — ${TODAY}" >> "$LOGFILE"
  echo "" >> "$LOGFILE"
}

write_line() {
  local line="$1"
  echo "- [$NOW] $line" >> "$LOGFILE"
}

log_error() {
  echo "[$TODAY $NOW] ❌ $1" >> "$ERRORFILE"
  echo "Logged error: $1"
}

log_stat() {
  local statname="$1"
  local increment="${2:-1}"
  if grep -q "^$statname:" "$STATSFILE"; then
    current=$(grep "^$statname:" "$STATSFILE" | awk -F ': ' '{print $2}')
    newval=$((current + increment))
    sed -i '' "s/^$statname:.*/$statname: $newval/" "$STATSFILE"
  else
    echo "$statname: $increment" >> "$STATSFILE"
  fi
  echo "Updated stat: $statname → +$increment"
}

# Commands
case "$1" in
  move)
    shift
    [[ ! -f "$LOGFILE" ]] && log_header
    write_line "$*"
    ;;
  error)
    shift
    log_error "$*"
    ;;
  stat)
    shift
    log_stat "$1" "${2:-1}"
    ;;
  *)
    echo "Usage:"
    echo "  ./log.sh move \"Your move summary here\""
    echo "  ./log.sh error \"Error message here\""
    echo "  ./log.sh stat statname [+N]"
    ;;
esac