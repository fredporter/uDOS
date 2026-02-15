# Transport Commands

> [!WARNING]
> Archived legacy page (v1.1). Transport/network command content here is not part of the canonical current Core command surface.
> Use `/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md` and Wizard docs for active command ownership.

> **Version:** Core v1.1.0.0

Commands for network management, mesh networking, and device pairing.

---

## NETWORK

Unified network management.

### Syntax

```bash
NETWORK [STATUS|SCAN|CONNECT|DISCONNECT]
```

### Examples

```bash
NETWORK               # Show network status
NETWORK STATUS        # Detailed status
NETWORK SCAN          # Scan for networks
NETWORK CONNECT wifi  # Connect to WiFi
NETWORK DISCONNECT    # Disconnect
```

---

## MESH

MeshCore P2P networking commands.

### Syntax

```bash
MESH [PEERS|SEND|BROADCAST|STATUS|JOIN|LEAVE]
```

### Subcommands

| Command             | Description           |
| ------------------- | --------------------- |
| `STATUS`            | Show mesh status      |
| `PEERS`             | List connected peers  |
| `SEND <peer> <msg>` | Send to specific peer |
| `BROADCAST <msg>`   | Send to all peers     |
| `JOIN <network>`    | Join mesh network     |
| `LEAVE`             | Leave current network |

### Examples

```bash
MESH                  # Show status
MESH STATUS
MESH PEERS            # List peers
MESH SEND node-123 "Hello"
MESH BROADCAST "System update"
MESH JOIN home-mesh
MESH LEAVE
```

### Notes

- MeshCore is the primary P2P transport
- Works offline without internet
- Part of Realm A (User Device Mesh)

---

## PAIR

Device pairing for mobile consoles and peripherals.

### Syntax

```bash
PAIR [CONSOLE|DEVICE|LIST|REMOVE|STATUS]
```

### Subcommands

| Command       | Description         |
| ------------- | ------------------- |
| `CONSOLE`     | Pair mobile console |
| `DEVICE`      | Pair generic device |
| `LIST`        | List paired devices |
| `REMOVE <id>` | Unpair device       |
| `STATUS`      | Pairing status      |

### Examples

```bash
PAIR CONSOLE          # Start console pairing
PAIR DEVICE           # Start device pairing
PAIR LIST             # Show paired devices
PAIR REMOVE phone-123
PAIR STATUS
```

### Pairing Process

1. Run `PAIR CONSOLE` on uDOS device
2. Scan QR code with mobile app
3. Confirm pairing on both devices
4. Devices now communicate via private transport

---

## TRANSPORT

Low-level transport management.

### Syntax

```bash
TRANSPORT [AUDIO|BLUETOOTH|NFC|QR] [subcommand]
```

### Audio Transport

```bash
TRANSPORT AUDIO ON       # Enable acoustic transport
TRANSPORT AUDIO OFF      # Disable
TRANSPORT AUDIO SEND "msg"
TRANSPORT AUDIO LISTEN
TRANSPORT AUDIO STATUS
```

### Bluetooth Transport

```bash
TRANSPORT BLUETOOTH ON
TRANSPORT BLUETOOTH OFF
TRANSPORT BLUETOOTH SCAN
TRANSPORT BLUETOOTH PAIR <device>
```

### NFC Transport

```bash
TRANSPORT NFC STATUS
TRANSPORT NFC READ
TRANSPORT NFC WRITE "data"
```

### QR Transport

```bash
TRANSPORT QR GENERATE "data"
TRANSPORT QR SCAN
```

---

## Transport Policy

uDOS enforces strict transport policies:

### Private Transports (Commands + Data)

| Transport         | Description         |
| ----------------- | ------------------- |
| MeshCore          | Primary P2P mesh    |
| Bluetooth Private | Paired devices only |
| NFC               | Physical contact    |
| QR Relay          | Visual transfer     |
| Audio Relay       | Acoustic packets    |

### Public Channels (Signal Only)

| Channel          | Allowed               |
| ---------------- | --------------------- |
| Bluetooth Public | Presence beacons ONLY |
| Never            | uDOS commands or data |

### Realm Rules

| Realm                 | Internet    | Use Case       |
| --------------------- | ----------- | -------------- |
| **A** (User Mesh)     | Never       | Daily use      |
| **B** (Wizard Server) | When needed | AI, web, email |

---

## SYNC

Synchronization between devices.

### Syntax

```bash
SYNC [STATUS|START|STOP|NOW]
```

### Examples

```bash
SYNC                  # Show sync status
SYNC STATUS
SYNC START            # Enable auto-sync
SYNC STOP             # Disable auto-sync
SYNC NOW              # Force immediate sync
```

### What Syncs

- Knowledge bank updates
- User preferences (opt-in)
- Bundle progress
- NOT: Private data, wellbeing, location

---

## Related

- [Vision - Transport Policy](VISION.md#transport-policy)
- [Groovebox](../groovebox/README.md) - Audio transport
- [Alpine](../tinycore/README.md) - Network setup (updated)

---

_Part of the [Command Reference](README.md)_
