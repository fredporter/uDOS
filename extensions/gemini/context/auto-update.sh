#!/bin/bash
# Auto-update UC context when missions change

UC_CONTEXT_DIR="${HOME}/uDOS/uCompanion/context"
MISSIONS_DIR="${HOME}/uDOS/uMemory/missions"
MILESTONES_DIR="${HOME}/uDOS/uMemory/milestones"

# Check if mission files have been modified in the last 5 minutes
recent_changes() {
    if [[ -d "$MISSIONS_DIR" ]]; then
        find "$MISSIONS_DIR" -name "*.md" -mmin -5 -type f | head -1
    fi
    if [[ -d "$MILESTONES_DIR" ]]; then
        find "$MILESTONES_DIR" -name "*.md" -mmin -5 -type f | head -1
    fi
}

# Update context if changes detected
if [[ -n "$(recent_changes)" ]]; then
    "${UC_CONTEXT_DIR}/../context/uc-context-integration.sh" update
fi
