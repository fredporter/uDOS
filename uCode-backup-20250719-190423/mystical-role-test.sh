#!/bin/bash

# Role System Test - Wizard, Sorcerer, Imp, Ghost
# Tests the new 4-tier role system with package/extension access

echo "🧙‍♂️ uDOS Mystical Role System Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 Available Roles:"
echo "────────────────────────────────────────────────"
./user-role-manager.sh roles
echo ""

echo "👤 Current User Status:"
echo "────────────────────────────────────────────────"
./user-role-manager.sh status | head -10
echo ""

echo "🔧 Testing Dev Mode Package/Extension Access:"
echo "────────────────────────────────────────────────"
echo "Enabling dev mode..."
./user-role-manager.sh dev-mode on
echo ""
echo "Checking package and extension folder access:"
./enhanced-list-command.sh all | grep -A 3 "📚 Documentation & Extensions:"
echo ""

echo "Testing folder access permissions:"
./user-role-manager.sh check package write && echo "✅ Package folder: Write access granted" || echo "❌ Package folder: Write access denied"
./user-role-manager.sh check extension write && echo "✅ Extension folder: Write access granted" || echo "❌ Extension folder: Write access denied"
echo ""

echo "🔒 Testing Security (Disabling Dev Mode):"
echo "────────────────────────────────────────────────"
./user-role-manager.sh dev-mode off
echo ""
echo "Checking restricted access:"
./enhanced-list-command.sh all | grep -A 3 "📚 Documentation & Extensions:"
echo ""

echo "🎭 Role Hierarchy Summary:"
echo "────────────────────────────────────────────────"
echo "🧙‍♂️ Wizard   (Level 100) - Full system access + package/extension in dev mode"
echo "🔮 Sorcerer (Level 75)  - Elevated powers, limited system access"
echo "👹 Imp      (Level 50)  - Script/template creation powers"
echo "🤖 Drone    (Level 25)  - Automated structured access to basic operations"
echo "👻 Ghost    (Level 10)  - Ethereal demo access only"
echo ""

echo "✨ Mystical Role System Test Complete!"
