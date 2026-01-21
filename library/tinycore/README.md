# TinyCore ISO Library

Local storage for TinyCore Linux ISO images. **Not tracked in git** - ISOs are downloaded on demand.

## Quick Start

```bash
# List available images
python -m wizard.library.tinycore.setup list

# Download TinyCore (default)
python -m wizard.library.tinycore.setup download tinycore

# Verify existing ISO
python -m wizard.library.tinycore.setup verify TinyCore-current.iso

# Create bootable USB (Linux/macOS only)
python -m wizard.library.tinycore.setup usb tinycore /dev/sdb
```

## Available Images

| Image | Size | Description |
|-------|------|-------------|
| `tinycore` | ~20MB | Base system + GUI (X/FLWM) |
| `core` | ~15MB | CLI only, no GUI |
| `coreplus` | ~150MB | Full installer with common TCZs |
| `tinycore64` | ~22MB | 64-bit TinyCore |
| `corepure64` | ~15MB | 64-bit CLI only |

## Directory Structure

```
wizard/library/tinycore/
├── README.md           # This file
├── setup.py            # Download/verify utility
├── __init__.py         # Python module init
├── TinyCore-current.iso   # ← Downloaded ISO (gitignored)
├── Core-current.iso       # ← Downloaded ISO (gitignored)
└── ...
```

## uDOS Integration

### From TUI (Dev Mode)

```
WIZARD ISO LIST          # List available images
WIZARD ISO DOWNLOAD tinycore    # Download
WIZARD ISO VERIFY TinyCore-current.iso
```

### From Python

```python
from wizard.library.tinycore.setup import TinyCoreSetup

setup = TinyCoreSetup()

# Get path to ISO (auto-downloads if missing)
iso_path = setup.get_iso_path("tinycore")

# Verify checksum
setup.verify(iso_path)
```

## Checksums

SHA256 checksums are stored in `../os-images/checksums.json` and updated automatically after download.

## Why TinyCore?

uDOS is designed as an overlay OS for TinyCore Linux because:

1. **Minimal footprint** - ~15-20MB base system
2. **RAM-based** - System runs entirely in RAM
3. **TCZ packages** - Clean extension management
4. **Persistent overlay** - User data survives reboots
5. **Offline first** - No internet required

## Creating a uDOS + TinyCore Installation

1. Download TinyCore ISO
2. Create bootable USB
3. Boot target machine from USB
4. Run uDOS installer:

```bash
# From live TinyCore environment
tce-load -wi python3.8
wget https://raw.githubusercontent.com/your-repo/uDOS/main/install.sh
chmod +x install.sh
./install.sh core
```

---

*See [distribution/README.md](../../../distribution/README.md) for TCZ packaging architecture.*
