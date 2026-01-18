# MeshCore Devices

Hardware devices for uDOS mesh networking layer.

---

## Frontmatter

```yaml
title: MeshCore Devices
category: tech/devices
tags: [meshcore, hardware, mesh, networking]
tier: 2
db_link: devices.db/devices
created: 2026-01-07
updated: 2026-01-07
```

---

## Overview

MeshCore is the uDOS peer-to-peer networking layer operating at TILE coordinates 600-650.

### Key Features

- **Offline-First**: No internet required
- **Self-Healing**: Automatic route discovery
- **Encrypted**: All traffic encrypted
- **Multi-Transport**: Radio, Bluetooth, WiFi

---

## Device Registry

### Symbols

| Symbol | Type | Description |
| ------ | ---- | ----------- |
| ⊚ | Node | Full uDOS participant |
| ⊕ | Gateway | Network bridge |
| ⊗ | Sensor | Data source |
| ⊙ | Repeater | Signal relay |
| ⊘ | End Device | Client |

### Status Indicators

```text
● Online    (green)
○ Offline   (grey)
◐ Degraded  (yellow)
◉ Alert     (red)
```

---

## Network Topology

```text
                    ┌─────┐
                    │ WIZ │  Wizard Server (optional)
                    │ ⊕  │  Internet access
                    └──┬──┘
                       │ Private Transport
         ┌─────────────┼─────────────┐
         │             │             │
      ┌──┴──┐       ┌──┴──┐       ┌──┴──┐
      │ ⊚  │       │ ⊚  │       │ ⊚  │  Nodes
      │NODE1│       │NODE2│       │NODE3│
      └──┬──┘       └──┬──┘       └──┬──┘
         │             │             │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │         │   │         │   │         │
  ┌─┴─┐     ┌─┴─┐ │       ┌─┴─┐ │       ┌─┴─┐
  │ ⊗ │     │ ⊘ │ │       │ ⊙ │ │       │ ⊗ │
  │SNS│     │END│ │       │RPT│ │       │SNS│
  └───┘     └───┘ │       └───┘ │       └───┘
                  │             │
              ┌───┴───┐     ┌───┴───┐
              │  ⊘   │     │  ⊘   │
              │ END  │     │ END  │
              └───────┘     └───────┘
```

---

## Commands

### DEVICE Commands

```bash
DEVICE LIST               # All registered devices
DEVICE INFO <id>          # Device details
DEVICE PING <id>          # Test connectivity
DEVICE RENAME <id> <name> # Rename device
DEVICE REMOVE <id>        # Unregister device
```

### MESH Commands

```bash
MESH STATUS               # Network overview
MESH TOPOLOGY             # Visual map
MESH ROUTES               # Routing table
MESH CHANNEL <n>          # Change channel
MESH SCAN                 # Find neighbors
```

---

## Device Configuration

### Node Configuration

```yaml
# device.yaml
type: node
role: full
channel: 1
encryption: aes256
features:
  - mesh_routing
  - command_execution
  - file_transfer
  - sensor_aggregation
```

### Sensor Configuration

```yaml
# sensor.yaml
type: sensor
role: readonly
channel: 1
sensors:
  - type: temperature
    interval: 60
  - type: gps
    interval: 300
```

---

## Database Schema

Device state stored in `devices.db`:

```sql
-- Device registry
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    hardware_type TEXT NOT NULL,
    device_role TEXT CHECK(device_role IN 
        ('node', 'gateway', 'sensor', 'repeater', 'end')),
    mesh_channel INTEGER DEFAULT 1,
    friendly_name TEXT,
    public_key TEXT,
    firmware_version TEXT,
    status TEXT DEFAULT 'offline',
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Connection tracking
CREATE TABLE device_connections (
    id INTEGER PRIMARY KEY,
    device_id TEXT REFERENCES devices(id),
    connection_type TEXT,
    connection_string TEXT,
    signal_strength INTEGER,
    latency_ms INTEGER,
    last_contact TIMESTAMP
);

-- Link to knowledge
CREATE TABLE device_knowledge_links (
    device_id TEXT REFERENCES devices(id),
    file_path TEXT,
    link_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Transport Types

### Private (Data Allowed)

| Transport | Range | Speed | Use Case |
| --------- | ----- | ----- | -------- |
| MeshCore | 1km+ | 115kbps | Primary |
| BT Private | 10m | 2Mbps | Pairing |
| NFC | Touch | 424kbps | Secure transfer |
| QR Relay | Visual | N/A | Bootstrap |
| Audio | 30m | 300bps | Backup |

### Public (Signal Only)

| Transport | Purpose |
| --------- | ------- |
| BT Public | Beacons/presence only |

---

## Security Model

### Key Hierarchy

```text
┌────────────────────────────────────┐
│          MESH MASTER KEY           │  Per-network
│  (Generated on first node)         │
└───────────────┬────────────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Device Key  │   │ Device Key  │    Per-device
│   Pair      │   │   Pair      │
└─────────────┘   └─────────────┘
```

### Enrollment Flow

1. New device scanned via Sonic Screwdriver
2. Device generates keypair
3. Public key shared via QR/NFC
4. Master key fragment distributed
5. Device can now participate

---

## Monitoring

### Health Metrics

| Metric | Good | Warning | Critical |
| ------ | ---- | ------- | -------- |
| Signal | > -70dBm | -70 to -85 | < -85dBm |
| Latency | < 100ms | 100-500ms | > 500ms |
| Packet Loss | < 1% | 1-5% | > 5% |
| Battery | > 50% | 20-50% | < 20% |

### Dashboard Command

```bash
MESH DASHBOARD
```

Output:

```text
╔══════════════════════════════════════════════════╗
║             MeshCore Network Status              ║
╠══════════════════════════════════════════════════╣
║  Nodes: 3/3 online    Channel: 1                 ║
║  Avg Latency: 45ms    Packet Loss: 0.2%          ║
╠══════════════════════════════════════════════════╣
║  ⊚ NODE1 [●] -52dBm  ⊚ NODE2 [●] -61dBm        ║
║  ⊗ TEMP1 [●] -70dBm  ⊙ RPT01 [●] -45dBm        ║
║  ⊘ PHONE [●] -55dBm  ⊘ TAB01 [○] offline       ║
╚══════════════════════════════════════════════════╝
```

---

## See Also

- [Sonic Screwdriver](screwdriver.md) - Device provisioning
- [Firmware Guide](firmware.md) - Updates
- [Mesh Setup](../networking/mesh-setup.md) - Network config
- [Transport Policy](../../reference/transport-policy.md)

---

Part of uDOS Knowledge Bank v1.0.2.0
