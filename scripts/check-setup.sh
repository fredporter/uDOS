#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UDOSE_HOME="/root/uDOS"

LOG_FILE="$UDOSE_HOME/uMemory/logs/permissions-$(date +%Y-%m-%d).md"
TARGET_DIRS=(
  "$UDOSE_HOME/scripts"
  "$UDOSE_HOME/uTemplate"
  "$UDOSE_HOME/sandbox"
  "$UDOSE_HOME/uMemory"
  "$UDOSE_HOME/uMemory/logs"
)
SYSTEM_CMD="$UDOSE_HOME/scripts/command.sh"

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
USER_FILE="$UDOSE_HOME/sandbox/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  echo ""
  echo "🔑 No identity found. Let's set up your user profile."

  read -rp "👤 Enter your preferred username: " username
  read -rsp "🔒 Enter a password: " password
  echo ""
  read -rp "📍 Enter your current location code (e.g., F00:00:00): " location

  mkdir -p "$(dirname "$USER_FILE")"
  {
    echo "Username: $username"
    echo "Password: $password"
    echo "Location: $location"
    echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } > "$USER_FILE"

  echo "✅ User identity created at $USER_FILE"

  IDENTITY_FILE="$UDOSE_HOME/identity.md"
  echo "$username" > "$IDENTITY_FILE"
  echo "✅ System identity stored at $IDENTITY_FILE"

  MOVE_LOG="$UDOSE_HOME/uMemory/logs/moves/moves-$(date +%Y-%m-%d).md"
  mkdir -p "$(dirname "$MOVE_LOG")"
  echo "- [$(date +%H:%M)] ✅ System setup completed by '$username' at $location" >> "$MOVE_LOG"
fi