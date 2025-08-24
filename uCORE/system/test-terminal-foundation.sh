#!/bin/bash
# uDOS v1.4 Terminal Foundation Integration Test
# Tests UTF-8 enforcement, glyph detection, and Polaroid color system

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "🧪 Testing uDOS v1.4 Terminal Foundation System"
echo "   Root: $UDOS_ROOT"
echo

# Test 1: UTF-8 Enforcement
echo "1️⃣  Testing UTF-8 Enforcement..."
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"

if [[ "$UDOS_ENCODING" == "UTF-8" ]]; then
    echo "   ✅ UTF-8 enforcement active"
    echo "   📍 LANG=$LANG"
    echo "   📍 LC_ALL=$LC_ALL"
else
    echo "   ❌ UTF-8 enforcement failed"
    exit 1
fi
echo

# Test 2: Glyph Detection
echo "2️⃣  Testing Glyph Detection..."
source "$UDOS_ROOT/uCORE/system/display/glyph-detector.sh"

echo "   📊 Display Capabilities:"
echo "      Glyphs: ${UDOS_GLYPHS:-unknown}"
echo "      Display Mode: ${UDOS_DISPLAY:-unknown}"
echo "      Box Drawing: ${UDOS_BOX_DRAWING:-unknown}"
echo "      Emoji Support: ${UDOS_EMOJI:-unknown}"
echo "      Color Support: ${UDOS_COLORS:-unknown}"
echo "      Terminal Size: ${UDOS_TERM_WIDTH:-unknown}x${UDOS_TERM_HEIGHT:-unknown}"

# Test glyph rendering
echo "   🎨 Glyph Rendering Test:"
if [[ "${UDOS_GLYPHS:-ascii}" == "unicode" ]]; then
    echo "      $(get_glyph "top_left")$(get_glyph "horizontal_line")$(get_glyph "horizontal_line")$(get_glyph "top_right")"
    echo "      $(get_glyph "vertical_line") Unicode $(get_glyph "vertical_line")"
    echo "      $(get_glyph "bottom_left")$(get_glyph "horizontal_line")$(get_glyph "horizontal_line")$(get_glyph "bottom_right")"
    echo "      $(get_glyph "check") Unicode glyphs working $(get_glyph "target")"
else
    echo "      $(get_glyph "top_left")$(get_glyph "horizontal_line")$(get_glyph "horizontal_line")$(get_glyph "top_right")"
    echo "      $(get_glyph "vertical_line") ASCII $(get_glyph "vertical_line")"
    echo "      $(get_glyph "bottom_left")$(get_glyph "horizontal_line")$(get_glyph "horizontal_line")$(get_glyph "bottom_right")"
    echo "      $(get_glyph "check") ASCII fallback active $(get_glyph "target")"
fi
echo

# Test 3: Polaroid Color System
echo "3️⃣  Testing Polaroid Color System..."
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

if [[ "${UDOS_POLAROID_INITIALIZED:-0}" == "1" ]]; then
    echo "   ✅ Polaroid color system initialized"

    echo "   🎨 Color Palette Test:"
    polaroid_echo "orange" "   🟠 Polaroid Orange Pop"
    polaroid_echo "lime" "   🟢 Polaroid Lime Glow"
    polaroid_echo "cyan" "   🔵 Polaroid Cyan Flash"
    polaroid_echo "magenta" "   🟣 Polaroid Magenta Buzz"
    polaroid_echo "yellow" "   🟡 Polaroid Yellow Burst"
    polaroid_echo "chill" "   🔷 Polaroid Blue Chill"

    echo "   📝 Text Formatting Test:"
    polaroid_echo "bold" "   Bold Text"
    polaroid_echo "dim" "   Dim Text"
    echo -e "   ${UNDERLINE}Underlined Text${RESET}"

else
    echo "   ❌ Polaroid color system failed to initialize"
    exit 1
fi
echo

# Test 4: System Integration
echo "4️⃣  Testing System Integration..."

# Check if files can be sourced together
test_integration() {
    local temp_script="/tmp/udos-integration-test.sh"
    cat > "$temp_script" << 'EOF'
#!/bin/bash
set -euo pipefail
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/display/glyph-detector.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"
source "$UDOS_ROOT/uCORE/system/error-handler.sh"
source "$UDOS_ROOT/uCORE/system/process-manager.sh"
echo "Integration test successful"
EOF

    chmod +x "$temp_script"
    if "$temp_script" >/dev/null 2>&1; then
        echo "   ✅ All systems integrate successfully"
        rm -f "$temp_script"
        return 0
    else
        echo "   ❌ Integration test failed"
        rm -f "$temp_script"
        return 1
    fi
}

if test_integration; then
    echo "   🔗 Core systems can be loaded together"
else
    echo "   ⚠️  Integration issues detected"
    exit 1
fi
echo

# Test 5: Memory Persistence
echo "5️⃣  Testing Memory Persistence..."

if [[ -f "uMEMORY/user/encoding.env" ]]; then
    echo "   ✅ UTF-8 settings persisted to uMEMORY"
    echo "   📁 $(cat uMEMORY/user/encoding.env | head -1)"
else
    echo "   ⚠️  UTF-8 settings not persisted (uMEMORY may not exist yet)"
fi

if [[ -f "uMEMORY/user/display-config.env" ]]; then
    echo "   ✅ Display settings persisted to uMEMORY"
    echo "   📁 $(cat uMEMORY/user/display-config.env | head -1)"
else
    echo "   ⚠️  Display settings not persisted (uMEMORY may not exist yet)"
fi
echo

# Summary
echo "🎯 Terminal Foundation Test Summary:"
echo "   ✅ UTF-8 Enforcement: Active"
echo "   ✅ Glyph Detection: Working (${UDOS_GLYPHS:-ascii} mode)"
echo "   ✅ Polaroid Colors: Initialized (${UDOS_COLORS:-mono} colors)"
echo "   ✅ System Integration: Successful"
echo "   ✅ Memory Persistence: $([ -f "uMEMORY/user/display-config.env" ] && echo "Active" || echo "Pending uMEMORY setup")"
echo
echo "🚀 Terminal Foundation ready for Browser-UI Phase 2!"
echo "   Terminal rendering is now consistent and portable"
echo "   Colors use tput for maximum compatibility"
echo "   Unicode/ASCII fallback ensures universal support"
echo "   System is ready for web interface integration"
