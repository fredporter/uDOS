# ⚠️ DEPRECATED: TinyCore VM Test Checklist

**Status:** DEPRECATED — Use Alpine Linux instead  
**Migration:** See [ADR-0003-alpine-linux-migration.md](../../docs/decisions/ADR-0003-alpine-linux-migration.md)  
**Date:** 2026-01-24

---

**This guide is archived for historical reference only.**  
**uDOS has migrated to Alpine Linux. Use Alpine VM testing instead.**

---

## Original Goal (Archived)

Validate uDOS packages on TinyCore VM (offline).

---

## 1) Prep Host

```sh
# On host
cd ~/uDOS
# Ensure packages + metadata exist
ls distribution/tcz/udos-*.tcz
```

## 2) VM ISO

```sh
# If remastering (optional)
./distribution/remaster_iso.sh \
  --packages="udos-core.tcz,udos-api.tcz,udos-wizard.tcz" \
  --from=distribution/tcz \
  --input=CorePlus-15.0.iso \
  --output=uDOS-TinyCore-15.0.iso
```

Use `uDOS-TinyCore-15.0.iso` (remastered) or base `CorePlus-15.0.iso` + manual copy.

## 3) Boot VM

- Boot TinyCore (TC 15.x).
- Create TC user password if prompted.

## 4) Copy Packages to VM

```sh
# From host to VM (adjust IP/user)
scp distribution/tcz/udos-*.tcz tc@<vm-ip>:/tmp/
scp distribution/tcz/udos-*.tcz.* tc@<vm-ip>:/tmp/
```

## 5) Install with Installer

```sh
ssh tc@<vm-ip>
cd /tmp
chmod +x installer.sh  # if copied; else run from host via scp
./installer.sh --tier=wizard --from=/tmp --yes
```

- Dry-run first (optional): `./installer.sh --tier=wizard --from=/tmp --dry-run`

## 6) Verify Install

```sh
which udos
udos --version
tce-load -i /tmp/udos-core.tcz
unsquashfs -l /tmp/tcloop/udos-core.tcz | head
```

## 7) Smoke Tests

```sh
# Core TUI
udos --help
# API server (if installed)
python /usr/local/lib/udos/extensions/api/server.py --help
# Wizard server (if installed)
python /usr/local/lib/udos/wizard/server.py --help
```

## 8) Cleanup (optional)

```sh
rm -rf /tmp/udos-*.tcz /tmp/installer.sh
```

---

**Pass criteria:**

- `udos` available in PATH and reports version.
- `tce-load -i udos-core.tcz` succeeds without errors.
- API/Wizard scripts reachable if their packages installed.
