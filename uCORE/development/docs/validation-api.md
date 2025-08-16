# uDOS Validation API Documentation

## Template Validation Functions

### `validate_dataget_schema(dataget_file)`
Validates a dataget JSON configuration against schema rules.

**Parameters:**
- `dataget_file`: Path to dataget JSON file

**Returns:**
- 0 on success, 1 on failure

**Validates:**
- JSON syntax
- Required fields (title, description, fields)
- Field structure and types
- noblank logic
- Default value requirements

### `validate_dataset_schema(dataset_file)`
Validates dataset JSON files.

**Parameters:**
- `dataset_file`: Path to dataset JSON file

**Returns:**
- 0 on success, 1 on failure

### `validate_template_files(template_dir)`
Validates all template files in a directory.

**Parameters:**
- `template_dir`: Directory containing templates

**Returns:**
- 0 on success, 1 on failure

**Supports:**
- JSON templates
- YAML templates (if yq available)
- Markdown templates

## Schema Validation Rules

### Dataget Fields
- `noblank`: Defaults to `true`, must be `false` for password fields
- `default`: Required when `noblank=true` (except passwords)
- `validation`: Recommended for text and email fields
- `help`: Required for all fields

### Dataset Structure
- Must contain valid JSON
- Schema varies by dataset type
- Shortcode datasets require `shortcodes` array
- Each shortcode needs `command`, `category`, `description`

## Error Handling
All validation functions provide detailed error messages and return appropriate exit codes for scripting integration.
