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

  # Timezone and time confirmation
  if date +%N &>/dev/null; then
    now_time=$(date +"%Y-%m-%d %H:%M:%S.%3N")
  else
    now_time=$(date +"%Y-%m-%d %H:%M:%S")  # Fallback if %3N unsupported
  fi

  sys_tz=$(date +%Z)
  sys_utc=$(date +%z)

  echo "🕒 Current system time: $now_time"
  echo "🌍 Detected timezone: $sys_tz (UTC$sys_utc)"
  echo -n "📌 Is this correct? (Y/n): "; read confirm

  if [[ "$confirm" =~ ^[Nn]$ ]]; then
    echo -n "🌐 Enter a 3-letter timezone code (e.g., AES): "; read tz_code

    # Attempt to locate in dataset
    DATASET="$UHOME/uTemplate/dataset-time-space.md"
    if [[ -f "$DATASET" ]]; then
      line=$(grep -E "^$tz_code\|" "$DATASET")
      if [[ -n "$line" ]]; then
        IFS='|' read -r code gmt country city tile <<< "$line"
        timezone="$code"
        location_default="$city"
        tile="$tile"
      else
        echo "❌ Timezone code not found. Defaulting to UTC."
        timezone="UTC"
        location_default="London"
        tile="F30"
      fi
    else
      echo "⚠️ Dataset not found, skipping lookup."
      timezone="$tz_code"
      location_default="Unknown"
      tile="UNKNOWN"
    fi
  else
    timezone="UTC"
    location_default="London"
    tile="UNKNOWN"
  fi

  echo "📍 Default location based on timezone [$timezone]: $location_default"
  # Prompt for custom location (optional)
  echo -n "🛰️ Enter your location name/code (press Enter to use default): "; read location
  [[ -z "$location" ]] && location="$location_default"

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
INSTANCE_FILE="$UHOME/uMemory/state/instance.md"
echo "# uDOS Instance Settings" > "$INSTANCE_FILE"
echo "- **Timezone**: $timezone" >> "$INSTANCE_FILE"
echo "- **Time**: $now_time" >> "$INSTANCE_FILE"
echo "- **Location**: $location" >> "$INSTANCE_FILE"
echo "- **Tile**: $tile" >> "$INSTANCE_FILE"
echo "- **Confirmed**: Yes" >> "$INSTANCE_FILE"

IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ ! -f "$IDENTITY_FILE" ]]; then
  echo "# Identity File" > "$IDENTITY_FILE"
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$IDENTITY_FILE"
  echo "Version: Beta v1.6.1" >> "$IDENTITY_FILE"
  echo "Timezone: $timezone" >> "$IDENTITY_FILE"
  echo "Install Location: $location" >> "$IDENTITY_FILE"
  echo "[$(date +%H:%M:%S)] → check-setup → identity.md created in state/" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
fi

echo "[$(date +%H:%M:%S)] → check-setup completed" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
