# Rounds 3-10 Guidance

## Round 3 – Core TUI Stabilization
- Harden the uCODE TUI window so it runs as the stable “slab” for downstream projects. Validate that the renderer, prompts, and selectors are visible (even under limited terminals) and that `SETUP` / `STORY tui-setup` can finish every question, confirm system date/time, and emit the final local/memory/bank/seed summary (reference `docs/SEED-INSTALLATION-GUIDE.md` for the verification checklist).
- Train the new executor pipeline to ensure CLI commands and developer workflows (hot reload triggers, `REPAIR`, `CONFIG`, etc.) stay available from within the TUI and from headless shells.
- Log Self-Healer diagnostics and Hot Reload watcher stats to `memory/logs/health-training.log` on every startup so automation can verify the hot-reload/self-heal training story each round.

## Round 4 – Plugin Ecosystem & Wizard Expansion
- Extend the Wizard to discover, install, and isolate modular bolt-on plugins; document how plugin metadata, versioning, and CLI commands enter the ecosystem so contributors can ship new capabilities safely, including the `/wizard/distribution/plugins/` manifest + `LibraryManagerService` flow that the Core `PLUGIN` command reuses.
- Capture the Sonic Screwdriver research: USB flashing routines, device database syncing, and Windows games/media player integrations that will be exposed as wizard bolt-ons.
- Publish the consolidated Wizard/Sonic plugin roadmap (see `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`) so the config page, hotkeys, and Sonic device/media APIs stay visible to future rounds.
- Drive the new `PLUGIN` command to surface the Wizard plugin catalog (`wizard/distribution/plugins/`), installation steps, and the Sonic Screwdriver gap document so contributors can see what still needs wiring into future wizard bolt-ons.

## Round 5-10 – Training & Automation
- **Hot-Reload / Self-Heal Training**: Integrate the `services/self_healer` diagnostics with the TUI’s startup banners and watchers. Train the automation scripts to re-run `REPAIR` when drift is detected, log each repair action, surface user-friendly guidance when auto-healing defers to manual steps, and assert the `memory/logs/health-training.log` payload before every round so the training summary can prove hot reload/self-heal coverage.
- Prioritize the same `health-training.log` payload for automation hooks (startup/reboot PATTERN scripts) so they only retrigger REPAIR/SHAKEDOWN when the SelfHealer report still shows remaining issues; this keeps every hot-reload/self-heal round accountable.
- Expand automated tests (TUI coverage, command dispatch, self-healing scenarios) so each round iterates on a tested baseline. Every change should trigger a regression check that covers the hot-reload/self-heal story and the plugin/sonic capabilities.
- Keep this doc up to date with new training materials, known limitations, and reference checkpoints so future rounds can build on the Core TUI as the canonical stable slab.
