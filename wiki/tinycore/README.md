# TinyCore Distribution

> **Version:** Core v1.0.0.64

uDOS is designed as an overlay OS for Tiny Core Linux, providing a complete offline-first system on minimal hardware.

---

## Overview

### Why Tiny Core?

- **Minimal**: ~21MB base system
- **RAM-based**: Runs entirely from RAM
- **Persistent Extensions**: TCZ packages
- **Ancient Hardware**: Works on 128MB RAM
- **Offline-First**: Perfect for air-gapped systems

### uDOS as Overlay

```
┌─────────────────────────────────────────┐
│              uDOS Layer                 │
│  (Python venv, TUI, Knowledge Bank)     │
├─────────────────────────────────────────┤
│           Tiny Core Linux               │
│  (Base system, TCZ extensions)          │
├─────────────────────────────────────────┤
│              Hardware                   │
│  (x86, x86_64, ARM)                     │
└─────────────────────────────────────────┘
```

---

## Installation

### Requirements

| Component | Minimum | Recommended |
| --------- | ------- | ----------- |
| RAM | 128MB | 512MB+ |
| Storage | 256MB | 2GB+ |
| CPU | i486+ | Any modern |

### Quick Install

```bash
# From running Tiny Core
tce-load -wi python3.11
tce-load -wi git

# Clone uDOS
git clone https://github.com/user/udos.git
cd udos

# Install
./install.sh
```

### Manual Install

```bash
# 1. Install Python dependencies
tce-load -wi python3.11
tce-load -wi python3.11-pip

# 2. Create venv
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Configure
cp core/config/settings.template.json core/config/settings.json

# 5. Run
./start_udos.sh
```

---

## TCZ Package Management

### INSTALL Command

```bash
# Install TCZ package
INSTALL nano
INSTALL python3.11-pip

# List installed
INSTALL LIST

# Search packages
INSTALL SEARCH editor

# Remove package
INSTALL REMOVE nano
```

### STACK Command

Capability-based installation for common workflows:

```bash
# Add capabilities
STACK ADD meshcore      # MeshCore P2P
STACK ADD audio         # Audio synthesis
STACK ADD wizard        # Wizard server deps

# Show available stacks
STACK LIST

# Check current
STACK STATUS
```

### Stack Definitions

| Stack | Packages | Description |
| ----- | -------- | ----------- |
| `meshcore` | meshtastic, bluetooth | P2P mesh networking |
| `audio` | pygame, portaudio | Groovebox audio |
| `wizard` | openssl, curl | Wizard server |
| `dev` | git, gcc | Development tools |

---

## Persistence

### Tiny Core Persistence

```bash
# Backup changes
filetool.sh -b

# List persistent files
cat /opt/.filetool.lst
```

### uDOS Persistence

```
/mnt/sda1/
├── tce/                    # TCZ extensions
│   └── optional/
├── udos/                   # uDOS installation
│   ├── .venv/
│   ├── core/
│   ├── memory/             # User data
│   └── knowledge/
└── mydata.tgz             # Tiny Core backup
```

### Persistent Paths

Add to `/opt/.filetool.lst`:

```
/mnt/sda1/udos/memory
/mnt/sda1/udos/core/config/settings.json
```

---

## BUILD Command

Create offline installation packages:

```bash
# Build installable package
BUILD OFFLINE

# Build ISO image
BUILD ISO

# Build USB installer
BUILD USB /dev/sdb
```

### Offline Package Contents

```
udos-offline-v1.0.0.64.tar.gz
├── udos/                   # Full uDOS tree
├── tcz/                    # Required TCZ packages
│   ├── python3.11.tcz
│   └── ...
├── install-offline.sh      # Offline installer
└── README.md               # Instructions
```

---

## Boot Configuration

### bootlocal.sh

Auto-start uDOS on boot:

```bash
#!/bin/sh
# /opt/bootlocal.sh

# Start uDOS TUI
/mnt/sda1/udos/start_udos.sh &
```

### Kiosk Mode

For dedicated uDOS terminals:

```bash
# In bootlocal.sh
export UDOS_KIOSK=1
/mnt/sda1/udos/start_udos.sh
```

---

## Hardware Profiles

### Minimal (128MB RAM)

```json
{
  "profile": "minimal",
  "tui": {
    "rainbow_splash": false,
    "syntax_highlight": false
  },
  "features": {
    "groovebox": false,
    "wizard": false
  }
}
```

### Standard (512MB RAM)

```json
{
  "profile": "standard",
  "tui": {
    "rainbow_splash": true,
    "syntax_highlight": true
  },
  "features": {
    "groovebox": true,
    "wizard": false
  }
}
```

### Wizard (2GB+ RAM)

```json
{
  "profile": "wizard",
  "features": {
    "groovebox": true,
    "wizard": true,
    "ollama": true
  }
}
```

---

## Troubleshooting

### Python Not Found

```bash
# Install Python
tce-load -wi python3.11

# Verify
python3.11 --version
```

### No Persistence

```bash
# Check mount
mount | grep sda

# Mount persistent storage
sudo mount /dev/sda1 /mnt/sda1

# Add to /etc/fstab for auto-mount
```

### Out of RAM

```bash
# Check RAM usage
free -m

# Use swap
tce-load -wi swap
sudo swapon /mnt/sda1/swapfile
```

### TCZ Errors

```bash
# Update mirror
tce-load -wi mirrors
tce-mirror

# Clear cache
rm /tmp/tce/optional/*.tcz
```

---

## Creating Custom Images

### ISO with uDOS

```bash
# Install remaster tools
tce-load -wi advcomp
tce-load -wi cdrtools

# Create remaster
./scripts/build-iso.sh

# Output: distribution/udos-tinycore.iso
```

### USB Image

```bash
# Create bootable USB
./scripts/build-usb.sh /dev/sdb

# Or use dd
dd if=distribution/udos.img of=/dev/sdb bs=4M
```

---

## Related

- [INSTALL Command](commands/system.md#install)
- [STACK Command](commands/system.md#stack)
- [BUILD Command](commands/system.md#build)
- [Offline-First](../VISION.md#offline-first)

---

*Part of the [uDOS Wiki](README.md)*
