# Dev Mode - uDOS Development Environment

## 📦 Wizard Folder Overview
The **wizard** folder contains all advanced development utilities, experiments, workflows, and historical notes.  
Key highlights:
- **Dev Features**: Tools for logging, file organization, script execution, and error handling.
- **VS Code Extensions**: Pre-configured workspace for development with integration support.
- **Workflow Manager**: Roadmaps, templates, and active task tracking for structured development.
- **Past Dev Notes**: Historical planning, decisions, and documentation for reference.

## 🧙‍♂️ Wizard Installation Development Mode

Special system development mode available only to Wizard Installations with advanced development tools housed in the wizard folder.

## 📁 Directory Structure

```
wizard/
├── dev-utils.sh         # Development utilities manager (main entry point)
├── vscode/              # VS Code configuration and extensions
│   └── .vscode/         # Workspace settings, tasks, launch configs
├── notes/               # Historical planning documents and implementation records
├── experiments/         # External packages and experimental tools
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
│   ├── roadmaps/        # Strategic planning and future roadmaps
│   ├── active/          # Currently running workflows
│   ├── templates/       # Workflow template definitions
│   ├── config.json      # Workflow system configuration
│   └── README.md        # Workflow documentation
└── logs/                # System logs (non-uDEV format)
```

## 🎯 Purpose

Dev Mode provides:

### 🔧 Development Tools
- **Development Utilities Manager** (`./dev-utils.sh`): Central command for all development operations
- **Filename Generator v2.0**: Generate compliant filenames with 40-char limit and HHMMSS precision
- **Claude VS Code Integration**: Dedicated notes and session tracking for AI-assisted development
- **Workflow Management**: Enhanced roadmap, versioning, and task tracking with organized completion flow

### 📚 Historical Documentation
- **Notes Directory**: Historical planning documents and implementation records moved from `/docs`
- **Strategic Archives**: Past development decisions and completed project documentation
- **Implementation Records**: Technical migration and reorganization documentation
- **Reference Materials**: Historical context for ongoing development

### 🧙‍♂️ Wizard-Only Features
- **Development Environment**: Complete development toolkit for Wizard Installations
- **Utility Script Management**: Build and run development utilities with integrated logging
- **Release Notes Management**: Centralized development documentation and organization summaries
- **Development Session Tracking**: Comprehensive logging with automatic organization to notes/ folder
- **Git Integration**: Full Git support with SSH key management (uCODE commands: PUSH, PULL, COMMIT, CLONE, etc.)

### 📚 Documentation Access
Documentation is organized across multiple directories for different purposes:

#### **Historical Documentation** (`notes/`)
- **Implementation Records**: `notes/uNOTE-*-Project-Planning-History.md`
- **Architecture Decisions**: `notes/uNOTE-*-Modular-Architecture-Migration.md`
- **System Reorganization**: `notes/uNOTE-*-Extension-Reorganization.md`
- **Historical Roadmaps**: `notes/uNOTE-*-Historical-Roadmap-v13.md`

#### **Future Planning** (`workflows/roadmaps/`)
- **Strategic Roadmaps**: `workflows/roadmaps/uRMP-*` files for v1.4-v1.5 planning
- **AI Integration Plans**: Comprehensive AI development strategies
- **Enterprise Features**: Business model and enterprise development plans

#### **Development Logs** (Various Locations)
- **Session Logs**: `claude-vscode/*/` - AI-assisted development tracking
- **System Logs**: `logs/` - Development activity logs
- **Reports**: `reports/` - Analysis and metrics

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
4. **Log Activities**: All actions automatically logged to notes/ directory
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
