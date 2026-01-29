---
title: "Firmware Management"
id: tech-devices-firmware
type: reference
category: devices
tags: [devices, devices]
difficulty: intermediate
last_updated: 2026-01-29
---

# Firmware Management

Managing firmware for uDOS mesh devices.

---

## Frontmatter

```yaml
title: Firmware Management
category: tech/devices
tags: [firmware, updates, flashing, ota]
tier: 2
db_link: devices.db/firmware_packages
wizard_link: wizard/tools/screwdriver/firmware/
created: 2026-01-07
updated: 2026-01-07
```

---

## Overview

uDOS device firmware is managed through the Sonic Screwdriver provisioning system. This guide covers firmware types, update methods, and troubleshooting.

---

## Firmware Types

### Available Packages

| Package | Target | Size | Features |
| ------- | ------ | ---- | -------- |
| `udos-node` | ESP32-C3/S3 | 1.2MB | Full mesh stack |
| `udos-lite` | RP2040 | 256KB | Minimal client |
| `udos-gateway` | ESP32-S3 | 2MB | Multi-transport bridge |
| `udos-sensor` | ESP32-C3 | 512KB | Sensor data only |
| `udos-repeater` | ESP32-C3 | 384KB | Relay only |

### Version Format

```text
udos-<type>-<chip>-v<major>.<minor>.<patch>.<build>.<ext>

Example: udos-node-esp32c3-v1.0.2.45.bin
```

---

## Update Methods

### Method 1: USB Flash (Recommended for new devices)

```bash
# Scan for device
SCREWDRIVER SCAN

# Flash via USB
SCREWDRIVER FLASH D1 --firmware=udos-node
```

### Method 2: OTA Update (For enrolled devices)

```bash
# Check current version
DEVICE INFO D1

# Update over-the-air
SCREWDRIVER UPDATE D1
```

### Method 3: Manual Flash

```bash
# For ESP32
esptool.py --port /dev/ttyUSB0 write_flash 0x0 udos-node-esp32c3-v1.0.2.bin

# For RP2040
# Hold BOOTSEL, connect USB, copy .uf2 file to RPI-RP2 drive
```

---

## Firmware Repository

### Local Storage

```text
wizard/tools/screwdriver/
├── firmware/
│   ├── esp32c3/
│   │   ├── udos-node-v1.0.2.45.bin
│   │   ├── udos-sensor-v1.0.2.45.bin
│   │   └── udos-repeater-v1.0.2.45.bin
│   ├── esp32s3/
│   │   └── udos-gateway-v1.0.2.45.bin
│   ├── rp2040/
│   │   └── udos-lite-v1.0.2.45.uf2
│   └── manifest.json
└── tools/
    ├── esptool.py
    ├── picotool
    └── verify.py
```

### Manifest Format

```json
{
  "version": "1.0.2.45",
  "packages": [
    {
      "name": "udos-node",
      "chip": "esp32c3",
      "file": "esp32c3/udos-node-v1.0.2.45.bin",
      "size": 1258291,
      "sha256": "abc123...",
      "features": ["mesh", "commands", "files", "sensors"]
    }
  ]
}
```

---

## Database Schema

Firmware packages tracked in `devices.db`:

```sql
CREATE TABLE firmware_packages (
    id TEXT PRIMARY KEY,
    package_name TEXT NOT NULL,
    version TEXT NOT NULL,
    chip_type TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    sha256 TEXT,
    features TEXT,  -- JSON array
    release_date TIMESTAMP,
    is_stable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track device firmware history
CREATE TABLE device_firmware_history (
    id INTEGER PRIMARY KEY,
    device_id TEXT REFERENCES devices(id),
    firmware_id TEXT REFERENCES firmware_packages(id),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    install_method TEXT,  -- usb, ota, manual
    success BOOLEAN
);
```

---

## Update Process

### OTA Update Flow

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CHECK     │────▶│  DOWNLOAD   │────▶│   VERIFY    │
│  Version    │     │  Package    │     │   SHA256    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   REBOOT    │◀────│   FLASH     │◀────│  BACKUP     │
│   Device    │     │   Firmware  │     │   Config    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Safety Features

| Feature | Description |
| ------- | ----------- |
| **Rollback** | Keep previous version for recovery |
| **Verify** | SHA256 check before flash |
| **Backup** | Save config before update |
| **Test Mode** | Boot once, verify, then commit |

---

## Commands Reference

### Firmware Commands

```bash
# List available firmware
SCREWDRIVER FIRMWARE LIST

# Check for updates
SCREWDRIVER FIRMWARE CHECK

# Download specific package
SCREWDRIVER FIRMWARE DOWNLOAD udos-node-v1.0.3

# Verify package integrity
SCREWDRIVER FIRMWARE VERIFY udos-node-v1.0.2.bin
```

### Device Update Commands

```bash
# Update single device
SCREWDRIVER UPDATE D1

# Update all devices
SCREWDRIVER UPDATE --all

# Force specific version
SCREWDRIVER UPDATE D1 --version=1.0.2.45

# Rollback to previous
SCREWDRIVER ROLLBACK D1
```

---

## Bootloader Mode

### ESP32 (C3/S3)

1. Hold **BOOT** button
2. Press **RESET** button
3. Release **RESET**
4. Release **BOOT**
5. Device is now in bootloader mode

### RP2040

1. Hold **BOOTSEL** button
2. Connect USB cable
3. Release **BOOTSEL**
4. Device appears as USB drive

### Recovery Mode

If device won't boot:

```bash
# Force bootloader
SCREWDRIVER RESCUE --port=/dev/ttyUSB0

# Factory reset flash
SCREWDRIVER FLASH D1 --factory-reset
```

---

## Troubleshooting

### Flash Failed

```text
Error: Failed to connect to ESP32
```

**Solutions:**

1. Check USB cable (data-capable)
2. Try different USB port
3. Install drivers (CH340/CP210x)
4. Enter bootloader mode manually

### OTA Failed

```text
Error: Connection lost during update
```

**Solutions:**

1. Move device closer
2. Check mesh connectivity
3. Try USB flash instead
4. Check battery level (>50%)

### Version Mismatch

```text
Warning: Firmware incompatible with mesh version
```

**Solutions:**

1. Update all devices together
2. Check minimum version requirements
3. Rollback to compatible version

---

## Best Practices

### Update Schedule

| Frequency | Type |
| --------- | ---- |
| Weekly | Security patches |
| Monthly | Feature updates |
| Quarterly | Major versions |

### Pre-Update Checklist

- [ ] Backup device config
- [ ] Check battery levels (>50%)
- [ ] Verify network stability
- [ ] Review release notes
- [ ] Test on one device first

### Post-Update Verification

```bash
# Verify all devices
SCREWDRIVER VERIFY --all

# Check mesh health
MESH STATUS

# Run diagnostics
DEVICE DIAG D1
```

---

## See Also

- [Sonic Screwdriver](screwdriver.md) - Provisioning
- [MeshCore Devices](meshcore.md) - Device types
- [Mesh Setup](../networking/mesh-setup.md) - Network config

---

Part of uDOS Knowledge Bank v1.0.2.0
