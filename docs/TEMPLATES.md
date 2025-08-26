# uDOS Template Standards

```
████████╗███████╗███╗   ███╗██████╗ ██╗      █████╗ ████████╗███████╗
╚══██╔══╝██╔════╝████╗ ████║██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝
   ██║   █████╗  ██╔████╔██║██████╔╝██║     ███████║   ██║   █████╗
   ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝
   ██║   ███████╗██║ ╚═╝ ██║██║     ███████╗██║  ██║   ██║   ███████╗
   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
```

*Universal Device Operating System***Version**: 1.0.4.1
**Date**: August 25, 2025
**Type**: Template Standards
**Status**: Foundational Development

---

## Template System Overview

### 🎯 **Core Template Capabilities**
- **Basic Structure**: Standard document and data templates
- **Variable Replacement**: Simple variable substitution system
- **ASCII Art Library**: Consistent visual elements and headers
- **Role-Based Content**: Templates adapt to user role capabilities
- **File Organization**: Clean template structure and naming

---

## Template Organization

### Directory Structure

```
templates/
├── documents/          # Document templates
│   ├── command-help.md    # Command documentation
│   ├── user-guide.md      # User guide structure
│   └── log-format.md      # Logging template
├── ascii/              # ASCII art headers
│   ├── headers/           # Standard headers
│   └── symbols/           # System symbols
├── config/             # Configuration templates
│   ├── basic.json         # Basic configuration
│   └── user-data.json     # User data structure
└── system/             # System templates
    ├── status.md          # Status reporting
    └── workflow.md        # Workflow documentation
```

### Template Variables

Basic variable substitution using simple format:
- `{USER_NAME}` - Current user
- `{DATE}` - Current date
- `{ROLE}` - User role
- `{SYSTEM}` - System information
## Basic Template Types

### 1. Document Templates
Standard document structures for consistent formatting:

- **Command Documentation**: Standardized help and manual pages
- **Log Files**: Consistent logging format with timestamps
- **Configuration Files**: JSON structure with metadata headers
- **User Guides**: Help documentation with role-appropriate content

### 2. ASCII Art Templates
Visual elements for headers and branding:

```
██╗  ██╗███████╗ █████╗ ██████╗ ███████╗██████╗
██║  ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
███████║█████╗  ███████║██║  ██║█████╗  ██████╔╝
██╔══██║██╔══╝  ██╔══██║██║  ██║██╔══╝  ██╔══██╗
██║  ██║███████╗██║  ██║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
```
*Example: HEADER style ASCII art*

---

## Document Template Example

### Basic Command Documentation Template
```markdown
---
title: "{COMMAND_NAME}"
version: "1.0.4.1"
type: "command-help"
role: "{USER_ROLE}"
date: "{DATE}"
---

# {COMMAND_NAME}

## Description
{COMMAND_DESCRIPTION}

## Usage
```
{COMMAND_SYNTAX}
```

## Examples
{COMMAND_EXAMPLES}

## See Also
{RELATED_COMMANDS}
```

### Configuration Template Example
```json
{
    "metadata": {
        "name": "{CONFIG_NAME}",
        "version": "1.0.4.1",
        "type": "user-config"
    },
    "configuration": {
        "user_name": "{USER_NAME}",
        "role": "{USER_ROLE}",
        "date_created": "{DATE}"
    }
}
```
---

## ASCII Art Examples

These ASCII art examples can be used in templates:

### System Names
```
██╗  ██╗██████╗  ██████╗ ███████╗
██║  ██║██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║  ██║██║   ██║███████╗
██║  ██║██║  ██║██║   ██║╚════██║
╚██████╔╝██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
```

### Status Headers
```
███████╗████████╗ █████╗ ████████╗██╗   ██╗███████╗
██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║   ██║██╔════╝
███████╗   ██║   ███████║   ██║   ██║   ██║███████╗
╚════██║   ██║   ██╔══██║   ██║   ██║   ██║╚════██║
███████║   ██║   ██║  ██║   ██║   ╚██████╔╝███████║
╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
```

---

## Template Development Guidelines

### Naming Conventions
- Template files: `lowercase-with-hyphens.template`
- Variables: `{CAPS_WITH_UNDERSCORES}`
- ASCII headers: Keep under 8 characters when possible
- Use consistent block font style

### Best Practices
1. Keep templates simple and focused
2. Use clear variable names
3. Include example usage
4. Test with different roles
5. Follow uDOS style guidelines

---

*For comprehensive style guidelines, see `/docs/STYLE-GUIDE.md`*
*For complete command reference, see `/docs/USER-COMMAND-MANUAL.md`*
