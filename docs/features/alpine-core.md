uDOS Alpine Core “One-App GUI Mode” (Alpine Diskless + Wayland + Cage + Tauri)

Goal

Implement uDOS Alpine Core: a single-application GUI session that boots on Alpine Linux (diskless/live) and launches exactly one uDOS GUI app (Tauri).
No desktop environment. No window manager UI. No multi-app shell. The GUI exists only to host uDOS.app as a controlled “front panel”.

We will use:
	•	Wayland
	•	Cage (single-app Wayland compositor)
	•	Tauri (uDOS GUI)
	•	Alpine OpenRC init
	•	Persistent storage via an overlay/apkovl and/or a dedicated persistence partition.

Design principle: TUI-first OS; GUI is an optional membrane that boots fast and runs one trusted app.

⸻

Non-Goals
	•	No GNOME/KDE/XFCE/LXQt.
	•	No full window manager session (no menus, panels, launchers).
	•	No multi-window browsing/desktop workflows.
	•	No graphical login manager (no GDM/SDDM/LightDM).
	•	No reliance on systemd.

⸻

Target Behaviour (Acceptance Criteria)
	1.	System boots diskless Alpine to TUI (Tier 1 default).
	2.	Entering Tier 2 can be done via one of:
	•	A dedicated OpenRC service enabled by a boot flag (preferred), or
	•	A CLI command (udos gui) that starts the compositor and app.
	3.	Tier 2 starts:
	•	seatd (or equivalent seat management)
	•	cage compositor
	•	launches exactly one app: udos-ui (Tauri binary)
	4.	Exiting the app:
	•	returns to TTY OR
	•	triggers a clean reboot (choose one and implement consistently).
	5.	No other windows are allowed (Cage enforces single-app).
	6.	Persistent config for the GUI mode (and Tauri state) is stored on a uDOS persistence mount, not inside ephemeral RAM root.

⸻

Platform Constraints
	•	Alpine Linux, diskless/live style.
	•	OpenRC init.
	•	Must support common hardware:
	•	Intel/AMD GPU with Mesa
	•	“modesetting” style operation
	•	Prefer Wayland-native paths (avoid X11).
	•	uDOS UI should not require privileged operations beyond what’s needed for Wayland session access.

⸻

Architecture Overview

Services / Components
	•	seatd — provides seat access without logind
	•	cage — Wayland compositor, runs one app
	•	udos-ui — Tauri app binary
	•	udosd (optional) — local daemon providing API access to uDOS Core

Runtime Flow
	1.	Boot → OpenRC → networking (optional) → TTY
	2.	User triggers Tier 2 → start seatd → start cage → cage execs udos-ui
	3.	If udos-ui exits:
	•	Cage exits automatically
	•	Launcher handles return path (TTY) or reboot

⸻

Packages (Conceptual List)

Implement as an Alpine apk add list (exact names may vary by release):

Core Wayland stack
	•	wayland
	•	mesa + DRI drivers (e.g. mesa-dri-gallium)
	•	libinput
	•	seatd

Compositor
	•	cage

Fonts / rendering
	•	fontconfig
	•	ttf-dejavu (or minimal font set)
	•	(Optional) emoji font later if required

Debug / diagnostics (optional)
	•	wayland-utils

Tauri runtime requirements
	•	WebView backend dependencies (WebKitGTK or equivalent as required by Tauri)
	•	Only minimal required libraries; no desktop pulls

Important: do not install a desktop environment to satisfy WebView dependencies.

⸻

Implementation Tasks (What Copilot Should Build)

1) uDOS GUI Launcher Script

Create a POSIX-compliant launcher, e.g. /usr/local/bin/udos-gui.

Responsibilities:
	•	Ensure persistence mount exists (e.g. /mnt/udos)
	•	Export required environment variables
	•	Ensure seatd is running (start if needed)
	•	Launch Cage with exactly one app
	•	Handle exit behaviour (TTY return or reboot)

Key environment considerations:
	•	XDG_RUNTIME_DIR (predictable path, e.g. /run/user/1000)
	•	Wayland-native execution only

Requirements:
	•	set -eu
	•	Log to persistent storage (/mnt/udos/logs/udos-gui.log)
	•	Clear error messages when graphics stack is unavailable

⸻

2) OpenRC Services

Implement OpenRC init scripts:
	•	seatd service
	•	Installed under /etc/init.d/seatd
	•	Enabled only for Tier 2 mode
	•	udos-gui service
	•	Installed under /etc/init.d/udos-gui
	•	Depends on seatd, localmount, optional net
	•	Executes cage -- /usr/local/bin/udos-ui
	•	Avoids respawn boot loops

Tier selection mechanism:
	•	Boot mode file: /etc/udos/mode
	•	tui (default)
	•	gui (Tier 2)
	•	Early OpenRC service reads mode and enables/disables udos-gui.

⸻

3) Tauri App Packaging Target

Produce a single executable:
	•	/usr/local/bin/udos-ui

Constraints:
	•	Must run without a desktop session
	•	Stores app data under /mnt/udos/var/ui
	•	Communicates with uDOS Core via:
	•	local HTTP (127.0.0.1:PORT) or
	•	unix socket

⸻

4) Persistence Strategy

Diskless Alpine requires explicit persistence.

Implement:
	•	Persistence partition (label: UDOS_PERSIST) mounted at /mnt/udos
	•	Bind-mount or symlink:
	•	/etc/udos → /mnt/udos/etc/udos
	•	Logs → /mnt/udos/logs
	•	UI state → /mnt/udos/var/ui

If using Alpine lbu / apkovl:
	•	Commit only minimal system config
	•	Keep app data separate from apkovl

⸻

5) Failure Modes & Recovery

System must handle:
	•	No DRM / GPU → fallback to TTY with clear message
	•	Missing packages → print required package list
	•	Tauri app crash → clean exit to TTY or reboot

Avoid:
	•	Infinite restart loops

⸻

Security & UX Rules
	•	No shell access from UI unless dev mode enabled
	•	No terminal launch buttons in production builds
	•	UI triggers uDOS Core actions via controlled API only
	•	Every installed package must be justified

⸻

Deliverables
	1.	udos-gui launcher script
	2.	OpenRC init scripts: seatd, udos-gui, and mode selector
	3.	Alpine package list (single source of truth)
	4.	Documentation: docs/tier2-one-app-gui.md
	5.	Optional build helper (Makefile or justfile)

⸻

Alpine Core Standards & Plugin Model (Migration from Tiny Core)

uDOS previously relied on Tiny Core Linux concepts such as .tcz extensions and tce-load. When migrating to Alpine Linux, uDOS must adopt Alpine-native primitives while preserving the plugin-oriented mental model.

Mapping: Tiny Core → Alpine

Tiny Core	Alpine Linux	uDOS Interpretation
.tcz extension	.apk package	uDOS plugin package
tce-load	apk add / del	Plugin enable / disable
onboot.lst	Plugin manifest file	Desired plugin state
TC backup/restore	apkovl (lbu)	Persisted system config
TC extension dir	APK repo + cache	Plugin distribution store

uDOS Plugin Strategy on Alpine
	•	All uDOS functionality is delivered as APK packages following the naming scheme:
	•	udos-core
	•	udos-net
	•	udos-wizard
	•	udos-gui
	•	udos-ui
	•	No custom binary plugin formats are introduced.
	•	Alpine’s package manager (apk) is the single source of truth for installed functionality.

Plugin Repositories

uDOS supports three repository models:
	1.	Local USB repository (default)
	•	Stored on persistence partition (e.g. /mnt/udos/repo)
	•	Contains .apk files and APKINDEX
	•	Added via /etc/apk/repositories
	2.	Remote uDOS repository (optional)
	•	Hosted by uDOS Wizard or CI
	•	Used for updates when network is available
	3.	Hybrid model
	•	Ship baseline repo snapshot on device
	•	Allow online updates without changing base OS

Plugin Manifest (Tiny Core onboot analogue)

uDOS defines a simple plugin manifest:
	•	File: /etc/udos/plugins.enabled
	•	Contents: one APK name per line

Boot or mode-switch logic ensures:

apk add $(cat /etc/udos/plugins.enabled)

This keeps system state declarative and reproducible.

Diskless Persistence Model
	•	System configuration: stored via apkovl (OpenRC services, mode flags, repo config)
	•	Downloaded APKs: stored in persistent APK cache (avoids re-download)
	•	Application data: stored under /mnt/udos and never inside the apkovl

This separation mirrors Tiny Core’s “extensions vs data” philosophy using Alpine-native tools.

Tier 2 Packaging

Tier 2 One-App GUI is delivered entirely via packages:
	•	udos-gui → Wayland, Cage, seatd, launcher, OpenRC services
	•	udos-ui → Tauri binary + runtime deps

Enabling Tier 2 = enabling packages + switching /etc/udos/mode to gui.

No filesystem mutation outside Alpine standards is permitted.

⸻

Definition of Done
	•	Tier 2 boots directly into uDOS UI on supported hardware
	•	Exiting UI follows defined return path
	•	No desktop packages installed
	•	Persistence verified across reboots
	•	Plugin enable/disable works via APK + manifest
	•	Tier 1 (TUI-only) remains default and functional