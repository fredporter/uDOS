# ⚠️ DEPRECATED: TinyCore ISO Library

**Status:** DEPRECATED  
**Date:** 2026-01-24  
**Replacement:** Alpine Linux (see migration guide)

---

## Migration

uDOS has migrated from TinyCore Linux to Alpine Linux.

**This directory is kept for historical reference only.**

### For Alpine Linux

See the new documentation:

- **Installation:** [docs/howto/alpine-install.md](../../docs/howto/alpine-install.md)
- **Architecture Decision:** [docs/decisions/ADR-0003-alpine-linux-migration.md](../../docs/decisions/ADR-0003-alpine-linux-migration.md)
- **Package Building:** Use APK format via `wizard/services/plugin_factory.py`

### Why Alpine?

1. **Modern package manager** — APK vs TCZ
2. **Better security** — Active maintenance, security updates
3. **Standard FHS** — Filesystem Hierarchy Standard compliance
4. **Multi-platform** — x86_64, aarch64, armv7, etc.
5. **Better tooling** — abuild, apk-tools, Alpine SDK

---

## Old Files (Do Not Use)

- `setup.py` — TinyCore ISO download utility (replaced by Alpine installer)
- `README.md` — TinyCore documentation (see Alpine guide instead)
- `TinyCore-current.iso` — Local ISO cache (not needed for Alpine)

---

**For help:** See [ALPINE-MIGRATION-STATUS.md](../../ALPINE-MIGRATION-STATUS.md)
