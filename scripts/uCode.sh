#!/bin/bash
# dashboard-sync.sh — uOS status dashboard

# Environment paths (must match uCode)
UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"

# User profile file (must exist and be maintained)
USER_FILE="$MEMORY_DIR/state/user.md"
MISSION_FILE="$MEMORY_DIR/state/current_mission.txt"
MOVES_LOG="$MEMORY_DIR/logs/session-$(date +%Y-%m-%d).md"
MAP_FILE="$KNOWLEDGE_DIR/map/current_region.txt"
TOWER_INDEX="$KNOWLEDGE_DIR/tower/indexed_rooms.txt"
STAT_LOG="$MEMORY_DIR/logs/statistics.log"

# Load user info safely
if [[ -f "$USER_FILE" ]]; then
  username=$(grep -m1 '^**Username**:' "$USER_FILE" | sed -E 's/\*\*Username\*\*:[[:space:]]*//')
  location=$(grep -m1 '^**Location**:' "$USER_FILE" | sed -E 's/\*\*Location\*\*:[[:space:]]*//')
  privacy=$(grep -m1 '^**Privacy**:' "$USER_FILE" | sed -E 's/\*\*Privacy\*\*:[[:space:]]*//')
  lifespan=$(grep -m1 '^**Lifespan**:' "$USER_FILE" | sed -E 's/\*\*Lifespan\*\*:[[:space:]]*//')
else
  username="Unknown"
  location="Unknown"
  privacy="n/a"
  lifespan="n/a"
fi

# Load mission info
if [[ -f "$MISSION_FILE" ]]; then
  mission=$(head -n 1 "$MISSION_FILE")
else
  mission="none"
fi

# Get current datetime for header
datetime=$(date '+%Y-%m-%d %H:%M:%S')

# Gather recent moves (session file)
if [[ -f "$MOVES_LOG" ]] && grep -q '^-\s*\[.*\]\s*Move:' "$MOVES_LOG"; then
  recent_moves=$(grep '^-\s*\[.*\]\s*Move:' "$MOVES_LOG" | tail -5 | sed -E 's/- \[(.*)\] Move: (.*)/\[\1\] \2/')
else
  recent_moves="No recent moves logged."
fi

# Map Peek content
if [[ -f "$MAP_FILE" ]]; then
  map_peek=$(head -5 "$MAP_FILE")
else
  map_peek="No map data available."
fi

# Tower of Knowledge snapshot
if [[ -f "$TOWER_INDEX" ]]; then
  tower_snapshot=$(head -5 "$TOWER_INDEX")
else
  tower_snapshot="No rooms indexed yet."
fi

# Health check (simple placeholder)
if [[ -f "$STAT_LOG" ]]; then
  health_status="Stat log available."
else
  health_status="No stat log available. Run generate_stats.sh."
fi

# Sync Status placeholder (can be expanded)
sync_status="Local OK, No pending exports"

# Encryption placeholder (can be dynamic)
encryption_status="[ENABLED]"

# Calculate padding helper
pad() {
  local str="$1"
  local width="$2"
  local len=${#str}
  if (( len < width )); then
    printf "%s%*s" "$str" $((width - len)) ""
  else
    printf "%.0s" $(seq 1 $width)
  fi
}

# Dashboard width (adjust if needed)
DASH_WIDTH=79

# Print dashboard
clear
echo "╔$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╗"
echo "║ User: $(pad "$username" 30) $datetime ║"
echo "║ Location: $(pad "$location" $((DASH_WIDTH - 12)))║"
echo "║ Active Mission: $(pad "$mission" $((DASH_WIDTH - 17)))║"
echo "╠$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╣"
echo "║ 🔎 Today’s Focus$(printf '%*s' $((DASH_WIDTH - 14)) '')║"
echo "║ Suggested Move: Run 'log_mission.sh' to begin your next journey$(printf '%*s' $((DASH_WIDTH - 50)) '')║"
echo "║ Region Pointer: /vault/crypt$(printf '%*s' $((DASH_WIDTH - 24)) '')║"
echo "╠$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╣"
echo "║ 📝 Recent Moves$(printf '%*s' $((DASH_WIDTH - 15)) '')║"
if [[ "$recent_moves" == "No recent moves logged." ]]; then
  echo "║ $recent_moves$(printf '%*s' $((DASH_WIDTH - ${#recent_moves} - 2)) '')║"
else
  while IFS= read -r line; do
    echo "║ $line$(printf '%*s' $((DASH_WIDTH - ${#line} - 2)) '')║"
  done <<< "$recent_moves"
fi
echo "╠$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╣"
echo "║ 🗺️  Map Peek$(printf '%*s' $((DASH_WIDTH - 11)) '')║"
if [[ "$map_peek" == "No map data available." ]]; then
  echo "║ $map_peek$(printf '%*s' $((DASH_WIDTH - ${#map_peek} - 2)) '')║"
else
  while IFS= read -r line; do
    echo "║ $line$(printf '%*s' $((DASH_WIDTH - ${#line} - 2)) '')║"
  done <<< "$map_peek"
fi
echo "╠$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╣"
echo "║ 🧠 Tower of Knowledge$(printf '%*s' $((DASH_WIDTH - 22)) '')║"
if [[ "$tower_snapshot" == "No rooms indexed yet." ]]; then
  echo "║ $tower_snapshot$(printf '%*s' $((DASH_WIDTH - ${#tower_snapshot} - 2)) '')║"
else
  while IFS= read -r line; do
    echo "║ $line$(printf '%*s' $((DASH_WIDTH - ${#line} - 2)) '')║"
  done <<< "$tower_snapshot"
fi
echo "╠$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╣"
echo "║ ✅ Health Check$(printf '%*s' $((DASH_WIDTH - 15)) '')║"
echo "║ $health_status$(printf '%*s' $((DASH_WIDTH - ${#health_status} - 2)) '')║"
echo "║ Encryption: $encryption_status   Privacy: $privacy   Lifespan: $lifespan$(printf '%*s' $((DASH_WIDTH - ${#encryption_status} - ${#privacy} - ${#lifespan} - 22)) '')║"
echo "║ Sync Status: $sync_status$(printf '%*s' $((DASH_WIDTH - ${#sync_status} - 14)) '')║"
echo "╚$(printf '═%.0s' $(seq 1 $DASH_WIDTH))╝"
echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."