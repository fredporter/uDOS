# Plugins UI Data Model

Contract for building the Plugins UI in Wizard (registry + discovery + lifecycle).

## Data Sources

- Registry (distribution catalog):
  - `GET /api/plugins/registry`
  - `GET /api/plugins/registry/{plugin_id}`
- Enhanced discovery (installed + git + containers):
  - `GET /api/plugins/catalog`
  - `GET /api/plugins/{plugin_id}`
- Catalog (enable/disable flags):
  - `GET /api/catalog/plugins`
  - `GET /api/catalog/plugins/{plugin_id}`
- Lifecycle actions:
  - `POST /api/plugins/{plugin_id}/install`
  - `POST /api/plugins/{plugin_id}/uninstall`
  - `POST /api/catalog/plugins/{plugin_id}/enable`
  - `POST /api/catalog/plugins/{plugin_id}/disable`

## Dashboard Aggregate

- `GET /api/plugins/dashboard`
  - Aggregated registry + catalog + discovery payload with summary counts.

## UI Model (per plugin)

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "plugin|container|transport|api|other",
  "tier": "core|library|extension|transport|api",
  "version": "string",
  "installed": false,
  "installed_version": "string|null",
  "enabled": false,
  "update_available": false,
  "license": "string",
  "author": "string",
  "homepage": "string",
  "documentation": "string",
  "source_path": "string",
  "config_path": "string|null",
  "installer_type": "git|apk|manual|container",
  "installer_script": "string|null",
  "package_file": "string|null",
  "dependencies": [],
  "health_check_url": "string|null",
  "running": false,
  "git": {
    "remote_url": "string|null",
    "branch": "string",
    "commit_hash": "string|null",
    "commit_date": "string|null",
    "tags": [],
    "is_dirty": false
  },
  "registry": {
    "registered": true,
    "manifest_type": "plugin|package|container|generic|missing",
    "validation_status": "validated|failed|skipped",
    "issues": [],
    "packages": [
      {
        "filename": "string",
        "path": "string",
        "size": 0
      }
    ]
  }
}
```

## Merge Rules

- Prefer `enhanced_plugin_discovery` for install state, git metadata, and container info.
- Prefer registry for manifest validation, packages, and catalog metadata when present.
- `enabled` comes from catalog or the registry entry (if mapped).
- `update_available` should reflect catalog + discovery data (if either marks true, show true).

## UI Sections

- Summary counters: total, installed, enabled, update_available
- Filters: category, tier, installer_type, installed, enabled, update_available
- Actions: install, uninstall, enable, disable, open repo, open docs
