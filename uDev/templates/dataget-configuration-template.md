# 📝 uDOS Dataget Configuration Template

A **dataget** is a collection of questions designed to gather variable data from users through an interactive interface. This template guides you through creating effective datagets for uDOS.

## 🎯 Basic Structure

```json
{
    "title": "Your Dataget Title",
    "description": "Brief description of what this dataget collects",
    "category": "setup|configuration|data-entry|survey|mission",
    "version": "1.0.0",
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
    "type": "text",
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
    "type": "choice",
    "options": ["option1", "option2", "option3"],
    "required": true,
    "noblank": true,
    "help": "Choose from the available options",
    "default": "option1"
}
```

### Boolean (Yes/No)
```json
{
    "name": "boolean_field",
    "label": "✅ Enable Feature",
    "type": "boolean",
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
    "type": "password",
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
    "type": "multi_select",
    "options": ["item1", "item2", "item3"],
    "required": false,
    "noblank": true,
    "help": "Select one or more options",
    "default": ["item1"]
}
```

### Dataset Integration
```json
{
    "name": "dataset_field",
    "label": "📊 Data Selection",
    "type": "dataset_select",
    "dataset": "dataset_name",
    "display_field": "display_field",
    "value_field": "value_field",
    "search_fields": ["field1", "field2"],
    "predictive_search": true,
    "required": true,
    "noblank": true,
    "help": "Select from available dataset values",
    "default": "default_value_from_dataset"
}
```

## 🎨 Validation Rules Summary

### Dataset Validation Standards
1. **Cannot Be Blank**: All fields default to `noblank: true`
2. **Password Exception**: Password fields default to `noblank: false`
3. **Meaningful Defaults**: Required for all `noblank=true` fields
4. **Validation Patterns**: Include regex validation for text inputs
5. **Help Text**: Always provide clear, actionable help text

### Field Naming Conventions
- Use lowercase with underscores: `field_name`
- Be descriptive: `preferred_companion` not `companion`
- Avoid abbreviations unless industry standard

### Label Guidelines
- Include relevant emoji for visual identification
- Keep labels concise but descriptive
- Use consistent terminology across datagets

## 🔧 Advanced Features

### Conditional Fields
```json
{
    "name": "conditional_field",
    "label": "🔄 Conditional Field",
    "type": "text",
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
    "type": "choice",
    "options_source": "dataset",
    "depends_on": ["field1", "field2"],
    "noblank": true,
    "default": "auto_detect"
}
```

## 💾 Output Configuration

### Output Files
```json
"output_files": [
    {
        "path": "uMemory/collected/{{field_name}}.json",
        "format": "json",
        "template": "optional_template_name"
    },
    {
        "path": "uMemory/config/{{field_name}}-env.sh",
        "format": "env_vars"
    }
]
```

### Post Actions
```json
"post_actions": [
    {
        "action": "update_dataset",
        "target": "uTemplate/datasets/target_dataset.json"
    },
    {
        "action": "create_directories",
        "paths": ["uMemory/path1", "uMemory/path2"]
    },
    {
        "action": "trigger_process",
        "script": "uCode/process_data.sh"
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

## 📊 Example: Complete Dataget

```json
{
    "title": "🔧 Development Environment Setup",
    "description": "Configure your development environment preferences and tools",
    "category": "setup",
    "version": "1.0.0",
    "fields": [
        {
            "name": "dev_language",
            "label": "💻 Primary Language",
            "type": "choice",
            "options": ["bash", "python", "javascript", "go", "rust", "other"],
            "required": true,
            "noblank": true,
            "help": "Select your primary development language",
            "default": "bash"
        },
        {
            "name": "editor_preference",
            "label": "✏️ Preferred Editor",
            "type": "choice",
            "options": ["nano", "vim", "emacs", "vscode", "other"],
            "required": false,
            "noblank": true,
            "help": "Choose your preferred text editor",
            "default": "nano"
        },
        {
            "name": "dev_password",
            "label": "🔐 Development Password",
            "type": "password",
            "required": false,
            "noblank": false,
            "help": "Optional password for development tools (leave blank if not needed)",
            "default": ""
        }
    ],
    "actions": {
        "save": "auto",
        "validate": "real_time",
        "output_format": "json"
    },
    "output_files": [
        {
            "path": "uMemory/config/dev-environment.json",
            "format": "json"
        }
    ],
    "post_actions": [
        {
            "action": "configure_environment",
            "create_directories": true
        }
    ]
}
```

## 🚀 Quick Start Checklist

When creating a new dataget:

- [ ] Choose descriptive title with emoji
- [ ] Write clear description of purpose
- [ ] Set appropriate category
- [ ] Define all required fields with meaningful defaults
- [ ] Set `noblank: true` for most fields (false only for passwords)
- [ ] Include helpful guidance text for each field
- [ ] Add validation patterns for text inputs
- [ ] Configure output files and locations
- [ ] Define post-processing actions
- [ ] Test JSON syntax with `jq '.' filename.json`
- [ ] Validate with `./uCode/validate-input-system.sh test`

---

Remember: A good dataget reduces user effort while collecting high-quality, validated data. Always prioritize user experience and data integrity.
