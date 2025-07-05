#!/bin/bash
# dashboard-sync.sh — Generate and display uDOS status dashboard (improved)

trap 'echo "🛑 Dashboard sync interrupted."; exit 143' SIGTERM

UHOME="${HOME}/uDOS"
UROOT="$UHOME"
bash "$UROOT/scripts/check-setup.sh" >/dev/null
MEMORY_DIR="${UOS_MEMORY_DIR:-$UHOME/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UHOME/uKnowledge}"

STATE_DIR="$MEMORY_DIR/state"
MOVE_DIR="$MEMORY_DIR/logs/moves"
MOVE_LOG="$MEMORY_DIR/logs/move-log-$(date +%Y-%m-%d).md"
NOW="$(date '+%Y-%m-%d %H:%M:%S')"

# Ensure sandbox directory and dash-log file exist
mkdir -p "$UHOME/sandbox"
touch "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

# Log execution to session dash-log
echo "[$(date +%H:%M:%S)] → dashboard-sync" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

# Initialize user variables with safe defaults
USER_NAME="Unknown"
PASSWORD="N/A"
CREATED="N/A"
LOCATION="Unknown"
ACTIVE_MISSION="none"
LEGACY="none"
LIFESPAN="n/a"
SHARING="n/a"
UDOS_VERSION="uDOS Beta v1.6.1"

#
# Read Username and Password from sandbox user.md
SANDBOX_USER_FILE="$UHOME/sandbox/user.md"
if [[ -f "$SANDBOX_USER_FILE" ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ ^([A-Za-z ]+):[[:space:]]*(.+)$ ]]; then
      key="${BASH_REMATCH[1]// /}"
      value="${BASH_REMATCH[2]}"
      case "$key" in
        Username) USER_NAME="$value" ;;
        Password) PASSWORD="$value" ;;
      esac
    fi
  done < "$SANDBOX_USER_FILE"
fi

# Read other fields from instance.md
INSTANCE_FILE="$STATE_DIR/instance.md"
if [[ -f "$INSTANCE_FILE" ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ ^([A-Za-z ]+):[[:space:]]*(.+)$ ]]; then
      key="${BASH_REMATCH[1]// /}"
      value="${BASH_REMATCH[2]}"
      case "$key" in
        Created) CREATED="$value" ;;
        Location) LOCATION="$value" ;;
        Mission) ACTIVE_MISSION="$value" ;;
        Legacy) LEGACY="$value" ;;
        Lifespan) LIFESPAN="$value" ;;
        Sharing) SHARING="$value" ;;
        uDOSVersion) UDOS_VERSION="$value" ;;
      esac
    fi
  done < "$INSTANCE_FILE"
else
  UDOS_VERSION="uDOS Beta v1.6.1"
fi

# If called with 'check' argument, output simple status summary and exit
if [[ "$1" == "check" ]]; then
  if [[ ! -f "$MOVE_LOG" ]]; then
    echo "Status: Move log file not found."
    exit 1
  fi

  # Count number of recent moves (lines) in today's move log
  RECENT_MOVES_COUNT=$(wc -l < "$MOVE_LOG" 2>/dev/null)
  if ! [[ "$RECENT_MOVES_COUNT" =~ ^[0-9]+$ ]]; then
    RECENT_MOVES_COUNT=0
  fi

  # Validate essential values
  if [[ -z "$USER_NAME" || "$USER_NAME" == "Unknown" ]] || [[ -z "$LOCATION" || "$LOCATION" == "Unknown" ]] || [[ -z "$ACTIVE_MISSION" ]]; then
    echo "Status: Invalid or missing data."
    exit 1
  fi

  echo "Username: $USER_NAME"
  echo "Location: $LOCATION"
  echo "Active Mission: $ACTIVE_MISSION"
  echo "Recent Moves Today: $RECENT_MOVES_COUNT"
  exit 0
fi

# Recent Moves
RECENT_DISPLAY=()
if [[ -f "$MOVE_LOG" ]]; then
  recent_lines=()
  while IFS= read -r line; do
    recent_lines+=("$line")
  done < <(tail -n 5 "$MOVE_LOG")
  if [[ ${#recent_lines[@]} -eq 0 ]]; then
    RECENT_DISPLAY+=("No recent moves logged.")
  else
    for line in "${recent_lines[@]}"; do
      trimmed_line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      RECENT_DISPLAY+=("$trimmed_line")
    done
  fi
else
  RECENT_DISPLAY+=("No recent moves logged.")
fi

# Map Peek
MAP_PEEK="No map data available."
MAP_FILE="$KNOWLEDGE_DIR/map/current_region.txt"
if [[ -f "$MAP_FILE" ]]; then
  MAP_PEEK=$(head -5 "$MAP_FILE" | sed 's/^/  /')
fi

# Tower of Knowledge placeholder
ROOMS_INDEXED_COUNT=0
ROOMS_DIR="$KNOWLEDGE_DIR/rooms"
if [[ -d "$ROOMS_DIR" ]]; then
  ROOMS_INDEXED_COUNT=$(find "$ROOMS_DIR" -maxdepth 1 -type f -name '*.md' | wc -l)
fi
TOWER_PEAK="Rooms Indexed: $ROOMS_INDEXED_COUNT"

# Health Check placeholder replaced with parsed [STATS] lines from current move log
HEALTH_CHECK_LINES=()
if [[ -f "$MOVE_LOG" ]]; then
  stats_lines=()
  while IFS= read -r line; do
    stats_lines+=("$line")
  done < <(grep '^\[STATS\]' "$MOVE_LOG")
  if [[ ${#stats_lines[@]} -gt 0 ]]; then
    for stat_line in "${stats_lines[@]}"; do
      HEALTH_CHECK_LINES+=("$stat_line")
    done
  else
    HEALTH_CHECK_LINES=("No stat log available. Run refresh or generate_stats.sh.")
  fi
else
  HEALTH_CHECK_LINES=("No stat log available. Run refresh or generate_stats.sh.")
fi

ENCRYPTION_STATUS="[ENABLED]"
SHARING_STATUS="$SHARING"
LIFESPAN_STATUS="$LIFESPAN"
SYNC_STATUS="Local OK, No pending exports"

# Compute Moves Remaining
if [[ "$LIFESPAN" == "0" ]]; then
  MOVES_REMAINING="∞"
else
  # Attempt to parse LIFESPAN as number, default to 0 if invalid
  if [[ "$LIFESPAN" =~ ^[0-9]+$ ]]; then
    MOVES_REMAINING=$((LIFESPAN * 1000))
  else
    MOVES_REMAINING="N/A"
  fi
fi

HEALTH_CHECK_LINES+=("Moves Remaining: $MOVES_REMAINING")


#
#
# Use new dashboard template directory
DASHBOARD_TEMPLATE_DIR="$UHOME/uTemplate/dashboard"

if [[ ! -d "$DASHBOARD_TEMPLATE_DIR" ]]; then
  echo "🚫 Missing dashboard templates: $DASHBOARD_TEMPLATE_DIR"
  exit 2
fi

# Unified dashboard rendering
bash "$UROOT/scripts/make-dash.sh"
cat "$UROOT/uMemory/rendered/dash-rendered.md"

if [[ ! -s "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md" && "$UCODE_HEADLESS" == "true" ]]; then
  echo "⚠️ Headless fallback: dashboard output suppressed."
  exit 1
elif [[ ! -s "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md" ]]; then
  ERROR_LOG_DIR="$UHOME/uMemory/logs/errors"
  mkdir -p "$ERROR_LOG_DIR"
  ERROR_FILE="$ERROR_LOG_DIR/fallback-$(date +%Y-%m-%d_%H%M%S).md"
  {
    echo "# 🚨 Dashboard Fallback Triggered"
    echo "- Timestamp: $(date)"
    echo "- User: $USER_NAME"
    echo "- Location: $LOCATION"
    echo "- Reason: Dashboard failed to render or timed out."
    echo ""
    echo "Recent moves: $(tail -n 5 "$MOVE_LOG" 2>/dev/null)"
  } > "$ERROR_FILE"

  echo "# 📊 uDOS Dashboard — (Fallback Mode)" > "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
  echo "Username: ${USER_NAME:-unknown}" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
  echo "Location: ${LOCATION:-unknown}" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
  echo "Recent Moves: (unavailable)" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
  echo "Health: (unknown)" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
  echo "" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

  if [[ "$UCODE_HEADLESS" == "true" ]]; then
    echo "🛟 Fallback dashboard in headless mode. Skipping DESTROY prompt."
    exit 1
  fi

  echo "🛟 Dashboard fallback rendered due to missing or broken data."
  echo ""
  echo "💥 FATAL ERROR: Dashboard failed to initialize properly."
  echo "🧹 To repair your environment, a full DESTROY will now be offered."
  echo ""
  read -n1 -rp "❓ Proceed with DESTROY and environment reset? [Y/n]: " destroy_confirm
  echo ""
  case "${destroy_confirm^^}" in
    Y|"") echo "☠️ Destroying environment..."; "$UHOME/scripts/uCode.sh" DESTROY ;;
    *) echo "🛑 Cancelled. uDOS may not function correctly until reset." ;;
  esac
fi

echo ""
echo "🧭 Use 'help' for available commands."
echo "Make your next move, Master."
echo "✅ Dashboard rendering complete."