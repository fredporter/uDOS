# uDOS Sandbox Structure v1.4

## Purpose
Sandbox is the active workspace for all uDOS activities:
- Session work and logging
- Document processing  
- Data collation
- Script development
- Temporary files

## Directory Structure

### Logging (All logs go here)
```
sandbox/logs/
├── system/          # System logs
├── user/           # User activity logs  
├── network/        # Network and server logs
├── errors/         # Error logs
├── debug/          # Debug information
├── crashes/        # Crash reports
└── runtime/        # Runtime logs
```

### Active Workspace
```
sandbox/
├── sessions/       # Session management
├── scripts/        # Temporary and development scripts
├── documents/      # Document processing workspace
├── data/          # Data processing workspace  
├── tasks/         # Task management
├── experiments/   # Experimentation area
└── backup/        # Local backups
```

## Workflow
1. **Work** in sandbox (logging, scripting, processing)
2. **Organize** useful results in sandbox
3. **File** completed data in uMEMORY when ready

Sandbox is flushable - uMEMORY is permanent.
