# Alpine Linux Installation Guide (uDOS APK)

**Date:** 2026-01-24  
**Status:** Active (replaces TinyCore guide)  
**Scope:** Install uDOS APK packages on Alpine Linux (offline-first)

---

## Prerequisites

- Alpine Linux 3.18+ (diskless or standard installation)
- `apk` package manager (default on Alpine)
- `abuild` tools (for building packages)
- uDOS packages + metadata in one directory (e.g., `distribution/apk`):
  - `udos-core-1.0.0.apk` (+ APKINDEX, signature)
  - `udos-api-1.0.0.apk` (optional)
  - `udos-wizard-1.0.0.apk` (optional)

---

## Quick Install

```bash
./distribution/installer.sh --tier=core --from=/path/to/apk --yes
```

**Options:**

- Custom packages: `--packages="udos-core,udos-api"`
- Specific tier: `--tier=core|desktop|wizard`

---

## Manual Installation

### 1. Add Local Repository

```bash
# Copy packages to persistence mount
sudo mkdir -p /mnt/udos/repo
sudo cp distribution/apk/* /mnt/udos/repo/

# Add to APK repositories
echo "/mnt/udos/repo" | sudo tee -a /etc/apk/repositories
```

### 2. Install Packages

```bash
# Update repository index
sudo apk update

# Install uDOS Core
sudo apk add udos-core

# Optional: Install extensions
sudo apk add udos-api udos-gui
```

### 3. Enable Services (OpenRC)

```bash
# Enable uDOS service
sudo rc-update add udos default

# Start service
sudo rc-service udos start
```

---

## Diskless/Live Boot Mode

Alpine's diskless mode uses Local Backup Utility (lbu) for persistence:

### Save Configuration

```bash
# Add uDOS to persistent files
sudo lbu include /opt/udos
sudo lbu include /etc/udos

# Commit changes
sudo lbu commit
```

### Plugin Manifest

Create `/etc/udos/plugins.enabled`:

```
udos-core
udos-api
udos-net
```

On boot, system will run:

```bash
apk add $(cat /etc/udos/plugins.enabled)
```

---

## Building APK Packages

### Setup Build Environment

```bash
# Install build tools
sudo apk add alpine-sdk abuild

# Setup build user
sudo adduser -D builder
sudo addgroup builder abuild
```

### Build Package

```bash
cd distribution/apkbuild/udos-core/
abuild checksum
abuild -r
```

Output: `~/packages/<arch>/udos-core-*.apk`

---

## ISO Remaster (bundle uDOS into Alpine ISO)

```bash
./distribution/remaster.sh \
  --base=alpine-standard-3.18-x86_64.iso \
  --packages="udos-core,udos-api,udos-gui" \
  --from=distribution/apk \
  --output=uDOS-Alpine-3.18.iso
```

**Result:**

- Output ISO: `distribution/uDOS-Alpine-3.18.iso` (bootable)
- Packages pre-installed, ready to boot

---

## Verification

```bash
# Check installed packages
apk list | grep udos

# Verify service status
rc-service udos status

# Test uDOS
udos --version
udos HELP
```

---

## Uninstallation

```bash
# Stop service
sudo rc-service udos stop

# Remove packages
sudo apk del udos-core udos-api udos-gui

# Clean persistence (optional)
sudo lbu exclude /opt/udos
sudo lbu commit
```

---

## Troubleshooting

### Package Not Found

```bash
# Verify repository
cat /etc/apk/repositories

# Check repository index
apk list | grep udos

# Rebuild index
cd /mnt/udos/repo
apk index -o APKINDEX.tar.gz *.apk
```

### Service Won't Start

```bash
# Check logs
cat /var/log/messages | grep udos

# Verify OpenRC configuration
cat /etc/init.d/udos
```

---

## Migration from TinyCore

If migrating from TinyCore Linux:

1. **Backup data:** `/opt/udos`, `/etc/udos`
2. **Boot Alpine:** Use live USB or remastered ISO
3. **Install packages:** Follow installation steps above
4. **Restore data:** Copy backups to new system
5. **Test:** Verify all functionality

See [ADR-0003-alpine-linux-migration.md](../../docs/decisions/ADR-0003-alpine-linux-migration.md) for complete migration guide.

---

## References

- **ADR:** [ADR-0003-alpine-linux-migration.md](../../docs/decisions/ADR-0003-alpine-linux-migration.md)
- **Spec:** [alpine-core.md](../../../dev/roadmap/alpine-core.md)
- **Alpine Docs:** https://docs.alpinelinux.org/
- **APK Tools:** https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper
- **OpenRC:** https://wiki.alpinelinux.org/wiki/OpenRC

---

_Last Updated: 2026-01-24_  
_Replaces: tinycore-install.md (deprecated)_
