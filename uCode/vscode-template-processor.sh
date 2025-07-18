#!/bin/bash
# uDOS VS Code Extension Template Processor v2.1.0
# Processes VS Code extension templates with system configuration

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UTEMPLATE="${UHOME}/uTemplate"
EXTENSION_DIR="${UHOME}/extension"
VSCODE_DIR="${UHOME}/.vscode"

# Template files
EXTENSION_TEMPLATE="${UTEMPLATE}/vscode-extension-template.md"
WORKSPACE_TEMPLATE="${UTEMPLATE}/vscode-workspace-template.md"

# Color output helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Get current system configuration
load_system_config() {
    # Load user identity if available
    local identity_file="${UMEM}/user/identity.md"
    if [[ -f "$identity_file" ]]; then
        USER_ROLE=$(grep "Role:" "$identity_file" | cut -d':' -f2 | xargs | cut -d' ' -f1 || echo "ghost")
        USERNAME=$(grep "Username:" "$identity_file" | cut -d':' -f2 | xargs || echo "user")
        LOCATION=$(grep "Location:" "$identity_file" | cut -d':' -f2 | xargs || echo "Unknown")
    else
        USER_ROLE="ghost"
        USERNAME="user"
        LOCATION="Unknown"
    fi
    
    # Load preferences if available
    local prefs_file="${UMEM}/user/preferences.json"
    if [[ -f "$prefs_file" ]] && command -v jq >/dev/null 2>&1; then
        THEME=$(jq -r '.theme // "default"' "$prefs_file")
        DEBUG_MODE=$(jq -r '.debug // false' "$prefs_file")
        ENABLE_CHESTER=$(jq -r '.ai_companion // true' "$prefs_file")
    else
        THEME="default"
        DEBUG_MODE="false"
        ENABLE_CHESTER="true"
    fi
    
    # System detection
    PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
    case "$PLATFORM" in
        "darwin") PLATFORM="osx"; DEFAULT_SHELL="zsh" ;;
        "linux") PLATFORM="linux"; DEFAULT_SHELL="bash" ;;
        *) PLATFORM="linux"; DEFAULT_SHELL="bash" ;;
    esac
    
    # uDOS version detection
    if [[ -f "${UHOME}/CHANGELOG.md" ]]; then
        UDOS_VERSION=$(grep "^## \[" "${UHOME}/CHANGELOG.md" | head -n1 | grep -o '\[.*\]' | tr -d '[]' || echo "1.1.0")
    else
        UDOS_VERSION="1.1.0"
    fi
    
    # Extension version from package.json
    if [[ -f "${EXTENSION_DIR}/package.json" ]] && command -v jq >/dev/null 2>&1; then
        EXTENSION_VERSION=$(jq -r '.version // "1.0.0"' "${EXTENSION_DIR}/package.json")
    else
        EXTENSION_VERSION="1.0.0"
    fi
}

# Process extension template variables
process_extension_template() {
    local template_content
    template_content=$(cat "$EXTENSION_TEMPLATE")
    
    # Core variables
    template_content="${template_content//\{\{extension_version\}\}/$EXTENSION_VERSION}"
    template_content="${template_content//\{\{udos_version\}\}/$UDOS_VERSION}"
    template_content="${template_content//\{\{display_name\}\}/User DOS Shell}"
    template_content="${template_content//\{\{extension_description\}\}/VS Code extension for uDOS v$UDOS_VERSION markdown-native operating system}"
    template_content="${template_content//\{\{publisher\}\}/udos}"
    template_content="${template_content//\{\{minimum_vscode_version\}\}/1.60.0}"
    template_content="${template_content//\{\{repository_url\}\}/https://github.com/fredporter/uDOS.git}"
    template_content="${template_content//\{\{timestamp\}\}/$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
    
    # Platform-specific
    template_content="${template_content//\{\{platform\}\}/$PLATFORM}"
    template_content="${template_content//\{\{default_shell\}\}/$DEFAULT_SHELL}"
    template_content="${template_content//\{\{shell_path\}\}/./uCode/ucode.sh}"
    
    # User configuration
    template_content="${template_content//\{\{user_role\}\}/$USER_ROLE}"
    template_content="${template_content//\{\{enable_copilot\}\}/true}"
    template_content="${template_content//\{\{enable_chester\}\}/$ENABLE_CHESTER}"
    template_content="${template_content//\{\{markdown_theme\}\}/dark}"
    template_content="${template_content//\{\{install_method\}\}/auto}"
    
    echo "$template_content"
}

# Process workspace template variables
process_workspace_template() {
    local template_content
    template_content=$(cat "$WORKSPACE_TEMPLATE")
    
    # Environment variables
    template_content="${template_content//\{\{target_environment\}\}/development}"
    template_content="${template_content//\{\{user_role\}\}/$USER_ROLE}"
    template_content="${template_content//\{\{timestamp\}\}/$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
    template_content="${template_content//\{\{udos_version\}\}/$UDOS_VERSION}"
    
    # Path variables
    template_content="${template_content//\{\{udos_shell_path\}\}/./uCode/ucode.sh}"
    template_content="${template_content//\{\{template_path\}\}/./uTemplate}"
    template_content="${template_content//\{\{memory_path\}\}/./uMemory}"
    
    # Theme configuration
    local color_theme icon_theme markdown_theme
    case "$THEME" in
        "dark")
            color_theme="Dark+ (default dark)"
            icon_theme="vs-seti"
            markdown_theme="dark"
            ;;
        "light")
            color_theme="Default Light+"
            icon_theme="vs-minimal"
            markdown_theme="light"
            ;;
        *)
            color_theme="Dark+ (default dark)"
            icon_theme="vs-seti"
            markdown_theme="dark"
            ;;
    esac
    
    template_content="${template_content//\{\{color_theme\}\}/$color_theme}"
    template_content="${template_content//\{\{icon_theme\}\}/$icon_theme}"
    template_content="${template_content//\{\{markdown_theme\}\}/$markdown_theme}"
    
    # Feature toggles
    template_content="${template_content//\{\{enable_copilot\}\}/true}"
    template_content="${template_content//\{\{enable_chester\}\}/$ENABLE_CHESTER}"
    template_content="${template_content//\{\{auto_validate\}\}/true}"
    template_content="${template_content//\{\{minimap_enabled\}\}/false}"
    
    # Font and UI settings
    template_content="${template_content//\{\{editor_font_size\}\}/14}"
    template_content="${template_content//\{\{editor_font_family\}\}/Menlo, Monaco, 'Courier New', monospace}"
    template_content="${template_content//\{\{terminal_font_size\}\}/13}"
    template_content="${template_content//\{\{markdown_font_size\}\}/14}"
    template_content="${template_content//\{\{markdown_line_height\}\}/1.6}"
    template_content="${template_content//\{\{word_wrap\}\}/on}"
    template_content="${template_content//\{\{tree_indent\}\}/8}"
    template_content="${template_content//\{\{git_autofetch\}\}/true}"
    
    # GitHub Copilot settings
    template_content="${template_content//\{\{copilot_global\}\}/true}"
    template_content="${template_content//\{\{copilot_uscript\}\}/true}"
    template_content="${template_content//\{\{copilot_markdown\}\}/true}"
    template_content="${template_content//\{\{copilot_javascript\}\}/true}"
    template_content="${template_content//\{\{copilot_typescript\}\}/true}"
    
    echo "$template_content"
}

# Generate workspace settings JSON
generate_workspace_settings() {
    cat << EOF
{
  "terminal.integrated.defaultProfile.$PLATFORM": "$DEFAULT_SHELL",
  "terminal.integrated.cwd": "\${workspaceFolder}",
  "terminal.integrated.fontSize": 13,
  
  "files.watcherExclude": {
    "**/uMemory/**": true,
    "**/node_modules/**": true,
    "**/.git/**": true,
    "**/progress/**": true,
    "**/*.vsix": true,
    "**/dist/**": true,
    "**/out/**": true
  },
  
  "search.exclude": {
    "**/uMemory/**": true,
    "**/node_modules/**": true,
    "**/progress/**": true,
    "**/*.vsix": true
  },
  
  "files.associations": {
    "*.uscript": "uscript",
    "*.us": "uscript",
    "mission-*.md": "markdown",
    "move-*.md": "markdown",
    "*-template.md": "markdown"
  },
  
  "markdown.preview.theme": "dark",
  "markdown.preview.fontSize": 14,
  "markdown.preview.lineHeight": 1.6,
  
  "editor.fontSize": 14,
  "editor.fontFamily": "Menlo, Monaco, 'Courier New', monospace",
  "editor.minimap.enabled": false,
  "editor.wordWrap": "on",
  "editor.rulers": [80, 120],
  
  "workbench.colorTheme": "Dark+ (default dark)",
  "workbench.iconTheme": "vs-seti",
  "workbench.tree.indent": 8,
  
  "git.ignoreLimitWarning": true,
  "git.enabled": true,
  "git.autofetch": true,
  
  "udos.shellPath": "./uCode/ucode.sh",
  "udos.enableCopilot": true,
  "udos.userRole": "$USER_ROLE",
  "udos.enableChester": $ENABLE_CHESTER,
  "udos.autoValidate": true,
  "udos.templatePath": "./uTemplate",
  "udos.memoryPath": "./uMemory",
  
  "github.copilot.enable": {
    "*": true,
    "uscript": true,
    "markdown": true,
    "javascript": true,
    "typescript": true
  }
}
EOF
}

# Generate enhanced package.json for extension
generate_package_json() {
    cat << EOF
{
  "name": "udos-extension",
  "displayName": "uDOS $UDOS_VERSION - User DOS Shell",
  "description": "VS Code extension for uDOS $UDOS_VERSION markdown-native operating system with user roles and Chester AI companion",
  "version": "$EXTENSION_VERSION",
  "publisher": "udos",
  "engines": {
    "vscode": "^1.60.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/fredporter/uDOS.git"
  },
  "license": "MIT",
  "categories": [
    "Programming Languages",
    "Snippets",
    "Other"
  ],
  "keywords": [
    "uDOS",
    "markdown",
    "shell",
    "operating system",
    "uScript",
    "user-roles",
    "chester",
    "ai-companion",
    "privacy-first",
    "template-system"
  ],
  "activationEvents": [
    "onLanguage:uscript",
    "onCommand:udos.runCommand",
    "onCommand:udos.validateInstallation", 
    "onCommand:udos.showUserRole",
    "onCommand:udos.startChester",
    "workspaceContains:**/uCode/ucode.sh"
  ],
  "main": "./dist/extension.js",
  "contributes": {
    "languages": [
      {
        "id": "uscript",
        "aliases": ["uScript", "uscript"],
        "extensions": [".uscript", ".us"],
        "configuration": "./language-configuration.json"
      }
    ],
    "grammars": [
      {
        "language": "uscript",
        "scopeName": "source.uscript",
        "path": "./syntaxes/uscript.tmLanguage.json"
      }
    ],
    "snippets": [
      {
        "language": "uscript",
        "path": "./snippets/uscript.json"
      }
    ],
    "commands": [
      {
        "command": "udos.runCommand",
        "title": "Run uDOS Command",
        "category": "uDOS"
      },
      {
        "command": "udos.generateDashboard",
        "title": "Generate Dashboard",
        "category": "uDOS"
      },
      {
        "command": "udos.createMission",
        "title": "Create New Mission",
        "category": "uDOS"
      },
      {
        "command": "udos.viewWithGlow",
        "title": "View with Glow",
        "category": "uDOS"
      },
      {
        "command": "udos.validateInstallation",
        "title": "Validate Installation",
        "category": "uDOS"
      },
      {
        "command": "udos.showUserRole",
        "title": "Show User Role",
        "category": "uDOS"
      },
      {
        "command": "udos.initializeUser",
        "title": "Initialize User",
        "category": "uDOS"
      },
      {
        "command": "udos.startChester",
        "title": "Start Chester AI",
        "category": "uDOS"
      }
    ],
    "menus": {
      "explorer/context": [
        {
          "when": "resourceExtname == .md",
          "command": "udos.viewWithGlow",
          "group": "navigation"
        }
      ],
      "commandPalette": [
        {
          "command": "udos.runCommand",
          "when": "workspaceContains:**/uCode/ucode.sh"
        },
        {
          "command": "udos.generateDashboard",
          "when": "workspaceContains:**/uCode/enhanced-dash.sh"
        }
      ]
    },
    "keybindings": [
      {
        "command": "udos.runCommand",
        "key": "ctrl+shift+u",
        "mac": "cmd+shift+u"
      }
    ],
    "configuration": {
      "title": "uDOS",
      "properties": {
        "udos.shellPath": {
          "type": "string",
          "default": "./uCode/ucode.sh",
          "description": "Path to uDOS shell script"
        },
        "udos.enableCopilot": {
          "type": "boolean",
          "default": true,
          "description": "Enable GitHub Copilot integration for uScript"
        },
        "udos.userRole": {
          "type": "string",
          "enum": ["wizard", "sorcerer", "ghost", "imp"],
          "default": "ghost",
          "description": "Current user role in uDOS system"
        },
        "udos.enableChester": {
          "type": "boolean",
          "default": true,
          "description": "Enable Chester AI companion integration"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "npx @vscode/vsce package",
    "install-extension": "code --install-extension \$(ls -t *.vsix | head -n1)"
  },
  "devDependencies": {
    "@types/vscode": "^1.60.0",
    "@types/node": "16.x",
    "typescript": "^4.9.4",
    "@vscode/vsce": "^2.15.0"
  }
}
EOF
}

# Main processing function
process_templates() {
    local command="${1:-process}"
    
    blue "🔧 uDOS VS Code Extension Template Processor v2.1.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Load system configuration
    blue "📋 Loading system configuration..."
    load_system_config
    
    echo "  👤 User: $USERNAME ($USER_ROLE)"
    echo "  🌍 Location: $LOCATION"
    echo "  🎨 Theme: $THEME"
    echo "  🖥️  Platform: $PLATFORM"
    echo "  📦 uDOS: $UDOS_VERSION"
    echo "  🔌 Extension: $EXTENSION_VERSION"
    echo
    
    case "$command" in
        "process"|"generate")
            blue "🔧 Processing templates..."
            
            # Create directories
            mkdir -p "$VSCODE_DIR"
            
            # Generate workspace settings
            blue "📝 Generating workspace settings..."
            generate_workspace_settings > "$VSCODE_DIR/settings.json"
            green "✅ Generated: $VSCODE_DIR/settings.json"
            
            # Update extension package.json if it exists
            if [[ -d "$EXTENSION_DIR" ]]; then
                blue "📦 Updating extension configuration..."
                generate_package_json > "$EXTENSION_DIR/package.json.new"
                
                if [[ -f "$EXTENSION_DIR/package.json" ]]; then
                    mv "$EXTENSION_DIR/package.json" "$EXTENSION_DIR/package.json.backup"
                    yellow "⚠️ Backed up original package.json"
                fi
                
                mv "$EXTENSION_DIR/package.json.new" "$EXTENSION_DIR/package.json"
                green "✅ Updated: $EXTENSION_DIR/package.json"
            fi
            
            green "🎉 Template processing complete!"
            ;;
        
        "validate")
            blue "🔍 Validating template configuration..."
            
            # Check template files
            if [[ -f "$EXTENSION_TEMPLATE" ]]; then
                green "✅ Extension template found"
            else
                red "❌ Extension template missing: $EXTENSION_TEMPLATE"
            fi
            
            if [[ -f "$WORKSPACE_TEMPLATE" ]]; then
                green "✅ Workspace template found"
            else
                red "❌ Workspace template missing: $WORKSPACE_TEMPLATE"
            fi
            
            # Check extension directory
            if [[ -d "$EXTENSION_DIR" ]]; then
                green "✅ Extension directory found"
                
                if [[ -f "$EXTENSION_DIR/package.json" ]]; then
                    green "✅ Extension package.json found"
                else
                    yellow "⚠️ Extension package.json missing"
                fi
            else
                red "❌ Extension directory missing: $EXTENSION_DIR"
            fi
            
            # Check VS Code configuration
            if [[ -d "$VSCODE_DIR" ]]; then
                green "✅ VS Code directory found"
                
                if [[ -f "$VSCODE_DIR/settings.json" ]]; then
                    green "✅ Workspace settings found"
                else
                    yellow "⚠️ Workspace settings missing"
                fi
            else
                yellow "⚠️ VS Code directory missing (will be created)"
            fi
            ;;
        
        "help")
            echo "🔧 uDOS VS Code Extension Template Processor"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  process   - Process templates and generate configuration"
            echo "  generate  - Alias for process"
            echo "  validate  - Validate template system"
            echo "  help      - Show this help"
            echo
            echo "Generated files:"
            echo "  .vscode/settings.json         - Workspace configuration"
            echo "  extension/package.json        - Extension manifest (updated)"
            echo
            ;;
        
        *)
            red "❌ Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
process_templates "$@"
