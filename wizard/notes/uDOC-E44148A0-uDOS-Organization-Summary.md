# uDOS v1.3 System Organization & Style Summary

## Overview

This document provides a comprehensive summary of uDOS v1.3 organizational structure, style guidelines, file naming conventions, and sharing protocols.

## 📁 Current Directory Structure

### Top-Level Organization (11 Core Folders)
```
uDOS/
├── docs/           # Documentation and architecture guides
├── extension/      # VS Code extension development  
├── install/        # Installation scripts and setup
├── sandbox/        # User workspace and development area
├── uCode/          # Core development utilities
├── uCORE/          # Core system architecture (main system)
├── uExtensions/    # Extension registry and AI integrations
├── uInstall/       # Installation configurations
├── uMEMORY/        # User memory and data management (gitignored)
├── uTemplate/      # Global template system
└── wizard/         # Development workflow tools (renamed from uDEV)
```

### Key Organizational Principles

#### **Security Model**
- **Public Repository**: Core system, documentation, tools, templates
- **Private/Local Only**: User data (uMEMORY/), logs, personal configs (.vscode/)
- **Git Exclusions**: Personal data never committed to repository

#### **Functional Separation**
- **Core System** (`uCORE/`): Foundational architecture and utilities
- **Development** (`wizard/`): Workflow tools and development automation
- **User Space** (`sandbox/`, `uMEMORY/`): Personal workspace and data
- **Extensions** (`uExtensions/`): Modular plugin architecture
- **Documentation** (`docs/`): All guides, standards, and architecture

## 🏷️ File Naming Conventions (v1.3)

### Core Naming Standard: CAPS-NUMERIC-DASH

#### **Universal File Format**
```
uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md
```

**Components:**
- `uTYPE`: File type prefix (uSCRIPT, uLOG, uDATA, uDOC, etc.)
- `YYYYMMDD`: ISO date format
- `HHMM`: 24-hour time format
- `TTZ`: 2-digit timezone code (from uDOS timezone dataset)
- `MMLLNN`: Enhanced location code (Map+Location+Number)

#### **File Type Prefixes**
- `uSCRIPT` - Executable scripts and automation
- `uLOG` - System and user activity logs
- `uDATA` - Data files and datasets
- `uDOC` - Documentation and guides
- `uMISSION` - Mission and project files
- `uLEGACY` - Historical and archived content
- `uCONFIG` - Configuration files
- `uTEMPLATE` - Template definitions
- `uREPORT` - Generated reports

#### **Special Files (No timestamp)**
- `README.md` - Repository documentation
- `CHANGELOG.md` - Version history
- `LICENSE` - Legal documentation
- `repo_structure.txt` - Generated structure documentation

### Examples
```
uSCRIPT-20250817-1640-28-00SY43.md  # Script in Sydney (AEDT)
uLOG-20250817-0930-02-00NY12.md     # Log in New York (EST)
uDATA-20250817-1500-08-00BE12.md    # Data in Berlin (CET)
```

## 🌍 Timezone & Location System

### Timezone Codes (38 Standard Codes)
| Code | Zone | UTC Offset | Primary Cities |
|------|------|------------|----------------|
| 02 | EST | -05:00 | New York, Toronto |
| 08 | CET | +01:00 | Berlin, Paris, Madrid |
| 23 | JST | +09:00 | Tokyo |
| 28 | AEDT | +11:00 | Sydney, Melbourne |
| 38 | UTC | ±00:00 | Coordinated Universal |

### Location Codes (MMLLNN Format)
- `MM`: Map number (00-99)
- `LL`: Location letters (A-Z, 2 chars)  
- `NN`: Tile number (01-99)

**Examples:**
- `00SY43` - Map 00, Sydney, Tile 43
- `00NY12` - Map 00, New York, Tile 12
- `05DR01` - Map 05, Dragon's Lair, Tile 01

## 🎨 Typography & Style Standards

### Capitalization Rules

#### **ALL CAPS Usage**
- Commands: `STATUS`, `HELP`, `MEMORY`, `PACKAGE`
- File types: `uSCRIPT`, `uLOG`, `uDATA`
- Variables: `UDOS-USERNAME`, `CURRENT-MODE`
- Shortcodes: `[MEM|LIST]`, `[PACK|INSTALL]`
- Technical elements: All system identifiers

#### **Sentence Case Usage**
- Documentation text: "Your memory stores all data"
- User messages: "Welcome to the system"
- Descriptions: "This command shows status"

#### **Proper Case Usage**
- System name: "uDOS"
- Component names: "Memory Vaults", "Command Center"
- Technology names: "Markdown", "ASCII"

### Color Coding Standards
- **Commands**: YELLOW (`STATUS`, `HELP`, `MEMORY`)
- **Shortcodes**: CYAN brackets, YELLOW content (`[MEM|LIST]`)
- **Variables**: GREEN (`UDOS-USERNAME`, `CURRENT-MODE`)
- **File paths**: BLUE (`/Users/username/uDOS/`)
- **Success**: GREEN (`✅ Operation completed`)
- **Warning**: YELLOW (`⚠️ Confirmation required`)
- **Error**: RED (`❌ Command not found`)
- **Info**: CYAN (`ℹ️ Helpful information`)

## 📄 Template System Standards

### Template Organization
```
uTemplate/
├── library/           # Standardized templates
│   ├── documentation/ # Document templates
│   ├── system/        # System output templates
│   ├── ascii-art/     # ASCII components
│   └── formats/       # Output format templates
├── active/            # User workspace templates
└── generated/         # System-generated outputs
```

### Variable Syntax
```markdown
{{SYSTEM_NAME}}         # uDOS
{{VERSION}}             # Current version
{{DATE}}                # Current date
{{USER_NAME}}           # Current user
{{CUSTOM:project_name}} # User-defined variables
{{INPUT:description}}   # User input prompts
```

### ASCII Art Standards
```ascii
# Primary Logo (Large)
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

# Status Icons
✅ SUCCESS    ❌ ERROR      ⚠️ WARNING
🔄 LOADING    ⏸️ PAUSED     ▶️ RUNNING
```

## 🔧 Development Workflow Standards

### wizard/ Development Environment
- **tools/**: Script executors, file organizers, report generators
- **workflows/**: Automated development workflow definitions
- **vscode/**: VS Code integration configurations
- **logs/**: Development session logs (gitignored)

### Command Standards
```bash
# All commands in CAPS
STATUS          # Show system status
MEMORY          # Access memory system
PACKAGE         # Package management
CONFIG-SET      # Configuration management
DASH-LIVE       # Live dashboard
```

### Shortcode Format
```bash
[TYPE|ACTION]   # Standard shortcode format
[MEM|LIST]      # List memory contents
[PACK|INSTALL]  # Install package
[CONFIG|SET]    # Set configuration
```

## 📊 Sharing & Collaboration Structure

### Repository Sharing Model

#### **Public Repository (GitHub)**
✅ **Shared Content:**
- Core system architecture (`uCORE/`)
- Documentation and guides (`docs/`)
- Extension framework (`uExtensions/`)
- Installation tools (`install/`, `uInstall/`)
- Development utilities (`wizard/tools/`, `uCode/`)
- Template system (`uTemplate/`)
- Project structure documentation

#### **Private/Local Only**
🔒 **Never Shared:**
- User memory and personal data (`uMEMORY/`)
- Development session logs (`wizard/notes/`)
- Personal workspace files (`sandbox/user.md`)
- Editor configurations (`.vscode/`)
- Authentication tokens and credentials

### Collaboration Guidelines

#### **Contributing to Core System**
1. Follow strict naming conventions (CAPS-NUMERIC-DASH)
2. Use proper file type prefixes (uSCRIPT, uDOC, etc.)
3. Include timezone and location codes
4. Maintain ASCII art standards
5. Update documentation with changes

#### **Extension Development**
1. Use `uExtensions/` registry system
2. Follow modular architecture principles
3. Include proper VS Code integration
4. Document APIs and interfaces
5. Test with development workflow tools

#### **Documentation Standards**
1. Update `ARCHITECTURE.md` for structural changes
2. Use template system for consistency
3. Include cross-references and navigation
4. Generate structure with TREE command
5. Maintain style guide compliance

## 🚀 Automation & Tools

### TREE Command System
```bash
./generate_tree.sh    # Generate complete repository structure
```
**Output:** `repo_structure.txt` with comprehensive documentation

### Filename Generators
```bash
generate_udos_filename "SCRIPT" "28" "00SY43"
# Output: uSCRIPT-20250817-1640-28-00SY43.md
```

### Validation Tools
```bash
validate_location_code "00SY43"    # Validate location format
get_timezone_code "AEDT"           # Get timezone code
```

## 📋 Compliance Checklist

### File Naming Compliance
- [ ] File type prefix uses uTYPE format
- [ ] Date format is YYYYMMDD
- [ ] Time format is HHMM (24-hour)
- [ ] Timezone code is 2-digit (01-38)
- [ ] Location code is MMLLNN format
- [ ] File extension is .md
- [ ] No lowercase in technical elements
- [ ] No underscores or special characters (except dash)

### Content Standards
- [ ] Commands in ALL CAPS
- [ ] Variables use CAPS-DASH format
- [ ] Shortcodes use [TYPE|ACTION] format
- [ ] Descriptions in sentence case
- [ ] Proper timezone integration
- [ ] Valid location codes
- [ ] ASCII art compliance

### Repository Standards
- [ ] No personal data in public repository
- [ ] Proper .gitignore exclusions
- [ ] Documentation updates with changes
- [ ] Extension registry compliance
- [ ] Template system integration

## 🔄 Migration & Updates

### From Previous Versions
- Use automated migration scripts for filename updates
- Update timezone codes to 2-digit format
- Convert location codes to MMLLNN format
- Migrate ASCII art to standard library

### Ongoing Maintenance
- Regular TREE command execution for structure updates
- Quarterly style guide compliance reviews
- Extension registry updates
- Documentation consistency checks

---

## Summary

uDOS v1.3 implements a comprehensive organizational system with:

1. **Strict Naming Conventions**: CAPS-NUMERIC-DASH standard for all files
2. **Modular Architecture**: 11 core folders with clear separation of concerns
3. **Security Model**: Public/private separation with gitignore protection
4. **Template System**: Standardized templates with variable processing
5. **Development Workflow**: Automated tools and VS Code integration
6. **Documentation Standards**: Living architecture with automated structure generation

The system prioritizes **consistency**, **maintainability**, and **collaboration** while preserving the retro computing aesthetic that defines the uDOS experience.

---

*uDOS v1.3 System Organization Summary*  
*Generated: August 17, 2025*  
*For complete details, see individual style guides and architecture documentation*
