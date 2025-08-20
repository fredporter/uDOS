# uDOS v1.3 Repository Structure

**Generated:** August 17, 2025  
**Status:** Current modular architecture after v1.3 implementation  
**Key Update:** Complete modular system with Visual Basic-style uCode scripts

## 🌳 Complete Directory Tree

```
uDOS/
├── 📄 CHANGELOG.md                              # Version history and updates
├── 📄 LICENSE                                   # Software license
├── 📄 README.md                                 # Main project documentation
├── 📄 repo_structure.txt                        # Legacy structure documentation
├── 📄 repo_structure_v1.3.txt                   # ⭐ NEW: Current structure v1.3
│
├── 📁 docs/                                     # System Documentation
│   ├── 📝 Adventure.md
│   ├── 📝 ARCHITECTURE.md
│   ├── 📝 ASCII-Gallery.md
│   ├── 📝 Filename-Convention.md               # ✅ Hex naming standard
│   ├── 📝 Markdown-Spec.md
│   ├── 📝 PROJECT-PLANNING.md
│   ├── 📝 README.md
│   ├── 📝 ROADMAP.md
│   ├── 📝 Smart-Input-System.md
│   ├── 📝 Style-Guide.md
│   ├── 📝 Template-Standard.md
│   ├── 📝 uDOS-Concepts-v1.3.md               # ✅ Updated with hex logging
│   ├── 📝 uSCRIPT-System.md
│   └── 📝 USER-GUIDE.md
│
├── 📁 extensions/                              # System Extensions
│   ├── 📄 README.md
│   └── 📁 gemini/                              # Gemini AI Integration
│       ├── 📄 manifest.json
│       ├── 🔧 udos-gemini.sh
│       ├── 🔧 ucode-commands.sh
│       ├── 📁 context/
│       ├── 📁 gemini/
│       ├── 📁 profiles/
│       │   └── 📁 sorcerer/
│       └── 📁 reasoning/
│           ├── 📁 drone/
│           ├── 📁 ghost/
│           └── 📁 imp/
│
├── 📁 install/                                 # Installation & Role Management
│   ├── 🔧 create-drone-installation.sh        # Installation scripts
│   ├── 🔧 create-master-wizard.sh
│   ├── 🔧 create-ubuntu-public.sh
│   ├── � manage-installations.sh             # Role management tool
│   │
│   └── 📁 roles/                               # Multi-Installation Architecture
│       ├── 📄 wizard -> ../../wizard          # Symlink to wizard environment
│       ├── 📄 README.md
│       │
│       ├── 📁 drone/                           # Level 40 - Task Automation
│       │   ├── 📄 README.md
│       │   ├── 📁 operation-logs/
│       │   ├── 📁 scheduler/
│       │   └── 📁 task-automation/
│       │
│       ├── 📁 ghost/                           # Level 10 - Demo Installation  
│       │   ├── 📄 README.md
│       │   ├── 📁 demo-interface/
│       │   ├── 📁 public-docs/
│       │   └── 📁 temp-sandbox/
│       │
│       ├── 📁 imp/                             # Level 60 - Developer Tools
│       │   ├── 📄 README.md
│       │   ├── 📁 script-editor/
│       │   ├── 📁 template-manager/
│       │   └── 📁 user-projects/
│       │
│       ├── 📁 sorcerer/                        # Level 80 - Advanced Management
│       │   ├── 📄 README.md
│       │   ├── 📁 advanced-tools/
│       │   ├── 📁 project-manager/
│       │   └── 📁 user-admin/
│       │
│       └── 📁 tomb/                            # Level 20 - Archive Management
│           ├── 📄 README.md
│           ├── 📁 archive-browser/
│           ├── 📁 backup-manager/
│           └── 📁 historical-data/
│
├── 📁 sandbox/                                 # Development & Testing
│   ├── 📄 user.md
│   │
│   ├── 📁 archived-tests/                      # Cleaned up test deployments
│   │   └── 📁 drone-test-20250817/            # Archived drone test
│   │       ├── 📁 .drone/
│   │       │   ├── 📁 config/
│   │       │   ├── 📁 logs/
│   │       │   └── 📁 status/
│   │       ├── 📁 docs/
│   │       ├── 📁 install/
│   │       ├── 📁 uCode/
│   │       ├── 📁 uMemory/
│   │       │   ├── 📁 active/
│   │       │   ├── 📁 archive/
│   │       │   └── 📁 templates/
│   │       └── 📁 uTemplate/
│   │           ├── 📁 datagets/
│   │           ├── 📁 drone/
│   │           ├── 📁 examples/
│   │           ├── 📁 forms/
│   │           ├── 📁 location/
│   │           ├── 📁 mapping/
│   │           ├── 📁 system/
│   │           ├── 📁 user/
│   │           └── 📁 variables/
│   │
│   ├── 📁 drafts/
│   ├── 📁 experiments/
│   │
│   ├── 📁 scripts/                             # Development Scripts
│   │   ├── 📄 README.md
│   │   ├── 📄 test-layout.us
│   │   ├── 🔧 uscript.sh
│   │   ├── 📁 active/
│   │   └── 📁 executed/
│   │
│   ├── 📁 tasks/                               # Task Management
│   │   ├── 📄 README.md
│   │   ├── 📁 assist-mode/
│   │   ├── 📁 completed/
│   │   ├── 📁 in-progress/
│   │   └── 📁 templates/
│   │
│   └── 📁 user/                                # User Sandbox
│       ├── 📄 README.md
│       └── 📁 .ssh/
│
├── 📁 shared/                                  # Shared Resources
│   ├── 📁 configs/
│   ├── 📁 permissions/                         # Role-based permissions
│   │   ├── 📄 drone-permissions.json
│   │   ├── 📄 ghost-permissions.json
│   │   ├── 📄 imp-permissions.json
│   │   ├── 📄 sorcerer-permissions.json
│   │   ├── 📄 tomb-permissions.json
│   │   └── 📄 wizard-permissions.json
│   └── 📁 resources/
│
├── 📁 uCORE/                                   # Core System Engine
│   ├── 📄 README.md
│   │
│   ├── 📁 code/                                # Core Code Systems
│   │   ├── 🔧 dash.sh
│   │   ├── 🔧 destroy.sh
│   │   ├── 🔧 log.sh
│   │   ├── 📄 README.md
│   │   ├── 🔧 setup.sh
│   │   ├── 🔧 smart-input.sh
│   │   ├── 🔧 ucode-modular.sh                # Modular uCODE shell
│   │   ├── 🔧 ucode.sh                        # Original uCODE shell
│   │   ├── 📁 micro-syntax/
│   │   └── 📁 packages/
│   │       ├── 📁 ascii-generator/
│   │       └── 📁 nethack/
│   │
│   ├── 📁 datasets/                            # Core Datasets
│   │   ├── 📁 mapping/
│   │   │   ├── 📁 map-output/
│   │   │   │   └── 📁 js/
│   │   │   └── 📁 maps/
│   │   └── 📁 src/
│   │       ├── 📁 data/
│   │       ├── 📁 templates/
│   │       └── 📁 utils/
│   │
│   ├── 📁 launcher/                            # Application Launchers
│   │   ├── 📁 assets/
│   │   ├── 📁 platform/
│   │   │   ├── 📁 linux/
│   │   │   ├── 📁 macos/
│   │   │   └── 📁 windows/
│   │   ├── 📁 uDOS.app/                       # macOS App Bundle
│   │   │   └── 📁 Contents/
│   │   │       ├── 📁 MacOS/
│   │   │       └── 📁 Resources/
│   │   ├── 📁 universal/
│   │   └── 📁 vscode/
│   │
│   └── 📁 templates/                           # Core Templates
│       ├── 📄 daily-move-log-v2.md           # Enhanced move logging
│       ├── 📁 datagets/
│       ├── 📁 examples/
│       ├── 📁 system/
│       └── 📁 variables/
│
├── 📁 uKNOWLEDGE/                              # Knowledge Base
│   └── 📄 README.md
│
├── 📁 uMEMORY/                                 # User Memory System
│   ├── 📄 001-welcome-mission.md
│   ├── 📄 identity.md
│   ├── 📄 natural-language-sample.md
│   ├── 📄 README.md
│   ├── 🔧 setup-vars.sh
│   ├── 🔧 setup.sh
│   ├── 📄 terminal_size.conf
│   │
│   ├── 📁 .backup/
│   │
│   ├── 📁 datagets/                           # Data Processing
│   │   ├── 📁 active/
│   │   ├── 📁 completed/
│   │   ├── 📁 drafts/
│   │   └── 📁 templates/
│   │
│   ├── 📁 datasets/                           # User Datasets
│   │   └── 📁 mapping/
│   │       └── 📁 map-05/
│   │           ├── 📁 locations/
│   │           └── 📁 tiles/
│   │
│   ├── 📁 logs/                               # Activity Logs
│   │   ├── 📁 explicit/
│   │   │   ├── 📁 daily/
│   │   │   └── 📁 movelog/
│   │   └── 📁 public/
│   │
│   ├── 📁 milestones/                         # Progress Tracking
│   │   ├── 📁 explicit/
│   │   └── 📁 public/
│   │
│   ├── 📁 missions/                           # Mission Files (uMIS-HEXCODE-*.md)
│   │   ├── 📁 explicit/
│   │   └── 📁 public/
│   │
│   ├── 📁 moves/                              # Move Files (uMOV-HEXCODE-*.md)
│   │   ├── 📁 explicit/
│   │   └── 📁 public/
│   │
│   ├── 📁 scripts/                            # User Scripts
│   │   ├── 📁 explicit/
│   │   └── 📁 public/
│   │
│   ├── 📁 templates/                          # User Templates
│   │   ├── 📁 explicit/
│   │   └── 📁 public/
│   │
│   └── 📁 user/                               # User-specific Files
│       ├── 📁 explicit/
│       └── 📁 public/
│
├── 📁 uSCRIPT/                                # Script Execution Engine
│   ├── 📄 README.md
│   ├── 📄 test-layout.us
│   ├── 🔧 uscript.sh
│   │
│   ├── 📁 active/                             # Currently executing scripts
│   ├── 📁 config/                             # Script configurations
│   ├── 📁 executed/                           # Completed script logs
│   │
│   ├── 📁 extensions/                         # Script Extensions
│   │   ├── 🔧 extensions.sh                  # Extension manager
│   │   ├── 📄 registry.json                  # Extension registry
│   │   ├── 🔧 deployment-manager.sh          # Deployment extension
│   │   ├── 🔧 smart-input-enhanced.sh        # Enhanced input system
│   │   └── 📁 templates/
│   │       └── 📁 drone/
│   │
│   ├── 📁 library/                            # Script Library
│   │   ├── 📁 automation/
│   │   ├── 📁 javascript/
│   │   ├── 📁 python/
│   │   ├── 📁 shell/
│   │   ├── 📁 ucode/                          # ⭐ Visual Basic-style uCode scripts (v1.3)
│   │   │   ├── 📄 DASH.ucode                  # Interactive dashboard system
│   │   │   ├── 📄 DEV.ucode                   # Development tools and testing
│   │   │   ├── 📄 LOG.ucode                   # Intelligent logging system
│   │   │   ├── 📄 MEMORY.ucode                # Memory management and search
│   │   │   ├── 📄 MISSION.ucode               # Mission control and tracking
│   │   │   ├── 📄 PACKAGE.ucode               # Package management system
│   │   │   ├── 📄 PANEL.ucode                 # System control panel
│   │   │   ├── 📄 RENDER.ucode                # Visual rendering and ASCII art
│   │   │   └── 📄 TREE.ucode                  # Repository structure generator
│   │   └── 📁 utilities/
│   │
│   ├── 📁 registry/                           # Script Registry
│   │   ├── 📁 dependencies/
│   │   └── 📁 versions/
│   │
│   ├── 📁 runtime/                            # Runtime Environment
│   │   ├── 📁 engines/
│   │   ├── 📁 logs/
│   │   └── 📁 sandbox/
│   │
│   └── 📁 templates/                          # Script Templates
│       ├── 📁 automation/
│       ├── 📁 javascript/
│       ├── 📁 python/
│       └── 📁 ucode/
│
├── 📁 wizard/                                  # Development Environment (Level 100)
│   ├── 🔧 dev-utils.sh
│   ├── 📄 README.md
│   │
│   ├── 📁 claude-vscode/                      # Claude Integration
│   │   ├── 📁 architecture/
│   │   ├── 📁 bugs/
│   │   ├── 📁 completed/
│   │   ├── 📁 features/
│   │   └── 📁 sessions/
│   │
│   ├── 📁 notes/                              # Development Notes (63+ hex files)
│   │   ├── 📄 uDEV-E4124AA0-Daily-Activity-Summary.md    # Converted
│   │   ├── 📄 uREP-E49D01A0-Structure-Cleanup.md         # Converted  
│   │   ├── 📄 uREP-E49101A0-v13-Multi-Install.md         # Converted
│   │   ├── 📄 uDOC-E4A041A0-Consolidation-Roadmap-v13.md # Converted
│   │   ├── 📄 uDOC-E4A041A0-Hex-Convention-Complete.md   # Implementation
│   │   └── ... (60+ more hex-named files)
│   │
│   ├── 📁 scripts/                            # Development Scripts
│   │   ├── 📁 archive/
│   │   ├── 📁 cleanup/
│   │   ├── 📁 maintenance/
│   │   ├── 📁 migration/
│   │   └── 📁 validation/
│   │
│   ├── 📁 tools/
│   │
│   ├── 📁 utilities/                          # Development Utilities
│   │   ├── 🔧 convert-to-hex-filenames.sh    # Filename converter (original)
│   │   ├── 🔧 convert-to-hex-v2.sh           # Advanced hex converter
│   │   └── 🔧 test-hex-conversion.sh         # Testing utility
│   │
│   ├── 📁 vscode/                             # VS Code Integration
│   │   ├── 📁 .vscode/                        # VS Code settings
│   │   └── 📁 vscode-extension/               # uDOS VS Code Extension
│   │       ├── 📄 package.json
│   │       ├── 📄 install-extension.sh
│   │       ├── 📁 snippets/
│   │       │   ├── 📄 uscript.json
│   │       │   └── � udos-enhanced.json
│   │       ├── �📁 src/
│   │       └── 📁 syntaxes/
│   │
│   └── 📁 workflows/                          # Development Workflows
│       ├── 📁 active/
│       ├── 📁 completed/
│       ├── 📁 development/
│       ├── 📁 failed/
│       ├── 📁 pending/
│       ├── 📁 technical/                      # Technical Documentation
│       │   ├── 📄 uTASK-E801032F-Filename-v3-Implementation-Task.md     # Converted
│       │   └── 📄 uTASK-E8010333-Wizard-Environment-Enhancement-Task.md # Converted
│       ├── 📁 tasks/
│       ├── 📁 templates/
│       └── 📁 versioning/
```

## 📊 Structure Statistics

### 🗂️ **Directory Summary**
- **Total Directories:** 180+
- **Core Systems:** 4 (uCORE, uMEMORY, uSCRIPT, uKNOWLEDGE)
- **Installation Types:** 6 (ghost, tomb, drone, imp, sorcerer, wizard)
- **uCode Scripts:** 9 (Visual Basic-style modular commands)
- **Extension Types:** 3 (System, Script, Development)
- **Workflow Stages:** 8 per workflow type

### 📝 **File Distribution**
- **Documentation:** 25+ core docs and guides
- **Configuration:** 20+ config files  
- **Shell Scripts:** 15+ automation scripts
- **uCode Scripts:** 9 modular Visual Basic-style scripts
- **Templates:** 50+ template files
- **JSON Files:** 20+ configuration and data files

### 🎯 **Key Features v1.3**
- ✅ **Modular Architecture** with clean separation of concerns
- ✅ **Visual Basic-style uCode Scripts** for complex functionality
- ✅ **Dual Interface Support** (shortcode and full commands)
- ✅ **Smart Command Routing** between core shell and uCode scripts
- ✅ **Multi-Installation Architecture** with 6 role-based environments
- ✅ **Role-based Permissions** with JSON configuration files
- ✅ **Comprehensive Templates** for all system components
- ✅ **Enhanced Error Handling** with non-interactive mode support
- ✅ **VS Code Integration** with custom extension and utilities

### ⭐ **v1.3 Modular Benefits**
- **Maintainability:** Easy to update individual components
- **Extensibility:** Add new commands without modifying core
- **Performance:** Optimized command processing and routing
- **Clean Code:** Clear separation between routing and functionality

### 🔧 **System Health**
- **Repository Structure:** ✅ Clean and consolidated
- **Naming Convention:** ✅ Hex format implemented  
- **Permission System:** ✅ Role-based access controls
- **Documentation:** ✅ Comprehensive and current
- **Development Tools:** ✅ Complete wizard environment
- **Installation Management:** ✅ Unified install/ structure
- **Core Organization:** ✅ Empty directories removed
- **Extension Management:** ✅ Consolidated into single extensions/ folder

---

**Structure Status:** 🎉 **CONSOLIDATED** - Extensions unified: empty extension/ removed, all extensions now in logical extensions/ structure.

*uDOS v1.3 Repository Structure - Where organization meets innovation*
