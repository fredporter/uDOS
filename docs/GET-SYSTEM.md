# uDOS GET System Documentation

**Version**: v1.0.4.1
**Purpose**: Complete guide for creating interactive data collection forms
**Integration**: uMEMORY, uCORE, uDATA systems

> **Category**: System Documentation
> **Target**: Form builders and system integrators
> **Standards**: uDOS v1.0.4.1 compatibility

---

## 🎯 GET System Overview

A **GET** is an interactive data collection form that gathers information from users through validated input fields. The GET system integrates with uDATA for intelligent lookups, templates for processing, and the role-based permission system.

### Architecture Integration

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                        GET SYSTEM ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  GET FORM   │◄──►│  VALIDATION │◄──►│   uDATA     │             │
│  │ DEFINITION  │    │   ENGINE    │    │ INTEGRATION │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│         │                   │                   │                  │
│         ▼                   ▼                   ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  TEMPLATE   │    │  ROLE-BASED │    │  OUTPUT     │             │
│  │ PROCESSING  │    │ PERMISSIONS │    │ GENERATION  │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📋 GET Form Structure

### Basic JSON Configuration
```json
{
    "title": "Form Title",
    "description": "Clear description of form purpose",
    "category": "SETUP|CONFIG|DATA-ENTRY|SURVEY|MISSION",
    "version": "1.0.4.1",
    "fields": [
        // Field definitions
    ],
    "actions": {
        // Processing configuration
    },
    "output_files": [
        // Output specifications
    ],
    "post_actions": [
        // Post-processing tasks
    ]
}
```

### Markdown Field Format
```markdown
## 🏷️ Display Label
DATA: field_name
ASK: Question to display to user
DEFAULT: default_value
TYPE: TEXT|PASSWORD|CHOICE|DATE|NUMBER|LOCATION_LOOKUP|TIMEZONE_LOOKUP|AUTO_GENERATE
uDATA: dataset_name
OPTIONS: [OPTION1, OPTION2, ...]
REQUIRED: TRUE|FALSE
VALIDATION: regex_pattern
HELP: Additional context or guidance
```

## 🔧 Field Types and Validation

### Core Field Types

#### Text Input
```json
{
    "name": "field_name",
    "label": "🏷️ Display Label",
    "type": "TEXT",
    "required": true,
    "noblank": true,
    "validation": "^[a-zA-Z0-9_]{3,20}$",
    "help": "Clear instructions for the user",
    "default": "meaningful_default_value"
}
```

#### Choice Selection
```json
{
    "name": "choice_field",
    "label": "📋 Select Option",
    "type": "CHOICE",
    "options": ["OPTION1", "OPTION2", "OPTION3"],
    "required": true,
    "noblank": true,
    "help": "Choose from available options",
    "default": "OPTION1"
}
```

#### Password Field
```json
{
    "name": "password_field",
    "label": "🔑 Password",
    "type": "PASSWORD",
    "required": false,
    "noblank": false,
    "help": "Leave blank for no password protection",
    "default": ""
}
```

### uDATA Integration Fields

#### Location Lookup
```markdown
## 📍 Location
DATA: location
ASK: Select your location
DEFAULT: LONDON
TYPE: LOCATION_LOOKUP
uDATA: locationMap
HELP: Search from 52 global cities with coordinates
```

#### Timezone Selection
```markdown
## 🕒 Timezone
DATA: timezone
ASK: Select your timezone
DEFAULT: UTC
TYPE: TIMEZONE_LOOKUP
uDATA: timezoneMap
HELP: Choose from 38 global timezones
```

#### Auto-Generated Fields
```markdown
## ⏱️ UTC Offset
DATA: utc_offset
ASK: (auto-detected from timezone)
DEFAULT: +00:00
TYPE: AUTO_GENERATE
uDATA: timezoneMap
```

## 🎨 Validation Rules

### uDATA Validation Standards
1. **Cannot Be Blank**: All fields default to `noblank: true`
2. **Password Exception**: Password fields default to `noblank: false`
3. **Meaningful Defaults**: Required for all `noblank=true` fields
4. **Validation Patterns**: Include regex validation for TEXT inputs
5. **Help Text**: Always provide clear, actionable guidance

### Field Naming Conventions
- Use lowercase with underscores: `field_name`
- Be descriptive: `preferred_companion` not `companion`
- Avoid abbreviations unless industry standard

### Label Guidelines
- Include relevant emoji for visual identification
- Keep labels concise but descriptive
- Use consistent terminology across forms

## 💾 Output Configuration

### Output Files
```json
"output_files": [
    {
        "path": "uMEMORY/collected/{{field_name}}.json",
        "format": "JSON",
        "template": "optional_template_name"
    },
    {
        "path": "uMEMORY/config/{{field_name}}-env.sh",
        "format": "ENV_VARS"
    }
]
```

### Post Actions
```json
"post_actions": [
    {
        "action": "UPDATE_uDATA",
        "target": "uTEMPLATE/datasets/target_dataset.json"
    },
    {
        "action": "CREATE_DIRECTORIES",
        "paths": ["uMEMORY/path1", "uMEMORY/path2"]
    },
    {
        "action": "TRIGGER_PROCESS",
        "script": "uCORE/process_data.sh"
    }
]
```

## 🎯 Advanced Features

### Conditional Fields
```json
{
    "name": "conditional_field",
    "label": "🔄 Conditional Field",
    "type": "TEXT",
    "conditional": {
        "show_when": "other_field",
        "equals": "specific_value"
    },
    "noblank": true,
    "default": "conditional_default"
}
```

### Multi-Select Options
```json
{
    "name": "multi_field",
    "label": "📦 Select Multiple",
    "type": "MULTI_SELECT",
    "options": ["ITEM1", "ITEM2", "ITEM3"],
    "required": false,
    "noblank": true,
    "help": "Select one or more options",
    "default": ["ITEM1"]
}
```

### uDATA Selection
```json
{
    "name": "data_field",
    "label": "📊 uDATA Selection",
    "type": "uDATA_SELECT",
    "dataset": "DATASET_NAME",
    "display_field": "DISPLAY_FIELD",
    "value_field": "VALUE_FIELD",
    "search_fields": ["FIELD1", "FIELD2"],
    "predictive_search": true,
    "required": true,
    "noblank": true,
    "help": "Select from available uDATA values",
    "default": "DEFAULT_VALUE_FROM_uDATA"
}
```

## 📊 Complete Example

### Development Environment Setup
```json
{
    "title": "🔧 Development Environment Setup",
    "description": "Configure your development environment preferences and tools",
    "category": "SETUP",
    "version": "1.0.4.1",
    "fields": [
        {
            "name": "dev_language",
            "label": "💻 Primary Language",
            "type": "CHOICE",
            "options": ["BASH", "PYTHON", "JAVASCRIPT", "GO", "RUST", "OTHER"],
            "required": true,
            "noblank": true,
            "help": "Select your primary development language",
            "default": "BASH"
        },
        {
            "name": "editor_preference",
            "label": "✏️ Preferred Editor",
            "type": "CHOICE",
            "options": ["NANO", "VIM", "EMACS", "VSCODE", "OTHER"],
            "required": false,
            "noblank": true,
            "help": "Choose your preferred text editor",
            "default": "NANO"
        },
        {
            "name": "dev_location",
            "label": "📍 Development Location",
            "type": "LOCATION_LOOKUP",
            "uDATA": "locationMap",
            "required": true,
            "noblank": true,
            "help": "Select your development location for timezone setup",
            "default": "NEW_YORK"
        },
        {
            "name": "dev_password",
            "label": "🔐 Development Password",
            "type": "PASSWORD",
            "required": false,
            "noblank": false,
            "help": "Optional password for development tools (leave blank if not needed)",
            "default": ""
        }
    ],
    "actions": {
        "save": "AUTO",
        "validate": "REAL_TIME",
        "output_format": "JSON"
    },
    "output_files": [
        {
            "path": "uMEMORY/config/dev-environment.json",
            "format": "JSON"
        },
        {
            "path": "sandbox/config/dev-setup.env",
            "format": "ENV_VARS"
        }
    ],
    "post_actions": [
        {
            "action": "CONFIGURE_ENVIRONMENT",
            "create_directories": true
        },
        {
            "action": "UPDATE_uDATA",
            "target": "uMEMORY/system/user-preferences.json"
        }
    ]
}
```

## 🎯 Best Practices

### Data Collection Strategy
1. **Progressive Disclosure**: Start with essential fields, show advanced conditionally
2. **Logical Grouping**: Group related fields together
3. **Clear Navigation**: Use consistent field ordering
4. **Immediate Validation**: Provide real-time feedback
5. **Default Intelligence**: Use smart defaults based on context

### User Experience Guidelines
1. **Minimal Typing**: Provide defaults and choices where possible
2. **Clear Instructions**: Every field should have helpful guidance
3. **Visual Hierarchy**: Use emojis and formatting consistently
4. **Error Prevention**: Validate inputs before processing
5. **Progress Indication**: Show completion status for long forms

### Technical Considerations
1. **JSON Validation**: All configurations must be valid JSON
2. **Template Variables**: Use `{{field_name}}` for dynamic paths
3. **Dataset Integration**: Ensure referenced uDATA datasets exist
4. **Output Planning**: Define where and how data will be stored
5. **Error Handling**: Plan for validation failures and corrections

## 🚀 Quick Start Checklist

When creating a new GET form:

- [ ] Choose descriptive title with emoji
- [ ] Write clear description of purpose
- [ ] Set appropriate category (SETUP|CONFIG|DATA-ENTRY|SURVEY|MISSION)
- [ ] Define all required fields with meaningful defaults
- [ ] Set `noblank: true` for most fields (false only for passwords)
- [ ] Include helpful guidance text for each field
- [ ] Add validation patterns for TEXT inputs
- [ ] Configure output files and locations
- [ ] Define post-processing actions
- [ ] Test JSON syntax with `jq '.' filename.json`
- [ ] Validate with GET system test commands

## 🔌 Template Integration

### Variable Processing
- Use `{{field_name}}` for user input variables
- Use `[get:key]` for uDATA lookups
- Use `[user:key]` for user profile data
- Use `[timestamp]` for automatic timestamps

### Template Examples
```markdown
# Welcome {{username}}!

Your location: {{location}}
Your timezone: {{timezone}} ({{utc_offset}})
Setup completed: [timestamp]

## Your Configuration
Language: {{dev_language}}
Editor: {{editor_preference}}
Location: {{dev_location}}
```

---

## 🎯 Role-Based Access

GET forms respect the 8-role hierarchy:

- **Ghost**: Read-only access to form templates
- **Tomb**: Basic form completion
- **Crypt**: Personal data forms
- **Drone**: Automated form processing
- **Knight**: Security-related forms
- **Imp**: Development forms
- **Sorcerer**: Advanced configuration forms
- **Wizard**: Core system forms

---

*uDOS v1.0.4.1 GET System Documentation*
*Complete guide for interactive data collection forms*
