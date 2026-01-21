# MeshCore Transport

**Version:** Alpha v1.1.0.4+  
**Status:** 🟢 Active  
**Policy:** PRIVATE (commands + data allowed)

---

## Overview

MeshCore transport layer for uDOS. Provides unified packet interface for peer-to-peer mesh networking. Wraps the MeshCore service from `extensions/play/` to provide transport-layer abstractions.

## Features

- **Device Discovery** - Scan for nearby mesh nodes
- **P2P Messaging** - Direct device-to-device communication
- **Command Relay** - Send uDOS commands to remote devices
- **Multi-hop Routing** - Packets route through intermediate nodes
- **Encrypted Transport** - All data encrypted in transit

## Transport Policy

```yaml
meshcore:
  type: private
  realm: user_mesh
  data_allowed: true
  commands_allowed: true
  max_packet_size: 65536  # 64KB
```

## Usage

### Basic Operations

```python
from extensions.transport.meshcore import MeshTransport, get_mesh_transport

# Get transport instance
transport = get_mesh_transport("my-device-id")

# Check availability
if transport.is_available():
    print(f"State: {transport.get_state()}")

# Scan for devices
devices = transport.scan(timeout=5.0)
for d in devices:
    print(f"Found: {d['name']} ({d['device_id']})")

# Send message
transport.send_message("target-device-id", "Hello from uDOS!")

# Send command to remote device
transport.send_command("target-device-id", "[FILE|LIST*memory/]")

# Broadcast to all
transport.broadcast("Network announcement!")

# Ping device
latency = transport.ping("target-device-id")
if latency:
    print(f"Latency: {latency:.2f}ms")
```

### Packet Types

| Type | Description |
|------|-------------|
| `HANDSHAKE` | Device pairing/unpairing |
| `DATA` | Binary file transfer |
| `COMMAND` | uDOS command relay |
| `MESSAGE` | Text message |
| `ACK` | Acknowledgment |
| `PING` | Connectivity check |
| `PONG` | Ping response |
| `DISCOVERY` | Device discovery |
| `BROADCAST` | Network-wide message |

### Custom Packet Handling

```python
from extensions.transport.meshcore import PacketType

def handle_incoming_command(packet):
    command = packet.payload.decode('utf-8')
    print(f"Received command from {packet.source_id}: {command}")
    # Execute command...

transport.register_handler(PacketType.COMMAND, handle_incoming_command)
```

## TUI Commands

Access via `MESH` command in TUI:

```bash
MESH SCAN              # Discover nearby devices
MESH PAIR <device>     # Pair with device
MESH SEND <dev> <msg>  # Send message
MESH BROADCAST <msg>   # Broadcast to all
MESH PING <device>     # Check connectivity
MESH DEVICES           # List known devices
MESH STATS             # Network statistics
MESH STATUS            # Connection state
```

## Dependencies

- `extensions/play/services/meshcore_service.py` - Core mesh service
- `extensions/play/services/meshcore_protocol.py` - Protocol definitions
- `extensions/play/meshcore_device_manager.py` - Device management

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   TUI Commands                       │
│               (core/commands/mesh_handler.py)        │
├─────────────────────────────────────────────────────┤
│              MeshCore Transport Layer                │
│        (extensions/transport/meshcore/__init__.py)   │
├─────────────────────────────────────────────────────┤
│               MeshCore Service                       │
│     (extensions/play/services/meshcore_service.py)   │
├─────────────────────────────────────────────────────┤
│              MeshCore Protocol                       │
│    (extensions/play/services/meshcore_protocol.py)   │
└─────────────────────────────────────────────────────┘
```

## Testing

```bash
# Test transport availability
python -c "from extensions.transport.meshcore import get_mesh_transport; t = get_mesh_transport(); print('OK' if t else 'N/A')"

# Run tests
pytest memory/tests/test_meshcore_transport.py -v
```

## Security

- All packets include TTL (max 8 hops by default)
- Hop count prevents routing loops
- Packet IDs prevent replay attacks
- Timestamp validation for freshness

---

*Last Updated: 2026-01-05*
