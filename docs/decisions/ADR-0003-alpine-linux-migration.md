# ADR-0003: Alpine Linux Migration (TinyCore → Alpine)

**Status:** Accepted  
**Date:** 2026-01-24  
**Supersedes:** Original TinyCore Linux design assumption

---

## Context

uDOS was initially designed to run on TinyCore Linux as its primary lightweight embedded OS target. TinyCore offered:

- Extremely small footprint (~15MB base)
- `.tcz` extension system for modular plugins
- `tce-load` package manager
- Diskless/live boot capability

However, operational experience revealed several limitations:

1. **Limited package ecosystem** — Many modern tools lack TinyCore packages
2. **Packaging complexity** — Creating `.tcz` packages requires TinyCore-specific tooling
3. **Security updates** — Slower security patch cycles compared to Alpine
4. **Industry adoption** — Alpine Linux has become the de facto standard for containerized/embedded Linux (Docker, Kubernetes)
5. **Multi-OS support needed** — uDOS runs on macOS, Ubuntu, Windows dev machines in addition to embedded targets

---

## Decision

**We migrate uDOS from TinyCore Linux to Alpine Linux as the primary embedded/TUI target.**

### New Architecture Model

**Primary Target:** Alpine Linux (diskless/live boot mode)  
**Development Platforms:** macOS, Ubuntu, Windows (WSL)  
**Plugin System:** Alpine APK packages (not TCZ extensions)

### OS-Aware Design Principles

1. **Core runtime is OS-agnostic** — Handlers work across all platforms
2. **OS-specific operations separated** — Disk formatting, package management live in `core/os_specific/`
3. **Platform detection at runtime** — `core/services/os_detector.py` provides capabilities
4. **Graceful degradation** — Commands warn/fail gracefully when OS doesn't support an operation

### Plugin System Migration

| TinyCore Concept  | Alpine Equivalent           | uDOS Implementation           |
| ----------------- | --------------------------- | ----------------------------- |
| `.tcz` extension  | `.apk` package              | uDOS plugins as APK packages  |
| `tce-load`        | `apk add/del`               | Plugin enable/disable via APK |
| `onboot.lst`      | `/etc/udos/plugins.enabled` | Desired plugin state manifest |
| TC backup/restore | `apkovl` (lbu)              | Persisted system config       |
| TC extension dir  | APK repo + cache            | Plugin distribution store     |

### Naming Convention

All uDOS APK packages follow: `udos-{component}` pattern:

- `udos-core` — TUI runtime
- `udos-net` — Networking extensions
- `udos-wizard` — Server components (Wizard-only)
- `udos-gui` — Wayland + Cage + Tauri (Tier 2 GUI mode)
- `udos-ui` — Tauri app binary

---

## Consequences

### Positive

1. **Better package ecosystem** — Access to 10,000+ Alpine packages
2. **Industry standard** — Alpine is proven in Docker, cloud, embedded
3. **Security posture** — Faster CVE patches, better musl libc security
4. **Simpler distribution** — Standard APK packaging vs custom TCZ builds
5. **Multi-OS awareness** — Core knows its environment and adapts

### Negative

1. **Migration effort** — Must update all TinyCore-specific code
2. **Slightly larger footprint** — Alpine base ~5MB vs TinyCore ~15MB (acceptable)
3. **Breaking change** — Existing TinyCore installations must migrate

### Neutral

1. **Still diskless/live boot** — Alpine supports same diskless model as TinyCore
2. **Persistence strategy same** — Alpine `apkovl` replaces TC backup mechanism
3. **Plugin philosophy preserved** — Still modular, composable, optional extensions

---

## Implementation Checklist

### Phase 1: Core Migration (This Sprint)

- [x] Create this ADR
- [ ] Update AGENTS.md references (lines 11, 27, 54)
- [ ] Update .github/copilot-instructions.md (line 3)
- [ ] Create `core/services/os_detector.py` with multi-OS detection
- [ ] Update `dev/goblin/core/utils/paths.py` → `is_alpine()` instead of `is_tinycore()`
- [ ] Update `bin/install.sh` detection logic
- [ ] Replace `wizard/services/plugin_factory.py` TCZ builder with APK builder
- [ ] Create `core/os_specific/` directory structure
- [ ] Audit all `/core/commands/` handlers for OS compatibility
- [ ] Update test suites (`test_paths.py` → `TestAlpineDetection`)

### Phase 2: Documentation (Next Sprint)

- [ ] Update all `/docs` references (TinyCore → Alpine)
- [ ] Create Alpine installation guide
- [ ] Document OS-specific command namespace
- [ ] Update quickstart for Alpine boot process
- [ ] Promote alpine-core.md spec to `/docs/specs/`

### Phase 3: Distribution (Future)

- [ ] Build initial APK repository structure
- [ ] Package `udos-core.apk`, `udos-gui.apk`
- [ ] Test Alpine live boot with uDOS
- [ ] Create Screwdriver flash image templates (Alpine base)

---

## Related Documents

- [alpine-core.md](/dev/roadmap/alpine-core.md) — Detailed Alpine implementation spec
- [AGENTS.md](../../AGENTS.md) — Core architectural boundaries
- [Development Streams](../development-streams.md) — Roadmap context

---

## Notes

**OS-Specific Command Example:**

```python
# core/services/os_detector.py
class OSDetector:
    def detect_platform(self) -> str:
        """Returns: 'alpine', 'macos', 'ubuntu', 'windows'"""

    def can_format_disk(self, filesystem: str) -> bool:
        """Check if OS supports disk formatting operation"""

    def warn_os_constraint(self, command: str, required_os: list):
        """Warn user if command not supported on current OS"""
```

**Swap-Box Concept:**

OS-specific utilities organized in `core/os_specific/{os_name}/`:

- `core/os_specific/alpine/` — Alpine-specific commands (apk, lbu, setup-alpine)
- `core/os_specific/macos/` — macOS-specific (diskutil, hdiutil, defaults)
- `core/os_specific/ubuntu/` — Ubuntu-specific (apt, snap, systemctl)
- `core/os_specific/windows/` — Windows-specific (PowerShell, diskpart)

Handlers delegate to OS-specific implementations when kernel/OS-level operations needed.

---

_Last Updated: 2026-01-24_
