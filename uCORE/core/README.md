# uCORE Core System - Consolidated v1.4.0

This directory contains the consolidated core system components for uDOS v1.4.0.

## Consolidation Changes

As of v1.4.0, the `uCORE/code/` directory has been merged into `uCORE/core/` for better organization:

- **Previous Structure:** Separate `core/` and `code/` directories
- **New Structure:** Unified `core/` with organized subdirectories

## Directory Structure

```
uCORE/core/
├── commands/          # Command interface and routing
│   └── ucode.sh      # Main command entry point
├── utilities/         # System utilities and tools
├── compat/           # Compatibility components
├── deployment-manager/  # Deployment management
├── smart-input/      # Smart input system
├── *.sh              # Core engines and handlers
└── registry.json     # Core component registry
```

## Core Components

### Engines
- `template-engine.sh` - Template processing system
- `help-engine.sh` - Interactive help system

### Handlers
- `command-router.sh` - Command routing and processing
- `backup-handler.sh` - Backup system management
- `get-handler.sh` - Resource retrieval handler
- `post-handler.sh` - Post-processing handler

### Managers
- `session-manager.sh` - Session state management
- `workflow-manager.sh` - Workflow orchestration

### Infrastructure
- `environment.sh` - Environment setup and configuration
- `logging.sh` - System logging utilities
- `sandbox.sh` - Sandbox environment management

### Utilities (Previously from code/)
- `backup.sh`, `restore.sh` - Backup/restore operations
- `check.sh` - System validation
- `dash.sh` - Dashboard generation
- `reboot.sh`, `destroy.sh` - System lifecycle
- `repair.sh` - System repair utilities
- `run.sh`, `show.sh` - Execution and display
- `tree.sh` - Directory tree visualization
- `trash.sh` - File management

## Migration Notes

All references to `uCORE/code/` have been automatically updated to point to the appropriate locations within `uCORE/core/`. The system maintains full backward compatibility.

Original files are preserved in the backup directory for reference.

## Usage

The main entry point remains the same:
```bash
./uCORE/core/commands/ucode.sh [command] [args]
```

All utilities are accessible through the unified command system.
