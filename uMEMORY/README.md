# uMEMORY - Centralized System Management & Data Archive

**Professional configuration management, asset repository, and personal data archive system with centralized uDOS architecture**

## Overview

The uMEMORY system provides centralized configuration management for the entire uDOS operating system. This professional architecture ensures consistent asset management, configuration, and system state across all uDOS modules while maintaining the original flat-like structure for user data.

## Directory Structure

```
uMEMORY/
├── system/                       # **Centralized System Data & Configuration**
│   ├── fonts/                    # Font management (simplified bundle)
│   │   ├── MODE7GX0.TTF          # BBC Mode 7 teletext font (primary)
│   │   ├── microknight.ttf       # C64-inspired pixel font
│   │   ├── pot_noodle.ttf        # Retro/BBS chunky pixel font
│   │   └── MANUAL-DOWNLOAD-REQUIRED.md  # Guide for additional fonts
│   ├── uDATA-colours.json        # Color palette system (uDATA format)
│   ├── uDATA-commands.json       # Command definitions (uDATA format)
│   ├── uDATA-shortcodes.json     # Shortcode system (uDATA format)
│   ├── uDATA-user-roles.json     # Role hierarchy system (uDATA format)
│   ├── uDATA-variable-system.json # System variables (uDATA format)
│   ├── uDATA-font-registry.json  # Font metadata and definitions
│   └── README.md                 # System data documentation
├── core/                         # Core memory templates and configs
├── templates/                    # Template repository for all uDOS components
├── user/                         # Personal user data and archives
│   ├── installation.md           # User installation tracking
│   ├── milestones/               # User milestone data
│   ├── missions/                 # User mission data
│   ├── moves/                    # User move tracking
│   └── README.md                 # User data documentation
├── role/                         # Role system documentation
├── logs/                         # System logs (organized by type)
│   ├── archived/                 # Archived log files
│   ├── daily/                    # Daily operational logs
│   ├── debug/                    # Debug and troubleshooting logs
│   ├── development/              # Development activity logs
│   ├── error/                    # Error logs
│   ├── session/                  # Session-specific logs
│   └── system/                   # System-level logs
├── identity.md                   # User identity and configuration
└── terminal_size.conf            # Terminal configuration
```

## Current System State (August 2025)

### Centralized uDATA System
All core system data is now stored in clean uDATA format (minified JSON, one record per line):
- **uDATA-colours.json** - Complete color palette system
- **uDATA-commands.json** - Core command definitions
- **uDATA-shortcodes.json** - Modern shortcode system
- **uDATA-user-roles.json** - 8-level role hierarchy (WIZARD→KNIGHT→SORCERER→CRYPT→IMP→DRONE→GHOST→TOMB)
- **uDATA-variable-system.json** - System variables and configuration
- **uDATA-font-registry.json** - Simplified font registry reflecting actual fonts

### Simplified Font Bundle (3 Core Fonts)
Essential retro/pixel fonts for uDOS operation:
- **MODE7GX0.TTF** - Primary BBC Mode 7 teletext font (18px, authentic)
- **microknight.ttf** - C64-inspired pixel font (14px, retro computing)
- **pot_noodle.ttf** - Chunky pixel font for headers/emphasis (18px)

Additional fonts available via manual installation (see MANUAL-DOWNLOAD-REQUIRED.md).

### Clean Architecture
- **Scripts moved to uCORE**: All .sh files relocated from uMEMORY to appropriate uCORE locations
- **Data-only uMEMORY**: Contains only data files, configurations, and assets
- **Organized logs**: Structured log directory with proper categorization
- **Role system**: Documented 8-level role hierarchy with capabilities

### Command Integration

The uDATA system integrates with uDOS command processing:

```bash
# Access system data through uCORE scripts
./uCORE/core/help-engine.sh              # Command help system
./uCORE/config/setup-vars.sh             # System variables (moved from uMEMORY)
./uCORE/bin/user-memory-manager.sh       # User memory utilities (moved from uMEMORY)

# Font management
ls uMEMORY/system/fonts/                  # View available fonts
cat uMEMORY/system/uDATA-font-registry.json  # Font metadata

# System data access
cat uMEMORY/system/uDATA-commands.json    # Core commands
cat uMEMORY/system/uDATA-colours.json     # Color palettes
cat uMEMORY/system/uDATA-user-roles.json  # Role hierarchy
```

## Core Data (`core/`)

Geographical, timezone, and location data:
- **City & Country Maps**: Global geographical mappings
- **Timezone Data**: Comprehensive timezone information
- **Currency & Language**: Localization reference data
- **Map Data**: Terrain and geographical visualization data
- **Validation Rules**: Geographic and timezone validation

## Templates (`templates/`)

Centralized template repository for all uDOS components:
- **Documentation Templates**: Markdown templates for consistent documentation
- **Interface Templates**: User interface and display templates
- **Development Templates**: Code and project development templates
- **Configuration Templates**: System and application configuration
- **Data Gathering Templates**: JSON-based template definitions (datagets)
- **System Configuration**: Template system integration and metadata
- **Examples & Variables**: Template usage examples and variable definitions

## Recent Improvements (August 2025)

### System Organization
- **Shell scripts relocated**: All .sh files moved from uMEMORY to uCORE (bin/, config/)
- **Clean data separation**: uMEMORY contains only data files and assets
- **Simplified font strategy**: Focused on 3 essential fonts instead of complex variants
- **uDATA standardization**: All system files converted to clean uDATA format

### Font System Simplification
- **Single MODE7 font**: MODE7GX0.TTF only (removed GX2, GX3, GX4 variants)
- **Essential bundle**: 3 core fonts sufficient for all uDOS operations
- **Manual expansion**: Additional fonts available via installation script
- **Clean registry**: Font metadata reflects actual available fonts

### Architecture Cleanup
- **Backup consolidation**: All backups moved to root /backup/ directory
- **Log organization**: Structured log directories by type and purpose
- **Role documentation**: Complete 8-level role system documented
- **Migration completion**: Legacy migration files archived

## Flat-Like Structure Principles

uMEMORY follows a flat-like organizational approach for user data:

### Direct Access
- All important files accessible at root or one level down
- Minimal deep nesting for better navigation
- Clear, descriptive directory names

### Hex Filename Convention
- Temporal-spatial organization where applicable
- 8-character hex encoding for timestamps
- Flat structure within directories

### Data Separation
- **System files**: Configuration, fonts, colors in system/
- **Data files**: JSON, MD, GeoJSON for user content
- **Scripts**: Processing scripts remain in uCORE
- **User content**: Personal files in user/ directory

## Privacy & Distribution

- **Included in git**: System data, configurations, templates, fonts, color palettes
- **Excluded from git**: Personal user data, archives, custom datasets
- **User isolation**: Personal content completely separated from system data

## Integration

uMEMORY integrates with:
- **uCORE**: Scripts access data files for processing
- **uCODE Interface**: Real-time configuration management through command system
- **CSS System**: Automatic font and color integration for web interfaces
- **Role system**: Permissions based on role-based directories
- **Template system**: Template definitions for consistent file creation
- **Backup system**: Automatic backup to role directories and sandbox

## Migration from Legacy

All system components have been successfully migrated and organized:

### Fonts Migration ✅
- **Centralized location**: All fonts moved to `uMEMORY/system/fonts/`
- **Simplified bundle**: 3 essential fonts (MODE7GX0.TTF, microknight.ttf, pot_noodle.ttf)
- **Installation script**: `dev/scripts/install-font-bundle.sh` for additional fonts
- **Updated references**: All CSS and configuration files updated

### uDATA Migration ✅
- **Clean filenames**: Removed date stamps from all system uDATA files
- **Consistent format**: All system data in proper uDATA format (minified JSON)
- **Reference updates**: All core scripts updated to use clean filenames
- **Smart input enhancement**: Multi-dataset support with uDATA parsing

### Script Organization ✅
- **Configuration scripts**: Moved to `uCORE/config/` (setup-vars.sh)
- **Utility scripts**: Moved to `uCORE/bin/` (user management tools)
- **Clean separation**: uMEMORY contains only data, uCORE contains executable code
- **Backup preservation**: All original files preserved in /backup/

---

*uMEMORY v2.1 (August 2025) - Clean, organized, and maintainable system data architecture*
