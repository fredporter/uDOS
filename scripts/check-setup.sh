#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"

LOG_FILE="$UHOME/uMemory/logs/permissions-$(date +%Y-%m-%d).md"
TARGET_DIRS=(
  "$UHOME/scripts"
  "$UHOME/uTemplate"
  "$UHOME/sandbox"
  "$UHOME/uMemory"
  "$UHOME/uMemory/logs"
)
SYSTEM_CMD="$UHOME/scripts/command.sh"

mkdir -p "$(dirname "$LOG_FILE")"

get_stat() {
  # Try GNU stat format first, fallback to BSD/macOS stat
  if stat -c "%a %U" "$1" &>/dev/null; then
    stat -c "%a %U" "$1"
  else
    stat -f "%Lp %Su" "$1"
  fi
}

{
  echo "🔍 Checking permissions for uDOS..."

  for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      echo "Checking directory: $dir"
      read -r perm owner <<< "$(get_stat "$dir")"
      echo "Permissions: $perm, Owner: $owner"
      if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
        echo "✅ $dir permissions are correctly set."
      else
        echo "❌ $dir permissions are NOT correctly set."
      fi
    else
      echo "❌ Directory $dir does not exist."
    fi
  done

  if [ -f "$SYSTEM_CMD" ]; then
    echo "Checking system command script: $SYSTEM_CMD"
    read -r perm owner <<< "$(get_stat "$SYSTEM_CMD")"
    echo "Permissions: $perm, Owner: $owner"
    if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
      echo "✅ $SYSTEM_CMD permissions are correctly set."
    else
      echo "❌ $SYSTEM_CMD permissions are NOT correctly set."
      echo "🔧 Fixing permissions for $SYSTEM_CMD..."
      chmod 700 "$SYSTEM_CMD"
      echo "Permissions corrected to 700."
    fi
  else
    echo "❌ System command script $SYSTEM_CMD does not exist."
  fi

  echo "🧪 Permission check complete. Log saved to $LOG_FILE"
} | tee -a "$LOG_FILE"

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

    read -rp "👤 Enter your preferred username: " username
    read -rsp "🔒 Enter a password: " password
    echo ""
    read -rp "📍 Enter your current location code (e.g., F00:00:00): " location
    timezone=$(date +%Z)
    utc_offset=$(date +%z)
    echo "🕒 Detected timezone: $timezone (UTC$utc_offset)"
    read -rp "📌 Is this correct? (Y/n): " confirm_tz
    if [[ "$confirm_tz" =~ ^[Nn]$ ]]; then
      read -rp "🌐 Enter your correct timezone (e.g., Australia/Sydney): " tz_input
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

  MOVE_LOG="$UHOME/uMemory/logs/moves/moves-$(date +%Y-%m-%d).md"
  mkdir -p "$(dirname "$MOVE_LOG")"
  echo "- [$(date +%H:%M)] ✅ System setup completed by '$username' at $location" >> "$MOVE_LOG"
fi

IDENTITY_FILE="$UHOME/identity.md"
echo "User: $username" > "$IDENTITY_FILE"
echo "Location: $location" >> "$IDENTITY_FILE"
echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
echo "Timezone: $(date +%Z)" >> "$IDENTITY_FILE"
echo "UTC Offset: $(date +%z)" >> "$IDENTITY_FILE"
echo "✅ System identity stored at $IDENTITY_FILE"