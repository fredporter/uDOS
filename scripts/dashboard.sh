#!/bin/bash
# uDOS Dashboard Beta v1.6 — Combines static blocks + live memory stats

UHOME="${HOME}/uDOS"
UROOT="$UHOME"   # Base directory

bash "$UROOT/scripts/check-setup.sh" >/dev/null

# Header
clear
USER_FILE="$UROOT/sandbox/user.md"
if [[ -f "$USER_FILE" && -s "$USER_FILE" ]]; then
  USER_NAME=$(grep -i '^Username:' "$USER_FILE" | head -n1 | cut -d':' -f2- | xargs)
  USER_NAME=$(echo -n "$USER_NAME" | sed 's/[[:space:]]*$//')
  if [[ -z "$USER_NAME" ]]; then
    USER_NAME="(unknown)"
  fi
else
  USER_NAME="(unknown)"
fi

### Gather info for blocks
DATE_NOW="$(date '+%Y-%m-%d %H:%M:%S')"
LOCATION=$(grep -i '^Location:' "$UROOT/uMemory/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LOCATION=$(echo -n "$LOCATION" | sed 's/[[:space:]]*$//')
[ -z "$LOCATION" ] && LOCATION="Unknown"
MISSION_FILE="$UROOT/uMemory/state/current_mission.md"
if [[ -f "$MISSION_FILE" ]]; then
  ACTIVE_MISSION=$(grep -i '^Title:' "$MISSION_FILE" | head -n1 | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
if [[ -z "$ACTIVE_MISSION" ]]; then
  ACTIVE_MISSION=$(grep -i '^Mission:' "$UROOT/uMemory/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
[ -z "$ACTIVE_MISSION" ] && ACTIVE_MISSION="(none)"

bash "$UROOT/scripts/make-dash.sh"

cat "$UROOT/uMemory/rendered/dash-rendered.md" | grep -v '^<!--'
