# Port Manager - Server and Port Management Utility

Complete server and port awareness and management utility for uDOS services.

## Overview

The Port Manager provides:

- **📋 Service Registry** - Centralized registry of all uDOS services and their ports
- **🔍 Conflict Detection** - Real-time detection of port conflicts
- **🔧 Port Management** - Auto-detect occupying processes, kill services, reassign ports
- **🚀 Launch Coordination** - Coordinated startup/shutdown with dependency awareness
- **📊 Status Dashboard** - Real-time visibility into all services
- **🌐 REST API** - Web endpoints for programmatic access
- **💻 CLI Tool** - Command-line utility for quick operations

## Service Registry

The port manager maintains awareness of all services:

| Service    | Port    | Environment  | Description                           |
| ---------- | ------- | ------------ | ------------------------------------- |
| **wizard** | 8765    | Production   | Always-on service layer               |
| **goblin** | 8767    | Experimental | Dev server with experimental features |
| **api**    | 5001    | Development  | REST/WebSocket API                    |
| **vite**   | 5173    | Development  | Frontend dev server                   |
| **tauri**  | dynamic | Development  | Desktop application                   |

## Features

### 1. Port Conflict Detection

Automatically detects when a registered service's port is occupied by a different process:

```bash
# Check for conflicts
python -m wizard.cli_port_manager conflicts

# Output
⚠️  PORT CONFLICTS DETECTED:

  Port 8767: Expected 'goblin' but found 'python' (PID 12345)
    Kill with: lsof -i :8767 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### 2. Service Status Monitoring

Check individual or all services:

```bash
# Check all services
python -m wizard.cli_port_manager status

# Check specific service
python -m wizard.cli_port_manager check wizard

# Output
📋 Service: wizard
   Port: 8765
   Environment: production
   Description: Wizard Server - Production always-on service
   Status: running
   Health: http://localhost:8765/health
```

### 3. Port Management

Kill services or reassign ports:

```bash
# Kill a specific service
python -m wizard.cli_port_manager kill wizard

# Kill by port
python -m wizard.cli_port_manager kill :8767

# Find available port
python -m wizard.cli_port_manager available 9000

# Reassign service to new port
python -m wizard.cli_port_manager reassign goblin 9000
```

### 4. Environment Variables

Generate environment setup script:

```bash
python -m wizard.cli_port_manager env

# Output
#!/bin/bash
# uDOS Service Port Environment - Auto-generated

export UDOS_WIZARD_PORT=8765
export UDOS_GOBLIN_PORT=8767
export UDOS_API_PORT=5001
export UDOS_VITE_PORT=5173

# Service URLs
export UDOS_WIZARD_URL=http://localhost:8765
export UDOS_GOBLIN_URL=http://localhost:8767
export UDOS_API_URL=http://localhost:5001
export UDOS_VITE_URL=http://localhost:5173
```

## REST API Endpoints

All endpoints available at `/api/v1/ports/`:

### Get Port Status Dashboard

```bash
GET /api/v1/ports/status

Response:
{
  "timestamp": "2026-01-17T12:00:00",
  "services": {
    "wizard": {
      "name": "wizard",
      "port": 8765,
      "environment": "production",
      "status": "running",
      "enabled": true,
      "pid": 12345
    }
  },
  "conflicts": [],
  "startup_order": ["wizard", "api", "goblin", "vite"],
  "shutdown_order": ["vite", "goblin", "api", "wizard"]
}
```

### List All Services

```bash
GET /api/v1/ports/services
```

### Check Specific Service

```bash
GET /api/v1/ports/services/wizard
```

### Get Port Conflicts

```bash
GET /api/v1/ports/conflicts
```

### Kill Service

```bash
POST /api/v1/ports/services/goblin/kill
```

### Kill Port

```bash
POST /api/v1/ports/ports/8767/kill
```

### Get Status Report

```bash
GET /api/v1/ports/report
```

### Get Environment Script

```bash
GET /api/v1/ports/env
```

## Python API

### Basic Usage

```python
from wizard.services.port_manager import get_port_manager

pm = get_port_manager()

# Check all services
statuses = pm.check_all_services()

# Print status report
print(pm.generate_report())

# Get conflicts
conflicts = pm.get_conflicts()

# Kill a service
pm.kill_service('goblin')

# Find available port
port = pm.get_available_port(9000)

# Reassign service
pm.reassign_port('goblin', port)
```

### Service Information

```python
from wizard.services.port_manager_service import get_port_service

ps = get_port_service()

# Get dashboard
dashboard = ps.get_dashboard()

# Check specific service
service_info = ps.check_service('wizard')
print(f"Status: {service_info.status}")
print(f"Port: {service_info.port}")
print(f"PID: {service_info.pid}")
```

## Launch Coordinator

Safely launch all services with automatic conflict resolution:

```bash
# Launch all services with interactive conflict resolution
python -m wizard.launch_with_port_manager

# Non-interactive mode
python -m wizard.launch_with_port_manager --non-interactive

# Check status only
python -m wizard.launch_with_port_manager --check-only

# Launch specific services
python -m wizard.launch_with_port_manager --services wizard,api
```

The launcher will:

1. ✅ Validate environment
2. 🔍 Detect port conflicts
3. 🗑️ Optionally kill conflicting processes
4. 🚀 Launch services in correct order
5. ❤️ Monitor health
6. 📊 Display final dashboard

## Configuration

Port registry stored in: `wizard/config/port_registry.json`

```json
{
  "timestamp": "2026-01-17T12:00:00",
  "services": [
    {
      "name": "wizard",
      "port": 8765,
      "environment": "production",
      "process_name": "python",
      "description": "Wizard Server - Production always-on service",
      "startup_cmd": "python -m wizard.server",
      "health_endpoint": "http://localhost:8765/health",
      "enabled": true
    }
  ]
}
```

## Integration with Wizard Server

The port manager is automatically integrated into Wizard Server. Access the port management dashboard:

1. **Web Dashboard**: `/api/v1/ports/status`
2. **Service List**: `/api/v1/ports/services`
3. **Formatted Report**: `/api/v1/ports/report`

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8767

# Kill the process
python -m wizard.cli_port_manager kill :8767

# Or manually
lsof -i :8767 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### Service Won't Start

```bash
# Check status
python -m wizard.cli_port_manager check goblin

# Check for conflicts
python -m wizard.cli_port_manager conflicts

# Reassign to available port
python -m wizard.cli_port_manager reassign goblin 9000
```

### Registry Out of Sync

```bash
# The registry auto-updates when checking services
# Force a full check
python -m wizard.cli_port_manager status
```

## Architecture

### Components

1. **PortManager** (`port_manager.py`)

   - Core registry and port checking logic
   - System-level port detection
   - Service lifecycle management

2. **PortManagerService** (`port_manager_service.py`)

   - FastAPI integration
   - REST endpoints
   - Health monitoring

3. **CLI Tool** (`cli_port_manager.py`)

   - Command-line interface
   - User-friendly output formatting
   - Quick operations

4. **Launch Coordinator** (`launch_with_port_manager.py`)
   - Coordinated startup sequence
   - Interactive conflict resolution
   - Service ordering and monitoring

## Future Enhancements

- [ ] Service auto-restart on failure
- [ ] Port watchdog monitoring
- [ ] Persistent service state
- [ ] Per-service rate limiting
- [ ] Service dependency declaration
- [ ] Automatic port allocation
- [ ] Historical port usage logs

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-17
