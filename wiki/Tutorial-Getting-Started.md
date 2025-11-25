# Getting Started Tutorial - Interactive Walkthrough

Learn uDOS through hands-on examples with ASCII diagrams and real code.

## 📚 Tutorial Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    uDOS LEARNING PATH                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Installation        [■■■■■□□□□□] 50% Complete          │
│  Step 2: First Commands      [■■■□□□□□□□] 30% Complete          │
│  Step 3: Knowledge Bank      [■□□□□□□□□□] 10% Complete          │
│  Step 4: uCODE Scripts       [□□□□□□□□□□]  0% Complete          │
│  Step 5: Extensions          [□□□□□□□□□□]  0% Complete          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Estimated Time:** 30-45 minutes
**Prerequisites:** Terminal, Python 3.9+, Git
**Difficulty:** Beginner

---

## Step 1: Installation

### 1.1 Clone and Setup

```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 1.2 First Launch

```bash
./start_udos.sh
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════════╗
║                         uDOS v1.4.0                              ║
║                 Universal Digital Operating System               ║
╚══════════════════════════════════════════════════════════════════╝

Initializing systems...
✓ Configuration loaded
✓ Knowledge bank ready (166 guides)
✓ Extensions available (4 active)
✓ uCODE validator ready

🔮 >
```

**You're in!** The `🔮 >` prompt means uDOS is ready for commands.

### 1.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     uDOS ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User Input → Command Parser → uCODE Translator → Executor     │
│      ↑                                                    ↓      │
│      └──────────────── Response ←───────────────────────┘       │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  Knowledge   │  │  Extensions  │  │  Config      │        │
│   │  Bank        │  │  System      │  │  Manager     │        │
│   │  (guides/    │  │  (web/cli)   │  │  (.env/json) │        │
│   │  diagrams)   │  │              │  │              │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 2: First Commands

### 2.1 Basic Commands

**Try these commands** (type them at the `🔮 >` prompt):

```bash
🔮 > HELP
```

**Output:**
```
Available Commands:
  HELP               - Show this help message
  STATUS             - System status and health check
  VERSION            - Display version information
  CONFIG             - Configuration management
  GENERATE           - Generate knowledge content
  SEARCH             - Search knowledge bank
  REFRESH            - Update content to standards
  ...
```

```bash
🔮 > STATUS
```

**Output:**
```
┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM STATUS                               │
├─────────────────────────────────────────────────────────────────┤
│ Version:          1.4.0                                         │
│ Python:           3.11.5                                        │
│ Knowledge Guides: 166 guides across 8 categories               │
│ Diagrams:         68 multi-format diagrams                     │
│ Extensions:       4 active, 0 disabled                         │
│ API Status:       ✓ Gemini (online) / ✓ Offline mode ready    │
│ uCODE Validator:  ✓ Operational                                │
└─────────────────────────────────────────────────────────────────┘
```

```bash
🔮 > VERSION
```

**Output:**
```
uDOS v1.4.0 - Universal Digital Operating System
Released: November 25, 2025
Python: 3.11.5
License: MIT
```

### 2.2 Command Syntax

uDOS commands follow simple patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND PATTERNS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Simple Command:                                             │
│     COMMAND                                                      │
│     Example: HELP, STATUS, VERSION                              │
│                                                                  │
│  2. Command with Arguments:                                     │
│     COMMAND argument1 argument2                                  │
│     Example: SEARCH water purification                          │
│                                                                  │
│  3. Command with Options:                                       │
│     COMMAND|option|value                                         │
│     Example: GENERATE|guide|water                               │
│                                                                  │
│  4. Command with Variables:                                     │
│     COMMAND $variable                                            │
│     Example: SEARCH $topic                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 3: Knowledge Bank

### 3.1 Browse Knowledge

```bash
🔮 > SEARCH water
```

**Output:**
```
Found 26 guides in 'water' category:

┌──────────────────────────────────────────────────────────────┐
│ 📘 Water Procurement & Purification                         │
├──────────────────────────────────────────────────────────────┤
│ 1. boiling.md              - Boiling water for purification │
│ 2. filtration.md           - Water filtration methods       │
│ 3. chemical_treatment.md   - Chemical purification          │
│ 4. uv_treatment.md         - UV sterilization               │
│ 5. collection.md           - Water collection techniques    │
│ ...                                                          │
└──────────────────────────────────────────────────────────────┘

Use: GENERATE|guide|water|boiling to create new content
```

### 3.2 Knowledge Organization

```
knowledge/
├── water/              (26 guides - 17.3%)
│   ├── collection/
│   ├── purification/
│   └── storage/
├── fire/               (20 guides - 20.0%)
├── shelter/            (20 guides - 16.7%)
├── food/               (23 guides - 12.8%)
├── navigation/         (20 guides - 20.0%)
├── medical/            (27 guides - 18.0%)
├── tools/              (15 guides - 15.0%)
└── communication/      (15 guides - 15.0%)

Total: 166 guides across 8 categories
```

### 3.3 Generate New Content

```bash
🔮 > GENERATE|guide|water|rainwater_collection
```

**What happens:**

```
┌─────────────────────────────────────────────────────────────────┐
│                  CONTENT GENERATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Parse Command                                               │
│     [GENERATE|guide|water|rainwater_collection]                 │
│     ↓                                                            │
│  2. Check API Status                                            │
│     ✓ Gemini API available                                      │
│     ↓                                                            │
│  3. Build Enhanced Prompt                                       │
│     Topic: rainwater_collection                                 │
│     Category: water                                             │
│     Complexity: detailed                                        │
│     ↓                                                            │
│  4. Generate Content                                            │
│     → OK Assist (Gemini 2.5-flash)                             │
│     ↓                                                            │
│  5. Validate & Format                                           │
│     ✓ Markdown structure                                        │
│     ✓ Frontmatter metadata                                      │
│     ✓ Cross-references                                          │
│     ↓                                                            │
│  6. Save to Knowledge Bank                                      │
│     → knowledge/water/rainwater_collection.md                   │
│     ✓ Complete                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 4: uCODE Scripts

### 4.1 What is uCODE?

uCODE is uDOS's scripting language for automation.

**Comparison:**

```
┌─────────────────────────────────────────────────────────────────┐
│              USER COMMAND vs uCODE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User types:                                                    │
│  SEARCH water purification                                      │
│                                                                  │
│  uDOS translates to:                                            │
│  [SEARCH|water|purification]                                    │
│                                                                  │
│  Benefits of uCODE:                                             │
│  ✓ Structured and parseable                                     │
│  ✓ Supports variables: [SEARCH|$category|$topic]               │
│  ✓ Can be validated before execution                           │
│  ✓ Easy to automate and script                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Your First Script

Create `my_first_script.uscript`:

```uscript
---
title: "My First uCODE Script"
author: "Student"
description: "Learning uCODE basics"
version: "1.0.0"
---

# My First Script

## Step 1: Check system status
[STATUS]

## Step 2: Search for water guides
[SEARCH|water]

## Step 3: Generate a new guide
[GENERATE|guide|water|my_topic]

## Step 4: Report completion
[REPORT|Script complete!]
```

**Run it:**

```bash
🔮 > MISSION|run|my_first_script.uscript
```

### 4.3 Variables in uCODE

```uscript
---
title: "Variable Demo"
---

# Define variables
$category = "water"
$topic = "filtration"
$format = "detailed"

# Use variables in commands
[SEARCH|$category|$topic]
[GENERATE|guide|$category|$topic|$format]
[REPORT|Generated $topic guide in $category category]
```

### 4.4 Script Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                   .uscript FILE STRUCTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. YAML Frontmatter (optional)                                 │
│     ---                                                          │
│     title: "Script Name"                                        │
│     version: "1.0.0"                                            │
│     ---                                                          │
│                                                                  │
│  2. Markdown Sections (for organization)                        │
│     # Main Section                                              │
│     ## Subsection                                               │
│                                                                  │
│  3. Variable Definitions                                        │
│     $variable = "value"                                          │
│                                                                  │
│  4. uCODE Commands                                              │
│     [COMMAND|param1|param2]                                     │
│                                                                  │
│  5. Comments                                                    │
│     # Single line comment                                       │
│     // Also works                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 5: Extensions

### 5.1 Available Extensions

```bash
🔮 > EXTENSION|list
```

**Output:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTALLED EXTENSIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ ok-assist       - AI content generation (Gemini)            │
│  ✓ dashboard       - Web-based system dashboard                │
│  ✓ teletext        - Retro broadcast TV interface              │
│  ✓ system-desktop  - Classic Mac OS desktop environment        │
│                                                                  │
│  Available but not installed:                                   │
│  ○ typo            - Web markdown editor                        │
│  ○ micro           - Terminal text editor                       │
│  ○ monaspace       - Modern fonts                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Extension Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   EXTENSION SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────┐         │
│   │               uDOS Core                           │         │
│   │  ┌────────────────────────────────────────────┐  │         │
│   │  │  Command System   Configuration  Logger   │  │         │
│   │  └────────────────────────────────────────────┘  │         │
│   └───────────────┬──────────────────────────────────┘         │
│                   │                                             │
│                   │ Extension API                               │
│                   │                                             │
│   ┌───────────────┴────────────┬──────────────┬────────────┐   │
│   │                            │              │            │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │   │
│   │  │  OK Assist   │  │  Dashboard   │  │ Teletext │   │   │
│   │  │  (AI Gen)    │  │  (Web UI)    │  │ (Retro)  │   │   │
│   │  └──────────────┘  └──────────────┘  └──────────┘   │   │
│   │                                                       │   │
│   │  Community Extensions (via marketplace)              │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Using Extensions

**Example: Generate Multi-Format Diagram**

```bash
🔮 > GENERATE|diagram|water_filter|ascii,teletext,svg
```

**What happens:**

1. **OK Assist extension** receives the command
2. Generates diagram in 3 formats:
   - ASCII art (terminal-friendly)
   - Teletext HTML (retro web)
   - SVG (technical + organic styles)
3. Saves to `knowledge/diagrams/`
4. Returns paths to generated files

**Output files:**
```
knowledge/diagrams/
├── water_filter_ascii.txt      (1.3 KB)
├── water_filter_teletext.html  (4.2 KB)
├── water_filter_technical.svg  (2.1 KB)
└── water_filter_organic.svg    (2.3 KB)
```

---

## Practice Exercises

### Exercise 1: Basic Commands
```
Task: Get system information and search for fire guides

Commands to try:
1. STATUS
2. VERSION
3. SEARCH fire
4. HELP GENERATE
```

### Exercise 2: Content Generation
```
Task: Create a survival guide about signaling for rescue

Command:
GENERATE|guide|communication|emergency_signals
```

### Exercise 3: Write a Script
```
Task: Create a script that generates 3 water-related guides

File: water_guides.uscript
---
$topics = ["boiling", "filtration", "storage"]

[GENERATE|guide|water|boiling]
[GENERATE|guide|water|filtration]
[GENERATE|guide|water|storage]
[REPORT|Generated 3 water guides]
```

### Exercise 4: Validate Scripts
```
Task: Check your script for errors

Command:
python -m core.ucode.validator --lint water_guides.uscript
```

---

## Next Steps

### Beginner Path
```
1. ✓ Complete this tutorial
2. → Read [Command Reference](Command-Reference.md)
3. → Try [uCODE Language Guide](uCODE-Language.md)
4. → Explore [Knowledge Architecture](Knowledge-Architecture.md)
```

### Intermediate Path
```
1. ✓ Master basic commands
2. → Write complex scripts
3. → Read [API Reference](API-Reference.md)
4. → Build your first extension
```

### Advanced Path
```
1. ✓ Understand system architecture
2. → Contribute to codebase
3. → Build community extensions
4. → Help other learners
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HELP [command]          - Show help for command                │
│  STATUS                  - System health check                  │
│  VERSION                 - Version information                  │
│  CONFIG                  - Manage configuration                 │
│                                                                  │
│  SEARCH topic            - Search knowledge bank                │
│  GENERATE|guide|...      - Generate survival guide              │
│  GENERATE|diagram|...    - Generate diagram (multi-format)      │
│  REFRESH|guide|...       - Update to current standards          │
│                                                                  │
│  MISSION|run|file        - Execute .uscript file                │
│  EXTENSION|list          - List extensions                      │
│                                                                  │
│  Exit: CTRL+C or EXIT command                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Common Issues

**Problem: "Command not found"**
```
Solution: Check spelling (commands are case-insensitive)
Try: HELP to see all available commands
```

**Problem: "API key not configured"**
```
Solution: uDOS works offline! No API key needed for basic features.
For AI features: Add GEMINI_API_KEY to .env file
```

**Problem: "Script validation failed"**
```
Solution: Check script syntax
Run: python -m core.ucode.validator --lint yourscript.uscript
```

---

## Learning Resources

### Documentation
- [Command Reference](Command-Reference.md) - All commands explained
- [uCODE Language](uCODE-Language.md) - Complete scripting guide
- [API Reference](API-Reference.md) - Extension development
- [Architecture](Architecture.md) - System design

### Examples
- `memory/workflow/` - Production scripts
- `extensions/core/ok-assist/examples/` - Code examples
- `knowledge/` - Real content organization

### Community
- [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)
- [Issues](https://github.com/fredporter/uDOS/issues)
- [Wiki](https://github.com/fredporter/uDOS/wiki)

---

**Congratulations!** You've completed the Getting Started tutorial.

Ready to dive deeper? Try the [Command Reference](Command-Reference.md) next! 🔮
