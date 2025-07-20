#!/bin/bash
# Template Validation Tool
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$UDEV/../uCode/template-validation.sh"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <template-file|directory>"
    echo
    echo "Examples:"
    echo "  $0 ../uTemplate/datagets/user-setup.json"
    echo "  $0 ../uTemplate/datagets/"
    exit 1
fi

target="$1"
if [[ -f "$target" ]]; then
    validate_dataget_schema "$target"
elif [[ -d "$target" ]]; then
    validate_template_files "$target"
else
    echo "Error: $target is not a valid file or directory"
    exit 1
fi
