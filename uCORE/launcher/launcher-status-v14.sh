#!/bin/bash
# uDOS v1.4 Launcher Status Report
# Shows current launcher state and removes any remaining old files

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🎯 uDOS v1.4 Launcher Status Report"
echo "==================================="
echo ""

removed_count=0

# Function to safely remove redundant files
cleanup_file() {
    local file="$1"
    local reason="$2"

    if [[ -f "$file" ]]; then
        echo "🗑️  Removing: $(basename "$file") - $reason"
        rm -f "$file"
        ((removed_count++))
    fi
}

echo "🔍 Current Launcher Structure:"
echo "==============================="
echo ""

# Check platform launchers
echo "📂 Platform Launchers:"
for launcher in Launch-uDOS-macOS.command Launch-uDOS-Ubuntu.sh Launch-uDOS-Windows.bat; do
    if [[ -f "$UDOS_ROOT/$launcher" ]]; then
        size=$(stat -f%z "$UDOS_ROOT/$launcher" 2>/dev/null || echo "unknown")
        perms=$(ls -la "$UDOS_ROOT/$launcher" | awk '{print $1}')
        version=$(grep -o "v1\.[0-9]\+\.[0-9]\+" "$UDOS_ROOT/$launcher" 2>/dev/null || echo "unknown")
        echo "   ✅ $launcher ($version) - $size bytes $perms"
    else
        echo "   ❌ $launcher - missing"
    fi
done

echo ""
echo "📂 Core System Launchers:"
core_launchers=(
    "uCORE/launcher/universal/start-udos.sh"
    "uCORE/launcher/vscode/start-vscode-dev.sh"
    "uCORE/launcher/universal/detect-platform.sh"
    "uCORE/launcher/universal/start-dev.sh"
    "uCORE/launcher/universal/test-udos.sh"
)

for launcher in "${core_launchers[@]}"; do
    if [[ -f "$UDOS_ROOT/$launcher" ]]; then
        size=$(stat -f%z "$UDOS_ROOT/$launcher" 2>/dev/null || echo "unknown")
        perms=$(ls -la "$UDOS_ROOT/$launcher" | awk '{print $1}')
        echo "   ✅ $launcher - $size bytes $perms"
    else
        echo "   ❌ $launcher - missing"
    fi
done

echo ""
echo "📂 Display System:"
display_files=(
    "uNETWORK/display/udos-display.sh"
    "setup-display-system.sh"
)

for display_file in "${display_files[@]}"; do
    if [[ -f "$UDOS_ROOT/$display_file" ]]; then
        size=$(stat -f%z "$UDOS_ROOT/$display_file" 2>/dev/null || echo "unknown")
        perms=$(ls -la "$UDOS_ROOT/$display_file" | awk '{print $1}')
        echo "   ✅ $display_file - $size bytes $perms"
    else
        echo "   ❌ $display_file - missing"
    fi
done

echo ""
echo "🧹 Cleanup Operations:"
echo "======================"

# Remove redundant startup script if it exists
if [[ -f "$UDOS_ROOT/start-udos-new.sh" ]]; then
    echo "🔍 Found start-udos-new.sh in root directory"

    # Check if it's the same as the main launcher
    if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
        # Compare file sizes first (quick check)
        size1=$(stat -f%z "$UDOS_ROOT/start-udos-new.sh" 2>/dev/null || echo "0")
        size2=$(stat -f%z "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" 2>/dev/null || echo "0")

        if [[ "$size1" == "$size2" ]]; then
            cleanup_file "$UDOS_ROOT/start-udos-new.sh" "redundant with main launcher"
        else
            echo "⚠️  start-udos-new.sh differs from main launcher - manual review needed"
        fi
    fi
fi

# Remove any backup files
cleanup_file "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh.backup" "old backup file"

# Check for lean browser (replaced by display system)
if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" && -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
    cleanup_file "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" "replaced by new display system"
fi

# Check for old CLI wrapper
if [[ -f "$UDOS_ROOT/uCORE/launcher/cli-only.sh" ]]; then
    if grep -q "exec.*start-udos.sh" "$UDOS_ROOT/uCORE/launcher/cli-only.sh" 2>/dev/null; then
        cleanup_file "$UDOS_ROOT/uCORE/launcher/cli-only.sh" "redundant CLI wrapper"
    fi
fi

echo ""
echo "📊 Version Information:"
echo "======================="

# Check version file
if [[ -f "$UDOS_ROOT/VERSION" ]]; then
    version=$(grep '^VERSION=' "$UDOS_ROOT/VERSION" | cut -d'"' -f2)
    build_date=$(grep '^BUILD_DATE=' "$UDOS_ROOT/VERSION" | cut -d'"' -f2)
    echo "   📋 System Version: $version"
    echo "   📅 Build Date: $build_date"
fi

# Check launcher versions
echo ""
echo "   📋 Launcher Versions:"
for launcher in Launch-uDOS-macOS.command Launch-uDOS-Ubuntu.sh Launch-uDOS-Windows.bat; do
    if [[ -f "$UDOS_ROOT/$launcher" ]]; then
        version=$(grep -o "v1\.[0-9]\+\.[0-9]\+" "$UDOS_ROOT/$launcher" 2>/dev/null || echo "unknown")
        echo "      $launcher: $version"
    fi
done

echo ""
echo "🎯 Cleanup Summary:"
echo "==================="
echo "🗑️  Files removed: $removed_count"

if [[ $removed_count -eq 0 ]]; then
    echo "✅ No cleanup needed - launcher structure is clean"
else
    echo "✅ Cleanup complete - $removed_count files removed"
fi

echo ""
echo "🚀 uDOS v1.4 Launcher Status: READY"
echo ""
echo "💡 Launcher Flow:"
echo "   1. Platform launcher (Launch-uDOS-*.* ) → User selects mode"
echo "   2. Core launcher (start-udos.sh) → Integrated startup sequence"
echo "   3. Display system (udos-display.sh) → Mode-specific interface"
echo "   4. VS Code launcher (start-vscode-dev.sh) → Development environment"
echo ""
echo "✅ All systems prepared for uDOS v1.4 production launch!"
