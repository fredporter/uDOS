# uDOS Data System
Basic data management and collection for v1.0.4

## Overview
The uDOS Data System provides simple, consistent data handling across three main areas:
- **Variable System**: System and user variables with STORY collection
- **GET Forms**: Interactive data collection
- **uDATA Files**: JSON-based configuration and geographic data

## Variable System

### Core Variables
System variables follow `$VARIABLE-NAME` format:
- `$USER-ROLE` - Current user role (GHOST to WIZARD)
- `$DISPLAY-MODE` - Interface mode (CLI, DESKTOP, WEB)
- `$PROJECT-TYPE` - Project category
- `$DEVELOPER-NAME` - User name

### Commands
```
[VAR|SET*NAME*VALUE]     - Set variable value
[VAR|GET*NAME]           - Get variable value
[VAR|LIST]               - List all variables
```

### STORY Collection
Interactive data collection using narrative prompts:

```json
{
    "metadata": {
        "name": "user-setup",
        "title": "User Setup",
        "type": "story"
    },
    "variables": [
        {
            "name": "USER-ROLE",
            "type": "choice",
            "prompt": "Select your role",
            "options": ["GHOST", "DRONE", "IMP", "WIZARD"],
            "default": "GHOST"
        }
    ]
}
```

## GET Forms

### Basic Form Structure
```json
{
    "title": "Form Title",
    "description": "Purpose of form",
    "fields": [
        {
            "name": "field_name",
            "label": "🏷️ Display Label",
            "type": "TEXT|CHOICE|PASSWORD",
            "required": true,
            "help": "User guidance"
        }
    ]
}
```

### Field Types
- **TEXT**: Basic text input with validation
- **CHOICE**: Selection from predefined options
- **PASSWORD**: Secure input (noblank: false)
- **AUTO_GENERATE**: System-generated values

### Template Processing
Use `{VARIABLE}` syntax for substitution:
```markdown
# Welcome {DEVELOPER-NAME}!
Role: {USER-ROLE}
Setup: {GENERATION-TIMESTAMP}
```

## uDATA Files

### Configuration Files
Located in `/uMEMORY/system/`:
- `uDATA-config.json` - Core system settings
- `uDATA-colours.json` - Color palettes
- `uDATA-commands.json` - Command definitions

### JSON Format
Standard and minified JSON supported:
```json
{
  "system_version": "1.0.4",
  "display_mode": "CLI",
  "features": {
    "smart_terminal": true
  }
}
```

### Geographic Data
- **Coordinate System**: Latitude/longitude (WGS84)
- **TILE System**: `[A-Z]{2}[0-9]{2}` format (e.g., "AA24")
- **Timezone Codes**: 4-alpha format (USPT, EUCE, GMTU)

## File Locations

### System Data
```
uMEMORY/
├── system/               # System configuration
│   ├── uDATA-config.json
│   └── stories/          # STORY templates
└── templates/            # File templates
    ├── installation.template.md
    └── user.template.md
```

### User Data
```
sandbox/
├── user.md              # User profile
├── current-role.conf    # Role configuration
└── templates/           # User templates
```

## Core Parser

### Shell-Based Processing
Uses `/uCORE/code/variable-manager.sh` for:
- JSON parsing with `jq` (preferred) or shell fallback
- Variable validation and storage
- STORY execution
- Template processing

### Usage Examples
```bash
# Variable management
./uCORE/code/variable-manager.sh set USER-ROLE WIZARD
./uCORE/code/variable-manager.sh get DEVELOPER-NAME

# STORY execution
./uCORE/code/variable-manager.sh story user-setup

# Template generation
./uCORE/code/setup.sh
```

## Integration

### Startup Process
1. Load system variables
2. Check user configuration
3. Execute STORY if needed
4. Generate profiles from templates

### Command Integration
Variables integrate with uCORE commands:
```
[SET $USER-ROLE|WIZARD]
[GET $PROJECT-TYPE]
```

## Best Practices

### Variable Naming
- Use CAPS-DASH-NUMBER format
- Be descriptive: `PROJECT-TYPE` not `TYPE`
- Avoid abbreviations

### Form Design
- Include emoji labels for visual clarity
- Provide helpful guidance text
- Use meaningful defaults
- Keep forms simple and focused

### Data Storage
- System data in `/uMEMORY/system/`
- User data in `/sandbox/`
- Use templates for consistent file generation
- Validate JSON format

---
*uDOS v1.0.4 - Simple, lean, fast*
