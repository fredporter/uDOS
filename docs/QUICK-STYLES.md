# uDOS Quick Style Reference v1.3.3

```ascii
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Quick Style Reference - Essential Rules
    ══════════════════════════════════════════
```

**Quick Reference**: Essential coding and formatting rules for uDOS v1.3.3
**Complete Guide**: See [STYLE-GUIDE.md](STYLE-GUIDE.md) for comprehensive specifications, advanced examples, and detailed standards
**Version**: 1.3.3 | **Updated**: August 23, 2025 | **Status**: Production Ready

---

## 🚀 Essential Rules Summary

### 📝 **Code Formatting**
```bash
# Function names: lowercase with underscores
function process_user_input() {
    # Variables: lowercase with underscores
    local user_name="value"
    # Constants: UPPERCASE with underscores
    readonly MAX_RETRIES=3
}

# File extensions: always lowercase
script.sh    config.json    readme.md
```

### 🔤 **Capitalization Standards**
```markdown
# System Components: Initial caps
uDOS    uCORE    uGRID    uMAP    uDATA
uCELL   uTILE    uHEX     uWORK   uBRIEF
uDEV    uREPORT
uTASK   uMEMORY
uKNOWLEDGE

# Commands: CAPS-DASH-NUMBERS
HELP     STATUS   GRID    TEMPLATE

# Roles: Title Case (8 Standard Roles)
👻 Ghost   ⚰️ Tomb   🔐 Crypt   🤖 Drone   ⚔️ Knight   😈 Imp   🧙‍♂️ Sorcerer   🧙‍♀️ Wizard

# File types: Lowercase
.md      .json      .sh      .py     .js
```

### ⌨️ **Command Syntax**
```ucode
# uCODE shortcode default
[HELP]                    ~ System help
[MEMORY|SEARCH*term]      ~ Memory operations
[GRID|INIT*80/30]        ~ Grid initialization
[TEMPLATE|PROCESS*file.md]   ~ Template processing

# Full command mode (uSCRIPT functions)
[HELP]
[MEMORY|SEARCH*term]
[GRID|INIT*80/30]
[TEMPLATE|PROCESS*file.md]
```

### 🔧 **Variable Naming**
```bash
# Shell variables: CAPS-DASH-NUMBERS
USER-INPUT=""
SYSTEM-STATUS="active"
GRID-WIDTH=80

# Template variables: CAPS-DASH-NUMBERS
{USER-NAME}
{GRID-SIZE}
{SYSTEM-STATUS}
```

### 🔤 **uDOS Syntax Characters**
```ucode
# Variable references: Single curly brackets
{VARIABLE}
{USER-NAME}
{GRID-SIZE}

# Commands: Square brackets
[COMMAND]
[HELP]
[MEMORY|SEARCH*term]

# Functions: Angle brackets
<FUNCTION>
<INIT>
<PROCESS>

~ Operators:
|  ~ Pipe for command actions
*  ~ Asterisk for parameters
/  ~ Slash for multiple parameters

~ Comments: Both # and ~ are REM in uCODE
# This is a full line comment
[HELP]                    ~ End-of-line comment
~ uCODE avoids these characters: '"`&%$

# Character Usage in Regular Text:
~ Avoid uCODE special characters in regular operations: []{}<>~/\|
~ Example: "Press [Enter]" could confuse with system shortcode
~ Preferred: "Press ENTER to continue" (all caps, no brackets)
~ uCODE avoids these characters altogether: '"`&%$
~ Minimize quotes: "Press ENTER" → Press ENTER
```

### 🌈 **Polaroid Colors Palette (System Default)**
```css
/* Primary Colors */
--cyan:    #0094BA    /* Cyan Flash */
--cyan2:   #66C6DD    /* Cyan Tint */
--lime:    #ABBA2A    /* Lime Glow */
--lime2:   #D5E272    /* Lime Tint */
--yellow:  #F7E614    /* Yellow Burst */
--orange:  #F0793A    /* Orange Pop */
--magenta: #DE0388    /* Magenta Snap */
--mag2:    #F26BB6    /* Magenta Tint */

/* Greyscale Colors */
--white:   #FFFFFF    /* White */
--light:   #F5F5F5    /* Light Grey */
--grey2:   #D9D9D9    /* Grey Light */
--grey:    #B3B3B3    /* Grey Mid */
--grey3:   #8C8C8C    /* Grey Strong */
--grey4:   #595959    /* Grey Dark */
--dark:    #262626    /* Dark Grey */
--black:   #000000    /* Black */
```

**Usage**: Default uDOS v1.3.3 system interface palette with authentic retro aesthetics
**All 8 Palettes**: See [STYLE-GUIDE.md](STYLE-GUIDE.md) for complete collection including Retro Unicorn, Nostalgia, Tropical Sunrise, Pastel Power, Arcade Pastels, Forest Sprite, and Solar Punk

### 📂 **Naming Conventions**
```bash
# Scripts: lowercase with hyphens
user-auth.sh
grid-manager.sh
template-engine.sh

# Configuration files: lowercase with extensions
config.json
settings.yaml
template.md

# Documentation: UPPERCASE for main docs
README.md
STYLE-GUIDE.md
USER-GUIDE.md

# Regular docs: lowercase with hyphens
quick-start.md
api-reference.md
troubleshooting.md
```

---

## 🎨 Common Patterns

### ✅ **Correct Examples**
```bash
# Function definition
function initialize_grid() {
    local width=$1
    local height=$2
    echo "Grid: ${width}/${height}"
}

# Variable assignment
readonly SYSTEM-NAME="uDOS"
local USER-ROLE="sorcerer"

# uDOS syntax examples
{USER-NAME} referenced in template
[GRID|INIT*80/30] command with asterisk and slash operators
<PROCESS> function in angle brackets
```

### ❌ **Incorrect Examples**
```bash
# Wrong function naming
function InitializeGrid() {        # Should be: initialize_grid
function initialize-grid() {       # Should be: initialize_grid

# Wrong variable naming
local UserRole="sorcerer"          # Should be: USER-ROLE
readonly max_retries=3             # Should be: MAX-RETRIES

# Wrong syntax usage
"USER_NAME"                        # Should be: {USER-NAME}
'[COMMAND]'                        # Should be: [COMMAND]
`function`                         # Should be: <FUNCTION>
# comment                          ~ Should be: # comment or ~ comment
```

---

## 📋 Quick Reference Tables

### **uDOS Syntax**
| Element | Format | Example |
|---------|--------|---------|
| Variables | `{CAPS-DASH}` | `{USER-NAME}` |
| Commands | `[COMMAND\|ACTION*param]` | `[GRID\|INIT*80/30]` |
| Functions | `<FUNCTION>` | `<PROCESS>` |
| Comments | `#` or `~` | `# full line` `~ end line` |

### **File Extensions**
| Type | Extension | Example |
|------|-----------|---------|
| Scripts | `.sh` | `user-auth.sh` |
| Configuration | `.json` | `config.json` |
| Documentation | `.md` | `README.md` |

---

## 🔗 Complete Documentation

For detailed specifications including:
- **uHEX Filename Convention v7.0**: File naming with metadata encoding
- **uDATA Format**: JSON processing and minification standards
- **8-Role System**: Complete hierarchy and access controls
- **BBC Mode 7 Design**: Authentic teletext graphics standards
- **8 Color Palettes**: Complete collection with 128 total colors
- **Template System**: Variable syntax and processing rules
- **uCORE Integration**: System commands and automation

**➡️ See the complete [STYLE-GUIDE.md](STYLE-GUIDE.md)**

---

## 🚀 Getting Started Checklist

### **For Developers**
- [ ] Use `lowercase_with_underscores` for functions and variables
- [ ] Use `CAPS-DASH-NUMBERS` for shell and template variables
- [ ] Use `{VARIABLE}` single brackets for variable references
- [ ] Use `[COMMAND|ACTION*param/param2]` format with pipe, asterisk, and slash operators
- [ ] Use `<FUNCTION>` angle brackets for function references
- [ ] Use `~` for end-of-line comments, `#` for full-line comments in uCODE
- [ ] Avoid `'"`&%$` characters in native uCODE syntax
- [ ] Always specify language in code blocks for proper highlighting
- [ ] Use descriptive file names with appropriate extensions
- [ ] Reference [STYLE-GUIDE.md](STYLE-GUIDE.md) for comprehensive JSON, documentation, and advanced syntax standards

### **For Content Creators**
- [ ] Use emoji prefixes for documentation headers (🚀 📚 ⚙️)
- [ ] Use **Bold** for UI elements, `code` for commands and variables
- [ ] Title case for section headers with consistent formatting
- [ ] Link to detailed guides when appropriate for complex topics
- [ ] Include code examples with proper syntax highlighting
- [ ] Avoid uCODE special characters in regular text: `[]{}<>~/\|`
- [ ] Use CAPS for key names instead of quotes: Press ENTER not "Enter"
- [ ] Reference [STYLE-GUIDE.md](STYLE-GUIDE.md) for comprehensive markdown and documentation standards

### **For System Integration**
- [ ] Follow uCORE component naming conventions (uGRID, uMAP, uDATA)
- [ ] Use template variables in CAPS-DASH-NUMBERS format: `{USER-NAME}`
- [ ] Maintain role-based formatting consistency across 8 standard roles
- [ ] Use Polaroid Colors palette as system default, reference complete collection in STYLE-GUIDE
- [ ] Implement uHEX v7.0 filename convention for all generated files
- [ ] Reference complete style guide for complex specifications and edge cases

---

*Quick Style Reference v1.3.3 - Essential rules for consistent uDOS development and content creation*
*Production Ready | For complete specifications and advanced examples: [STYLE-GUIDE.md](STYLE-GUIDE.md)*
