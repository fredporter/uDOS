#!/bin/bash
# uCODE: RUN - Execute modular uSCRIPT
set -euo pipefail

RED='\033[0;31m'
NC='\033[0m'
USCRIPT="$UDOS_ROOT/uSCRIPT"
script_name="${1:-}" # Name of script to run
if [[ -z "$script_name" ]]; then
    echo -e "${RED}❌ No script specified${NC}"
    exit 1
fi
script_path="$USCRIPT/active/$script_name.sh"
if [[ -f "$script_path" && -x "$script_path" ]]; then
    "$script_path"
else
    echo -e "${RED}❌ Script not found: $script_name${NC}"
    exit 1
fi
