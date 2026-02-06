# Tier 2 One-App GUI (Alpine + Wayland + Cage + Tauri)

This document describes the Alpine "One-App GUI" mode for uDOS: a diskless Alpine system that boots to a TUI by default and can enter a single-application Wayland session running the uDOS Tauri UI.

## Goals
- Diskless Alpine boot with OpenRC.
- Tier 1 (TUI) remains default and functional.
- Tier 2 (GUI) runs exactly one app under Cage.
- Persistent state is stored on the UDOS_PERSIST mount.

## Components
- `seatd` for seat access
- `cage` single-app Wayland compositor
- `udos-ui` Tauri binary
- OpenRC services: `seatd`, `udos-gui`, `tier-selector`
- Persistence manager: `udos-persist`

## Package List (Single Source of Truth)
- `distribution/alpine-core/packages.txt`

Install (example):
```sh
apk add $(grep -Ev '^\s*#|^\s*$' distribution/alpine-core/packages.txt)
```

## Persistence Layout
Mount `UDOS_PERSIST` at `/mnt/udos`. The following paths are bind-mounted into the rootfs:
- `/etc/udos` -> `/mnt/udos/etc/udos`
- `/var/log/udos` -> `/mnt/udos/logs`
- `/var/udos/ui` -> `/mnt/udos/var/ui`

The GUI launcher ensures these directories exist and bind mounts are in place. You can also run:
```sh
udos-persist mount
udos-persist bind
```

## Tier Selection
- Default mode: `tui`
- Enable GUI: set `/etc/udos/mode` to `gui` or use `udos-tier switch gui`

OpenRC services:
- `tier-selector` runs early to ensure the mode file exists.
- `udos-gui` checks `/etc/udos/mode` before starting.

## GUI Launch Flow
1. `seatd` starts (OpenRC).
2. `udos-gui` validates graphics stack, persistence, and `udos-ui`.
3. `cage -- /usr/local/bin/udos-ui` launches the UI.
4. On exit, control returns to TTY.
   - Restart the GUI from TTY:
   - `rc-service udos-gui start`
   - Or: `udos-gui start`

## Files & Scripts
- Launcher: `distribution/udos/bin/udos-gui`
- Tier switcher: `distribution/udos/bin/udos-tier`
- Persistence manager: `distribution/udos/bin/udos-persist`
- OpenRC services: `distribution/udos/etc/init.d/seatd`, `distribution/udos/etc/init.d/udos-gui`, `distribution/udos/etc/init.d/tier-selector`

## Recovery & Failure Behavior
- Missing GPU/Wayland stack: launcher exits with clear error messages.
- Missing packages: error directs to the package list.
- `udos-ui` crash: session exits cleanly back to TTY.
- No respawn loops are configured for `udos-gui`.

## Notes
- No desktop environment, login manager, or multi-app shell is used.
- UI state is stored under `/mnt/udos/var/ui` via bind mounts.
