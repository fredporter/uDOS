#!/bin/bash
# Test all three platform launchers for syntax and functionality

set -euo pipefail

echo "🧪 Testing All Platform Launchers"
echo "================================="

# Test Ubuntu launcher
echo ""
echo "1. 🐧 Testing Ubuntu Launcher..."
if bash -n Launch-uDOS-Ubuntu.sh; then
    echo "   ✅ Ubuntu launcher syntax valid"
else
    echo "   ❌ Ubuntu launcher has syntax errors"
fi

# Test macOS launcher  
echo ""
echo "2. 🍎 Testing macOS Launcher..."
if bash -n Launch-uDOS-macOS.command; then
    echo "   ✅ macOS launcher syntax valid"
else
    echo "   ❌ macOS launcher has syntax errors"
fi

# Test Windows launcher (basic syntax check)
echo ""
echo "3. 🪟 Testing Windows Launcher..."
if command -v cmd >/dev/null 2>&1; then
    echo "   ⚠️  Cannot fully test .bat file on Linux - checking basic structure"
else
    echo "   ⚠️  Windows CMD not available - checking file exists and is executable"
fi

if [[ -f "Launch-uDOS-Windows.bat" && -x "Launch-uDOS-Windows.bat" ]]; then
    echo "   ✅ Windows launcher exists and is executable"
    # Check for basic Windows batch syntax
    if grep -q "@echo off" Launch-uDOS-Windows.bat && grep -q "set.*UDOS_ROOT" Launch-uDOS-Windows.bat; then
        echo "   ✅ Windows launcher has valid batch structure"
    else
        echo "   ❌ Windows launcher missing key batch commands"
    fi
else
    echo "   ❌ Windows launcher missing or not executable"
fi

echo ""
echo "🎯 Platform Launcher Test Complete"
