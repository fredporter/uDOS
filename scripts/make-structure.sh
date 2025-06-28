#!/bin/bash
# make-structure.sh — Ensure required uDOS directories and templates exist

UHOME="${HOME}/uDOS"
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
  fi
}


# Ensure dashboards subdirectory exists
DASHBOARD_DIR="$TEMPLATE_DIR/dashboards"
mkdir -p "$DASHBOARD_DIR"

create_template "$TEMPLATE_DIR/mission-template.md" "Mission"
create_template "$TEMPLATE_DIR/milestone-template.md" "Milestone"
create_template "$TEMPLATE_DIR/legacy-template.md" "Legacy"

# Create dashboard templates if they don't exist
create_template "$DASHBOARD_DIR/dashboard-header.md" "Dashboard Header"
create_template "$DASHBOARD_DIR/dashboard-footer.md" "Dashboard Footer"
create_template "$DASHBOARD_DIR/dashboard-map.md" "Dashboard Map"
create_template "$DASHBOARD_DIR/dashboard-knowledge.md" "Dashboard Knowledge"
create_template "$DASHBOARD_DIR/dashboard-health.md" "Dashboard Health"
create_template "$DASHBOARD_DIR/dashboard-recent.md" "Dashboard Recent"
create_template "$DASHBOARD_DIR/dashboard-legacy.md" "Dashboard Legacy"
create_template "$DASHBOARD_DIR/dashboard-rooms.md" "Dashboard Rooms"
create_template "$DASHBOARD_DIR/dashboard-focus.md" "Dashboard Focus"

echo "✅ uDOS directory structure initialized and verified."