# Sonic Integration Spec - Devices, USB Builder & Media Launcher

## 1. Device Database Contract

Sonic Screwdriver publishes its curated device catalog via `wizard.routes.sonic_routes`. Any Wizard/Sonic bolt-on can consume the same SQLite + Schema artifacts described here and bundle them for CLI/GUI consumers. The Wizard API routes keep the catalog discoverable both from the TUI (`PLUGIN list`) and from remote automation by exposing the same contract documented here.

### Storage
- Database: `memory/sonic/sonic-devices.db`
- Schema: `sonic/datasets/sonic-devices.schema.json`
- Markdown reference table: `sonic/datasets/sonic-devices.table.md`
- Seed script: `sqlite3 memory/sonic/sonic-devices.db < sonic/datasets/sonic-devices.sql`
- Datasets folder also hosts `sonic-devices.csv` for bulk editing before rebuilding.

### Key Fields (device record)

| Field | Description |
|---|---|
| `id` | Unique slug (vendor-model-variant) |
| `vendor`, `model`, `variant` | Human identifiers |
| `year`, `cpu`, `gpu`, `ram_gb`, `storage_gb` | Performance profile |
| `bios`, `secure_boot`, `tpm` | Firmware/security capabilities |
| `usb_boot`, `ventoy`, `reflash_potential` | Sonic/boot readiness |
| `methods` | JSON array, e.g. `["sonic_usb","wizard_netboot"]` |
| `notes`, `sources` | Freeform guidance |
| `last_seen` | Last update timestamp |

### Wizard API Endpoints
- `GET /api/v1/sonic/health` – quick availability summary & rebuild hints.
- `GET /api/v1/sonic/schema` – JSON schema for validation.
- `GET /api/v1/sonic/table` – Markdown table for dashboards/docs.
- `GET /api/v1/sonic/devices` – paginated catalog with filters: `vendor`, `reflash_potential`, `usb_boot`, `ventoy`.

Consumers should respect the `methods` array to know whether a device supports `windows10_boot`, `media_mode`, `sonic_usb`, or `ventoy`. The `wizard.routes.sonic_routes` router can also return `manifest_verified` and `dependencies` fields so installers can enforce manifest validation and dependency wiring before calling the library manager.

### Syncing Plan
1. Build tool (`wizard.routes.sonic_routes`) exports `devices` so dashboards show current catalog.
2. Any `devices.db` refresh should overwrite `memory/sonic/sonic-devices.db` and trigger `sqlite3 ... < sonic/datasets/sonic-devices.sql`.
3. UI/automation can poll `/api/v1/sonic/health` and show quick instructions when the DB is stale.

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

Wizard bolt-ons should treat the plan/run APIs as a two-phase contract: the plan command returns a signed manifest JSON plus `sha256(layout)` so a UI can verify the payload before running. The run phase consumes that manifest; it is idempotent but destructive, so the Core TUI should prompt users before executing the plan. Logging from both CLI commands should be captured in `memory/sonic/sonic-flash.log` so `PLUGIN` or `WIZARD` pages can surface execution history.

Wizard bolt-ons should treat plan/run as a two-phase API: the plan response is a manifest JSON plus a `sha256` of the layout; the run script is idempotent but destructive so the UI must warn users before launching.

## 3. Windows Gaming & Media Launcher Requirements

Sonic expects a Windows payload to include the following bits so Wizard can script the final launcher:

### Launch Modes
| Mode | Details |
|---|---|
| `gaming` | Boots Windows with GPU drivers + command shortcuts (Steam, Epic). Maximum perf. |
| `media` | Boots Kodi/WantMyMTV with limited desktop; remote control friendly. |
| `wtg` | Windows-to-Go partition for direct boot, used when reinstalling Windows fails. |

### Launch Hooks (Wizard & uDOS)
1. **Boot profile metadata** stored in `payloads/windows/settings.json`:
   ```json
   {
     "mode": "media",
     "launcher": "wantmymtv",
     "auto_repair": true,
     "sound_profile": "dolby",
     "device_profile": "dell-precision-7920"
   }
   ```
2. uDOS/Wizard uses `payloads/windows/scripts/launch-windows.sh` to switch boot order, optionally install QoS/driver updates, and update `devices.db` with `windows10_boot` status.
3. Media player logging writes to `memory/sonic/sonic-media.log` which Wizard monitors to detect playback errors and feed back to the UI.

### Media Player Checklist
- **Kodi**: Must have `kodi-standalone.sh` that sets `KODI_USER_HOME=SONIC_MEDIA_HOME`.
- **WantMyMTV**: Requires `wmmtv-launcher` to load playlists from `payloads/media/playlists.json`.
- **Plex (optional)**: Should include a service definition for `plexmediaserver.service` with dependencies on `sonic-media-network.service`.

Wizard interfaces should expose a “Media Launch” panel that:
1. Lists available launchers per platform (Kodi, WantMyMTV, Plex).
2. Provides `Start/Stop` buttons that call `scripts/media-controller.sh <launcher>`.
3. Shows auto-detected device capabilities (via `/api/v1/sonic/devices?media_mode=htpc`).

## 4. Wizard Plugin Installation Flow

Plugin installs flowing through the Core `PLUGIN install <id>` command should reuse the same repository index/manifest validation logic that Wizard already exposes:

1. `core/tui/ucode.py` copies `/wizard/distribution/plugins/<id>` into `/library/<id>` and writes `container.json` metadata so the Wizard `LibraryManagerService` can load it.
2. The CLI then calls `LibraryManagerService.install_integration`, which enforces dependency wiring, runs setup scripts, and optionally builds APK bundles for the plugin.
3. `wizard.services.plugin_repository.PluginRepository` keeps track of available plugins, manifest checksums, and whether a plugin is already installed so the CLI can report upgrade availability.
4. Add hooks from the Wizard `plugin_repository` into _the same_ Sonic/USB story so plugin install actions can trigger schema validation (`GET /api/v1/sonic/schema`) before enabling new media/USB tooling.

## 5. Sonic Gap Catalog & Roadmap

To keep the Sonic/UWizard capability visible to future rounds:

- Track missing APIs and feature gaps (USB builder scripts, device database syncing, Windows media launcher) by updating this doc and linking to `ROUNDS-3-10.md`.
- Document the Sonic Screwdriver ″gap targets″ for USB flashing (`core/sonic_cli.py plan|run`), the device DB sync webhook (`/api/v1/sonic/sync`), and the Windows media launcher contract (`payloads/windows/settings.json` plus `media-controller.sh`).
- Surface `memory/sonic/sonic-devices.db` updates (new columns `wizard_profile`, `media_launcher`) in the Wizard dashboard so the TUI/Wizard story can display the planned capability list.
