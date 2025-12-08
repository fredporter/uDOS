# uDOS Unified API Server

Consolidated REST API and web servers for all uDOS extensions.

## Structure

- `server.py` - Main Flask API server (consolidated from teletext/markdown)
- `manager.py` - Server lifecycle management
- `routes/` - API endpoint definitions
  - `commands.py` - Command execution endpoints
  - `knowledge.py` - Knowledge/markdown browsing
  - `system.py` - System status and health
- `static/` - Shared web assets
- `templates/` - Shared HTML templates

## Ports

- **5001** - Main API server (command execution, WebSocket)
- **9000** - Knowledge viewer (markdown rendering)

## Previous Locations (Archived)

- `extensions/core/teletext/api_server.py` → Consolidated into server.py
- `extensions/core/markdown/server.py` → Merged into server.py
- Core functionality preserved, duplicates removed
