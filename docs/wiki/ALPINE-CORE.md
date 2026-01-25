# uDOS Alpine Core Protocol

**Version:** 1.0.0  
**Status:** Specification  
**Last Updated:** 2026-01-25

## Overview

uDOS Alpine Core defines a single-application GUI mode that boots on Alpine Linux (diskless/live) and launches exactly one uDOS application (Tauri). There is no desktop environment, no window manager UI, and no multi-app shell—the GUI exists only to host the uDOS app as a controlled interface.

## Design Principles

- **TUI-first OS:** Terminal is the default. GUI is an optional membrane.
- **Single responsibility:** Cage compositor runs one app only.
- **No desktop bloat:** No GNOME, KDE, XFCE, or LXQt.
- **OpenRC-native:** No systemd dependency.
- **Diskless by default:** Persistent storage via overlay/apkovl or dedicated partition.

## Target Tiers

### Tier 1: TUI-Only (Default)

- Alpine Linux boots to command line.
- Full TUI functionality available.
- Minimal resource footprint.
- Suitable for headless deployment.

### Tier 2: One-App GUI

- User optionally enables Tier 2 via boot flag or CLI command (`udos gui`).
- Starts Wayland + Cage + Tauri application.
- Exiting the app returns to TTY or triggers clean reboot.
- GUI mode is stateless (on-demand) or persistent (via apkovl).

## Architecture

### Core Stack

| Component    | Purpose                                 |
| ------------ | --------------------------------------- |
| **Wayland**  | Display server (Wayland-native, no X11) |
| **Cage**     | Single-app Wayland compositor           |
| **seatd**    | Seat management without systemd-logind  |
| **Tauri**    | Application runtime (Rust + WebView)    |
| **udos-gui** | Launcher script (POSIX shell)           |

### Runtime Flow

```
Boot (Alpine OpenRC)
  ↓
Tier 1: TTY (default)
  ├─ Read /etc/udos/mode
  ├─ Boot complete → user input
  └─ [User command: udos gui]
      ↓
  Tier 2: GUI
    ├─ seatd + Cage + Tauri
    ├─ Single app running
    └─ Exit → TTY or reboot
```

### Persistence Strategy

**System config:** Stored via apkovl (Alpine Backup List)

- OpenRC services
- Mode flags (/etc/udos/mode)
- Repository config
- Boot parameters

**Application data:** Stored under /mnt/udos (never in apkovl)

- UI state
- User documents
- Persistent workspace

This separation mirrors Tiny Core's "extensions vs data" philosophy.

## Packages

### Required

```
# Core Wayland stack
wayland
libxkbcommon
wayland-protocols

# Compositor
cage

# Seat management
seatd

# Fonts / rendering
fontconfig
mesa
libxkbcommon-dev

# Tauri runtime
webkit2gtk (or WebKitGTK equivalent)
gtk+3.0-dev
```

### Optional

```
# Debug / diagnostics
wayland-utils
xwayland (legacy app support)

# Fonts / emoji
noto-fonts
noto-fonts-emoji
```

## Implementation Tasks

### 1. Launcher Script: `udos-gui`

**Location:** `/usr/local/bin/udos-gui`

**Responsibilities:**

- Validate persistence mount (`/mnt/udos`)
- Set up XDG_RUNTIME_DIR and Wayland environment
- Start seatd service
- Launch Cage + Tauri app
- Handle exit gracefully (TTY return or reboot)

**Example:**

```bash
#!/bin/sh
set -eu

# Ensure persistence
if ! mountpoint -q /mnt/udos; then
    mount /dev/disk/by-label/UDOS_PERSIST /mnt/udos || \
        { echo "Persistence unavailable"; exit 1; }
fi

# Setup Wayland
export XDG_RUNTIME_DIR=/run/user/1000
mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"

# Start seatd
seatd -u user -g input &
SEATD_PID=$!

# Launch Tauri app
exec /usr/local/bin/udos-ui

# Cleanup
kill $SEATD_PID
```

### 2. OpenRC Services

**seatd service:** `/etc/init.d/seatd`

- Managed by OpenRC
- Runs as unprivileged user
- Provides seat access for Wayland

**udos-gui service:** `/etc/init.d/udos-gui`

- Reads `/etc/udos/mode`
- Enabled/disabled based on boot configuration
- Prevents respawn loops on app crash

### 3. Mode Selection

**File:** `/etc/udos/mode`

**Contents:**

```
tui          # Tier 1: TUI only (default)
gui          # Tier 2: Auto-start GUI
gui-on-demand # Tier 2: Manual 'udos gui' command
```

**Early OpenRC service** reads mode and enables/disables Tier 2 accordingly.

### 4. Tauri App Binary

**Target:** `/usr/local/bin/udos-ui`

**Constraints:**

- Must run without a desktop session
- Minimal WebKit dependencies (no GTK layers)
- Communicate with Core via local socket or API

### 5. Failure Handling

| Failure Mode            | Recovery                              |
| ----------------------- | ------------------------------------- |
| No GPU/DRM available    | Fallback message; return to TTY       |
| Tauri app crash         | Clean exit to TTY or safe reboot      |
| Persistence unavailable | Warn user; continue in ephemeral mode |
| Cage compositor crash   | Restart or exit gracefully            |

**Avoids:** Infinite restart loops, kernel panics, or unrecoverable states.

## Security & UX

- **No shell access** from UI unless dev mode enabled.
- **Package justification:** Every dependency must be necessary.
- **Minimal privilege:** Wayland app runs as unprivileged user.
- **Clear error messages:** Users always know what went wrong.

## Deliverables Checklist

- [ ] `udos-gui` launcher script
- [ ] `seatd` OpenRC service
- [ ] `udos-gui` OpenRC service
- [ ] Tauri app binary (`udos-ui`)
- [ ] `/etc/udos/mode` configuration
- [ ] Persistence mount setup
- [ ] Build helper (Makefile or justfile)

## References

- [AGENTS.md](../../AGENTS.md) — Architecture overview
- [Wayland Documentation](https://wayland.freedesktop.org/)
- [Cage Compositor](https://github.com/cage-kiosk/cage)
- [Alpine Linux](https://alpinelinux.org/)

---

**Status:** Specification v1.0.0 ready for implementation  
**Next Steps:** Scaffold OpenRC services, build Tauri binary, test on target hardware
