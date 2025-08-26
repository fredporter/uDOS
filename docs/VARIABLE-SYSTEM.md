# uDOS Variable System Documentation

## Overview

The uDOS Variable System provides a centralized, lean architecture for managing both system and user-defined variables with STORY-based input collection. It integrates seamlessly with uCORE and uSCRIPT for consistent variable handling across the entire platform.

## Components

### 1. Variable Manager (`uCORE/core/variable-manager.sh`)
Central system for variable definition, storage, and retrieval.

### 2. uSCRIPT Integration (`uSCRIPT/integration/uscript-variables.sh`)
Provides variable support within uSCRIPT container environment.

### 3. Command Router Integration
Added VAR and STORY commands to the core command routing system.

## Variable Types

### System Variables
Predefined variables managed by uDOS core:
- `$USER-ROLE` - Current user role (GHOST to WIZARD)
- `$DISPLAY-MODE` - Interface mode (CLI, DESKTOP, WEB)
- `$MAX-RESOLUTION` - Display resolution
- `$GRID-SIZE` - Grid dimensions
- `$DETAIL-LEVEL` - Information verbosity
- `$TILE-CODE` - Geographic location code
- `$PROJECT-NAME` - Current project identifier
- `$SESSION-ID` - Session identifier

### User Variables
Custom variables defined by users or applications with validation rules.

## Command Syntax

### Variable Management
```
[VAR|DEFINE*NAME*TYPE*DEFAULT*SCOPE*DESCRIPTION*VALUES*PATTERN]
[VAR|SET*NAME*VALUE*SESSION]
[VAR|GET*NAME*SESSION]
[VAR|LIST*SCOPE]
[VAR|VALIDATE*NAME*VALUE]
```

### STORY System
```
[STORY|CREATE*NAME*TITLE*VARIABLES]
[STORY|EXECUTE*STORY-FILE*SESSION]
```

### uSCRIPT Integration
```
[USCRIPT|VAR|LOAD*SESSION]
[USCRIPT|VAR|SAVE*SESSION]
[USCRIPT|VAR|EXEC*SCRIPT*SESSION]
[USCRIPT|VAR|TEMPLATE*NAME*TYPE*VARIABLES]
```

## Usage Examples

### 1. Define a User Variable
```bash
[VAR|DEFINE*API-KEY*string**user*API authentication key]
```

### 2. Set Variable Value
```bash
[VAR|SET*API-KEY*sk-abc123*my-session]
```

### 3. Create a STORY for Input Collection
```bash
[STORY|CREATE*api-setup*API Configuration*API-KEY,API-URL,TIMEOUT]
```

### 4. Execute STORY to Collect Variables
```bash
[STORY|EXECUTE*api-setup.json*my-session]
```

### 5. Create Variable-Aware Script
```bash
[USCRIPT|VAR|TEMPLATE*api-client*python*API-KEY,API-URL]
```

## STORY System

STORY templates replace traditional forms/tutorials for variable collection. They provide:

- **Narrative Context**: Introduction and purpose explanation
- **Sequential Flow**: Guided variable collection process
- **Smart Validation**: Type and pattern checking
- **User-Friendly Prompts**: Clear questions with help text
- **Session Integration**: Values stored per session

### STORY Structure
```json
{
    "metadata": {
        "name": "story-name",
        "title": "Human-readable title",
        "type": "story"
    },
    "story": {
        "introduction": "Welcome message",
        "context": "Explanation of purpose",
        "purpose": "What this accomplishes"
    },
    "variables": [
        {
            "name": "VARIABLE-NAME",
            "type": "string|number|email|url",
            "description": "Variable purpose",
            "required": true|false,
            "values": ["option1", "option2"],
            "pattern": "regex-pattern",
            "prompt": "User question",
            "help": "Additional guidance"
        }
    ],
    "flow": {
        "sequential": true,
        "allow_skip": false,
        "validate_each": true
    }
}
```

## File Structure

```
uMEMORY/
├── system/
│   ├── variables/
│   │   └── system-variables.json     # Core system variables
│   └── stories/
│       ├── user-onboarding.json      # Example STORY
│       └── project-setup.json        # Project creation STORY
└── user/
    ├── variables/
    │   ├── user-variables.json        # User-defined variables
    │   └── values-{session}.json      # Session-specific values
    └── missions/
        └── uTASK-{hex}-{name}.md      # Generated missions
```

## Integration Points

### 1. Command Router
- VAR commands route to variable manager
- STORY commands handle input collection
- Session-aware variable storage

### 2. uSCRIPT
- Variable loading in script headers
- Environment variable export
- Template generation with variable support
- Substitution during execution

### 3. Smart Input System
- Enhanced prompts with validation
- Context-aware suggestions
- Multi-step wizards
- Form generation capabilities

## Session Management

Variables are stored per-session to support:
- Multiple concurrent users
- Isolated variable spaces
- Session-specific overrides
- Development/production separation

## Validation System

Built-in validation for:
- **Types**: string, number, email, url, date, time, phone
- **Patterns**: Regex validation for custom formats
- **Values**: Enumerated options for selection
- **Requirements**: Required vs optional fields

## Future Expansion

The system is designed for easy extension:
- New variable types can be added
- Custom validation functions
- Integration with external systems
- Role-based variable access
- Variable inheritance and scoping

## Best Practices

1. **Use System Variables** for core uDOS functionality
2. **Define User Variables** for application-specific needs
3. **Create STORYs** instead of complex forms
4. **Validate Early** using the built-in validation
5. **Session Isolation** for different contexts
6. **Clear Naming** with descriptive variable names
7. **Documentation** in variable descriptions
