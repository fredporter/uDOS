# uDOS TCZ Packaging Architecture

**Version:** Alpha v1.0.3.0+  
**Status:** Implementation Ready

This document defines the TinyCore Extension (TCZ) packaging system for uDOS distribution.

---

## 📦 Package Types

### Core Packages

| Package | Contents | Size | Required |
|---------|----------|------|----------|
| `udos-core.tcz` | TUI, uPY runtime, base commands | ~5MB | Yes |
| `udos-api.tcz` | REST/WebSocket API server | ~2MB | Optional |
| `udos-knowledge.tcz` | Knowledge bank (markdown) | ~10MB | Optional |

### Extension Packages

| Package | Contents | Size | Dependencies |
|---------|----------|------|--------------|
| `udos-groovebox.tcz` | MML music production | ~3MB | udos-core |
| `udos-transport.tcz` | MeshCore, QR, Audio relay | ~4MB | udos-core |
| `udos-wizard.tcz` | AI providers, web access | ~8MB | udos-core, udos-api |
| `udos-tauri.tcz` | Desktop Tauri app | ~50MB | udos-core, udos-api |

### Voice Packages (Wizard Library)

| Package | Contents | Size | Dependencies |
|---------|----------|------|--------------|
| `udos-voice-piper.tcz` | Piper TTS engine | ~15MB | udos-core |
| `udos-voice-handy.tcz` | Handy STT engine | ~20MB | udos-core |
| `udos-voice-models.tcz` | Voice models (separate) | ~500MB+ | piper/handy |

---

## 🏗️ TCZ Structure

### Standard TCZ Layout

```
udos-core.tcz/
├── opt/
│   └── udos/
│       ├── core/                 # Python core modules
│       │   ├── __init__.py
│       │   ├── commands/         # Command handlers
│       │   ├── services/         # Core services
│       │   ├── ui/               # TUI components
│       │   └── runtime/          # uPY interpreter
│       ├── bin/                  # Executables
│       │   ├── udos             # Main entry point
│       │   └── upy              # uPY script runner
│       └── lib/                  # Python libraries
│           └── python3.11/
│               └── site-packages/
├── etc/
│   └── udos/
│       └── system.conf          # System defaults
└── usr/
    └── share/
        ├── applications/
        │   └── udos.desktop     # Desktop entry
        └── doc/
            └── udos/
                └── README.md
```

### Dependency File (.dep)

```
# udos-groovebox.tcz.dep
udos-core.tcz
python3.11.tcz
```

### Info File (.info)

```
Title:          udos-core
Description:    uDOS TUI and uPY Runtime
Version:        1.0.0.34
Author:         uDOS Team
Original-site:  https://github.com/udos-project/udos
Copying-policy: MIT
Size:           5.2M
Extension_by:   uDOS Wizard Server
Comments:       Offline-first knowledge system
Change-log:     Initial release
Current:        1.0.0.34
```

---

## 🔧 Build Process

### 1. Prepare Source

```bash
# Create build directory
mkdir -p distribution/build/udos-core

# Copy core files
cp -r core distribution/build/udos-core/opt/udos/core
cp -r bin distribution/build/udos-core/opt/udos/bin
```

### 2. Create TCZ

```bash
# Build squashfs
mksquashfs distribution/build/udos-core \
    distribution/udos-core.tcz \
    -b 4096 -no-xattrs -noappend

# Generate md5
md5sum distribution/udos-core.tcz > distribution/udos-core.tcz.md5.txt

# Create dependency file
echo "python3.11.tcz" > distribution/udos-core.tcz.dep

# Create info file
cat > distribution/udos-core.tcz.info << EOF
Title:          udos-core
Description:    uDOS TUI and uPY Runtime
Version:        $(python -m core.version show core)
Author:         uDOS Team
Original-site:  https://github.com/udos-project/udos
Copying-policy: MIT
Size:           $(du -h distribution/udos-core.tcz | cut -f1)
Extension_by:   uDOS Wizard Server
Comments:       Offline-first knowledge system
Current:        $(python -m core.version show core)
EOF
```

### 3. Install on TinyCore

```bash
# Copy to tce directory
cp distribution/udos-core.tcz /mnt/sda1/tce/optional/

# Add to onboot.lst for persistence
echo "udos-core.tcz" >> /mnt/sda1/tce/onboot.lst

# Load immediately
tce-load -i udos-core.tcz
```

---

## 📋 Package Manifest

### distribution/manifest.json

```json
{
  "version": "1.0.0.34",
  "build_date": "2026-01-05T12:00:00Z",
  "packages": {
    "udos-core": {
      "version": "1.0.0.34",
      "size": "5.2M",
      "md5": "abc123...",
      "dependencies": ["python3.11"],
      "required": true
    },
    "udos-api": {
      "version": "1.0.0.1",
      "size": "2.1M",
      "md5": "def456...",
      "dependencies": ["udos-core"],
      "required": false
    },
    "udos-groovebox": {
      "version": "1.0.0.1",
      "size": "3.4M",
      "md5": "ghi789...",
      "dependencies": ["udos-core"],
      "required": false
    }
  },
  "profiles": {
    "minimal": ["udos-core"],
    "standard": ["udos-core", "udos-api", "udos-knowledge"],
    "full": ["udos-core", "udos-api", "udos-knowledge", "udos-groovebox", "udos-transport"],
    "wizard": ["udos-core", "udos-api", "udos-wizard", "udos-transport"]
  }
}
```

---

## 🚀 Distribution Workflow

### Wizard Server Build Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 WIZARD SERVER (Has Web Access)              │
│                                                             │
│   1. Pull latest code from git                              │
│   2. Run tests                                              │
│   3. Build TCZ packages                                     │
│   4. Generate manifests and checksums                       │
│   5. Sign packages (optional)                               │
│   6. Store in wizard/library/packages/                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
              (Private Transport Only)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    USER DEVICE (Offline)                    │
│                                                             │
│   1. Request package via mesh/QR/audio                      │
│   2. Verify checksum                                        │
│   3. Install TCZ                                            │
│   4. Update local manifest                                  │
└─────────────────────────────────────────────────────────────┘
```

### TUI Distribution Commands

```bash
# On Wizard Server
PACKAGE BUILD core                    # Build udos-core.tcz
PACKAGE BUILD all                     # Build all packages
PACKAGE LIST                          # List available packages
PACKAGE SIGN udos-core.tcz            # Sign with GPG (optional)

# On User Device
INSTALL udos-groovebox                # Request package from mesh
INSTALL --profile standard            # Install standard profile
UPDATE                                # Check for updates
UPDATE --apply                        # Apply available updates
```

---

## 🔐 Security

### Package Verification

1. **MD5 Checksum** - Basic integrity check
2. **SHA256 Checksum** - Stronger integrity
3. **GPG Signature** - Optional authenticity verification

### Trust Model

- Packages only from known Wizard Servers
- Private transport only (never direct internet on user devices)
- Version pinning for critical systems

---

## 📁 Directory Structure

```
distribution/
├── build/                    # Build working directory
│   ├── udos-core/
│   ├── udos-api/
│   └── ...
├── packages/                 # Built TCZ packages
│   ├── udos-core.tcz
│   ├── udos-core.tcz.dep
│   ├── udos-core.tcz.info
│   ├── udos-core.tcz.md5.txt
│   └── ...
├── manifest.json             # Package manifest
├── checksums.sha256          # All package checksums
└── README.md                 # This file
```

---

## 🛠️ Build Scripts

### wizard/tools/package_builder.py

Main package builder - see implementation in `wizard/tools/package_builder.py`

### Quick Build

```bash
# Build single package
python -m wizard.tools.package_builder build core

# Build all packages
python -m wizard.tools.package_builder build all

# Create distribution bundle
python -m wizard.tools.package_builder bundle standard
```

---

*Last Updated: 2026-01-05*
*Alpha v1.0.3.0+*
