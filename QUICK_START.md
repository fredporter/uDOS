# uDOS Quick Start Guide

## Welcome to uDOS v1.1.2! ✅

uDOS is production-ready with **1,062 passing tests**, enterprise security, and dual-interface support (Terminal + Web GUI).

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

On first startup, you'll see the welcome screen showing your current role and installation type:

```
==================================================
Welcome to uDOS v1.1.2
==================================================

Current Role: User (offline-first mode)
Installation Type: CLONE (full repository)

Type 'help' for available commands
Type 'guide list' to browse survival knowledge
```

## Basic Commands

Once started, try these commands:

```
help              # Show all available commands
help <command>    # Get help on specific command
status            # Show system status
version           # Show version (v1.1.2)

# Knowledge & Learning
guide list        # List all survival guides
guide start <name>  # Start interactive guide
learn search <topic>  # Search knowledge base
docs <command>    # Command documentation

# File operations (memory tier system)
memory tier       # Show 4-tier memory structure
file list         # List files in current tier
file edit <file>  # Edit file
file show <file>  # Display file

# Security & Configuration
config role       # Show current role (User/Power/Wizard/Root)
config install    # Show installation type
memory encrypt <file>  # Encrypt file (Private tier)

# Web GUI (if enabled)
web start         # Start web server
web open          # Open in browser
web status        # Check server status

# Navigation
workspace         # Manage workspaces
memory            # Access memory tiers
exit              # Quit (or Ctrl+D)
```

## Understanding the Structure

### `/knowledge` - Read-Only Knowledge Library
- Bundled with uDOS (74+ guides in 8 categories)
- Contains: survival guides, medical, food, water, tech, reference
- **Never edit these files** - they're system content
- Updated when uDOS is updated
- Access via `guide list` and `learn search`

### `/memory` - Your Workspace (4-Tier System)
- **This is where you work**
- All your files go here
- Four security tiers:
  - **Tier 1 (Private)**: AES-256 encrypted, user-only (100MB quota)
  - **Tier 2 (Shared)**: AES-128 encrypted, team collaboration (500MB quota)
  - **Tier 3 (Community)**: Plain text, group knowledge sharing (1GB quota)
  - **Tier 4 (Public)**: Open knowledge base (5GB quota)
- Three main areas:
  - `sandbox/` - Temporary work, experiments
  - `workflow/` - Active projects and missions
  - `legacy/` - Archived outcomes and learnings

## v1.1.2 Features

### Security (RBAC)
- **User Role**: Offline-first, restricted access, safe for general use
- **Power Role**: Trusted user, web access, API features
- **Wizard Role**: Developer mode, full system access, debugging
- **Root Role**: Admin, installation management, system configuration

### Web GUI
- Production server with Teletext display
- Browser extension for knowledge capture (Chrome/Firefox/Edge)
- Mobile PWA with offline support
- Real-time CLI↔Web synchronization

### Offline Knowledge
- 74+ curated survival guides (foundation for 500+)
- AI prompt development (no API calls required)
- SVG diagram generation with citations
- Content validation and quality scoring

## Workflow

1. **Start in sandbox**: Draft, experiment, test ideas
2. **Validate work**: Review and test your content
3. **Promote to tier**: Move to appropriate security level
4. **Archive to legacy**: Preserve completed work and learnings

## Testing the System

Run automated tests:
```bash
# All v1.1.x tests (1,062 tests)
pytest memory/tests/test_v1_1_*.py

# Specific milestone
pytest memory/tests/test_v1_1_0_*.py  # v1.1.0 (268 tests)
pytest memory/tests/test_v1_1_1_*.py  # v1.1.1 (327 tests)
pytest memory/tests/test_v1_1_2_*.py  # v1.1.2 (467 tests)
```

All 1,062 tests should pass ✅

## Troubleshooting

### System won't start
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./start_udos.sh
```

### Missing dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Web GUI won't start
```bash
# Check if web dependencies are installed
pip install flask flask-cors flask-socketio

# Start web server
python uDOS.py
# Then type: web start
```

## Getting Help

- Type `help` in uDOS for command reference
- Check `/knowledge/system/` for system documentation
- Wiki: https://github.com/fredporter/uDOS/wiki
- Full documentation: [Release v1.1.2](wiki/Release-v1.1.2.md)

## Current Status (2025-11-24)

✅ v1.1.2 Production Release
✅ 1,062 tests passing (100%)
✅ Full cross-platform support (macOS/Linux/Windows)
✅ Enterprise security (RBAC, encryption)
✅ Dual interface (Terminal + Web GUI)
✅ Offline knowledge library (74+ guides)
✅ Zero breaking changes from v1.0.x

**The system is production-ready for serious use!**

---

*Last updated: 2025-11-24*
*uDOS v1.1.2 - Secure Dual-Interface Framework with Offline Knowledge*
