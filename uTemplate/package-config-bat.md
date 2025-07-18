# Package Configuration: bat

**Generated:** {{timestamp}}  
**User:** {{username}}  
**Location:** {{location}}  
**Package Version:** {{package_version}}

---

## 👀 bat Configuration

### 📋 Basic Settings
- **Command:** `bat`
- **Config File:** `~/.config/bat/config`
- **Themes Directory:** `~/.config/bat/themes`
- **Cache Directory:** `~/.cache/bat`

### ⚙️ Default Configuration
```bash
# Default bat configuration for uDOS
# Generated: {{timestamp}}

# Theme and appearance
--theme="Monokai Extended Bright"
--style="numbers,changes,header,grid"

# Paging behavior
--paging=always
--wrap=auto

# Language mappings
--map-syntax "*.ucode:Markdown"
--map-syntax "*.udos:Bash"
--map-syntax "Dockerfile.*:Dockerfile"
--map-syntax ".ignore:Git Ignore"
```

### 🎨 Theme Customization
```bash
# uDOS custom theme settings
# Add to ~/.config/bat/config

# For dark terminals
--theme="Dracula"

# For light terminals  
--theme="GitHub"

# High contrast
--theme="base16"
```

### 🎯 uDOS Integration

#### Shortcode Commands
- **[view:file.md]** - View file with syntax highlighting
- **[cat:script.sh]** - Display script with line numbers
- **[preview:document.md]** - Preview with paging

#### uCode Integration
```bash
# View uDOS files
bat --language=markdown {{file_path}}

# View logs with timestamps
bat --style=plain --color=always {{log_file}} | grep "{{search_term}}"

# Compare files
bat --diff {{file1}} {{file2}}
```

### 🔧 Custom Functions
```bash
# Add to ~/.zshrc or ~/.bashrc

# Quick uDOS file viewer
function batudos() {
    if [[ -f "$UHOME/$1" ]]; then
        bat "$UHOME/$1"
    else
        find "$UHOME" -name "*$1*" -type f | head -5 | xargs bat
    fi
}

# View with custom pager
function batless() {
    bat --paging=always --pager="less -RF" "$@"
}

# Syntax highlighting for unknown files
function batguess() {
    local lang=$(file --mime-type "$1" | awk '{print $2}' | cut -d'/' -f2)
    bat --language="$lang" "$1"
}
```

### 📊 Performance Settings
```bash
# For large files
--line-range=1:100
--tabs=4

# Memory optimization
--italic-text=always
--decorations=always
```

### 🎮 Integration with Other Tools
```bash
# With ripgrep
function rg-bat() {
    rg --line-number --color=never "$1" | 
    while IFS=: read -r file line content; do
        echo "==> $file <=="
        bat --style=plain --color=always --highlight-line="$line" "$file"
        echo
    done
}

# With fzf for file preview
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=header,grid --line-range :300 {}'"
```

### 🔧 Language Extensions
```bash
# Custom syntax definitions
# Add to ~/.config/bat/syntaxes/

# uDOS specific file types
*.ucode -> Markdown
*.udos -> Bash
*.utemplate -> Mustache
*.umemory -> YAML
```

---

## 📈 Monitoring & Maintenance

### Health Checks
- **[package:status bat]** - Check installation status
- **[view:benchmark]** - Performance testing

### Configuration Management
- **[package:config bat]** - Show current configuration
- **[package:themes bat]** - List available themes

---

*Configuration managed by uDOS Package System v2.0.0*
