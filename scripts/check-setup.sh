#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UHOME="$HOME/uDOS"

# Load reusable prompt questions and default vars
source "$UHOME/scripts/load_user_prompts.sh"

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
  echo "🧑 No valid user profile found."
  read -rp "$USERNAME_PROMPT" username
  read -rp "$LOCATION_PROMPT" location
  read -rp "$TIMEZONE_PROMPT" timezone
  utc_offset=$(date +%z | sed 's/^\([+-][0-9][0-9]\)\([0-9][0-9]\)$/\1:\2/')
  mkdir -p "$(dirname "$USER_FILE")"
  {
    echo "Username: $username"
    echo "Location: $location"
    echo "Timezone: $timezone"
    echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } > "$USER_FILE"
  echo "[$(date +%H:%M:%S)] → check-setup → user.md (re)created in sandbox/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ ! -f "$IDENTITY_FILE" ]]; then
  mkdir -p "$(dirname "$IDENTITY_FILE")"
  echo "Installation ID: [Pending]" > "$IDENTITY_FILE"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
  echo "Timezone: $timezone" >> "$IDENTITY_FILE"
  echo "UTC Offset: $utc_offset" >> "$IDENTITY_FILE"
  echo "Version: Beta v1.6.3" >> "$IDENTITY_FILE"
  echo "[$(date +%H:%M:%S)] → check-setup → identity.md (re)created in state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

