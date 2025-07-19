#!/bin/bash
# uDOS Tree Generator v2.0.0 - Consolidated tree generation system
# Combines make-tree.sh and make-tree-simple.sh functionality

UHOME="${HOME}/uDOS"
uDOS_ROOT="$UHOME"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Validate uDOS root
if [ ! -d "$uDOS_ROOT" ]; then
    red "❌ uDOS root directory not found at: $uDOS_ROOT"
    exit 1
fi

# Generate simple static tree
generate_simple_tree() {
    local output_file="$1"
    
    blue "🌳 Generating simple static tree structure..."
    
    cat > "$output_file" << 'EOF'
# uDOS v1.1.0 - Repository Structure
# Generated with consolidated tree generator

uDOS/
uDOS/
├── README.md                    # Main documentation and installation guide
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history and changes
├── start-udos.sh               # Quick launcher script
├── install-udos.sh             # One-click installation
├── docs/                       # Complete documentation
│   ├── command-reference.md    # 484-line complete command reference
│   ├── user-manual.md          # Comprehensive user guide
│   ├── feature-guide.md        # Feature documentation
│   ├── technical-architecture.md # System architecture
│   ├── template-system-v2-implementation.md # Template system docs
│   ├── development/            # Development documentation (dev-only)
│   └── roadmap/                # Future development plans
├── launcher/                   # macOS application launcher
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history and changes
├── start-udos.sh               # Quick launcher script
├── install-udos.sh             # One-click installation
├── docs/                       # Complete documentation
│   ├── command-reference.md    # 484-line complete command reference
│   ├── user-manual.md          # Comprehensive user guide
│   ├── feature-guide.md        # Feature documentation
│   ├── technical-architecture.md # System architecture
│   ├── template-system-v2-implementation.md # Template system docs
│   ├── development/            # Development documentation (dev-only)
│   └── roadmap/                # Future development plans
├── launcher/                   # macOS application launcher
│   ├── Launch-uDOS.command     # Command line launcher
│   ├── uDOS.app/               # Native macOS app
│   └── build-app.sh           # App build script
├── extension/                  # VS Code extension system
│   ├── udos-extension-1.0.0.vsix # Packaged extension (277KB)
│   ├── package.json           # Enhanced extension manifest
│   ├── dist/extension.js      # Compiled TypeScript
│   ├── src/extension.ts       # Source implementation
│   ├── syntaxes/              # uScript language support
│   ├── snippets/              # Code snippets
│   └── README.md              # Extension documentation
├── install/                    # Installation and distribution tools
│   ├── validate-alpha-v1.0.sh # Alpha validation
│   ├── prepare-release.sh     # Release preparation
│   └── create-clean-distribution.sh # Distribution builder
├── package/                    # Package management system
│   ├── manifest.json          # Package manifest
│   ├── assets/                # Package assets
│   ├── development/           # Development packages
│   ├── docs/                  # Package documentation
│   ├── editors/               # Editor integrations
│   └── utils/                 # Utility packages
├── uCode/                      # Core operational scripts (40+ scripts)
│   ├── ucode.sh               # Main uDOS shell (1,846 lines)
│   ├── unified-manager.sh     # Consolidated script manager
│   ├── dash.sh                # Dashboard system
│   ├── companion-system.sh   # Chester AI companion
│   ├── validate-installation.sh # System validation
│   ├── vscode-template-processor.sh # VS Code templates
│   ├── shortcode-processor-simple.sh # Shortcode system
│   ├── template-generator.sh  # Template generation
│   ├── user-roles.sh          # User role management
│   ├── init-user.sh           # User initialization
│   ├── package-manager.sh     # Package management
│   ├── privacy-guard.sh       # Privacy protection
│   ├── packages/              # Package installation scripts
│   │   ├── install-ripgrep.sh # Fast text search
│   │   ├── install-glow.sh    # Markdown viewer
│   │   ├── install-bat.sh     # Syntax highlighting
│   │   └── manager-simple.sh  # Package manager
│   └── vb-examples/           # VB command examples
├── uKnowledge/                 # Knowledge management system
│   ├── roadmap/               # 11 technical roadmaps
│   │   ├── v1.0-feature-roadmap.md
│   │   ├── v1.1-enhancement-roadmap.md
│   │   └── companion-system-roadmap.md
│   └── technical/             # Technical documentation
├── uMemory/                    # User data and memory (created on first run)
│   ├── user/                  # User profiles and identity
│   ├── moves/                 # Command history and moves
│   ├── missions/              # User missions and tasks
│   ├── logs/                  # System and user logs
│   └── backup/                # Backup storage
├── uScript/                    # uScript language files
│   ├── examples/              # Example uScript programs
│   ├── templates/             # uScript templates
│   └── libraries/             # uScript libraries
├── uTemplate/                  # Template system v2.1.0
│   ├── user-setup-template.md # User setup templates
│   ├── vscode-extension-template.md # VS Code extension templates
│   ├── vscode-workspace-template.md # Workspace configuration
│   ├── mission-template.md    # Mission templates
│   ├── move-template.md       # Move templates
│   └── system/                # System templates
├── .vscode/                    # VS Code workspace configuration
│   ├── settings.json          # Generated workspace settings (64 lines)
│   └── tasks.json             # 27+ automated tasks
├── progress/                   # Development progress and archives
│   ├── v1.0-archive/          # Historical v1.0 files
│   └── v1.1-archive/          # Redundant v1.1 files
└── sandbox/                    # Development sandbox environment
    ├── test-files/            # Test file area
    ├── experiments/           # Experimental features
    └── drafts/                # Draft documents

Key Features:
• 🎯 User DOS Shell - Markdown-native operating system
• 👤 User Role System - wizard, sorcerer, ghost, imp roles
• 🤖 Chester AI Companion - Integrated AI assistance
• 📝 uScript Language - Custom scripting language with VS Code support
• 🔧 Template System v2.1.0 - Advanced template processing
• 📊 Real-time Dashboard - System monitoring and analytics
• 🔒 Privacy-First Design - Local-first data storage
• 🌐 Cross-Platform Support - macOS, Linux, Windows compatibility
• 🔌 VS Code Extension - Complete development environment
• 📦 Package Management - Modular component system

Installation: ./install-udos.sh
Quick Start: ./start-udos.sh
Documentation: ./docs/user-manual.md
EOF

    green "✅ Simple tree generated: $output_file"
}

# Generate dynamic tree with filtering
generate_dynamic_tree() {
    local output_file="$1"
    local max_depth="${2:-3}"
    
    blue "🌳 Generating dynamic tree structure (depth: $max_depth)..."
    
    echo "# uDOS v1.1.0 - Dynamic Repository Structure" > "$output_file"
    echo "# Generated: $(date)" >> "$output_file"
    echo "" >> "$output_file"
    echo "uDOS/" >> "$output_file"
    
    generate_tree_recursive "$uDOS_ROOT" "├── " 1 "$max_depth" >> "$output_file"
    
    green "✅ Dynamic tree generated: $output_file"
}

# Recursive tree generation with filtering
generate_tree_recursive() {
    local dir="$1"
    local prefix="$2"
    local current_depth="$3"
    local max_depth="$4"
    
    if [[ "$current_depth" -gt "$max_depth" ]]; then
        return
    fi
    
    find "$dir" -mindepth 1 -maxdepth 1 ! -name ".*" | sort | while read -r entry; do
        local name=$(basename "$entry")
        
        # Filter out system and build artifacts
        case "$name" in
            "Contents"|"Icon"|"_CodeSignature"|*.lproj|*.car|*.icns|"Assets.car"|"Info.plist"|"document.wflow")
                continue
                ;;
            "node_modules"|".git"|".DS_Store"|"dist"|"out"|"build"|"target")
                continue
                ;;
            "__pycache__"|"*.pyc"|"*.pyo"|".pytest_cache")
                continue
                ;;
        esac
        
        if [[ -d "$entry" ]]; then
            echo "${prefix}${name}/"
            if [[ "$current_depth" -lt "$max_depth" ]]; then
                generate_tree_recursive "$entry" "│   $prefix" $((current_depth + 1)) "$max_depth"
            fi
        else
            # Add file size and description for key files
            local size=""
            if [[ -f "$entry" ]]; then
                local bytes=$(wc -c < "$entry" 2>/dev/null || echo "0")
                if [[ "$bytes" -gt 1048576 ]]; then
                    size=" ($(($bytes / 1048576))MB)"
                elif [[ "$bytes" -gt 1024 ]]; then
                    size=" ($(($bytes / 1024))KB)"
                elif [[ "$bytes" -gt 0 ]]; then
                    size=" (${bytes}B)"
                fi
            fi
            
            echo "${prefix}${name}${size}"
        fi
    done
}

# Generate tree with file counts
generate_stats_tree() {
    local output_file="$1"
    
    blue "🌳 Generating tree with statistics..."
    
    echo "# uDOS v1.1.0 - Repository Statistics" > "$output_file"
    echo "# Generated: $(date)" >> "$output_file"
    echo "" >> "$output_file"
    
    # Overall statistics
    echo "## Repository Overview" >> "$output_file"
    echo "" >> "$output_file"
    
    local total_files=$(find "$uDOS_ROOT" -type f ! -path "*/.*" ! -path "*/node_modules/*" ! -path "*/uMemory/*" | wc -l)
    local total_dirs=$(find "$uDOS_ROOT" -type d ! -path "*/.*" ! -path "*/node_modules/*" ! -path "*/uMemory/*" | wc -l)
    local total_scripts=$(find "$uDOS_ROOT" -name "*.sh" ! -path "*/.*" | wc -l)
    local total_templates=$(find "$uDOS_ROOT" -name "*-template.md" ! -path "*/.*" | wc -l)
    
    echo "- **Total Files**: $total_files" >> "$output_file"
    echo "- **Total Directories**: $total_dirs" >> "$output_file"
    echo "- **Shell Scripts**: $total_scripts" >> "$output_file"
    echo "- **Templates**: $total_templates" >> "$output_file"
    echo "" >> "$output_file"
    
    # Directory statistics
    echo "## Directory Breakdown" >> "$output_file"
    echo "" >> "$output_file"
    
    for dir in docs uCode uKnowledge uTemplate extension; do
        if [[ -d "$uDOS_ROOT/$dir" ]]; then
            local dir_files=$(find "$uDOS_ROOT/$dir" -type f ! -path "*/.*" | wc -l)
            echo "- **$dir/**: $dir_files files" >> "$output_file"
        fi
    done
    
    echo "" >> "$output_file"
    generate_simple_tree "/dev/stdout" | tail -n +4 >> "$output_file"
    
    green "✅ Statistics tree generated: $output_file"
}

# Main function
main() {
    local command="${1:-simple}"
    local output_file="${2:-$uDOS_ROOT/repo_structure.txt}"
    local depth="${3:-3}"
    
    case "$command" in
        "simple"|"static")
            generate_simple_tree "$output_file"
            ;;
        "dynamic"|"live")
            generate_dynamic_tree "$output_file" "$depth"
            ;;
        "stats"|"statistics")
            generate_stats_tree "$output_file"
            ;;
        "all")
            generate_simple_tree "$uDOS_ROOT/repo_structure_simple.txt"
            generate_dynamic_tree "$uDOS_ROOT/repo_structure_dynamic.txt" "$depth"
            generate_stats_tree "$uDOS_ROOT/repo_structure_stats.txt"
            green "✅ All tree variants generated"
            ;;
        "help")
            echo "🌳 uDOS Tree Generator v2.0.0"
            echo ""
            echo "Usage: $0 [command] [output_file] [depth]"
            echo ""
            echo "Commands:"
            echo "  simple     - Generate simple static tree (default)"
            echo "  dynamic    - Generate dynamic tree with filtering"
            echo "  stats      - Generate tree with file statistics"
            echo "  all        - Generate all variants"
            echo "  help       - Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 simple"
            echo "  $0 dynamic repo_tree.txt 4"
            echo "  $0 stats"
            echo "  $0 all"
            ;;
        *)
            red "❌ Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
