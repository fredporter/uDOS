---
uid: udos-seed-quick-ref-20260130015100-UTC-L301AB04
title: Seed Installer Quick Reference
tags: [guide, quick-reference, installer, development]
status: living
updated: 2026-01-30
---

# Seed Installer Quick Reference

**TL;DR version of [SEED-INSTALLATION-GUIDE.md](../howto/SEED-INSTALLATION-GUIDE.md)**

---

## For Users

### First Run (No Action Needed!)
```bash
python uDOS.py  # Automatically bootstraps seed data
```

### Check Status
```
[uCODE] > SEED
[uCODE] > SEED STATUS
```

### Reinstall Seeds
```
[uCODE] > SEED INSTALL
[uCODE] > SEED INSTALL --force    # Overwrite
```

### Get Help
```
[uCODE] > SEED HELP
```

---

## For Developers

### Test Seed Installation
```bash
python -c "from core.framework.seed_installer import SeedInstaller; \
    s = SeedInstaller(); \
    success, msgs = s.install_all(force=True); \
    print('\n'.join(msgs))"
```

### Check Status Programmatically
```python
from core.framework.seed_installer import SeedInstaller

installer = SeedInstaller()
status = installer.status()
print(f"Locations seeded: {status['locations_seeded']}")
```

### Bootstrap in Code
```python
from core.framework.seed_installer import bootstrap_seed

success, messages = bootstrap_seed(force=False)
if success:
    print("✅ Seeds installed")
else:
    print("❌ Installation failed")
```

---

## For CI/CD

### Status Check
```bash
python bin/install-seed.py --status
```

### Fresh Install
```bash
python bin/install-seed.py /opt/udos
```

### Force Reinstall
```bash
python bin/install-seed.py /opt/udos --force
```

### In Docker
```dockerfile
RUN python bin/install-seed.py
```

---

## In shell/install.sh

Seed directories created during installation:
```bash
mkdir -p "$udos_home/memory/bank/locations"
mkdir -p "$udos_home/memory/system/help"
mkdir -p "$udos_home/memory/system/templates"
mkdir -p "$udos_home/memory/system/graphics/diagrams/templates"
mkdir -p "$udos_home/memory/system/workflows"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `FileNotFoundError: locations.json` | `SEED INSTALL` in TUI or `python bin/install-seed.py --force` |
| Missing bank seeds | Check `core/framework/seed/bank/` exists, then `SEED INSTALL --force` |
| Permission denied | `chmod 755 memory/system memory/bank && SEED INSTALL --force` |
| Partial installation | `python bin/install-seed.py --status` to check what's missing |

---

## Key Files

| File | Purpose |
|------|---------|
| `core/framework/seed_installer.py` | Core implementation |
| `core/commands/seed_handler.py` | TUI command |
| `bin/install-seed.py` | Standalone script |
| `core/framework/seed/` | Seed data files |

---

## What Gets Seeded

| Source | Target | Size |
|--------|--------|------|
| `core/framework/seed/locations-seed.json` | `memory/bank/locations/locations.json` | 2KB |
| `core/framework/seed/timezones-seed.json` | `memory/bank/locations/timezones.json` | 2KB |
| `core/framework/seed/bank/*` | `memory/system/*` | 115 files |

---

## Key Methods

**SeedInstaller class:**
- `ensure_directories()` — Create structure
- `install_locations_seed()` — Install location data
- `install_timezones_seed()` — Install timezone data
- `install_bank_seeds()` — Install templates
- `install_all()` — Everything at once
- `status()` — Check completeness

---

## Integration Points

- **LocationService** — Auto-bootstrap on first load
- **CommandDispatcher** — `SEED` command registration
- **shell/install.sh** — Directory structure creation
- **uDOS.py** — Transparent startup flow

---

**Full Guide:** [SEED-INSTALLATION-GUIDE.md](SEED-INSTALLATION-GUIDE.md)
