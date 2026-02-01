# Round 8 — Wizard Plugin Ecosystem (Wiki Reference)

Round 8 stabilizes the plugin catalog, manifest distribution, and bolt-on workflow that the Wizard and Core teams share. This wiki entry mirrors the specs from `docs/specs/ROUNDS-3-10.md` and the plugin doc so contributors get context without digging through the bigger roadmap files.

## Key deliverables

- **Plugin manifest spec** (see `packages/` for existing manifests and `wizard/services/plugin_validation.py` for the schema).  
- **PackageManager service** – `wizard/services/library_manager_service.py` handles installation, update checks, dependency wiring, and health log reporting (`core/services/health_training.log_plugin_install_event`).  
- **Distribution repo** – Plugins live under `wizard/distribution/plugins/<plugin_id>`; each folder contains `manifest.json`, assets, and payloads that the CLI `PLUGIN` command (link `core/tui/ucode.py`) copies into `/library/` before calling `LibraryManagerService`.  
- **UI controls** – The config page, Hotkey Center, and wizard dashboard cards share the same metadata (manifest, checksum, validation) and the `/api/library/integration/<name>/install` endpoint to keep CLI/GUIs consistent.  
- **Health logging** – Every installation logs to `memory/logs/health-training.log` and the Hotkey Center register, letting automation and reminders spot manifest errors before `REPAIR` or `PATTERN` reruns.

## Next steps

1. Publish the plugin manifest spec (e.g., `docs/specs/PLUGIN-ARCHITECTURE.md`) and keep the index updated (`wizard/services/plugin_repository.py`).  
2. Add overlay controls/mod loader that respect plugin permissions (Future doc).  
3. Monitor the Sonic Screwdriver/Hotkey doc and add references to plugin statuses in `memory/logs/hotkey-center.json`.

This page can serve as the “plugin story desk” so future rounds can reference it for configuration, release, and automation context.
