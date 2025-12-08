# Help Templates Directory

This directory contains structured JSON templates for uDOS command documentation.

## Purpose

Help templates provide detailed, structured information about commands that can be:
- Loaded by the HelpManager service for enhanced help output
- Used to generate documentation automatically
- Parsed by tools for command completion and validation
- Referenced for API documentation

## Structure

```
help_templates/
├── _index.json                    # Template catalog and metadata
├── system_commands.json           # System administration commands
├── file_commands.json             # File operations
├── assistant_commands.json        # AI assistant commands
├── grid_commands.json             # Grid management
└── README.md                      # This file
```

## Template Format

Each template file follows this structure:

```json
{
  "category": "Category Name",
  "description": "Category description",
  "commands": {
    "COMMAND_NAME": {
      "name": "COMMAND_NAME",
      "syntax": ["COMMAND [options]"],
      "description": "Brief description",
      "detailed": "Detailed explanation",
      "parameters": [
        {
          "name": "param_name",
          "type": "string|integer|boolean",
          "optional": true,
          "description": "Parameter description"
        }
      ],
      "examples": [
        {
          "command": "COMMAND example",
          "description": "What this does"
        }
      ],
      "related": ["RELATED_CMD1", "RELATED_CMD2"],
      "notes": ["Important information"],
      "version_added": "1.0.0",
      "version_enhanced": "1.0.12"
    }
  }
}
```

## Fields Explained

### Command Object

- **name**: Official command name (uppercase)
- **syntax**: Array of syntax variations
- **description**: One-line summary (max 80 chars)
- **detailed**: Full explanation (multiple sentences)
- **parameters**: Array of parameter objects
- **examples**: Array of example usage objects
- **related**: Array of related command names
- **notes**: Array of important notes and tips
- **version_added**: Version when command was introduced
- **version_enhanced**: Version when significantly enhanced (optional)

### Parameter Object

- **name**: Parameter name
- **type**: Data type (string, integer, boolean, etc.)
- **optional**: Whether parameter is optional (boolean)
- **description**: What the parameter does

### Example Object

- **command**: Full command with parameters
- **description**: What the example demonstrates

## Integration with HelpManager

The HelpManager service can load these templates to enhance help output:

```python
from core.services.help_manager import HelpManager

help_manager = HelpManager(templates_dir="data/system/help_templates")
help_text = help_manager.format_help_from_template("HELP")
```

## Creating New Templates

When adding commands to new categories:

1. Create a new JSON file following the structure above
2. Add entry to `_index.json`
3. Update this README with the new category
4. Consider adding examples that demonstrate real use cases

## Version History

- **v1.0.12**: Initial help templates system
  - System commands template
  - File operations template
  - AI assistant template
  - Grid management template
  - Template index and documentation

## Future Enhancements

- [ ] Navigation commands template
- [ ] Server management template
- [ ] Knowledge system template
- [ ] Extension system template
- [ ] Template validation schema
- [ ] Automated documentation generation from templates
