### Architecture Model

**Primary Target:** Alpine Linux (diskless/live boot mode)  
**Development Platforms:** macOS, Ubuntu, Windows (WSL)  
**Plugin System:** Alpine APK packages

### OS-Aware Design Principles

1. **Core runtime is OS-agnostic** — Handlers work across all platforms
2. **OS-specific operations separated** — Disk formatting, package management live in `core/os_specific/`
3. **Platform detection at runtime** — `core/services/os_detector.py` provides capabilities
4. **Graceful degradation** — Commands warn/fail gracefully when OS doesn't support an operation

### Plugin System Standards

| Alpine Base Service         | uDOS Implementation           |
| --------------------------- | ----------------------------- |
| `.apk` package              | uDOS plugins as APK packages  |
| `apk add/del`               | Plugin enable/disable via APK |
| `/etc/udos/plugins.enabled` | Desired plugin state manifest |
| `apkovl` (lbu)              | Persisted system config       |
| APK repo + cache            | Plugin distribution store     |

### Naming Convention

All uDOS APK packages follow: `udos-{component}` pattern:

- `udos-core` — TUI runtime
- `udos-net` — Networking extensions
- `udos-wizard` — Server components (Wizard-only)
- `udos-gui` — Wayland + Cage + Tauri (Tier 2 GUI mode)
- `udos-ui` — Tauri app binary

---

### Features

1. **Package ecosystem** — Access to 10,000+ Alpine packages
2. **Industry standard** — Alpine is proven in Docker, cloud, embedded
3. **Security posture** — Faster CVE patches, better musl libc security
4. **Simple distribution** — Standard APK packaging v
5. **Multi-OS awareness** — Core knows its environment and adapts
6. **Diskless/live boot** — Alpine supports  diskless model 
7. **Persistence strategy same** — Alpine `apkovl` backup mechanism
8. **Plugin philosophy** — Modular, composable, optional extensions


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
