# Plugin Architecture v1.0

**Version:** 1.0  
**Status:** Specification  
**Date:** 2026-01-14  
**Scope:** uDOS Plugin System (formerly "Extensions")

---

## Overview

A **Plugin** in uDOS is a modular, discoverable, installable feature that extends uDOS capabilities. Plugins can be:

- **User-facing:** Available to uCode Markdown App users (e.g., API plugin)
- **Wizard-only:** Dev Mode features for developers (e.g., experimental Groovebox)

All plugins follow the same structure and lifecycle.

---

## Plugin Structure

```
plugins/
├── api/
│   ├── __init__.py
│   ├── version.json
│   ├── manifest.json
│   ├── requirements.txt
│   ├── README.md
│   ├── server.py
│   ├── routes/
│   ├── services/
│   ├── tests/
│   └── .archive/
│
└── transport/
    ├── __init__.py
    ├── version.json
    ├── manifest.json
    ├── requirements.txt
    ├── README.md
    ├── __init__.py (exports)
    ├── policy.yaml
    ├── validator.py
    ├── audio/
    ├── meshcore/
    ├── qr/
    ├── tests/
    └── .archive/
```

---

## Required Files

### 1. `version.json` (Required)

```json
{
  "name": "api",
  "version": "1.1.0.0",
  "component": "api",
  "type": "plugin",
  "stability": "stable",
  "api_version": "1.0",
  "release_date": "2026-01-10",
  "changelog": "Modular server with websocket support"
}
```

**Fields:**
- `name` — Plugin ID (lowercase, no spaces)
- `version` — Semantic version (major.minor.patch.build)
- `component` — Same as plugin folder name
- `type` — Always "plugin"
- `stability` — "stable" | "beta" | "alpha"
- `api_version` — Plugin API compatibility (for consumers)
- `release_date` — ISO 8601
- `changelog` — Brief summary of latest changes

### 2. `manifest.json` (Recommended)

```json
{
  "name": "api",
  "title": "REST/WebSocket API",
  "description": "HTTP/WebSocket server for uDOS",
  "author": "uDOS Team",
  "license": "MIT",
  "repository": "https://github.com/uDOS/uDOS/tree/main/plugins/api",
  
  "scope": "user-facing",
  "realm": "either",
  
  "requirements": {
    "python": ">=3.8",
    "packages": ["flask", "python-socketio"]
  },
  
  "dependencies": {
    "core": ">=1.0.0",
    "transport": ">=1.0.0"
  },
  
  "ports": [8765],
  "environment": {
    "UDOS_API_PORT": "8765",
    "UDOS_API_HOST": "127.0.0.1"
  },
  
  "commands": ["API"],
  "entry_point": "server.py:create_app()"
}
```

**Fields:**
- `scope` — "user-facing" (ships with v1) or "wizard-only" (dev mode)
- `realm` — "user-device" | "wizard" | "either"
- `requirements` — Python version + pip packages
- `dependencies` — Other plugins required
- `ports` — Network ports used
- `environment` — Environment variables
- `commands` — TUI commands this plugin implements
- `entry_point` — How to start/initialize plugin

### 3. `README.md` (Required)

```markdown
# API Plugin

Brief description.

## Quick Start

Installation, basic usage, configuration.

## Commands

List of TUI commands (if any).

## Configuration

Environment variables, config files.

## API Reference

Endpoints, WebSocket schema.

## Troubleshooting

Common issues and solutions.

## Contributing

How to modify this plugin.
```

### 4. `requirements.txt` (If Python)

Standard pip format.

---

## Plugin Lifecycle

### Discovery

Wizard scans `/plugins/` and loads `version.json` + `manifest.json`:

```python
# wizard/plugin_manager/catalog.py
catalog.discover_plugins()  # Returns list of (name, version, manifest)
```

### Installation

For user-facing plugins, Wizard enables them:

```bash
PLUGIN INSTALL api@1.1.0  # From GitHub releases
PLUGIN ENABLE api          # Activate in /plugins/api
```

For experimental plugins (e.g., Groovebox), move from `.archive/`:

```bash
PLUGIN ENABLE groovebox    # Move from .archive/groovebox → /plugins/groovebox
```

### Activation

Plugin is loaded into uDOS runtime:
- Core imports plugin services
- API server starts plugin routes
- Commands registered

### Updates

Wizard pulls from GitHub and bumps version:

```bash
PLUGIN UPDATE api          # Pulls latest release
PLUGIN UPDATE api@1.2.0    # Pin to specific version
```

### Deprecation

Move to `.archive/` but keep `version.json`:

```bash
PLUGIN DISABLE groovebox   # Move to .archive/, keep metadata
```

---

## Plugin Types

### Type 1: Service Plugin (e.g., API)

Provides a service or API surface.

```python
# plugins/api/server.py
class APIServer:
    def start(host, port)
    def stop()
    def register_route(path, handler)
```

**Manifest fields:**
```json
{
  "type_specific": {
    "service_type": "http",
    "port": 8765
  }
}
```

### Type 2: Transport Plugin (e.g., Transport)

Adds a communication protocol.

```python
# plugins/transport/__init__.py
class MeshCoreTransport:
    def send(destination, payload)
    def receive(timeout=None)
    def validate_message(msg)
```

**Manifest fields:**
```json
{
  "type_specific": {
    "transport_type": "mesh",
    "protocols": ["meshcore", "qr", "audio"]
  }
}
```

### Type 3: Extension Plugin (e.g., Groovebox)

Adds features or commands to Core.

```python
# plugins/groovebox/groovebox.py
class GrooveboxExtension:
    def handle_command(cmd, params)
    def initialize()
```

**Manifest fields:**
```json
{
  "type_specific": {
    "extension_type": "command",
    "commands": ["GROOVE", "PLAY", "RECORD"]
  }
}
```

---

## Plugin Development

### Scaffold a New Plugin

```bash
mkdir -p plugins/my-plugin
cd plugins/my-plugin

cat > version.json <<EOF
{
  "name": "my-plugin",
  "version": "1.0.0.0",
  "component": "my-plugin",
  "type": "plugin"
}
EOF

cat > manifest.json <<EOF
{
  "name": "my-plugin",
  "title": "My Plugin",
  "scope": "user-facing",
  "realm": "either"
}
EOF

cat > README.md <<EOF
# My Plugin

Description here.
EOF

touch requirements.txt __init__.py
```

### Test Plugin

```bash
cd /path/to/uDOS

# Check manifest
python -m wizard.plugin_manager.validator plugins/my-plugin

# Run tests
pytest plugins/my-plugin/tests/ -v

# Load in TUI (if command-based)
./start_udos.sh
# Type: MY-COMMAND arg1 arg2
```

### Version Bump

Use the version manager:

```bash
python -m core.version bump plugins/my-plugin patch
# Updates version.json automatically
```

### Publish Release

Wizard can publish to GitHub:

```bash
# In GitHub: create a release with tag v1.1.0
# Wizard detects it:
PLUGIN UPDATE my-plugin
```

---

## Plugin Dependencies

### Declaring Dependencies

```json
{
  "dependencies": {
    "core": ">=1.0.0",
    "transport": ">=1.0.0"
  }
}
```

### Version Ranges

- `"1.0.0"` — Exact version
- `">1.0.0"` — Greater than
- `">=1.0.0"` — Greater than or equal
- `"1.x"` or `"1.0.x"` — Wildcard ranges

### Dependency Resolution

Wizard checks at load time:

```python
# wizard/plugin_manager/dependency_resolver.py
resolver.validate_dependencies(plugin_manifest)
# Raises PluginDependencyError if unsatisfiable
```

---

## Configuration

### Environment Variables

Plugins can declare environment variables in `manifest.json`:

```json
{
  "environment": {
    "UDOS_API_PORT": "8765",
    "UDOS_API_HOST": "127.0.0.1"
  }
}
```

Users override:

```bash
export UDOS_API_PORT=9000
./start_udos.sh
```

### Config Files

Optional `config/` folder in plugin:

```
plugins/api/
├── config/
│   ├── default.yaml
│   └── production.yaml
└── config_loader.py
```

```python
# plugins/api/config_loader.py
class ConfigLoader:
    def load(env="default")
    def get(key, default=None)
```

---

## Testing

### Unit Tests

```python
# plugins/api/tests/test_routes.py
import pytest
from plugins.api.server import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_health_endpoint(app):
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
```

### Integration Tests

```python
# plugins/api/tests/test_integration.py
def test_api_with_core():
    from core.services import ConfigService
    from plugins.api.server import create_app
    
    config = ConfigService()
    app = create_app(config)
    
    # Test full workflow
    assert app is not None
```

### Run Tests

```bash
# All plugins
pytest plugins/*/tests/ -v

# Single plugin
pytest plugins/api/tests/ -v

# With coverage
pytest plugins/*/tests/ --cov=plugins --cov-report=html
```

---

## Security

### Sandbox Rules

- Plugins can only access `/plugins/my-plugin/` directory
- Network access limited to declared ports
- File system access restricted (no `/memory/` or `/wizard/` unless explicit)
- No subprocess execution without User approval

### Policy Enforcement

Transport plugin validates all messages:

```python
# plugins/transport/validator.py
def validate_message(msg, source_transport):
    if source_transport == "bluetooth-public":
        # No uDOS data allowed
        raise PolicyViolation("BT Public can only carry signals")
```

---

## Distribution

### For v1 (Shipped with App)

Plugin is included in:
- Tauri app bundle
- TCZ distribution
- ISO image

No download required.

### For v1.1+ (Plugin Marketplace)

Wizard can fetch from GitHub:

```bash
PLUGIN SEARCH music           # Query marketplace
PLUGIN INSTALL groovebox      # Download + enable
```

---

## Checklist for New Plugin

- [ ] Folder created in `/plugins/`
- [ ] `version.json` with all required fields
- [ ] `manifest.json` with metadata + dependencies
- [ ] `README.md` with quick start + examples
- [ ] `requirements.txt` (if Python)
- [ ] `__init__.py` with exports
- [ ] `tests/` folder with unit tests
- [ ] Entry point documented in manifest
- [ ] Commands (if any) registered in Core
- [ ] Passes `wizard.plugin_manager.validator`
- [ ] All tests pass (`pytest`)
- [ ] Documentation complete

---

## References

- [ADR-0012: Library & Plugins Reorganization](../decisions/ADR-0012-library-plugins-reorganization.md)
- [Wizard GitHub Integration](wizard-github-integration.md)
- [Transport Policy](../../extensions/README.md) (to be migrated to plugins/)
- [API Plugin README](../../plugins/api/README.md)

---

*Last Updated: 2026-01-14*  
*Version: 1.0 Specification*
