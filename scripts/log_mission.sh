#!/bin/bash
# === uDOS Move 011-B: Log New Mission [v1.6.1 compliant] ===

UDOSE_HOME="/root/uDOS"
UROOT="$UDOSE_HOME"
UMEMORY="$UROOT/uMemory/missions"
TEMPLATE="$UROOT/uTemplate/mission-template.md"
DEFAULT_EDITOR="${EDITOR:-nano}"

# ──────────────────────────────────────────────
# 🔤 Canonical Filename Generator (v1.6)
# ──────────────────────────────────────────────
generate_filename() {
  local CATEGORY="$1"         # e.g. uML, uIO, uMS
  local LOCATION="${2:-F00:00:00}"  # fallback if unknown

  local DATESTAMP=$(date +%Y%m%d)
  local TIMESTAMP=$(date +%H%M%S%3N)
  local LOCATION_SAFE=$(echo "$LOCATION" | tr -d ':')
  local TIMEZONE="AEST"  # Eventually this will be read from a system default
  echo "${CATEGORY}-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
}

# ──────────────────────────────────────────────
# 🧠 Generate mission log filename
# ──────────────────────────────────────────────
LOCATION=$(cat "$UROOT/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
FILENAME=$(generate_filename "mission" "$LOCATION")
DEST="$UMEMORY/$FILENAME"

# ──────────────────────────────────────────────
# 📦 Create file
# ──────────────────────────────────────────────
mkdir -p "$UMEMORY"
if cp "$TEMPLATE" "$DEST"; then
  echo "📝 Mission file created: $DEST"
else
  echo "# Mission created on $(date)" > "$DEST"
  echo "⚠️ No template found — blank mission file created."
fi

$DEFAULT_EDITOR "$DEST"