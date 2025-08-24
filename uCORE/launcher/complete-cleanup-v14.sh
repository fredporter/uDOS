#!/bin/bash
# uDOS v1.4 Complete Cleanup Script
# Remove redundant files and prepare clean structure for v1.4

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧹 uDOS v1.4 Complete Cleanup"
echo "=============================="
echo ""

# Track what we're removing
removed_count=0
moved_count=0

# Create deprecated directory if needed
DEPRECATED_DIR="$UDOS_ROOT/trash/deprecated/v14-cleanup"
mkdir -p "$DEPRECATED_DIR"

# Function to safely remove file
safe_remove() {
    local file="$1"
    local reason="$2"

    if [[ -f "$file" ]]; then
        echo "🗑️  Removing: $file - $reason"
        rm -f "$file"
        ((removed_count++))
    fi
}

# Function to move file to deprecated
move_to_deprecated() {
    local file="$1"
    local reason="$2"

    if [[ -f "$file" ]]; then
        echo "📦 Moving to deprecated: $file - $reason"
        mv "$file" "$DEPRECATED_DIR/$(basename "$file").$(date +%Y%m%d)"
        ((moved_count++))
    fi
}

echo "1️⃣  Removing redundant startup script..."
# Remove the redundant start-udos-new.sh in root
if [[ -f "$UDOS_ROOT/start-udos-new.sh" ]]; then
    echo "🔍 Comparing start-udos-new.sh with main launcher..."
    if diff -q "$UDOS_ROOT/start-udos-new.sh" "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" >/dev/null 2>&1; then
        safe_remove "$UDOS_ROOT/start-udos-new.sh" "identical to main launcher"
    else
        move_to_deprecated "$UDOS_ROOT/start-udos-new.sh" "different from main launcher - preserving"
    fi
fi

echo ""
echo "2️⃣  Removing backup files..."
# Remove backup files
safe_remove "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh.backup" "old backup"

# Remove other backup files in backup directory (they're already archived)
if [[ -d "$UDOS_ROOT/backup/system" ]]; then
    find "$UDOS_ROOT/backup/system" -name "*.backup" -type f | while read -r backup_file; do
        safe_remove "$backup_file" "archived backup file"
    done
fi

echo ""
echo "3️⃣  Checking for old launcher components..."

# Check for old lean browser if we have new display system
if [[ -f "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" && -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
    move_to_deprecated "$UDOS_ROOT/uCORE/launcher/universal/lean-browser.sh" "replaced by new display system"
fi

# Check for old CLI launcher if it's just a wrapper
if [[ -f "$UDOS_ROOT/uCORE/launcher/cli-only.sh" ]]; then
    if grep -q "start-udos.sh" "$UDOS_ROOT/uCORE/launcher/cli-only.sh" 2>/dev/null; then
        move_to_deprecated "$UDOS_ROOT/uCORE/launcher/cli-only.sh" "redundant wrapper - main launcher handles CLI"
    fi
fi

echo ""
echo "4️⃣  Checking platform launchers..."

# Verify all platform launchers are v1.4
for launcher in Launch-uDOS-macOS.command Launch-uDOS-Ubuntu.sh Launch-uDOS-Windows.bat; do
    if [[ -f "$UDOS_ROOT/$launcher" ]]; then
        if grep -q "v1\.4" "$UDOS_ROOT/$launcher"; then
            echo "✅ $launcher is v1.4"
        else
            echo "⚠️  $launcher may need v1.4 update"
        fi
    fi
done

echo ""
echo "5️⃣  Checking VS Code launcher..."

# Make sure VS Code launcher is current
if [[ -f "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh" ]]; then
    echo "✅ VS Code launcher present"

    # Check if it's executable
    if [[ ! -x "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh" ]]; then
        echo "🔧 Making VS Code launcher executable"
        chmod +x "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh"
    fi
fi

echo ""
echo "6️⃣  Cleaning up temporary files..."

# Remove any temporary files
find "$UDOS_ROOT" -name "*.tmp" -type f | while read -r tmp_file; do
    safe_remove "$tmp_file" "temporary file"
done

# Remove any ~ backup files
find "$UDOS_ROOT" -name "*~" -type f | while read -r tilde_file; do
    safe_remove "$tilde_file" "editor backup file"
done

echo ""
echo "7️⃣  Verifying launcher permissions..."

# Make sure all launchers are executable
for launcher in "$UDOS_ROOT"/Launch-uDOS-*.*; do
    if [[ -f "$launcher" && ! -x "$launcher" ]]; then
        echo "🔧 Making executable: $(basename "$launcher")"
        chmod +x "$launcher"
    fi
done

# Make sure core launchers are executable
for core_launcher in \
    "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" \
    "$UDOS_ROOT/uCORE/launcher/universal/detect-platform.sh" \
    "$UDOS_ROOT/uCORE/launcher/universal/start-dev.sh" \
    "$UDOS_ROOT/uCORE/launcher/universal/test-udos.sh"; do

    if [[ -f "$core_launcher" && ! -x "$core_launcher" ]]; then
        echo "🔧 Making executable: $(basename "$core_launcher")"
        chmod +x "$core_launcher"
    fi
done

echo ""
echo "📊 Cleanup Summary:"
echo "==================="
echo "🗑️  Files removed: $removed_count"
echo "📦 Files moved to deprecated: $moved_count"

if [[ -d "$DEPRECATED_DIR" ]]; then
    deprecated_files=$(find "$DEPRECATED_DIR" -type f | wc -l)
    if [[ $deprecated_files -gt 0 ]]; then
        echo "📁 Deprecated files location: $DEPRECATED_DIR"
    fi
fi

echo ""
echo "✅ uDOS v1.4 Launcher Structure Verified:"
echo "=========================================="
echo ""

echo "📂 Platform Launchers:"
for launcher in Launch-uDOS-macOS.command Launch-uDOS-Ubuntu.sh Launch-uDOS-Windows.bat; do
    if [[ -f "$UDOS_ROOT/$launcher" ]]; then
        perms=$(ls -la "$UDOS_ROOT/$launcher" | cut -d' ' -f1)
        version=$(grep -o "v1\.[0-9]" "$UDOS_ROOT/$launcher" 2>/dev/null || echo "unknown")
        echo "   ✅ $launcher ($version) $perms"
    fi
done

echo ""
echo "📂 Core Launchers:"
for core_launcher in \
    "uCORE/launcher/universal/start-udos.sh" \
    "uCORE/launcher/vscode/start-vscode-dev.sh" \
    "uCORE/launcher/universal/detect-platform.sh"; do

    if [[ -f "$UDOS_ROOT/$core_launcher" ]]; then
        perms=$(ls -la "$UDOS_ROOT/$core_launcher" | cut -d' ' -f1)
        echo "   ✅ $core_launcher $perms"
    fi
done

echo ""
echo "📂 Display System:"
if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
    perms=$(ls -la "$UDOS_ROOT/uNETWORK/display/udos-display.sh" | cut -d' ' -f1)
    echo "   ✅ uNETWORK/display/udos-display.sh $perms"
fi

echo ""
echo "🎯 Ready for uDOS v1.4 Production!"
echo ""
echo "💡 Next Steps:"
echo "   • Test all platform launchers"
echo "   • Verify display system integration"
echo "   • Run final system validation"
