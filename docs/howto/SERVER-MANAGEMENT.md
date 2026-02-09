# uDOS Server Management Guide

**Status:** 📘 CURRENT DOCUMENTATION (Beta v1.0.26+)  
**Last Updated:** 2025-12-02

## Overview

uDOS v1.0.26 introduces a comprehensive server infrastructure with bulletproof port management, health monitoring, and unified control across all web extensions.

## Architecture

### Shared Framework (`extensions/core/shared/`)

#### Port Manager (`port_manager.py`)
- **Auto-detection**: Identifies processes using ports
- **Self-healing**: Automatically cleans up conflicts
- **Graceful shutdown**: SIGTERM → SIGKILL escalation
- **Alternative ports**: Finds nearby available ports if preferred is busy
- **Health checks**: TCP connection verification

#### Base Server (`base_server.py`)
- **BaseExtensionServer**: Foundation for all web extensions
- **BaseExtensionHandler**: Common HTTP handler with CORS
- **Logging**: Rotating file logs to `sandbox/logs/`
- **Signal handling**: Graceful shutdown on SIGTERM/SIGINT
- **Health endpoints**: `/health` and `/status` built-in

### Server Manager (`extensions/server_manager.py`)

Unified CLI tool for managing all uDOS servers.

## Usage

### Quick Start

```bash
# Check status of all servers
python extensions/server_manager.py status

# Start all servers
python extensions/server_manager.py start-all

# Start specific server
python extensions/server_manager.py start terminal

# Restart server (cleanup + start)
python extensions/server_manager.py restart api

# Stop all servers
python extensions/server_manager.py cleanup-all

# Check health
python extensions/server_manager.py health terminal
```

### Available Servers

| Server | Port | Description |
|--------|------|-------------|
| `api` | 5001 | Core uDOS command API |
| `terminal` | 8889 | Retro terminal interface |
| `dashboard` | 8888 | Arcade-style dashboard |
| `teletext` | 9002 | Teletext interface |
| `desktop` | 8892 | Retro desktop environment |

### Status Display

The status command shows:
- ✅ **HEALTHY**: Server responding to health checks
- ⚠️ **RUNNING**: Port in use but no health response
- ❌ **STOPPED**: Port available, server not running

```bash
$ python extensions/server_manager.py status

======================================================================
                          uDOS Server Status
======================================================================

✅ API Server           HEALTHY                         Port: 5001
   └─ Health: healthy

✅ Terminal             HEALTHY                         Port: 8889
   └─ Health: healthy

❌ Dashboard            STOPPED                         Port: 8888

======================================================================
```

## Server Lifecycle

### Manual Server Management

#### Start Individual Extension

```bash
cd ~/uDOS
source .venv/bin/activate

# Start API server
PORT=5001 python extensions/api/server.py &

# Start terminal server
python extensions/core/extensions_server.py terminal &

# Start dashboard
python extensions/core/extensions_server.py dashboard &
```

#### Health Check

All servers provide `/health` endpoint:

```bash
curl http://localhost:8889/health
# Returns: {"status": "healthy", "extension": "Retro Terminal", "uptime": 123.45}

curl http://localhost:5001/api/health
# Returns: {"status": "healthy", "version": "1.0.19", ...}
```

### Automatic Port Cleanup

The port manager automatically:
1. Detects if port is already in use
2. Identifies the process using it
3. Sends SIGTERM for graceful shutdown
4. Waits up to 5 seconds
5. Sends SIGKILL if still running
6. Finds alternative port if cleanup fails

### Logging

All servers log to `sandbox/logs/`:
- `api_server.log` - API server
- `terminal_server.log` - Terminal extension
- `dashboard_server.log` - Dashboard extension
- `extensions_server.log` - Main extensions server

Logs use rotating file handler:
- Max size: 10MB per file
- Backup count: 5 files
- Total capacity: ~50MB per service

## Integration with uDOS Core

### Terminal → API Integration

The terminal extension now properly integrates with uDOS core:

1. **Command Execution**:
   - Terminal sends commands to `http://localhost:5001/api/command`
   - API processes through uDOS core
   - Results displayed in terminal

2. **Session Management**:
   - Session initialized on startup
   - Current directory tracked
   - Command history maintained

3. **Fallback Handling**:
   - If API unavailable, uses local command handlers
   - Comprehensive logging for debugging
   - Error messages indicate core availability

### Command Flow

```
User Input → Terminal JS → API Server → uDOS Core → Response
                ↓ (if API down)
            Local Handlers
```

## Troubleshooting

### Port Conflicts

If you see "Port already in use":

```bash
# Check what's using the port
lsof -i :8889

# Use server manager to cleanup
python extensions/server_manager.py cleanup terminal

# Or force cleanup all
python extensions/server_manager.py cleanup-all
```

### Server Won't Start

1. **Check logs**: `tail -f sandbox/logs/terminal_server.log`
2. **Verify port**: `lsof -i :8889`
3. **Check health**: `curl http://localhost:8889/health`
4. **Use server manager**: `python extensions/server_manager.py status`

### Health Check Fails

```bash
# Detailed health check
curl -v http://localhost:8889/health

# Check if server is running
ps aux | grep "python.*terminal"

# Restart with cleanup
python extensions/server_manager.py restart terminal
```

### Browser Cache Issues

After server updates:
1. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
2. Clear cache completely
3. Open DevTools → Network tab → Disable cache
4. Check console for errors

## Development Workflow

### Adding New Extension

1. Create extension directory: `extensions/core/myext/`
2. Add to `EXTENSIONS` dict in `extensions_server.py`
3. Use `BaseExtensionServer` for server setup
4. Add to `server_manager.py` SERVERS dict
5. Test with server manager

### Extension Template

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import BaseExtensionServer

def main():
    server = BaseExtensionServer(
        name='MyExtension',
        port=9999,
        root_dir=Path(__file__).parent
    )
    server.start(auto_cleanup=True)

if __name__ == '__main__':
    main()
```

## Performance Tips

1. **Start only needed servers**: Don't run all servers if you only need terminal
2. **Monitor logs**: Watch for excessive requests or errors
3. **Use health checks**: Verify servers before making requests
4. **Cleanup regularly**: Use `cleanup-all` when done developing

## API Reference

### Port Manager

```python
from shared import get_port_manager

pm = get_port_manager()

# Check availability
pm.is_port_available(8889)

# Cleanup port
pm.cleanup_port(8889)

# Find alternative
pm.find_available_port(8889)

# Health check
pm.health_check(8889)
```

### Base Server

```python
from shared import BaseExtensionServer

server = BaseExtensionServer(
    name='MyServer',
    port=9999,
    root_dir=Path('.'),
    api_url='http://localhost:5001/api'
)

# Start with automatic cleanup
server.start(auto_cleanup=True)

# Check health
server.is_healthy()

# Cleanup
server.cleanup()
```

## Best Practices

1. **Always use server manager** for production
2. **Monitor logs** in `sandbox/logs/`
3. **Cleanup before starting** to avoid conflicts
4. **Check health** before making requests
5. **Use graceful shutdown** (Ctrl+C) when possible
6. **Hard refresh browser** after server updates

## Future Enhancements

- [ ] Web UI for server management
- [ ] Automatic server restart on crash
- [ ] Load balancing for multiple instances
- [ ] Metrics and monitoring dashboard
- [ ] Docker container support
- [ ] Systemd service files
- [ ] Nginx reverse proxy configs
