#!/bin/bash
# make-structure.sh — Ensure required uDOS directories and templates exist

UHOME="${HOME}/uDOS"
SANDBOX_DIR="$UHOME/sandbox"
mkdir -p "$SANDBOX_DIR"

TEMPLATE_DIR="$UHOME/uTemplate"
MEMORY_DIR="$UHOME/uMemory"
LOG_DIR="$MEMORY_DIR/logs"


# Defer sandbox creation to check-setup

# Create necessary directories
mkdir -p "$TEMPLATE_DIR"
mkdir -p "$MEMORY_DIR/missions" "$MEMORY_DIR/milestones" "$MEMORY_DIR/state" "$MEMORY_DIR/legacy" "$LOG_DIR" "$LOG_DIR/errors" "$LOG_DIR/moves"

# Create default templates if they don't exist
create_template() {
  local file="$1"
  local title="$2"
  if [ ! -f "$file" ]; then
    echo "# $title Template" > "$file"
    echo "Created: $(date)" >> "$file"
    echo "" >> "$file"
    [[ "$UCODE_VERBOSE" == "true" ]] && echo "Created template: $file"
  fi
}



# Ensure dashboard subdirectory exists
DASHBOARD_DIR="$TEMPLATE_DIR/dashboard"
mkdir -p "$DASHBOARD_DIR"

create_template "$TEMPLATE_DIR/mission-template.md" "Mission"
create_template "$TEMPLATE_DIR/milestone-template.md" "Milestone"
create_template "$TEMPLATE_DIR/legacy-template.md" "Legacy"

DASHBOARD_FILES=(
  "dashboard-header.md" "Dashboard Header"
  "dashboard-footer.md" "Dashboard Footer"
  "dashboard-map.md" "Dashboard Map"
  "dashboard-knowledge.md" "Dashboard Knowledge"
  "dashboard-health.md" "Dashboard Health"
  "dashboard-recent.md" "Dashboard Recent"
  "dashboard-legacy.md" "Dashboard Legacy"
  "dashboard-rooms.md" "Dashboard Rooms"
  "dashboard-focus.md" "Dashboard Focus"
)

for ((i=0; i<${#DASHBOARD_FILES[@]}; i+=2)); do
  file="$DASHBOARD_DIR/${DASHBOARD_FILES[i]}"
  title="${DASHBOARD_FILES[i+1]}"
  create_template "$file" "$title"
done
