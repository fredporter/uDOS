# API Reference - uDOS Extension Development

Complete API reference for building uDOS extensions, integrating with core systems, and extending functionality.

## 📚 Table of Contents

1. [Core APIs](#core-apis)
2. [Extension System](#extension-system)
3. [Knowledge Bank API](#knowledge-bank-api)
4. [Configuration API](#configuration-api)
5. [uCODE Scripting API](#ucode-scripting-api)
6. [OK Assist (AI) API](#ok-assist-ai-api)
7. [Theme System API](#theme-system-api)
8. [Command System API](#command-system-api)

---

## Core APIs

### Config - Unified Configuration Manager

```python
from core.config import Config

# Initialize configuration
config = Config()

# Environment variables (.env)
api_key = config.get_env('GEMINI_API_KEY')
config.set_env('CUSTOM_KEY', 'value')
config.save_env()

# User settings (user.json)
username = config.get('username', 'default')
config.set('theme', 'synthwave')
config.save()

# Runtime state
config.runtime['current_session'] = 'session-123'
```

**Key Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `get_env(key, default=None)` | Get environment variable | str/None |
| `set_env(key, value)` | Set environment variable | None |
| `save_env()` | Save .env file | bool |
| `get(key, default=None)` | Get user setting | Any |
| `set(key, value)` | Set user setting | None |
| `save()` | Save user.json | bool |
| `get_all_config()` | Get complete config | dict |

**Environment Keys:**

```python
ENV_KEYS = {
    'GEMINI_API_KEY': 'Gemini AI API Key',
    'OPENROUTER_API_KEY': 'OpenRouter API Key',
    'ANTHROPIC_API_KEY': 'Anthropic API Key',
    'OPENAI_API_KEY': 'OpenAI API Key',
    'UDOS_USERNAME': 'Username',
    'UDOS_INSTALLATION_ID': 'Installation ID',
    'DEFAULT_WORKSPACE': 'Default workspace',
    'DEFAULT_MODEL': 'Default AI model',
    'AUTO_START_WEB': 'Auto-start web dashboard',
    'AUTO_START_SERVER': 'Auto-start HTTP server',
    'HTTP_SERVER_PORT': 'HTTP server port',
    'THEME': 'Color theme',
    'MAX_SESSION_HISTORY': 'Max session history',
    'AUTO_SAVE_SESSION': 'Auto-save session',
}
```

---

## Extension System

### ExtensionManager - Install & Verify Extensions

```python
from extensions.core.extension_manager import ExtensionManager

# Initialize manager
manager = ExtensionManager()

# Check installation status
is_installed = manager.check_extension_installed('typo')

# Install extension
success, message = manager.install_extension('micro', quiet=True)

# Get all extension statuses
statuses = manager.get_extension_status()
# Returns: {'typo': True, 'micro': False, ...}

# Install missing extensions
results = manager.install_missing_extensions(quiet=True)

# Verify all extensions
all_ok, details = manager.verify_all_extensions()

# Get extension info
info = manager.get_extension_info('typo')
```

**Extension Types:**

- `typo` - Web markdown editor
- `micro` - Terminal text editor
- `monaspace` - Monaspace fonts
- `cmd` - Web terminal interface

### ExtensionDevTools - Create Extensions

```python
from extensions.core.extension_dev_tools import ExtensionDevTools

# Initialize dev tools
dev = ExtensionDevTools()

# Create new extension from template
success = dev.create_extension_template(
    name="my-extension",
    ext_type="web",  # web, cli, service
    port=8090,
    author="Your Name"
)

# Validate extension
is_valid, errors = dev.validate_extension("my-extension")

# Package extension for distribution
success = dev.package_extension("my-extension")

# Test extension
results = dev.test_extension("my-extension")
```

**Extension Template Structure (Web):**

```
my-extension/
├── extension.json          # Metadata
├── server.py              # HTTP server
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── assets/
└── templates/
    └── index.html
```

**extension.json Schema:**

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "type": "web",
  "author": "Your Name",
  "description": "Extension description",
  "port": 8090,
  "entry_point": "server.py",
  "dependencies": [],
  "permissions": ["filesystem", "network"],
  "compatibility": {
    "min_udos_version": "1.4.0"
  }
}
```

### ExtensionMetadataManager - Metadata & Security

```python
from extensions.core.extension_metadata_manager import ExtensionMetadataManager

# Initialize metadata manager
meta = ExtensionMetadataManager()

# Load extension metadata
metadata = meta.load_extension_metadata("my-extension")

# Validate metadata
is_valid, message = meta.validate_extension_metadata("my-extension", metadata)

# Check compatibility
compatible, issues = meta.check_compatibility(metadata)

# Get security information
security_info = meta.get_extension_security_info("my-extension")

# Generate comprehensive report
report = meta.generate_extension_report("my-extension")
```

---

## Knowledge Bank API

### Generating Content

```python
from extensions.core.ok_assist.ok_assist import OKAssist

# Initialize OK Assist
assistant = OKAssist()

# Generate survival guide
guide = assistant.generate_guide(
    topic="water purification",
    category="water",
    complexity="detailed",  # simple, detailed, technical
    format="markdown"
)

# Generate diagram (multi-format)
diagrams = assistant.generate_diagram(
    topic="fire triangle",
    style="technical",  # technical, hand-drawn, hybrid
    formats=["ascii", "teletext", "svg-technical", "svg-organic"]
)

# Batch generation
results = assistant.batch_generate(
    topics=["topic1", "topic2", "topic3"],
    category="survival",
    template="guide_template.md"
)
```

### Knowledge Organization

```python
from core.knowledge.knowledge_manager import KnowledgeManager

# Initialize knowledge manager
km = KnowledgeManager()

# Search knowledge bank
results = km.search(
    query="water filtration",
    category="water",  # Optional filter
    tags=["purification", "treatment"]
)

# Get guide metadata
metadata = km.get_guide_metadata("water/boiling.md")

# List all guides in category
guides = km.list_category_guides("water")

# Get cross-references
refs = km.get_cross_references("water/boiling.md")

# Add guide to knowledge bank
km.add_guide(
    content=guide_content,
    category="water",
    tags=["purification", "emergency"],
    metadata={
        "author": "OK Assist",
        "difficulty": "beginner",
        "time_required": "15 minutes"
    }
)
```

---

## Configuration API

### User Preferences

```python
from core.config import Config

config = Config()

# Theme settings
config.set('theme', 'synthwave')
config.set('font_size', 14)
config.set('color_scheme', 'dark')

# Workspace settings
config.set('default_workspace', '/Users/me/workspace')
config.set('auto_save', True)
config.set('session_history_size', 100)

# AI settings
config.set('default_model', 'gemini-1.5-pro')
config.set('max_tokens', 8000)
config.set('temperature', 0.7)

# Save all changes
config.save()
```

### Environment Configuration

```python
# API keys
config.set_env('GEMINI_API_KEY', 'your-api-key')
config.set_env('OPENROUTER_API_KEY', 'your-api-key')

# System settings
config.set_env('HTTP_SERVER_PORT', '8080')
config.set_env('AUTO_START_WEB', 'true')

# Save environment
config.save_env()
```

---

## uCODE Scripting API

### UCodeValidator - Syntax Validation

```python
from core.ucode.validator import UCodeValidator

# Initialize validator
validator = UCodeValidator()

# Validate script file
is_valid, errors = validator.validate_file("script.uscript")

# Lint script with details
stats = validator.lint("script.uscript")
# Returns: {
#   'lines': 100,
#   'commands': 25,
#   'variables': 5,
#   'comments': 10,
#   'errors': [],
#   'warnings': []
# }

# Validate script content
script_content = "[GENERATE|guide|water]"
is_valid, errors = validator.validate_script(script_content)

# Strict mode (warnings as errors)
is_valid, errors = validator.validate_file("script.uscript", strict=True)
```

### UCodeParser - Parse Scripts

```python
from core.ucode.parser import UCodeParser

# Initialize parser
parser = UCodeParser()

# Parse script file
commands = parser.parse_file("script.uscript")

# Parse individual command
command = parser.parse_command("[GENERATE|guide|water|$topic]")
# Returns: {
#   'command': 'GENERATE',
#   'params': ['guide', 'water', '$topic'],
#   'variables': ['topic'],
#   'line': 1
# }

# Extract variables
variables = parser.extract_variables(script_content)

# Get YAML frontmatter
metadata = parser.parse_frontmatter("script.uscript")
```

### CommandRegistry - Available Commands

```python
from core.ucode.validator import CommandRegistry

# Get all commands
all_commands = CommandRegistry.COMMANDS

# Check command exists
exists = CommandRegistry.has_command('GENERATE')

# Get command schema
schema = CommandRegistry.get_schema('GENERATE')
# Returns: {
#   'required': ['type'],
#   'params': ['type', 'category', 'topic', 'options'],
#   'description': 'Generate content (guides, diagrams, etc.)'
# }

# Validate command parameters
is_valid = CommandRegistry.validate_params(
    'GENERATE',
    ['guide', 'water', 'filtration']
)
```

**Available Commands:**

| Category | Commands |
|----------|----------|
| **Content** | GENERATE, CONVERT, REFRESH |
| **Organization** | MANAGE, SEARCH, CLEANUP |
| **Execution** | MISSION, PARALLEL, REMOTE |
| **System** | CONFIG, SYSTEM, EXTENSION |
| **Control** | IF, FOR, TRY, CONTINUE, EXIT |
| **Output** | LOG, NOTIFY, REPORT |
| **Utilities** | DATE, HELP, VERSION, STATUS |

---

## OK Assist (AI) API

### OKAssist - AI Content Generation

```python
from extensions.core.ok_assist.ok_assist import OKAssist

# Initialize with API key
assistant = OKAssist(api_key="your-gemini-key")

# Generate text content
response = assistant.generate_text(
    prompt="Explain water purification",
    max_tokens=2000,
    temperature=0.7
)

# Generate with enhanced prompts
response = assistant.generate_enhanced(
    topic="fire starting",
    complexity="detailed",
    style="technical",
    perspective="isometric",
    annotations=["labels", "dimensions"]
)

# Multi-format diagram generation
diagrams = assistant.generate_multi_format(
    topic="shelter construction",
    formats=["ascii", "teletext", "svg-technical"]
)

# Batch processing
results = assistant.batch_process(
    items=["topic1", "topic2", "topic3"],
    operation="generate_guide",
    parallel=True
)
```

### Enhanced Prompt Controls

```python
# Complexity levels
complexity_options = ["simple", "detailed", "technical"]

# Style variations
style_options = ["technical", "hand-drawn", "hybrid", "minimalist"]

# Perspective options
perspective_options = ["isometric", "top-down", "side-view", "3d-perspective"]

# Annotation layers
annotation_options = ["labels", "dimensions", "callouts", "notes", "warnings"]

# Category-specific templates
categories = [
    "water", "fire", "shelter", "food",
    "navigation", "medical", "tools", "communication"
]
```

---

## Theme System API

### Theme Manager

```python
from core.theme.theme_manager import ThemeManager

# Initialize theme manager
themes = ThemeManager()

# Get available themes
available = themes.list_themes()

# Load theme
theme_data = themes.load_theme("synthwave")

# Apply theme
themes.apply_theme("synthwave")

# Get current theme
current = themes.get_current_theme()

# Create custom theme
themes.create_theme(
    name="my-theme",
    base="c64",
    colors={
        "primary": "#00FF00",
        "background": "#000000",
        "text": "#FFFFFF"
    }
)
```

**Built-in Themes:**

- `c64` - Commodore 64 (blue/purple)
- `nes` - 8-bit Nintendo (red/white)
- `synthwave` - Cyberpunk (pink/cyan)
- `teletext` - Broadcast TV (8 colors)
- `mac-os` - Classic Mac (monochrome)
- `terminal` - Green phosphor
- `amber` - Amber monitor
- `paper` - White/sepia

---

## Command System API

### Command Registration

```python
from core.commands.command_registry import CommandRegistry

# Register custom command
@CommandRegistry.register('CUSTOM')
def custom_command(params, context):
    """Custom command implementation."""
    # Process command
    result = process_params(params)
    return result

# Unregister command
CommandRegistry.unregister('CUSTOM')

# Get command handler
handler = CommandRegistry.get_handler('GENERATE')

# Execute command
result = CommandRegistry.execute('GENERATE', ['guide', 'water'])
```

### Command Context

```python
# Command context structure
context = {
    'workspace': '/path/to/workspace',
    'user': 'username',
    'session_id': 'session-123',
    'config': config_object,
    'variables': {'var1': 'value1'},
    'output_format': 'markdown',
    'verbose': True
}

# Access in command handler
def my_command(params, context):
    workspace = context['workspace']
    user = context['user']
    config = context['config']
    # Process command...
```

---

## Best Practices

### 1. Error Handling

```python
from core.exceptions import UDOSError, ValidationError

try:
    result = risky_operation()
except ValidationError as e:
    print(f"Validation failed: {e}")
except UDOSError as e:
    print(f"System error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 2. Logging

```python
from core.logger import get_logger

logger = get_logger(__name__)

logger.info("Operation started")
logger.warning("Potential issue detected")
logger.error("Operation failed", exc_info=True)
logger.debug("Debug information", extra={'data': debug_data})
```

### 3. Configuration Management

```python
# Always use Config for settings
from core.config import Config

config = Config()

# Read settings
value = config.get('setting_name', default_value)

# Write settings
config.set('setting_name', new_value)
config.save()

# Never hardcode paths or keys
api_key = config.get_env('GEMINI_API_KEY')  # ✅ Good
api_key = "hardcoded-key"  # ❌ Bad
```

### 4. Extension Isolation

```python
# Keep extension code in isolated namespace
class MyExtension:
    def __init__(self):
        self.name = "my-extension"
        self.version = "1.0.0"
        self.config = {}

    def initialize(self, udos_context):
        """Initialize with uDOS context."""
        self.context = udos_context
        self.config = udos_context.config

    def cleanup(self):
        """Clean up resources on shutdown."""
        pass
```

---

## Example: Complete Extension

```python
"""
Example uDOS Extension - Water Quality Checker
Demonstrates API usage and best practices.
"""

from core.config import Config
from core.knowledge.knowledge_manager import KnowledgeManager
from extensions.core.ok_assist.ok_assist import OKAssist
from core.logger import get_logger

class WaterQualityExtension:
    """Check water quality and suggest purification methods."""

    def __init__(self):
        self.name = "water-quality-checker"
        self.version = "1.0.0"
        self.logger = get_logger(__name__)

        # Initialize dependencies
        self.config = Config()
        self.knowledge = KnowledgeManager()
        self.assistant = OKAssist(
            api_key=self.config.get_env('GEMINI_API_KEY')
        )

    def check_quality(self, water_source: str, location: str):
        """
        Check water quality and recommend purification.

        Args:
            water_source: Type of water source (river, lake, rain, etc.)
            location: Geographic location

        Returns:
            dict: Quality assessment and recommendations
        """
        self.logger.info(f"Checking {water_source} at {location}")

        # Search knowledge bank for relevant guides
        guides = self.knowledge.search(
            query=f"{water_source} purification",
            category="water"
        )

        # Generate AI recommendation
        prompt = f"""
        Assess water quality for:
        Source: {water_source}
        Location: {location}

        Provide:
        1. Likely contaminants
        2. Recommended purification methods
        3. Safety considerations
        """

        assessment = self.assistant.generate_text(
            prompt=prompt,
            max_tokens=1000
        )

        return {
            'source': water_source,
            'location': location,
            'assessment': assessment,
            'relevant_guides': guides,
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self, assessment: dict) -> str:
        """Generate formatted report."""
        report = f"""
# Water Quality Assessment

**Source:** {assessment['source']}
**Location:** {assessment['location']}
**Date:** {assessment['timestamp']}

## Assessment

{assessment['assessment']}

## Relevant Guides

"""
        for guide in assessment['relevant_guides']:
            report += f"- [{guide['title']}]({guide['path']})\n"

        return report

# Extension entry point
def initialize(udos_context):
    """Initialize extension with uDOS context."""
    extension = WaterQualityExtension()
    return extension
```

---

## API Reference Summary

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **Config** | Configuration management | get(), set(), get_env(), set_env() |
| **ExtensionManager** | Extension installation | install_extension(), verify_all_extensions() |
| **ExtensionDevTools** | Extension development | create_extension_template(), validate_extension() |
| **KnowledgeManager** | Knowledge bank access | search(), add_guide(), list_category_guides() |
| **OKAssist** | AI content generation | generate_guide(), generate_diagram(), batch_process() |
| **UCodeValidator** | Script validation | validate_file(), lint(), validate_script() |
| **UCodeParser** | Script parsing | parse_file(), parse_command(), extract_variables() |
| **ThemeManager** | Theme management | load_theme(), apply_theme(), create_theme() |

---

## Getting Help

- **Wiki**: [https://github.com/fredporter/uDOS/wiki](https://github.com/fredporter/uDOS/wiki)
- **Issues**: [https://github.com/fredporter/uDOS/issues](https://github.com/fredporter/uDOS/issues)
- **Discussions**: [https://github.com/fredporter/uDOS/discussions](https://github.com/fredporter/uDOS/discussions)
- **Examples**: See `extensions/core/ok-assist/examples/`

---

**Version:** 1.4.0
**Last Updated:** November 25, 2025
**Maintainer:** Fred Porter
