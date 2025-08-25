# uDOS AI Coding Agent Instructions

## Overview
uDOS (Universal Device Operating System) v1.4.0 is a modular, role-based system providing a unified interface across CLI Terminal, Desktop Application, and Web Export modes. This document guides AI coding agents in understanding the architecture, conventions, and development patterns specific to this codebase.

## 🏗️ Architecture Overview

### Core Modules
- **uCORE**: System code, launchers, templates, and core functionality
- **uMEMORY**: User data storage, logs, sessions, and persistent memory
- **uNETWORK**: Flask/SocketIO server, display system, and client connectivity
- **uSCRIPT**: Script library, utilities, and automation tools
- **uKNOWLEDGE**: Documentation, help system, and knowledge base
- **sandbox**: User workspace for active development and experimentation
- **extensions**: Modular extension system with user/platform/core categories

### Critical Architecture Principles (v1.4)
1. **Data Separation**: uCORE contains system code, uMEMORY contains user data
2. **Logging Consolidation**: All logs flow through centralized uMEMORY system
3. **Role-Based Access**: Different permission levels (user/wizard/sorcerer/imp/student/admin)
4. **Three-Mode Display**: CLI Terminal, Desktop Application, Web Export compatibility

## 🧙‍♂️ uCODE Programming Language

uDOS uses its own uCODE syntax for commands and templates:

### Command Syntax
```
[COMMAND] <ACTION> {PARAMETER} ~ Description
[COMMAND|ACTION*params] {VARIABLE} | pipeline_operation
```

### Common Patterns
- `[WORKFLOW] <STATUS>` - Check workflow status
- `[BACKUP] <CREATE> {FULL}` - Create full backup
- `[LOG] <WRITE> {message}` - Write to log
- `[ROLE] <GET|SET> {wizard}` - Role management
- `DEF {VAR} = {VALUE}` - Variable definition
- `{get:variable_name}` - Variable interpolation

### Data Control Operations
- `[DATA] <SAVE> {key} {value}` - Save data
- `[DATA] <LOAD> {key}` - Load data
- `[DATA] <DELETE> {key}` - Delete data
- `[GRID] <DISPLAY> {content}` - Grid system display

## 🛠️ Development Workflows

### VS Code Integration
- Use `./uCORE/launcher/vscode/start-vscode-dev.sh` for development mode
- Workspace configuration in `.vscode/` includes:
  - Multi-folder workspace setup
  - Live preview integration for UI components
  - Custom terminal profiles with uDOS environment variables
  - Debugging configuration for Bash scripts

### Development Server
- Flask/SocketIO server at `uNETWORK/server/server.py` (1064 lines)
- Runs on localhost:8080 in development
- WebSocket support for real-time communication
- API endpoints under `/api/` namespace

### Task Management System
Available VS Code tasks (use Ctrl+Shift+P > Tasks: Run Task):
- 🚀 Start uDOS Development
- 🔄 Restart uDOS Server
- 🌐 Open UI Preview
- 🧪 Run Quick Tests
- 📝 Quick Commit
- 🌀 Start uDOS
- 🧠 Development Mode

### Workflow Management
The system uses a four-stage user journey:
1. **Move** → Current activity logging
2. **Milestone** → Achievement tracking
3. **Mission** → Goal and objective management
4. **Legacy** → Long-term impact documentation

Commands:
```bash
./uCORE/core/workflow-manager.sh move "development" "Adding new feature"
./uCORE/core/workflow-manager.sh milestone "Feature Complete" "Successfully implemented X"
./uCORE/core/workflow-manager.sh mission create "Project Y" "Build comprehensive Y system"
```

## 📁 Directory Structure Guidelines

### File Organization
```
uCORE/
├── code/           # Core system scripts
├── core/           # Essential components (sandbox.sh, workflow-manager.sh)
├── launcher/       # Platform-specific launchers
├── platform/       # OS-specific implementations
└── templates/      # System templates

uMEMORY/
├── user/           # User-specific data
├── system/         # System logs and data
├── logs/           # Centralized logging
└── sessions/       # Session management

sandbox/
├── workflow/       # User journey tracking
├── session/        # Current session data
├── tasks/          # Task management
└── development/    # Active development workspace
```

### Naming Conventions
- **Scripts**: kebab-case with descriptive names (`workflow-manager.sh`)
- **Log Files**: uLOG format with timestamps (`uLOG-20250825-123456-Summary.md`)
- **Configuration**: JSON format with .json extension
- **Templates**: Descriptive names with purpose (`task-template.md`)

## 🔧 Code Patterns and Conventions

### Bash Scripting Standards
```bash
#!/bin/bash
# Script description and purpose
set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}
```

### Python Server Patterns
- Use Flask with SocketIO for real-time features
- Follow RESTful API conventions under `/api/` namespace
- Implement proper error handling and logging
- Support CORS for cross-origin requests

### JSON Configuration
All configuration files use consistent JSON structure:
```json
{
    "metadata": {
        "name": "component-name",
        "version": "1.0.0",
        "type": "user|system|core",
        "platform": "universal|macos|linux|windows"
    },
    "description": "Component description",
    "configuration": {
        // Component-specific config
    }
}
```

## 🎯 Role-Based Development

### Role Hierarchy
1. **User** (Level 20): Basic operations
2. **Student** (Level 40): Learning and experimentation
3. **Imp** (Level 60): Development tools and automation
4. **Sorcerer** (Level 80): Advanced administration
5. **Wizard** (Level 100): Full development access

### Permission Patterns
- Check role permissions before executing privileged operations
- Use role-specific directories and configurations
- Implement graceful degradation for lower privilege levels

## 🚨 Important Guidelines

### Data Safety
1. **Never modify uCORE directly** in production environments
2. **Always use backup systems** before major changes
3. **Validate user inputs** especially in role management
4. **Follow logging conventions** for audit trails

### Performance Considerations
- Use efficient file operations for large datasets
- Implement proper caching for frequently accessed data
- Consider asynchronous operations for long-running tasks
- Monitor memory usage in user data operations

### Testing Patterns
- Use `./uCORE/launcher/universal/test-udos.sh` for system tests
- Implement unit tests for critical components
- Test cross-platform compatibility
- Validate role-based access controls

## 🔌 Extension Development

### Extension Structure
```
extensions/user/my-extension/
├── manifest.json           # Extension metadata
├── commands/              # Command implementations
├── library/               # Supporting libraries
│   ├── shell/            # Bash scripts
│   └── python/           # Python modules
└── templates/            # Extension templates
```

### Integration Points
- Register commands in manifest.json
- Follow uCODE syntax for command definitions
- Implement proper error handling and logging
- Support sandbox integration for user workflows

## 🎨 UI Development

### Frontend Technologies
- HTML5 with Tailwind CSS for styling
- JavaScript for interactivity
- WebSocket integration for real-time updates
- Responsive design for multiple device types

### UI Components Location
- Main UI: `uCORE/launcher/universal/ucode-ui/`
- Live preview integration with VS Code
- Grid-based layout system
- Role-aware interface elements

## 📚 Documentation Standards

- Use Markdown format for all documentation
- Include practical examples in code documentation
- Follow the established template structure
- Maintain changelog for version tracking
- Document API endpoints with request/response examples

## 🔄 Version Control

### Commit Patterns
- Use descriptive commit messages
- Include component prefixes (uCORE:, uMEMORY:, etc.)
- Reference issue numbers when applicable
- Use `git add -A && git commit -m "message"` pattern

### Branch Strategy
- Development work in feature branches
- Test thoroughly before merging to main
- Tag releases with version numbers
- Maintain backup branches for major changes

## 🎯 Common Development Tasks

### Adding New Commands
1. Define uCODE syntax in documentation
2. Implement command in appropriate module
3. Add to command registry
4. Create tests and documentation
5. Update help system

### Creating Extensions
1. Use extension template structure
2. Register in extension manager
3. Follow naming conventions
4. Implement proper error handling
5. Test cross-platform compatibility

### Modifying Core Systems
1. Create backup before changes
2. Follow data separation principles
3. Update documentation
4. Test role-based permissions
5. Validate logging integration

This document should be referenced whenever working on the uDOS codebase to ensure consistency with established patterns and architectural principles.
