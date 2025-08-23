# uDOS Development Directory

This directory contains all development tools, documentation, and resources for the uDOS project.

## 📁 Directory Structure

```
dev/
├── README.md                    # This file
├── workflow-manager.sh          # Enhanced workflow manager with Assist/Command modes
├── workflow.sh                  # Main workflow command entry point
├── config.json                  # Workflow system configuration
├── .assist-mode                 # File indicating Assist Mode is active
├── notes/                       # Development documentation (78 standardized files)
├── briefings/                   # AI assistant briefings and session docs
├── roadmaps/                    # Project roadmaps (flattened structure, 15+ files)
├── scripts/                     # Development and build scripts
├── tools/                       # Development utilities (migrated from wizard/dev-utils)
├── templates/                   # Workflow templates (migrated from wizard)
├── active/                      # Active workflows (migrated from wizard)
├── vscode-extension/            # VS Code extension for uDOS
└── vscode-backup-root/          # Backup of original root .vscode config
```

## � Enhanced Workflow System v1.3.3

### File Organization & Cleanup
- **Standardized Naming**: All files follow `uDEV-YYYYMMDD-Description.md`, `uBRIEF-YYYYMMDD-Description.md`, `uROAD-YYYYMMDD-Description.md` conventions
- **Automated Maintenance**: Integrated cleanup scripts with conflict prevention and intelligent renaming
- **Flat Structure**: Simplified directory organization for easy access and maintenance

### Assist Mode vs Command Mode
- **Command Mode (IO)**: Traditional user-driven interface (default)
- **Assist Mode (OI)**: AI-driven interface that analyzes context and recommends actions

### Workflow Manager
```bash
# Start interactive workflow manager
./dev/workflow.sh

# Specific commands
./dev/workflow.sh assist enter          # Enter AI-driven Assist Mode
./dev/workflow.sh assist exit           # Return to user-driven Command Mode
./dev/workflow.sh assist analyze        # Analyze context and get recommendations

# Briefings Management
./dev/workflow.sh briefings list        # List all briefings
./dev/workflow.sh briefings current     # Show current session briefing
./dev/workflow.sh briefings update      # Update briefing with current context
./dev/workflow.sh briefings cleanup     # Run briefings cleanup script

# Roadmaps Management
./dev/workflow.sh roadmaps list         # List all roadmaps
./dev/workflow.sh roadmaps cleanup      # Run roadmaps cleanup script

# Integrated Cleanup
./dev/workflow.sh cleanup all           # Run all cleanup scripts
./dev/workflow.sh cleanup notes         # Run notes cleanup script
./dev/workflow.sh cleanup briefings     # Run briefings cleanup script
./dev/workflow.sh cleanup roadmaps      # Run roadmaps cleanup script

# Other functions
./dev/workflow.sh list active           # List active workflows
./dev/workflow.sh tool <name>           # Run development tool
./dev/workflow.sh logs                  # View recent logs
```

### Key Features
- **Context Analysis**: AI analyzes past logs and future roadmaps
- **Smart Recommendations**: AI suggests next actions based on patterns
- **Role-Aware Logging**: Integrates with uMEMORY centralized logging
- **Mode Switching**: Seamless transition between user and AI control
- **Enhanced Debugging**: Centralized logging with context awareness

## 🛠️ Development Scripts

### Core Scripts
- `convert-to-udata.sh` - Convert JSON files to uDATA format
- `test-json-parser.sh` - Test JSON parsing functionality
- `setup-local.sh` - Setup local development environment
- `dev-utils.sh` - Enhanced development utilities (migrated from wizard)
- `dev-integration.sh` - Development integration tools
- `dev-mode-detection.sh` - Development mode detection
- `uhex-generator.sh` - Generate uHEX identifiers

### Enhanced Workflow Scripts
- `workflow-manager.sh` - Main workflow management with AI/user modes
- `workflow.sh` - Workflow command entry point
- `assist-logger.sh` - AI-enhanced logging system (located in uCORE/code/)

### Usage
All scripts can be run from the root directory or accessed via VS Code tasks.

```bash
# Run from root directory
./dev/scripts/convert-to-udata.sh
./dev/scripts/test-json-parser.sh
./dev/scripts/setup-local.sh
```

## 🎯 VS Code Integration

The root `.vscode/` directory now contains the consolidated development configuration:

- **tasks.json** - Combined build tasks from all sources
- **settings.json** - Merged editor and workspace settings
- **launch.json** - Debug configurations
- **extensions.json** - Recommended extensions
- **keybindings.json** - Custom keybindings

### Key Tasks Available in VS Code
- 🚀 Start uDOS Development (default)
- 🔄 Restart uDOS Server
- 🌐 Open UI Preview
- 🧪 Run Quick Tests
- 🔄 Convert JSON to uDATA
- ⚙️ Setup Local Development

## 📚 Documentation

Development documentation is organized in the `docs/` subdirectory and includes:
- Implementation guides
- Architecture documentation
- API references
- Migration notes

## 🗺️ Roadmaps

Project planning and roadmaps are in the `roadmaps/` subdirectory with:
- Feature roadmaps
- Version planning
- Milestone tracking

## 🔧 Development Workflow

1. **Start Development**: Use the VS Code task or run `./uCORE/launcher/vscode/start-vscode-dev.sh`
2. **Edit Code**: All development tools are available via Command Palette
3. **Test Changes**: Use quick test tasks or specific script tests
4. **Convert Data**: Use the uDATA conversion tools as needed
5. **Commit**: Use the quick commit task with custom messages

## 🧩 VS Code Extension

The `vscode-extension/` directory contains the uDOS language support extension with:
- Syntax highlighting for uDOS files
- Code snippets
- Language configuration
- IntelliSense support

## ⚡ Quick Start

1. Open the project in VS Code
2. The "🚀 Start uDOS Development" task will run automatically
3. Use `./dev/workflow.sh` to access enhanced workflow management
4. Enter Assist Mode with `./dev/workflow.sh assist enter` for AI-driven development
5. Use Ctrl/Cmd+Shift+P to access all development tasks
6. Access scripts via terminal or VS Code tasks

### Assist Mode Quick Start
```bash
# Enter AI-driven mode
./dev/workflow.sh assist enter

# Let AI analyze and recommend next actions
./dev/workflow.sh assist analyze
```

## 📋 Latest Reorganization (v1.3.3)

### ✅ Completed Improvements
- **📁 Logical Structure**: Moved Claude briefings to `dev/briefings/`, flattened `dev/roadmaps/`
- **📄 File Standardization**: All files follow `uDEV-`, `uBRIEF-`, `uROAD-` naming conventions
- **🔧 Integrated Cleanup**: Automated maintenance scripts accessible via workflow system
- **🧠 Briefings Management**: Dedicated management for AI assistant session documentation
- **🗺️ Roadmaps Organization**: Simplified flat structure with automated categorization
- **🔄 Workflow Integration**: All cleanup and maintenance integrated into dev mode workflow

### 📊 Current Statistics
- **Development Notes**: 78 standardized files in `dev/notes/`
- **Briefings**: 2 files in `dev/briefings/` with session management
- **Roadmaps**: 15+ files in `dev/roadmaps/` with timeline categorization
- **Scripts**: Enhanced cleanup automation in `dev/scripts/`

### 🔗 Workflow Scheduler Integration
The entire system is now integrated with the uDOS Assist Mode workflow scheduler:
- Automatic context analysis and recommendations
- Seamless transitions between Command Mode (user-driven) and Assist Mode (AI-driven)
- Intelligent briefing updates with current session context
- Automated maintenance scheduling and execution

*For complete workflow documentation, see files in `dev/notes/` with prefix `uDEV-*-Workflow-*`*

## 🔍 Troubleshooting

If you encounter issues:
1. Check that all scripts have execute permissions
2. Ensure required dependencies are installed
3. Review the consolidated VS Code settings
4. Check the backup configurations in `vscode-backup-root/`

---

**Note**: This enhanced development environment now includes the complete migration from `wizard/workflows` with AI-driven workflow management, providing both traditional user-driven (Command Mode) and innovative AI-assisted (Assist Mode) development workflows. The system integrates with uMEMORY centralized logging and uCORE command enhancement for a comprehensive development experience.

**Migration Status**: ✅ Complete - All wizard/workflows content migrated and enhanced
**AI Integration**: ✅ Operational - Assist Mode (OI) and Command Mode (IO) active
**System Integration**: ✅ Complete - uMEMORY and uCORE logging enhanced
