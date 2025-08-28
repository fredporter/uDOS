# uDOS Style Guide

```
███████ ████████ ██   ██ ██     ███████
██         ██     ██ ██  ██     ██
███████    ██      ███   ██     █████
     ██    ██      ██    ██     ██
███████    ██      ██    ██████ ███████
```

*Universal Device Operating System v1.0.4.1*

**Quick Reference**: [QUICK-STYLES.md](QUICK-STYLES.md) | **Complete Reference**: [USER-CODE-MANUAL.md](USER-CODE-MANUAL.md)

---

## 🎯 Core Principles

### uCODE Language Standards
```ucode
[COMMAND|OPTION*PARAMETER]     ~ Universal shortcode syntax
{VARIABLE-NAME}                ~ Variables: CAPS-DASH-NUMBERS
<FUNCTION>                     ~ Functions: angle brackets
DEF {VAR} = {VALUE}           ~ Variable definitions
```

### 8-Role System
```
👻 GHOST (10)    ⚰️ TOMB (20)     🔐 CRYPT (30)    🤖 DRONE (40)
⚔️ KNIGHT (50)   😈 IMP (60)      🧙‍♂️ SORCERER (80) 🧙‍♀️ WIZARD (100)
```

---

## 📁 File Naming Standards

### uHEX Convention (Core Files)
```
uTYPE-uHEXCODE-Description.md
uLOG-A1B2C3D4-System-Status.md
uDOC-5E6F7G8H-User-Manual.md
```

### System Files
```bash
# Scripts: kebab-case
cleanup-system.sh
start-server.sh

# Config: kebab-case
system-config.json
user-settings.conf

# Data: camelCase
locationMap.json
userPreferences.json
```

---

## 🎨 Code Formatting

### Bash Scripts
```bash
#!/bin/bash
# Script description

function process_data() {
    local input_file="$1"
    readonly MAX_RETRIES=3

    # Use descriptive names
    log_info "Processing: $input_file"
}
```

### uCODE Scripts
```ucode
<FUNCTION> {PROCESS-USER-DATA} {INPUT-FILE}
    DEF {MAX-RETRIES} = 3
    DEF {RESULT} = [FILE] <READ> {INPUT-FILE}

    IF {RESULT} = SUCCESS THEN
        [LOG] <INFO> {Processing complete}
    END IF
<END-FUNCTION>
```

### JSON Configuration
```json
{
    "metadata": {
        "name": "component-name",
        "version": "1.0.4.1",
        "type": "user|system|core"
    },
    "configuration": {
        "setting": "value"
    }
}
```

---

## 🎨 Visual Standards

### Terminal Colors (8 Palettes)
**Default: Polaroid** (High-contrast)
```css
--red: #FF1744     --green: #00E676    --yellow: #FFEB3B
--blue: #2196F3    --purple: #E91E63   --cyan: #00E5FF
```

**Available Palettes**: Polaroid, Retro Unicorn, Nostalgia, Tropical Sunrise, Pastel Power, Arcade Pastels, Grayscale, Solar Punk

### ASCII Art Standards
```
██████╗  █████╗ ████████╗ █████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
██║  ██║███████║   ██║   ███████║
██║  ██║██╔══██║   ██║   ██╔══██║
██████╔╝██║  ██║   ██║   ██║  ██║
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
```

**Rules**: Keep under 8 characters, use standard block characters, include system branding

---

## 📋 Documentation Standards

### Markdown Structure
```markdown
# Title (H1 - one per document)
## Section (H2 - main sections)
### Subsection (H3 - details)

**Bold**: Important terms
*Italic*: Emphasis
`code`: Inline code
```

### Code Blocks
````markdown
```ucode
[COMMAND] <ACTION> {PARAMETER}
```

```bash
#!/bin/bash
function example() {
    echo "Standard formatting"
}
```
````

### Lists and Tables
```markdown
- **Item**: Description
- **Item**: Description

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |
```

---

## 🗂️ Directory Structure

### Core System
```
uCORE/          ~ System code and launchers
uMEMORY/        ~ Permanent storage and templates
uNETWORK/       ~ Server and display systems
uSCRIPT/        ~ Script execution and automation
```

### User Workspace
```
sandbox/        ~ Active work and experimentation
├── logs/       ~ All system logging
├── data/       ~ Working data files
├── scripts/    ~ User scripts and containers
├── backup/     ~ Session backups
└── trash/      ~ Temporary file storage
```

### Development (Wizard + DEV mode only)
```
dev/            ~ Core development environment
├── active/     ~ Current development work
├── templates/  ~ Development templates
├── docs/       ~ Architecture documentation
└── scripts/    ~ Development automation
```

---

## 🔧 Best Practices

### Variable Naming
```ucode
{USER-NAME}        ~ Descriptive and clear
{SYSTEM-STATUS}    ~ Use CAPS-DASH format
{API-ENDPOINT-URL} ~ Compound names allowed
{MAX-RETRIES-3}    ~ Include numbers when helpful
```

### Function Design
```ucode
<FUNCTION> {PROCESS-USER-INPUT} {INPUT-DATA}
    ~ Single responsibility
    ~ Clear parameter names
    ~ Comprehensive error handling
    ~ Role-appropriate functionality
<END-FUNCTION>
```

### Error Handling
```ucode
[TRY]
    [OPERATION] <EXECUTE>
[CATCH] {ERROR}
    [LOG] <ERROR> {Operation failed: } + {ERROR}
    [ROLE] <ACTIVATE> {GHOST}  ~ Safe fallback
[END]
```

### Comments
```bash
# Full line comments use hash
function process_data() {
    local file="$1"    # End-of-line explanation
    # Avoid excessive commenting
}
```

```ucode
# Full line comments in uCODE
[COMMAND] <ACTION> {PARAM}     ~ End-of-line comment
~ Alternative comment style
```

---

## 🎯 uDOS Naming Rules

### System Components
```
uCORE  uGRID  uMAP   uDATA  uCELL  uTILE  uHEX  uLOG
uDOC   uTASK  uWORK  uBRIEF uREPORT uDEV  uKNOWLEDGE
```

### Commands
```
STATUS  HELP   GRID   TEMPLATE  BACKUP  TRASH  ROLE
```

### File Extensions
```
.md     .json   .sh    .py      .js     .conf
```

---

## 🔄 Integration Standards

### uCORE Commands
```ucode
[uCORE] <COMMAND> {OPERATION}      ~ System operations
[uCORE] <SESSION> {SAVE}           ~ Session management
[uCORE] <FILENAME> {GENERATE}      ~ File operations
```

### Template Processing
```ucode
[TEMPLATE] <PROCESS> {INPUT} {OUTPUT} {VARIABLES}
{SYSTEM:TIMESTAMP}     ~ System variables
{USER:NAME}            ~ User variables
{CONTAINER:TYPE}       ~ Container variables
```

### Role Integration
```ucode
[ROLE] <CURRENT>                   ~ Get current role
[ROLE] <ACTIVATE> {WIZARD}         ~ Switch roles
[ROLE] <PERMISSIONS> {OPERATION}   ~ Check permissions
```

---

*uDOS Style Guide v1.0.4.1 - Foundational standards for clean, consistent development*

**Complete Specifications**: Original detailed guide moved to `/dev/docs/style-complete.md`
**Quick Reference**: [QUICK-STYLES.md](QUICK-STYLES.md) for essential rules
**Technical Manual**: [USER-CODE-MANUAL.md](USER-CODE-MANUAL.md) for implementation
