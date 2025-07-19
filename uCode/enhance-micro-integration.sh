#!/bin/bash
# uDOS Enhanced Micro Editor Integration
# Extends micro editor with uDOS-specific features without forking

set -euo pipefail

UHOME="${HOME}/uDOS"
MICRO_CONFIG_DIR="${HOME}/.config/micro"
UDOS_MICRO_DIR="${UHOME}/uCode/micro-integration"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Initialize enhanced micro integration
init_micro_integration() {
    bold "🎨 uDOS Enhanced Micro Editor Integration v1.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create directories
    mkdir -p "$MICRO_CONFIG_DIR/plugins"
    mkdir -p "$MICRO_CONFIG_DIR/colorschemes"
    mkdir -p "$UDOS_MICRO_DIR/plugins"
    mkdir -p "$UDOS_MICRO_DIR/configs"
    
    # Check if micro is installed
    if ! command -v micro >/dev/null 2>&1; then
        yellow "⚠️  Micro editor not found. Installing..."
        if [[ -f "$UHOME/uCode/packages/consolidated-manager.sh" ]]; then
            bash "$UHOME/uCode/packages/consolidated-manager.sh" install micro
        else
            echo "❌ Package manager not available"
            return 1
        fi
    fi
    
    # Setup uDOS-specific micro configuration
    setup_micro_config
    
    # Install uDOS syntax highlighting
    setup_syntax_highlighting
    
    # Create uDOS color scheme
    setup_color_scheme
    
    # Install uDOS plugins
    setup_plugins
    
    # Update editor integration
    update_editor_integration
    
    green "✅ Enhanced micro integration complete!"
    show_usage_examples
}

# Setup micro configuration optimized for uDOS
setup_micro_config() {
    cyan "⚙️ Setting up uDOS-optimized micro configuration..."
    
    cat > "$MICRO_CONFIG_DIR/settings.json" << 'EOF'
{
    "autoclose": true,
    "autoindent": true,
    "autosave": 5,
    "autosu": false,
    "backup": true,
    "backupdir": "",
    "basename": false,
    "colorcolumn": 0,
    "colorscheme": "udos-dark",
    "cursorline": true,
    "diff": true,
    "diffgutter": true,
    "divchars": "|-",
    "divreverse": true,
    "encoding": "utf-8",
    "eofnewline": true,
    "fastdirty": false,
    "fileformat": "unix",
    "filetype": "unknown",
    "hlsearch": false,
    "ignorecase": false,
    "indentchar": " ",
    "infobar": true,
    "keepautoindent": false,
    "keymenu": false,
    "matchbrace": true,
    "matchbraceleft": false,
    "mkparents": true,
    "mouse": true,
    "parsecursor": false,
    "paste": false,
    "pluginchannels": [
        "https://github.com/micro-editor/plugin-channel"
    ],
    "pluginrepos": [],
    "readonly": false,
    "rmtrailingws": true,
    "ruler": true,
    "savecursor": true,
    "savehistory": true,
    "saveundo": true,
    "scrollbar": false,
    "scrollmargin": 3,
    "scrollspeed": 2,
    "smartpaste": true,
    "softwrap": false,
    "splitbottom": true,
    "splitright": true,
    "statusformatl": "$(filename) $(modified)$(line:col) $(opt:filetype) $(opt:fileformat) $(opt:encoding)",
    "statusformatr": "$(bind:ToggleKeyMenu): bindings, $(bind:ToggleHelp): help",
    "statusline": true,
    "sucmd": "sudo",
    "syntax": true,
    "tabmovement": false,
    "tabsize": 2,
    "tabstospaces": true,
    "termtitle": false,
    "trimdiff": false,
    "useprimary": true,
    "wordwrap": false,
    "xterm": false
}
EOF
    
    echo "  📄 Created uDOS-optimized settings.json"
}

# Setup syntax highlighting for uDOS file types
setup_syntax_highlighting() {
    cyan "🎨 Setting up uDOS syntax highlighting..."
    
    # Create uScript syntax file
    cat > "$MICRO_CONFIG_DIR/syntax/uscript.yaml" << 'EOF'
filetype: uscript

detect:
    filename: "\\.u(script|s)$"

rules:
    # Comments
    - comment: "^\\s*'.*$"
    
    # Keywords
    - statement: "\\b(SET|IF|THEN|ELSE|END|FOR|NEXT|FUNCTION|SUB|RETURN|CALL|RUN|LOG|TREE|LIST|DASH)\\b"
    
    # Data types
    - type: "\\b(AS|STRING|INTEGER|BOOLEAN|ARRAY)\\b"
    
    # uDOS Commands
    - special: "\\b(CHECK|MISSION|MOVE|TEMPLATE|PACKAGE|CHESTER|COMPANION)\\b"
    
    # Shortcodes
    - constant.string: "\\[\\w+:[^\\]]*\\]"
    
    # Strings
    - constant.string: "\".*\""
    - constant.string: "'[^']*'"
    
    # Numbers
    - constant.number: "\\b[0-9]+\\b"
    
    # Operators
    - symbol.operator: "[=<>!+\\-*/%]"
    
    # Variables
    - identifier: "\\$\\w+"
EOF

    # Create markdown extension for shortcodes
    cat > "$MICRO_CONFIG_DIR/syntax/udos-markdown.yaml" << 'EOF'
filetype: udos-markdown

detect:
    filename: "\\.(md|markdown)$"

rules:
    # Inherit from markdown
    - include: "markdown"
    
    # uDOS Shortcodes - highlighted as special
    - special: "\\[\\w+:[^\\]]*\\]"
    
    # uDOS Template Variables
    - identifier: "\\{\\{[^}]*\\}\\}"
    
    # Mission/Move markers
    - constant.bool: "^# 🎯 MISSION:"
    - constant.bool: "^# 📝 MOVE:"
    
    # uDOS Commands in code blocks
    - statement: "\\bucode\\s+\\w+"
EOF

    echo "  🎨 Created uScript and uDOS-markdown syntax highlighting"
}

# Setup uDOS color scheme
setup_color_scheme() {
    cyan "🌈 Creating uDOS color scheme..."
    
    cat > "$MICRO_CONFIG_DIR/colorschemes/udos-dark.micro" << 'EOF'
# uDOS Dark Theme
# Optimized for terminal usage with uDOS

color-link default "231,235"
color-link comment "242"
color-link identifier "81"
color-link constant "141"
color-link constant.string "185"
color-link constant.string.char "185"
color-link constant.number "141"
color-link constant.bool "141"
color-link statement "204"
color-link symbol.operator "204"
color-link preproc "204"
color-link type "81"
color-link special "226"
color-link underlined "underline"
color-link error "196"
color-link todo "226"
color-link hlsearch "235,226"
color-link statusline "231,239"
color-link tabbar "231,239"
color-link indent-char "239"
color-link line-number "244"
color-link current-line-number "226"
color-link diff-added "119"
color-link diff-modified "221"
color-link diff-deleted "204"
color-link gutter-error "196"
color-link gutter-warning "221"
color-link cursor-line "238"
color-link color-column "237"
color-link ignore "237"
color-link scrollbar "239"
color-link divider "239"

# uDOS-specific highlighting
color-link uscript.statement "204"
color-link uscript.special "226"
color-link markdown.shortcode "226"
color-link template.variable "81"
EOF

    echo "  🎨 Created uDOS dark color scheme"
}

# Setup uDOS-specific plugins
setup_plugins() {
    cyan "🔌 Setting up uDOS plugins..."
    
    # Create shortcode processor plugin
    cat > "$UDOS_MICRO_DIR/plugins/udos-shortcuts.lua" << 'EOF'
VERSION = "1.0.0"

local config = import("micro/config")
local shell = import("micro/shell")
local buffer = import("micro/buffer")

function init()
    config.MakeCommand("udos-process", processShortcodes, config.NoComplete)
    config.MakeCommand("udos-chester", callChester, config.NoComplete)
    config.MakeCommand("udos-template", insertTemplate, config.NoComplete)
    config.TryBindKey("Ctrl-u", "command:udos-process", true)
    config.TryBindKey("Ctrl-h", "command:udos-chester", true)
end

function processShortcodes(bp)
    local buf = bp.Buf
    local output, err = shell.RunCommand("bash " .. os.getenv("HOME") .. "/uDOS/uCode/shortcode-processor-simple.sh process")
    
    if err ~= nil then
        micro.InfoBar():Error("Error processing shortcodes: " .. err)
    else
        micro.InfoBar():Message("✅ Shortcodes processed successfully")
    end
end

function callChester(bp)
    local buf = bp.Buf
    local selection = buf:GetSelection()
    local text = selection or "help"
    
    local output, err = shell.RunCommand("bash " .. os.getenv("HOME") .. "/uDOS/uCode/companion-system.sh chester-help \"" .. text .. "\"")
    
    if err ~= nil then
        micro.InfoBar():Error("Chester unavailable: " .. err)
    else
        micro.InfoBar():Message("🐕 Chester: " .. output)
    end
end

function insertTemplate(bp)
    local buf = bp.Buf
    micro.InfoBar():Prompt("Template type: ", "", "template", function(input, canceled)
        if not canceled and input ~= "" then
            local output, err = shell.RunCommand("bash " .. os.getenv("HOME") .. "/uDOS/uCode/template-generator.sh generate " .. input)
            if err == nil then
                buf:Insert(buf:GetActiveCursor().Loc, output)
            end
        end
    end)
end
EOF

    # Copy plugin to micro plugins directory
    cp "$UDOS_MICRO_DIR/plugins/udos-shortcuts.lua" "$MICRO_CONFIG_DIR/plugins/"
    
    echo "  🔌 Installed uDOS shortcuts plugin"
    echo "    • Ctrl-U: Process shortcodes in current file"
    echo "    • Ctrl-H: Call Chester AI assistant"
    echo "    • :udos-template: Insert template"
}

# Update editor integration to prefer enhanced micro
update_editor_integration() {
    cyan "🔄 Updating editor integration preferences..."
    
    # Create enhanced editor preferences
    local editor_prefs="${UHOME}/uMemory/config/enhanced-editor-prefs.json"
    mkdir -p "$(dirname "$editor_prefs")"
    
    cat > "$editor_prefs" << 'EOF'
{
    "enhanced_micro": {
        "enabled": true,
        "config_path": "~/.config/micro",
        "features": {
            "udos_syntax": true,
            "shortcode_processing": true,
            "chester_integration": true,
            "template_insertion": true
        },
        "keybindings": {
            "process_shortcodes": "Ctrl-U",
            "chester_help": "Ctrl-H",
            "insert_template": ":udos-template"
        }
    },
    "file_associations": {
        ".uscript": "micro",
        ".us": "micro",
        ".md": "micro",
        ".markdown": "micro",
        "mission-*.md": "micro",
        "move-*.md": "micro"
    }
}
EOF

    echo "  ✅ Enhanced micro is now preferred editor for uDOS files"
}

# Show usage examples
show_usage_examples() {
    echo
    bold "🎯 Enhanced Micro Editor Usage"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    green "📝 Quick Commands:"
    echo "  • micro filename.md        # Opens with uDOS syntax highlighting"
    echo "  • Ctrl-U                   # Process shortcodes in file"
    echo "  • Ctrl-H                   # Get Chester AI help"
    echo "  • :udos-template mission   # Insert mission template"
    echo
    green "🎨 Features:"
    echo "  • Syntax highlighting for uScript and shortcodes"
    echo "  • uDOS dark color scheme optimized for terminal"
    echo "  • Integrated shortcode processing"
    echo "  • Chester AI assistant integration"
    echo "  • Template insertion commands"
    echo
    green "🔧 Configuration:"
    echo "  • Settings: ~/.config/micro/settings.json"
    echo "  • Plugins: ~/.config/micro/plugins/"
    echo "  • Color schemes: ~/.config/micro/colorschemes/"
    echo
    cyan "💡 Try editing a mission file to see the enhanced experience!"
}

# Command handling
case "${1:-init}" in
    "init"|"install"|"setup")
        init_micro_integration
        ;;
    "update")
        cyan "🔄 Updating enhanced micro configuration..."
        setup_micro_config
        setup_syntax_highlighting
        setup_color_scheme
        green "✅ Configuration updated"
        ;;
    "plugins")
        cyan "🔌 Reinstalling uDOS plugins..."
        setup_plugins
        green "✅ Plugins updated"
        ;;
    "help"|"--help"|"-h")
        echo "Enhanced Micro Editor Integration for uDOS"
        echo ""
        echo "Commands:"
        echo "  init      Initialize enhanced micro integration"
        echo "  update    Update configuration files"
        echo "  plugins   Reinstall uDOS plugins"
        echo "  help      Show this help"
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use 'help' for available commands"
        exit 1
        ;;
esac
