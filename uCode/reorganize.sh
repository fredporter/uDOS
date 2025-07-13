#!/bin/bash
# uDOS Reorganization Script v1.7.1
# Migrates existing content to new architectural structure

UHOME="${HOME}/uDOS"

echo "🏗️ uDOS Repository Reorganization v1.7.1"
echo "========================================"
echo ""
echo "New Architecture:"
echo "📚 uKnowledge = Central shared knowledge bank (system docs, doesn't change with user)"
echo "🧠 uMemory = All user content storage (missions, moves, logs, user scripts)"
echo "⚙️ uCode = Complete command centre (shell, utilities, system management)"
echo "🔧 uScript = System scripts and bash execution environment"
echo "📋 uTemplate = System templates, datasets, variables"
echo ""

# Create new directory structure
echo "Creating new directory structure..."

# uMemory = All user content storage
mkdir -p "$UHOME/uMemory/user"
mkdir -p "$UHOME/uMemory/scripts"
mkdir -p "$UHOME/uMemory/templates"
mkdir -p "$UHOME/uMemory/sandbox"

# uKnowledge = Central shared knowledge bank
mkdir -p "$UHOME/uKnowledge/roadmap"

# uScript = System scripts and bash execution
mkdir -p "$UHOME/uScript/system"
mkdir -p "$UHOME/uScript/utilities"
mkdir -p "$UHOME/uScript/automation"

# uTemplate = System templates and datasets
mkdir -p "$UHOME/uTemplate/system"
mkdir -p "$UHOME/uTemplate/datasets"
mkdir -p "$UHOME/uTemplate/variables"

echo "✅ Directory structure created"

# Migration Operations
echo ""
echo "🔄 Migrating content..."

# 1. Move roadmap to uKnowledge (shared system docs)
if [[ -d "$UHOME/roadmap" ]]; then
    echo "📚 Moving roadmap to uKnowledge..."
    mv "$UHOME/roadmap"/* "$UHOME/uKnowledge/roadmap/" 2>/dev/null
    rmdir "$UHOME/roadmap" 2>/dev/null
    echo "✅ Roadmap migrated to uKnowledge/roadmap/"
fi

# 2. Move sandbox to uMemory (user content)
if [[ -d "$UHOME/sandbox" ]]; then
    echo "🧠 Moving sandbox to uMemory..."
    mv "$UHOME/sandbox"/* "$UHOME/uMemory/sandbox/" 2>/dev/null
    rmdir "$UHOME/sandbox" 2>/dev/null
    echo "✅ Sandbox migrated to uMemory/sandbox/"
fi

# 3. Move user scripts from uScript to uMemory
if [[ -d "$UHOME/uScript" ]]; then
    echo "🔧 Reorganizing uScript..."
    
    # Move user-created scripts to uMemory
    if [[ -f "$UHOME/uScript/hello.md" ]]; then
        mv "$UHOME/uScript/hello.md" "$UHOME/uMemory/scripts/" 2>/dev/null
        echo "  📝 Moved hello.md to uMemory/scripts/"
    fi
    
    if [[ -f "$UHOME/uScript/uCode-BASIC.md" ]]; then
        mv "$UHOME/uScript/uCode-BASIC.md" "$UHOME/uMemory/scripts/" 2>/dev/null
        echo "  📝 Moved uCode-BASIC.md to uMemory/scripts/"
    fi
    
    # Move system utilities to proper uScript structure
    if [[ -f "$UHOME/uScript/cleanup.sh" ]]; then
        mv "$UHOME/uScript/cleanup.sh" "$UHOME/uScript/system/" 2>/dev/null
        echo "  🔧 Moved cleanup.sh to uScript/system/"
    fi
    
    if [[ -f "$UHOME/uScript/ucode-interpreter.py" ]]; then
        mv "$UHOME/uScript/ucode-interpreter.py" "$UHOME/uScript/system/" 2>/dev/null
        echo "  🐍 Moved ucode-interpreter.py to uScript/system/"
    fi
    
    if [[ -f "$UHOME/uScript/ucode-runner.sh" ]]; then
        mv "$UHOME/uScript/ucode-runner.sh" "$UHOME/uScript/system/" 2>/dev/null
        echo "  🔧 Moved ucode-runner.sh to uScript/system/"
    fi
    
    # Move datasets to uTemplate
    if [[ -d "$UHOME/uScript/datasets" ]]; then
        mv "$UHOME/uScript/datasets"/* "$UHOME/uTemplate/datasets/" 2>/dev/null
        rmdir "$UHOME/uScript/datasets" 2>/dev/null
        echo "  📊 Moved datasets to uTemplate/datasets/"
    fi
    
    # Move vars to uTemplate
    if [[ -d "$UHOME/uScript/vars" ]]; then
        mv "$UHOME/uScript/vars"/* "$UHOME/uTemplate/variables/" 2>/dev/null
        rmdir "$UHOME/uScript/vars" 2>/dev/null
        echo "  🔢 Moved variables to uTemplate/variables/"
    fi
    
    echo "✅ uScript reorganized"
fi

# 4. Move templates from uTemplate to proper structure
if [[ -d "$UHOME/uTemplate" ]]; then
    echo "📋 Reorganizing uTemplate..."
    
    # System templates
    for template in dash-template.md dashboard.md dataset-*.md; do
        if [[ -f "$UHOME/uTemplate/$template" ]]; then
            mv "$UHOME/uTemplate/$template" "$UHOME/uTemplate/system/" 2>/dev/null
            echo "  📄 Moved $template to uTemplate/system/"
        fi
    done
    
    # TypeScript project files stay in root uTemplate
    echo "  ⚙️ TypeScript project files remain in uTemplate root"
    echo "✅ uTemplate reorganized"
fi

# 5. Update identity file location
if [[ -f "$UHOME/uMemory/sandbox/user.md" ]] && [[ ! -f "$UHOME/uMemory/user/identity.md" ]]; then
    echo "🔑 Moving user identity..."
    mv "$UHOME/uMemory/sandbox/user.md" "$UHOME/uMemory/user/identity.md"
    echo "✅ Identity moved to uMemory/user/identity.md"
fi

echo ""
echo "🎯 Reorganization Summary:"
echo "========================="
echo "📚 uKnowledge/"
echo "  ├── roadmap/        # System roadmap documents"
echo "  ├── packages/       # Package documentation"
echo "  ├── companion/      # AI assistance guides"
echo "  ├── general-library/"
echo "  └── maps/"
echo ""
echo "🧠 uMemory/"
echo "  ├── user/           # User identity and settings"
echo "  ├── scripts/        # User-created scripts"
echo "  ├── templates/      # User-customized templates"
echo "  ├── sandbox/        # User workspace"
echo "  ├── missions/       # User missions"
echo "  ├── milestones/     # User milestones"
echo "  ├── legacy/         # User legacy items"
echo "  ├── logs/           # User activity logs"
echo "  └── state/          # User state data"
echo ""
echo "⚙️ uCode/"
echo "  ├── packages/       # Package integration scripts"
echo "  └── *.sh           # System command scripts"
echo ""
echo "🔧 uScript/"
echo "  ├── system/         # Core system scripts"
echo "  ├── utilities/      # Utility scripts"
echo "  ├── automation/     # Automation scripts"
echo "  ├── examples/       # Example scripts"
echo "  └── extract/        # Data extraction tools"
echo ""
echo "📋 uTemplate/"
echo "  ├── system/         # System templates"
echo "  ├── datasets/       # System datasets"
echo "  ├── variables/      # System variables"
echo "  └── [TS project]    # TypeScript template engine"
echo ""
echo "✅ Reorganization Complete!"
echo ""
echo "🚀 Next Steps:"
echo "1. Run: ./uCode/ucode.sh to test the new structure"
echo "2. Update any custom scripts that reference old paths"
echo "3. User content is now clearly separated from system content"
echo "4. All system documentation is centralized in uKnowledge"
echo ""
