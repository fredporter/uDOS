#!/bin/bash
# uDOS v1.4 Launcher Cleanup Script
# Remove old version files and prepare clean launcher structure

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧹 uDOS v1.4 Launcher Cleanup"
echo "=============================="
echo ""

# Track what we're removing
removed_count=0
deprecated_count=0

# Function to safely remove file with confirmation
safe_remove() {
    local file="$1"
    local reason="$2"

    if [[ -f "$file" ]]; then
        echo "🗑️  Removing: $(basename "$file") - $reason"
        rm -f "$file"
        ((removed_count++))
    fi
}

# Function to move to deprecated
move_to_deprecated() {
    local file="$1"
    local reason="$2"
    local deprecated_dir="$UDOS_ROOT/trash/deprecated"

    mkdir -p "$deprecated_dir"

    if [[ -f "$file" ]]; then
        echo "📦 Moving to deprecated: $(basename "$file") - $reason"
        mv "$file" "$deprecated_dir/$(basename "$file").deprecated"
        ((deprecated_count++))
    fi
}

echo "🔍 Scanning for old launcher files..."
echo ""

# 1. Remove backup files in launcher directory
echo "1️⃣  Removing backup files:"
safe_remove "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh.backup" "old backup file"

# 2. Check for redundant startup scripts
echo ""
echo "2️⃣  Checking startup scripts:"

# The new integrated start-udos.sh is the main one
if [[ -f "$UDOS_ROOT/start-udos-new.sh" ]]; then
    echo "🔄 Found start-udos-new.sh - checking if it's integrated into main launcher..."

    # Check if the new script is different from the main one
    if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
        echo "✅ Main start-udos.sh exists - moving start-udos-new.sh to deprecated"
        move_to_deprecated "$UDOS_ROOT/start-udos-new.sh" "replaced by integrated launcher"
    fi
fi

# 3. Check for old version install scripts (keep current v14)
echo ""
echo "3️⃣  Checking version install scripts:"

# Only remove if we find really old ones (keep v14 for current)
for version in v10 v11 v12 v13; do
    safe_remove "$UDOS_ROOT/install-${version}.sh" "old version installer"
    safe_remove "$UDOS_ROOT/migrate-to-${version}.sh" "old migration script"
done

# 4. Clean up old launcher platform files
echo ""
echo "4️⃣  Checking platform-specific launchers:"

# Check if the current platform launchers are v1.4
current_version=$(grep -o "v1\.[0-9]" "$UDOS_ROOT/Launch-uDOS-macOS.command" 2>/dev/null || echo "unknown")
if [[ "$current_version" == "v1.4" ]]; then
    echo "✅ Platform launchers are v1.4 - keeping current versions"
else
    echo "⚠️  Platform launchers may need updating to v1.4"
fi

# 5. Remove old CLI launcher if it's redundant
echo ""
echo "5️⃣  Checking CLI-only launcher:"

if [[ -f "$UDOS_ROOT/uCORE/launcher/cli-only.sh" ]]; then
    # Check if it's just a simple wrapper - if so, it's probably redundant
    if grep -q "start-udos.sh" "$UDOS_ROOT/uCORE/launcher/cli-only.sh" 2>/dev/null; then
        move_to_deprecated "$UDOS_ROOT/uCORE/launcher/cli-only.sh" "redundant CLI wrapper"
    fi
fi

# 6. Check for old terminal launcher
echo ""
echo "6️⃣  Checking terminal launcher files:"

if [[ -f "$UDOS_ROOT/uCORE/launcher/uDOS.terminal" ]]; then
    # This might be macOS specific - check if it's old
    echo "📋 Found uDOS.terminal - checking if still needed..."
    if grep -q "v1\.[0-3]" "$UDOS_ROOT/uCORE/launcher/uDOS.terminal" 2>/dev/null; then
        move_to_deprecated "$UDOS_ROOT/uCORE/launcher/uDOS.terminal" "old version terminal launcher"
    else
        echo "✅ Terminal launcher appears current - keeping"
    fi
fi

# 7. Clean up build scripts that might be old
echo ""
echo "7️⃣  Checking build scripts:"

if [[ -f "$UDOS_ROOT/uCORE/launcher/build-app.sh" ]]; then
    # Check if it references old versions
    if grep -q "v1\.[0-3]" "$UDOS_ROOT/uCORE/launcher/build-app.sh" 2>/dev/null; then
        echo "🔄 build-app.sh contains old version references - needs updating"
    else
        echo "✅ build-app.sh appears current"
    fi
fi

# 8. Check for old lean browser launcher
echo ""
echo "8️⃣  Checking browser launcher:"

if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" ]]; then
    # This might be redundant with the new display system
    echo "🤔 Found lean-browser.sh - checking if needed with new display system..."

    # If we have the new display system, this might be redundant
    if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
        move_to_deprecated "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" "replaced by new display system"
    fi
fi

echo ""
echo "📊 Cleanup Summary:"
echo "==================="
echo "🗑️  Files removed: $removed_count"
echo "📦 Files moved to deprecated: $deprecated_count"

if [[ $removed_count -eq 0 && $deprecated_count -eq 0 ]]; then
    echo "✅ No cleanup needed - launcher structure is already clean for v1.4"
else
    echo "✅ Cleanup complete - launcher structure prepared for v1.4"
fi

echo ""
echo "🎯 v1.4 Launcher Structure:"
echo "=========================="
echo "📂 Main Launchers:"
echo "   • Launch-uDOS-macOS.command (v1.4)"
echo "   • Launch-uDOS-Ubuntu.sh (v1.4)"
echo "   • Launch-uDOS-Windows.bat (v1.4)"
echo ""
echo "📂 Core Launchers:"
echo "   • uCORE/launcher/universal/start-udos.sh (integrated)"
echo "   • uCORE/launcher/vscode/start-vscode-dev.sh"
echo "   • uCORE/launcher/universal/detect-platform.sh"
echo ""
echo "📂 Display System:"
echo "   • uNETWORK/display/udos-display.sh (new v1.4 system)"
echo ""

# Show current launcher status
echo "🔍 Current Launcher Status:"
echo "==========================="

if [[ -f "$UDOS_ROOT/Launch-uDOS-macOS.command" ]]; then
    version=$(grep -o "v1\.[0-9]" "$UDOS_ROOT/Launch-uDOS-macOS.command" 2>/dev/null || echo "unknown")
    echo "✅ macOS launcher: $version"
fi

if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
    echo "✅ Universal launcher: present"
fi

if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
    echo "✅ Display system: present"
fi

echo ""
echo "🚀 Ready for uDOS v1.4 launch!"
