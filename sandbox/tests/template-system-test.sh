#!/bin/bash
# uDOS v1.3.3 Template System Test
# Demonstrates the new template engine and data system

set -euo pipefail

# Configuration
UDOS_ROOT="/Users/agentdigital/uDOS"
TEST_USERNAME="testuser"
TEMPLATE_FILE="$UDOS_ROOT/uMEMORY/templates/input-user-setup.md"
OUTPUT_DIR="$UDOS_ROOT/sandbox/v1.3.3-test"

echo "🎯 uDOS v1.3.3 Template System Test"
echo "=================================="

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "1. Testing Template Engine..."
echo "   Template: $TEMPLATE_FILE"

# Test template validation
echo "2. Validating template syntax..."
if "$UDOS_ROOT/uCORE/core/template-engine-v1.3.3-compat.sh" validate "$TEMPLATE_FILE"; then
    echo "   ✅ Template validation passed"
else
    echo "   ❌ Template validation failed"
fi

echo ""
echo "3. Testing GET data retrieval..."

# Test GET operations
echo "   Testing user data retrieval:"
user_data=$("$UDOS_ROOT/uCORE/core/get-handler-v1.3.3.sh" "USER-DATA" "$TEST_USERNAME")
echo "   📄 User Data: $user_data"

echo ""
echo "   Testing setup status retrieval:"
setup_status=$("$UDOS_ROOT/uCORE/core/get-handler-v1.3.3.sh" "SETUP-STATUS" "$TEST_USERNAME")
echo "   📊 Setup Status: $setup_status"

echo ""
echo "   Testing system version:"
system_version=$("$UDOS_ROOT/uCORE/core/get-handler-v1.3.3.sh" "SYSTEM-VERSION")
echo "   🏷️  System Version: $system_version"

echo ""
echo "4. Testing POST data operations..."

# Test POST operations
test_preferences='{"THEME": "dark", "LANGUAGE": "en", "NOTIFICATIONS": true}'
echo "   Creating preference update..."
"$UDOS_ROOT/uCORE/core/post-handler-v1.3.3.sh" "PREFERENCE-UPDATE" "$TEST_USERNAME|$test_preferences"
echo "   ✅ Preferences updated"

echo ""
echo "5. Template Engine Version Info:"
"$UDOS_ROOT/uCORE/core/template-engine-v1.3.3-compat.sh" version

echo ""
echo "6. Directory Structure:"
echo "   GET data directory:"
ls -la "$UDOS_ROOT/uMEMORY/system/get/"
echo ""
echo "   POST data directory:"
ls -la "$UDOS_ROOT/uMEMORY/system/post/"

echo ""
echo "7. uCODE Syntax Examples:"
echo "   Commands: [GET-RETRIEVE] {USER-DATA | USERNAME}"
echo "   Functions: <FORMAT-TIMESTAMP>"
echo "   Variables: {{USERNAME | <SLUGIFY>}}"
echo "   VB-Style: {{#IF CONDITION}}...{{/IF}}"

echo ""
echo "🎉 uDOS v1.3.3 Template System Test Complete!"
echo ""
echo "📂 Test output saved to: $OUTPUT_DIR"
echo "📋 Template file location: $TEMPLATE_FILE"
echo "🔧 Core engines: $UDOS_ROOT/uCORE/core/"
echo ""
echo "Next Steps:"
echo "- Test template rendering with real data"
echo "- Implement component system"
echo "- Add caching layer"
echo "- Create additional templates"
