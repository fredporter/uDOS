#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"

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

# Prompt for user identity setup if not present
USER_FILE="$UHOME/sandbox/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  if [ ! -t 0 ]; then
    echo "⚠️ Non-interactive shell detected. Creating default identity."
    username="default"
    password="none"
    location="unknown"
  else
    echo ""
    echo "🔑 No identity found. Let's set up your user profile."

    echo ""; read -rp "👤 Enter your preferred username: " username
    echo ""; read -rsp "🔒 Enter a password: " password
    echo ""
    echo ""; read -rp "📍 Enter your current location code (e.g., F00:00:00): " location
    timezone=$(date +%Z)
    utc_offset=$(date +%z)
    echo "🕒 Detected timezone: $timezone (UTC$utc_offset)"
    echo ""; read -rp "📌 Is this correct? (Y/n): " confirm_tz
    if [[ "$confirm_tz" =~ ^[Nn]$ ]]; then
      echo ""; read -rp "🌐 Enter your correct timezone (e.g., Australia/Sydney): " tz_input
      if [[ -n "$tz_input" ]]; then
        export TZ="$tz_input"
        timezone=$(date +%Z)
        utc_offset=$(date +%z)
        echo "📍 Updated timezone: $timezone (UTC$utc_offset)"
      fi
    fi
    location="$timezone"
  fi

  mkdir -p "$(dirname "$USER_FILE")"
  {
    echo "Username: $username"
    echo "Password: $password"
    echo "Location: $location"
    echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } > "$USER_FILE"
  echo "Timezone: $(date +%Z)" >> "$USER_FILE"
  echo "UTC Offset: $(date +%z)" >> "$USER_FILE"

  echo "✅ User identity created at $USER_FILE"

  MOVE_LOG="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  mkdir -p "$(dirname "$MOVE_LOG")"
  echo "[$(date +%H:%M:%S)] → check-setup → user.md + identity.md created for '$username'" >> "$MOVE_LOG"
fi

IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
echo "Installation ID: [Pending]" > "$IDENTITY_FILE"
echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
echo "Timezone: $(date +%Z)" >> "$IDENTITY_FILE"
echo "UTC Offset: $(date +%z)" >> "$IDENTITY_FILE"
echo "Version: Beta v1.6.3" >> "$IDENTITY_FILE"
echo "[$(date +%H:%M:%S)] → check-setup → identity.md created in state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"

STATE_FILE="$UHOME/uMemory/state/instance.md"
echo "Location: $location" > "$STATE_FILE"
echo "Timezone: $timezone" >> "$STATE_FILE"
echo "UTC Offset: $utc_offset" >> "$STATE_FILE"

echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
