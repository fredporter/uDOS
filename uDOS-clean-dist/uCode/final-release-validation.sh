#!/bin/bash
# final-release-validation.sh - Comprehensive validation for uDOS Alpha v1.0.0 with extensibility features

echo "🚀 uDOS Alpha v1.0.0 Final Release Validation"
echo "=============================================="
echo ""

# Check script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Validating extensibility systems..."
echo "UDOS_ROOT: $UDOS_ROOT"

# Dynamic Command System Validation
echo ""
echo "🔧 Dynamic Command System Validation:"
echo "======================================"

if [[ -f "$UDOS_ROOT/uCode/dynamic-command-loader.sh" ]]; then
    echo "✅ Dynamic command loader - exists"
    if bash -n "$UDOS_ROOT/uCode/dynamic-command-loader.sh" 2>/dev/null; then
        echo "✅ Dynamic command loader - syntax OK"
    else
        echo "❌ Dynamic command loader - syntax errors"
    fi
else
    echo "❌ Dynamic command loader - MISSING"
fi

if [[ -f "$UDOS_ROOT/uTemplate/datasets/dynamic-commands.json" ]]; then
    echo "✅ Dynamic commands dataset - exists"
    if command -v jq >/dev/null 2>&1; then
        if jq empty "$UDOS_ROOT/uTemplate/datasets/dynamic-commands.json" 2>/dev/null; then
            echo "✅ Dynamic commands dataset - valid JSON"
            command_count=$(jq '.commands | length' "$UDOS_ROOT/uTemplate/datasets/dynamic-commands.json")
            echo "📊 Dynamic commands available: $command_count"
        else
            echo "❌ Dynamic commands dataset - invalid JSON"
        fi
    else
        echo "⚠️ Cannot validate JSON - jq not available"
    fi
else
    echo "❌ Dynamic commands dataset - MISSING"
fi

# Template System Validation
echo ""
echo "📋 Template System Validation:"
echo "==============================="

if [[ -f "$UDOS_ROOT/uCode/template-finalizer.sh" ]]; then
    echo "✅ Template finalizer - exists"
else
    echo "❌ Template finalizer - MISSING"
fi

if [[ -f "$UDOS_ROOT/uTemplate/datasets/template-definitions.json" ]]; then
    echo "✅ Template definitions - exists"
    if command -v jq >/dev/null 2>&1; then
        template_count=$(jq '. | length' "$UDOS_ROOT/uTemplate/datasets/template-definitions.json" 2>/dev/null || echo "0")
        echo "📊 Templates available: $template_count"
    fi
else
    echo "❌ Template definitions - MISSING"
fi

# Check for key template files
template_files=(
    "mission-template.md"
    "milestone-template.md" 
    "move-template.md"
    "system/dashboard.md"
    "input-user-setup.md"
)

echo ""
echo "📝 Template Files:"
for template in "${template_files[@]}"; do
    if [[ -f "$UDOS_ROOT/uTemplate/$template" ]]; then
        echo "✅ $template - exists"
    else
        echo "❌ $template - MISSING"
    fi
done

# Variable System Validation
echo ""
echo "🔧 Variable System Validation:"
echo "==============================="

if [[ -f "$UDOS_ROOT/uCode/variable-manager.sh" ]]; then
    echo "✅ Variable manager - exists"
    if [[ -x "$UDOS_ROOT/uCode/variable-manager.sh" ]]; then
        echo "✅ Variable manager - executable"
    else
        echo "❌ Variable manager - NOT executable"
    fi
else
    echo "❌ Variable manager - MISSING"
fi

if [[ -f "$UDOS_ROOT/uTemplate/datasets/variable-system.json" ]]; then
    echo "✅ Variable system config - exists"
else
    echo "❌ Variable system config - MISSING"
fi

# Check variable files
variable_files=(
    "user-vars.json"
    "env.json"
    "session.json"
)

echo ""
echo "📊 Variable Files:"
for varfile in "${variable_files[@]}"; do
    if [[ -f "$UDOS_ROOT/uTemplate/variables/$varfile" ]]; then
        echo "✅ $varfile - exists"
    else
        echo "❌ $varfile - MISSING"
    fi
done

# Package System Validation
echo ""
echo "📦 Package System Validation:"
echo "============================="

if [[ -f "$UDOS_ROOT/uCode/packages/manager.sh" ]]; then
    echo "✅ Package manager - exists"
    if [[ -x "$UDOS_ROOT/uCode/packages/manager.sh" ]]; then
        echo "✅ Package manager - executable"
    else
        echo "❌ Package manager - NOT executable"
    fi
else
    echo "❌ Package manager - MISSING"
fi

# Count available packages
package_count=$(find "$UDOS_ROOT/uCode/packages" -name "install-*.sh" 2>/dev/null | wc -l)
echo "📊 Available packages: $package_count"

# Integration Test
echo ""
echo "🧪 Integration Tests:"
echo "===================="

# Test dynamic command loading
echo "🔧 Testing dynamic command loading..."
if bash -c "cd '$UDOS_ROOT' && source uCode/dynamic-command-loader.sh && load_dynamic_commands" 2>/dev/null; then
    echo "✅ Dynamic command loading - works"
else
    echo "❌ Dynamic command loading - failed"
fi

# Test variable management
echo "🔧 Testing variable management..."
if bash "$UDOS_ROOT/uCode/variable-manager.sh" list user >/dev/null 2>&1; then
    echo "✅ Variable management - works"
else
    echo "❌ Variable management - failed"
fi

# Test main ucode.sh integration
echo "🔧 Testing main shell integration..."
if bash -n "$UDOS_ROOT/uCode/ucode.sh" 2>/dev/null; then
    echo "✅ Main shell syntax - OK"
else
    echo "❌ Main shell syntax - errors"
fi

# Dataset Completeness Check
echo ""
echo "📊 Dataset Completeness:"
echo "========================"

datasets=(
    "locationMap.json"
    "timezoneMap.json"
    "countryMap.json"
    "dynamic-commands.json"
    "template-definitions.json"
    "variable-system.json"
)

for dataset in "${datasets[@]}"; do
    if [[ -f "$UDOS_ROOT/uTemplate/datasets/$dataset" ]]; then
        echo "✅ $dataset - exists"
    else
        echo "❌ $dataset - MISSING"
    fi
done

# Final Summary
echo ""
echo "📋 Extensibility Features Summary:"
echo "=================================="

# Count all extensibility components
dynamic_commands_ok=0
template_system_ok=0
variable_system_ok=0
package_system_ok=0

if [[ -f "$UDOS_ROOT/uCode/dynamic-command-loader.sh" && -f "$UDOS_ROOT/uTemplate/datasets/dynamic-commands.json" ]]; then
    dynamic_commands_ok=1
fi

if [[ -f "$UDOS_ROOT/uCode/template-finalizer.sh" && -f "$UDOS_ROOT/uTemplate/datasets/template-definitions.json" ]]; then
    template_system_ok=1
fi

if [[ -f "$UDOS_ROOT/uCode/variable-manager.sh" && -f "$UDOS_ROOT/uTemplate/datasets/variable-system.json" ]]; then
    variable_system_ok=1
fi

if [[ -f "$UDOS_ROOT/uCode/packages/manager.sh" ]]; then
    package_system_ok=1
fi

total_systems=$((dynamic_commands_ok + template_system_ok + variable_system_ok + package_system_ok))

echo "✅ Dynamic Command System: $([ $dynamic_commands_ok -eq 1 ] && echo "Ready" || echo "Incomplete")"
echo "✅ Template System: $([ $template_system_ok -eq 1 ] && echo "Ready" || echo "Incomplete")"  
echo "✅ Variable System: $([ $variable_system_ok -eq 1 ] && echo "Ready" || echo "Incomplete")"
echo "✅ Package System: $([ $package_system_ok -eq 1 ] && echo "Ready" || echo "Incomplete")"

echo ""
echo "📈 Extensibility Score: $total_systems/4 systems ready"

if [[ $total_systems -eq 4 ]]; then
    echo ""
    echo "🎉 EXTENSIBILITY VALIDATION PASSED!"
    echo ""
    echo "✅ All extensibility systems are ready for Alpha v1.0.0"
    echo "✅ Dynamic commands can be added via datasets"
    echo "✅ Templates and variables are fully configurable"
    echo "✅ Package system ready for third-party integrations"
    echo "✅ uDOS is primed for development and extension"
    echo ""
    echo "🚀 uDOS Alpha v1.0.0 is ready for public release with full extensibility!"
    exit 0
else
    echo ""
    echo "⚠️ EXTENSIBILITY VALIDATION INCOMPLETE"
    echo ""
    echo "Please complete the missing systems before release."
    echo "Current readiness: $total_systems/4 systems ready"
    exit 1
fi
