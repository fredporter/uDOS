# ⚠️ Documentation Moved

> **This file has been superseded by the wiki.**

For current command reference and quick start guides, see:
- **[Command Reference](../wiki/Command-Reference.md)** - Complete command documentation with quick reference
- **[Quick Start](../wiki/Quick-Start.md)** - Getting started guide
- **[CLI Features](../wiki/CLI-Features-v1-0-6.md)** - v1.0.6 CLI enhancements

---

# uDOS Quick Reference Guide (LEGACY - v1.0.6)

## 🚀 Quick Start

### Essential Commands
```bash
# File Operations
LIST                      # List files in current directory
LOAD <file>              # Load file into memory
SAVE <file>              # Save current content
EDIT <file>              # Edit file

# Grid Management
GRID                     # Show current grid
NEW GRID                 # Create new grid
GRID LIST                # List all grids
SHOW GRID <name>         # Display specific grid

# Navigation
MAP                      # Show current map
GOTO <location>          # Jump to location
MOVE <direction>         # Move in direction
LEVEL                    # Show current level
GODOWN                   # Descend one level
GOUP                     # Ascend one level

# System
STATUS                   # System status
VIEWPORT                 # Display info
REPAIR                   # Run diagnostics
HELP                     # Command help
```

## 📋 Command Reference

### File Operations
| Command | Description | Example |
|---------|-------------|---------|
| `LIST [path]` | List directory contents | `LIST data/` |
| `LOAD <file>` | Load file into memory | `LOAD config.json` |
| `SAVE <file>` | Save current content | `SAVE output.txt` |
| `EDIT <file>` | Edit file | `EDIT README.md` |

### Grid Management
| Command | Description | Example |
|---------|-------------|---------|
| `GRID` | Display current grid | `GRID` |
| `NEW GRID [name]` | Create new grid | `NEW GRID workspace` |
| `GRID LIST` | List all grids | `GRID LIST` |
| `SHOW GRID <name>` | Show specific grid | `SHOW GRID main` |

### Navigation
| Command | Description | Example |
|---------|-------------|---------|
| `MAP` | Display current map | `MAP` |
| `GOTO <location>` | Jump to location | `GOTO A5` |
| `MOVE <direction>` | Move in direction | `MOVE NORTH` |
| `LEVEL` | Show current level | `LEVEL` |
| `GODOWN` | Descend one level | `GODOWN` |
| `GOUP` | Ascend one level | `GOUP` |

### System Commands
| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | Show system status | `STATUS` |
| `VIEWPORT` | Display viewport info | `VIEWPORT` |
| `PALETTE` | Show color palette | `PALETTE` |
| `REPAIR` | Run system diagnostics | `REPAIR` |
| `REBOOT` | Restart system | `REBOOT` |

### Auto-Resize
- Automatically adapts to terminal size changes
- Mobile-friendly responsive design
- Wide-screen enhancements

## ⌨️ Tab Completion Features

### Smart Completion
- **Fuzzy matching** - Type partial commands
- **Context awareness** - Parameter suggestions
- **History integration** - Recent command priority
- **File path completion** - Workspace-aware

### Examples
```bash
THM<TAB>          # Expands to THEME
THEME S<TAB>      # Suggests SET
FILE SEARCH *.p<TAB>  # Completes to *.py
```

## 💾 Session Types

### Session Categories
- **Manual** - User-created sessions
- **Automatic** - Auto-saved at intervals
- **Checkpoint** - Milestone markers
- **Backup** - Safety snapshots

### What's Saved
### History Commands
| Command | Description | Example |
|---------|-------------|---------|
| `UNDO` | Undo last action | `UNDO` |
| `REDO` | Redo undone action | `REDO` |
| `RESTORE <state>` | Restore to saved state | `RESTORE checkpoint1` |

### Automation
| Command | Description | Example |
|---------|-------------|---------|
| `RUN <script>` | Execute script file | `RUN setup.uscript` |

### Assisted Task
| Command | Description | Example |
|---------|-------------|---------|
| `OK <task>` | AI-assisted task execution | `OK analyze data` |
| `READ <content>` | Read and process content | `READ file.txt` |

### Utilities
| Command | Description | Example |
|---------|-------------|---------|
| `HELP [command]` | Show help information | `HELP GRID` |
| `CLEAR` | Clear screen | `CLEAR` |
| `SETUP` | Run setup wizard | `SETUP` |

## 🔍 Command Categories

### Core Operations
Commands organized by function:

1. **File Operations** - LIST, LOAD, SAVE, EDIT
2. **Grid Management** - GRID, NEW GRID, GRID LIST, SHOW GRID
3. **Navigation** - MAP, GOTO, MOVE, LEVEL, GODOWN, GOUP
4. **System** - REBOOT, STATUS, VIEWPORT, PALETTE, REPAIR
5. **History** - UNDO, REDO, RESTORE
6. **Automation** - RUN
7. **Assisted Task** - OK, READ
8. **Utilities** - HELP, CLEAR, SETUP
