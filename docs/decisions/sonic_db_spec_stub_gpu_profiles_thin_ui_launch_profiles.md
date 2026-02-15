# Sonic DB Spec Stub

## GPU Profiles + Thin UI Launch Profiles

This spec is implemented via Sonic DB launch profiles.

The launcher must not invent flags outside Sonic DB except for safe defaults.
The launcher must materialize and/or consume:

- `machines`
- `gpu_profiles`
- `ui_bundles`
- `ui_launch_profiles`

Then execute the resulting plan deterministically.



# 1. Purpose

This document defines the minimal Sonic DB schema stubs required to support:

- GPU driver selection (Intel / AMD / Headless)
- Thin UI launch profile generation (Alpine Chromium Kiosk)
- UI parity hooks for Windows (Tauri) and Alpine (Chromium)

Sonic DB is the source of truth. Launchers are deterministic.

---

# 2. Data Model Overview

Sonic DB stores **machine capability** and **launch intent**.

- `machines` → stable machine identity + discovery facts
- `gpu_profiles` → driver packages + rendering mode + launch flags
- `ui_bundles` → UI versions and build metadata
- `ui_launch_profiles` → resolved launch plans per machine + UI bundle

---

# 3. Canonical Keys

## 3.1 Machine ID

A stable identifier that does not change across reboots.

Recommended (conceptual):

- `machine_id`: `LOC-...` (or LocId + hardware fingerprint)

## 3.2 Profile IDs

- `gpu_profile_id`: string (e.g. `gpu-intel-mesa-v1`)
- `ui_bundle_id`: string (e.g. `ui-2026.02.15+001`)
- `ui_launch_profile_id`: string (e.g. `launch-<machine_id>-<ui_bundle_id>`)

---

# 4. Schema Stubs

This is intentionally minimal and JSON-first.

## 4.1 `machines`

```json
{
  "machine_id": "LOC-AU-BNE-0001",
  "label": "alpine-core-lounge",
  "role": "core",
  "os": {
    "family": "alpine",
    "arch": "x86_64",
    "version": "3.x"
  },
  "hardware": {
    "cpu": "intel",
    "pci": {
      "gpu": {
        "vendor": "intel",
        "device_id": "8086:0000",
        "class": "0300"
      }
    }
  },
  "network": {
    "hostname": "core.local",
    "ip": "192.168.1.50"
  },
  "created_at": "2026-02-15T00:00:00+10:00",
  "updated_at": "2026-02-15T00:00:00+10:00"
}
```

Fields:

- `role`: `core | wizard | winbox | control | vm`
- `os.arch`: `aarch64 | x86_64`
- `hardware.pci.gpu.vendor`: `intel | amd | nvidia | headless`

---

## 4.2 `gpu_profiles`

A GPU profile expresses:

- rendering mode
- package set
- chromium flags
- wayland/compositor notes

```json
{
  "gpu_profile_id": "gpu-intel-mesa-v1",
  "vendor": "intel",
  "mode": "hw",
  "stack": "mesa",
  "packages": [
    "mesa",
    "mesa-dri-gallium",
    "libdrm"
  ],
  "kernel": {
    "driver": "i915",
    "firmware": []
  },
  "chromium": {
    "flags": [
      "--ozone-platform=wayland"
    ]
  },
  "notes": "Default Intel iGPU profile. Validate VAAPI before enabling.",
  "schema_version": 1
}
```

AMD example:

```json
{
  "gpu_profile_id": "gpu-amd-mesa-v1",
  "vendor": "amd",
  "mode": "hw",
  "stack": "mesa",
  "packages": [
    "mesa",
    "mesa-dri-gallium",
    "libdrm"
  ],
  "kernel": {
    "driver": "amdgpu",
    "firmware": ["linux-firmware"]
  },
  "chromium": {
    "flags": [
      "--ozone-platform=wayland"
    ]
  },
  "notes": "AMD profile. Firmware may be required depending on card.",
  "schema_version": 1
}
```

Headless / software example:

```json
{
  "gpu_profile_id": "gpu-headless-sw-v1",
  "vendor": "headless",
  "mode": "sw",
  "stack": "mesa",
  "packages": [
    "mesa",
    "mesa-dri-gallium",
    "libdrm"
  ],
  "kernel": {
    "driver": "none",
    "firmware": []
  },
  "chromium": {
    "flags": [
      "--disable-gpu",
      "--disable-software-rasterizer=false"
    ]
  },
  "notes": "Use in VMs or no-DRM environments.",
  "schema_version": 1
}
```

---

## 4.3 `ui_bundles`

A UI bundle is the canonical UI release that all shells must align to.

```json
{
  "ui_bundle_id": "ui-2026.02.15+001",
  "name": "udos-ui",
  "framework": "sveltekit",
  "styling": "tailwind",
  "build": {
    "type": "static",
    "entry": "/opt/udos/ui/index.html",
    "asset_root": "/opt/udos/ui/"
  },
  "compat": {
    "alpine": {"engine": "chromium", "min_version": "stable"},
    "windows": {"engine": "webview2", "min_version": "stable"}
  },
  "sonic_schema": {
    "min": 1,
    "max": 1
  },
  "created_at": "2026-02-15T00:00:00+10:00"
}
```

---

## 4.4 `ui_launch_profiles`

A launch profile binds:

- machine
- UI bundle
- GPU profile
- resolved packages
- final command lines

Alpine (Chromium kiosk) example:

```json
{
  "ui_launch_profile_id": "launch-LOC-AU-BNE-0001-ui-2026.02.15+001",
  "machine_id": "LOC-AU-BNE-0001",
  "ui_bundle_id": "ui-2026.02.15+001",
  "platform": "alpine",
  "shell": "cage+chromium",
  "gpu_profile_id": "gpu-intel-mesa-v1",
  "packages": {
    "apk": ["cage", "chromium", "mesa", "mesa-dri-gallium", "libdrm"]
  },
  "env": {
    "XDG_RUNTIME_DIR": "/run/user/0",
    "UDOS_LOG_ROOT": "~/memory/logs"
  },
  "launch": {
    "compositor": {
      "bin": "/usr/bin/cage",
      "args": ["--"]
    },
    "app": {
      "bin": "/usr/bin/chromium",
      "args": [
        "--kiosk",
        "--no-first-run",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--ozone-platform=wayland",
        "file:///opt/udos/ui/index.html"
      ]
    }
  },
  "logging": {
    "stdout": "~/memory/logs/udos-gui.out.log",
    "stderr": "~/memory/logs/udos-gui.err.log"
  },
  "schema_version": 1,
  "created_at": "2026-02-15T00:00:00+10:00",
  "updated_at": "2026-02-15T00:00:00+10:00"
}
```

Windows (Tauri) example (alignment record):

```json
{
  "ui_launch_profile_id": "launch-LOC-AU-BNE-WIN01-ui-2026.02.15+001",
  "machine_id": "LOC-AU-BNE-WIN01",
  "ui_bundle_id": "ui-2026.02.15+001",
  "platform": "windows",
  "shell": "tauri",
  "engine": "webview2",
  "mode": "windowed",
  "logging": {
    "file": "%USERPROFILE%\\memory\\logs\\udos-ui.log"
  },
  "schema_version": 1
}
```

---

# 5. Resolution Rules (Deterministic)

The launcher resolves a launch profile as follows:

1. Identify machine (`machine_id`) and detect GPU facts (PCI)
2. Choose `gpu_profile_id` based on:
   - `hardware.pci.gpu.vendor`
   - presence/absence of DRM device
   - optional override in Sonic DB
3. Choose `ui_bundle_id` based on:
   - pinned release channel
   - or explicit version lock
4. Materialise `ui_launch_profiles` and persist it
5. Execute launch plan

No hidden heuristics. Everything explainable from Sonic DB.

---

# 6. Thin UI Wiring Points

The Thin UI launcher must:

- Read `ui_launch_profiles` (or generate it if missing)
- Install missing packages from offline APK repo if configured
- Start the compositor + app exactly as specified
- Log all decisions and final command

The UI itself must be able to display:

- active `ui_bundle_id`
- active `gpu_profile_id`
- rendering mode (`hw` vs `sw`)
- last launch outcome and logs

---

# 7. Minimal API Surface (Optional)

If Sonic DB is accessed via a local service, expose only:

- `GET /machines/:id`
- `GET /gpu_profiles/:id`
- `GET /ui_bundles/:id`
- `GET /ui_launch_profiles/:id`
- `POST /ui_launch_profiles/resolve?machine_id=...&ui_bundle_id=...`

All responses are JSON.

---

# 8. Versioning

- Each object contains `schema_version`
- UI bundles declare supported Sonic DB schema range
- Launchers refuse to run if schema is incompatible

---

END OF SPEC
