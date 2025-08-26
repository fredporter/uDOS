# uDOS Development Context for AI Assistants

## Development Environment
This `/dev` folder is the core development environment for uDOS, accessible only to wizard role with DEV mode activated.

## Architecture Overview
uDOS uses a **modular environment strategy**:

### 🚀 **uCORE** - Native Bash (Lean & Fast)
- System management, CLI tools, execution scripts
- **No Python dependencies** - uses standard bash/UNIX utilities
- Optimized for older machines and minimal environments
- Instant startup for core operations

### 🐍 **uNETWORK & uSCRIPT** - Python venv (Modern Features)
- **uNETWORK**: Web server, APIs, browser interfaces
- **uSCRIPT**: Python automation, complex scripting
- **Isolated virtual environment** at `uSCRIPT/venv/python/`
- Modern Python features with dependency isolation

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
