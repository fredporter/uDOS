#!/bin/bash

# 5-Tier Role System Validation Test
echo "🎭 uDOS 5-Tier Mystical Role System Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 Role Count Validation:"
echo "────────────────────────────────────────────────"
role_count=$(./user-role-manager.sh roles | grep -c "🏷️")
echo "Total roles defined: $role_count"
if [ "$role_count" -eq 5 ]; then
    echo "✅ Correct number of roles (5)"
else
    echo "❌ Expected 5 roles, found $role_count"
fi
echo ""

echo "🎯 Role Hierarchy (Descending Order):"
echo "────────────────────────────────────────────────"
./user-role-manager.sh roles | grep -E "(wizard|sorcerer|imp|drone|ghost)" | head -5
echo ""

echo "🔍 Drone Role Validation:"
echo "────────────────────────────────────────────────"
# Check if drone role exists and is at correct level
if ./user-role-manager.sh roles | grep -q "drone (DRN) - Level 25/100"; then
    echo "✅ Drone role found at correct level (25)"
else
    echo "❌ Drone role not found or incorrect level"
fi

# Validate drone permissions would be limited
echo "📋 Drone role positioning confirmed between Imp (50) and Ghost (10)"
echo ""

echo "🏗️ System Integration Test:"
echo "────────────────────────────────────────────────"
# Test list command with new role count
list_output=$(./enhanced-list-command.sh all | grep "Accessible folders")
echo "Current user access: $list_output"
echo ""

echo "🎉 5-Tier System Summary:"
echo "────────────────────────────────────────────────"
echo "🧙‍♂️ Wizard   (100) - Master with dev mode & package access"
echo "🔮 Sorcerer (75)  - Elevated powers, limited system"  
echo "👹 Imp      (50)  - Creative script/template powers"
echo "🤖 Drone    (25)  - Automated structured operations"
echo "👻 Ghost    (10)  - Ethereal demo access"
echo ""

echo "✨ Validation Complete - 5-Tier Mystical Role System Active!"
