# Wizard Enhanced Plugin System Documentation

**Date:** 2026-02-01  
**Version:** 1.0.0  
**Status:** Complete & Ready for Integration

---

## Overview

The **Enhanced Plugin System** provides comprehensive plugin discovery, management, and installation directly from the Wizard Server GUI. It discovers and manages:

- **Distribution Plugins** (`distribution/plugins/`) — Packaged and indexed plugins
- **Library Containers** (`library/`) — Containerized services (home-assistant, songscribe)
- **Extensions** (`extensions/transport/`, `extensions/api/`) — API and transport integrations

Each plugin includes full **git/version control** metadata, **installer pathways**, and **update management**.

---

## Architecture

### Components

```
Wizard Server (FastAPI)
├── Services
│   ├── enhanced_plugin_discovery.py    ← Discovery engine with git metadata
│   ├── plugin_repository.py             ← Legacy (still used for index.json)
│   └── library_manager_service.py       ← Container management
│
├── Routes
│   ├── enhanced_plugin_routes.py        ← Plugin API endpoints
│   └── container_launcher_routes.py     ← Container lifecycle
│
└── Dashboard
    ├── src/routes/Plugins.svelte        ← Enhanced UI (grid/list/tiers/categories)
    ├── src/routes/Catalog.svelte        ← Legacy catalog (compatibility)
    └── src/components/WizardTopBar.svelte ← Navigation
```

### Discovery Process

```
EnhancedPluginDiscovery.discover_all()
├── Scan distribution/plugins/ → Read index.json + manifests
├── Scan library/ → Read container.json files  
├── Scan extensions/transport/ → Read version.json
├── Scan extensions/api/ → Read version.json
└── For each plugin/container/extension:
    ├── Extract metadata (name, version, description, license)
    ├── Get git info (remote URL, branch, commit, status)
    ├── Determine installer type (git | apk | container | script)
    └── Return PluginMetadata object
```

---

## Configuration

### .env Setup

Add `UDOS_ROOT` to your `.env` file for git operations:

```dotenv
# ============================================================================
# SYSTEM PATHS (Required for Wizard Git Operations)
# ============================================================================
UDOS_ROOT="/Users/fredbook/Code/uDOS"
```

The system will:
- Use `UDOS_ROOT` from `.env` if available
- Fall back to `get_repo_root()` (uDOS installation directory)
- Expand `~` and environment variables in paths

### Example .env

```dotenv
# System paths
UDOS_ROOT="/Users/fredbook/Code/uDOS"

# User identity
USER_NAME="Fred"
USER_DOB="1980-01-01"
USER_ROLE="admin"

# Wizard server
WIZARD_KEY="uLqKKwMn6fapD7RZGEB_s5hYlGixBX_nAHxA-yrux-I"
WIZARD_ADMIN_TOKEN="c7JUX_TQ0h8K436JGYLK1dAw7adZCNEZmHK9jLPqLk"
```

---

## API Endpoints

All endpoints require `Authorization: Bearer <ADMIN_TOKEN>` header (except public stats).

### Plugin Discovery

#### Get Complete Catalog
```bash
GET /api/v1/plugins/catalog

Response:
{
  "success": true,
  "timestamp": "2026-02-01T16:30:00Z",
  "total": 42,
  "plugins": {
    "meshcore": { ... },
    "home-assistant": { ... },
    "songscribe": { ... },
    ...
  }
}
```

#### Get Plugins by Tier
```bash
GET /api/v1/plugins/tiers

Response:
{
  "success": true,
  "tiers": {
    "core": [ { id: "meshcore", ... } ],
    "library": [ { id: "home-assistant", ... } ],
    "extension": [ { id: "meshcore-transport", ... } ],
    ...
  }
}
```

#### Get Plugins by Category
```bash
GET /api/v1/plugins/categories

Response:
{
  "success": true,
  "categories": {
    "container": [ { id: "home-assistant", ... } ],
    "transport": [ { id: "meshcore-transport", ... } ],
    "api": [ { id: "server-modular", ... } ],
    ...
  }
}
```

#### Search Plugins
```bash
GET /api/v1/plugins/search?q=home

Response:
{
  "success": true,
  "query": "home",
  "found": 2,
  "plugins": [
    { id: "home-assistant", name: "Home Assistant", ... },
    { id: "home_automation_kit", ... }
  ]
}
```

### Plugin Details

#### Get Plugin Details
```bash
GET /api/v1/plugins/{plugin_id}

Response:
{
  "success": true,
  "plugin": {
    "id": "songscribe",
    "name": "Songscribe",
    "description": "Music transcription...",
    "version": "1.2.1",
    "tier": "library",
    "category": "container",
    "installed": true,
    "installer_type": "container",
    "git": {
      "remote_url": "https://github.com/gabe-serna/songscribe",
      "branch": "main",
      "commit_hash": "a1b2c3d4",
      "commit_date": "2026-01-31T12:00:00Z",
      "is_dirty": false
    },
    "dependencies": ["python3.11+", "node.js 18+"],
    ...
  }
}
```

### Git Operations

#### Get Git Status
```bash
GET /api/v1/plugins/{plugin_id}/git/status

Response:
{
  "success": true,
  "plugin_id": "meshcore",
  "git": {
    "remote_url": "https://github.com/meshcore-dev/MeshCore",
    "branch": "main",
    "commit_hash": "abc12345",
    "commit_date": "2026-01-25T10:30:00Z",
    "is_dirty": true
  }
}
```

#### Pull Updates from Git
```bash
POST /api/v1/plugins/{plugin_id}/git/pull

Response:
{
  "success": true,
  "plugin_id": "meshcore",
  "status": "updating",
  "message": "Pulling latest changes for meshcore..."
}
```

#### Clone from Git
```bash
POST /api/v1/plugins/{plugin_id}/git/clone
Body:
{
  "git_url": "https://github.com/owner/repo.git"
}

Response:
{
  "success": true,
  "plugin_id": "my_extension",
  "status": "cloning",
  "target_path": "/Users/fredbook/Code/uDOS/extensions/my_extension"
}
```

### Installation

#### Install/Update Plugin
```bash
POST /api/v1/plugins/{plugin_id}/install

Response:
{
  "success": true,
  "plugin_id": "meshcore",
  "status": "updating"  # or "installing"
}
```

Behavior:
- **Git-based** → Clone if not exists, pull if already cloned
- **Container** → Redirect to `/api/v1/containers/{id}/launch`
- **APK** → Run installer script from `wizard/tools/{id}_setup.py`
- **Custom script** → Execute installer from plugin manifest

---

## Plugin Metadata Format

### Complete Plugin Object

```python
@dataclass
class PluginMetadata:
    # Identity
    id: str                          # Unique identifier
    name: str                        # Display name
    description: str                 # Short description
    category: str                    # container|transport|api|editor|etc
    tier: str                        # core|library|extension
    
    # Versioning
    version: str                     # Semantic version
    installed: bool                  # Currently installed?
    installed_version: str           # Version on disk
    update_available: bool           # Update pending?
    
    # Metadata
    license: str                     # MIT|Apache-2.0|etc
    author: str                      # Creator/maintainer
    homepage: str                    # Project URL
    documentation: str               # Docs URL
    
    # Paths
    source_path: str                 # Relative to UDOS_ROOT
    config_path: str                 # Config file path
    
    # Git Info
    git: GitMetadata                 # {remote_url, branch, commit_hash, ...}
    
    # Installation
    installer_type: str              # git|apk|manual|container|script
    installer_script: str            # Path to setup script
    package_file: str                # Path to package
    
    # Dependencies
    dependencies: List[str]          # Required packages
    
    # Status
    available: bool                  # Can be installed?
    health_check_url: str            # For container services
    running: bool                    # Currently running?
```

### Git Metadata

```python
@dataclass
class GitMetadata:
    remote_url: str          # Repository URL
    branch: str              # Current branch (default: "main")
    commit_hash: str         # Short commit hash
    commit_date: str         # Last commit timestamp
    tags: List[str]          # Git tags
    is_dirty: bool           # Has uncommitted changes?
```

---

## UI Features

### Plugins Page (`/plugins` route)

#### Grid View
- 3-column responsive grid
- Plugin cards with:
  - Name, ID, version badge
  - Tier indicator (📦 Core, 📚 Library, 🔌 Extension)
  - Category badge + install status
  - Git info (remote, commit, dirty status)
  - Install/Update/Details buttons
  - Click card to see full details

#### List View
- Single-column list with horizontal cards
- More compact than grid
- Same info, optimized for scrolling

#### Tier View
- Organized by tier (Core → Library → Extension)
- See plugin distribution across tiers
- Useful for understanding system architecture

#### Category View
- Organized by category (Container → Transport → API)
- Group related functionality together

### Search & Filtering
- Full-text search (name, description, ID)
- Filter by tier/category
- Real-time results

### Details Modal
- Full plugin information
- Git status and history
- Dependencies list
- Links to homepage/docs
- Install/Update buttons
- Git branch info + commit hash

---

## Installation Types

### 1. Git-Based (`installer_type: "git"`)

**Process:**
1. Check if `source_path` exists locally
2. If not → `git clone <remote_url> <target_path>`
3. If exists → `git pull origin <branch>`

**Example:**
```bash
# First install (clones)
POST /api/v1/plugins/meshcore/install
→ git clone https://github.com/meshcore-dev/MeshCore \
           /Users/.../uDOS/extensions/meshcore

# Update (pulls)
POST /api/v1/plugins/meshcore/install
→ git pull origin main
```

**Plugins:** meshcore, custom extensions, etc.

### 2. Container (`installer_type: "container"`)

**Process:**
1. Validate container is in `library/`
2. Read `container.json` for launch config
3. Redirect to `/api/v1/containers/{id}/launch`
4. Container launcher handles startup

**Example:**
```bash
POST /api/v1/plugins/home-assistant/install
→ Redirect to: /api/v1/containers/home-assistant/launch
→ Service starts on localhost:8123
```

**Plugins:** home-assistant, songscribe, etc.

### 3. Script-Based (`installer_script: "wizard/tools/{id}_setup.py"`)

**Process:**
1. Validate script exists
2. Run: `python wizard/tools/{id}_setup.py`
3. Script handles all setup

**Example:**
```bash
POST /api/v1/plugins/devstral/install
→ python wizard/tools/devstral_setup.py
```

### 4. APK Package (`installer_type: "apk"`)

**Process:**
1. Use `plugin_factory.py` to build APK
2. Execute APK installer
3. Install into Alpine Linux environment

---

## Plugin Discovery Examples

### Example 1: Container Plugin (home-assistant)

**Source:** `/library/home-assistant/container.json`

```json
{
  "id": "home-assistant",
  "name": "Home Assistant",
  "tier": "library",
  "category": "container",
  "installer_type": "container",
  "source_path": "library/home-assistant"
}
```

**Discovery:**
1. Scans `library/` directory
2. Finds `home-assistant/container.json`
3. Extracts metadata
4. Gets git info (if `.git/` exists)
5. Sets `installer_type: "container"`

**API Response:**
```json
{
  "id": "home-assistant",
  "name": "Home Assistant",
  "tier": "library",
  "category": "container",
  "installer_type": "container",
  "git": {
    "remote_url": "https://github.com/home-assistant/core",
    "branch": "master",
    "commit_hash": "xyz789",
    "is_dirty": false
  }
}
```

### Example 2: Extension Plugin (meshcore-transport)

**Source:** `/extensions/transport/meshcore/version.json`

```json
{
  "version": "1.0.0",
  "description": "P2P mesh networking transport"
}
```

**Discovery:**
1. Scans `extensions/transport/`
2. Finds `meshcore/version.json`
3. Reads metadata
4. Gets git info (from parent git repo)
5. Sets `installer_type: "git"` (already installed)

**API Response:**
```json
{
  "id": "meshcore",
  "name": "Meshcore",
  "tier": "extension",
  "category": "transport",
  "installed": true,
  "installer_type": "git",
  "git": {
    "remote_url": "https://github.com/meshcore-dev/MeshCore",
    "branch": "main",
    "commit_hash": "abc1234"
  }
}
```

### Example 3: Distribution Plugin (typo-editor)

**Source:** `/distribution/plugins/index.json`

```json
{
  "plugins": {
    "typo": {
      "id": "typo",
      "name": "Typo Markdown Editor",
      "version": "1.0.0",
      "category": "editor",
      "installed": true
    }
  }
}
```

**Discovery:**
1. Scans `distribution/plugins/`
2. Reads `index.json`
3. Extracts plugin entries
4. Attempts to get git info
5. Sets based on manifest

---

## Integration with uCODE

Users can install plugins directly from uDOS TUI:

```ucode
PLUGIN LIST              # Show all plugins
PLUGIN INSTALL meshcore  # Install from catalog
PLUGIN UPDATE meshcore   # Update existing plugin
PLUGIN REMOVE meshcore   # Uninstall plugin
```

Implementation in `core/tui/ucode.py`:
```python
def _cmd_plugin(self, args: str) -> None:
    """Plugin/extension management."""
    action = args.split()[0] if args else "list"
    
    if action == "list":
        self._plugin_list()  # Call Wizard API
    elif action == "install":
        self._plugin_install(args.split()[1])
    # ...
```

---

## File Structure

```
uDOS/
├── .env                                    # UDOS_ROOT path + identity
├── wizard/
│   ├── services/
│   │   ├── enhanced_plugin_discovery.py    ← Discovery engine (NEW)
│   │   ├── plugin_repository.py            ← Legacy index support
│   │   └── library_manager_service.py
│   │
│   ├── routes/
│   │   ├── enhanced_plugin_routes.py       ← API endpoints (NEW)
│   │   ├── catalog_routes.py               ← Legacy catalog
│   │   └── container_launcher_routes.py
│   │
│   ├── dashboard/src/
│   │   ├── routes/
│   │   │   ├── Plugins.svelte              ← Enhanced UI (NEW)
│   │   │   └── Catalog.svelte              ← Legacy (kept for compat)
│   │   ├── components/
│   │   │   └── WizardTopBar.svelte         ← Updated with Plugins link
│   │   └── App.svelte                      ← Route registration
│   │
│   └── server.py                           ← Route registration (updated)
│
├── library/                                # Container sources
│   ├── home-assistant/container.json
│   ├── songscribe/container.json
│   └── ...
│
├── distribution/plugins/
│   ├── index.json                          # Legacy index
│   ├── home-assistant/manifest.json        ← Plugin metadata
│   ├── songscribe/manifest.json
│   └── ...
│
└── extensions/
    ├── transport/meshcore/version.json
    ├── api/server_modular/version.json
    └── ...
```

---

## Testing

### Manual Testing Checklist

- [ ] Wizard server starts without errors
- [ ] `/api/v1/plugins/catalog` returns all plugins
- [ ] `/api/v1/plugins/tiers` shows correct tier grouping
- [ ] `/api/v1/plugins/categories` shows correct category grouping
- [ ] `/api/v1/plugins/search?q=home` finds home-assistant
- [ ] `/api/v1/plugins/meshcore` shows git metadata
- [ ] Plugins page loads in Wizard Dashboard
- [ ] Grid/List/Tiers/Categories views work
- [ ] Install button triggers git clone/pull
- [ ] Update button pulls latest changes
- [ ] Details modal shows full information
- [ ] Search works in real-time

### Integration Testing

```bash
# Test discovery
curl http://localhost:8765/api/v1/plugins/catalog \
  -H "Authorization: Bearer <ADMIN_TOKEN>" | jq .

# Test git status
curl http://localhost:8765/api/v1/plugins/meshcore/git/status

# Test update
curl -X POST http://localhost:8765/api/v1/plugins/meshcore/git/pull \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## Troubleshooting

### Plugin Not Discovered

1. **Check path:** Is plugin in correct location?
   - Distribution: `distribution/plugins/{id}/`
   - Library: `library/{id}/`
   - Extensions: `extensions/{type}/{id}/`

2. **Check metadata file:**
   - Distribution: `index.json` entry exists?
   - Library: `container.json` exists?
   - Extensions: `version.json` exists?

3. **Check .gitmodules:** For submodules, ensure entry exists

### Git Operations Failing

1. **Check `UDOS_ROOT`:**
   ```bash
   echo $UDOS_ROOT  # Should be set in .env
   ```

2. **Check git access:**
   ```bash
   git ls-remote <remote_url>  # Verify remote is accessible
   ```

3. **Check permissions:**
   ```bash
   ls -la plugins/directory  # Verify write access
   ```

### Duplicate Plugins in Results

- Discovery might find plugins in both `distribution/plugins/` and `extensions/`
- Results are deduplicated by ID
- Check that plugin entries don't conflict

---

## Future Enhancements

1. **Version Pinning** — Lock to specific git tags/branches
2. **Dependency Resolution** — Auto-install dependencies
3. **Plugin Validation** — Schema validation for manifests
4. **Update Notifications** — Alert when updates available
5. **Rollback Support** — Git tags for version history
6. **Plugin Marketplace** — Public registry discovery
7. **Containerized Installation** — Isolate deps in containers
8. **Plugin Signing** — GPG signatures for security

---

**Documentation Version:** 1.0.0  
**Last Updated:** 2026-02-01  
**Author:** GitHub Copilot
