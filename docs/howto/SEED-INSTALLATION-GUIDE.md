---
uid: udos-installer-guide-20260130014500-UTC-L301AB02
title: Seed Installation & Initialization Guide
tags: [guide, installation, bootstrap, seed, infrastructure]
status: active
updated: 2026-02-06
---

# Seed Installation & Initialization Guide

**Last Updated:** 2026-02-06  
**Status:** Complete (v1.3+ seed flows)  
**Components:** Seed Installer, Bootstrap Handler, TUI Integration

---

## Overview

uDOS now provides multiple mechanisms to bootstrap framework seed data into fresh installations:

1. **Automatic Bootstrap** — Triggered on first TUI run (no user action needed)
2. **TUI SEED Command** — Manual control and status checking in the TUI
3. **Standalone Python Script** — For CI/CD, Docker, or headless installations
4. **Shell Installer** — Updated bin/install.sh with seed directory structure

---

## Automatic Bootstrap (First Run)

### How It Works

When you launch uDOS for the first time:

```bash
./start_udos.sh
# or
python uDOS.py
```

The system automatically detects missing `vault-md/bank/locations/locations.json` and:

1. Creates required directory structure (`vault-md/bank/locations/`, `memory/system/help/`, etc.)
2. Copies `core/framework/seed/locations-seed.json` to `vault-md/bank/locations/locations.json`
3. Installs additional seed data (timezones, templates, graphics)
4. Logs bootstrap progress

**Result:** Users can run the TUI immediately without manual setup.

---

## TUI SEED Command

### Interactive Control

Once the TUI is running, use the `SEED` command to control seed installation:

#### Check Status
```
[uCODE] > SEED
[uCODE] > SEED STATUS
```

Output:
```
Seed Installation Status:
----------------------------------------
Directories:       ✅
Locations seeded:  ✅
Timezones seeded:  ❌
Framework seed dir: ✅
```

#### Install/Reinstall Seeds
```
[uCODE] > SEED INSTALL
[uCODE] > SEED INSTALL --force    # Overwrite existing
```

Output:
```
✅ Directory structure created
✅ Locations seed installed
✅ Timezones seed installed
✅ Seed files installed (15 files)
```

#### Get Help
```
[uCODE] > SEED HELP
```

---

## Standalone Seed Installer Script

### Purpose

The `bin/install-seed.py` script enables:
- **CI/CD pipelines** — Bootstrap in automated deployments
- **Docker/Container builds** — Initialize seed before starting service
- **Headless installations** — No TUI interaction needed
- **Fresh installs** — Explicit seed installation without TUI

### Usage

#### Check Status
```bash
python bin/install-seed.py --status
```

#### Install Seeds (Current Directory)
```bash
python bin/install-seed.py
```

#### Install Seeds (Custom Root)
```bash
python bin/install-seed.py /path/to/udos
```

#### Reinstall (Force Overwrite)
```bash
python bin/install-seed.py --force
```

### Example Output

```
Bootstrapping uDOS Seed Data
========================================
✅ Directory structure created
✅ Locations seed installed
✅ Timezones seed installed
✅ Bank seeds installed (15 files)

✅ Seed installation complete!
```

---

## Shell Installer Integration

### Updated Directory Structure

The `bin/install.sh` script now creates seed-ready directory structure:

```bash
setup_user_directory() {
    # ... existing code ...
    
    # Create seed-ready directory structure
    mkdir -p "$udos_home/vault-md/bank/locations"
    mkdir -p "$udos_home/memory/system/help"
    mkdir -p "$udos_home/memory/system/templates"
    mkdir -p "$udos_home/memory/system/graphics/diagrams/templates"
    mkdir -p "$udos_home/memory/system/workflows"
}
```

### Installation Modes

All install modes now support seed initialization:

```bash
# Development mode (automatic bootstrap on first run)
./bin/install.sh --mode dev

# Core-only installation
./bin/install.sh --mode core

# Desktop installation
./bin/install.sh --mode desktop

# Wizard server installation
./bin/install.sh --mode wizard
```

---

## File Structure

### Seed Data Location

```
core/framework/seed/
├── locations-seed.json           # Minimal location database
├── timezones-seed.json           # Timezone seed data
└── bank/                          # Bank seed templates
    ├── help/                      # Help template seeds
    ├── templates/                 # Runtime template seeds
    └── graphics/diagrams/         # Diagram templates
```

### Installation Target

```
vault-md/bank/
├── locations/
│   ├── locations.json            # Installed from locations-seed.json
│   └── timezones.json            # Installed from timezones-seed.json
└── binders/                      # User binders (seeded as needed)

memory/system/
├── help/                         # Installed system templates
├── templates/                    # Installed system templates
└── graphics/                     # Installed system templates
```

---

## Implementation Details

### SeedInstaller Class

Location: `core/framework/seed_installer.py`

**Main Methods:**

| Method | Purpose |
|--------|---------|
| `__init__(framework_dir, memory_dir)` | Initialize with paths |
| `ensure_directories()` | Create vault-md/bank/ + memory/system/ structure |
| `install_locations_seed(force=False)` | Bootstrap locations data |
| `install_timezones_seed(force=False)` | Bootstrap timezone data |
| `install_bank_seeds(force=False)` | Copy bank seed files |
| `install_all(force=False)` | Install all seeds |
| `status()` | Check installation status |

**Error Handling:**

- Missing framework seed files → logged error, continues
- Directory creation failures → logged, returns False
- JSON validation → loaded and validated before copy
- Graceful degradation → incomplete seeds don't block system startup

### Bootstrap Hook in LocationService

Location: `core/location_service.py`

The `LocationService._bootstrap_from_seed()` method:

1. Detects missing `locations.json` on initialization
2. Imports and creates `SeedInstaller`
3. Ensures directories and installs location seed
4. Retries JSON load after bootstrap
5. Provides clear error messages if bootstrap fails

### SeedHandler TUI Command

Location: `core/commands/seed_handler.py`

Provides user-facing control:
- `SEED` / `SEED STATUS` — Show installation status
- `SEED INSTALL` — Bootstrap seeds (skip existing)
- `SEED INSTALL --force` — Reinstall (overwrite)
- `SEED HELP` — Show command help

Registered in `core/tui/dispatcher.py`

---

## Usage Examples

### Fresh Development Installation

```bash
# Clone and enter repo
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# First run (automatic bootstrap)
python uDOS.py

# Welcome! System is fully initialized
```

### Docker Installation

```dockerfile
FROM python:3.9-alpine

WORKDIR /opt/udos

# Copy source
COPY . .

# Create venv and install dependencies
RUN python -m venv .venv && \
    .venv/bin/pip install -r requirements.txt

# Bootstrap seed data
RUN .venv/bin/python bin/install-seed.py

# Run Wizard server
CMD [".venv/bin/python", "-m", "wizard.server"]
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Bootstrap uDOS seed
  run: python bin/install-seed.py

- name: Validate system
  run: python -m pytest core/tests/ -v
```

### Fresh System Reset

```
[uCODE] > DESTROY --reset-all --confirm
[uCODE] > SEED INSTALL
[uCODE] > STATUS
```

---

## Troubleshooting

### "Locations file not found" Error

**Cause:** Seed installer failed during bootstrap

**Solution:**

```bash
# Check status
python bin/install-seed.py --status

# Manually reinstall
python bin/install-seed.py --force

# Or from TUI:
[uCODE] > SEED INSTALL --force
```

### Missing Bank Seeds

**Cause:** `core/framework/seed/bank/` directory missing or incomplete

**Solution:**

```bash
# Verify framework structure
ls -la core/framework/seed/

# Check which seeds are missing
python bin/install-seed.py --status

# Reinstall
python bin/install-seed.py --force
```

### Permission Errors

**Cause:** User doesn't have write access to memory directory

**Solution:**

```bash
# Fix permissions
chmod 755 memory/system vault-md/bank
chmod 755 memory

# Or reinstall as correct user
python bin/install-seed.py --force
```

---

## Architecture Notes

### Why Bootstrap on First Run?

1. **Zero-Configuration** — Users don't need to remember manual steps
2. **Automatic Recovery** — Fresh TUI always has valid seed data
3. **CI/CD Friendly** — Containers automatically initialize on startup
4. **Backwards Compatible** — Existing installations unaffected

### Why Multiple Methods?

1. **Automatic** — Best for users and developers
2. **TUI Command** — Best for manual control and recovery
3. **Python Script** — Best for CI/CD and containers
4. **Shell Integration** — Best for system package managers

### Data Flow

```
User runs: python uDOS.py
    ↓
TUI initializes CommandDispatcher
    ↓
PanelHandler creates LocationService
    ↓
LocationService._load_from_json() called
    ↓
locations.json not found?
    ↓
_bootstrap_from_seed() triggered
    ↓
SeedInstaller.ensure_directories() creates structure
    ↓
SeedInstaller.install_locations_seed() copies seed
    ↓
Retry _load_from_json()
    ↓
✅ System ready!
```

---

## Related Documentation

- [Development Setup](../QUICKSTART.md) — Getting started guide
- [AGENTS.md](../AGENTS.md) — Development rules and boundaries
- [Framework README](../../core/framework/README.md) — Framework structure
- [LocationService](../../core/location_service.py) — Location data management

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-01-30 | Initial seed installer system |

---

**Maintainers:** uDOS Engineering  
**Status:** Production Ready  
**Last Review:** 2026-01-30
