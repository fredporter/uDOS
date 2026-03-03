# Sonic Integration Spec - v1.5 Device Catalog and uHOME Install Lanes

Status: Active
Updated: 2026-03-03

This document aligns Sonic's public integration story to the active v1.5
`uHOME` scope in `docs/specs/UHOME-v1.5.md`.

For v1.5, Sonic's canonical `uHOME` alignment is:

- a tested standalone bundle installer for `uHOME Server`
- a bounded USB or image lane that can materialize either `uHOME Server` or
  `uHOME TV Node`
- node bootstrap that can hand off to Wizard-managed home-node and beacon
  networking
- packaging that may ship `uHOME` with thin GUI, Steam-console UX, or both
- device-catalog and launch-profile inputs that remain profile-aware rather than
  defining a separate `uHOME` runtime

Older Sonic hybrid-console or media-launcher briefs may remain in the repo as
historical exploration, but they are not the active v1.5 source of truth.

## 1. Device Database Contract

Sonic Screwdriver publishes its curated device catalog via `wizard.routes.sonic_plugin_routes`. Any Wizard/Sonic bolt-on can consume the same SQLite + Schema artifacts described here and bundle them for CLI/GUI consumers. The Wizard API routes keep the catalog discoverable both from the TUI (`PLUGIN list`) and from remote automation by exposing the same contract documented here.

### Storage
- Seed catalog sources: `sonic/datasets/`
- Seed runtime DB: `memory/sonic/seed/sonic-devices.seed.db`
- User runtime DB: `memory/sonic/user/sonic-devices.user.db`
- Legacy compatibility mirror: `memory/sonic/sonic-devices.db`
- Schema: `sonic/datasets/sonic-devices.schema.json`
- Markdown reference table: `sonic/datasets/sonic-devices.table.md`
- Seed rebuild source: `sonic/datasets/sonic-devices.sql`
- Datasets folder also hosts `sonic-devices.csv` for bulk editing before rebuilding.

Normal-user contract:
- seed catalog is distributed and read-only
- user catalog is local, writable, and overlays seed records at read time
- current-machine bootstrap records live in the user catalog
- both layers may carry `*_template_md` refs

### Key Fields (device record)

| Field | Description |
|---|---|
| `id` | Unique slug (vendor-model-variant) |
| `vendor`, `model`, `variant` | Human identifiers |
| `year`, `cpu`, `gpu`, `ram_gb`, `storage_gb` | Performance profile |
| `bios`, `secure_boot`, `tpm` | Firmware/security capabilities |
| `usb_boot`, `uefi_native`, `reflash_potential` | Sonic/boot readiness |
| `methods` | JSON array, e.g. `["sonic_usb","wizard_netboot"]` |
| `notes`, `sources` | Freeform guidance |
| `last_seen` | Last update timestamp |
| `settings_template_md` | Obsidian-style Markdown template for configurable settings |
| `installers_template_md` | Obsidian-style Markdown template for installer flows |
| `containers_template_md` | Obsidian-style Markdown template for container/service notes |
| `drivers_template_md` | Obsidian-style Markdown template for driver/firmware notes |

### Wizard API Endpoints
- `GET /api/sonic/health` – quick availability summary & rebuild hints.
- `GET /api/sonic/schema` – JSON schema for validation.
- `GET /api/sonic/devices` – paginated catalog with filters: `vendor`, `reflash_potential`, `usb_boot`, `uefi_native`.
- `GET /api/sonic/db/status` – DB sync status alias.
- `POST /api/sonic/db/rebuild` – DB rebuild alias.
- `GET /api/sonic/db/export` – DB export alias.
- `POST /api/sonic/bootstrap/current` – register the current machine in the local user catalog.

Consumers should respect the `methods` array to know whether a device supports
`sonic_usb`, native UEFI boot, or additional profile-specific install methods.
Template fields should be treated as open-box Markdown references, not embedded opaque payloads.

### Syncing Plan
1. Build tool (`wizard.routes.sonic_plugin_routes`) exports `devices` so dashboards show current catalog.
2. Seed rebuild refreshes `memory/sonic/seed/sonic-devices.seed.db` from `sonic/datasets/sonic-devices.sql`.
3. User imports and current-machine bootstrap write only to `memory/sonic/user/sonic-devices.user.db`.
4. UI/automation can poll `/api/sonic/health` or `/api/sonic/sync/status` and show quick instructions when the seed catalog is stale or the current machine has not yet been registered.

## 2. USB Builder API (Plan + Run)

Sonic exposes two CLI verbs via `core/sonic_cli.py` plus helper scripts for partitioning/payloads. Wizard bolt-ons can wrap or invoke these commands over SSH/CLI.

### Commands
```bash
python3 core/sonic_cli.py plan \
  --usb-device /dev/sdX \
  --layout-file config/sonic-layout.json \
  --out memory/sonic/sonic-manifest.json

python3 core/sonic_cli.py run \
  --manifest memory/sonic/sonic-manifest.json \
  [--dry-run]
```

### Manifest expectations (`core/plan.py`)
- `usb_device` – raw block device.
- `layout` – `config/sonic-layout.json` describing partition labels/payloads.
- `payloads` mapping partitions to directories within `payloads/`.
- `windows_mode` – `install` or `wtg`.
- `device_profile` – matches `devices.id` from sonic DB to set `windows10_boot`, `media_mode`.

Primary post-plan steps:
1. `scripts/partition-layout.sh` uses manifest partitions to set GPT entries, format them, and create labels.
2. `scripts/apply-payloads-v2.sh` mounts partitions and copies from `payloads/`.
3. `scripts/sonic-stick.sh` (run phase) executes payload application, installs grub/bootloaders, and finalizes Windows payloads (ISO extraction or WTG injection).

Wizard bolt-ons should treat the plan/run APIs as a two-phase contract: the
plan command returns a manifest JSON plus `sha256(layout)` so a UI can verify
the payload before running. The run phase consumes that manifest; it is
idempotent but destructive, so the TUI should prompt users before executing the
plan. Logging from both CLI commands should be captured in
`memory/sonic/sonic-flash.log` so `PLUGIN` or `WIZARD` pages can surface
execution history.

### v1.5 `uHOME` alignment for USB and image builds

For v1.5, any `uHOME`-aligned USB or image build must:

1. resolve to one deployment role:
   - `uHOME Server`
   - `uHOME TV Node`
2. stay consistent with `docs/specs/UHOME-v1.5.md`
3. support node bootstrap only up to the point of handing networking control to
   Wizard-owned surfaces
4. avoid claiming mandatory dual-boot gaming or Windows media-launcher behavior
   unless backed by active implementation and acceptance evidence
5. reuse the same component and config concepts as the standalone bundle lane
   where practical
6. support packaging of thin GUI, Steam-console UX, or both as presentation
   surfaces for the deployed node

### Wizard networking handoff

Sonic's v1.5 role is to prepare a deployable node. After install, node
networking and managed control must hand off to Wizard-owned services.

For `uHOME` this includes:

- LAN-local home-node operation by default
- optional enrollment into Wizard-managed beacon or tunnel flows
- no Sonic-owned long-running network control protocol
- no requirement for the full `uDOS/core` runtime in standalone Sonic or
  standalone `uHOME` distributions

## 3. Standalone uHOME bundle installer

The standalone bundle installer is the strongest current `uHOME` install
surface and is the canonical Sonic lane for `uHOME Server`.

Authoritative code:

- `sonic/core/uhome_bundle.py`
- `sonic/core/uhome_installer.py`
- `sonic/core/uhome_preflight.py`

Install contract summary:

- artifact manifest: `uhome-bundle.json`
- verification: checksum validation per component
- rollback: optional rollback token and snapshot record support
- preflight: hardware profile gating
- plan phases:
  - `preflight`
  - `verify`
  - `stage`
  - `configure`
  - `enable`
  - `finalize`

Current canonical bundle components:

- `jellyfin`
- `comskip`
- `hdhomerun_config`
- `udos_uhome`

Bundle variants may additionally stage:

- thin-GUI presentation assets
- Steam-console launcher assets
- both presentation layers side by side

## 4. Home-node and beacon alignment

Sonic must treat `uHOME` node networking as a Wizard contract.

### Home-node rollout expectations

- a `uHOME Server` deployment may advertise or expose Wizard-managed control
  endpoints after install
- a `uHOME TV Node` deployment may be prepared as a playback-facing node that
  later enrolls with the household server and optional Wizard network control
- a deployment may expose thin GUI, Steam-console UX, or both on the same node
- Sonic documentation must describe node role selection directly rather than
  relying on older hybrid-console narratives

### Beacon alignment

When a deployment uses Wizard beacon networking:

- Sonic may install the node with the files and profile needed for later beacon
  enrollment
- Wizard routes under `/api/beacon/*` remain the active runtime control surface
- beacon configuration, tunnel status, quotas, and cache operations remain
  Wizard-owned

## 5. Wizard plugin installation flow

Plugin installs flowing through the Core `PLUGIN install <id>` command should reuse the same repository index/manifest validation logic that Wizard already exposes:

1. `core/tui/ucode.py` copies `/wizard/distribution/plugins/<id>` into `/library/<id>` and writes `container.json` metadata so the Wizard `LibraryManagerService` can load it.
2. The CLI then calls `LibraryManagerService.install_integration`, which enforces dependency wiring, runs setup scripts, and optionally builds APK bundles for the plugin.
3. `wizard.services.plugin_repository.PluginRepository` keeps track of available plugins, manifest checksums, and whether a plugin is already installed so the CLI can report upgrade availability.
4. Add hooks from the Wizard `plugin_repository` into _the same_ Sonic/USB story so plugin install actions can trigger schema validation (`GET /api/sonic/schema`) before enabling new media/USB tooling.

## 6. Wizard and Home Assistant control-plane alignment

For `uHOME`, Wizard integration is bounded to control-plane ownership rather
than install ownership.

Current `uHOME`-relevant Wizard surfaces:

- Home Assistant bridge routes under `/api/ha/`
- `uhome.*` command dispatch for tuner, DVR, ad-processing, and playback
- optional config-controlled bridge enablement

This remains optional for v1.5 and does not define install validity by itself.

## 7. Sonic scope guardrails for v1.5

To keep the active scope stable:

- treat the device catalog and launch-profile decisions as install inputs, not as
  a replacement for the `uHOME` runtime spec
- keep older hybrid-console, launcher-heavy, or dual-boot product exploration
  docs non-canonical unless promoted by active implementation
- prefer the tested standalone bundle contract when documenting `uHOME Server`
- keep the USB or image lane profile-aware and bounded when documenting
  `uHOME TV Node`
- align node networking and beacon behavior to Wizard's active route and service
  contracts

## 8. Related documents

- `docs/specs/UHOME-v1.5.md`
- `docs/decisions/uHOME-spec.md`
- `docs/decisions/SONIC-DB-SPEC-GPU-PROFILES.md`
- `docs/decisions/HOME-ASSISTANT-BRIDGE.md`
- `wizard/docs/BEACON-IMPLEMENTATION.md`
