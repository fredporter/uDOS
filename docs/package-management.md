# uDOS Package Management System v2.0.0

**Version:** v2.0.0  
**Updated:** {{timestamp}}  
**System:** Enhanced Package Management with Shortcode Integration

---

## 🌀 Overview

The uDOS Package Management System v2.0.0 provides a unified, shortcode-integrated approach to managing external tools and dependencies. It combines traditional package installation with uDOS's template system and shortcode processor for seamless workflow integration.

---

## 🔧 Core Components

### 📦 Package Manager (`manager-enhanced.sh`)
- Enhanced package database with metadata
- Shortcode integration for all operations
- Template-based configuration management
- Comprehensive logging and error handling
- Category-based package organization

### 📋 Template System Integration
- Package-specific configuration templates
- Automatic config generation from templates
- Variable substitution and customization
- Integration with uDOS template processor

### ⚡ Shortcode Integration
All package operations available through shortcodes:
```bash
[package:list]                    # List all packages
[package:install ripgrep]         # Install specific package
[package:status bat]              # Check package status
[package:search markdown]         # Search packages
[pkg:install-all]                 # Shorthand for install all
```

---

## 📂 Package Categories

### 🔍 Search & Find Tools
- **ripgrep** (`rg`) - Fast text search
- **fd** (`fd`) - Fast file finder  
- **fzf** (`fzf`) - Fuzzy finder

### 👀 File Viewers & Displays
- **bat** (`bat`) - Syntax-highlighted file viewer
- **glow** (`glow`) - Terminal markdown renderer

### 🛠️ System Utilities
- **jq** (`jq`) - JSON processor
- **eza** (`eza`) - Modern ls replacement
- **delta** (`delta`) - Better diff viewer

### 🤖 AI & Intelligence Tools
- **gemini** (`gemini`) - Google Gemini CLI

### 🧭 Navigation & Movement
- **zoxide** (`zoxide`) - Smart cd command

---

## 🎯 Usage Examples

### Basic Package Operations
```bash
# List all packages
[package:list]

# List packages by category
[package:list search]
[package:list viewer]

# Install specific package
[package:install ripgrep]

# Install all packages
[package:install-all]

# Check package status
[package:status bat]

# Get detailed package info
[package:info glow]

# Search for packages
[package:search markdown]
[package:search json]
```

### Package Information & Management
```bash
# Show package categories
[package:categories]

# Show package registry
[package:registry]

# Update package
[package:update ripgrep]

# Remove package
[package:remove fd]

# Reinstall package
[package:reinstall bat]
```

### Integration with uDOS Workflow
```bash
# Use installed tools through shortcodes
[search:text "function.*process"]    # Uses ripgrep
[view:README.md]                     # Uses bat
[preview:docs/guide.md]              # Uses glow

# Combine with other shortcodes
[run:analyze-logs] && [view:results.txt]
```

---

## 📋 Configuration Management

### Template-Based Configuration
Each package can have a configuration template in `uTemplate/package-config-{package}.md`:

```markdown
# Package Configuration: {{package_name}}
**Generated:** {{timestamp}}
**User:** {{username}}

## Default Settings
{{default_config}}

## uDOS Integration
{{integration_commands}}
```

### Automatic Configuration
When a package is installed:
1. Installation script runs
2. Status is updated in registry
3. Configuration template is processed
4. Custom config file is created
5. Integration shortcuts are established

### Configuration Files Location
```
uMemory/packages/
├── installed/           # Installation status files
├── configs/            # Processed configuration files
├── cache/              # Package cache and temp files
└── registry.json       # Central package registry
```

---

## 🔧 Advanced Features

### Package Registry
JSON-based registry tracking:
- Package metadata and status
- Installation timestamps
- Version information
- Configuration paths
- Integration status

### Error Handling & Logging
- Comprehensive error logging
- Installation logs per package
- Status tracking and recovery
- Troubleshooting assistance

### Template Processing
- Variable substitution in configs
- Dynamic configuration generation
- User-specific customizations
- Location and timezone awareness

### Shortcode Extensions
Packages can register their own shortcodes:
```bash
# Ripgrep extensions
[search:code function_name]
[search:docs search_term]

# Bat extensions  
[view:file --theme dracula]
[cat:script --line-range 1:50]
```

---

## 🚀 Installation & Setup

### Initialize Package System
```bash
# First time setup
[package:list]                    # Creates registry and directories

# Install essential packages
[package:install ripgrep]
[package:install bat]
[package:install fd]

# Install all packages
[package:install-all]
```

### Verify Installation
```bash
# Check system status
[package:status]                  # Shows all package status
[check:packages]                  # System health check

# Test package functionality
[search:text "shortcode"]        # Test ripgrep
[view:README.md]                  # Test bat
```

---

## 📊 Monitoring & Maintenance

### Health Monitoring
```bash
# Package status overview
[package:list]

# Detailed status check
[package:status ripgrep]

# Search for issues
[package:search error]
```

### Update Management
```bash
# Check for updates
[package:update --check-all]

# Update specific package
[package:update ripgrep]

# Batch updates
[package:update-all]
```

### Troubleshooting
```bash
# View installation logs
[log:package install-ripgrep-*]

# Reset package configuration
[package:config ripgrep --reset]

# Reinstall problematic package
[package:reinstall fd]
```

---

## 🎮 Integration Examples

### With uScript System
```bash
# Create script that uses packages
[script:create search-tool automation]

# Script content uses:
# - ripgrep for searching
# - bat for displaying results
# - jq for processing JSON output
```

### With Dashboard System
```bash
# Package status in dashboard
[dashboard:generate] includes package health

# Monitor package usage
[dashboard:package-stats]
```

### With Mission System
```bash
# Include package requirements in missions
[mission:create name=analysis packages="ripgrep,jq,bat"]
```

---

## 🔮 Future Enhancements

### Planned Features
- **Custom Package Repositories** - Add external package sources
- **Dependency Management** - Automatic dependency resolution
- **Version Pinning** - Lock packages to specific versions
- **Package Profiles** - Predefined package sets for different use cases
- **Integration Testing** - Automated testing of package integrations

### Extensibility
- Plugin system for custom packages
- API for third-party package managers
- Template marketplace for configurations
- Community package sharing

---

## 📝 Developer Guide

### Adding New Packages
1. Add package to `PACKAGES` array in `manager-enhanced.sh`
2. Create installer script: `install-{package}.sh`
3. Create configuration template: `package-config-{package}.md`
4. Add shortcode integrations
5. Update documentation

### Creating Package Templates
```markdown
# Package Configuration: {{package_name}}
**Generated:** {{timestamp}}

## Configuration
{{package_config}}

## Integration
{{integration_commands}}
```

### Testing Package Integration
```bash
# Test installation
[package:install test-package]

# Test shortcode integration
[test-package:command]

# Verify configuration
[package:config test-package]
```

---

*uDOS Package Management System v2.0.0*  
*Enhanced with Shortcode Integration and Template Processing*  
*Documentation Path:* `docs/package-management.md`
