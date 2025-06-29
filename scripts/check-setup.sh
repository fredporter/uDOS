#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

# Load reusable prompt questions and default vars

echo "[$(date +%H:%M:%S)] → check-setup started" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

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


get_stat() {
  # Try GNU stat format first, fallback to BSD/macOS stat
  if stat -c "%a %U" "$1" &>/dev/null; then
    stat -c "%a %U" "$1"
  else
    stat -f "%Lp %Su" "$1"
  fi
}

USER_FILE="$UHOME/sandbox/user.md"

if [[ ! -f "$USER_FILE" || -z "$(grep 'Username:' "$USER_FILE")" ]]; then
  echo "🧑 Let's create your user profile for uDOS."

  # Prompt for user info
  echo -n "📝 Username: "; read username
  while [[ -z "$username" ]]; do
    echo "⚠️  Username cannot be empty."
    echo -n "📝 Username: "; read username
  done

  echo -n "🔐 Password (input hidden): "; read -s password; echo ""

  echo -n "🌍 Location (e.g., Sydney): "; read location
  [[ -z "$location" ]] && location="Unknown"

  # Detect timezone
  timezone=$(date +%Z)
  utc_offset=$(date +%z)
  echo "🕒 Detected timezone: $timezone (UTC$utc_offset)"
  echo -n "📌 Is this correct? (Y/n): "; read confirm_tz
  if [[ "$confirm_tz" =~ ^[Nn]$ ]]; then
    echo -n "🌐 Enter your timezone (e.g., Australia/Sydney): "; read tz_input
    if [[ -n "$tz_input" ]]; then
      export TZ="$tz_input"
      timezone=$(date +%Z)
      utc_offset=$(date +%z)
      echo "📍 Updated timezone: $timezone (UTC$utc_offset)"
    fi
  fi

  # Now write user.md
  mkdir -p "$UHOME/sandbox"
  {
    echo "# uDOS User Profile"
    echo "- **Username**: $username"
    echo "- **Password**: $password"
    echo "- **Location**: $location"
    echo "- **Timezone**: $timezone"
  } > "$USER_FILE"

  echo "[$(date +%H:%M:%S)] → check-setup → user.md created in sandbox/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

mkdir -p "$UHOME/uMemory/state"
echo "# Instance File" > "$UHOME/uMemory/state/instance.md"
echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$UHOME/uMemory/state/instance.md"
echo "Version: Beta v1.6.1" >> "$UHOME/uMemory/state/instance.md"
echo "Location: $location" >> "$UHOME/uMemory/state/instance.md"
echo "Timezone: $timezone" >> "$UHOME/uMemory/state/instance.md"
echo "UTC Offset: $utc_offset" >> "$UHOME/uMemory/state/instance.md"

IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ ! -f "$IDENTITY_FILE" ]]; then
  echo "# Identity File" > "$IDENTITY_FILE"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
  echo "Version: Beta v1.6.1" >> "$IDENTITY_FILE"
  echo "Timezone: $timezone" >> "$IDENTITY_FILE"
  echo "UTC Offset: $utc_offset" >> "$IDENTITY_FILE"
  echo "Install Location: $location" >> "$IDENTITY_FILE"
  echo "[$(date +%H:%M:%S)] → check-setup → identity.md created in state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
