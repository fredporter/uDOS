#!/bin/bash
# make-log.sh — Unified logger for uDOS missions, milestones, legacies (v1.6.1)

UDOSE_HOME="/root/uDOS"

generate_filename() {
  CATEGORY="$1" # e.g. uML, uIO, uTA
  LOCATION="${2:-F00:00:00}" # default fallback
  TIMEZONE="${3:-AEST}" # human-readable timezone code

  # Format timestamps
  DATESTAMP=$(date +%Y%m%d)
  TIMESTAMP=$(date +%H%M%S%3N)

  # Normalise location for filename
  LOCATION_SAFE=$(echo "$LOCATION" | tr -d ':')

  echo "${CATEGORY}-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
}

TARGET="$1"  # mission, milestone, legacy
LOCATION=$(cat "$UDOSE_HOME/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
TIMEZONE="AEST"

if [[ -z "$TARGET" ]]; then
  echo "❌ Usage: make-log.sh [mission|milestone|legacy]"
  exit 1
fi

FILE_NAME=$(generate_filename "$TARGET" "$LOCATION" "$TIMEZONE")
DEST="$UDOSE_HOME/uMemory/${TARGET}s/$FILE_NAME"
TEMPLATE="$UDOSE_HOME/uTemplate/${TARGET}-template.md"

mkdir -p "$(dirname "$DEST")"

if [[ -f "$TEMPLATE" ]]; then
  cp "$TEMPLATE" "$DEST"
else
  echo "# $TARGET created on $(date)" > "$DEST"
  echo "⚠️ No template found. Created blank file."
fi

echo "📄 New $TARGET logged: $DEST"