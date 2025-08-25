# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-08-25

### 🎯 **Major System Reorganization**

#### Added
- **Centralized Logging**: All system logs consolidated in `/sandbox/logs/`
- **Development Environment**: Structured `/dev` folder for wizard role development
- **AI Assistant Integration**: GitHub Copilot instructions and development context
- **VS Code Integration**: Development-specific configurations and tasks
- **Role-Based Access Control**: Enhanced DEV mode for core development
- **Build/Test Infrastructure**: Automated build and test scripts for core system
- **Development Templates**: Standardized templates for extensions and commands
- **Git Sync Strategy**: Selective synchronization for collaboration vs individual work

#### Changed
- **Data Separation**: uCORE contains only system code, sandbox contains active work
- **Logging Architecture**: All logging redirected from uMEMORY to sandbox
- **Directory Philosophy**: uMEMORY = filing cabinet, sandbox = active workspace
- **Development Workflow**: Core development in `/dev`, user experiments in `/sandbox`
- **System Scripts**: Updated error handler, smart input, and deployment manager for new log locations
- **Repository Structure**: Clean separation of system code vs user/development data

#### Removed
- **Development Bloat**: Cleaned up old development artifacts and empty directories
- **Redundant Documentation**: Consolidated DEV-MODE-INSTRUCTIONS.md into dev structure
- **Legacy Log Locations**: Migrated all logging from uMEMORY to sandbox
- **Versioned Filenames**: Removed version numbers from all filenames for clean distribution

#### Fixed
- **Git Repository Health**: Proper .gitignore patterns for development environments
- **Log Path References**: Updated all system scripts to use new sandbox log locations
- **Directory Structure**: Eliminated duplicate and empty directories
- **Documentation Consistency**: Single source of truth for development instructions

### 🔧 **Technical Improvements**

#### **Memory/Sandbox Reorganization**
- **Workflow**: Work in sandbox → Process in sandbox → File in uMEMORY
- **Logging**: All logs centralized in `sandbox/logs/` with organized categories
- **Compatibility**: Symlink `uMEMORY/logs` → `../sandbox/logs` for legacy references

#### **Development Framework**
- **Structure**: Organized dev folder with active/, scripts/, templates/, docs/
- **Access Control**: Wizard + DEV mode required for core development
- **AI Integration**: Copilot context and examples for consistent development
- **Build System**: Automated core system building and testing

#### **System Updates**
- **Error Handler**: Updated to use sandbox/logs/errors
- **Smart Input**: Logging redirected to sandbox/logs/system
- **Deployment Manager**: Log files moved to sandbox/logs/system

### 🐛 **Bug Fixes**
- Fixed logging placement issues (user data in system directories)
- Resolved directory organization inconsistencies
- Corrected git tracking patterns for development files
- Enhanced backward compatibility with symlinks

### 🛠️ **Breaking Changes**
- Log file locations moved (symlinks provide compatibility)
- Development environment structure reorganized
- Version numbers removed from filenames
- Enhanced git exclusion patterns

### 📋 **Migration Notes**
- Existing log references work via compatibility symlinks
- Development environments properly excluded from git
- All logging now flows through sandbox for session management
- uMEMORY reserved for permanent data archival only

## [1.3.3] - 2025-08-23

### 🧹 System Organization & Extension Architecture

#### Added
- **Extension Architecture**: Complete cross-platform extension system with core/user separation
- **CLI Server Enhancement**: Role-based access for GHOST/TOMB roles with command filtering
- **Component Registry**: JSON-based tracking system for core components
- **Clean Directory Structure**: Organized uCORE/code with essential components only
- **Testing Environment**: Enhanced sandbox/experiments with development tools

#### Changed
- **Extension Organization**: Moved from scattered structure to organized extensions/ folder
- **Smart-Input Classification**: Moved from user extension to core essential component
- **uSCRIPT Library**: Cleaned and organized script library with proper categorization
- **Component Location**: Core components now in uCORE/code instead of separate extensions
- **Package Management**: Moved development tools to sandbox/experiments for testing

#### Removed
- **Legacy UI Components**: Removed viewport-manager and ucode-ui (preparing for rebuild)
- **Empty Directories**: Cleaned up all empty folders throughout the system
- **Obsolete Packages**: Removed uSCRIPT packages folder, kept only testing modules
- **Duplicate Files**: Eliminated backup files and duplicate manager scripts
- **Legacy Extensions**: Archived old extension backup folders

#### Fixed
- **Registry Format**: Corrected JSON structure for component tracking
- **Path References**: Updated all system references to new component locations (uSERVER → uNETWORK/server)
- **Broken Symlinks**: Removed broken symlinks after directory reorganization
- **Installation Scripts**: Updated all launcher and setup scripts with correct paths
- **Documentation**: Aligned all README files with current clean structure

## [1.3.1] - 2024-08-22

### 🎨 Font System Optimization & Smart Input Enhancement

#### Added
- **System Font Integration**: Added 10 professional system fonts (Monaco, Menlo, SF Mono, Courier New, Consolas)
- **Programming Font Support**: Integrated Fira Code, JetBrains Mono, Source Code Pro
- **Smart Autocomplete System**: 50+ predefined commands with category-based suggestions
- **Enhanced uMEMORY Integration**: Direct resource loading from uMEMORY system
- **Progressive Startup Graphics**: 6-phase visual startup sequence with resource status
- **Real-time Status Updates**: Font, theme, and system status tracking in status bar
- **Professional UI Design**: Flat design with authentic retro computing aesthetics

#### Changed
- **Default Font**: MODE7GX3 → MODE7GX0 (more authentic BBC Mode 7 square aspect)
- **Font Library**: Streamlined from 11 to 11 fonts, but with better system integration
- **Command Suggestions**: Updated all font commands to reflect new font options
- **HTML Structure**: Cleaned up duplicate elements and optimized layout

#### Removed
- **Legacy Fonts**: Removed Amiga fonts (TOPAZ_A500, TOPAZ_A1200)
- **Commodore 64 Fonts**: Removed MICROKNIGHT font
- **Redundant Mode 7 Variants**: Removed MODE7GX2, MODE7GX3, MODE7GX4
- **Special Fonts**: Removed POT_NOODLE chunky display font
- **Temporary Files**: Cleaned up development artifacts and cache files

#### Fixed
- **UI Icon Handlers**: All emoji and dashboard icons now properly functional
- **Event Listeners**: Fixed onclick handlers and JavaScript function references
- **Status Bar Integration**: Added missing display-stat element for proper updates
- **Font Cycling**: Improved font switching with proper status updates
- **HTML Structure**: Removed duplicate command input containers and script sections

#### Technical Improvements
- **Performance**: Reduced font loading overhead with system font integration
- **Compatibility**: Better cross-platform font fallbacks
- **Maintenance**: Cleaner codebase with fewer external font dependencies
- **User Experience**: Keyboard navigation for autocomplete and command history

## [1.3.0] - 2025-08-17

### 🚀 Universal Device Operating System v1.3

#### Added
- **Modular Architecture**: Complete system refactor with ucode-modular.sh
- **Web Content Integration**: Full urltomarkdown system with Python converter
- **Package Management**: Hybrid distribution strategy with core/external separation
- **Filename Convention v3.0**: 8-character hex encoding with chronological sorting
- **External Package Organization**: Moved to wizard/experiments for better separation
- **Enhanced Documentation**: Updated all READMEs with proper naming conventions

#### Changed
- **System Name**: "Universal Data Operating System" → "Universal Device Operating System"
- **Package Structure**: Separated core packages from external dependencies
- **File Organization**: Applied hex filename convention across all documentation
- **Package Manager**: Renamed to package-manager.sh for simpler access

#### Fixed
- **Interactive Loop**: Resolved command prompt infinite loop issues
- **Terminal Handling**: Improved modular system with timeout detection
- **File References**: Updated all package manager references to new locations

## [1.1.0] - 2025-07-18

### 🗺️ Advanced Mapping System

#### Added
- **Multi-Dimensional Mapping**: Advanced geospatial visualization with 7+ virtual layers
- **Shortcode Templates**: Template-driven map creation with 20+ shortcode types
- **Projection Support**: Mercator, Robinson, and interactive 3D Orthographic globe
- **Temporal Navigation**: Historical playback, real-time updates, and predictive modeling
- **ASCII Visualization**: Enhanced data presentation with ASCII art blocks
- **Interactive Processor**: Complete shortcode extraction and JavaScript generation

#### Enhanced Logging System v2.1.0
- **Template Compliance**: Full integration with uDOS template standards
- **JSON Statistics**: Structured data collection with analytics
- **Progress Tracking**: Visual progress bars and completion metrics
- **Error Context**: Enhanced error logging with command context
- **Data Export**: Multiple format support (JSON, CSV, Markdown)
- **Auto-archival**: Automated cleanup of old log files

#### Documentation Updates
- **Roadmap Consolidation**: Moved from scattered roadmap folder to centralized docs
- **Template Standardization**: Updated all templates to v2.1.0 format
- **ASCII Integration**: Enhanced visual documentation with ASCII blocks
- **Shortcode Documentation**: Comprehensive shortcode reference guide

#### File Organization
- **Legacy Archival**: Moved redundant files to progress folder
- **Naming Compliance**: Updated file naming to match conventions
- **Structure Optimization**: Improved directory organization

### 📊 Enhanced Daily Tracking

#### Daily Notes v2.1.0
- **Shortcode Integration**: Activity tracking with structured shortcodes
- **Progress Visualization**: ASCII progress bars and activity dashboards
- **Objective Tracking**: Goal-oriented daily planning system
- **Performance Analytics**: Productivity scoring and trend analysis

#### Move Logging Enhancements
- **Metadata Enrichment**: Comprehensive move context and categorization
- **Performance Metrics**: Command timing and success rate tracking
- **Smart Categorization**: Automatic move type classification
- **Predictive Insights**: Pattern recognition and workflow optimization

### 🔧 Technical Improvements

#### Template Engine v2.1.0
- **Variable Substitution**: Dynamic content generation with {{variables}}
- **Conditional Logic**: Template branching and conditional rendering
- **Dataset Integration**: JSON dataset binding for dynamic content
- **Nested Shortcodes**: Hierarchical content structure support

#### Integration Framework
- **uDOS Ecosystem**: Seamless integration across all uDOS components
- **Dashboard Widgets**: Map and analytics dashboard integration
- **Memory System**: Configuration persistence in uMemory
- **Export Pipeline**: Multi-format data export capabilities

### 🌍 Mapping Framework Details

#### Virtual Layer Architecture
- **Atmosphere Layer** (+10km): Satellite imagery, weather patterns, aurora data
- **Aviation Layer** (+10km): Flight paths, air traffic control, no-fly zones
- **Cloud Layer** (+2km): Weather radar, precipitation, wind patterns
- **Surface Layer** (0m): Geography, cities, transportation networks
- **Subsurface Layer** (-100m): Underground infrastructure, utilities
- **Geological Layer** (-1km): Rock formations, mineral deposits, groundwater
- **Core Layer** (-6,371km): Seismic activity, tectonic plates, magnetic field

#### Shortcode System
- **Map Projections**: MAP_MERCATOR, MAP_ROBINSON, MAP_ORTHOGRAPHIC
- **Layer Controls**: LAYER_ATMOSPHERE, LAYER_SURFACE, LAYER_GEOLOGICAL
- **Data Visualization**: VIZ_CHOROPLETH, VIZ_POINTS, VIZ_FLOW, VIZ_HEATMAP
- **Timeline Controls**: TIMELINE_HISTORICAL, TIMELINE_REALTIME, TIMELINE_PROJECTION
- **Dataset Integration**: DATASET_REGISTRY, GEO_CONTEXT, LOCATION_HIERARCHY

### Breaking Changes
- **Log Format**: Move logs now use enhanced JSON structure
- **Template Version**: Templates require v2.1.0 compliance
- **File Naming**: Daily files follow YYYY-MM-DD format consistently

### Migration Guide
- Existing move logs remain compatible
- New features require template updates
- Archive old formats to progress folder

## [1.0.0] - 2025-07-18

### 🎉 First Production Release

**The world's first markdown-native operating system is now production ready!**

### Added

#### 🏗️ Core Architecture
- Complete 5-directory system structure (uCode, uMemory, uKnowledge, uScript, uTemplate)
- Four-tier user role system (wizard, sorcerer, ghost, imp) with granular permissions
- Privacy-first, local-first architecture with optional cloud sync
- Security model with proper separation of system and user files

#### 🤖 Chester AI Companion
- Personality-driven AI assistant with small dog characteristics
- Context-aware help and guidance system
- Integrated throughout uDOS experience
- Role-appropriate assistance for all user types

#### 📚 Complete Documentation Suite
- 11 comprehensive roadmap documents (001-011) covering entire system
- Architecture documentation and development guides
- Installation strategy and user role management
- Template system documentation

#### 💻 VS Code Integration
- Complete TypeScript extension with uScript language support
- 8 integrated commands for uDOS operations
- Custom themes, snippets, and syntax highlighting
- Workspace configuration with build tasks

#### 🛠️ Development Environment
- Comprehensive validation suite (52 validation points)
- Template generation system for all content types
- Automated setup and configuration scripts
- Rich debugging and logging capabilities

#### 📦 Distribution System
- Universal installer script for macOS/Linux
- macOS app bundle with DMG distribution
- GitHub release preparation with multiple package formats
- VS Code extension packaging and distribution

#### 🔒 Security & Privacy
- Local-first operation with no telemetry
- User role-based access controls
- Private user data separation (uMemory excluded from repo)
- Encryption-ready architecture

### Technical Features

#### 📄 Template System
- Standardized templates for missions, moves, milestones
- Dynamic template generation with variable substitution
- User-customizable template library
- Integration with VS Code snippets

#### 🚀 Automation Framework
- uScript scripting language for system automation
- Role-based script execution permissions
- Library of common automation patterns
- Integration with system commands

#### 📊 Monitoring & Analytics
- Comprehensive logging system
- Dashboard generation capabilities
- System health monitoring
- User activity tracking (privacy-respecting)

### Installation Options

- **Quick Install**: One-command curl installation
- **Manual Install**: Git clone and setup script
- **macOS App**: Native application bundle
- **Development**: Full source setup for contributors

### Browser Support

- Works with any markdown-aware text editor
- Optimized for VS Code with custom extension
- Terminal-based interface for headless systems
- Future web interface planned

### System Requirements

- **OS**: macOS 10.15+ or Linux
- **Dependencies**: Git, Bash, curl
- **Recommended**: VS Code, Node.js for optimal experience
- **Storage**: ~50MB for base installation

### Breaking Changes

- None (first release)

### Security

- No known vulnerabilities
- Privacy-first architecture
- Local data sovereignty
- Role-based access controls

### Performance

- Lightweight installation (~50MB)
- Fast startup and operation
- Efficient file organization
- Minimal system resource usage

---

## Development History

### Pre-Release Development (2024-2025)

#### Major Milestones
- **Foundation Phase**: Core architecture and design principles
- **Implementation Phase**: System scripts and automation
- **Integration Phase**: VS Code extension and tooling
- **Documentation Phase**: Complete roadmap and user guides
- **Distribution Phase**: Packaging and release preparation

#### Key Contributors
- Fred Porter - Creator and lead developer
- Chester AI - Companion system design and personality

#### Community
- Built for the markdown community
- Open source MIT license
- Welcoming contributor environment

---

## Future Roadmap

### Planned Features (v1.1+)
- Web interface for browser-based access
- Mobile companion applications
- Enhanced AI capabilities and integrations
- Plugin ecosystem and marketplace
- Advanced automation and workflow tools

### Long-term Vision
- Universal markdown-native computing platform
- Cross-platform compatibility and sync
- Community-driven extension ecosystem
- Enterprise and team collaboration features

---

**For detailed technical information, see the roadmap documents in `docs/roadmap/`**

**For support and contributions, visit: https://github.com/fredporter/uDOS**
