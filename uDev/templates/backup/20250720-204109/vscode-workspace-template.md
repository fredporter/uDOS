# 🔧 VS Code Workspace Settings Template

**Template Version**: v2.1.0  
**Target**: {{target_environment}}  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 🎯 Workspace Configuration Template

### Complete Settings Template
```json
{
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.defaultProfile.linux": "bash",
  "terminal.integrated.defaultProfile.windows": "powershell",
  "terminal.integrated.cwd": "${workspaceFolder}",
  "terminal.integrated.fontSize": {{terminal_font_size}},
  
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
  
  "markdown.preview.theme": "{{markdown_theme}}",
  "markdown.preview.fontSize": {{markdown_font_size}},
  "markdown.preview.lineHeight": {{markdown_line_height}},
  
  "editor.fontSize": {{editor_font_size}},
  "editor.fontFamily": "{{editor_font_family}}",
  "editor.minimap.enabled": {{minimap_enabled}},
  "editor.wordWrap": "{{word_wrap}}",
  "editor.rulers": [80, 120],
  
  "workbench.colorTheme": "{{color_theme}}",
  "workbench.iconTheme": "{{icon_theme}}",
  "workbench.tree.indent": {{tree_indent}},
  
  "git.ignoreLimitWarning": true,
  "git.enabled": true,
  "git.autofetch": {{git_autofetch}},
  
  "udos.shellPath": "{{udos_shell_path}}",
  "udos.enableCopilot": {{enable_copilot}},
  "udos.userRole": "{{user_role}}",
  "udos.enableChester": {{enable_chester}},
  "udos.autoValidate": {{auto_validate}},
  "udos.templatePath": "{{template_path}}",
  "udos.memoryPath": "{{memory_path}}",
  
  "github.copilot.enable": {
    "*": {{copilot_global}},
    "uscript": {{copilot_uscript}},
    "markdown": {{copilot_markdown}},
    "javascript": {{copilot_javascript}},
    "typescript": {{copilot_typescript}}
  }
}
```

### Role-Specific Configurations

#### Wizard Role Settings
```json
{
  "udos.userRole": "wizard",
  "udos.debugMode": true,
  "udos.enableAllFeatures": true,
  "udos.showSystemCommands": true,
  "udos.allowDangerousOperations": true,
  "terminal.integrated.env.osx": {
    "UDOS_ROLE": "wizard",
    "UDOS_DEBUG": "true"
  }
}
```

#### Sorcerer Role Settings
```json
{
  "udos.userRole": "sorcerer",
  "udos.debugMode": true,
  "udos.enableAllFeatures": true,
  "udos.showSystemCommands": false,
  "udos.allowDangerousOperations": false,
  "terminal.integrated.env.osx": {
    "UDOS_ROLE": "sorcerer",
    "UDOS_DEBUG": "true"
  }
}
```

#### Ghost Role Settings
```json
{
  "udos.userRole": "ghost",
  "udos.debugMode": false,
  "udos.enableAllFeatures": false,
  "udos.showSystemCommands": false,
  "udos.allowDangerousOperations": false,
  "terminal.integrated.env.osx": {
    "UDOS_ROLE": "ghost",
    "UDOS_DEBUG": "false"
  }
}
```

#### Imp Role Settings
```json
{
  "udos.userRole": "imp",
  "udos.debugMode": false,
  "udos.enableAllFeatures": false,
  "udos.showSystemCommands": false,
  "udos.allowDangerousOperations": false,
  "udos.sandboxMode": true,
  "terminal.integrated.env.osx": {
    "UDOS_ROLE": "imp",
    "UDOS_DEBUG": "false",
    "UDOS_SANDBOX": "true"
  }
}
```

---

## 🎨 Theme Integration Template

### Dark Theme Configuration
```json
{
  "workbench.colorTheme": "{{dark_theme}}",
  "terminal.integrated.theme": "{{dark_terminal_theme}}",
  "markdown.preview.theme": "dark",
  "udos.theme": "dark",
  "udos.asciiColors": {
    "primary": "{{dark_primary_color}}",
    "secondary": "{{dark_secondary_color}}",
    "accent": "{{dark_accent_color}}"
  }
}
```

### Light Theme Configuration
```json
{
  "workbench.colorTheme": "{{light_theme}}",
  "terminal.integrated.theme": "{{light_terminal_theme}}",
  "markdown.preview.theme": "light",
  "udos.theme": "light",
  "udos.asciiColors": {
    "primary": "{{light_primary_color}}",
    "secondary": "{{light_secondary_color}}",
    "accent": "{{light_accent_color}}"
  }
}
```

---

## 🔧 Development Environment Template

### TypeScript Configuration
```json
{
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "typescript.updateImportsOnFileMove.enabled": "always",
  "typescript.suggest.autoImports": true,
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

### Extension Development Settings
```json
{
  "extensions.autoUpdate": {{auto_update_extensions}},
  "extensions.ignoreRecommendations": false,
  "extensions.showRecommendationsOnlyOnDemand": {{show_recommendations_on_demand}},
  "vsce.packagePath": "./extension"
}
```

### Debugging Configuration
```json
{
  "debug.console.fontSize": {{debug_console_font_size}},
  "debug.console.wordWrap": true,
  "debug.openDebug": "{{debug_open_mode}}",
  "debug.inlineValues": {{debug_inline_values}}
}
```

---

## 📋 Template Variables Reference

### Environment Variables
- `{{target_environment}}` - Target environment (development/production)
- `{{user_role}}` - Current user role (wizard/sorcerer/ghost/imp)
- `{{timestamp}}` - Generation timestamp
- `{{udos_version}}` - uDOS system version

### Path Variables
- `{{udos_shell_path}}` - Path to uDOS shell script
- `{{template_path}}` - Path to uTemplate directory
- `{{memory_path}}` - Path to uMemory directory

### Theme Variables
- `{{color_theme}}` - VS Code color theme
- `{{icon_theme}}` - VS Code icon theme
- `{{markdown_theme}}` - Markdown preview theme
- `{{dark_theme}}` / `{{light_theme}}` - Theme variants

### Feature Toggles
- `{{enable_copilot}}` - GitHub Copilot integration (true/false)
- `{{enable_chester}}` - Chester AI integration (true/false)
- `{{auto_validate}}` - Automatic validation (true/false)
- `{{minimap_enabled}}` - Editor minimap (true/false)

### Font & UI Variables
- `{{editor_font_size}}` - Editor font size (default: 14)
- `{{editor_font_family}}` - Editor font family
- `{{terminal_font_size}}` - Terminal font size (default: 13)
- `{{markdown_font_size}}` - Markdown preview font size
- `{{word_wrap}}` - Editor word wrap setting

---

## 🔄 Template Processing Instructions

### Generate Workspace Settings
```bash
# Process template with current user configuration
./uCode/template-processor.sh process vscode-workspace-template.md

# Generated files:
# - .vscode/settings.json (complete workspace configuration)
# - .vscode/launch.json (debugging configuration)
# - .vscode/tasks.json (enhanced with user role awareness)
```

### Role-Based Processing
```bash
# Generate settings for specific role
./uCode/template-processor.sh process vscode-workspace-template.md --role wizard

# Generate settings with custom theme
./uCode/template-processor.sh process vscode-workspace-template.md --theme dark
```

---

*This template ensures VS Code workspace is optimally configured for uDOS development with proper user role integration and feature customization.*
