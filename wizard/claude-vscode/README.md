# Claude VS Code Development Notes

This directory contains development notes, session logs, and collaboration records for Claude-assisted development in VS Code.

## Directory Structure

```
claude-vscode/
├── sessions/        # Development session notes
├── features/        # Feature development tracking
├── bugs/           # Bug fixes and issue resolution
├── architecture/   # Architecture decisions and changes
└── completed/      # Completed development summaries
```

## Filename Convention

All files follow the uDOS v2.0 naming convention:

```
uDEV-YYYYMMDD-HHMMSS-TZ-Session-Topic.md
```

Examples:
- `uDEV-20250817-180000-C0-Architecture-Review.md`
- `uDEV-20250817-180000-C0-Feature-uSCRIPT.md`
- `uDEV-20250817-180000-C0-Bug-Fix-Naming.md`

## Usage

1. **Active Development**: Create files in appropriate subdirectories
2. **Session Completion**: Move completed summaries to `../log/` directory
3. **Task Management**: Use `../workflows/tasks/` for ongoing development tasks
4. **Roadmap Planning**: Use `../workflows/roadmaps/` for future development planning

## Integration

This system integrates with:
- `../dev-utils.sh` - Development utilities manager
- `../log/` - Centralized logging system
- `../workflows/` - Workflow and task management
- `../utilities/` - Development utility scripts

---

*Part of uDOS Wizard Development Environment*
