# Wizard + Sonic Plugin Ecosystem (v1.1+)

This reference describes the restored All-In-One Wizard config panel, the Sonic Screwdriver document API surface, and the hotkey + GUI tooling coverage that keeps the Plugin Ecosystem story visible for rounds 3‑10.

## Wizard Central Config

The Wizard config page now highlights:

- **.venv management** (create/delete) so Python dependencies that power the dashboards, CLI, and plugin installers stay isolated.
- **Wizard API / Secret Store** entries that show each key/secret name plus rotate buttons, forcing all sensitive values through the unified keystore instead of ad-hoc text files.
- **Plugin repository view** that reads the manifests from `wizard/distribution/plugins/`, surfaces name/description/version, and installs them through the `LibraryManagerService`. These installs run the same manifest/verification logic that the Core `PLUGIN install` command consumes.
- **Hotkey link** to the new `hotkeys` route so TAB, F1-F8, and arrow bindings documented in `core/tui/fkey_handler.py` stay synchronized between the GUI and CLI.

> The config panel is the single place to manage the runtime’s plugin lifecycle, secret store, and `.venv` bootstrap with explicit references to the plugin catalog and hotkey center.

## Sonic Screwdriver APIs and Roadmap

### USB builder and device database

- The Sonic CLI (`sonic/core/sonic_cli.py --plan`/`--run`) orchestrates USB builds and produces signed manifests plus `sha256(layout)` digests for UI verification.
- Device data lives in `sonic/datasets/sonic-devices.sql` + `sonic/datasets/sonic-devices.schema.json`; the runtime loads it into the SQLite `memory/sonic/sonic-devices.db`, which Wizard shares so the dashboard can show available targets and the `Sonic Device DB` panel.
- For Windows deployments the payload pipeline injects `payloads/windows/scripts/launch-windows.sh`, updates `devices.db` with `windows10_boot` flags, and pushes QoS/driver prep scripts before handing control to the Sonic media player.

### Media, Windows games, and Sonic launcher hooks

- Media playback uses `memory/sonic/sonic-media.log` and `sonic-stick-media-addon-brief.md` to surface media errors; the Wizard dashboard reads that log to report playback health.
- Windows/gaming payloads include the `media-player` and `Sonic Launcher` hooks described in `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`; the dashboard surfaces the planned capability list so contributors can see what still needs wiring.
- The Sonic/Sonic CLI plan-run contract (two-phase manifest/execute) is surfaced via the Wizard plugin installer so the Core `PLUGIN` command can orchestrate `Sonic` stories within the same UI – everything shares the `LibraryManagerService` validation pipeline.

## Hotkeys, Font & Graphics Tool Coverage

- The new Wizard `Hotkey Center` page documents the F1-F8, TAB, and history keystrokes that Core’s `SmartPrompt` and `FKeyHandler` rely on. It keeps hotkey mappings visible to automation scripts that inspect `memory/logs/health-training.log` before retraining hot reload/self-heal flows.
- `Font Manager`, `SVG Processor`, `Pixel Editor`, and `Layer Editor` now include notes stating they read assets from `core/framework/seed/bank/graphics` and send exports through the GUI file picker/workspace selector so Sonic USB payloads, map layers, and font collections stay aligned with seeded data.
- The workspace selector, GUI file picker, and media/player dashboards all share plugin metadata pulled from the `Wizard LibraryManagerService`, ensuring new extension installs automatically register fonts, map tiles, and tool palettes for use inside these editors.

## Next Steps for Rounds 3‑10

1. Link the Core `PLUGIN` command to the same manifest validation pipeline (`wizard/plugin_repository` + `LibraryManagerService`) so installs via CLI or GUI obey the same signatures.
2. Surface Sonic USB build plan logs, device DB updates, and media player events within the Wizard dashboard so each Hot Reload / Self Heal round can confirm those capabilities from the same `memory/logs/health-training.log` entries.
3. Keep the Hotkey Center, config page, and Sonic documentation updated whenever new Wizard bolt-ons (Font/Pixel/Layer editors) or Sonic payloads are added so the roadmap remains visible to contributors.
