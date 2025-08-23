# uMEMORY System Configuration v1.3.3

This directory contains system configuration files, command definitions, operational data, and the new unified data management system for uDOS v1.3.3.

## Contents

### Command Definitions
- `commands.json` - Core command definitions and metadata
- `ucode-commands.json` - uCode-specific command configurations
- `vb-commands.json` - Visual Basic-style command definitions
- `dynamic-commands.json` - Dynamically loaded command configurations

### System Configuration
- `user-roles.json` - Role-based permission and access definitions
- `variable-system.json` - System variable definitions and configurations
- `shortcodes.json` - Shortcode definitions and mappings

### v1.3.3 Data Management System

#### `/get/` - Data Retrieval System
- `user-data/` - User profile information
- `setup-status/` - User setup completion status
- `location/` - Geographic data cache
- `timezone/` - Timezone information
- `system-status/` - System health and status
- `preferences/` - User preference data

#### `/post/` - Data Creation/Submission System
- `user-creation/` - New user setup data
- `form-submissions/` - Form submission data
- `preference-updates/` - User preference changes
- `location-updates/` - Location data updates
- `system-configs/` - System configuration changes

#### `/templates/` - System Template Repository
- `core/` - Essential system templates
- `user/` - User interface templates
- `forms/` - Data collection templates
- `components/` - Reusable template components
- `reports/` - Output formatting templates

## v1.3.3 uCODE Integration

### Data Access Commands
```bash
[GET-RETRIEVE] {DATA-SOURCE | QUERY-PARAMS}
[POST-CREATE] {DATA-TYPE | PAYLOAD}
[POST-SUBMIT] {FORM-NAME | DATA}
```

### Template Processing
```bash
[TEMPLATE-RENDER] {TEMPLATE-NAME | DATA-SOURCE}
[TEMPLATE-VALIDATE] {TEMPLATE-PATH}
[COMPONENT-LOAD] {COMPONENT-NAME | CONTEXT}
```

### Function Standards
```bash
<FORMAT-TIMESTAMP>
<RESOLVE-LOCATION>
<HUMANIZE-KEY>
<SLUGIFY>
```

## Template Integration

Templates access system data using enhanced uCODE syntax:
```handlebars
{{#WITH [GET-RETRIEVE] {USER-DATA | USERNAME}}}
- Name: {{FULL-NAME}}
- Email: {{EMAIL | <VALIDATE-EMAIL>}}
{{/WITH}}
```

## Data Format Standards

All v1.3.3 data files use JSON format with UPPERCASE-DASH field names:
```json
{
    "FIELD-NAME": "value",
    "CREATED-DATE": "2025-08-22T10:00:00Z",
    "LAST-UPDATED": "2025-08-22T10:00:00Z"
}
```

## Legacy Integration

Legacy systems continue to work alongside v1.3.3 enhancements:
- Existing command processing remains functional
- Role-based directory permissions maintained
- Shortcode expansion system preserved
- Backward compatibility for all existing configurations

## System Version

- Core System: v1.3.3
- Template Engine: v1.3.3
- Data Management: v1.3.3
- Legacy Compatibility: Full
