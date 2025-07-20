#!/bin/bash
# Development Template Validator
UDEV="$(dirname "$0")"
source "$UDEV/../uCode/template-validation.sh"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <template-file>"
    exit 1
fi

validate_template_files "$(dirname "$1")"
