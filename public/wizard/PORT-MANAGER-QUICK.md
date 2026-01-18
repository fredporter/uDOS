# Port Manager Quick Reference

## Instant Commands

### Check Status

```bash
python -m wizard.cli_port_manager status
```

### Check Specific Service

```bash
python -m wizard.cli_port_manager check wizard
python -m wizard.cli_port_manager check goblin
python -m wizard.cli_port_manager check api
```

### Find Conflicts

```bash
python -m wizard.cli_port_manager conflicts
```

### Kill Service or Port

```bash
# By service name
python -m wizard.cli_port_manager kill wizard

# By port number
python -m wizard.cli_port_manager kill :8767
```

### Find Available Port

```bash
python -m wizard.cli_port_manager available 9000
```

### Get Environment Variables

```bash
python -m wizard.cli_port_manager env
```

## Web API Access

### Get Full Dashboard

```bash
curl http://localhost:8765/api/v1/ports/status
```

### List All Services

```bash
curl http://localhost:8765/api/v1/ports/services
```

### Check Specific Service

```bash
curl http://localhost:8765/api/v1/ports/services/wizard
```

### Get Conflicts

```bash
curl http://localhost:8765/api/v1/ports/conflicts
```

### Get Formatted Report

```bash
curl http://localhost:8765/api/v1/ports/report
```

### Kill a Service

```bash
curl -X POST http://localhost:8765/api/v1/ports/services/goblin/kill
```

### Kill a Port

```bash
curl -X POST http://localhost:8765/api/v1/ports/ports/8767/kill
```

## Python API Quick Start

```python
from wizard.services.port_manager import get_port_manager

pm = get_port_manager()

# Check all services
statuses = pm.check_all_services()

# Print formatted report
print(pm.generate_report())

# Get conflicts
conflicts = pm.get_conflicts()
for svc_name, occupant in conflicts:
    print(f"Port conflict: {svc_name} vs {occupant['process']}")

# Kill a service
pm.kill_service('goblin')

# Find available port
port = pm.get_available_port(9000)
print(f"Available port: {port}")
```

## Common Issues & Solutions

### "Port 8767 already in use"

```bash
# Check what's using it
lsof -i :8767

# Kill it
python -m wizard.cli_port_manager kill :8767

# Or with one-liner
lsof -i :8767 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### Service won't start

```bash
# Check status
python -m wizard.cli_port_manager check goblin

# Check for conflicts
python -m wizard.cli_port_manager conflicts

# Find available port and reassign
port=$(python -m wizard.cli_port_manager available 9000)
python -m wizard.cli_port_manager reassign goblin $port
```

### All services dashboard

```bash
# Check everything at once
python -m wizard.cli_port_manager status

# Or via API
curl http://localhost:8765/api/v1/ports/status | jq .
```

## Service Ports Reference

| Service    | Port    | Type         | Command                           |
| ---------- | ------- | ------------ | --------------------------------- |
| **Wizard** | 8765    | Production   | `python -m wizard.server`         |
| **Goblin** | 8767    | Experimental | `python dev/goblin/server.py`     |
| **API**    | 5001    | Development  | `python -m extensions.api.server` |
| **Vite**   | 5173    | Development  | `npm run dev`                     |
| **Tauri**  | dynamic | Development  | `npm run tauri dev`               |

---

**Full Documentation**: See [wizard/docs/PORT-MANAGER.md](PORT-MANAGER.md)
