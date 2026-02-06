---
uid: udos-guide-tech-20260129131300-UTC-L300AB77
title: uDOS-Compatible Devices - Sonic Screwdriver Library
tags: [guide, knowledge, tech]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# uDOS-Compatible Devices - Sonic Screwdriver Library

**Last Updated:** 2026-01-29
**Source:** `/sonic/` device library

---

## Overview

This directory references **flashable devices** from the Sonic Screwdriver library that are compatible with uDOS. All device specifications, firmware, and setup guides live in the `/sonic/` directory.

**Purpose:**
- Device catalog for uDOS ecosystem
- Flashable hardware references
- Setup and provisioning guides
- Firmware compatibility matrix

---

## Device Categories

### 1. Sonic Screwdriver (Primary Device)

**Location:** `/sonic/docs/specs/`

The Sonic Screwdriver is the primary portable device for uDOS:
- **USB flash drive** form factor
- Bootable Alpine Linux (uDOS Core)
- Persistent storage for user data
- Mesh network capable
- Multiple boot modes (Wizard, Kodi, RetroArch)

**Specifications:**
- [Sonic Screwdriver v1.0.1](/sonic/docs/specs/sonic-screwdriver-v1.0.1.md)
- [Sonic Screwdriver v1.1.0](/sonic/docs/specs/sonic-screwdriver-v1.1.0.md)

**Setup Guides:**
- [USB Setup Guide](/sonic/docs/02-usb-setup.md)
- [Ubuntu Wizard Mode](/sonic/docs/05-ubuntu-wizard.md)
- [uDOS Core Integration](/sonic/docs/03-udos-core.md)

---

### 2. MeshCore Devices

**Location:** `/sonic/datasets/`

MeshCore is the P2P mesh network backbone for device-to-device communication:
- LoRa-based mesh networking
- Bluetooth Low Energy
- Wi-Fi Direct
- NFC pairing

**Device Catalog:**
- [Sonic Devices Table](/sonic/datasets/sonic-devices.table.md)

**Setup:**
- [MeshCore Setup](/knowledge/tech/devices/meshcore.md) (internal reference)

---

### 3. Beacon Portal Devices

**Coming Soon**

Wi-Fi access point devices for local network infrastructure:
- 2.4GHz and 5GHz support
- Captive portal for device registration
- VPN tunnel to Wizard server
- Plugin caching and distribution

**Specifications:** (in development)
- See [BEACON-PORTAL.md](/docs/wiki/BEACON-PORTAL.md)

---

### 4. Retroarch/Gaming Devices

**Location:** `/sonic/docs/`

Gaming-capable devices that can run RetroArch:
- Raspberry Pi configurations
- Steam Deck integration
- Handheld emulation devices

**Guides:**
- [RetroArch Single Profile Netplay](/sonic/docs/retroarch-single-profile-netplay.md)
- [Sonic Stick Kodi Launcher](/sonic/docs/sonic-stick-kodi-launcher-flow-and-modes.md)

---

### 5. Media Center Devices

**Location:** `/sonic/docs/`

Kodi-based media center configurations:
- TV/monitor displays
- Local media playback
- Streaming integration

**Guides:**
- [Sonic Stick Media Addon](/sonic/docs/sonic-stick-media-addon-brief.md)
- [WantMyMTV Kiosk Wrapper](/sonic/docs/wantmymtv-kiosk-wrapper-spec.md)

---

## Firmware & Flashing

**Location:** `/sonic/payloads/`

Pre-built firmware images and flashing tools:
- Alpine Linux base images
- uDOS Core installations
- Kodi/RetroArch payloads

**Flashing Guide:**
- [Overview](/sonic/docs/01-overview.md)
- [Local Drives Setup](/sonic/docs/06-local-drives.md)

---

## Device Provisioning

**Location:** `/sonic/scripts/`

Scripts for setting up new devices:
- Initial flash
- Wi-Fi configuration
- User profile setup
- Mesh network pairing

**Automation:**
- [Sonic Scripts](/sonic/scripts/)

---

## UI Themes & Configuration

**Location:** `/sonic/ui/`

Visual themes and UI configurations for devices:
- Kodi skins
- RetroArch themes
- uDOS TUI color schemes

**Customization:**
- [UI README](/sonic/ui/README.md)

---

## Compatibility Matrix

| Device Type | Alpine Linux | uDOS Core | MeshCore | RetroArch | Kodi |
|------------|--------------|-----------|----------|-----------|------|
| Sonic Screwdriver (USB) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Raspberry Pi 4 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Raspberry Pi Zero W | ✅ | ⚠️ Limited | ✅ | ❌ | ⚠️ Basic |
| Steam Deck | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generic x86_64 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Beacon Portal (RPi) | ✅ | ⚠️ Server only | ✅ | ❌ | ❌ |

---

## Quick Reference

### Get Device Info
```bash
# From uDOS TUI
DEVICE INFO

# From sonic directory
cat /sonic/datasets/sonic-devices.table.md
```

### Flash New Device
```bash
# Navigate to sonic directory
cd /path/to/uDOS/sonic

# Run flash script
./scripts/flash-sonic-screwdriver.sh /dev/sdX
```

### Update Firmware
```bash
# From uDOS TUI
REPAIR --upgrade-device

# Or manually
cd /sonic/payloads
sudo dd if=sonic-latest.img of=/dev/sdX bs=4M status=progress
```

---

## Development & Testing

**Location:** `/sonic/core/`

Core device management code:
- Device detection
- Firmware validation
- Update mechanisms

**Testing:**
- Run device tests from `/sonic/core/tests/`

---

## Related Documentation

- [SONIC-SCREWDRIVER.md](/docs/wiki/SONIC-SCREWDRIVER.md) — Device catalog spec
- [BEACON-PORTAL.md](/docs/wiki/BEACON-PORTAL.md) — Wi-Fi infrastructure
- [Sonic Roadmap](/sonic/docs/roadmap.md) — Future device plans
- [Sonic Changelog](/sonic/CHANGELOG.md) — Version history

---

## Contributing

To add a new device to the Sonic library:

1. Create device spec in `/sonic/docs/specs/`
2. Add entry to `/sonic/datasets/sonic-devices.table.md`
3. Create setup guide in `/sonic/docs/`
4. Add firmware payload to `/sonic/payloads/`
5. Update this README with new device category

---

**Status:** Active Reference
**Source Library:** `/sonic/` (uDOS-sonic repository)
**Last Device Added:** Sonic Screwdriver v1.1.0 (2026-01-26)
