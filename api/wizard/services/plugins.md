# Service: wizard.plugins

## Purpose
Manage plugin registry, distribution catalog, validation, and install lifecycle.

## Endpoints (current + target)

### Registry
- `GET /api/plugins/registry`
  - Query: `refresh` (bool), `include_manifests` (bool)
- `POST /api/plugins/registry/refresh`
  - Body: `{ "write_index": false }`
- `GET /api/plugins/registry/schema`
- `GET /api/plugins/registry/{plugin_id}`

### CLI Stub (migration placeholder)
- `POST /api/plugin/command`
  - Body: `{ "command": "list" }`

### Install/Enable/Disable
- `POST /api/plugins/{plugin_id}/install`
- `POST /api/plugins/{plugin_id}/uninstall`
- `POST /api/catalog/plugins/{plugin_id}/enable`
- `POST /api/catalog/plugins/{plugin_id}/disable`

## Response (example)

```json
{
  "success": true,
  "count": 12,
  "registry": {
    "plugin-id": {
      "id": "plugin-id",
      "version": "1.2.0",
      "description": "...",
      "installed": false
    }
  }
}
```

## MCP Tool Mapping

- `wizard.plugins.registry.list`
- `wizard.plugins.registry.get`
- `wizard.plugins.registry.refresh`
- `wizard.plugins.registry.schema`
- `wizard.plugin.command` (stub)
- `wizard.plugin.install`
- `wizard.plugin.uninstall`
- `wizard.plugin.enable`
- `wizard.plugin.disable`

## Notes

- Distribution artifacts live under `distribution/plugins`.
- CLI stub should be removed once Wizard plugin service is fully migrated.
