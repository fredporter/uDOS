# uDOS Alpine Thin GUI Runtime Spec

## Chromium Kiosk Standard

---

# 1. Objective

Define the official uDOS thin GUI runtime for Alpine Core using:

- Chromium
- Wayland
- Cage (single-app compositor)
- SvelteKit + Tailwind UI bundle

This replaces any previous discussion of "simple browsers" or experimental engines.

The goal is:

- Stable
- Minimal
- Offline-capable
- Single visible process
- Reproducible
- Packageable via offline installer

---

# 2. Architectural Principle

Thinness is achieved by minimising the OS layer, not by chasing smaller browser engines.

The runtime stack is:

```
Alpine Linux (minimal)
  └── Wayland
        └── Cage (kiosk compositor)
              └── Chromium (kiosk mode)
                    └── uDOS UI (SvelteKit static build)
```

No desktop environment. No display manager. No background session services.

---

# 3. Core Runtime Components

## 3.1 Alpine Base

- Alpine Linux (latest stable)
- musl-based
- Minimal install profile
- OpenRC init

Required packages:

- wayland
- cage
- chromium
- mesa / GPU drivers (hardware dependent)
- font packages (minimal system + chosen UI fonts)

---

## 3.2 Compositor: Cage

Cage is selected because:

- Single-window Wayland compositor
- Designed for kiosk environments
- Extremely lightweight
- No desktop environment required

Cage ensures:

- Only one visible application
- Automatic full-screen
- No window switching

---

## 3.3 Browser Engine: Chromium

Chromium is selected because:

- Stable and mature
- Full modern JS/CSS support
- Tailwind-compatible
- SvelteKit-compatible
- Good Wayland support
- Available in Alpine repositories
- Predictable dependency tree

Chromium runs in kiosk mode.

Example launch:

```
cage -- chromium --kiosk --no-first-run --disable-infobars \
  --disable-session-crashed-bubble \
  file:///opt/udos/ui/index.html
```

Or local service mode:

```
cage -- chromium --kiosk http://127.0.0.1:3000
```

---

# 4. UI Bundle Standard

## 4.1 Source of Truth

- SvelteKit
- Tailwind CSS
- Static build output

Build command:

```
npm run build
```

Output directory copied to:

```
/opt/udos/ui/
```

---

## 4.2 Runtime Modes

The UI must support:

- Mode A - Standalone (local only)
- Mode B - Wizard Client (connects to Ubuntu server)
- Mode C - Hybrid

Switching modes must not require rebuild.

---

# 5. Offline Installer Strategy

## 5.1 APK Mirror

To support fully offline deployment:

- Mirror required Alpine APK packages
- Host local APK repository on installer media

Directory example:

```
/install/
  ├── apk-repo/
  ├── ui-build/
  ├── install.sh
```

Install script will:

1. Install required packages from local repo
2. Copy UI bundle to /opt/udos/ui/
3. Install OpenRC service for kiosk launch
4. Enable service

---

## 5.2 OpenRC Service Example

Service file: `/etc/init.d/udos-gui`

Responsibilities:

- Start cage
- Launch chromium in kiosk mode
- Restart on crash

Pseudo-structure:

```
#!/sbin/openrc-run

command="/usr/bin/cage"
command_args="-- /usr/bin/chromium --kiosk file:///opt/udos/ui/index.html"
command_background=false

respawn_delay=2
```

Enable:

```
rc-update add udos-gui default
```

---

# 6. GPU Driver Matrix (Intel / AMD / Headless)

This section defines the official GPU driver handling for the Alpine Thin GUI runtime.

uDOS manages GPU configuration via **Sonic DB** (hardware capability registry) and wires the results into the Thin UI launcher.

## 6.1 Sonic DB: GPU Capability Records

Sonic DB stores a device profile keyed by a stable machine identifier (e.g. LocId + hardware fingerprint), containing:

- GPU vendor and device IDs
- Driver path and package set
- Rendering mode (hardware vs software)
- Chromium + Wayland launch flags

Example Sonic DB record (conceptual):

```json
{
  "machine_id": "LOC-...",
  "gpu": {
    "vendor": "intel",
    "pci_id": "8086:...",
    "mode": "hw",
    "stack": "mesa",
    "packages": ["mesa", "mesa-dri-gallium", "libdrm"],
    "chromium_flags": ["--ozone-platform=wayland"],
    "notes": "Use i915 kernel driver; VAAPI optional"
  }
}
```

Sonic DB is the single source of truth for the GUI launcher’s GPU decisions.

## 6.2 Driver Matrix

| Target | Sonic DB `gpu.vendor` | Alpine packages (baseline) | Kernel/driver notes | Chromium/Wayland notes |
|---|---|---|---|---|
| Intel iGPU | `intel` | `mesa`, `mesa-dri-gallium`, `libdrm` (+ optional VAAPI packages) | Typically i915; confirm DRM node exists | Prefer Wayland Ozone; enable VAAPI only when validated |
| AMD GPU | `amd` | `mesa`, `mesa-dri-gallium`, `libdrm` | amdgpu; firmware may be required depending on card | Wayland Ozone; avoid experimental flags unless needed |
| Headless / No GPU | `headless` | `mesa`, `mesa-dri-gallium`, `libdrm` (software path) | No DRM device expected | Force software rendering; disable GPU acceleration |

Notes:

- Keep **Mesa** as the default graphics stack for Intel/AMD.
- Headless mode exists for:
  - VM environments
  - weak GPUs
  - remote/virtual display targets
- Any device-specific extras must be represented in Sonic DB `packages`.

## 6.3 Thin UI Wiring (Sonic DB → Launcher)

The Thin UI layer reads Sonic DB at boot and generates the final launch profile:

1. Detect hardware (PCI scan) and resolve to Sonic DB profile
2. Ensure required packages are installed (offline repo supported)
3. Select `gpu.mode`:
   - `hw` → default
   - `sw`/`headless` → software rendering
4. Compose final command:

### Hardware (Intel/AMD) example

```
GPU_FLAGS="--ozone-platform=wayland"

cage -- chromium --kiosk --no-first-run --disable-infobars \
  --disable-session-crashed-bubble \
  $GPU_FLAGS \
  file:///opt/udos/ui/index.html
```

### Headless / Software example

```
GPU_FLAGS="--disable-gpu --disable-software-rasterizer=false"

cage -- chromium --kiosk --no-first-run --disable-infobars \
  --disable-session-crashed-bubble \
  $GPU_FLAGS \
  file:///opt/udos/ui/index.html
```

The launcher must log:

- chosen Sonic DB profile
- resolved packages
- final command line

Logs go to `~/memory/logs/` per uDOS logging standard.

---

# 7. UI Layer Contract (Tailwind + SvelteKit)

This ensures the Thin UI wrapper and the Windows Tauri shell render the *same* experience.

## 7.1 Tailwind Requirements

- Tailwind is the styling source of truth
- Use Tailwind Typography (Prose) for document rendering
- Use system-first fonts (uDOS font utilities)
- No per-platform CSS forks

## 7.2 SvelteKit UI Elements

Minimum shared UI components (must exist in the UI bundle):

- App Shell Layout
  - Top bar / status strip
  - Primary navigation
  - Content viewport
- Panels
  - Card
  - Table
  - List
  - Modal / Drawer
- System views
  - Logs viewer (from `~/memory/logs/`)
  - Network status
  - Device/GPU profile summary (from Sonic DB)

These components must be:

- keyboard-first
- responsive to 80x30 grid constraints
- compatible with kiosk full-screen

---

# 8. Resource Profile

Estimated idle footprint:

- Chromium: 150–300MB RAM
- Cage: minimal overhead
- Alpine base: extremely small

This is acceptable for:

- 2–4GB RAM systems
- Thin hardware
- Embedded-style deployments

The thinness comes from eliminating full desktop stacks.

---

# 9. What We Are NOT Using

- No GNOME
- No KDE
- No X11 (Wayland preferred)
- No Electron
- No experimental browser engines
- No Swift-based wrapper

---

# 8. Future Optimisation Track (Optional)

If future performance work is required:

- Evaluate WPE WebKit
- Evaluate GPU tuning flags
- Evaluate disabling unnecessary Chromium features

These are Phase 2 optimisations.

They are not required for initial release.

---

# 11. Alignment with uDOS Philosophy

This runtime:

- Preserves minimal core
- Maintains modular layering
- Avoids cloud dependency
- Enables offline-first deployments
- Keeps Windows and Ubuntu roles separate
- Allows identical UI across all platforms

Mac = Control Plane Windows = Gaming / Compatibility Ubuntu = Wizard Server Alpine = Core + Thin GUI Wrapper (Chromium Kiosk)

---

# 12. Final Standard

Official Alpine GUI Runtime:

Chromium + Cage + Wayland

Single UI bundle. Single visible process. Offline reproducible.

This is the uDOS Thin GUI Standard.

---

END OF SPEC
