#!/bin/bash
# Alpha v1.0.0 Release Validation Script
# Quick validation test for uDOS alpha release readiness

echo "🚀 uDOS Alpha v1.0.0 Release Validation"
echo "========================================"
echo ""

# Check script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Checking file structure..."
echo "UDOS_ROOT: $UDOS_ROOT"

# Essential directories
REQUIRED_DIRS=(
    "uCode"
    "uMemory" 
    "uKnowledge"
    "uScript"
    "uTemplate"
    "launcher"
    "roadmap"
)

missing_dirs=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$UDOS_ROOT/$dir" ]]; then
        echo "✅ $dir/ - exists"
    else
        echo "❌ $dir/ - MISSING"
        ((missing_dirs++))
    fi
done

echo ""
echo "🔧 Checking essential scripts..."

# Essential scripts
ESSENTIAL_SCRIPTS=(
    "uCode/ucode.sh"
    "uCode/check.sh" 
    "uCode/log.sh"
    "uCode/dash.sh"
    "uCode/template-generator.sh"
    "uCode/json-processor.sh"
    "start-udos.sh"
)

missing_scripts=0
for script in "${ESSENTIAL_SCRIPTS[@]}"; do
    if [[ -f "$UDOS_ROOT/$script" ]]; then
        echo "✅ $script - exists"
        if [[ -x "$UDOS_ROOT/$script" ]]; then
            echo "   └── executable ✅"
        else
            echo "   └── NOT executable ❌"
            ((missing_scripts++))
        fi
    else
        echo "❌ $script - MISSING"
        ((missing_scripts++))
    fi
done

echo ""
echo "📚 Checking documentation..."

# Essential documentation
ESSENTIAL_DOCS=(
    "README.md"
    "CHANGELOG.md" 
    "ALPHA_RELEASE_PREP.md"
    "docs/roadmap/ROADMAP_STATUS.md"
    "docs/roadmap/001-uDOS-foundation.md"
)

missing_docs=0
for doc in "${ESSENTIAL_DOCS[@]}"; do
    if [[ -f "$UDOS_ROOT/$doc" ]]; then
        echo "✅ $doc - exists"
    else
        echo "❌ $doc - MISSING"
        ((missing_docs++))
    fi
done

echo ""
echo "🧪 Testing shell script syntax..."

syntax_errors=0
for script in "$UDOS_ROOT"/uCode/*.sh; do
    if [[ -f "$script" ]]; then
        script_name=$(basename "$script")
        if bash -n "$script" 2>/dev/null; then
            echo "✅ $script_name - syntax OK"
        else
            echo "❌ $script_name - SYNTAX ERROR"
            ((syntax_errors++))
        fi
    fi
done

echo ""
echo "📊 Validation Summary"
echo "===================="
echo "Missing directories: $missing_dirs"
echo "Missing/broken scripts: $missing_scripts" 
echo "Missing docs: $missing_docs"
echo "Syntax errors: $syntax_errors"
echo ""

total_issues=$((missing_dirs + missing_scripts + missing_docs + syntax_errors))

if [[ $total_issues -eq 0 ]]; then
    echo "🎉 VALIDATION PASSED - READY FOR ALPHA RELEASE!"
    echo ""
    echo "✅ All essential components present"
    echo "✅ All scripts executable and syntactically correct"
    echo "✅ All documentation in place"
    echo "✅ File structure complete"
    echo ""
    echo "🚀 uDOS Alpha v1.0.0 is ready for public release!"
    exit 0
else
    echo "⚠️  VALIDATION ISSUES FOUND ($total_issues total)"
    echo ""
    echo "Please resolve the issues above before releasing alpha v1.0.0"
    exit 1
fi
