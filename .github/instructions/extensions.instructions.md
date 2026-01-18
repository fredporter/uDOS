# Extensions Subsystem Instructions

> **Scope:** `applyTo: ["extensions/**"]`

---

## Extensions Architecture

**Extensions** are optional, composable feature packs for uDOS.

### Current Extensions

1. **API** (`extensions/api/`) — REST/WebSocket API server
2. **Transport** (`extensions/transport/`) — MeshCore, Audio, QR, NFC, Bluetooth

### Requirements

Each extension must have:

- `README.md` — Purpose, usage, dependencies
- `version.json` — Independent versioning
- Clear capability declarations
- No assumptions about always-on connectivity (unless explicitly stated)

---

## API Extension

### Responsibilities

- REST API endpoints
- WebSocket connections
- API documentation
- Request/response handling

### Non-Responsibilities

- ❌ Business logic (use Core services)
- ❌ Direct file manipulation
- ❌ Cloud integration (use Wizard)

### Current Version

API v1.1.0.0

### Structure

```
extensions/api/
├── routes/
│   ├── __init__.py
│   ├── files.py
│   ├── knowledge.py
│   ├── ai.py
│   └── ...
├── services/
├── websocket/
├── server.py
└── version.json
```

### Development

```bash
# Run API server
source .venv/bin/activate
python extensions/api/server.py

# Or use Dev Mode
./Dev-Mode.command
```

---

## Transport Extension

### Responsibilities

- MeshCore P2P networking
- Audio relay (acoustic packets)
- QR code relay
- NFC contact transfer
- Bluetooth Private (paired devices)
- Bluetooth Public (beacons only, **NO DATA**)

### Transport Policy (Non-Negotiable)

**Private Transports** (Commands + Data Allowed):
- MeshCore
- Bluetooth Private
- NFC
- QR Relay
- Audio Relay

**Public Signal Channels** (NO DATA EVER):
- Bluetooth Public — Beacons/presence ONLY

### Current Version

Transport v1.0.1.0

### Structure

```
extensions/transport/
├── meshcore/          # P2P mesh networking
├── audio/             # Acoustic data transfer
├── qr/                # QR code relay
├── policy.yaml        # Transport policy rules
├── validator.py       # Policy enforcement
└── version.json
```

### Logging Tags

- `[MESH]` — MeshCore operation
- `[BT-PRIV]` — Bluetooth Private
- `[BT-PUB]` — Bluetooth Public (signal only!)
- `[NFC]` — NFC contact
- `[QR]` — QR relay
- `[AUD]` — Audio transport

### Policy Validation

**ALWAYS** validate transport tier before sending:

```python
from extensions.transport.validator import validate_transport

if validate_transport('bluetooth_public', has_data=True):
    raise PolicyViolation("Bluetooth Public cannot carry data")
```

---

## Creating New Extensions

### Template Structure

```
extensions/my-extension/
├── README.md           # Required
├── version.json        # Required
├── __init__.py
├── services/
├── tests/
└── ...
```

### version.json Template

```json
{
  "$schema": "../../core/version.schema.json",
  "component": "my-extension",
  "name": "My Extension",
  "version": {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build": 0
  },
  "display": "v1.0.0.0",
  "channel": "alpha",
  "released": "2026-01-13",
  "description": "Extension purpose",
  "dependencies": {
    "core": ">=1.0.0.0"
  }
}
```

### README.md Template

```markdown
# My Extension

**Version:** v1.0.0.0  
**Status:** Alpha

## Purpose

[Description]

## Features

- Feature 1
- Feature 2

## Dependencies

- Core v1.0.0.0+
- [Other dependencies]

## Usage

[Instructions]

## Configuration

[Config details]

## Testing

[Test commands]
```

---

## Version Management

```bash
# Check all extension versions
python -m core.version check

# Bump extension version
python -m core.version bump <extension-name> patch
```

---

## Testing

```bash
# Run extension tests
pytest extensions/<extension-name>/tests/ -v

# Integration tests
pytest memory/tests/ -v
```

---

## References

- [AGENTS.md](../../AGENTS.md)
- [docs/_index.md](../../docs/_index.md)
- [extensions/README.md](../../extensions/README.md)
- [extensions/transport/policy.yaml](../../extensions/transport/policy.yaml)

---

*Last Updated: 2026-01-13*
