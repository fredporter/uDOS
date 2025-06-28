#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

# Load reusable prompt questions and default vars


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
  username=$(grep "^Username:" "$USER_FILE" | cut -d':' -f2 | xargs)
  location=$(grep "^Location:" "$USER_FILE" | cut -d':' -f2 | xargs)
  timezone=$(grep "^Timezone:" "$USER_FILE" | cut -d':' -f2 | xargs)

  [[ -z "$username" || -z "$location" || -z "$timezone" ]] && need_prompt=true
else
  need_prompt=true
fi

if [[ "$need_prompt" = true ]]; then
  echo "🧑 Created user profile in sandbox/user.md"
  echo "🧑 Creating user profile. Please provide the following details:"
  if [[ -z "$username" ]]; then read -rp "Username: " username; fi
  if [[ -z "$location" ]]; then read -rp "Location: " location; fi
  if [[ -z "$timezone" ]]; then read -rp "Timezone: " timezone; fi
  utc_offset=$(date +%z | sed 's/^\([+-][0-9][0-9]\)\([0-9][0-9]\)$/\1:\2/')
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
  location=$(grep "^-" "$USER_FILE" | grep "Location" | cut -d':' -f2 | xargs)
  timezone=$(grep "^-" "$USER_FILE" | grep "Timezone" | cut -d':' -f2 | xargs)

  echo "# Instance File" > "$UHOME/sandbox/instance.md"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$UHOME/sandbox/instance.md"
  echo "Version: Beta v1.6.1" >> "$UHOME/sandbox/instance.md"

  echo "# Identification File" > "$UHOME/sandbox/identification.md"
  echo "User: $username" >> "$UHOME/sandbox/identification.md"
  echo "Location: $location" >> "$UHOME/sandbox/identification.md"
  echo "Timezone: $timezone" >> "$UHOME/sandbox/identification.md"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$UHOME/sandbox/identification.md"
  echo "UTC Offset: $utc_offset" >> "$UHOME/sandbox/identification.md"
  echo "[$(date +%H:%M:%S)] → check-setup → user.md (re)created in sandbox/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

if [[ ! -f "$UHOME/uMemory/state/identification.md" ]]; then
  mkdir -p "$UHOME/uMemory/state"
  mv "$UHOME/sandbox/instance.md" "$UHOME/uMemory/state/"
  mv "$UHOME/sandbox/identification.md" "$UHOME/uMemory/state/"
  echo "[$(date +%H:%M:%S)] → check-setup → sandbox state files moved to uMemory/state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  cp "$UHOME/uMemory/state/identification.md" "$UHOME/uMemory/state/identity.md"
fi
