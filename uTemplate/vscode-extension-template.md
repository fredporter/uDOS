# 🔌 VS Code Extension Template for uDOS

**Template Version**: v2.1.0  
**Extension Version**: {{extension_version}}  
**uDOS Version**: {{udos_version}}  
**Generated**: {{timestamp}}

---

## 📦 Extension Configuration Template

### Extension Manifest
```json
{
  "name": "udos-extension",
  "displayName": "uDOS {{udos_version}} - {{display_name}}",
  "description": "{{extension_description}}",
  "version": "{{extension_version}}",
  "publisher": "{{publisher}}",
  "engines": {
    "vscode": "^{{minimum_vscode_version}}"
  },
  "repository": {
    "type": "git",
    "url": "{{repository_url}}"
  },
  "license": "MIT",
  "categories": [
    "Programming Languages",
    "Snippets",
    "Other"
  ],
  "keywords": {{keywords_json}},
  "activationEvents": {{activation_events_json}},
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
    "commands": {{commands_json}},
    "menus": {{menus_json}},
    "keybindings": {{keybindings_json}},
    "configuration": {{configuration_json}}
  },
  "scripts": {{scripts_json}},
  "devDependencies": {{dev_dependencies_json}}
}
```

### VS Code Workspace Settings Template
```json
{
  "terminal.integrated.defaultProfile.{{platform}}": "{{default_shell}}",
  "terminal.integrated.cwd": "${workspaceFolder}",
  "files.watcherExclude": {
    "**/uMemory/**": true,
    "**/node_modules/**": true,
    "**/.git/**": true
  },
  "search.exclude": {
    "**/uMemory/**": true,
    "**/node_modules/**": true
  },
  "markdown.preview.theme": "{{markdown_theme}}",
  "udos.shellPath": "{{shell_path}}",
  "udos.enableCopilot": {{enable_copilot}},
  "udos.userRole": "{{user_role}}",
  "udos.enableChester": {{enable_chester}}
}
```

---

## 🎯 Extension Installation Template

### Automated Installation Script
```bash
#!/bin/bash
# uDOS VS Code Extension Installer (Generated from Template)
# Version: {{extension_version}}
# Target: {{target_platform}}

set -euo pipefail

# Configuration from template
EXTENSION_VERSION="{{extension_version}}"
UDOS_VERSION="{{udos_version}}"
VSCODE_MIN_VERSION="{{minimum_vscode_version}}"
INSTALL_METHOD="{{install_method}}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🔵 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check prerequisites
check_vscode() {
    log_info "Checking VS Code installation..."
    
    if command -v code &> /dev/null; then
        local vscode_version=$(code --version | head -n1)
        log_success "VS Code found: $vscode_version"
        return 0
    else
        log_error "VS Code not found. Please install VS Code first."
        return 1
    fi
}

# Build extension
build_extension() {
    log_info "Building uDOS VS Code Extension v$EXTENSION_VERSION..."
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing dependencies..."
        npm install
    fi
    
    # Compile TypeScript
    log_info "Compiling TypeScript..."
    npm run compile
    
    if [[ $? -eq 0 ]]; then
        log_success "Extension compiled successfully"
    else
        log_error "Compilation failed"
        return 1
    fi
    
    # Package extension
    log_info "Packaging extension..."
    npm run package
    
    if [[ $? -eq 0 ]]; then
        log_success "Extension packaged successfully"
    else
        log_error "Packaging failed"
        return 1
    fi
}

# Install extension
install_extension() {
    log_info "Installing uDOS VS Code Extension..."
    
    # Get the latest VSIX file
    local vsix_file=$(ls -t *.vsix | head -n1)
    
    if [[ -n "$vsix_file" ]]; then
        log_info "Installing extension: $vsix_file"
        code --install-extension "$vsix_file"
        
        if [[ $? -eq 0 ]]; then
            log_success "uDOS VS Code Extension v$EXTENSION_VERSION installed!"
            log_info "Please reload VS Code to activate the extension"
            return 0
        else
            log_error "Installation failed"
            return 1
        fi
    else
        log_error "No VSIX file found"
        return 1
    fi
}

# Configure workspace
configure_workspace() {
    log_info "Configuring VS Code workspace..."
    
    # Create .vscode directory if it doesn't exist
    mkdir -p ../.vscode
    
    # Generate workspace settings from template
    cat > ../.vscode/settings.json << 'EOF'
{{workspace_settings_json}}
EOF
    
    log_success "Workspace configured for uDOS development"
}

# Main installation process
main() {
    log_info "🔌 uDOS VS Code Extension Installer v$EXTENSION_VERSION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    check_vscode || exit 1
    build_extension || exit 1
    install_extension || exit 1
    configure_workspace || exit 1
    
    echo
    log_success "🎉 uDOS VS Code Extension installation complete!"
    echo
    echo "Available commands:"
    echo "  - uDOS: Run Command"
    echo "  - uDOS: Validate Installation" 
    echo "  - uDOS: Show User Role"
    echo "  - uDOS: Start Chester AI"
    echo "  - uDOS: Create Mission"
    echo
    echo "Keyboard shortcut: Ctrl+Shift+U (Cmd+Shift+U on macOS)"
}

main "$@"
```

---

## 📝 Template Variables Reference

### Core Variables
- `{{extension_version}}` - Extension version (e.g., "1.0.0")
- `{{udos_version}}` - uDOS system version (e.g., "v1.1.0")
- `{{display_name}}` - Extension display name
- `{{extension_description}}` - Extension description
- `{{publisher}}` - Extension publisher ID

### Technical Variables
- `{{minimum_vscode_version}}` - Minimum VS Code version
- `{{repository_url}}` - Git repository URL
- `{{platform}}` - Target platform (osx/linux/win32)
- `{{default_shell}}` - Default shell (zsh/bash/powershell)
- `{{shell_path}}` - Path to uDOS shell script

### Configuration Variables
- `{{user_role}}` - Default user role (wizard/sorcerer/ghost/imp)
- `{{enable_copilot}}` - GitHub Copilot integration (true/false)
- `{{enable_chester}}` - Chester AI integration (true/false)
- `{{markdown_theme}}` - Markdown preview theme
- `{{install_method}}` - Installation method (auto/manual/task)

### JSON Arrays (Template Processor Populated)
- `{{keywords_json}}` - Extension keywords array
- `{{activation_events_json}}` - VS Code activation events
- `{{commands_json}}` - Extension commands configuration
- `{{menus_json}}` - Context menu configuration
- `{{keybindings_json}}` - Keyboard shortcuts
- `{{configuration_json}}` - Extension settings schema
- `{{scripts_json}}` - NPM scripts configuration
- `{{dev_dependencies_json}}` - Development dependencies
- `{{workspace_settings_json}}` - Complete workspace settings

---

## 🔄 Template Processing Instructions

### Generate Extension Configuration
```bash
# Process template with current system configuration
./uCode/template-processor.sh process vscode-extension-template.md

# Generated files:
# - extension/package.json (updated with current config)
# - extension/install-extension.sh (platform-specific installer)
# - .vscode/settings.json (workspace configuration)
```

### Customization Points
1. **User Role Integration**: Extension respects current user role
2. **Platform Detection**: Automatically configures for macOS/Linux/Windows
3. **Feature Toggles**: Chester AI and Copilot can be enabled/disabled
4. **Theme Integration**: Matches uDOS color scheme and preferences

---

*This template ensures the VS Code extension is properly configured for each installation environment and maintains consistency with uDOS system configuration.*
