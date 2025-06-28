#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"

# Ensure directory structure exists before continuing
if [[ ! -d "$UHOME/uMemory" || ! -d "$UHOME/sandbox" || ! -d "$UHOME/uTemplate" ]]; then
  bash "$UHOME/scripts/make-structure.sh"
fi

TARGET_DIRS=(
  "$UHOME/scripts"
  "$UHOME/uTemplate"
  "$UHOME/sandbox"
  "$UHOME/uMemory"
  "$UHOME/uMemory/logs"
)

echo "[$(date +%H:%M:%S)] → check-setup started" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

get_stat() {
  # Try GNU stat format first, fallback to BSD/macOS stat
  if stat -c "%a %U" "$1" &>/dev/null; then
    stat -c "%a %U" "$1"
  else
    stat -f "%Lp %Su" "$1"
  fi
}

source "$UHOME/scripts/load_user_prompts.sh"

USER_FILE="$UHOME/sandbox/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  echo "⚠️ No identity found. Gathering details from user-setup.md..."
  bash "$UHOME/scripts/load_user_prompts.sh" "$UHOME/uTemplate/getdata-user-setup.md"
fi

mkdir -p "$(dirname "$USER_FILE")"
{
  echo "Username: $username"
  echo "Password: $password"
  echo "Location: $location"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Timezone: $timezone"
  echo "UTC Offset: $utc_offset"
} > "$USER_FILE"
echo "✅ User identity created at $USER_FILE"

MOVE_LOG="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$MOVE_LOG")"
echo "[$(date +%H:%M:%S)] → check-setup → user.md + identity.md created for '$username'" >> "$MOVE_LOG"

IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
echo "Installation ID: [Pending]" > "$IDENTITY_FILE"
echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
echo "Timezone: $timezone" >> "$IDENTITY_FILE"
echo "UTC Offset: $utc_offset" >> "$IDENTITY_FILE"
echo "Version: Beta v1.6.3" >> "$IDENTITY_FILE"
echo "[$(date +%H:%M:%S)] → check-setup → identity.md created in state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"

STATE_FILE="$UHOME/uMemory/state/instance.md"
echo "Location: $location" > "$STATE_FILE"
echo "Timezone: $timezone" >> "$STATE_FILE"
echo "UTC Offset: $utc_offset" >> "$STATE_FILE"

echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
