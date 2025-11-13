# Getting Started with uDOS

**Welcome to The People's Operating System!**

This guide will get you from zero to productive in 30 minutes. No prior experience with command-line interfaces required.

---

## Table of Contents

1. [What is uDOS?](#what-is-udos)
2. [Installation](#installation)
3. [First Launch](#first-launch)
4. [Your First 5 Minutes](#your-first-5-minutes)
5. [Essential Commands](#essential-commands)
6. [Basic Workflows](#basic-workflows)
7. [Common Beginner Mistakes](#common-beginner-mistakes)
8. [Learning Path](#learning-path)
9. [Getting Help](#getting-help)
10. [Next Steps](#next-steps)

---

## What is uDOS?

**uDOS** (μDOS - Micro DOS) is a text-based knowledge repository and productivity system. Think of it as:

- 📚 **A personal library** for organizing information
- 💻 **A productivity tool** for focused work
- 🎓 **A learning environment** for skill development
- 🔧 **An automation platform** for repetitive tasks

**Not** a traditional operating system - runs on top of your existing OS (macOS, Linux, Windows).

### Why Text-Only?

- ⚡ **Lightning fast** - loads instantly, searches in milliseconds
- 🌍 **Universal** - works anywhere, on any device
- 📖 **Future-proof** - text files from 1970s still work today
- ♿ **Accessible** - screen readers work perfectly
- 🔋 **Efficient** - runs on 20+ year old hardware

**Learn more**: [Why uDOS](Why-uDOS.md) | [Text-First Computing](Text-First-Computing.md) | [Philosophy](Philosophy.md)

---

## Installation

### Prerequisites

- **Python 3.8+** (check: `python3 --version`)
- **Git** (optional, for cloning)
- **Terminal** (macOS Terminal, Linux terminal, Windows Terminal/WSL)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Install dependencies
pip3 install -r requirements.txt

# Run uDOS
./start_udos.sh
```

### Detailed Installation Steps

#### macOS

1. **Open Terminal** (⌘ + Space, type "Terminal")

2. **Check Python version**:
   ```bash
   python3 --version
   ```
   Should show Python 3.8 or higher. If not: `brew install python3`

3. **Clone uDOS**:
   ```bash
   cd ~/Documents  # or wherever you want uDOS
   git clone https://github.com/fredporter/uDOS.git
   cd uDOS
   ```

4. **Install requirements**:
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Launch uDOS**:
   ```bash
   ./start_udos.sh
   ```

#### Linux

```bash
# Ensure Python 3.8+ is installed
sudo apt update && sudo apt install python3 python3-pip git

# Clone and setup
cd ~
git clone https://github.com/fredporter/uDOS.git
cd uDOS
pip3 install -r requirements.txt

# Launch
./start_udos.sh
```

#### Windows (WSL)

1. Install WSL: https://aka.ms/wsl
2. Open Ubuntu/WSL terminal
3. Follow Linux instructions above

---

## First Launch

When you run `./start_udos.sh` for the first time, you'll see:

```
┌─────────────────────────────────────┐
│         μDOS v1.0.15                │
│    The People's Operating System    │
└─────────────────────────────────────┘

Initializing system...
Loading configuration...
Welcome to uDOS!

🔮 >
```

The `🔮 >` is the **command prompt** - where you type commands.

### First-Time Setup

uDOS may ask a few questions:

```
📋 First-time setup detected.

1. Choose your theme:
   [1] Classic (green on black)
   [2] Amber (amber on black)
   [3] Matrix (bright green on black)

Choice: 1

2. Enable AI assistant? (requires API key)
   [Y/n]: n

Setup complete! Type HELP to see available commands.
```

**Don't worry** - you can change these settings anytime with the `SETUP` command.

---

## Your First 5 Minutes

Let's learn the basics by doing. Type these commands one at a time:

### 1. See All Commands (30 seconds)

```bash
🔮 > HELP
```

This shows all available commands organized by category. Don't try to memorize - just notice the categories.

### 2. Check System Status (30 seconds)

```bash
🔮 > STATUS
```

Shows your uDOS system info - version, memory usage, current location.

### 3. List Files (1 minute)

```bash
🔮 > LIST
```

Shows files in your current directory. Similar to `ls` on Unix or `dir` on Windows.

Try listing a specific folder:
```bash
🔮 > LIST knowledge
```

### 4. Read a File (1 minute)

```bash
🔮 > CAT knowledge/README.md
```

Displays the content of a file (like `cat` on Unix or `type` on Windows).

### 5. Get Help on a Command (1 minute)

```bash
🔮 > HELP LIST
```

Shows detailed help for the LIST command, including examples.

### 6. Clear the Screen (30 seconds)

```bash
🔮 > CLEAR
```

Clears the terminal. Fresh start!

**🎉 Congratulations!** You just learned the 6 most essential commands. That's enough to be productive.

---

## Essential Commands

These 15 commands cover 90% of daily uDOS usage:

### Getting Help
| Command | What It Does | Example |
|---------|-------------|---------|
| `HELP` | Show all commands | `HELP` |
| `HELP <command>` | Help for specific command | `HELP COPY` |
| `HELP DETAILED` | Complete documentation | `HELP DETAILED` |

### File Operations
| Command | What It Does | Example |
|---------|-------------|---------|
| `LIST [path]` | List directory contents | `LIST data/` |
| `CAT <file>` | Display file content | `CAT README.md` |
| `COPY <from> <to>` | Copy file | `COPY notes.md backup.md` |
| `EDIT <file>` | Edit file | `EDIT todo.txt` |
| `MKDIR <name>` | Create directory | `MKDIR projects` |
| `DELETE <file>` | Delete file | `DELETE old.txt` |

### System Commands
| Command | What It Does | Example |
|---------|-------------|---------|
| `STATUS` | System status | `STATUS` |
| `CLEAR` | Clear screen | `CLEAR` |
| `PATH` | Show current directory | `PATH` |
| `THEME <name>` | Change theme | `THEME matrix` |
| `QUIT` | Exit uDOS | `QUIT` |

**Tip**: uDOS commands are NOT case-sensitive. `help`, `HELP`, and `Help` all work.

---

## Basic Workflows

### Workflow 1: Reading and Organizing Knowledge (5 minutes)

**Goal**: Explore the knowledge library and add a note.

```bash
# See what knowledge categories exist
🔮 > LIST knowledge

# Explore survival knowledge
🔮 > LIST knowledge/survival

# Read a survival guide
🔮 > CAT knowledge/survival/first-aid.md

# Create your own note
🔮 > EDIT knowledge/personal/my-notes.md
```

In the editor (nano by default):
1. Type your note
2. Press `Ctrl+O` to save (then Enter)
3. Press `Ctrl+X` to exit

**Verify your note was saved**:
```bash
🔮 > CAT knowledge/personal/my-notes.md
```

### Workflow 2: File Management (5 minutes)

**Goal**: Organize some files.

```bash
# Create a project folder
🔮 > MKDIR my-project

# Create a text file
🔮 > EDIT my-project/README.md
# (Write something, save with Ctrl+O, exit with Ctrl+X)

# Copy it
🔮 > COPY my-project/README.md my-project/README-backup.md

# List the folder to see both files
🔮 > LIST my-project

# Move into the folder (if you have CD/navigation)
🔮 > CD my-project
🔮 > PATH  # Shows you're now in my-project
```

### Workflow 3: Searching Knowledge (3 minutes)

**Goal**: Find information quickly.

```bash
# Search for "water" in knowledge base
🔮 > FIND "water" knowledge/

# Search for multiple terms
🔮 > FIND "first aid" knowledge/survival/

# List all Markdown files
🔮 > LIST knowledge/*.md
```

**Note**: FIND command syntax may vary - use `HELP FIND` for your version.

### Workflow 4: Using Scripts/Automation (5 minutes)

**Goal**: Run a simple uCODE script.

uDOS has a scripting language called **uCODE** for automation.

```bash
# Look at example scripts
🔮 > LIST examples

# Run a simple script
🔮 > RUN examples/hello-automation.uscript
```

**Create your own simple script**:
```bash
🔮 > EDIT my-first-script.uscript
```

In the editor, type:
```
# My First Script
ECHO "Hello from my script!"
LIST
STATUS
```

Save (Ctrl+O) and exit (Ctrl+X), then run:
```bash
🔮 > RUN my-first-script.uscript
```

**Learn more**: [uCODE Language](uCODE-Language.md)

---

## Common Beginner Mistakes

### Mistake #1: Forgetting quotes for paths with spaces

❌ **Wrong**:
```bash
COPY my file.txt new file.txt
```

✅ **Right**:
```bash
COPY "my file.txt" "new file.txt"
```

### Mistake #2: Using wrong slash direction

uDOS uses Unix-style forward slashes (`/`), even on Windows.

❌ **Wrong**: `LIST data\knowledge`
✅ **Right**: `LIST data/knowledge`

### Mistake #3: Not using HELP when stuck

When in doubt:
```bash
HELP              # See all commands
HELP <command>    # See specific command help
```

### Mistake #4: Expecting GUI features

uDOS is text-only. No mouse, no windows, no icons. This is intentional!

- **Need to see images?** Use external viewer
- **Need to edit rich documents?** Convert to Markdown
- **Need a web browser?** Use `WEB <url>` (if extension loaded)

**Learn why this is powerful**: [Text-First Computing](Text-First-Computing.md)

### Mistake #5: Not experimenting

**uDOS is safe to experiment with!**

- Files aren't deleted unless you explicitly `DELETE` them
- `UNDO` exists for many operations
- Your system OS isn't affected

**Pro tip**: Create a `sandbox/` folder for experiments:
```bash
MKDIR sandbox
CD sandbox
# Experiment freely!
```

---

## Learning Path

### Beginner (Week 1) ✅ You Are Here

**Goal**: Learn essential commands and basic workflows.

- [ ] Install uDOS
- [ ] Learn `HELP`, `STATUS`, `LIST`, `CAT`
- [ ] Create and edit a few files
- [ ] Explore the knowledge/ directory
- [ ] Run an example script

**Time**: 30 minutes to 2 hours

**Resources**:
- This guide (you're reading it!)
- [Command Reference - Quick Reference section](Command-Reference.md#quick-reference-card)
- [FAQ](FAQ.md)

### Intermediate (Week 2-3)

**Goal**: Customize uDOS and build productivity workflows.

- [ ] Change themes and settings
- [ ] Create a personal knowledge organization system
- [ ] Write basic uCODE scripts
- [ ] Set up automated tasks
- [ ] Explore grid system (if available)

**Time**: 2-5 hours

**Resources**:
- [Workflows](Workflows.md)
- [uCODE Language](uCODE-Language.md)
- [Command Reference](Command-Reference.md) (full reference)

### Advanced (Month 2+)

**Goal**: Master uDOS and contribute to the community.

- [ ] Build complex automation scripts
- [ ] Contribute knowledge to the library
- [ ] Customize with extensions
- [ ] Map system and navigation (if available)
- [ ] Contribute code or documentation

**Time**: Ongoing

**Resources**:
- [Architecture](Architecture.md)
- [Contributing](Contributing.md)
- [Dev Rounds Workflow](Dev-Rounds-Workflow.md)
- [Extensions System](Extensions-System.md)

---

## Getting Help

### Built-In Help

1. **HELP command** (your first stop):
   ```bash
   HELP              # All commands
   HELP <command>    # Specific command
   HELP DETAILED     # Everything
   ```

2. **STATUS command** (troubleshooting):
   ```bash
   STATUS            # Check system state
   ```

3. **REPAIR command** (diagnostics):
   ```bash
   REPAIR            # Run diagnostics
   ```

### Documentation

- **[FAQ](FAQ.md)** - Common questions
- **[Command Reference](Command-Reference.md)** - All commands in detail
- **[Wiki README](README.md)** - Complete documentation index

### Community

- **GitHub Issues**: https://github.com/fredporter/uDOS/issues
- **Discussions**: https://github.com/fredporter/uDOS/discussions
- **Wiki**: https://github.com/fredporter/uDOS/wiki

### Troubleshooting

**Problem: Command not found**
```bash
🔮 > HELP
# Find the correct command name
```

**Problem: File not found**
```bash
🔮 > PATH         # Where am I?
🔮 > LIST         # What files exist here?
🔮 > CD ..        # Go up one directory
```

**Problem: Permission denied**
```bash
# On Unix/Linux, you may need to make start_udos.sh executable:
chmod +x start_udos.sh
```

**Problem: Python errors**
```bash
# Check Python version
python3 --version

# Reinstall requirements
pip3 install -r requirements.txt --upgrade
```

**Still stuck?** Open a GitHub issue with:
- What you tried to do
- The exact command you ran
- The error message
- Your OS and Python version

---

## Next Steps

You've completed the Getting Started guide! Here's what to explore next:

### 1. Deep Dive into One Topic

Choose what interests you most:

- **Knowledge Management** → [Knowledge Architecture](Knowledge-Architecture.md)
- **Automation** → [uCODE Language](uCODE-Language.md)
- **Philosophy** → [Why uDOS](Why-uDOS.md) and [Human-Centric Design](Human-Centric-Design.md)
- **All Commands** → [Command Reference](Command-Reference.md)

### 2. Customize Your Setup

```bash
🔮 > SETUP         # Run setup wizard
🔮 > THEME list    # See available themes
🔮 > HELP CONFIG   # Learn about configuration
```

### 3. Build Your Knowledge Library

Start collecting and organizing information:

```bash
# Create your personal knowledge area
🔮 > MKDIR knowledge/personal

# Organize by topics
🔮 > MKDIR knowledge/personal/projects
🔮 > MKDIR knowledge/personal/learning
🔮 > MKDIR knowledge/personal/ideas

# Start writing!
🔮 > EDIT knowledge/personal/ideas/great-idea.md
```

**Learn more**: [Content Curation](Content-Curation.md) *(coming soon)*

### 4. Try Advanced Features

Once comfortable with basics:

- **Grid System**: Organize data in 2D grids
- **Map/Navigation**: NetHack-style spatial navigation
- **Extensions**: Web extensions, teletext graphics
- **AI Assistant**: If you have an API key

### 5. Contribute

Love uDOS? Help make it better:

- **Add knowledge** to the library
- **Report bugs** or suggest features
- **Write documentation** or examples
- **Contribute code**

**Learn how**: [Contributing](Contributing.md)

---

## Quick Reference Card (Print/Save)

```
═══════════════════════════════════════════════════════════
                  uDOS QUICK REFERENCE
═══════════════════════════════════════════════════════════

GETTING HELP
  HELP                    - Show all commands
  HELP <command>          - Help for specific command
  STATUS                  - System status

FILES
  LIST [path]             - List directory
  CAT <file>              - Display file
  EDIT <file>             - Edit file
  COPY <from> <to>        - Copy file
  MKDIR <name>            - Create directory
  DELETE <file>           - Delete file

NAVIGATION
  PATH                    - Current directory
  CD <path>               - Change directory

SYSTEM
  CLEAR                   - Clear screen
  THEME <name>            - Change theme
  SETUP                   - Configuration wizard
  QUIT                    - Exit uDOS

AUTOMATION
  RUN <script>            - Run uCODE script

TIPS
  • Commands are NOT case-sensitive
  • Use quotes for paths with spaces: "my file.txt"
  • Use forward slashes: data/files (not data\files)
  • Experiment in sandbox/ directory
  • HELP is your friend!

═══════════════════════════════════════════════════════════
```

---

## Welcome to the Community!

You're now part of the uDOS community - people who value:

- 🧠 **Knowledge over entertainment**
- 🔧 **Empowerment over dependency**
- 🌱 **Sustainability over planned obsolescence**
- 🤝 **Open source over corporate control**
- 📖 **Learning over confusion**

**This is The People's Operating System.**

We're glad you're here.

---

## Appendix: Installation Troubleshooting

### Python not found

**macOS**:
```bash
brew install python3
```

**Ubuntu/Debian Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Windows**: Download from https://python.org

### Git not found

**macOS**:
```bash
xcode-select --install
# or
brew install git
```

**Linux**:
```bash
sudo apt install git
```

**Windows**: Download from https://git-scm.com

### Requirements install fails

```bash
# Try upgrading pip first
pip3 install --upgrade pip

# Then install requirements
pip3 install -r requirements.txt

# If specific package fails, install individually
pip3 install google-generativeai  # example
```

### Permission errors on start_udos.sh

```bash
# Make executable
chmod +x start_udos.sh

# Run
./start_udos.sh
```

### Display/character encoding issues

```bash
# Set UTF-8 encoding (add to ~/.bashrc or ~/.zshrc)
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

---

**Last Updated**: November 14, 2025
**Version**: v1.0.15
**Feedback**: Open an issue or discussion on GitHub

**Next**: [Command Reference](Command-Reference.md) | [Philosophy](Philosophy.md) | [FAQ](FAQ.md)
