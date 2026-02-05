# ⚠️ DEPRECATED: TinyCore Installation Guide (uDOS TCZ)

**Last Updated:** 2026-01-14 (Deprecated: 2026-01-24)  
**Status:** DEPRECATED — Use Alpine Linux instead  
**Migration:** See [ADR-0003-alpine-linux-migration.md](../../docs/decisions/ADR-0003-alpine-linux-migration.md)

---

**⚠️ This guide is archived for historical reference only.**  
**uDOS has migrated to Alpine Linux. Please use:**

- **New Guide:** [docs/howto/alpine-install.md](../../docs/howto/alpine-install.md)
- **APK packages** instead of TCZ packages

---

## Original Scope (Archived)

Install uDOS TCZ packages on TinyCore Linux (offline-first)

---

## Prerequisites

- TinyCore 15.x (CorePlus recommended for drivers)
- `tce-load`, `md5sum`, `unsquashfs` available (default on TC)
- uDOS packages + metadata in one directory (e.g., `distribution/tcz`):
  - `udos-core.tcz` (+ `.dep/.md5.txt/.info/.list`)
  - `udos-api.tcz` (optional)
  - `udos-wizard.tcz` (optional)

---

## Quick Install (tier-based)

```sh
./distribution/installer.sh --tier=core --from=/path/to/tcz --yes
```

- Tiers: `ultra | micro | mini | core | standard | wizard`
- Auto-select: if no `--tier` and no custom list, installer recommends based on RAM.
- Custom packages: `--packages="udos-core.tcz,udos-api.tcz"`
- Dry run: `--dry-run` (no changes)

### What the installer does

- Detects platform (TC version, arch, RAM, CPUs)
- Resolves local dependencies via `.tcz.dep` files
- Copies packages + metadata to `/tmp/udos-tcz` and installs with `tce-load -i`
- Fails fast if any package/dep file is missing

---

## ISO Remaster (bundle uDOS into TinyCore ISO)

```sh
# Base ISO in distribution/: CorePlus-15.0.iso
./distribution/remaster_iso.sh \
  --packages="udos-core.tcz,udos-api.tcz,udos-wizard.tcz" \
  --from=distribution/tcz \
  --input=CorePlus-15.0.iso \
  --output=uDOS-TinyCore-15.0.iso
```

- Copies `.tcz` + metadata into `cde/optional` and appends to `onboot.lst`.
- Output ISO: `distribution/uDOS-TinyCore-15.0.iso` (bootable).

---

## Verification

After install (or after boot with remastered ISO):

```sh
which udos
udos --version
unsquashfs -l /tmp/tcloop/udos-core.tcz | head
```

- If `udos` not found, ensure `tce-load -i udos-core.tcz` succeeded and PATH includes `/usr/local/bin`.

---

## Troubleshooting

- **Missing package/dep**: Ensure `.tcz` and `.tcz.dep` are in the `--from` directory.
- **MD5 mismatch**: Regenerate with `md5sum pkg.tcz > pkg.tcz.md5.txt`.
- **Low RAM devices**: Use `--tier=ultra` (core only) or let auto-selection pick based on RAM.
- **No internet**: Keep all required `.tcz` + metadata together; the installer uses local files only.
- **tce-load path issues**: Installer retries from cache dir; verify `tce-load` exists on PATH.

---

## Files Reference

- Installer: `distribution/installer.sh`
- Packages (example): `distribution/tcz/`
- ISO remaster: `distribution/remaster_iso.sh`
- Spec: `docs/specs/tinycore-packaging.md`
