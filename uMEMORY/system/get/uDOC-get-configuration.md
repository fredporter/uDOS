# 📝 uDOS GET Configuration Documentation

**Type**: Documentation
**Version**: v1.3.3
**Purpose**: Guide for creating effective GET forms for uDOS
**Location**: uMEMORY/system/get/

> **Category**: uGET System Documentation
> **Target**: Form builders and system integrators
> **Integration**: uMEMORY, uCORE, uDATA systems

---

A **GET** is a collection of questions designed to gather variable data from users through an interactive interface. This documentation guides you through creating effective GET forms for uDOS.

## 🎯 Basic GET Structure

```json
{
    "title": "Your GET Title",
    "description": "Brief description of what this GET collects",
    "category": "SETUP|CONFIG|DATA-ENTRY|SURVEY|MISSION",
    "version": "1.3.3",
    "fields": [
        // Field definitions go here
    ],
    "actions": {
        // Processing actions
    },
    "output_files": [
        // Where to save the collected data
    ],
    "post_actions": [
        // What to do after data collection
    ]
}
```

## 📋 Field Types and Validation Rules

### Required Field Properties
- **`noblank`**: Defaults to `true` for all fields except password
- **`default`**: Must provide meaningful default for all `noblank=true` fields
- **`help`**: Always include contextual help text

### Text Input
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

### Choice Selection
```json
{
    "name": "choice_field",
    "label": "📋 Select Option",
    "type": "CHOICE",
    "options": ["OPTION1", "OPTION2", "OPTION3"],
    "required": true,
    "noblank": true,
    "help": "Choose from the available options",
    "default": "OPTION1"
}
```

### Boolean (Yes/No)
```json
{
    "name": "boolean_field",
    "label": "✅ Enable Feature",
    "type": "BOOLEAN",
    "required": false,
    "noblank": true,
    "help": "Enable or disable this feature",
    "default": false
}
```

### Password Field (Special Case)
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

### Multi-Select
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

### uDATA Integration
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

## 🎨 Validation Rules Summary

### uDATA Validation Standards
1. **Cannot Be Blank**: All fields default to `noblank: true`
2. **Password Exception**: Password fields default to `noblank: false`
3. **Meaningful Defaults**: Required for all `noblank=true` fields
4. **Validation Patterns**: Include regex validation for TEXT inputs
5. **Help Text**: Always provide clear, actionable help text

### Field Naming Conventions
- Use lowercase with underscores: `field_name`
- Be descriptive: `preferred_companion` not `companion`
- Avoid abbreviations unless industry standard

### Label Guidelines
- Include relevant emoji for visual identification
- Keep labels concise but descriptive
- Use consistent terminology across GET forms

## 🔧 Advanced Features

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

### Field Dependencies
```json
{
    "name": "dependent_field",
    "label": "🔗 Dependent Field",
    "type": "CHOICE",
    "options_source": "uDATA",
    "depends_on": ["field1", "field2"],
    "noblank": true,
    "default": "AUTO_DETECT"
}
```

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

## 🎯 Best Practices

### Data Collection Strategy
1. **Progressive Disclosure**: Start with essential fields, show advanced options conditionally
2. **Logical Grouping**: Group related fields together
3. **Clear Navigation**: Use consistent field ordering
4. **Immediate Validation**: Provide real-time feedback
5. **Default Intelligence**: Use smart defaults based on context

### User Experience Guidelines
1. **Minimal Typing**: Provide defaults and choices where possible
2. **Clear Instructions**: Every field should have helpful guidance
3. **Visual Hierarchy**: Use emojis and formatting consistently
4. **Error Prevention**: Validate inputs before processing
5. **Progress Indication**: Show completion status for long datagets

### Technical Considerations
1. **JSON Validation**: All configurations must be valid JSON
2. **Template Variables**: Use `{{field_name}}` for dynamic paths
3. **Dataset Integration**: Ensure referenced datasets exist
4. **Output Planning**: Define where and how data will be stored
5. **Error Handling**: Plan for validation failures and user corrections

## 📊 Example: Complete GET Form

```json
{
    "title": "🔧 Development Environment SETUP",
    "description": "Configure your development environment preferences and tools",
    "category": "SETUP",
    "version": "1.3.3",
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
        }
    ],
    "post_actions": [
        {
            "action": "CONFIGURE_ENVIRONMENT",
            "create_directories": true
        }
    ]
}
```

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
- [ ] Validate with `./uCORE/validate-input-system.sh TEST`

---

Remember: A good GET form reduces user effort while collecting high-quality, validated data. Always prioritize user experience and data integrity.

---

*uDOS v1.3.3 GET Configuration Documentation - uGET System*
