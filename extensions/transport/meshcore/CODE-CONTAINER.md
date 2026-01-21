# MeshCore Code Container

**Version:** Alpha v1.1.0.5+  
**Status:** 🟢 Active  
**Architecture:** Code Container (Wizard-managed)

---

## 📋 Overview

MeshCore is integrated as a **Code Container** - the official repository is cloned and maintained by Wizard Server, while uDOS layers its own transport wrapper on top.

### Code Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WIZARD SERVER (Realm B)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Code Container: MeshCore                                │    │
│  │  Source: github.com/meshcore-dev/MeshCore               │    │
│  │  Type: git clone (official repo)                        │    │
│  │  Location: extensions/cloned/meshcore/                  │    │
│  │  Update: git pull (Wizard-managed)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Package & Distribute                                    │    │
│  │  • QR relay for mesh configs                            │    │
│  │  • TCZ packaging for Tiny Core                          │    │
│  │  • Firmware builds for supported hardware               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
               (Private Transport: Mesh/QR/Audio)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    USER DEVICE (Realm A)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  extensions/cloned/meshcore/                             │    │
│  │  (Received via private transport from Wizard)           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  uDOS Extension Layer (Our Code)                        │    │
│  │  • extensions/transport/meshcore/__init__.py            │    │
│  │  • extensions/play/meshcore_device_manager.py           │    │
│  │  • extensions/play/services/meshcore_service.py         │    │
│  │  • core/commands/mesh_handler.py                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Code Container vs Custom Code

| Layer | Source | Maintained By | Updates |
|-------|--------|---------------|---------|
| **Container** | github.com/meshcore-dev/MeshCore | MeshCore Team | git pull (Wizard) |
| **Transport** | extensions/transport/meshcore/ | uDOS | version.json |
| **Service** | extensions/play/services/ | uDOS | version.json |
| **Handler** | core/commands/mesh_handler.py | uDOS | version.json |

**Rule:** Container code is **read-only** on user devices. All modifications go in uDOS layers.

---

## 📦 Container Management

### Wizard Server Commands

```bash
# Clone official repo (Wizard only - has web access)
PLUGIN CLONE meshcore https://github.com/meshcore-dev/MeshCore

# Update container
PLUGIN UPDATE meshcore

# Check container status
PLUGIN STATUS meshcore

# Package for distribution
PLUGIN PACKAGE meshcore --format tcz
```

### Container Manifest

**File:** `extensions/cloned/meshcore/container.json`

```json
{
  "container": {
    "id": "meshcore",
    "name": "MeshCore Mesh Networking",
    "type": "git",
    "source": "https://github.com/meshcore-dev/MeshCore",
    "ref": "main",
    "cloned_at": "2026-01-05T12:00:00Z",
    "last_update": "2026-01-05T12:00:00Z",
    "commit": "abc123..."
  },
  "policy": {
    "read_only": true,
    "auto_update": false,
    "update_channel": "wizard_only"
  },
  "distribution": {
    "transport": ["mesh", "qr"],
    "package_format": "tcz",
    "requires_wizard": true
  }
}
```

---

## 🔐 Transport Policy

From `extensions/transport/policy.yaml`:

```yaml
meshcore:
  type: private
  realm: user_mesh
  data_allowed: true
  commands_allowed: true
  max_packet_size: 65536
  container:
    source: "github.com/meshcore-dev/MeshCore"
    managed_by: wizard_server
    local_extensions_allowed: true
```

---

## 📂 Directory Structure

```
extensions/
├── cloned/
│   └── meshcore/                    # ← CODE CONTAINER (git clone)
│       ├── container.json           # Container manifest
│       ├── .git/                    # Git repo
│       ├── firmware/                # MeshCore firmware
│       ├── examples/                # Official examples
│       └── src/                     # MeshCore source
├── transport/
│   └── meshcore/                    # ← uDOS TRANSPORT LAYER
│       ├── __init__.py              # MeshTransport, MeshPacket
│       └── README.md                # This file
├── play/
│   ├── meshcore_device_manager.py   # Device management
│   └── services/
│       ├── meshcore_service.py      # Core service
│       └── meshcore_protocol.py     # Protocol definitions
└── setup/
    └── install_meshcore.py          # Installer script
```

---

## 🚀 Usage

### 1. Install Container (Wizard Server)

```bash
# On Wizard Server (has internet)
cd /path/to/udos
git clone https://github.com/meshcore-dev/MeshCore extensions/cloned/meshcore
python extensions/setup/install_meshcore.py --install
```

### 2. Distribute to Devices (Private Transport)

```bash
# Package for distribution
PLUGIN PACKAGE meshcore

# Send via QR (large file = multiple QR codes)
QR SEND distribution/meshcore-1.0.0.tcz

# Or via mesh network
MESH SEND device-id distribution/meshcore-1.0.0.tcz
```

### 3. Use on Device

```python
from extensions.transport.meshcore import MeshTransport, get_mesh_transport

# Get transport (wraps container code)
transport = get_mesh_transport()

# Scan for devices
devices = transport.scan(timeout=5.0)

# Send message
transport.send_message("target-id", "Hello from uDOS!")
```

---

## 🔄 Update Flow

```
1. MeshCore team pushes update to GitHub
                    ↓
2. Wizard Server detects update (scheduled check)
                    ↓
3. Wizard pulls: git -C extensions/cloned/meshcore pull
                    ↓
4. Wizard rebuilds TCZ package
                    ↓
5. Wizard notifies mesh devices of update
                    ↓
6. Devices request update via private transport
                    ↓
7. Devices install update offline
```

---

## 🛡️ Security Considerations

1. **No direct web access** - User devices never access GitHub directly
2. **Wizard verification** - Wizard Server verifies commits before distribution
3. **Read-only container** - Container code cannot be modified on user devices
4. **Private transport only** - Updates distributed via mesh/QR/audio, not internet
5. **Version pinning** - Can pin to specific commits for stability

---

## 📚 Related Files

- [WIZARD-PLUGIN-SYSTEM.md](../../dev/roadmap/WIZARD-PLUGIN-SYSTEM.md) - Plugin system spec
- [extensions/setup/install_meshcore.py](../setup/install_meshcore.py) - Installer
- [extensions/cloned/README.md](../cloned/README.md) - Cloned extensions guide
- [policy.yaml](policy.yaml) - Transport policy

---

*Last Updated: 2026-01-05*
