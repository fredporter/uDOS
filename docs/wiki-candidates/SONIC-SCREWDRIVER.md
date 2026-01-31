---
uid: udos-wiki-sonic-20260125160000-UTC-L300AB05
title: Sonic Screwdriver Protocol
tags: [wiki, guide, experimental]
status: draft
updated: 2026-01-25
spec: wiki_spec_obsidian.md
---

# Sonic Screwdriver Protocol

**Version:** 1.1.0 (Draft)  
**Status:** Specification (Summary)  
**Last Updated:** 2026-01-25

## Purpose

**Sonic Screwdriver** is a device catalog and installation guide system that identifies hardware configurations and recommends the optimal method for reflashing / provisioning them with Alpine Linux + uDOS.

It is maintained as a public database (`/sonic/datasets/`) and distributed via Wizard Server.

## Core Responsibilities

1. **Device Catalog:** Track hardware variants (vendor, model, year, CPU, GPU, BIOS, TPM, USB boot capability)
2. **Reflashing Guidance:** Identify the best method for each device (Ventoy, UEFI, legacy BIOS, direct imaging)
3. **Driver Sourcing:** Link devices to online driver repositories and firmware downloads
4. **Beacon Integration:** Recommend routers suitable for use as uDOS beacon nodes

## Data Structure

### Sonic Devices Database

**Location:** `/sonic/datasets/sonic-devices.table.md` (human-editable Markdown table)

**Schema:** JSON (`sonic-devices.schema.json`)

**Storage:** SQLite (`memory/sonic/sonic-devices.db`)

### Table Columns

| Field               | Type       | Purpose                                                       |
| ------------------- | ---------- | ------------------------------------------------------------- |
| `id`                | string     | Unique device identifier (e.g., `macbookpro-2012`)            |
| `vendor`            | string     | Manufacturer (Apple, Dell, Lenovo, Raspberry Pi)              |
| `model`             | string     | Product name                                                  |
| `variant`           | string     | Specific SKU or configuration (e.g., `13" Mid 2012`)          |
| `year`              | integer    | Release year                                                  |
| `cpu`               | string     | CPU model                                                     |
| `gpu`               | string     | GPU / iGPU                                                    |
| `ram_gb`            | integer    | Maximum RAM capacity                                          |
| `storage_gb`        | integer    | Storage capacity                                              |
| `bios`              | enum       | UEFI / Legacy / UEFI+Legacy                                   |
| `secure_boot`       | enum       | yes / no / unknown                                            |
| `tpm`               | enum       | yes / no / unknown                                            |
| `usb_boot`          | enum       | yes / no / unknown                                            |
| `ventoy`            | enum       | works / issues / unknown                                      |
| `reflash_potential` | enum       | high / medium / low / unknown                                 |
| `methods`           | JSON array | Recommended flashing methods: `["Ventoy", "UEFI", "dd", ...]` |
| `notes`             | string     | Device-specific guidance / caveats                            |
| `sources`           | JSON array | Links to driver repos, firmware, documentation                |
| `last_seen`         | date       | Last verified working date                                    |
| `windows10_boot`    | enum       | none / install / wtg / unknown                                |
| `media_mode`        | enum       | none / htpc / retro / unknown                                 |
| `udos_launcher`     | enum       | none / basic / advanced / unknown                             |

## Device Categories

### Recommended for Beacon Deployment

Devices with:

- ✅ Stable USB boot support
- ✅ Moderate CPU (sufficient for Wi-Fi router + Web portal)
- ✅ At least 512 MB RAM
- ✅ Large enough storage for Alpine + persistence (~2 GB)

**Examples:**

- TP-Link TL-WR841N
- Ubiquiti EdgeRouter X
- OpenWrt-compatible home routers
- Old laptop repurposed as router

### Recommended for Alpine Core Tier 2 (Desktop Deployment)

Devices with:

- ✅ Working Wayland driver (Intel iGPU, AMD, NVIDIA preferred)
- ✅ USB 3.0 support for faster boot/storage
- ✅ UEFI firmware (cleaner setup)
- ✅ TPM 2.0 (for future security features)

**Examples:**

- Modern Intel / AMD laptops (2015+)
- MacBooks with native Mesa support (newer generations)
- Desktop systems with dedicated GPUs

## API Endpoints (Wizard Server)

### GET `/api/v1/sonic/devices`

**Query params:**

- `vendor` (string, optional) — Filter by vendor
- `reflash_potential` (enum, optional) — high / medium / low
- `usb_boot` (boolean, optional) — Filter by USB boot support
- `ventoy` (enum, optional) — works / issues
- `limit` (int, 1–1000, default 100)
- `offset` (int, default 0)

**Response:**

```json
{
  "total": 1250,
  "devices": [
    {
      "id": "dell-optiplex-9020",
      "vendor": "Dell",
      "model": "OptiPlex 9020",
      "year": 2013,
      "reflash_potential": "high",
      "usb_boot": "yes",
      "ventoy": "works",
      "methods": ["Ventoy", "UEFI", "dd"],
      "notes": "Excellent for Alpine. BIOS update may be needed for USB 3.0 boot.",
      "sources": ["https://dell.com/support/9020", ...]
    }
  ]
}
```

### GET `/api/v1/sonic/devices/{device_id}`

Fetch details for a specific device.

### GET `/api/v1/sonic/schema`

Return JSON Schema for device records.

### GET `/api/v1/sonic/table`

Return raw Markdown table (for local storage / offline access).

### GET `/api/v1/sonic/stats`

**Response:**

```json
{
  "total_devices": 1250,
  "by_reflash_potential": {
    "high": 450,
    "medium": 600,
    "low": 150,
    "unknown": 50
  },
  "usb_boot_capable": 900,
  "ventoy_compatible": 750,
  "unique_vendors": 42
}
```

## Integration Points

### Beacon Setup Wizard

When user configures a router as beacon:

1. Query Sonic: "What routers work best for beacon?"
2. Filter: `reflash_potential: high`, `usb_boot: yes`
3. Display recommendations + setup guides
4. Link to device-specific drivers / firmware

### Device Reflashing Guidance

When user wants to flash Alpine to hardware:

1. Query Sonic: "I have a Dell OptiPlex 9020"
2. Fetch: methods, notes, driver sources
3. Display step-by-step instructions:
   - Boot from USB
   - Flash Alpine ISO (Ventoy vs. direct dd)
   - Enable UEFI (if recommended)
   - Install to internal storage

### Online Driver Lookup

Link to manufacturer support pages:

- **Dell:** `https://dell.com/support/{model}`
- **Lenovo:** `https://pcsupport.lenovo.com/{model}`
- **Apple:** `https://support.apple.com/{model}`
- **Generic:** Link to manufacturer's download page

## Maintenance Workflow

### Adding a Device

1. Test Alpine + uDOS on hardware
2. Record: vendor, model, variant, CPU, GPU, BIOS, TPM, USB boot result, Ventoy result
3. Add row to `sonic-devices.table.md`
4. Recompile database: `sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql`
5. Bump version if significant changes
6. Commit to `/sonic/datasets/`

### Verifying Device Status

1. Periodically re-test devices (`last_seen` field)
2. Update notes if methods change (e.g., new BIOS breaks legacy boot)
3. Flag "unknown" devices for community testing
4. Archive obsolete devices (move to "historical" table)

## Distribution

**Public availability:** Via Wizard Server `/api/v1/sonic/*`

**Offline access:** Download Markdown table + JSON from distribution system

**Live updates:** Wizard can fetch latest Sonic DB from uDOS package repository

## Non-Goals

- ❌ Not a complete hardware database (like ARK or SpecOut)
- ❌ Not a price tracker or reseller guide
- ❌ Not a benchmark database
- ❌ Not a compatibility matrix for every Linux distro

**Focus:** Devices + Alpine + uDOS + reflashing methods only.

## References

- [BEACON-PORTAL.md](BEACON-PORTAL.md) — Beacon router configuration
- [ALPINE-CORE.md](ALPINE-CORE.md) — Alpine deployment target
- [sonic/datasets/README.md](../../sonic/datasets/README.md) — Dataset documentation
- [wizard/routes/sonic_routes.py](../../wizard/routes/sonic_routes.py) — API implementation

---

**Status:** Specification v1.0.0 ready for data collection  
**Maintenance:** Community-driven; distributed via package system
