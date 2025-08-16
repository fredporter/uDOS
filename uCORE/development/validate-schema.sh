#!/bin/bash
# JSON Schema Validator for Development
if command -v ajv >/dev/null 2>&1; then
    ajv validate -s "$1" -d "$2"
else
    echo "⚠️ ajv-cli not installed. Install with: npm install -g ajv-cli"
    exit 1
fi
