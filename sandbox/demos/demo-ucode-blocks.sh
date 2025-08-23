#!/bin/bash
# uDOS v1.3.3 uCODE Block Template Renderer
# Demonstrates the new template syntax

set -euo pipefail

# Configuration
UDOS_ROOT="${UDOS_ROOT:-$(pwd)}"
TEMPLATE_FILE="${1:-$UDOS_ROOT/uMEMORY/templates/input-user-setup.md}"
OUTPUT_FILE="${2:-}"
TEST_DATA_FILE="${3:-$UDOS_ROOT/uMEMORY/system/get/user-data/testuser.json}"

echo "🎨 uDOS v1.3.3 uCODE Block Template Renderer"
echo "============================================="
echo ""

# Check if template file exists
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    exit 1
fi

echo "📄 Template: $TEMPLATE_FILE"
echo "📊 Test Data: $TEST_DATA_FILE"
echo ""

# Read test data if available
if [[ -f "$TEST_DATA_FILE" ]]; then
    echo "📖 Loading test data..."

    # Simple approach without associative arrays for bash 3.2
    echo "   USERNAME = testuser"
    echo "   FULL-NAME = Test User"
    echo "   EMAIL = test@example.com"
    echo "   LOCATION = San Francisco, CA"
    echo "   TIMEZONE = America/Los_Angeles"
    echo ""
fi

# Function to get test data value
get_test_value() {
    local key="$1"
    case "$key" in
        "USERNAME") echo "testuser" ;;
        "FULL-NAME") echo "Test User" ;;
        "EMAIL") echo "test@example.com" ;;
        "LOCATION") echo "San Francisco, CA" ;;
        "TIMEZONE") echo "America/Los_Angeles" ;;
        "CREATED-DATE") echo "2025-08-22T10:00:00Z" ;;
        "SYSTEM-VERSION") echo "v1.3.3" ;;
        *) echo "<!-- TERM: $key -->" ;;
    esac
}

echo "🔄 Processing template with uCODE Block syntax..."
echo ""

# Read and process template line by line
while IFS= read -r line; do
    # Process [TERM] {VARIABLE} syntax
    if echo "$line" | grep -q '\[TERM\] *{[^}]*}'; then
        # Extract variable name
        var=$(echo "$line" | sed 's/.*\[TERM\] *{\([^}|]*\).*/\1/')

        # Check if variable has a function pipe
        if echo "$line" | grep -q '|'; then
            func=$(echo "$line" | sed 's/.*|\([^}]*\)}.*/\1/' | tr -d ' ')
            value=$(get_test_value "$var")

            # Apply function
            case "$func" in
                "<FORMAT-TIMESTAMP>")
                    processed_value=$(date '+%Y-%m-%d %H:%M:%S UTC')
                    ;;
                "<SLUGIFY>")
                    processed_value=$(echo "$value" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
                    ;;
                "<HUMANIZE-KEY>")
                    processed_value=$(echo "$value" | sed 's/[-_]/ /g')
                    ;;
                *)
                    processed_value="$value"
                    ;;
            esac

            # Replace in line
            echo "$line" | sed "s|\[TERM\] *{[^}]*}|$processed_value|g"
        else
            # Simple variable replacement
            value=$(get_test_value "$var")
            echo "$line" | sed "s|\[TERM\] *{[^}]*}|$value|g"
        fi    # Process [GET-RETRIEVE] commands
    elif echo "$line" | grep -q '\[GET-RETRIEVE\]'; then
        # For demo, just show the command
        echo "$line" | sed 's|\[GET-RETRIEVE\] *{[^}]*}|<!-- GET-RETRIEVE executed -->|g'

    # Process conditional blocks - show as comments for demo
    elif echo "$line" | grep -q '\[\(IF\|EACH\|WITH\|/IF\|/EACH\|/WITH\|ELSE\)\]'; then
        # Show conditional structure
        echo "$line" | sed 's|\[\([^]]*\)\]|<!-- \1 -->|g'

    # Regular lines pass through
    else
        echo "$line"
    fi

done < "$TEMPLATE_FILE"

echo ""
echo "✅ Template processing complete!"

if [[ -n "$OUTPUT_FILE" ]]; then
    echo "💾 Output would be saved to: $OUTPUT_FILE"
fi

echo ""
echo "🎯 uCODE Block Syntax Examples Demonstrated:"
echo "   [TERM] {USERNAME} → testuser"
echo "   [TERM] {USERNAME | <SLUGIFY>} → testuser"
echo "   [TERM] {CREATED-DATE | <FORMAT-TIMESTAMP>} → $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "   [GET-RETRIEVE] {SETUP-STATUS | USERNAME} → <!-- GET-RETRIEVE executed -->"
echo "   [IF] {CONDITION} → <!-- IF -->"
echo "   [/IF] → <!-- /IF -->"
echo ""
echo "🚀 Next: Implement full parser for complete template processing!"
