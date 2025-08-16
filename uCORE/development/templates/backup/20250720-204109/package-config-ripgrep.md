# Package Configuration: ripgrep (rg)

**Generated:** {{timestamp}}  
**User:** {{username}}  
**Location:** {{location}}  
**Package Version:** {{package_version}}

---

## 🔍 ripgrep Configuration

### 📋 Basic Settings
- **Command:** `rg`
- **Config File:** `~/.ripgreprc`
- **Data Directory:** `~/.cache/ripgrep`

### ⚙️ Default Configuration
```bash
# Default ripgrep configuration for uDOS
# Generated: {{timestamp}}

# Search behavior
--smart-case
--follow
--hidden

# Output formatting
--line-number
--column
--color=always
--heading

# File type associations
--type-add=ucode:*.md,*.ucode
--type-add=udos:*.udos,*.uds

# Ignore patterns
--glob=!.git/*
--glob=!node_modules/*
--glob=!target/*
--glob=!build/*
--glob=!dist/*
--glob=!*.log
--glob=!*.tmp
```

### 🎯 uDOS Integration

#### Shortcode Commands
- **[search:text query]** - Search text across uDOS
- **[search:file pattern]** - Find files by pattern
- **[search:code function_name]** - Search code patterns

#### uCode Integration
```bash
# Search uDOS scripts
rg --type ucode "function.*{{function_name}}"

# Search documentation
rg --type md "{{search_term}}" uDOS/docs/

# Search templates
rg --type md "{{template_var}}" uDOS/uTemplate/
```

### 🔧 Custom Aliases
```bash
# Add to ~/.zshrc or ~/.bashrc
alias rgu='rg --type ucode'
alias rgm='rg --type md'
alias rgudos='rg --glob "*.{md,ucode,udos,sh}"'
alias rgfast='rg --no-heading --no-line-number'
```

### 📊 Performance Tuning
```bash
# For large repositories
--max-filesize=10M
--max-columns=500
--max-count=100

# Memory optimization
--mmap

# Threading (auto-detected)
--threads={{cpu_cores}}
```

### 🎮 Interactive Usage
```bash
# Fuzzy search integration
function rg-fzf() {
    rg --color=always --line-number --no-heading --smart-case "${*:-}" |
    fzf --ansi \
        --color "hl:-1:underline,hl+:-1:underline:reverse" \
        --delimiter : \
        --preview 'bat --color=always {1} --highlight-line {2}' \
        --preview-window 'up,60%,border-bottom,+{2}+3/3,~3'
}
```

---

## 📈 Monitoring & Maintenance

### Health Checks
- **[package:status ripgrep]** - Check installation status
- **[search:benchmark]** - Performance testing

### Update Management
- **[package:update ripgrep]** - Update to latest version
- **[package:config ripgrep]** - Reload configuration

---

*Configuration managed by uDOS Package System v2.0.0*
