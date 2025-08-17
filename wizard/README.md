# Dev Mode - uDOS Development Environment

## 🧙‍♂️ Wizard Installation Development Mode

Special system development mode available only to Wizard Installations with advanced development tools housed in the wizard folder.

## 📁 Directory Structure

```
wizard/
├── dev-utils.sh         # Development utilities manager (main entry point)
├── vscode/              # VS Code configuration and extensions
│   └── .vscode/         # Workspace settings, tasks, launch configs
├── log/                 # All development logs, reports, and summaries (flat structure)
├── utilities/           # Development utility scripts
│   └── generate-filename-v2.sh  # Filename generator v2.0
├── claude-vscode/       # Claude VS Code development notes
│   ├── sessions/        # Development session notes
│   ├── features/        # Feature development tracking
│   ├── bugs/           # Bug fixes and issue resolution
│   ├── architecture/   # Architecture decisions and changes
│   └── completed/      # Completed development summaries
├── tools/               # Development utilities and scripts
├── scripts/             # Development and maintenance scripts
├── reports/             # Analysis and metrics (non-uDEV files)
├── workflows/           # Enhanced workflow management
│   ├── roadmaps/        # Project roadmaps and planning
│   ├── versioning/      # Version planning and release management
│   ├── development/     # Development workflows and processes
│   ├── tasks/           # Task management and tracking
│   ├── active/          # Active workflows
│   ├── completed/       # Completed workflows
│   └── templates/       # Workflow templates
├── RELEASE_NOTES_v1.3.md          # Release documentation
├── uDOS-ORGANIZATION-SUMMARY.md   # Organization and structure notes
├── WORKFLOW-SYSTEM.md              # Workflow system documentation
└── logs/                # System logs (non-uDEV format)
```

## 🎯 Purpose

Dev Mode provides:

### 🔧 Development Tools
- **Development Utilities Manager** (`./dev-utils.sh`): Central command for all development operations
- **Filename Generator v2.0**: Generate compliant filenames with 40-char limit and HHMMSS precision
- **Claude VS Code Integration**: Dedicated notes and session tracking for AI-assisted development
- **Workflow Management**: Enhanced roadmap, versioning, and task tracking with organized completion flow

### 🧙‍♂️ Wizard-Only Features
- **Development Environment**: Complete development toolkit for Wizard Installations
- **Utility Script Management**: Build and run development utilities with integrated logging
- **Release Notes Management**: Centralized development documentation and organization summaries
- **Development Session Tracking**: Comprehensive logging with automatic organization to log/ folder

## 🚀 Getting Started

### Using Development Utilities

```bash
# Show available commands and utilities
./dev-utils.sh help

# Generate filename (general system file)
./dev-utils.sh filename uLOG System-Status

# Generate filename (uMEMORY file with location tile)
./dev-utils.sh filename uNOTE Notes true 05

# Check development status
./dev-utils.sh status

# Organize logs and completed summaries
./dev-utils.sh organize

# Manage roadmap tasks
./dev-utils.sh roadmap list
./dev-utils.sh roadmap add "New-Feature-Development"
```

### Development Workflow

1. **Start Development Session**: Use appropriate subdirectory in claude-vscode/
2. **Create Utilities**: Add scripts to utilities/ directory
3. **Track Progress**: Use workflows/ for roadmaps and task management
4. **Log Activities**: All actions automatically logged to log/ directory
5. **Complete Sessions**: Move completed summaries using organize command

### 📊 Development Logging
- **Activity Logs**: All development actions logged in uLOG format
- **Progress Tracking**: Milestone and feature development logs
- **Debug Sessions**: Detailed debugging information
- **Performance Metrics**: System optimization data

### 🧪 Testing Environment
- **Isolated Testing**: Safe environment for experimental features
- **Integration Testing**: Component interaction validation
- **Performance Testing**: System optimization validation
- **Regression Testing**: Change impact assessment

## 🚀 Key Features

### Wizard User Exclusive
- Advanced development capabilities
- System-level access and modifications
- Direct integration with uDOS core systems
- Administrative development privileges

### VS Code Integration
- Custom workspace configuration
- uDOS-specific snippets and templates
- Integrated terminal with uDOS context
- Extension development environment

### Automated Logging
- All development activities automatically logged
- uLOG v1.3 naming convention compliance
- Searchable development history
- Progress tracking and reporting

## 🛠️ Usage

### Entering Wizard Dev Mode
```bash
# Access development environment
cd /Users/agentdigital/uDOS/wizard

# Launch VS Code with uDOS development workspace
code vscode/

# Start development logging
./tools/start-dev-session.sh
```

### Development Workflow
1. **Initialize Session**: Start development logging
2. **Define Objectives**: Create task in sandbox/tasks/
3. **Develop Features**: Use Dev Mode tools and environment
4. **Test Integration**: Validate changes in testing/
5. **Document Progress**: Auto-logged in logs/ directory
6. **Complete Session**: Archive results in summaries/

## 🔗 Integration Points

### uDOS Core Systems
- **uCORE**: Direct access to core functionality
- **uMEMORY**: Development state persistence
- **uKNOWLEDGE**: Documentation and learning integration
- **Sandbox Tasks**: Active task management integration

### External Tools
- **VS Code**: Primary development interface
- **Git**: Version control integration
- **Shell Scripts**: Advanced automation capabilities
- **ASSIST Mode**: AI-enhanced development support

## 📋 File Naming Convention

All development files follow uDOS v1.3 naming convention:

### Log Files
```
uLOG-YYYYMMDD-HHMM-TTZ-MMLLNN.md
```

### Development Scripts
```
uSCRIPT-YYYYMMDD-HHMM-TTZ-MMLLNN.sh
```

### Documentation
```
uDOC-YYYYMMDD-HHMM-TTZ-MMLLNN.md
```

## 🎯 Development Objectives

### Primary Goals
- **System Enhancement**: Continuous uDOS improvement
- **Feature Development**: New capability implementation
- **Performance Optimization**: System efficiency improvements
- **Integration Expansion**: External tool and service integration

### Quality Standards
- **Code Quality**: Consistent, documented, testable code
- **Documentation**: Comprehensive development documentation
- **Testing**: Thorough validation of all changes
- **Compliance**: Adherence to uDOS naming and structure conventions

---

**Environment Status**: ACTIVE  
**Last Updated**: uLOG-20250816-2250-28-00SY43  
**Wizard Access**: ENABLED
