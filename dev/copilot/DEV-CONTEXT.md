# uDOS v1.0.5.1 Development Context for AI Assistants

## Development Environment
This `/dev` folder is the core development environment for uDOS, accessible only to wizard role with DEV mode activated.

## Architecture Overview - MODULAR REFACTORING COMPLETE
uDOS uses a **clean modular architecture**:

### � **uCORE** - Pure Bash Core (100% Clean)
- **Essential command routing, authentication, variable management**
- **ZERO Python dependencies** - completely bash-only as intended
- **Reduced from 27,643 to 21,512 lines** through modular extraction
- **Module loader system** for clean interface to uSCRIPT modules
- Optimized for instant startup and universal compatibility

### 📦 **uSCRIPT/modules** - Feature Modules (Organized)
- **Session Management** (`modules/session/`) - Persistent state tracking
- **Workflow Management** (`modules/workflow/`) - User journey automation  
- **Story Management** (`modules/stories/`) - Interactive variable collection
- **Backup System** (`modules/backup/`) - Comprehensive backup/restore
- **Smart Input** (`modules/input/`) - Advanced input processing
- **Legacy Python** (`legacy-python/`) - Moved Python files from uCORE

### 🐍 **uNETWORK & uSCRIPT** - Python Environment (Modern Features)
- **uNETWORK**: Web server, APIs, browser interfaces
- **uSCRIPT**: Python automation, complex scripting
- **Isolated virtual environment** at `uSCRIPT/venv/python/`
- Modern Python features with dependency isolation

## Key Changes in v1.0.5.1
- **6,431 lines moved** from uCORE to modular uSCRIPT structure
- **installation.id moved** to uMEMORY for proper organization
- **Trash system moved** from uCORE to sandbox
- **All Python files removed** from uCORE (moved to uSCRIPT/legacy-python)
- **Empty /core folder eliminated** (merged with /code)
- **Root launchers organized** into `/launchers` directory

## Key Scripts
- `activate-udos-env.sh` - Shell venv activator (root level)
- `uNETWORK/server/launch-with-venv.sh` - Guaranteed venv server launcher
- `uSCRIPT/activate-udos-python.sh` - Python environment manager
- `uCORE/code/system-monitor.sh` - Native bash system monitoring

## Structure
- `active/` - Current core development projects
- `scripts/` - Development automation scripts
- `templates/` - Core system templates
- `tools/` - Development utilities
- `roadmaps/` - Project planning and roadmaps
- `docs/` - Architecture and API documentation
- `copilot/` - AI assistant context and instructions
- `vscode/` - VS Code development configurations

## Role Access
- **Wizard + DEV mode**: Full access to all development tools
- **All other roles**: Use `/sandbox` for user development

## Integration Points
- `.github/copilot-instructions.md` - Main AI instructions
- `.vscode/` - VS Code development environment
- `/dev/copilot/` - Development-specific AI context
- `/sandbox/` - User workspace (flushable)
