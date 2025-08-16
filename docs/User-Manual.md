# uDOS v1.2 User Manual

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Data Operating System
    ═══════════════ v1.2 ═══════════════
```

**Published**: August 2025  
**Edition**: First Edition  
**System**: Universal Data Operating System v1.2  
**Architecture**: Markdown-Native Terminal Interface

---

## Table of Contents

```
Chapter 1: Getting Started ............................ 3
Chapter 2: Basic Operations ........................... 7
Chapter 3: The Memory System ......................... 11
Chapter 4: Shortcode Magic .......................... 15
Chapter 5: Adventure Mode ........................... 19
Chapter 6: Advanced Features ........................ 23
Chapter 7: System Administration .................... 27
Chapter 8: Troubleshooting ......................... 31

Appendix A: Command Reference ....................... 35
Appendix B: Shortcode Library ....................... 39
Appendix C: ASCII Art Guide ......................... 43
Appendix D: Configuration Files ..................... 47
```

---

## Foreword

Welcome to uDOS v1.2, the Universal Data Operating System. This manual will guide you through your journey from novice user to advanced data wizard.

```
    🧙‍♂️ "Any sufficiently advanced data system
        is indistinguishable from magic."
                    - Arthur C. Clarke (adapted)
```

uDOS transforms your terminal into a living, breathing data realm where commands become spells, files become scrolls, and you become the master of your digital domain.

---

## Chapter 1: Getting Started

### 1.1 What is uDOS?

uDOS is a revolutionary approach to data management that combines:

- **Markdown-native architecture** - Everything is human-readable
- **Adventure-game interface** - Learning through storytelling
- **Visual Basic-inspired scripting** - Accessible programming
- **ASCII art integration** - Beautiful terminal graphics
- **Flat-file simplicity** - No databases, just files

### 1.2 Your First Boot

When you start uDOS, you'll see the startup sequence:

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Data Operating System
    ═══════════════ v1.2 ═══════════════

ℹ️  Validating system integrity...
✅ System validation passed

🌀 System ready - Welcome to uDOS!
```

### 1.3 Character Creation

If this is your first time, you'll enter the **Character Creation Wizard**:

```
⚔️ Phase 1: Character creation

The Guardian of the Data Realm appears before you:
"Greetings, traveler! Before you can enter the realm of uDOS,
you must choose your identity..."

👤 Enter your adventurer name: _
```

Choose your class wisely:

| Class | Description | Specialty |
|-------|-------------|-----------|
| 🧙 **Wizard** | Command-line master | Shortcuts and automation |
| 🪄 **Sorcerer** | Data manipulation expert | Analysis and transformation |
| 👻 **Ghost** | Minimalist wanderer | Clean, efficient interfaces |
| 😈 **Trickster** | Feature experimenter | Beta testing and exploration |
| 📚 **Scholar** | Documentation keeper | Methodical learning |

### 1.4 The Command Prompt

Your adventure begins at the command prompt:

```
🌀 _
```

This simple symbol represents infinite possibility. Type `HELP` to see what you can do.

---

## Chapter 2: Basic Operations

### 2.1 Essential Commands

Every uDOS adventurer should master these fundamental spells:

```ascii
┌─── CORE COMMANDS ───────────────────────────────────┐
│                                                     │
│  STATUS  ⚡ Show system overview                    │
│  HELP    📖 Display this manual                     │
│  GO      🚀 Browse all shortcuts                    │
│  DASH    📊 Live dashboard                          │
│  EXIT    🚪 Leave the realm                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2.2 Command Syntax

uDOS supports two command formats:

#### Direct Commands
```
COMMAND ARGUMENTS
```
Examples:
- `STATUS` - Show system information
- `MEMORY LIST` - List all memory files
- `MISSION CREATE "My Task"` - Create a new mission

#### Shortcode Format
```
[COMMAND|ARGUMENTS]
```
Examples:
- `[MEM|LIST]` - List memory files
- `[PACK|INSTALL|ripgrep]` - Install ripgrep package
- `[DASH|LIVE]` - Start live dashboard

### 2.3 Color Coding System

uDOS uses intelligent color coding to help you navigate:

- **🟡 COMMANDS** - Yellow text for all commands
- **🔵 [SHORTCODES]** - Cyan brackets around shortcodes  
- **🟢 $VARIABLES** - Green text for variables
- **🔵 /paths/** - Blue text for file paths
- **⚪ descriptions** - White text for explanations

### 2.4 Getting Help

```
HELP                    # Full command reference
HELP COMMAND            # Help for specific command
GO                      # Browse shortcuts interactively
TUTORIAL                # Replay the adventure tutorial
```

---

## Chapter 3: The Memory System

### 3.1 Understanding Memory

In uDOS, your "memory" is a collection of markdown files stored in the `uMemory/` directory. Think of it as your personal digital brain.

```ascii
   🧠 uMemory Structure
   ═══════════════════════
   
   📁 uMemory/
   ├── 📄 identity.md
   ├── 📄 001-welcome-mission.md
   ├── 📄 FILE-20250816-HOME-143022.md
   ├── 📄 MISSION-20250816-PROJECT-143500.md
   └── 📄 LOG-20250816-DAILY-180000.md
```

### 3.2 File Naming Convention

All memory files follow a structured naming pattern:

```
TYPE-YYYYMMDD-LOCATION-HHMMSS.md
```

Where:
- **TYPE**: FILE, MISSION, LOG, NOTE, etc.
- **YYYYMMDD**: Date (e.g., 20250816)
- **LOCATION**: Where created (HOME, OFFICE, etc.)
- **HHMMSS**: Time (e.g., 143022 = 2:30:22 PM)

### 3.3 Memory Commands

```ascii
┌─── MEMORY SPELLS ───────────────────────────────────┐
│                                                     │
│  MEM LIST           📋 Show all memory files       │
│  MEM VIEW file.md   👁️  Read a specific file        │
│  MEM EDIT file.md   ✏️  Edit a file                 │
│  MEM SEARCH term    🔍 Search through all files    │
│  MEM CREATE type    ➕ Create new memory file      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3.4 Shortcode Alternatives

For faster memory access, use shortcodes:

```
[MEM|LIST]                    # List files
[MEM|VIEW|filename.md]        # View file
[MEM|EDIT|filename.md]        # Edit file
[MEM|SEARCH|keyword]          # Search files
```

---

## Chapter 4: Shortcode Magic

### 4.1 The Philosophy of Shortcodes

Shortcodes are uDOS's most powerful feature. They're like magical incantations that compress complex operations into simple, readable commands.

```ascii
   🪄 Shortcode Anatomy
   ═══════════════════════
   
   [COMMAND|ARGUMENT1|ARGUMENT2]
    │       │         │
    │       │         └─── Additional parameters
    │       └─────────────── Primary argument
    └─────────────────────── Base command
```

### 4.2 Common Shortcode Patterns

#### Memory Operations
```
[MEM|LIST]                    # List all files
[MEM|VIEW|identity.md]        # View identity file
[MEM|EDIT|new-note.md]        # Create/edit note
```

#### Mission Management
```
[MISSION|CREATE|"Learn uDOS"] # Create new mission
[MISSION|COMPLETE|001]        # Complete mission
[MISSION|LIST]                # Show all missions
```

#### Package System
```
[PACK|LIST]                   # Show packages
[PACK|INSTALL|ripgrep]        # Install ripgrep
[PACK|INFO|bat]               # Package information
```

#### Dashboard Views
```
[DASH|LIVE]                   # Live dashboard
[DASH|MEMORY]                 # Memory statistics
[DASH|MISSIONS]               # Mission overview
```

### 4.3 Interactive Shortcode Builder

Type `GO` to enter the interactive shortcode browser:

```ascii
┌─── uDOS SHORTCODE BROWSER ──────────────────────────┐
│                                                     │
│  1. 📋 Templates    - Pre-built shortcode library  │
│  2. 🔧 Builder      - Step-by-step construction    │
│  3. 🌐 Browse       - Explore all possibilities    │
│  4. 📚 History      - Your recent shortcodes       │
│  5. ❤️  Favorites   - Your saved shortcuts         │
│                                                     │
│  Type number or press Enter for quick builder...   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 4.4 Building Custom Shortcodes

The visual builder helps you construct complex shortcodes:

```
🔧 Shortcode Builder
═══════════════════════

Step 1: Choose base command
  1. MEM     - Memory operations
  2. MISSION - Task management  
  3. PACK    - Package system
  4. DASH    - Dashboard views
  5. EDIT    - File editing

Your choice: 1

Step 2: Choose operation
  1. LIST    - Show all items
  2. VIEW    - Display content
  3. EDIT    - Modify item
  4. SEARCH  - Find items

Your choice: 3

Step 3: Specify target
Enter filename: my-notes.md

✨ Generated shortcode: [MEM|EDIT|my-notes.md]
```

---

## Chapter 5: Adventure Mode

### 5.1 The Trial of First Commands

New users begin their journey with an epic tutorial adventure. This isn't just a boring manual - it's an interactive story that teaches you uDOS through gameplay.

```ascii
   🗡️ THE TRIAL OF FIRST COMMANDS
   ═══════════════════════════════
   
   Chapter 1: The Entrance Hall
   Chapter 2: The Memory Chambers
   Chapter 3: The Shortcode Sanctum
   Chapter 4: The Chamber of Choices
   Bonus: The Hall of Living Code
```

### 5.2 Character Progression

As you use uDOS, you gain experience and unlock new abilities:

```
🎖️ Your Achievements:
  • STATUS Mastery         - View system information
  • Memory Navigation      - Access your data vault
  • Shortcode Magic        - Cast [COMMAND|ARGS] spells
  • Choice Wisdom         - Understanding paths
  • uCode Enlightenment   - Programming knowledge

Total: 85 XP - Accomplished Adventurer! 🏆
```

### 5.3 Adventure Commands

Special commands enhance the adventure experience:

```
TUTORIAL          # Replay the epic tutorial
ACHIEVEMENTS      # View your progress  
LEVEL             # Check experience points
QUEST             # Available challenges
STORY             # Continue your narrative
```

### 5.4 Character Classes and Abilities

Each character class has unique strengths:

#### 🧙 Wizard
- **Specialty**: Command mastery and shortcuts
- **Bonus**: Extra command history and favorites
- **Theme**: Ancient knowledge and efficiency

#### 🪄 Sorcerer  
- **Specialty**: Data manipulation and analysis
- **Bonus**: Enhanced dashboard and metrics
- **Theme**: Magical data transformation

#### 👻 Ghost
- **Specialty**: Minimalist, clean interfaces  
- **Bonus**: Simplified displays and shortcuts
- **Theme**: Invisible efficiency

#### 😈 Trickster
- **Specialty**: Experimental features and beta testing
- **Bonus**: Access to development commands
- **Theme**: Pushing boundaries

#### 📚 Scholar
- **Specialty**: Documentation and methodology
- **Bonus**: Enhanced help and tutorials
- **Theme**: Systematic learning

---

## Chapter 6: Advanced Features

### 6.1 Dashboard System

The dashboard provides real-time insights into your uDOS realm:

```ascii
┌─── uDOS LIVE DASHBOARD ─────────────────────────────┐
│                                                     │
│  📊 System Status    🧠 Memory Usage               │
│  ══════════════      ═══════════════               │
│  Online    ✅        Files: 42                     │
│  Mode: Command       Size:  1.2MB                  │
│  Layout: Standard    Recent: notes.md              │
│                                                     │
│  🎯 Active Missions  📈 Activity Graph             │
│  ════════════════    ════════════════              │
│  Total: 5           ▁▃▅▇█▇▅▃▁                      │
│  Active: 3          Commands today: 87             │
│  Done: 2            Peak hour: 14:00               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

Access dashboard views:
```
DASH              # Interactive dashboard
DASH LIVE         # Auto-updating display
[DASH|MEMORY]     # Memory-focused view  
[DASH|MISSIONS]   # Mission tracking
[DASH|ACTIVITY]   # Usage statistics
```

### 6.2 Layout System

uDOS adapts to your screen and workflow:

```ascii
📐 Layout Presets:
════════════════

  compact     - 80x24   (mobile-friendly)
  standard    - 120x30  (recommended)  
  wide        - 140x35  (spacious)
  coding      - 120x50  (tall, for scripts)
  writing     - 100x35  (narrow, focused)
  dashboard   - 160x40  (wide, data-rich)
  auto        - Smart detection
```

Layout commands:
```
LAYOUT                # Show layout manager
LAYOUT standard       # Switch to standard
LAYOUT auto on        # Enable auto-detection
LAYOUT suggest        # Get recommendations
```

### 6.3 Panel System

Create custom ASCII panels for data visualization:

```ascii
┌─── MEMORY PANEL ────┐  ┌─── STATUS PANEL ────┐
│                     │  │                     │
│ Files: 42           │  │ System: ✅ Online   │
│ Size:  1.2MB        │  │ Mode: Command       │
│ Recent: notes.md    │  │ Layout: Standard    │
│ Status: ✅ Active   │  │ Uptime: 2h 15m      │
│                     │  │                     │
└─────────────────────┘  └─────────────────────┘
```

Panel commands:
```
PANEL                 # Show panel dashboard
PANEL MEMORY          # Memory statistics panel
PANEL STATUS          # System status panel
PANEL GRID            # Custom grid layout
```

### 6.4 Character Font System

Inspired by Acorn BBC Micro, customize your display:

```
🔤 Font Options:
═══════════════

Font Styles:
  • Mono      - Fixed-width (default)
  • Condensed - Compact display  
  • Expanded  - Wide spacing

Character Sets:
  • Basic     - ASCII 32-126
  • Extended  - ASCII + Box Drawing
  • Unicode   - Full Unicode subset

Constraints:
  • Strings: ≤40 characters
  • Panels:  ≤15 lines
  • Items:   ≤8 per panel
```

---

## Chapter 7: System Administration

### 7.1 User Management

Your uDOS identity is stored in `uMemory/identity.md`:

```markdown
# ⚔️ Adventurer Profile

**Name**: YourName  
**Class**: wizard  
**Joined Realm**: 2025-08-16  
**System**: uDOS v1.2

## Character Sheet
- **Equipment**: Standard Orb (balanced viewing)
- **Adventure Style**: Guided Explorer (helpful hints)
- **Memory Type**: Infinite Scroll Architecture
- **Spellbook**: uCode Visual Basic Dialect v1.2

## Current Stats
- **Level**: Accomplished Adventurer
- **Experience**: 85 XP
- **Realm Mastery**: Advanced
- **Favorite Spells**: [MEM|LIST], [DASH|LIVE]
```

### 7.2 Configuration Files

uDOS stores preferences in several locations:

```
~/.udos_history       # Command history
~/.udos_favorites     # Favorite shortcuts
~/.udos_layout        # Layout preferences
uMemory/setup-vars.sh # Environment variables
```

### 7.3 Backup and Restore

Your entire uDOS realm can be backed up simply:

```bash
# Backup
tar -czf udos-backup-$(date +%Y%m%d).tar.gz uMemory/

# Restore  
tar -xzf udos-backup-YYYYMMDD.tar.gz
```

### 7.4 System Reset

The DESTROY command provides clean reset options:

```ascii
⚔️ uDOS Realm Reset
🏰 Choose your path, adventurer:

  [A] Reset Identity    - Clear character, keep data
  [B] Fresh Start      - Complete clean slate
  [C] Archive & Reset  - Save to legacy vault
  [D] Reboot Only      - Restart (no data loss)
  [E] Exit Safely      - Return unchanged
```

---

## Chapter 8: Troubleshooting

### 8.1 Common Issues

#### Command Not Found
```
🌀 ❌ Unknown command: COMMND
Type 'HELP' for available commands or '[' for shortcode browser
```

**Solution**: Check spelling, use `HELP` to see available commands.

#### File Not Found
```
❌ Memory file not found: missing.md
```

**Solution**: Use `MEM LIST` to see available files.

#### Permission Errors
```
❌ Cannot write to file: readonly.md
```

**Solution**: Check file permissions, ensure you have write access.

### 8.2 System Validation

Run system checks:
```
VALIDATE              # Full system check
STATUS                # Quick system overview
HELP SYSTEM           # System-specific help
```

### 8.3 Performance Tips

1. **Keep memory organized** - Use descriptive filenames
2. **Use shortcodes** - Faster than full commands  
3. **Enable auto-layout** - Optimizes for your usage
4. **Regular cleanup** - Archive old missions
5. **Use favorites** - Save frequently used commands

### 8.4 Getting Support

```ascii
📞 Support Channels:
═══════════════════

  HELP              - Built-in documentation
  TUTORIAL          - Interactive learning
  STATUS            - System diagnostics
  VALIDATE          - Health checks
  
  Community:
  • GitHub Issues   - Bug reports
  • Discussions     - Feature requests  
  • Wiki           - Community knowledge
```

---

## Appendix A: Command Reference

### A.1 Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | System overview | `STATUS` |
| `HELP` | Show documentation | `HELP`, `HELP MEM` |
| `GO` | Browse shortcuts | `GO` |
| `DASH` | Dashboard system | `DASH`, `DASH LIVE` |
| `EXIT` | Leave uDOS | `EXIT`, `QUIT`, `BYE` |

### A.2 Memory Commands

| Command | Description | Example |
|---------|-------------|---------|
| `MEM LIST` | List all files | `MEM LIST` |
| `MEM VIEW file` | Display file | `MEM VIEW notes.md` |
| `MEM EDIT file` | Edit file | `MEM EDIT task.md` |
| `MEM SEARCH term` | Search files | `MEM SEARCH project` |

### A.3 Mission Commands

| Command | Description | Example |
|---------|-------------|---------|
| `MISSION LIST` | Show missions | `MISSION LIST` |
| `MISSION CREATE name` | New mission | `MISSION CREATE "Learn uDOS"` |
| `MISSION COMPLETE id` | Finish mission | `MISSION COMPLETE 001` |

### A.4 System Commands

| Command | Description | Example |
|---------|-------------|---------|
| `RESTART` | Restart uDOS | `RESTART`, `REBOOT` |
| `RESET` | Refresh interface | `RESET`, `REFRESH` |
| `DESTROY` | System reset | `DESTROY` |
| `VALIDATE` | System check | `VALIDATE` |

---

## Appendix B: Shortcode Library

### B.1 Memory Shortcodes

```
[MEM|LIST]                    # List all memory files
[MEM|VIEW|filename.md]        # View specific file
[MEM|EDIT|filename.md]        # Edit/create file
[MEM|SEARCH|keyword]          # Search through files
[MEM|CREATE|type]             # Create new file
```

### B.2 Mission Shortcodes

```
[MISSION|LIST]                # Show all missions
[MISSION|CREATE|"Task Name"]  # Create new mission
[MISSION|COMPLETE|001]        # Mark mission complete
[MISSION|VIEW|mission-id]     # View mission details
```

### B.3 Package Shortcodes

```
[PACK|LIST]                   # Available packages
[PACK|INSTALL|package-name]   # Install package
[PACK|INFO|package-name]      # Package information
[PACK|UPDATE|package-name]    # Update package
```

### B.4 Dashboard Shortcodes

```
[DASH|LIVE]                   # Live updating dashboard
[DASH|MEMORY]                 # Memory-focused view
[DASH|MISSIONS]               # Mission tracking
[DASH|ACTIVITY]               # Usage statistics
[DASH|SYSTEM]                 # System monitoring
```

---

## Appendix C: ASCII Art Guide

### C.1 uDOS ASCII Elements

#### Box Drawing Characters
```
┌─┬─┐  ╔═╦═╗  ╭─┬─╮
├─┼─┤  ╠═╬═╣  ├─┼─┤
└─┴─┘  ╚═╩═╝  ╰─┴─╯
```

#### Progress Indicators  
```
▁▃▅▇█▇▅▃▁    Progress bars
░▒▓█         Density indicators
◯◐◑●         Loading spinners
```

#### Interface Elements
```
🌀  Main prompt symbol
⚡  Status indicators
📊  Dashboard elements
🧠  Memory system
🎯  Mission system
```

### C.2 Panel Templates

#### Standard Panel
```ascii
┌─── TITLE ───────────┐
│                     │
│  Content line 1     │
│  Content line 2     │
│  Content line 3     │
│                     │
└─────────────────────┘
```

#### Data Panel
```ascii
┌─ METRICS ────┐
│ Item:    42  │
│ Size:  1.2MB │
│ Status:  ✅  │
└──────────────┘
```

---

## Appendix D: Configuration Files

### D.1 Identity File (`uMemory/identity.md`)

```markdown
# ⚔️ Adventurer Profile

**Name**: [Your Name]
**Class**: [wizard|sorcerer|ghost|trickster|scholar]
**Joined Realm**: [Date]
**System**: uDOS v1.2

## Character Sheet
- **Equipment**: [Display preference]
- **Adventure Style**: [Workflow preference]
- **Memory Type**: Infinite Scroll Architecture
- **Spellbook**: uCode Visual Basic Dialect v1.2

## Current Stats
- **Level**: [Experience level]
- **Experience**: [XP points]
- **Realm Mastery**: [Skill level]
- **Favorite Spells**: [Preferred commands]
```

### D.2 Environment Variables (`uMemory/setup-vars.sh`)

```bash
#!/bin/bash
# uDOS realm configuration

export UDOS_USER="[username]"
export UDOS_ROLE="[character class]"
export UDOS_SCREEN_PREF="[layout preference]"
export UDOS_WORKFLOW="[workflow style]"
export UDOS_VERSION="v1.2"
export UDOS_SETUP_DATE="[setup date]"
export UDOS_MEMORY_TYPE="flat"
```

### D.3 Layout Configuration (`~/.udos_layout`)

```bash
# uDOS Layout Configuration
CURRENT_LAYOUT="standard"
AUTO_LAYOUT=true
PREFERRED_CODING_LAYOUT="coding"
PREFERRED_WRITING_LAYOUT="writing"
PREFERRED_DASHBOARD_LAYOUT="dashboard"
```

---

## Index

**A**
Adventure mode, 19
ASCII art, 43
Authentication, 27

**B**
Backup, 27
Box drawing, 43

**C**
Character creation, 3
Commands, 7
Configuration, 47

**D**
Dashboard, 23
DESTROY command, 27

**E**
Experience points, 19

**F**
File naming, 11
Favorites, 15

**G**
Getting started, 3

**H**
Help system, 7
History, 15

**L**
Layout system, 23

**M**
Memory system, 11
Missions, 15

**P**
Panels, 23
Permissions, 31

**S**
Shortcodes, 15
System reset, 27

**T**
Tutorial, 19
Troubleshooting, 31

**U**
User management, 27

---

**End of Manual**

*uDOS v1.2 User Manual - First Edition*  
*Published August 2025*  
*Universal Data Operating System*
