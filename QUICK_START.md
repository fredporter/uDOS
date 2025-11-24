# uDOS Quick Start Guide

## System Ready! ✅

All startup issues have been resolved. The system is stable and ready for use.

## Starting uDOS

### Option 1: Using the startup script (Recommended)
```bash
cd /Users/fredbook/Code/uDOS
./start_udos.sh
```

### Option 2: Direct Python execution
```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python3 uDOS.py
```

## First Run

On first startup, you may see:
```
🏥 System health... ❌ Issues
  ❌ 1 critical issue(s) detected - run REPAIR for details
  Attempt auto-repair? (y/n/OK):
```

**Type `y` and press Enter** to let the system create missing files automatically.

## Basic Commands

Once started, try these commands:

```
help              # Show all available commands
help <command>    # Get help on specific command
status            # Show system status
viewport          # Show terminal size
blank             # Clear screen

# File operations (all in /memory)
new story myfile  # Create new file
edit myfile       # Edit file
show myfile       # Display file

# Navigation
workspace         # Manage workspaces (sandbox/workflow/legacy)
memory            # Access memory tiers
guide             # Browse knowledge guides

# System
repair            # Run system diagnostics
reboot            # Restart uDOS
exit              # Quit (or Ctrl+D)
```

## Understanding the Structure

### `/knowledge` - Read-Only System Content
- Bundled with uDOS
- Contains: guides, templates, reference material
- **Never edit these files**
- Updated when uDOS is updated

### `/memory` - Your Workspace
- **This is where you work**
- All your files go here
- Three main areas:
  - `sandbox/` - Temporary work, experiments
  - `workflow/` - Active projects and missions
  - `legacy/` - Archived outcomes and learnings

## Workflow

1. **Start in sandbox**: Draft, experiment, test ideas
2. **Move to workflow**: Commit to active projects
3. **Archive to legacy**: Preserve completed work

## Testing the System

Run automated tests:
```bash
python3 test_system.py
```

All tests should pass with ✅

## Troubleshooting

### System won't start
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
./start_udos.sh
```

### Missing commands.json or other files
Type `y` when prompted for auto-repair, or run:
```
repair
```

### Python 3.9 warnings
These are non-critical. Consider upgrading to Python 3.10+ for better performance.

## License

- ✅ **Personal use**: Free for personal, educational, non-commercial use
- ✅ **Your data**: You own all content in `/memory`
- ❌ **Commercial use**: Requires separate license

## Getting Help

- Type `help` in uDOS for command reference
- Check `/knowledge/system/` for documentation
- Wiki: https://github.com/fredporter/uDOS/wiki

## Current Status (2025-11-22)

✅ All startup issues resolved
✅ System initialization works
✅ Interactive & piped modes functional
✅ REBOOT command works
✅ Auto-repair works
✅ Empty input handled
✅ Knowledge/memory separation verified

**The system is stable and ready for production use outside VSCode!**

---

*Last updated: 2025-11-22*
*uDOS v1.0.0 - Smart Commands & Interactive System*
