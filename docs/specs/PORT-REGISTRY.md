# uDOS Server Port Registry

**Status:** 📘 CURRENT DOCUMENTATION  
**Version**: 1.1.15  
**Last Updated**: December 2, 2025

## Overview

This document provides the authoritative registry of all server ports used by uDOS core and extensions. All ports are bound to `127.0.0.1` (localhost) for security.

## Core Servers

Managed via `extensions/server_manager.py`:

| Port | Service | Location | Health Endpoint | Description |
|------|---------|----------|-----------------|-------------|
| **5001** | API Server | `extensions/api/server.py` | `/api/health` | REST API for all uDOS commands |
| **8888** | System Dashboard | `extensions/core/dashboard/` | `/health` | Advanced system monitoring (NES.css) |
| **8889** | Retro Terminal | `extensions/core/terminal/` | `/health` | PetMe font terminal interface |
| **8892** | Retro Desktop | `extensions/core/desktop/` | `/health` | System 7 desktop environment |
| **9002** | Teletext Display | `extensions/core/teletext/` | `/health` | BBC Teletext with WebSocket |

## Extension Servers

Additional services not in server_manager.py:

| Port | Service | Location | Type | Description |
|------|---------|----------|------|-------------|
| **5000** | Mission Control | `extensions/core/mission/` | Embedded | Real-time mission tracking |
| **5555** | Graphics Renderer | `extensions/core/graphics-renderer/` | Node.js | 5-format graphics rendering (v1.2.15) |
| **8080** | Map Server | `extensions/play/commands/map_handler.py` | Dynamic | Planet map visualization |

## Port Allocation Rules

### Reserved Ranges

- **5000-5099**: Extension-specific servers (mission, etc.)
- **8800-8899**: Core web extensions (dashboard, terminal, desktop)
- **9000-9099**: Display extensions (teletext, etc.)

### Allocation Guidelines

1. **Core servers** (managed via server_manager.py): Use 8800-8899 range
2. **Extension servers** (standalone): Use 5000-5099 range
3. **API servers**: Use 5001 (primary) or 5000-5099 (alternates)
4. **Display servers**: Use 9000-9099 range

### Conflict Resolution

If a port is already in use:

1. **server_manager.py** will auto-cleanup via port_manager
2. Manual cleanup: `python extensions/server_manager.py cleanup <server>`
3. Check conflicts: `lsof -i :<port>`
4. Health check: `curl http://localhost:<port>/health`

## Server Management

### Quick Commands

```bash
# Check all server status
python extensions/server_manager.py status

# Start specific server
python extensions/server_manager.py start terminal

# Start all servers
python extensions/server_manager.py start-all

# Cleanup specific server
python extensions/server_manager.py cleanup dashboard

# Restart server
python extensions/server_manager.py restart api

# Health check
python extensions/server_manager.py health teletext
```

### Manual Server Control

```bash
# API Server (5001)
PORT=5001 python extensions/api/server.py

# Extensions Server (8888, 8889, 8892, 9002)
python extensions/core/extensions_server.py dashboard  # 8888
python extensions/core/extensions_server.py terminal   # 8889
python extensions/core/extensions_server.py desktop    # 8892
python extensions/core/extensions_server.py teletext   # 9002
```

## Health Endpoints

All servers implement standard health check endpoints:

### API Server (5001)

```bash
curl http://localhost:5001/api/health
# Response:
# {
#   "status": "healthy",
#   "version": "1.0.19",
#   "uptime": 123.45,
#   "endpoints": 60
# }
```

### Extension Servers (8888, 8889, 8892, 9002)

```bash
curl http://localhost:8889/health
# Response:
# {
#   "status": "healthy",
#   "extension": "Retro Terminal",
#   "uptime": 67.89
# }
```

## Port Change History

### v1.1.15 (December 2, 2025)
- **Removed**: `extensions/web/dashboard` (port 5050) - Archived to `memory/system/archived/`
- **Updated**: Mission Control now documented as port 5000 (embedded server)
- **Clarified**: System Dashboard uses port 8888 (not 8887 as in old startup config)

### v1.1.14 (November 2025)
- Added Mission Control dashboard extension (port 5000)
- Standardized health check endpoints

### v1.1.1 (October 2025)
- Introduced server_manager.py for unified control
- Implemented port_manager with auto-cleanup
- Added health monitoring

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8889

# Kill process (use server_manager for graceful shutdown)
python extensions/server_manager.py cleanup terminal

# Or force kill
kill -9 <PID>
```

### Server Won't Start

1. Check if port is available: `lsof -i :<port>`
2. Check server logs: `tail -f memory/logs/<server>_server.log`
3. Verify Python environment: `which python` (should be in venv)
4. Check health endpoint: `curl http://localhost:<port>/health`

### Health Check Fails

```bash
# Detailed health check with verbose output
curl -v http://localhost:8889/health

# Check if server process is running
ps aux | grep "python.*terminal"

# Restart with cleanup
python extensions/server_manager.py restart terminal
```

## Future Allocations

Reserved for upcoming features:

- **5050-5099**: Reserved for future extension servers
- **8893-8899**: Reserved for additional web extensions
- **9003-9099**: Reserved for display/visualization extensions

## See Also

- [SERVER-MANAGEMENT.md](SERVER-MANAGEMENT.md) - Detailed server management guide
- [extensions/core/shared/](core/shared/) - Base server and port manager implementation
- [server_manager.py](server_manager.py) - Unified server control tool

---

**Note**: Always use `server_manager.py` for starting/stopping servers to ensure proper port management and health monitoring.
