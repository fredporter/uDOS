# uDOS Form Template Configuration
# Enhanced data collection forms with predictive input system integration

## 🎨 Form Template Structure

Each form configuration uses JSON format with the following structure:

```json
{
    "title": "Form Title",
    "description": "Brief description of the form purpose",
    "category": "setup|configuration|data-entry|survey",
    "version": "1.0.0",
    "fields": [
        {
            "name": "field_identifier",
            "label": "Display Label",
            "type": "field_type",
            "required": true|false,
            "validation": "regex_pattern",
            "help": "Help text for the user",
            "options": ["choice1", "choice2"],
            "default": "default_value",
            "dataset": "dataset_name",
            "conditional": {
                "show_when": "other_field_name",
                "equals": "value"
            }
        }
    ],
    "actions": {
        "save": "auto|manual",
        "validate": "real_time|on_submit",
        "output_format": "json|yaml|env_vars"
    }
}
```

## 📝 Field Types

### Text Input
```json
{
    "name": "username",
    "label": "Username",
    "type": "text",
    "required": true,
    "validation": "^[a-zA-Z][a-zA-Z0-9_]{2,19}$",
    "help": "Enter a username (3-20 characters, alphanumeric and underscore only)"
}
```

### Choice Selection (Dropdown/Radio)
```json
{
    "name": "theme",
    "label": "Interface Theme", 
    "type": "choice",
    "options": ["dark", "light", "matrix", "cyberpunk"],
    "default": "dark",
    "help": "Choose your preferred visual theme"
}
```

### Multi-Select (Checkbox group)
```json
{
    "name": "features",
    "label": "Enable Features",
    "type": "multi_select",
    "options": ["auto_backup", "notifications", "advanced_mode", "debug_logging"],
    "help": "Select features to enable (multiple selections allowed)"
}
```

### Boolean (Yes/No)
```json
{
    "name": "auto_backup",
    "label": "Enable Auto Backup",
    "type": "boolean",
    "default": true,
    "help": "Automatically backup your work and configurations"
}
```

### Password Input
```json
{
    "name": "password",
    "label": "Password",
    "type": "password",
    "required": true,
    "validation": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d@$!%*?&]{8,}$",
    "help": "Minimum 8 characters with uppercase, lowercase, and number"
}
```

### Email Address
```json
{
    "name": "email",
    "label": "Email Address",
    "type": "email",
    "validation": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "help": "Enter a valid email address"
}
```

### Number Input
```json
{
    "name": "port",
    "label": "Port Number",
    "type": "number",
    "min": 1024,
    "max": 65535,
    "default": 8080,
    "help": "Enter port number (1024-65535)"
}
```

### Dataset-Linked Selection
```json
{
    "name": "location",
    "label": "Location",
    "type": "dataset_select",
    "dataset": "locationMap",
    "display_field": "city_display",
    "value_field": "tile_reference",
    "search_fields": ["city", "country", "tile"],
    "help": "Search and select from global location database"
}
```

### File Path Input
```json
{
    "name": "config_path",
    "label": "Configuration File Path",
    "type": "file_path",
    "file_type": "file|directory", 
    "extensions": [".json", ".yaml", ".conf"],
    "default": "~/uDOS/config/",
    "help": "Select configuration file location"
}
```

### Date/Time Input
```json
{
    "name": "scheduled_time",
    "label": "Schedule Time",
    "type": "datetime",
    "format": "YYYY-MM-DD HH:mm",
    "timezone_aware": true,
    "help": "Select date and time for scheduling"
}
```

## 🔄 Conditional Fields

Fields can be shown/hidden based on other field values:

```json
{
    "name": "database_config",
    "label": "Database Configuration",
    "type": "text",
    "conditional": {
        "show_when": "use_database",
        "equals": true
    },
    "help": "Database connection string (shown only if database is enabled)"
}
```

## 📊 Dataset Integration

Fields can integrate with uDOS datasets for intelligent suggestions:

```json
{
    "name": "timezone",
    "label": "Timezone",
    "type": "dataset_select",
    "dataset": "timezoneMap",
    "display_field": "timezone_display",
    "value_field": "timezone_code",
    "search_fields": ["timezone_name", "timezone_code", "utc_offset"],
    "predictive_search": true,
    "help": "Search timezones by name, code, or UTC offset"
}
```

## 🎨 Visual Styling

Forms automatically adapt to uDOS ASCII interface styling:

- **Block Width**: Adapts to terminal size using `$UDOS_BLOCK_WIDTH`
- **Border Style**: Uses configured border style from display settings
- **Colors**: Integrates with uDOS color scheme
- **Navigation**: Consistent arrow key and keyboard navigation
- **Validation**: Real-time visual feedback for errors

## 📥 Form Output

Forms can generate multiple output formats:

### JSON Output (default)
```json
{
    "username": "agentdigital",
    "theme": "dark",
    "auto_backup": true,
    "email": "user@example.com",
    "form_metadata": {
        "completed_at": "2025-07-20T10:30:00Z",
        "version": "1.0.0"
    }
}
```

### Environment Variables
```bash
# Generated environment variables
export UDOS_USERNAME="agentdigital"
export UDOS_THEME="dark"  
export UDOS_AUTO_BACKUP="true"
export UDOS_EMAIL="user@example.com"
```

### YAML Output
```yaml
username: agentdigital
theme: dark
auto_backup: true
email: user@example.com
form_metadata:
  completed_at: 2025-07-20T10:30:00Z
  version: 1.0.0
```

## 🚀 Integration Examples

### User Setup Form
Complete user onboarding with dataset integration:

```json
{
    "title": "uDOS User Setup",
    "description": "Complete your uDOS environment configuration",
    "category": "setup",
    "fields": [
        {
            "name": "username",
            "label": "Username",
            "type": "text",
            "required": true,
            "validation": "^[a-zA-Z][a-zA-Z0-9_]{2,19}$"
        },
        {
            "name": "location",
            "label": "Location", 
            "type": "dataset_select",
            "dataset": "locationMap",
            "predictive_search": true
        },
        {
            "name": "timezone",
            "label": "Timezone",
            "type": "dataset_select", 
            "dataset": "timezoneMap",
            "predictive_search": true
        },
        {
            "name": "role",
            "label": "Primary Role",
            "type": "choice",
            "options": ["developer", "analyst", "admin", "user"]
        }
    ]
}
```

### System Configuration Form
```json
{
    "title": "System Configuration",
    "description": "Configure uDOS system settings",
    "category": "configuration",
    "fields": [
        {
            "name": "debug_mode",
            "label": "Enable Debug Mode",
            "type": "boolean",
            "default": false
        },
        {
            "name": "log_level",
            "label": "Logging Level",
            "type": "choice",
            "options": ["ERROR", "WARN", "INFO", "DEBUG"],
            "default": "INFO",
            "conditional": {
                "show_when": "debug_mode",
                "equals": true
            }
        },
        {
            "name": "backup_schedule",
            "label": "Backup Schedule",
            "type": "choice", 
            "options": ["hourly", "daily", "weekly", "manual"],
            "default": "daily"
        }
    ]
}
```

## 🎯 Usage in uCode Shell

The input system integrates directly with the uCode shell:

```bash
# Launch shortcode selector with [ trigger
ucode [

# Process a form configuration
ucode FORM user-setup

# Create new mission with form
ucode MISSION CREATE --form

# Enhanced setup with forms
ucode SETUP --interactive
```

## 📁 File Organization

Form templates are organized in the uTemplate directory:

```
uTemplate/
├── forms/
│   ├── user-setup.json
│   ├── system-config.json  
│   ├── mission-create.json
│   └── data-import.json
├── datasets/
│   ├── locationMap.json
│   ├── timezoneMap.json
│   └── shortcodes.json
└── variables/
    └── form-outputs/
```

This template system provides a comprehensive foundation for creating rich, interactive forms that integrate seamlessly with the uDOS ecosystem while maintaining the signature ASCII visual style.
