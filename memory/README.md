# Memory Folder

**Purpose**: Permanent storage for confirmed user data, research, and life's work.

## Structure

```
memory/
├── research/     # Confirmed research, findings, knowledge
├── missions/     # User's active and completed missions
├── archive/      # Historical records, completed projects
├── scripts/      # Maintainer/developer scripts (deploy, tools)
└── README.md     # This file
```

## Usage

This folder contains **finalized, confirmed user data** that has been:
1. Created/edited in `/sandbox`
2. Reviewed and validated by the user
3. Committed via the `EMPTY_SANDBOX` command

## Difference from Other Folders

- **`/sandbox`**: Working directory, drafts, active sessions (temporary)
- **`/knowledge`**: Read-only system knowledge library (uDOS reference materials)
- **`/memory`**: Confirmed user data (permanent, tracked in git)

## Commands

- `EMPTY_SANDBOX` - Review and commit sandbox work to memory
- `CATALOG memory/` - List all memory contents
- `LOAD memory/research/[file]` - Load confirmed research

## Git Tracking

All files in `/memory` are tracked in version control to preserve your work.
