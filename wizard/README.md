# Dev Mode - uDOS Development Environment

## 🧙‍♂️ Wizard Installation Development Mode

Special system development mode available only to Wizard Installations with advanced development tools housed in the wizard folder.

## 📁 Directory Structure

```
wizard/
├── vscode/              # VS Code configuration and extensions
│   └── .vscode/         # Workspace settings, tasks, launch configs
├── uLOG/                # All development logs, reports, and summaries (flat structure)
├── tools/               # Development utilities and scripts
├── scripts/             # Development and maintenance scripts
├── reports/             # Analysis and metrics (non-uLOG files)
├── workflows/           # Enhanced workflow management
│   ├── roadmaps/        # Project roadmaps and planning
│   ├── versioning/      # Version planning and release management
│   ├── development/     # Development workflows and processes
│   ├── tasks/           # Task management and tracking
│   ├── active/          # Active workflows
│   ├── completed/       # Completed workflows
│   └── templates/       # Workflow templates
└── logs/                # System logs (non-uLOG format)
```

## 🎯 Purpose

Dev Mode provides:

### 🔧 Development Tools
- **VS Code Integration**: Dedicated workspace configuration
- **Development Scripts**: Advanced development and maintenance scripting
- **uLOG Management**: Centralized logging system with flat file structure
- **Workflow System**: Enhanced roadmap, versioning, and task management

### 🧙‍♂️ Wizard-Only Features
- **System Development**: Core system enhancement and modification
- **Advanced Scripting**: Development mode exclusive utilities
- **Version Planning**: Roadmap and release management workflows
- **Development Tracking**: Comprehensive logging and reporting

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
cd /Users/agentdigital/uDOS/uDEV

# Launch VS Code with uDOS development workspace
code vscode/

# Start development logging
./tools/start-dev-session.sh
```

### Development Workflow
1. **Initialize Session**: Start development logging
2. **Define Objectives**: Create task in sandbox/tasks/
3. **Develop Features**: Use uDEV tools and environment
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
