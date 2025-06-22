#!/bin/bash
# === uOS Move 011-B: Log New Mission [v1.6 compliant] ===

UROOT="$HOME/uOS"
UMEMORY="$UROOT/uMemory/missions"
TEMPLATE="$UROOT/templates/mission-template.md"
DEFAULT_EDITOR="${EDITOR:-nano}"

# ──────────────────────────────────────────────
# 🔤 Canonical Filename Generator (v1.6)
# ──────────────────────────────────────────────
generate_filename() {
  local CATEGORY="$1"         # e.g. uML, uIO, uMS
  local LOCATION="${2:-F00:00:00}"  # fallback if unknown
  local TZCODE="P10"

  local DATESTAMP=$(date +%Y%m%d)
  local TIMESTAMP=$(date +%H%M%S%3N)
  local LOCATION_SAFE=$(echo "$LOCATION" | tr ':' '-')

  echo "${CATEGORY}-${DATESTAMP}-${TIMESTAMP}-${TZCODE}-${LOCATION_SAFE}.md"
}

# ──────────────────────────────────────────────
# 🧠 Generate mission log filename
# ──────────────────────────────────────────────
LOCATION=$(cat "$UROOT/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
FILENAME=$(generate_filename "uMS" "$LOCATION")
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