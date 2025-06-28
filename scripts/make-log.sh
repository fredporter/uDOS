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
  cp "$TEMPLATE" "$DEST"
else
  echo "# $TARGET created on $(date)" > "$DEST"
  echo "⚠️ No template found. Created blank file."
fi


# Log outcome to move-log (only keep long-form file if content exceeds 120 characters)
CONTENT_LENGTH=$(wc -c < "$DEST")
if [[ "$CONTENT_LENGTH" -le 120 ]]; then
  echo "ℹ️ Content too short, skipping file creation."
  rm "$DEST"
  echo "[$(date +%H:%M:%S)] → make-log $TARGET → inline entry only" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
else
  echo "[$(date +%H:%M:%S)] → make-log $TARGET → see: ${DEST#"$UHOME/"}" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  echo "✅ Long-form log created at ${DEST#"$UHOME/"}"
  echo "📄 New $TARGET logged: $DEST"
fi