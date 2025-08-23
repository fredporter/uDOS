#!/bin/bash

# uDOS Workflow Command Integration v1.3.3
# Main entry point for workflow management
# Location: /Users/agentdigital/uDOS/dev/workflow.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_MANAGER="$SCRIPT_DIR/workflow-manager.sh"

# Colors
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Quick header
echo -e "${CYAN}🔄 uDOS Workflow System v1.3.3${NC}"
echo ""

# Check if we're in dev mode (VS Code context)
if [[ "${VSCODE_INJECTION:-}" == "1" ]] || [[ -n "${VSCODE_PID:-}" ]] || [[ -n "${TERM_PROGRAM:-}" && "$TERM_PROGRAM" == "vscode" ]]; then
    echo -e "${WHITE}📍 Dev Mode Detected - Enhanced Features Available${NC}"
    echo ""
fi

# Execute the workflow manager with all arguments
exec "$WORKFLOW_MANAGER" "$@"
