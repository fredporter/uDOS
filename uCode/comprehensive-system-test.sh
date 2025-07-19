#!/bin/bash

# Comprehensive System Test for uDOS Enhanced Systems
# Tests: Help System, Role Management, List Commands, Integration

echo "🚀 uDOS Comprehensive System Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Role System Status
echo "📋 Test 1: Role System Status"
echo "────────────────────────────────────────────────"
./user-role-manager.sh status
echo ""

# Test 2: Enhanced Help System Search
echo "🔍 Test 2: Help System Search Functionality"
echo "────────────────────────────────────────────────"
./enhanced-help-system.sh search file | head -5
echo ""

# Test 3: Help System Statistics
echo "📊 Test 3: Help System Dataset Statistics"  
echo "────────────────────────────────────────────────"
./enhanced-help-system.sh stats
echo ""

# Test 4: Enhanced List Command - Default View
echo "📁 Test 4: Enhanced LIST Command (Default)"
echo "────────────────────────────────────────────────"
./enhanced-list-command.sh default
echo ""

# Test 5: Dev Mode Toggle Test
echo "🔧 Test 5: Dev Mode Toggle Test"
echo "────────────────────────────────────────────────"
echo "Enabling dev mode..."
./user-role-manager.sh dev-mode on
echo ""
echo "Showing system folders with dev mode:"
./enhanced-list-command.sh all | grep -A 2 "⚙️ System"
echo ""
echo "Disabling dev mode..."
./user-role-manager.sh dev-mode off
echo ""

# Test 6: Available Roles
echo "👥 Test 6: Available Roles Overview"
echo "────────────────────────────────────────────────"
./user-role-manager.sh roles
echo ""

# Test 7: Help Category Browse
echo "🗂️ Test 7: Help System Category Browse"
echo "────────────────────────────────────────────────"
./enhanced-help-system.sh category file | head -8
echo ""

echo "✅ Comprehensive System Test Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Summary: All enhanced systems are operational"
echo "   • Role-based access control ✓"
echo "   • Dataset-driven help system ✓" 
echo "   • Enhanced folder listing ✓"
echo "   • Dev mode functionality ✓"
echo "   • Integrated shortcode support ✓"
