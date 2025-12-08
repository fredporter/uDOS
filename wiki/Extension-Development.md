# Extension Development Guide

**Last Updated:** December 1, 2025
**Version:** 2.0.0
**Status:** Complete

---

## Overview

The uDOS extension system provides a flexible architecture for adding new features, commands, services, and interfaces without modifying core system files. Extensions are self-contained modules that can be discovered, validated, and monitored automatically.

**Key Features:**
- Automatic discovery and registration
- JSON-based manifest validation
- Health monitoring and metrics
- Dependency checking
- Hot-reloading capability
- Command registry aggregation

---

## Extension Architecture

### Directory Structure

Extensions live in categorized directories under `extensions/`:

```
extensions/
├── core/           # Core system extensions (bundled with uDOS)
├── bundled/        # Pre-installed extensions
├── native/         # Platform-specific extensions
├── cloned/         # User-installed extensions
├── play/           # Gameplay and adventure extensions
├── web/            # Web interface extensions
├── cloud/          # Cloud service integrations
└── api/            # External API integrations
```

### Extension Anatomy

Each extension requires:

```
my-extension/
├── extension.json          # Manifest (required)
├── main.py                 # Entry point
├── README.md               # Documentation
├── commands/               # Command handlers (optional)
├── services/               # Background services (optional)
├── static/                 # Static assets (optional)
└── tests/                  # Unit tests (optional)
```

---

## Extension Manifest (extension.json)

### Required Schema

```json
{
  "id": "my-extension",
  "name": "My Extension",
  "version": "1.0.0",
  "type": "command",
  "category": "bundled",
  "description": "Brief description of what this extension does",
  "author": "Your Name",
  "license": "MIT",
  "status": "active"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier (lowercase, hyphens) |
| `name` | string | ✅ | Human-readable name |
| `version` | string | ✅ | Semantic version (X.Y.Z) |
| `type` | string | ✅ | Extension type (see below) |
| `category` | string | ✅ | Extension category (see below) |
| `description` | string | ✅ | Purpose and functionality |
| `author` | string | ✅ | Creator name or team |
| `license` | string | ✅ | License type (MIT, Apache, GPL, etc.) |
| `status` | string | ✅ | Current status (see below) |
| `main_file` | string | ❌ | Entry point (default: main.py) |
| `dependencies` | object | ❌ | Required dependencies |
| `provides_commands` | array | ❌ | Commands this extension adds |
| `provides_services` | array | ❌ | Services this extension provides |
| `endpoints` | array | ❌ | HTTP/WebSocket endpoints |
| `static_files` | array | ❌ | Static assets to serve |
| `configuration` | object | ❌ | Default configuration |

### Valid Types

- `service` - Background services
- `command` - Command handlers
- `interface` - UI components
- `integration` - External integrations
- `tool` - Utility tools

### Valid Categories

- `core` - Core system extensions
- `bundled` - Pre-installed extensions
- `native` - Platform-specific extensions
- `cloned` - User-installed extensions
- `play` - Gameplay extensions
- `web` - Web interface extensions
- `cloud` - Cloud service extensions
- `api` - API integrations

### Valid Statuses

- `active` - Fully operational
- `inactive` - Disabled
- `experimental` - Under development
- `deprecated` - Being phased out

---

## Extension Types

### Command Extensions

Add new commands to the uDOS command system.

```json
{
  "type": "command",
  "provides_commands": [
    {
      "name": "MYCOMMAND",
      "handler": "commands.my_handler",
      "description": "Execute my custom command",
      "syntax": "MYCOMMAND <arg1> [--option]"
    }
  ]
}
```

**Implementation:**

```python
# commands/my_handler.py
def handle_mycommand(args, config):
    """Handler for MYCOMMAND."""
    # Process command
    return {"status": "success", "output": "Command executed"}
```

### Service Extensions

Provide background services or utilities.

```json
{
  "type": "service",
  "provides_services": [
    {
      "name": "my_service",
      "class": "services.MyService",
      "description": "Background service for processing"
    }
  ]
}
```

**Implementation:**

```python
# services/my_service.py
class MyService:
    """Background service."""

    def __init__(self):
        self.running = False

    def start(self):
        """Start the service."""
        self.running = True

    def stop(self):
        """Stop the service."""
        self.running = False
```

### Interface Extensions

Add UI components or web interfaces.

```json
{
  "type": "interface",
  "category": "web",
  "endpoints": [
    {
      "path": "/dashboard",
      "handler": "dashboard_handler",
      "method": "GET",
      "description": "Main dashboard"
    }
  ],
  "static_files": [
    "dashboard.html",
    "dashboard.css",
    "dashboard.js"
  ]
}
```

### Integration Extensions

Connect to external APIs or services.

```json
{
  "type": "integration",
  "category": "cloud",
  "dependencies": {
    "api_keys": ["EXTERNAL_API_KEY"],
    "packages": ["requests>=2.28.0"]
  }
}
```

---

## Dependencies

### Core Dependencies

Specify required uDOS version:

```json
{
  "dependencies": {
    "core": ">=1.1.8"
  }
}
```

### Service Dependencies

Require specific services:

```json
{
  "dependencies": {
    "services": ["knowledge_manager", "asset_manager"]
  }
}
```

### API Key Dependencies

Specify required API keys:

```json
{
  "dependencies": {
    "api_keys": ["GEMINI_API_KEY", "OPENAI_API_KEY"]
  }
}
```

### Package Dependencies

Require Python packages:

```json
{
  "dependencies": {
    "packages": [
      "requests>=2.28.0",
      "pillow>=9.0.0"
    ]
  }
}
```

---

## Extension Manager

The `ExtensionManager` provides automatic discovery, validation, and health monitoring.

### Using ExtensionManager

```python
from core.services.extension_manager import get_extension_manager

# Get singleton instance
manager = get_extension_manager()

# Discover all extensions
count = manager.discover_extensions()
print(f"Found {count} extensions")

# List extensions
extensions = manager.list_extensions(category='core')
for ext in extensions:
    print(f"{ext.name} v{ext.version}")

# Get specific extension
ext = manager.get_extension('my-extension')
if ext:
    print(f"Main file: {ext.main_file}")
    print(f"Status: {ext.status}")

# Check health
health = manager.check_health()
print(f"Healthy: {health['healthy']}/{health['total']}")

# Get command registry
registry = manager.get_commands_registry()
for cmd_name, cmd_info in registry.items():
    print(f"{cmd_name}: {cmd_info['description']}")
```

### CLI Interface

```bash
# Discover extensions
python core/services/extension_manager.py discover

# List all extensions
python core/services/extension_manager.py list

# Check health
python core/services/extension_manager.py health

# Show command registry
python core/services/extension_manager.py commands
```

---

## Health Monitoring

Extensions are automatically monitored for health issues.

### Health Checks

1. **File Existence** - Main file and static files exist
2. **Dependencies** - Required packages installed
3. **API Keys** - Required environment variables set
4. **Extension Directory** - Valid directory structure

### Health Status

```python
from core.services.extension_manager import get_extension_manager

manager = get_extension_manager()

# Check specific extension
health_info = manager.health_monitor.check_extension(extension)

# Health score: X/Y checks passed
print(f"Health: {health_info['checks_passed']}/{health_info['total_checks']}")

# Check details
for check in health_info['checks']:
    status = "✅" if check['passed'] else "❌"
    print(f"{status} {check['name']}: {check['message']}")
```

### Health Report

```bash
$ python core/services/extension_manager.py health

🏥 Extension Health Report
============================================================
Total Extensions: 3
Healthy: 2 ✅
Unhealthy: 1 ❌

❌ SVG Diagram Generator (svg-generator)
   Category: core | Version: 1.0.0
   Status: Failed: api_gemini (3/4 passed)
   Commands: SVG

✅ Mission Control Dashboard (mission-control)
   Category: web | Version: 1.1.2
   Status: All checks passed (1/1)

✅ Cloud Access - POKE (cloud)
   Category: 2.0.0
   Status: All checks passed (2/2)
```

---

## Creating a New Extension

### Step 1: Create Directory

```bash
mkdir -p extensions/cloned/my-extension
cd extensions/cloned/my-extension
```

### Step 2: Create Manifest

```json
{
  "id": "my-extension",
  "name": "My Extension",
  "version": "1.0.0",
  "type": "command",
  "category": "cloned",
  "description": "My custom extension for uDOS",
  "author": "Your Name",
  "license": "MIT",
  "status": "active",
  "main_file": "main.py",
  "provides_commands": [
    {
      "name": "MYCOMMAND",
      "handler": "main.handle_command",
      "description": "Execute my custom command",
      "syntax": "MYCOMMAND <input>"
    }
  ]
}
```

### Step 3: Create Main File

```python
# main.py
"""My Extension - Custom functionality for uDOS."""

from core.config import Config

def handle_command(args, config):
    """Handle MYCOMMAND.

    Args:
        args: Command arguments
        config: Configuration instance

    Returns:
        dict: Command result
    """
    # Process command
    input_value = args.get('input')

    return {
        "status": "success",
        "output": f"Processed: {input_value}"
    }

def initialize(config):
    """Initialize extension.

    Called when extension is loaded.
    """
    print("My Extension initialized")

def cleanup():
    """Cleanup extension.

    Called when extension is unloaded.
    """
    print("My Extension cleanup")
```

### Step 4: Create README

```markdown
# My Extension

**Version:** 1.0.0
**Author:** Your Name
**License:** MIT

## Description

My custom extension for uDOS.

## Installation

Copy to `extensions/cloned/my-extension/`.

## Usage

```bash
MYCOMMAND <input>
```

## Commands

- `MYCOMMAND` - Execute custom command

## Configuration

No configuration required.

## Dependencies

None.
```

### Step 5: Validate Extension

```bash
python core/services/extension_manager.py discover
python core/services/extension_manager.py health
```

---

## Best Practices

### Naming Conventions

- **Extension ID**: Lowercase with hyphens (`my-extension`)
- **Command names**: UPPERCASE with hyphens (`MY-COMMAND`)
- **File names**: snake_case (`my_handler.py`)
- **Class names**: PascalCase (`MyService`)

### Version Management

Use semantic versioning (X.Y.Z):
- **Major (X)**: Breaking changes
- **Minor (Y)**: New features (backward compatible)
- **Patch (Z)**: Bug fixes

Example: `1.2.3` → Major 1, Minor 2, Patch 3

### Error Handling

Always handle errors gracefully:

```python
def handle_command(args, config):
    """Handle command with error handling."""
    try:
        result = process_input(args['input'])
        return {"status": "success", "output": result}
    except KeyError as e:
        return {"status": "error", "message": f"Missing argument: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
```

### Configuration

Use Config service for settings:

```python
from core.config import Config

config = Config()

# Get setting with default
api_key = config.get_env('MY_API_KEY', default='')
theme = config.get('my_extension.theme', default='dark')

# Set setting
config.set('my_extension.last_run', datetime.now().isoformat())
config.save()
```

### Logging

Use uDOS logger:

```python
from core.uDOS_logger import get_logger

logger = get_logger('my-extension')

logger.info("Extension initialized")
logger.warning("Deprecated feature used")
logger.error(f"Failed to process: {error}")
logger.debug(f"Processing {count} items")
```

### Testing

Create unit tests:

```python
# tests/test_my_extension.py
import pytest
from main import handle_command

def test_handle_command():
    """Test command handler."""
    args = {'input': 'test'}
    result = handle_command(args, None)

    assert result['status'] == 'success'
    assert 'test' in result['output']

def test_handle_command_error():
    """Test error handling."""
    args = {}  # Missing input
    result = handle_command(args, None)

    assert result['status'] == 'error'
    assert 'Missing argument' in result['message']
```

---

## Performance Metrics

Extensions automatically track performance:

```python
# Performance data collected
{
    "load_time_ms": 45,
    "total_invocations": 127,
    "avg_response_time_ms": 23.5,
    "error_count": 2,
    "last_error": "API timeout"
}
```

Access metrics:

```python
ext = manager.get_extension('my-extension')
print(f"Load time: {ext.performance['load_time_ms']}ms")
print(f"Invocations: {ext.performance['total_invocations']}")
```

---

## Common Patterns

### Command with Options

```python
def handle_command(args, config):
    """Handle command with options."""
    # Required argument
    input_value = args.get('input')
    if not input_value:
        return {"status": "error", "message": "Input required"}

    # Optional flag
    verbose = args.get('--verbose', False)

    # Optional value
    format_type = args.get('--format', 'json')

    # Process
    result = process(input_value, verbose=verbose, format=format_type)
    return {"status": "success", "output": result}
```

### Background Service

```python
import threading
import time

class MyBackgroundService:
    """Background service example."""

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start background service."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._worker)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop background service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _worker(self):
        """Background worker loop."""
        while self.running:
            # Do background work
            self._process_queue()
            time.sleep(1)

    def _process_queue(self):
        """Process items in queue."""
        # Implementation
        pass
```

### Web Interface

```python
from flask import render_template, jsonify

def register_routes(app):
    """Register web interface routes."""

    @app.route('/my-dashboard')
    def dashboard():
        """Render dashboard."""
        return render_template('dashboard.html')

    @app.route('/api/data')
    def get_data():
        """API endpoint for data."""
        data = fetch_data()
        return jsonify(data)
```

---

## Troubleshooting

### Extension Not Discovered

**Check:**
1. `extension.json` exists and is valid JSON
2. Extension is in a scanned directory (`extensions/*/`)
3. Run discovery: `python core/services/extension_manager.py discover`

### Validation Errors

**Common issues:**
- Missing required fields (`id`, `name`, `version`, etc.)
- Invalid `type` or `category` value
- Invalid version format (must be X.Y.Z)
- Invalid JSON syntax

**Fix:**
```bash
# Validate JSON syntax
python -m json.tool extension.json

# Check validation errors
python core/services/extension_manager.py discover
```

### Health Check Failures

**Common causes:**
- Main file missing or path incorrect
- Required API keys not set in environment
- Dependencies not installed
- Extension directory structure invalid

**Fix:**
```bash
# Check health details
python core/services/extension_manager.py health

# Set required API keys
export REQUIRED_API_KEY="your-key-here"

# Install dependencies
pip install -r requirements.txt
```

### Command Not Registered

**Check:**
1. Command listed in `provides_commands`
2. Handler path correct (`module.function`)
3. Extension discovered and active
4. Command registry rebuilt: `manager.get_commands_registry()`

---

## Example Extensions

### Minimal Extension

```json
{
  "id": "hello-world",
  "name": "Hello World",
  "version": "1.0.0",
  "type": "command",
  "category": "cloned",
  "description": "Simple hello world extension",
  "author": "Example",
  "license": "MIT",
  "status": "active"
}
```

```python
# main.py
def initialize(config):
    """Initialize extension."""
    print("Hello World extension loaded!")
```

### Command Extension

See `extensions/core/svg-generator/` for complete example.

### Service Extension

See `extensions/core/server/` for complete example.

### Web Interface Extension

See `extensions/core/mission-control/` for complete example.

---

## API Reference

### ExtensionManager

```python
class ExtensionManager:
    """Central extension management."""

    def discover_extensions(self) -> int:
        """Discover and load all extensions.

        Returns:
            Number of extensions discovered
        """

    def list_extensions(
        self,
        category: str = None,
        status: str = None
    ) -> List[ExtensionMetadata]:
        """List extensions with optional filters.

        Args:
            category: Filter by category
            status: Filter by status

        Returns:
            List of extension metadata
        """

    def get_extension(self, extension_id: str) -> ExtensionMetadata:
        """Get extension by ID.

        Args:
            extension_id: Extension identifier

        Returns:
            Extension metadata or None
        """

    def check_health(self) -> dict:
        """Check health of all extensions.

        Returns:
            Health summary dict
        """

    def get_health_report(self) -> str:
        """Get formatted health report.

        Returns:
            Formatted health report string
        """

    def get_commands_registry(self) -> dict:
        """Get aggregated command registry.

        Returns:
            Dict mapping command names to info
        """
```

### ExtensionValidator

```python
class ExtensionValidator:
    """Validate extension manifests."""

    def validate(self, manifest: dict, extension_path: Path) -> bool:
        """Validate extension manifest.

        Args:
            manifest: Extension manifest dict
            extension_path: Path to extension directory

        Returns:
            True if valid, False otherwise
        """
```

### ExtensionHealthMonitor

```python
class ExtensionHealthMonitor:
    """Monitor extension health."""

    def check_extension(
        self,
        extension: ExtensionMetadata
    ) -> dict:
        """Perform health checks on extension.

        Args:
            extension: Extension metadata

        Returns:
            Health check results dict
        """
```

---

## Resources

- **Extension Manager**: `core/services/extension_manager.py`
- **Example Extensions**: `extensions/core/`
- **Test Suite**: `sandbox/tests/test_extension_manager.py`
- **Development Guide**: `wiki/Developers-Guide.md`

---

## Next Steps

1. Review example extensions in `extensions/core/`
2. Create your first extension following this guide
3. Test with `extension_manager.py discover` and `health`
4. Submit to community repository (if public)
5. Share with other uDOS users

**Questions?** See `wiki/Developers-Guide.md` or file an issue.
