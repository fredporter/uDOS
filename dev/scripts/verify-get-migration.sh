#!/bin/bash

# uDOS Datagets → Get Migration Verification
# Verify that all datagets references have been updated to get

echo "🔍 Verifying datagets → get migration..."
echo ""

# Check for remaining datagets references
echo "📋 Searching for remaining 'datagets' references:"
datagets_count=$(grep -r "datagets" /Users/agentdigital/uDOS --exclude-dir=.git --exclude-dir=trash --exclude="*.log" 2>/dev/null | wc -l)

if [[ $datagets_count -gt 0 ]]; then
    echo "⚠️  Found $datagets_count references to 'datagets' that may need updating:"
    grep -r "datagets" /Users/agentdigital/uDOS --exclude-dir=.git --exclude-dir=trash --exclude="*.log" 2>/dev/null | head -10
else
    echo "✅ No problematic 'datagets' references found"
fi

echo ""
echo "📁 Verifying directory structure changes:"

# Check if old datagets directories exist
if [[ -d "/Users/agentdigital/uDOS/sandbox/datagets" ]]; then
    echo "⚠️  Old sandbox/datagets directory still exists"
else
    echo "✅ sandbox/datagets → sandbox/get migration complete"
fi

if [[ -d "/Users/agentdigital/uDOS/uMEMORY/templates/datagets" ]]; then
    echo "⚠️  Old uMEMORY/templates/datagets directory still exists"
else
    echo "✅ uMEMORY/templates/datagets → uMEMORY/system/get migration complete"
fi

# Check if new get directories exist
if [[ -d "/Users/agentdigital/uDOS/sandbox/get" ]]; then
    echo "✅ New sandbox/get directory exists"
else
    echo "❌ New sandbox/get directory missing"
fi

if [[ -d "/Users/agentdigital/uDOS/uMEMORY/system/get" ]]; then
    echo "✅ New uMEMORY/system/get directory exists"
else
    echo "❌ New uMEMORY/system/get directory missing"
fi

if [[ -d "/Users/agentdigital/uDOS/uMEMORY/get" ]]; then
    echo "✅ New uMEMORY/get directory exists"
else
    echo "❌ New uMEMORY/get directory missing"
fi

if [[ -d "/Users/agentdigital/uDOS/sandbox/shared/get" ]]; then
    echo "✅ New sandbox/shared/get directory exists"
else
    echo "❌ New sandbox/shared/get directory missing"
fi

echo ""
echo "📊 Migration Summary:"
echo "- Terminology: datagets → get"
echo "- Directories: Moved and created"
echo "- Scripts: Updated references"
echo "- Structure: Ready for uMEMORY reorganization"
