# Wizard + Sonic Plugin Ecosystem (v1.1+)
This reference describes the restored all-in-one Wizard config dashboard, the Sonic Screwdriver device/media APIs, and the hotkey + GUI tooling coverage that keeps the Plugin Ecosystem story visible for rounds 3‑10.

## Wizard Central Config

The config page (`http://127.0.0.1:8765/config`) now owns the full lifecycle:

- **.venv management** at the top ensures dependency isolation is complete before any Wizard helpers run. You can create, inspect, or recreate the `.venv` that powers the dashboard, CLI helpers, and plugin installers.
- **Wizard API / Secret store** entries follow, showing each key/secret name with rotate buttons powered by `wizard/services/secret_store.py`. All updates go through the keystore so nothing leaks into ad-hoc files.
- **Extension / API installers** sit next. They read manifests from `wizard/distribution/plugins/`, validate them with `wizard/services/plugin_repository.py`, and install through `wizard/services/library_manager_service.py`. The Core `PLUGIN install` command (see `core/tui/ucode.py::_plugin_install`) calls the same services so CLI installs share manifest validation, signature checks, and dependency wiring with the GUI buttons, and the config page buttons call `/api/v1/config/secret/<key_id>/rotate` and `/api/v1/library/integration/<name>/install` for the same effects.
- **Hotkey Center** perches beside the installers so every config change stays tethered to key bindings that expose TAB, F1‑F8, and arrow-history behavior.

Ordering the panel as `.venv → secrets → installers → hotkeys` makes the config view the single place for runtime bootstrap, credential rotation, and extension lifecycle control.

## Wizard Hotkey Center

The Hotkey Center (`http://127.0.0.1:8765/hotkeys`) mirrors the key bindings embedded in `core/tui/fkey_handler.py`, `input/smart_prompt.py`, and `core/ui/command_selector.py`:

- Documents the F1–F8 shortcuts and highlights the Tab command selector so users know which keys keep the prompt lively even when `prompt_toolkit` is unavailable.
- Explains how the two-line context display uses `EnhancedPrompt` and why automation scripts that inspect `memory/logs/health-training.log` rely on the same keys to re-run hot reload/self-heal rounds.
- Gives quick links to the CLI fallback bindings (Arrow ↑/↓ history, Tab variants) so ghost or headless sessions can still surface suggestions.
- Mentions the `HOTKEYS` CLI command introduced in `core/commands/hotkey_handler.py` and the `/hotkeys/data` JSON payload so the same key map is traceable from both CLI and dashboard surfaces.

Keeping hotkey mappings centralized makes the dashboard the authoritative reference for CLI key bindings and automation scripts that train hot reload/self-heal behavior every round.

## Plugin Installer & Manifest Flow

Plugin installation now flows through Wizard-native services:

- `core/tui/ucode.py` copies `wizard/distribution/plugins/<id>` into `/library/<id>`, writes a `container.json` payload, then calls `wizard/services/library_manager_service.LibraryManagerService.install_integration`. That service validates the manifest, runs dependency wiring hooks, and emits a `result` object with `success`, `message`, and `error`.
- `wizard/services/plugin_repository.get_repository()` powers both the config page and the CLI `PLUGIN` command, so every install fetches the same metadata and version hints.
- The Dashboard buttons, the CLI `PLUGIN install`, and automation scripts all log plugin installations to `memory/logs/health-training.log`, ensuring manifest/verification errors appear in the same health summary the TUI banner prints.


## Repair + Backup Flow

- `REPAIR --refresh-runtime` clears runtime caches (`.venv`, `extensions/`, dashboard bundles, `memory/wizard`, plugin caches) and calls `wizard/services/library_manager_service.LibraryManagerService` to reinstall every enabled integration with the same dependency wiring that the config page uses.
- `REPAIR --install-plugin <id>` speaks directly to the Wizard plugin catalog so maintenance scripts can force a reinstall of a single integration using the same manifest validation hooks that power the GUI buttons.
- `BACKUP`, `RESTORE`, and the new `UNDO` command all work with `<scope>/.backup/<timestamp>-<label>.tar.gz` archives (tar + gzip) so we follow Alpine’s conventions; `UNDO` simply re-applies the most recent archive and can be run from scripts or the TUI to roll back the last backup point.

These maintenance paths keep caches aligned with Wizard’s plugin/distribution library (`wizard/services/plugin_repository.py` + `wizard/services/library_manager_service.py`) so the repair command can always reach back into the same catalog the config page and Sonic workflows rely on.

## Sonic Device Database & USB Builder APIs

The Sonic Screwdriver wiring spans CLI, datasets, and runtime state:

- `sonic/core/sonic_cli.py` exposes `plan` and `run` subcommands. `plan` accepts `--usb-device`, `--layout-file`, `--ventoy-version`, `--payloads-dir`, `--format-mode`, and `--dry-run` to emit a signed manifest using `sonic/core/manifest.py` and `sonic/core/plan.py`.
- Manifest validation references `sonic/datasets/sonic-devices.schema.json`, while the data itself originates from `sonic/datasets/sonic-devices.sql`. At runtime this dataset syncs into `memory/sonic/sonic-devices.db`, which the Wizard dashboard’s Sonic Device DB panel reads to show BIOS, Windows flags, media expectations, and `udos_launcher` readiness.
- Partitioning and payload scripts (`sonic/scripts/partition-layout.sh`, `sonic/scripts/apply-payloads-v2.sh`) read the manifest to build GPT layouts, write the Alpine squashfs image, and copy Windows/media payloads. Each run writes a `sha256(layout)` digest so the dashboard can confirm the builder output before handing off to `Sonic Launcher`.

Documenting these APIs lets the plugin catalog, launchers, and automation scripts share the same manifest signing, device catalog, and wizard-friendly metadata that drives future Sonic bolt-ons.

## Sonic Media Player & Windows Launch Requirements

- The Windows and media payload expectations live in `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`. That spec details the multi-partition layout, `payloads/windows/scripts/launch-windows.sh`, and the three-mode boot priority (uDOS → Windows → Wizard).
- `memory/sonic/sonic-media.log` plus `sonic/docs/sonic-stick-media-addon-brief.md` capture the media player launch parameters and error codes; the Wizard dashboard pulls those logs so each hot reload/self-heal round can confirm the media-player story remains stable.
- Sonic also sets `windows10_boot`, `media_mode`, and `udos_launcher` flags in the device DB, letting the dashboard highlight whether a USB build contains the gaming launcher, Kodi kiosk, or Windows To Go profile.

Surfacing this information keeps the Sonic build plan, media player, and Windows launcher facts visible to contributors and automation hooks alike.

## Graphics, Font & Workspace Tools

- The dashboard’s `Font Manager`, `SVG Processor`, `Pixel Editor`, and `Layer Editor` all read seeds from `core/framework/seed/bank/graphics` and push exports back through the GUI file picker/workspace selector.
- Each tool shares plugin metadata with the `Wizard LibraryManagerService`, so imported fonts, SVG layers, and map tiles register with the same catalog the Sonic USB builder and plugin installers depend on.
- `wizard/routes/font_routes.py`, `wizard/routes/pixel_editor_routes.py`, and `wizard/routes/layer_editor_routes.py` surface the GUI file picker and workspace selectors so the editors always point at the seeded graphics, font collections, and tiled map layers stored in `memory/seed`.
 - Core font binaries now live outside the public repo (they are sourced locally from `~/uDOS/fonts` and mirrored to `https://cdn.fredporter.com/` per `docs/WIZARD-FONT-SYNC.md`), while `wizard/fonts` retains the manifest, distribution scripts, and credits referenced by the font manager. This keeps the repository lightweight while retaining the bundled Chicago FLF, PetMe64, Player2up, Teletext50, and other MUST-HAVE retro fonts for offline builds.

This keeps the graphics toolchain aligned with seeded assets, Sonic media payloads, and future plugin installers that expect consistent map and font collections.

## Automation & Roadmap Visibility

- The TUI startup banner writes the Self-Healer summary + Hot Reload stats to `memory/logs/health-training.log`, and automation scripts reread that payload before running `REPAIR`, `SHAKEDOWN`, or the `startup-script`/`reboot-script`. They rerun diagnostics only when the log shows remaining issues, so every training round is accountable.
- `memory/system/startup-script.md` and `.../reboot-script.md` now live in the seeded templates, execute automatically, and emit `PATTERN TEXT "Startup ready"` or `PATTERN TEXT "Reboot ready"` for tooling to detect the run without extra logging.
- Keeping the Hotkey Center, config page, and Sonic documentation updated keeps rounds 3‑10 pointing at this doc as the canonical slab described in `ROUNDS-3-10.md`.
- Maintain this doc and `docs/TUI-HOTKEY-AUTOMATION.md` whenever new plugin/Sonic milestones land so the Round 2 daily-cycle table always references the freshest installer/status/hotkey story.
 - The health log now surfaces `monitoring_summary`, `notification_history`, and the latest `provider-load.log` entries so automation banners, PATTERN runs, and the monitoring_manager dashboard all see the same throttling/issue state before gating PATTERN/REPAIR flows. `tools/trigger_library_throttles.py` exercises `/api/v1/library/*` and parser endpoints to populate `provider-load.log` before Cycle 2 so automation can replay throttling history during `/dev/` restarts.
