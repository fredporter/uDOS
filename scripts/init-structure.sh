

#!/bin/bash
# init-structure.sh — Ensure required uDOS directories and templates exist

UDOSE_HOME="/root/uDOS"
TEMPLATE_DIR="$UDOSE_HOME/uTemplate"
SANDBOX_DIR="$UDOSE_HOME/sandbox"
MEMORY_DIR="$UDOSE_HOME/uMemory"
LOG_DIR="$MEMORY_DIR/logs"

# Create necessary directories
mkdir -p "$TEMPLATE_DIR" "$SANDBOX_DIR"
mkdir -p "$MEMORY_DIR/missions" "$MEMORY_DIR/milestones" "$MEMORY_DIR/moves" "$MEMORY_DIR/state" "$LOG_DIR"
mkdir -p "$UDOSE_HOME/uKnowledge/assets" "$UDOSE_HOME/uKnowledge/companion"

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

create_template "$TEMPLATE_DIR/mission-template.md" "Mission"
create_template "$TEMPLATE_DIR/milestone-template.md" "Milestone"
create_template "$TEMPLATE_DIR/legacy-template.md" "Legacy"

echo "✅ uDOS directory structure initialized."