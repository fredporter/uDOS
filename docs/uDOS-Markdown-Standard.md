# uDOS Markdown Documentation Standard

```
    ██████╗  ██████╗  ██████╗███████╗    ███████╗████████╗ █████╗ ███╗   ██╗██████╗  █████╗ ██████╗ ██████╗ 
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝    ██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗
    ██║  ██║██║   ██║██║     ███████╗    ███████╗   ██║   ███████║██╔██╗ ██║██║  ██║███████║██████╔╝██║  ██║
    ██║  ██║██║   ██║██║     ╚════██║    ╚════██║   ██║   ██╔══██║██║╚██╗██║██║  ██║██╔══██║██╔══██╗██║  ██║
    ██████╔╝╚██████╔╝╚██████╗███████║    ███████║   ██║   ██║  ██║██║ ╚████║██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═════╝  ╚═════╝  ╚═════╝╚══════╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 

    Universal Data Operating System - Documentation Standard v1.0
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
```

**Version**: 1.0  
**Date**: August 16, 2025  
**Part Number**: uDOS-MD-STD-001  
**Issue**: 1

---

## Document Format Specification

### Header Template

```markdown
# [Document Title]

**Version**: [x.x]  
**Date**: [Month DD, YYYY]  
**Part Number**: [uDOS-XXX-000]  
**Issue**: [Number]  
**Status**: [Draft|Review|Current|Archived]

---
```

### Warning/Important Notices

```markdown
> **⚠️ WARNING**: [Critical safety or system information]

> **📋 IMPORTANT**: [Essential operational information]

> **💡 NOTE**: [Helpful clarification or tip]
```

### Table of Contents Format

```markdown
## Contents

1. [About this Guide](#about-this-guide)
2. [Getting Started](#getting-started)
   2.1 [Setup Requirements](#setup-requirements)
   2.2 [Installation](#installation)
3. [System Overview](#system-overview)
   3.1 [Architecture](#architecture)
   3.2 [Components](#components)
4. [Using the System](#using-the-system)
   4.1 [Basic Operations](#basic-operations)
   4.2 [Advanced Features](#advanced-features)
5. [Reference](#reference)
   5.1 [Command Reference](#command-reference)
   5.2 [Error Codes](#error-codes)
6. [Technical Information](#technical-information)
7. [Appendices](#appendices)

---
```

### ASCII Art Standards

#### System Logos
```ascii
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
```

#### Box Frames (Standard)
```ascii
┌─────────────────────────────────────────────────┐
│                 Content Here                    │
└─────────────────────────────────────────────────┘
```

#### Box Frames (Double Line)
```ascii
╔═════════════════════════════════════════════════╗
║                 Content Here                    ║
╚═════════════════════════════════════════════════╝
```

#### Section Dividers
```ascii
    ═══════════════════════════════════════════════════════════════
```

### Command Reference Format

```markdown
### COMMAND_NAME

**Description**  
Brief description of what the command does.

**Syntax**  
```
COMMAND_NAME [required_parameter] [optional_parameter]
```

**Parameters**
- `required_parameter` - Description of required parameter
- `optional_parameter` - Description of optional parameter (default: value)

**Examples**
```bash
# Basic usage
COMMAND_NAME value1

# Advanced usage
COMMAND_NAME value1 value2
```

**Notes**
- Important implementation details
- Known limitations
- Cross-references to related commands

**See Also**: [Related Command](#related-command)

---
```

### Code Block Standards

#### Terminal Commands
```bash
# Comment explaining the command
ucode COMMAND parameter
```

#### Configuration Files
```json
{
  "setting": "value",
  "description": "Configuration example"
}
```

#### Script Examples
```shell
#!/bin/bash
# uDOS Script Example
echo "Starting uDOS operation..."
./ucode.sh operation
```

### Table Formats

#### Command Reference Table
| Command | Purpose | Syntax | Notes |
|---------|---------|--------|-------|
| `STATUS` | System status | `STATUS [detail]` | Shows current state |
| `HELP` | Command help | `HELP [command]` | Context-sensitive |

#### Configuration Table
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `log_level` | string | "INFO" | Logging verbosity |
| `max_memory` | integer | 1024 | Memory limit (MB) |

### Error/Status Messages

```markdown
#### Error Codes

| Code | Message | Description | Resolution |
|------|---------|-------------|------------|
| E001 | System not initialized | uDOS core not started | Run `ucode START` |
| W001 | Low memory warning | Available memory < 10% | Clear temp files |
| I001 | Operation completed | Command executed successfully | Continue |
```

### Figures and Diagrams

```markdown
#### Figure 1.1: System Architecture

```ascii
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   uMemory   │◄──►│    uCode    │◄──►│ uTemplate   │
│  (Storage)  │    │   (Core)    │    │ (Rendering) │
└─────────────┘    └─────────────┘    └─────────────┘
        ▲                  ▲                  ▲
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  uScript    │    │ uCompanion  │    │  uMapping   │
│ (Automation)│    │    (AI)     │    │ (Navigation)│
└─────────────┘    └─────────────┘    └─────────────┘
```

*Figure 1.1 shows the core uDOS architecture with bidirectional data flow.*
```

### File Structure Documentation

```markdown
#### Directory Structure

```
uDOS/
├── uCode/          # Core system scripts
│   ├── ucode.sh    # Main system interface
│   └── dash.sh     # Dashboard system
├── uMemory/        # User data storage
│   ├── missions/   # Mission files
│   └── config/     # Configuration
├── uTemplate/      # Template engine
│   ├── formats/    # Output formats
│   └── library/    # Template library
└── docs/           # Documentation
    ├── user/       # User guides
    └── technical/  # Technical docs
```
```

### Installation Instructions Format

```markdown
## Installation

### Prerequisites

> **📋 IMPORTANT**: Ensure you have the following before proceeding:

- macOS 10.15 or later
- Terminal access
- 100MB free disk space
- Internet connection (for packages)

### Step 1: Download uDOS

```bash
# Clone the repository
git clone https://github.com/user/uDOS.git
cd uDOS
```

### Step 2: Run Installation

```bash
# Make installer executable
chmod +x install-udos.sh

# Run installation
./install-udos.sh
```

### Step 3: Verify Installation

```bash
# Start uDOS
./uCode/ucode.sh

# Check system status
STATUS
```

Expected output:
```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ╚██████╔╝██████╔╝╚██████╔╝███████║

    uDOS v1.2 - System Ready
    ═══════════════════════════════

    Status: OPERATIONAL
    Memory: 847MB available
    Modules: 6 loaded
```
```

### Footer Template

```markdown
---

## Copyright and Licensing

© 2025 uDOS Project. All rights reserved.

This document is part of the uDOS Universal Data Operating System project. 
Distribution and modification are permitted under the terms of the project license.

**Technical Support**: Contact via GitHub issues  
**Documentation Updates**: Submit pull requests  
**Version History**: See CHANGELOG.md

---

*uDOS Documentation Standard v1.0*  
*Universal Data Operating System Project*  
*August 2025*
```

### Style Guidelines

#### Typography
- **Headings**: Use sentence case with proper nouns capitalized
- **Commands**: Always use `backticks` for inline code
- **File paths**: Use `backticks` for file references
- **Emphasis**: Use **bold** for important terms, *italic* for variables

#### Spacing
- Single blank line between paragraphs
- Double blank line before major sections
- Triple dash (`---`) for section breaks

#### Cross-References
```markdown
See [Section 4.2](#advanced-features) for detailed configuration.
Refer to the [User Manual](User-Manual.md#getting-started) for basics.
```

#### External Links
```markdown
Visit the [uDOS GitHub Repository](https://github.com/user/uDOS) for source code.
```

### Template Usage

1. Copy the appropriate template section
2. Replace placeholder text in `[brackets]`
3. Add ASCII art using standard formats
4. Include proper cross-references
5. Test all code examples
6. Validate formatting with `glow`

---

This standard ensures consistency across all uDOS documentation while maintaining the retro computing aesthetic that makes uDOS unique.
