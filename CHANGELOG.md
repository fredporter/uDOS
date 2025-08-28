# Changelog

All notable changes to uDOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4.3] - 2025-08-28

### 🎨 **Template System Integration & Self-Healing**

#### Added
- **Advanced Template Engine**: Complete template processing with conditionals and variable formatting
  - `{#if USER-LEVEL:number >= X}` role-based content filtering
  - `{#if DEV-MODE}` development-specific sections
  - `{USER-ROLE:title}`, `{USER-LEVEL:number}` formatted variables
  - Template inheritance support with `{#extend}` processing
- **Comprehensive Self-Healing System**: NetHack-inspired automatic dependency resolution
  - Platform-aware package management (Debian/Fedora/Arch/macOS/Windows)
  - Python environment auto-recovery with venv validation
  - Node.js/desktop dependency healing
  - Retry mechanisms with attempt limiting and exponential backoff
  - Humorous NetHack-style error messages for user engagement
- **Enhanced Command Router v1.0.4.3**: Template rendering integration
  - `[TEMPLATE|RENDER*name]` command for manual template processing
  - `[STATUS|DASHBOARD]` with dynamic template-driven dashboards
  - Template listing and management commands
  - Error handling with graceful fallbacks

#### Enhanced
- **Dynamic Content Generation**: Real-time dashboards with live system status
- **Role-Based Help System**: Context-aware command references showing appropriate commands
- **Level-Gated Features**: Progressive feature disclosure (10, 20, 40, 60, 80, 100+ levels)
- **Development Mode Integration**: Special template sections for development workflows
- **Variable System**: Enhanced with template-aware variable formatting and substitution

#### Technical Improvements
- **Template Processing Pipeline**: Multi-stage rendering with conditional processing
- **Self-Healing Integration**: All startup scripts include dependency health checks
- **Platform Detection**: Enhanced cross-platform compatibility for self-healing
- **Error Recovery**: Automatic retry logic with user-friendly failure messages
- **Logging Enhancement**: Comprehensive self-healing activity tracking

#### User Experience
- **NetHack-Style Messages**: Entertaining error feedback ("You cast 'summon python'")
- **Progressive Disclosure**: Users only see features appropriate to their level
- **Context-Aware Help**: Help system adapts to user role and development mode
- **Real-Time Updates**: Templates render with current system state

## [1.0.4.2] - 2025-08-28

### 🔄 **Self-Healing Foundation & Template Preparation**

#### Added
- **Dependency Healer**: Initial self-healing system implementation
- **Template Engine Foundation**: Basic template rendering capabilities
- **Enhanced Variable Management**: Improved variable system for template integration

## [1.0.4] - 2025-08-26

### 🔄 **Development Workflow Enhancement**

#### Added
- **ASSIST Mode Implementation**: High-efficiency development workflow for AI collaboration
- **Session Management**: Comprehensive session tracking and finalization
- **Git Workflow Integration**: Streamlined commit and push procedures
- **Development Environment**: Enhanced native setup with unified activation scripts
- **VS Code Task System**: Complete task integration for development operations
- **Documentation Consolidation**: Improved guides and development patterns

#### Enhanced
- **Build System**: Core system development and testing capabilities
- **Extension Organization**: Better separation of core, platform, and user extensions
- **Environment Management**: Unified activation with proper dependency handling
- **Development Scripts**: Improved setup and maintenance automation

#### Philosophy Alignment
- **Version Discipline**: Corrected version inflation - staying at v1.0.4 per uDOS philosophy
- **Descriptive Naming**: Focus on meaningful build names over version increments
- **Foundation First**: Building solid v1.0.4 capabilities before advancing versions

## [1.0.4.1] - 2025-08-26

### �️ **Foundational System Design**

#### Added
- **Core Architecture**: Clean separation between system code (uCORE), workspace (sandbox), and archive (uMEMORY)
- **Role-Based Access**: 8-tier hierarchy from Ghost (10) to Wizard (100) with appropriate permissions
- **Three-Mode Display**: CLI Terminal, Desktop Application, Web Export based on role access
- **Development Environment**: Protected `/dev` workspace for core development (Wizard + DEV mode only)
- **Extension System**: Modular components organized by access level (core/platform/user)
- **Documentation Standards**: Comprehensive style guide with ASCII art and naming conventions
- **Data Management**: uDATA format with JSON-based configuration and structured templates
- **VS Code Integration**: Complete task system and development environment setup
- **AI Assistant Context**: GitHub Copilot instructions for maintaining consistency

#### Philosophy
- **Simple, Lean, Fast**: Foundational approach without over-engineering
- **Data Separation**: Clear boundaries between system, workspace, and archive
- **Version Control**: Consistent v1.0.4.1 approach across all components
- **Clean Distribution**: Proper separation of development tools vs user content
- **Sustainable Growth**: Structured for expansion without complexity bloat

#### Core Components
- **uCORE**: System code and essential components
- **sandbox**: Active workspace with session archiving
- **uMEMORY**: Permanent archive with role isolation
- **uNETWORK**: Display and networking services
- **uSCRIPT**: Script execution engine with virtual environment support
- **extensions**: Modular extension system with registry

### 🔧 **Technical Foundation**

#### **Data Organization**
- **Workspace Flow**: Work in sandbox → Archive in uMEMORY → System in uCORE
- **Logging**: Centralized logging in `sandbox/logs/` with organized categories
- **Session Management**: Automatic archiving before sandbox flush

#### **Development Framework**
- **Access Control**: Wizard + DEV mode required for core development
- **Template System**: Standardized templates for extensions and configurations
- **Build System**: Automated build and test scripts for core system
- **Documentation**: Single source of truth with cross-referenced guides

#### **Security Model**
- **Role Isolation**: Separate permissions and data spaces for each role
- **Script Safety**: Controlled execution environment with virtual environments
- **Extension Registry**: Centralized management of system extensions

---

## Future Roadmap

### Planned Development (v1.0.x)
- Enhanced role-based features
- Extension ecosystem growth
- Cross-platform compatibility improvements
- Community template contributions

### Long-term Vision (v1.1+)
- Advanced networking capabilities
- Mobile companion applications
- Enterprise collaboration features
- Community-driven extension marketplace

---

*For detailed technical information, see the documentation in `docs/`*

*For support and contributions, visit: https://github.com/fredporter/uDOS*
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
