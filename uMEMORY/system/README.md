# uMEMORY System Configuration v1.3.3

This directory contains system configuration files in uDATA format - minified JSON with one record per line, maintaining compatibility with standard JSON tools while optimizing for uDOS processing.

## Contents

### uDATA System Files (✅ CLEAN FILENAMES)
- `uDATA-commands.json` - Core command definitions and metadata (v1.3.3)
- `uDATA-shortcodes.json` - Shortcode definitions and mappings
- `uDATA-user-roles.json` - Role-based permission and access definitions
- `uDATA-variable-system.json` - System variable definitions and configurations
- `uDATA-colours.json` - Color palette definitions (Polaroid Colors default)## uDATA Format Specification

### Format Features:
- **Minified JSON**: No extra whitespace, optimized for performance
- **One Record Per Line**: Fast parsing and streaming support
- **Standard Compatible**: Works with regular JSON tools and parsers
- **Metadata Header**: First record contains system metadata

### Example Format:
```json
{"metadata":{"system":"uDOS-v1.3.3","format":"uDATA-v1","version":"1.3.3"}}
{"command":"HELP","category":"system","description":"Dynamic help system"}
{"command":"GRID","category":"ugrid","description":"Advanced grid operations"}
```

## System Integration

### uCORE Engine Access
- Help system reads directly from `uDATA-commands.json`
- Role system processes `uDATA-user-roles.json`
- Color system uses `uDATA-colours.json` (Polaroid Colors default)

### Template System Access
```bash
[GET-COMMANDS] → uDATA-commands.json
[GET-ROLES] → uDATA-user-roles.json
[GET-COLORS] → uDATA-colours.json
```

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
