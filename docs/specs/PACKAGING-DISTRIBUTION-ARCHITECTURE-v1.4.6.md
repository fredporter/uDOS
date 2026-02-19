# uDOS v1.4.6 Packaging & Distribution Architecture

**Status:** Specification (v1.4.6 dev round)
**Owner:** uDOS Build/Release Team
**Target Release:** 2026-05-31

---

## Vision

Transform uDOS from a monolithic repository into a **consumable distribution system** with:

- **Multi-variant packaging:** Core-only, Wizard-full, Sonic-standalone, Dev-complete
- **Local library ecosystem:** Versioned packages with dependency resolution, updates, sharing
- **Hardened Docker:** Health checks, lifecycle management, security scanning, backup/restore
- **Standalone Sonic:** Bootable ISO without Wizard dependency; integration bridge for Wizard hosts
- **Decentralized distribution:** No central monorepository; packages distributed via GitHub Releases, package registries, local libraries

---

## Package Architecture

### Package Variants

#### 1. `udos-core-slim` (Core Runtime Only)
**Use Case:** Lightweight local installation (Mac/Linux dev machines)

```
udos-core-slim-v1.4.6/
  core/                           # Stdlib-only Python runtime
  bin/
    ucli                          # Terminal entry point
    uDOS.py                      # Main executable
  docs/                           # Documentation
  themes/genre/                   # TUI themes (no Wizard GUI themes)
  README.md
  version.json                    # {"version": "1.4.6", "variant": "core-slim"}
  INSTALLATION.md
  requirements.txt                # Stdlib-only (empty or ecosystem)
```

**Install Size:** ~50 MB (no containers)
**Dependencies:** Python 3.8+, bash
**Installation:** Direct download or `brew tap fredbook/udos && brew install udos-core-slim`

#### 2. `udos-wizard-full` (Core + Wizard + Docker)
**Use Case:** Full-featured local installation (Wizard GUI + containers)

```
udos-wizard-full-v1.4.6/
  core/                           # Core runtime
  wizard/                         # Wizard server + GUI
    requirements.txt
    web/                          # Dashboard frontend (Svelte compiled)
    routes/                       # API routes
  venv/                           # Shared Python venv (root-level snapshot)
  docker-compose.yml              # Full service stack
  distribution/
    jekyll-site-template/         # GitHub Pages template
    local-library-catalog.json    # Library registry
  bin/
    ucli
    uDOS.py
    wizard-server
  README.md
  version.json                    # {"version": "1.4.6", "variant": "wizard-full"}
  INSTALLATION.md
  DOCKER-OPERATIONS.md
  LIBRARY-MANAGEMENT.md
```

**Install Size:** ~500 MB (with Docker images layered)
**Dependencies:** Python 3.11+, Docker, Docker Compose, Node.js (optional, for GUI dev)
**Installation:** `brew install udos-wizard-full` or direct download + `chmod +x uDOS.py && ./uDOS.py wizard start`

#### 3. `udos-sonic-iso` (Standalone Bootable ISO)
**Use Case:** Bootable USB media for system installation/recovery (no Wizard)

```
udos-sonic-v1.4.6.iso            # UEFI + MBR bootable ISO
  ~1.2 GB, contains:
    - Alpine Linux minimal kernel
    - Core uDOS TUI runtime
    - System installer script
    - Hardware detection utilities
    - Network bootstrap tools

Documentation:
  SONIC-STANDALONE.md             # Boot, install, recovery
  SONIC-HARDWARE-SUPPORT.md       # CPU, disk, GPU support matrix
```

**Install Size:** 1.2 GB ISO (bootable)
**Requirements:** USB drive (≥2GB), UEFI or BIOS firmware, internet for full install
**Installation:** WriteToUSB, `dd`, Balena Etcher, or Sonic installer script

#### 4. `udos-dev-complete` (Full Dev Environment)
**Use Case:** Complete development stack (Core + Wizard + Sonic + /dev)

```
udos-dev-complete-v1.4.6/
  core/                           # Core + TS runtime + examples
  wizard/                         # Wizard + dev extensions
  sonic/                          # Sonic + build tools
  dev/                            # Development tools, test harnesses
  / + everything from wizard-full
```

**Install Size:** ~1 GB
**Dependencies:** Full dev toolchain (Rust, Go, Node.js, Python 3.11, Docker, GCC, Make)
**Installation:** Developers clone git repo configured per [INSTALLATION-DEV.md](../INSTALLATION-DEV.md)

### Release Manifest

**`releases/v1.4.6-manifest.json`:**

```json
{
  "version": "1.4.6",
  "release_date": "2026-05-31T00:00:00Z",
  "variants": [
    {
      "name": "core-slim",
      "filename": "udos-core-slim-v1.4.6.tar.gz",
      "size_bytes": 52428800,
      "checksum_sha256": "abc123def456...",
      "checksum_sha512": "xyz789...",
      "gpg_signature": "-----BEGIN PGP SIGNATURE-----...",
      "platforms": ["macos-amd64", "macos-arm64", "linux-amd64", "linux-arm64"],
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-core-slim-v1.4.6.tar.gz",
      "minimum_python": "3.8"
    },
    {
      "name": "wizard-full",
      "filename": "udos-wizard-full-v1.4.6.tar.gz",
      "size_bytes": 524288000,
      "checksum_sha256": "def456abc123...",
      "platforms": ["macos-amd64", "macos-arm64", "linux-amd64"],
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-wizard-full-v1.4.6.tar.gz",
      "minimum_python": "3.11",
      "requires_docker": true
    },
    {
      "name": "sonic-iso",
      "filename": "udos-sonic-v1.4.6.iso",
      "size_bytes": 1258291200,
      "checksum_sha256": "ghi789jkl012...",
      "gpg_signature": "-----BEGIN PGP SIGNATURE-----...",
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-sonic-v1.4.6.iso",
      "bootable": true,
      "uefi_supported": true,
      "bios_fallback": true
    }
  ],
  "sbom": {
    "format": "cyclonedx",
    "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-v1.4.6-sbom.json"
  },
  "release_notes": "https://github.com/fredbook/uDOS/releases/tag/v1.4.6"
}
```

---

## Local Library System

### Library Catalog Schema

**`distribution/local-library-catalog.json`:**

```json
{
  "catalog_version": "1.0",
  "last_updated": "2026-05-31T00:00:00Z",
  "libraries": [
    {
      "id": "lib-grid-extensions",
      "namespace": "@uDOS/grid-extensions",
      "name": "Grid Extensions",
      "version": "1.2.3",
      "description": "Enhanced grid rendering and pathfinding utilities",
      "author": "fredbook",
      "license": "MIT",
      "homepage": "https://github.com/fredbook/lib-grid-extensions",
      "repository": {
        "type": "git",
        "url": "https://github.com/fredbook/lib-grid-extensions"
      },
      "downloads": 1250,
      "rating": 4.8,
      "dependencies": {
        "@uDOS/core": "^1.4.0"
      },
      "entry_point": "lib/grid_extensions/__init__.py",
      "install_path": "library/grid-extensions",
      "tags": ["grid", "spatial", "pathfinding"],
      "checksums": {
        "sha256": "abc123def456...",
        "sha512": "xyz789..."
      },
      "installed": {
        "timestamp": "2026-02-20T14:30:00Z",
        "version": "1.2.3"
      }
    }
  ]
}
```

### Library Manager Commands

```bash
# Search and Info
LIBRARY search <query>                      # Search catalog
LIBRARY info <name>[@version]               # Show library details + dependencies
LIBRARY list                                # List installed libraries
LIBRARY list --available                    # List available libraries in catalog

# Install/Update
LIBRARY install <name>[@version]            # Install specific version (default: latest)
LIBRARY install <name>@~1.2                 # Semantic version constraint
LIBRARY install ./custom-lib.udos-package   # Install from archive
LIBRARY update <name>                       # Update to latest compatible
LIBRARY update --all                        # Update all installed libraries
LIBRARY check-updates                       # Show available updates

# Management
LIBRARY uninstall <name>                    # Remove library
LIBRARY rollback <name> --to <version>      # Downgrade to specific version
LIBRARY config <name> --edit                # Edit library config (JSON)
LIBRARY config <name> --show                # Show library configuration

# Publishing/Sharing
LIBRARY pack <name> [--output ./lib.udos-package]  # Export as distributable
LIBRARY share <name> --github               # Publish to GitHub registry
LIBRARY sync                                # Pull latest catalog from registry
```

### Library Package Format (`.udos-package`)

Distributable library archive (tar.gz + metadata):

```
lib-grid-extensions-v1.2.3.udos-package
  ├── manifest.json                # Library metadata + checksums
  ├── lib/
  │   └── grid_extensions/
  │       ├── __init__.py
  │       ├── grid.py
  │       └── pathfinder.py
  ├── docs/
  │   └── README.md
  ├── examples/
  │   └── pathfinding-demo.py
  └── requirements.txt              # Library dependencies
```

**Manifest:**
```json
{
  "id": "lib-grid-extensions",
  "version": "1.2.3",
  "name": "Grid Extensions",
  "author": "fredbook",
  "license": "MIT",
  "entry_point": "lib/grid_extensions/__init__.py",
  "install_path": "library/grid-extensions",
  "dependencies": {
    "@uDOS/core": "^1.4.0"
  },
  "checksums": {
    "sha256": "abc123def456..."
  }
}
```

### Dependency Resolution

Library manager implements:

1. **Semantic Versioning:** `^1.4.0` (≥1.4.0, <2.0.0), `~1.4.3` (≥1.4.3, <1.5.0)
2. **Circular Dependency Detection:** Warn if A→B→A, block install
3. **Version Conflict Resolution:** If B requires `^1.2` and C requires `~1.4`, error if mismatch
4. **Transitive Dependencies:** Auto-install dependencies of dependencies
5. **Lockfile:** `library/lock.json` pins exact versions (reproducible installs)

---

## Docker Container Hardening

### Health Checks

**All services in `docker-compose.yml` include:**

```yaml
services:
  wizard:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart_policy:
      condition: on-failure
      delay: 5s
      max_retries: 5
      window: 120s
```

**Health Check Contract:**
- `GET /api/health` returns `{"status": "healthy"}` if ready
- Interval: 30s, timeout: 10s
- Auto-restart on unhealthy (exponential backoff, max 5 retries)

### Lifecycle Management

**`docker/lifecycle-manager.py`:**

```python
class ContainerLifecycleManager:
  # Startup sequence enforcement
  def startup(self):
    # 1. Start dependency services first
    # 2. Wait for health checks to pass
    # 3. Mark service ready only when deps healthy
    # 4. Log startup event to audit trail
    pass

  # Graceful shutdown
  def shutdown(self):
    # 1. Send SIGTERM to all containers
    # 2. Wait 30s for graceful shutdown
    # 3. Force SIGKILL if timeout
    # 4. Log shutdown event with exit codes
    pass

  # Recovery from failure
  def recover(self, failed_service):
    # 1. Identify failed service
    # 2. Check logs for error patterns
    # 3. Attempt recovery (restart, reset state)
    # 4. Alert user if recovery fails
    pass
```

### Network Isolation

**Custom Docker Network (`udos-network`):**

```yaml
networks:
  udos-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  wizard:
    networks:
      - udos-network
    # Only accessible to other containers on udos-network
    # No direct port exposure unless explicitly mapped
```

### Volume Security

**Hardened Mounts:**

```yaml
services:
  wizard:
    volumes:
      - wizard-vault:/vault:rw         # Read-write vault data
      - wizard-config:/config:ro       # Read-only config
      - wizard-logs:/logs:rw           # Write-only logs
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### Image Security

1. **Vulnerability Scanning:** Trivy scans all images at build time
2. **Minimal Base Images:** Alpine Linux where possible; distroless for prod
3. **Image Signing:** Sign images with GPG, verify in compose
4. **No Root:** Containers run as non-root user (UID 1000+)

---

## Sonic Standalone Integration

### Sonic ISO Build Pipeline

**`sonic/build-iso.sh`:**

```bash
# 1. Create minimal Alpine rootfs
# 2. Add Core uDOS TUI runtime
# 3. Add installer script
# 4. Build UEFI/MBR bootable image
# 5. Sign image (GPG)
# 6. Generate checksums
```

**Output:** `builds/udos-sonic-v1.4.6.iso` (1.2 GB)

### Boot Modes

| Boot Mode | Use Case | Hardware | Boot Time |
|-----------|----------|----------|-----------|
| **UEFI** | Modern laptops/desktops (>2012) | x86_64, ARM64 | ~8s |
| **BIOS** | Older systems, VMs | x86_64 | ~10s |
| **TFTP/PXE** | Network install | Any networked | Variable |

### Sonic → Wizard Bridge

**How Booted Sonic Connects to Wizard Host:**

1. **Discovery Phase:**
   - Sonic detects Wizard services on LAN (mDNS/Bonjour)
   - Wizard broadcasts `_udos-wizard._tcp` service
   - Sonic resolves host, obtains SSH public key

2. **Auth Phase:**
   - Sonic challenges host with random nonce
   - Host signs with private key
   - Sonic verifies signature

3. **Command Execution:**
   - User runs command in Sonic TUI: `SSH> run-command my-command`
   - SSH tunnel established to Wizard host
   - Command routed to Wizard → Core execution
   - Results streamed back to Sonic

4. **State Sync:**
   - Sonic syncs game state to Wizard (via SSH)
   - Wizard manages persistent state
   - Sonic shutdown doesn't lose progress

### Sonic Update Mechanism

**`SONIC update`:**

```bash
# 1. Check GitHub releases for newer ISO
# 2. Download new ISO (bg transfer if >500MB)
# 3. Verify checksum + GPG signature
# 4. Apply binary delta (only download differences)
# 5. Offer user to reboot and boot from new ISO
```

---

## Build & Release Automation

### GitHub Actions Release Workflow

**`.github/workflows/release.yml`:**

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v1.4.*'

jobs:
  build-matrix:
    runs-on: ${{ matrix.runner }}
    strategy:
      matrix:
        runner: [macos-latest, ubuntu-latest]
        variant: [core-slim, wizard-full]
    steps:
      - uses: actions/checkout@v4
      - name: Build variant
        run: python bin/build-release.py --variant ${{ matrix.variant }}
      - name: Sign artifact
        run: gpg --detach-sign built/${{ matrix.variant }}.tar.gz
      - name: Upload to releases
        uses: softprops/action-gh-release@v1
        with:
          files: built/**
          draft: false
```

### Artifact Signing

**GPG workflow:**

```bash
# Build artifacts
python bin/build-release.py --variant core-slim

# Sign with release key
gpg --default-key releases@udos.dev --detach-sign udos-core-slim-v1.4.6.tar.gz

# Verify signature (CI)
gpg --verify udos-core-slim-v1.4.6.tar.gz.sig udos-core-slim-v1.4.6.tar.gz
```

---

## Success Criteria

✅ **Packaging:** All 4 variants build successfully on macOS and Linux
✅ **Install:** Any variant installable in <5 minutes on clean system
✅ **Libraries:** Library install/update/rollback <30 seconds per library
✅ **Docker:** All containers healthy, auto-restart on failure (>99% uptime)
✅ **Sonic:** Boots on 5+ diverse hardware targets; Wizard bridge latency <200ms
✅ **Security:** No CVEs in Docker images; all artifacts signed and verified
✅ **Tests:** E2E coverage for all 4 variants + upgrade paths (v1.4.3 → v1.4.6)
✅ **Documentation:** Installation guides for all platforms, library docs, Docker ops manual

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Specification](https://github.com/compose-spec/compose-spec)
- [Semantic Versioning](https://semver.org/)
- [Trivy Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [UEFI Specification](https://uefi.org/specifications)
