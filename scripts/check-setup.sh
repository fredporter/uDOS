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

# Prompt for user input if sandbox/user.md is missing or incomplete
USER_FILE="$UHOME/sandbox/user.md"
need_prompt=false

if [[ -f "$USER_FILE" ]]; then
  username=$(grep "Username" "$USER_FILE" | head -n1 | cut -d':' -f2 | xargs)
  password=$(grep "Password" "$USER_FILE" | head -n1 | cut -d':' -f2 | xargs)
  location=$(grep "Location" "$USER_FILE" | head -n1 | cut -d':' -f2 | xargs)
  timezone=$(grep "Timezone" "$USER_FILE" | head -n1 | cut -d':' -f2 | xargs)

  [[ -z "$username" || -z "$password" || -z "$location" || -z "$timezone" ]] && need_prompt=true
else
  need_prompt=true
fi

if [[ "$need_prompt" = true ]]; then
  echo "🧑 Created user profile in sandbox/user.md"
  echo "🧑 Creating user profile. Please provide the following details:"
  if [[ -z "$username" ]]; then read -rp "Username: " username; fi
  if [[ -z "$password" ]]; then read -rsp "Password: " password; echo ""; fi
  if [[ -z "$location" ]]; then read -rp "Location: " location; fi

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

  mkdir -p "$UHOME/sandbox"
  {
    echo "# uDOS User Profile"
    echo "- **Username**: $username"
    echo "- **Password**: $password"
    echo "- **Location**: $location"
    echo "- **Timezone**: $timezone"
  } > "$USER_FILE"

  # Refresh local vars from saved user.md
  username=$(grep "^-" "$USER_FILE" | grep "Username" | cut -d':' -f2 | xargs)
  password=$(grep "^-" "$USER_FILE" | grep "Password" | cut -d':' -f2 | xargs)
  location=$(grep "^-" "$USER_FILE" | grep "Location" | cut -d':' -f2 | xargs)
  timezone=$(grep "^-" "$USER_FILE" | grep "Timezone" | cut -d':' -f2 | xargs)

  echo "[$(date +%H:%M:%S)] → check-setup → user.md (re)created in sandbox/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
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
