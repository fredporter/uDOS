# uDOS AI Coding Agent Instructions

## Overview
uDOS (Universal Device Operating System) v1.4.0 is a modular, role-based system providing a unified interface across CLI Terminal, Desktop Application, and Web Export modes. This document guides AI coding agents in understanding the architecture, conventions, and development patterns specific to this codebase.

## 🏗️ Architecture Overview

### Core Modules
- **uCORE**: System code, launchers, templates, and core functionality
- **uMEMORY**: User data storage, sessions, and persistent memory (logs moved to sandbox)
- **uNETWORK**: Flask/SocketIO server, display system, and client connectivity
- **uSCRIPT**: Script library, utilities, and automation tools
- **uKNOWLEDGE**: Documentation, help system, and knowledge base
- **sandbox**: User workspace for active work, logging, and experimentation
- **extensions**: Modular extension system with user/platform/core categories
- **dev**: Core development environment (wizard role + DEV mode only)

### Critical Architecture Principles (v1.4)
1. **Data Separation**: uCORE contains system code, sandbox contains active work and logging
2. **Role-Based Development**: Core development (/dev) requires wizard role + DEV mode
3. **Workspace Separation**: sandbox (active/flushable) vs uMEMORY (permanent archive)
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
├── role/           # Role-specific configurations
└── templates/      # Data templates

sandbox/
├── logs/           # All system and user logging
├── sessions/       # Current session data
├── tasks/          # Task management
├── scripts/        # Temporary scripts
└── experiments/    # Development workspace

dev/                # Core development (wizard + DEV mode only)
├── active/         # Current core development projects
├── scripts/        # Development automation scripts
├── templates/      # Development templates
├── docs/           # Architecture documentation
├── copilot/        # AI assistant context
└── vscode/         # VS Code development configs
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

### Development Access (Wizard + DEV Mode Only)
- **Core Development**: `/dev` folder for system development
- **User Development**: `/sandbox` for experiments and user scripts
- **Templates**: Use `/dev/templates` for consistent development patterns
- **Documentation**: Architecture docs in `/dev/docs`
- **AI Integration**: Development context in `/dev/copilot`
- **VS Code**: Development configs in `/dev/vscode`

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
- Use `./dev/scripts/test/test-core-system.sh` for development tests
- Implement unit tests for critical components
- Test cross-platform compatibility
- Validate role-based access controls

## 🔧 Development Environment

### /dev Folder - Wizard Role + DEV Mode Only
The `/dev` folder is the core development environment, accessible only to wizard role with DEV mode activated.

#### Development Structure
```
dev/
├── active/              # Current core development (local only)
│   ├── core/           # Core system development
│   ├── extensions/     # Extension development
│   └── tools/          # Tool development
├── scripts/            # Development automation
│   ├── build/         # Build scripts (./dev/scripts/build/build-core.sh)
│   ├── test/          # Test scripts (./dev/scripts/test/test-core-system.sh)
│   ├── deploy/        # Deployment scripts
│   └── maintenance/   # Maintenance scripts
├── templates/          # Development templates (synced)
│   ├── commands/      # Command templates
│   ├── extensions/    # Extension templates
│   └── configs/       # Configuration templates
├── docs/              # Architecture documentation (synced)
├── copilot/           # AI assistant context (synced)
└── vscode/            # VS Code configurations (synced)
```

#### Development Workflow
- **Core development** → `/dev/active/` (wizard + DEV mode required)
- **User experiments** → `/sandbox/` (all roles, flushable workspace)
- **Build system** → `./dev/scripts/build/build-core.sh`
- **Testing** → `./dev/scripts/test/test-core-system.sh`
- **Templates** → Use `/dev/templates/` for consistent development

#### Git Sync Strategy
- **Synced**: `/dev/templates/`, `/dev/docs/`, `/dev/copilot/`, `/dev/vscode/`
- **Local only**: `/dev/active/`, temporary scripts, work-in-progress files

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
1. Use templates from `dev/templates/commands/`
2. Implement command in appropriate module
3. Test with `./dev/scripts/test/test-core-system.sh`
4. Add to command registry
5. Update help system and documentation

### Creating Extensions
1. Use extension template from `dev/templates/extensions/`
2. Develop in `dev/active/extensions/` (wizard + DEV mode)
3. Test with extension manager
4. Deploy to `extensions/` when ready
5. Follow naming conventions and documentation standards

### Development Best Practices
1. **Use dev environment**: Work in `/dev/active/` for core development
2. **Follow templates**: Use `/dev/templates/` for consistency
3. **Test thoroughly**: Run `./dev/scripts/test/` before deployment
4. **Document changes**: Update `/dev/docs/` with architectural changes
5. **Sync selectively**: Only collaborative content goes to git

### Modifying Core Systems
1. **Check permissions**: Wizard role + DEV mode required
2. **Create backup**: Use development branching
3. **Follow data separation**: uCORE = system code, sandbox = active work
4. **Test role-based permissions**: Validate access controls
5. **Update documentation**: Keep `/dev/docs/` current

This document should be referenced whenever working on the uDOS codebase to ensure consistency with established patterns and architectural principles.
