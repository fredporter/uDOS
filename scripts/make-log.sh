#!/bin/bash
# make-log.sh — Logs a mission, milestone or legacy to uMemory (v1.6.1)

UHOME="${HOME}/uDOS"

generate_filename() {
  CATEGORY="$1" # e.g. uML, uIO, uTA
  LOCATION="${2:-F00:00:00}" # default fallback
  TIMEZONE="${3:-AEST}" # human-readable timezone code

  # Format timestamps
  DATESTAMP=$(date +%Y%m%d)
  TIMESTAMP=$(date +%H%M%S%3N)

  # Normalise location for filename
  LOCATION_SAFE=$(echo "$LOCATION" | tr -d ':')

  echo "${CATEGORY}-log-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
}

TARGET="$1"  # mission, milestone, legacy
LOCATION=$(cat "$UHOME/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
TIMEZONE="AEST"

if [[ -z "$TARGET" ]]; then
  echo "❌ Usage: make-log.sh [mission|milestone|legacy]"
  exit 1
fi

FILE_NAME=$(generate_filename "$TARGET" "$LOCATION" "$TIMEZONE")

# Rename legacy folder to singular form
if [[ "$TARGET" == "legacy" ]]; then
  DEST="$UHOME/uMemory/legacy/$FILE_NAME"
else
  DEST="$UHOME/uMemory/${TARGET}s/$FILE_NAME"
fi

TEMPLATE="$UHOME/uTemplate/${TARGET}-template.md"

mkdir -p "$(dirname "$DEST")"

if [[ -f "$TEMPLATE" ]]; then
  CONTENT_LENGTH=$(wc -c < "$TEMPLATE")
  if [[ "$CONTENT_LENGTH" -le 120 ]]; then
    echo "ℹ️ Template content too short, skipping file creation."
    exit 0
  fi
  cp "$TEMPLATE" "$DEST"
else
  echo "# $TARGET created on $(date)" > "$DEST"
  echo "⚠️ No template found. Created blank file."
fi

echo "📄 New $TARGET logged: ${DEST#"$UHOME/"}"

# Log to move-log
LOG_FILE="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
echo "📄 [$TIMESTAMP] $TARGET saved: ${DEST#"$UHOME/"}" >> "$LOG_FILE"