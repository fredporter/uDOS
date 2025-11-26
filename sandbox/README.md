# Sandbox - Private Workspace

## Overview

The `/sandbox` directory is your **private workspace** in uDOS. This is where you develop, test, and organize all your personal content before sharing it with others.

## Structure

```
sandbox/
├── trash/      # Archived and processed files
├── dev/        # Development notes and planning
├── docs/       # Completed documentation
├── drafts/     # Work-in-progress files
├── tests/      # Testing scripts and data
├── logs/       # All system and session logs
├── scripts/    # Utility and automation scripts
├── ucode/      # uScript automation files
├── workflow/   # Workflow definitions
└── peek/       # File processing inbox
```

## Quick Start

### Working with Files
```bash
# Create a draft
POKE drafts/myidea.md "# My Idea\nContent here..."

# View it
PEEK drafts/myidea.md

# Edit it
EDIT drafts/myidea.md
```

### Processing External Files
```bash
# Drop a file into peek/ for automatic processing
# uDOS will convert it to the appropriate format

PEEK peek/           # View inbox
```

### Maintenance
```bash
# Clean up old logs and trash
CLEAN

# Clean specific area
CLEAN logs
CLEAN trash

# Organize files
TIDY

# View sandbox statistics
TIDY --report
```

## Best Practices

1. **Start in drafts/** - Create new content here first
2. **Test in tests/** - Put test scripts and data here
3. **Document in docs/** - Move completed docs here
4. **Regular cleanup** - Use `CLEAN` weekly to manage disk space
5. **Organize regularly** - Use `TIDY` to keep things sorted

## Privacy

- Everything in `/sandbox` is **private to you**
- Not synced by default
- Excluded from git (except structure)
- Your personal workspace

When ready to share:
- Move to `/memory/shared` for specific users
- Move to `/memory/groups` for your team
- Contribute to `/memory/community` for everyone

## Learn More

- [Sandbox Structure Guide](docs/SANDBOX-STRUCTURE.md)
- [4-Tier Knowledge Architecture](docs/KNOWLEDGE-ARCHITECTURE.md)
- Use `HELP CLEAN` and `HELP TIDY` for command help

---

**Version**: 2.0 (November 2025)
