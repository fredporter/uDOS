#!/bin/bash

# uCORE Directory Consolidation Analysis
# Version: 1.4.0
# Purpose: Analyze and plan consolidation of core, code, and system directories

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UCORE_DIR="$UDOS_ROOT/uCORE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 uCORE Directory Consolidation Analysis${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Analyze current structure
echo -e "${YELLOW}📁 Current uCORE Structure:${NC}"
ls -la "$UCORE_DIR" | sed 's/^/   /'
echo ""

# Analyze each target directory
echo -e "${YELLOW}🔍 Detailed Directory Analysis:${NC}"
echo ""

# CORE directory analysis
echo -e "${CYAN}📂 uCORE/core/ - Core Engine Components${NC}"
if [ -d "$UCORE_DIR/core" ]; then
    file_count=$(ls -1 "$UCORE_DIR/core" | wc -l)
    echo "   📊 Files: $file_count"
    echo "   🎯 Purpose: Core system engines and handlers"
    echo "   📋 Contents:"
    ls -1 "$UCORE_DIR/core" | sed 's/^/      • /'

    # Analyze file types
    engine_count=$(ls -1 "$UCORE_DIR/core"/*engine* 2>/dev/null | wc -l || echo 0)
    handler_count=$(ls -1 "$UCORE_DIR/core"/*handler* 2>/dev/null | wc -l || echo 0)
    manager_count=$(ls -1 "$UCORE_DIR/core"/*manager* 2>/dev/null | wc -l || echo 0)

    echo "   🔧 Engines: $engine_count files"
    echo "   ⚡ Handlers: $handler_count files"
    echo "   📋 Managers: $manager_count files"
else
    echo "   ❌ Directory not found"
fi
echo ""

# CODE directory analysis
echo -e "${CYAN}📂 uCORE/code/ - Command Interface Layer${NC}"
if [ -d "$UCORE_DIR/code" ]; then
    file_count=$(ls -1 "$UCORE_DIR/code" | grep -v "^d" | wc -l)
    dir_count=$(ls -1 "$UCORE_DIR/code" | grep "^d" | wc -l || echo 0)
    echo "   📊 Files: $file_count"
    echo "   📁 Subdirs: $dir_count"
    echo "   🎯 Purpose: User command interface and utilities"
    echo "   📋 Contents:"
    ls -1 "$UCORE_DIR/code" | sed 's/^/      • /'

    # Analyze main files
    if [ -f "$UCORE_DIR/code/ucode.sh" ]; then
        echo "   🌀 Main Entry: ucode.sh (command router)"
    fi

    # Check for command utilities
    util_count=$(ls -1 "$UCORE_DIR/code"/*.sh 2>/dev/null | wc -l || echo 0)
    echo "   🔧 Utilities: $util_count shell scripts"
else
    echo "   ❌ Directory not found"
fi
echo ""

# SYSTEM directory analysis
echo -e "${CYAN}📂 uCORE/system/ - System Infrastructure${NC}"
if [ -d "$UCORE_DIR/system" ]; then
    file_count=$(find "$UCORE_DIR/system" -type f | wc -l)
    dir_count=$(find "$UCORE_DIR/system" -type d | grep -v "^$UCORE_DIR/system$" | wc -l)
    echo "   📊 Files: $file_count"
    echo "   📁 Subdirs: $dir_count"
    echo "   🎯 Purpose: System-level infrastructure and configuration"
    echo "   📋 Contents:"
    ls -1 "$UCORE_DIR/system" | sed 's/^/      • /'

    # Analyze system components
    if [ -f "$UCORE_DIR/system/error-handler.sh" ]; then
        echo "   🚨 Error Handling: Comprehensive error management"
    fi
    if [ -d "$UCORE_DIR/system/display" ]; then
        echo "   🖥️  Display System: UI and rendering components"
    fi
else
    echo "   ❌ Directory not found"
fi
echo ""

# Functional overlap analysis
echo -e "${YELLOW}🔍 Functional Overlap Analysis:${NC}"
echo ""

# Check for duplicate functionality
echo -e "${CYAN}Potential Consolidation Opportunities:${NC}"
echo ""

echo "1. 🎯 Command Processing:"
echo "   • core/command-router.sh - Core command routing engine"
echo "   • code/ucode.sh - User command interface"
echo "   → Can be integrated into unified command system"
echo ""

echo "2. 🔧 Error Handling:"
echo "   • core/ - Various handler components"
echo "   • system/error-handler.sh - System error management"
echo "   → Could be consolidated into system/error/ subdirectory"
echo ""

echo "3. 📋 Management Functions:"
echo "   • core/*manager* - Core managers"
echo "   • code/ utilities - Command utilities"
echo "   • system/ infrastructure - System managers"
echo "   → Natural grouping by function rather than abstraction level"
echo ""

# Proposed consolidation plan
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📋 Consolidation Proposal${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${CYAN}Option 1: Functional Reorganization${NC}"
echo "└── uCORE/"
echo "    ├── commands/           # All command processing (from code + core routing)"
echo "    ├── engines/            # Core engines (from core)"
echo "    ├── handlers/           # All handlers (from core + system)"
echo "    ├── managers/           # All managers (from core)"
echo "    ├── infrastructure/     # System infrastructure (from system)"
echo "    └── [existing dirs]     # Keep bin, config, launcher, etc."
echo ""

echo -e "${CYAN}Option 2: Layer-Based Consolidation${NC}"
echo "└── uCORE/"
echo "    ├── runtime/            # All runtime components (core + code merged)"
echo "    ├── system/             # Enhanced system infrastructure"
echo "    └── [existing dirs]     # Keep bin, config, launcher, etc."
echo ""

echo -e "${CYAN}Option 3: Minimal Merge${NC}"
echo "└── uCORE/"
echo "    ├── core/               # Merge code/ into core/ (keep core as main)"
echo "    ├── system/             # Keep system separate"
echo "    └── [existing dirs]     # Keep bin, config, launcher, etc."
echo ""

# File impact analysis
echo -e "${YELLOW}📊 Impact Analysis:${NC}"
echo ""

core_files=$(find "$UCORE_DIR/core" -name "*.sh" 2>/dev/null | wc -l)
code_files=$(find "$UCORE_DIR/code" -name "*.sh" 2>/dev/null | wc -l)
system_files=$(find "$UCORE_DIR/system" -name "*.sh" 2>/dev/null | wc -l)

echo "📁 Files to relocate:"
echo "   • core/: $core_files shell scripts"
echo "   • code/: $code_files shell scripts"
echo "   • system/: $system_files shell scripts"
echo "   • Total: $((core_files + code_files + system_files)) files"
echo ""

echo "🔗 Dependencies to update:"
echo "   • Check source statements in scripts"
echo "   • Update import paths"
echo "   • Verify launcher scripts"
echo "   • Test command routing"
echo ""

echo -e "${GREEN}✅ Recommendation: Option 3 (Minimal Merge)${NC}"
echo ""
echo "Rationale:"
echo "• Least disruptive to existing functionality"
echo "• code/ naturally belongs with core/ (both handle commands)"
echo "• system/ has distinct infrastructure role"
echo "• Maintains clear separation of concerns"
echo "• Easiest to implement and validate"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "1. Create backup of current structure"
echo "2. Merge code/ into core/"
echo "3. Update all source/import statements"
echo "4. Test all command functionality"
echo "5. Update documentation"
echo ""
