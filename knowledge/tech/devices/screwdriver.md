---
title: "Sonic Screwdriver Device Provisioning"
id: tech-devices-screwdriver
type: reference
category: devices
tags: [devices, devices]
difficulty: intermediate
last_updated: 2026-01-29
---

# Sonic Screwdriver Device Provisioning

Device discovery, flashing, and mesh enrollment for uDOS nodes.

---

## Frontmatter

```yaml
title: Sonic Screwdriver Provisioning
category: tech/devices
tags: [screwdriver, provisioning, firmware, meshcore]
tier: 2
db_link: devices.db/devices
wizard_link: wizard/tools/screwdriver/
created: 2026-01-07
updated: 2026-01-07
```

---

## Overview

The **Sonic Screwdriver** is the uDOS device provisioning system. It discovers, flashes, and enrolls hardware into your mesh network.

### Capabilities

| Feature | Description |
| ------- | ----------- |
| **Scan** | Discover available devices |
| **Flash** | Write firmware to device |
| **Configure** | Set device parameters |
| **Enroll** | Add to mesh network |
| **Verify** | Test device function |
| **Update** | OTA firmware updates |

---

## Quick Start

### 1. Scan for Devices

```bash
SCREWDRIVER SCAN
```

Output:

```text
🔧 Sonic Screwdriver - Scanning...

Found 3 devices:
  [D1] ESP32-C3 @ /dev/ttyUSB0  (not provisioned)
  [D2] RP2040 @ /dev/ttyACM0    (uDOS v1.0.2)
  [D3] Meshtastic @ BT:MESH01   (external)
```

### 2. Flash a Device

```bash
SCREWDRIVER FLASH D1
```

This will:

1. Download appropriate firmware
2. Enter bootloader mode
3. Flash firmware
4. Verify installation
5. Enroll in mesh

### 3. Configure Device

```bash
SCREWDRIVER CONFIG D1 --role=repeater --channel=7
```

---

## Device Types

### Supported Hardware

| Hardware | Chip | Use Case |
| -------- | ---- | -------- |
| ESP32-C3 | RISC-V | Nodes, sensors |
| ESP32-S3 | Xtensa | High-power nodes |
| RP2040 | ARM M0+ | Low-power sensors |
| Meshtastic | Various | External mesh |
| Custom | STM32 | Specialized |

### Device Roles

```text
┌─────────────┐
│    NODE     │  Primary mesh participant
│     ⊚       │  Full uDOS stack
└─────────────┘

┌─────────────┐
│   GATEWAY   │  Router between networks
│     ⊕       │  WiFi/BT/MeshCore bridge
└─────────────┘

┌─────────────┐
│   SENSOR    │  Read-only data source
│     ⊗       │  Temperature, GPS, etc.
└─────────────┘

┌─────────────┐
│  REPEATER   │  Signal relay
│     ⊙       │  No processing, just forward
└─────────────┘

┌─────────────┐
│    END      │  Client device
│     ⊘       │  Mobile, tablet console
└─────────────┘
```

---

## Provisioning Flow

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  DETECT  │───▶│  FLASH   │───▶│  CONFIG  │───▶│  ENROLL  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  USB/BT          Firmware        Set role      Add to mesh
  Serial          Download        Channel       Generate keys
                  Verify          Name          Test comms
```

### Step Details

1. **DETECT**: Identify hardware via USB/Bluetooth
2. **FLASH**: Write appropriate uDOS firmware
3. **CONFIG**: Set device-specific parameters
4. **ENROLL**: Generate mesh keys, test communication

---

## Commands Reference

### SCREWDRIVER Command

```bash
SCREWDRIVER <action> [device] [options]
```

| Action | Description | Example |
| ------ | ----------- | ------- |
| `SCAN` | Find devices | `SCREWDRIVER SCAN` |
| `FLASH` | Write firmware | `SCREWDRIVER FLASH D1` |
| `CONFIG` | Configure | `SCREWDRIVER CONFIG D1 --role=node` |
| `ENROLL` | Add to mesh | `SCREWDRIVER ENROLL D1` |
| `INFO` | Device details | `SCREWDRIVER INFO D2` |
| `UPDATE` | OTA update | `SCREWDRIVER UPDATE D2` |
| `RESET` | Factory reset | `SCREWDRIVER RESET D1 --confirm` |

### Options

| Option | Description |
| ------ | ----------- |
| `--role=<role>` | Device role (node/gateway/sensor/repeater/end) |
| `--channel=<n>` | Mesh channel (1-16) |
| `--name=<name>` | Device friendly name |
| `--force` | Skip confirmations |
| `--dry-run` | Simulate without changes |

---

## Database Schema

The Sonic Screwdriver maintains device state in `devices.db`:

```sql
-- devices table
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    hardware_type TEXT NOT NULL,
    firmware_version TEXT,
    device_role TEXT DEFAULT 'node',
    mesh_channel INTEGER DEFAULT 1,
    friendly_name TEXT,
    last_seen TIMESTAMP,
    status TEXT DEFAULT 'offline',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- device_connections
CREATE TABLE device_connections (
    device_id TEXT REFERENCES devices(id),
    connection_type TEXT,  -- usb, bluetooth, mesh
    connection_string TEXT,
    signal_strength INTEGER,
    last_contact TIMESTAMP
);
```

---

## Firmware Management

### Available Firmware

| Firmware | Target | Size | Features |
| -------- | ------ | ---- | -------- |
| `udos-node-esp32c3` | ESP32-C3 | 1.2MB | Full stack |
| `udos-lite-rp2040` | RP2040 | 256KB | Minimal |
| `udos-gateway-s3` | ESP32-S3 | 2MB | Multi-transport |
| `udos-sensor-c3` | ESP32-C3 | 512KB | Sensor-only |

### Firmware Location

```text
wizard/tools/screwdriver/
├── firmware/
│   ├── esp32c3/
│   │   ├── udos-node-v1.0.2.bin
│   │   └── udos-sensor-v1.0.2.bin
│   ├── esp32s3/
│   │   └── udos-gateway-v1.0.2.bin
│   └── rp2040/
│       └── udos-lite-v1.0.2.uf2
└── tools/
    ├── esptool.py
    └── picotool
```

---

## Troubleshooting

### Device Not Found

```bash
# Check USB connection
ls /dev/tty*

# Manual scan with verbose
SCREWDRIVER SCAN --verbose

# Specify port directly
SCREWDRIVER INFO --port=/dev/ttyUSB0
```

### Flash Failed

1. **Bootloader Mode**: Hold BOOT button, press RESET
2. **Driver Issues**: Install CH340/CP210x drivers
3. **Permission**: Add user to `dialout` group

### Mesh Not Connecting

```bash
# Check mesh status
MESH STATUS

# Verify channel match
SCREWDRIVER INFO D1 | grep channel

# Force re-enroll
SCREWDRIVER ENROLL D1 --force
```

---

## Security

### Key Management

Each device gets unique mesh credentials:

```text
Device Keys:
  - Public Key: Shared with mesh
  - Private Key: Stored on device
  - Mesh Secret: Shared with enrolled devices
```

### Transport Policy

Devices follow uDOS transport policy:

- **Private Transports**: Commands + Data allowed
- **Public Signals**: Beacon only, no data

---

## See Also

- [MeshCore Devices](meshcore.md)
- [Firmware Guide](firmware.md)
- [Mesh Network Setup](../networking/mesh-setup.md)
- [Transport Policy](../../reference/transport-policy.md)

---

Part of uDOS Knowledge Bank v1.0.2.0
