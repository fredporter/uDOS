# Tech Knowledge Category

Hardware, devices, networking, and communication systems for uDOS.

## Structure

```text
tech/
├── README.md           ← This file
├── devices/            ← Hardware & device management
│   ├── meshcore.md     ← MeshCore networking devices
│   ├── screwdriver.md  ← Sonic Screwdriver provisioning
│   └── firmware.md     ← Firmware management
├── networking/         ← Network configuration
│   ├── mesh-setup.md
│   └── transport.md
├── radio/              ← Radio communication
│   ├── ham-basics.md
│   ├── cb-radio.md
│   └── emergency.md
└── signaling/          ← Visual/acoustic signals
    ├── morse-code.md
    └── signal-mirrors.md
```

## Database Links

| Database | Table | Link Type |
| -------- | ----- | --------- |
| `devices.db` | `devices` | `documentation` |
| `devices.db` | `firmware_packages` | `reference` |
| `wizard/scripts.db` | `wizard_scripts` | `provisioning` |

## Tags

- `#meshcore` - MeshCore networking
- `#screwdriver` - Sonic Screwdriver tools
- `#firmware` - Device firmware
- `#radio` - Radio communication
- `#networking` - Network setup
- `#offline` - Offline-first methods

---

## MeshCore Layer (600-650)

Device management for peer-to-peer mesh networking.

### Device Types

| Type | Symbol | Purpose |
| ---- | ------ | ------- |
| Node | ⊚ | Primary hub |
| Gateway | ⊕ | Router |
| Sensor | ⊗ | Monitor |
| Repeater | ⊙ | Relay |
| End Device | ⊘ | Client |

### Quick Reference

- [MeshCore Devices](devices/meshcore.md) - Device registry
- [Sonic Screwdriver](devices/screwdriver.md) - Provisioning
- [Firmware Guide](devices/firmware.md) - Updates & flashing

---

## Communication Systems

Off-grid communication methods and equipment.

### Contents

- **Radio**: HAM radio, CB, FRS/GMRS
- **Signaling**: Visual signals, smoke, mirrors
- **Codes**: Morse code, signal flags
- **Networks**: Mesh networks, repeaters
- **Antennas**: Construction, tuning
- **No-Power Methods**: Semaphore, runners
- **Security**: Basic encryption, code words

### Off-Grid Communication

When internet/cell networks fail:

- HAM radio networks
- CB radio (limited range)
- Visual signaling
- Physical message delivery
- Community bulletin systems

---

## uDOS Integration

The uDOS device spawning system (v1.1.0+) enables:

- Peer-to-peer mesh networking
- Laptop → mobile device spawning
- No corporate ISP dependency
- Local-only communication

### Related Commands

```bash
SCREWDRIVER SCAN         # Find devices
SCREWDRIVER FLASH D1     # Provision device
MESH STATUS              # Network status
DEVICE LIST              # All devices
```

---

## Tier: Mixed (Tier 3 & 4)

- **Tier 4**: General communication methods
- **Tier 3**: Group-specific frequencies and codes

---

*Part of uDOS Knowledge Bank v1.0.2.0*
