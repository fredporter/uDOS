# Rounds 3-10 Guidance

## Round 3 – Core TUI Stabilization
- Harden the uCODE TUI window so it runs as the stable “slab” for downstream projects. Validate that the renderer, prompts, and selectors stay visible (even under limited terminals), that `SETUP` / `STORY tui-setup` finishes every question with the combined Date/Time/Timezone approval + override path, and that the completion banner lists the local/memory/bank/seed structure (reference `docs/SEED-INSTALLATION-GUIDE.md`).
- Train the new executor pipeline to ensure CLI commands and developer workflows (hot reload triggers, `REPAIR`, `CONFIG`, `PLUGIN`, etc.) stay available from within the TUI and from headless shells.
- Log Self-Healer diagnostics and Hot Reload watcher stats to `memory/logs/health-training.log` on every startup, capture the latest `/hotkeys/data` JSON + snapshot for traceability (see `docs/TUI-HOTKEY-AUTOMATION.md`), and surface everything in the banner so automation can verify the hot-reload/self-heal training story before each round. The banner should also emit how many remaining issues exist so the automation scripts gate `REPAIR`/`SHAKEDOWN` and `startup-script.md`/`reboot-script.md` reruns accordingly.

## Round 4 – Plugin Ecosystem & Wizard Expansion
- Extend the Wizard config page so `.venv`, the API/secret store, and the plugin/extension installers all render in one flow while linking to the Hotkey Center. Document how the manifest metadata surfaces through `wizard/services/plugin_repository.py` and `wizard/services/library_manager_service.py` so CLI installs reuse the same pipeline as the GUI.
- Capture the Sonic Screwdriver research (USB builder scripts, device database syncing, and Windows games/media player launch patterns) so these gaps are tracked as wizard bolt-ons with runtime artifacts, `sonic/datasets/sonic-devices.*`, and the `memory/sonic/sonic-media.log` steam.
- Keep the consolidated Wizard/Sonic plugin roadmap (`core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`) updated so the config panel, hotkey page, and Sonic docs remain the reference for rounds 3‑10.
- Drive the `PLUGIN` command to show the Wizard catalog, install through `LibraryManagerService`, and log every installation in `memory/logs/health-training.log` so automation and future rounds know what bolt-ons shipped.

## Round 5-10 – Training & Automation
- **Hot-Reload / Self-Heal Training**: Surface `SelfHealer` metrics directly in the `ucode` banner, log them to `memory/logs/health-training.log`, and keep the automation scripts tied to that same payload. Automation should only rerun `REPAIR`/`SHAKEDOWN`/startup scripts when `remaining` issues persist and should echo those details in the PATTERN banners.
- Guard the `startup-script.md` and `reboot-script.md` PATTERN flows with `services/health_training.needs_self_heal_training()` so the scripts auto-run only when drift exists, emit a traceable PATTERN banner for testing, read `memory/logs/hotkey-center.json` before running to confirm bindings match the hotkey snapshot, and log the `/hotkeys/data` payload so automation can audit key binding changes alongside health metrics.
- Expand automated tests (TUI coverage, command dispatch, self-healing scenarios) so each round iterates on a tested baseline. Every change should trigger a regression check that touches the hot-reload/self-heal story and the plugin/sonic capabilities.
- Keep this doc synced with `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` and the Hotkey Center so future rounds know where the stable slab lives.
