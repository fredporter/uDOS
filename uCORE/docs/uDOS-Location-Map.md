# uDOS Location Map & Directory Standards v1.2
**Comprehensive system mapping and location coding reference**

## 📋 Overview

This document provides the complete location coding system for uDOS components, enabling precise navigation and reference across the entire system architecture.

## 🗺️ Complete System Map

### [00-XX-XX] Root System & Configuration
```
[00-00-00] / (Root Directory)
├── [00-10-00] README.md                    # Main documentation
├── [00-11-00] CHANGELOG.md                 # Version history
├── [00-12-00] LICENSE                      # Licensing information
├── [00-20-00] RELEASE_NOTES_v1.2.md       # Current release
├── [00-21-00] CROSS_PLATFORM_LAUNCHER_SUMMARY.md
├── [00-30-00] Configuration files (.gitignore, etc.)
└── [00-40-00] Installation scripts (install, setup)
```

### [10-XX-XX] uCORE - Core System
```
[10-00-00] uCORE/ (Core System Root)
├── [10-10-00] launcher/                    # Cross-platform launcher
│   ├── [10-10-01] platform/macos/         # macOS launchers
│   ├── [10-10-02] platform/windows/       # Windows launchers  
│   ├── [10-10-03] platform/linux/         # Linux launchers
│   ├── [10-10-04] universal/              # Universal scripts
│   ├── [10-10-05] vscode/                 # VS Code integration
│   └── [10-10-06] assets/                 # Launcher assets
├── [10-20-00] code/                        # Core scripts
│   ├── [10-20-01] ucode.sh                # Main system script
│   ├── [10-20-02] setup.sh                # System setup
│   ├── [10-20-03] dash.sh                 # Dashboard generator
│   └── [10-20-04] destroy.sh              # System cleanup
├── [10-30-00] extensions/                  # System extensions
│   ├── [10-30-01] gemini/                 # Gemini integration
│   └── [10-30-02] registry.json           # Extension registry
├── [10-40-00] templates/                   # Core templates
├── [10-50-00] docs/                        # System documentation
│   ├── [10-50-01] uDOS-Markdown-Standard.md
│   ├── [10-50-02] Development-Guide.md
│   └── [10-50-03] User-Manual.md
├── [10-60-00] development/                 # Development tools
├── [10-70-00] installers/                 # Installation systems
└── [10-80-00] datasets/                   # Core datasets
```

### [20-XX-XX] uMEMORY - User Data
```
[20-00-00] uMEMORY/ (User Data Root)
├── [20-10-00] configs/                     # User configuration
│   ├── [20-10-01] identity.md             # User identity
│   └── [20-10-02] settings.json           # User settings
├── [20-20-00] templates/                   # User templates
├── [20-30-00] scripts/                     # User scripts
├── [20-40-00] datasets/                    # User datasets
├── [20-50-00] projects/                    # User projects
├── [20-60-00] extensions/                  # User extensions
├── [20-70-00] setup.sh                     # Memory setup script
└── [20-71-00] backup.sh                    # Memory backup script
```

### [30-XX-XX] uKNOWLEDGE - Knowledge Base
```
[30-00-00] uKNOWLEDGE/ (Knowledge Base Root)
├── [30-10-00] ARCHITECTURE.md             # System architecture
├── [30-20-00] knowledge-articles/         # Knowledge articles
└── [30-30-00] reference-materials/        # Reference docs
```

### [40-XX-XX] sandbox - User Workspace
```
[40-00-00] sandbox/ (User Workspace Root)
├── [40-10-00] user.md                      # User workspace
├── [40-20-00] scripts/                     # Script experiments
├── [40-30-00] drafts/                      # Draft documents
└── [40-40-00] experiments/                 # Testing area
```

## 📋 Component Classification

### Major Systems (XX-00-00)
- **00**: Root configuration and documentation
- **10**: uCORE - Core system components
- **20**: uMEMORY - User data and customization
- **30**: uKNOWLEDGE - Shared knowledge repository
- **40**: sandbox - User workspace and experimentation

### Component Categories (10-XX-00)
- **10**: Launcher and platform integration
- **20**: Core scripts and execution
- **30**: Extensions and modules
- **40**: Templates and scaffolding
- **50**: Documentation and guides
- **60**: Development tools and utilities
- **70**: Installation and setup systems
- **80**: Data and datasets

### Subcomponent Details (10-10-XX)
- **01**: Platform-specific implementations
- **02**: Cross-platform utilities
- **03**: Integration components
- **04**: Configuration and settings
- **05**: Assets and resources
- **06**: Testing and validation

## 🎯 Usage Guidelines

### Reference Format
```markdown
# In documentation
See [10-20-01] uCORE/code/ucode.sh for main system script

# In scripts
# Location: [10-10-04] uCORE/launcher/universal/start-udos.sh
# Dependencies: [10-10-04] detect-platform.sh
```

### Navigation Commands
```bash
# Use location codes for quick navigation
cd $(locate-code 10-20-00)  # Navigate to core scripts
find . -path "*[10-50-*]*"  # Find all documentation
```

### File Headers
```bash
#!/bin/bash
# Script Name - Brief Description
# Location: [XX-YY-ZZ] relative/path/to/script
# Dependencies: [XX-YY-ZZ] other-script.sh
```

## 📊 Directory Standards

### Naming Conventions
| Type | Pattern | Example | Location Code |
|------|---------|---------|---------------|
| **Core Directories** | `lowercase/` | `launcher/`, `code/` | [10-XX-00] |
| **User Directories** | `CamelCase/` | `uMEMORY/`, `uKNOWLEDGE/` | [20-00-00], [30-00-00] |
| **Platform Dirs** | `platform/os/` | `platform/macos/` | [10-10-01] |
| **Feature Dirs** | `feature-name/` | `cross-platform/` | [XX-XX-XX] |

### Script Standards
| Type | Pattern | Example | Location |
|------|---------|---------|----------|
| **Main Scripts** | `name.sh` | `ucode.sh`, `setup.sh` | [10-20-XX] |
| **Utility Scripts** | `action-target.sh` | `detect-platform.sh` | [10-10-04] |
| **User Scripts** | `user-action.sh` | `user-backup.sh` | [20-30-XX] |

### Documentation Standards
| Type | Pattern | Example | Location |
|------|---------|---------|----------|
| **Main Docs** | `README.md` | Component documentation | [XX-XX-00] |
| **Standards** | `uDOS-Name.md` | `uDOS-Markdown-Standard.md` | [10-50-01] |
| **Guides** | `Topic-Guide.md` | `Development-Guide.md` | [10-50-02] |
| **Summaries** | `TOPIC_SUMMARY.md` | `LAUNCHER_SUMMARY.md` | [00-21-00] |

## 🔄 Migration Guidelines

### Updating Existing Documentation
1. Add location codes to file headers
2. Update cross-references with location codes
3. Apply new naming conventions
4. Standardize emoji usage

### New Component Guidelines
1. Assign appropriate location code
2. Follow naming conventions
3. Include location in file headers
4. Document dependencies with location codes

## ✅ Validation Checklist

### For New Components
- [ ] Location code assigned and documented
- [ ] Follows naming conventions
- [ ] File header includes location
- [ ] Dependencies mapped with location codes
- [ ] Directory structure follows standards

### For Existing Components
- [ ] Location code added to documentation
- [ ] Cross-references updated
- [ ] Naming aligned with standards
- [ ] File headers updated
- [ ] Directory structure validated

This location mapping system provides precise navigation and clear organization across the entire uDOS ecosystem, enabling efficient development and maintenance.
