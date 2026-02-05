# Home Assistant Container Gateway — uDOS Wizard

## Overview

Complete REST/WebSocket gateway for Home Assistant device integration in uDOS Wizard, providing:

- **Device Discovery** — Automatic detection via UDP, mDNS, UPnP, HA API
- **Real-time State Sync** — WebSocket subscriptions for live updates
- **Service Control** — Turn on/off, set properties, call services
- **Health Monitoring** — Track device availability and signal strength

## Architecture

```
       uDOS Wizard
            |
    +-------+--------+
    |                |
 [REST API]    [WebSocket]
    |                |
    +-------+--------+
            |
     Gateway Manager
            |
    +-------+---+---+
    |           |   |
Registry    Discovery  Controller
```

## Components

### 1. Gateway Manager (`gateway/manager.py`)
- Connects to Home Assistant
- Manages device state
- Handles events and subscriptions
- Coordinates discovery and monitoring

### 2. Device Registry (`devices/__init__.py`)
- Maintains device inventory
- Tracks device aliases
- Manages device metadata
- Supports filtering by type/manufacturer

### 3. Discovery Service
- UDP broadcast discovery
- mDNS/Bonjour support
- UPnP device detection
- Home Assistant API polling

### 4. REST API (`api/rest.py`)
- Status & health endpoints
- Device discovery and listing
- Entity management
- Service calls (turn_on, turn_off, etc)

### 5. WebSocket Gateway (`api/websocket.py`)
- Real-time state updates
- Event subscriptions
- Bidirectional communication
- Automatic reconnection

## Quick Start

### Run Service Standalone

```bash
# From uDOS root
python -m wizard.services.home_assistant

# Service starts on http://localhost:8765
```

### Check Status

```bash
curl http://localhost:8765/api/ha/status
```

### Discover Devices

```bash
curl http://localhost:8765/api/ha/discover
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8765/ws/ha');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    topics: ['device:*', 'entity:*']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### Turn On/Off Device

```bash
# Turn on
curl -X POST http://localhost:8765/api/ha/turn-on \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": ["light.living_room"]}'

# Turn off
curl -X POST http://localhost:8765/api/ha/turn-off \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": ["light.living_room"]}'
```

## API Reference

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/ha/status` | Gateway status |
| `GET` | `/api/ha/health` | Health check |
| `GET` | `/api/ha/discover` | Trigger discovery |
| `GET` | `/api/ha/devices` | List devices |
| `GET` | `/api/ha/devices/{id}` | Get device details |
| `GET` | `/api/ha/devices/{id}/state` | Get device state |
| `GET` | `/api/ha/entities` | List entities |
| `POST` | `/api/ha/turn-on` | Turn on entities |
| `POST` | `/api/ha/turn-off` | Turn off entities |
| `POST` | `/api/ha/services/{domain}/{service}` | Call service |

### WebSocket Messages

#### Subscribe

```json
{
  "type": "subscribe",
  "topics": ["device:*", "entity:*"]
}
```

#### State Change Event

```json
{
  "type": "state_changed",
  "device_id": "light.living_room",
  "state": {
    "is_available": true,
    "connection_status": "connected"
  }
}
```

## Configuration

Edit `schemas/gateway.py` `GatewayConfigSchema`:

```python
config = GatewayConfigSchema(
    gateway_id="udos-ha-main",
    ha_url="http://localhost:8123",
    ha_token="your-token",
    ws_enabled=True,
    auto_discovery=True,
    discovery_interval=60,
    heartbeat_interval=30,
)
```

## Integration with Wizard

### Register in Container Launcher

Add to `wizard/routes/container_launcher_routes.py`:

```python
"home-assistant": {
    "name": "Home Assistant",
    "port": 8765,
    "service_path": "wizard/services/home_assistant",
    "launch_command": ["python", "-m", "wizard.services.home_assistant"],
    "browser_route": "/ui/ha",
}
```

### Use in Routes

```python
from wizard.services.home_assistant.api import set_gateway_manager
from wizard.services.home_assistant.gateway.manager import GatewayManager

# In your route handler
manager_instance = GatewayManager(config)
set_gateway_manager(manager_instance)
await manager_instance.initialize()
```

## Extending

### Add Custom Device Type

1. Update `schemas/device.py` `DeviceType` enum
2. Implement discovery in `DiscoveryService`
3. Add controller method in `DeviceController`

### Add Discovery Method

```python
class DiscoveryService:
    async def _custom_discovery(self) -> List[Dict]:
        # Implement custom protocol
        return discovered_devices
```

### Add Event Handler

```python
async def on_device_discovered(device):
    logger.info(f"Device: {device.name}")

manager.on_event("device_discovered", on_device_discovered)
```

## Logging Tags

- `[WIZ]` — Wizard integration
- `[LOCAL]` — Local device communication
- `[MESH]` — Mesh network updates

## Testing

```bash
# Run health check
curl http://localhost:8765/api/ha/health

# Check active connections
curl http://localhost:8765/api/ha/status | jq '.data.active_connections'
```

## Notes

- Token is redacted in config responses for security
- Device aliases enable lookup by name or ID
- WebSocket subscriptions support glob patterns (`device:*`)
- Health checks run every 30 seconds by default
- Device discovery runs every 60 seconds by default

---

**Status:** Active Development
**Version:** 0.1.0
**Last Updated:** 2026-02-05
