# uDOS Style Guide & Language Policy

**Version**: 1.2  
**Date**: August 16, 2025  
**Scope**: uDOS Universal Data Operating System

---

## Overview

This guide defines the official formatting, typography, and language standards for the uDOS ecosystem. Consistency across all documentation, interfaces, and code ensures a professional, accessible user experience.

---

## Typography Standards

### 1. Capitalization Rules

#### ALL CAPS Usage (Technical Elements)
- **Commands**: `STATUS`, `MEMORY`, `PACKAGE`, `RESTART`
- **Variables**: `$USERNAME`, `$CURRENT_MODE`, `$UDOS_VERSION`
- **Shortcodes**: `[MEM|LIST]`, `[PACK|INSTALL]`, `[DASH|LIVE]`
- **Section Headers**: `## CORE COMMANDS` (only for major sections)
- **File Extensions**: `.MD`, `.US`, `.SH`

#### Sentence Case Usage (Human Elements)
- **Headings**: "## Memory commands (alias MEM)"
- **Descriptions**: "Your memory stores all data in markdown files"
- **UI Labels**: "Current status:", "Available layouts:"
- **Messages**: "Welcome to the Universal Data Operating System"
- **Tutorial Text**: "You stand in a dimly lit stone chamber"

#### Proper Case Usage (Names & Titles)
- **System Name**: "uDOS", "Universal Data Operating System"
- **Component Names**: "Memory Vaults", "Shortcode Sanctum"
- **File Types**: "Markdown", "Visual Basic"
- **Technology Names**: "NetHack", "ASCII"

### 2. Color Coding Standards

#### Command Elements
```bash
# Commands (YELLOW)
STATUS, HELP, MEMORY, PACKAGE

# Shortcodes (CYAN brackets, YELLOW content)
[MEM|LIST], [PACK|INSTALL], [DASH|LIVE]

# Variables (GREEN)
$USERNAME, $CURRENT_MODE, $UDOS_VERSION

# File paths (BLUE)
/Users/username/uDOS/uMemory/
```

#### Interface Elements
```bash
# Headers (BOLD + color)
log_header "System Status"

# Success (GREEN)
✅ Operation completed successfully

# Warning (YELLOW)
⚠️ This action requires confirmation

# Error (RED)
❌ Command not found

# Info (CYAN)
ℹ️ Helpful information
```

---

## Markdown Language Standards

### 1. Heading Structure
```markdown
# Document Title (Title Case)
## Major sections (Sentence case)
### Subsections (Sentence case)
#### Details (Sentence case)
```

### 2. Command Documentation Format
```markdown
## Core commands

- **STATUS** - Show system overview
- **HELP** - Display documentation
- **[MEM|LIST]** - List memory files
- **$USERNAME** - Current user variable
```

### 3. Code Block Standards
```markdown
# Bash commands
```bash
./uCode/ucode.sh
```

# uCode examples
```ucode
IF status = "ready" THEN
    PRINT "System operational"
END IF
```

# Configuration files
```ini
UDOS_USER="wizard"
UDOS_ROLE="sorcerer"
```
```

---

## Interface Design Principles

### 1. Visual Hierarchy
1. **Commands** - Bright yellow, immediate recognition
2. **Shortcodes** - Cyan brackets, structured format
3. **Variables** - Green, environment context
4. **Text** - White/default, readable content
5. **Accents** - Blue for paths, purple for special

### 2. Accessibility Guidelines
- **Color blindness**: Never rely on color alone
- **Text symbols**: Use emoji + text labels
- **Contrast**: Ensure readability on dark terminals
- **Consistency**: Same elements always same color

### 3. Adventure Theme Integration
- **Fantasy terminology**: "spells", "chambers", "artifacts"
- **Character classes**: wizard, sorcerer, ghost, trickster, scholar
- **Game mechanics**: XP, levels, achievements
- **Narrative elements**: story-driven tutorials

---

## Code Implementation

### 1. Color Variable Definitions
```bash
# Core colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'  # No Color

# Semantic colors
COMMAND_COLOR="$YELLOW"
SHORTCODE_COLOR="$CYAN"
VARIABLE_COLOR="$GREEN"
PATH_COLOR="$BLUE"
```

### 2. Display Functions
```bash
# Command display
show_command() {
    echo -e "${COMMAND_COLOR}$1${NC}"
}

# Shortcode display
show_shortcode() {
    echo -e "${SHORTCODE_COLOR}[$1${NC}${SHORTCODE_COLOR}]${NC}"
}

# Variable display
show_variable() {
    echo -e "${VARIABLE_COLOR}\$$1${NC}"
}
```

---

## Documentation Standards

### 1. File Naming Convention
- **Style guides**: `uDOS-Style-Guide.md`
- **User manuals**: `User-Manual.md`
- **Technical docs**: `API-Reference.md`
- **Templates**: `template-name.md`

### 2. Content Structure
```markdown
# Title
**Metadata block**

## Overview
Brief description

## Main Content
Detailed information

## Examples
Code samples and usage

## Reference
Quick lookup information
```

### 3. Cross-References
- **Commands**: Link to `## Core commands` section
- **Shortcodes**: Reference `## Shortcode format`
- **Variables**: Point to environment documentation
- **Files**: Include full paths with proper coloring

---

## Quality Assurance

### 1. Review Checklist
- [ ] Commands in ALL CAPS and yellow
- [ ] Shortcodes in [BRACKET|FORMAT] with cyan
- [ ] Variables with $ prefix in green
- [ ] Headings in sentence case
- [ ] Descriptions in sentence case
- [ ] Proper emoji usage
- [ ] Consistent terminology

### 2. Testing Requirements
- Test on multiple terminal types
- Verify color rendering
- Check accessibility compliance
- Validate cross-references
- Ensure narrative consistency

---

## Enforcement

### 1. Automated Checks
```bash
# Check for capitalization consistency
grep -n "## [A-Z][A-Z]" *.md

# Verify color coding implementation
grep -n "echo.*COMMAND" *.sh
```

### 2. Manual Review Points
- New documentation must follow style guide
- Code changes affecting display require review
- User-facing text must use proper case
- Adventure narrative must maintain tone

---

## Updates & Maintenance

This style guide is a living document. Updates should:

1. Maintain backward compatibility
2. Include migration instructions
3. Update all affected documentation
4. Test across all components
5. Communicate changes to users

**Last updated**: August 16, 2025  
**Next review**: September 2025
