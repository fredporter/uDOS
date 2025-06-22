#!/bin/bash
# filename-gen.sh — uOS Filename Generator v1.6

generate_filename() {
  CATEGORY="$1" # e.g. uML, uIO, uTA
  LOCATION="${2:-F00:00:00}" # default fallback
  TIMEZONE="P10" # hardcoded for now, will support dynamic later

  # Format timestamps
  DATESTAMP=$(date +%Y%m%d)
  TIMESTAMP=$(date +%H%M%S%3N)

  # Normalise location for filename
  LOCATION_SAFE=$(echo "$LOCATION" | tr ':' '-')

  echo "${CATEGORY}-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
}