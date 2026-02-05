# ROADMAP TODO (v1.1.0)

## Core TUI & Story Forms
- [x] Audit `tui/form_fields.py`, `tui/story_form_handler.py`, and `src/tui` for duplicated widgets/handlers that can be consolidated into shared builders. Focus on the `DateTimeApproval`, `select`, and `location` pipelines because they are the most touched by the new TUI story.
- [x] Confirm variable input handlers emit predictions/prompts and surface the TUI command prompt even when the active terminal window is resized or running in ghost mode.
- [x] Verify `TUIFormRenderer` still paints fields, selectors, and progress status to keep the “wizard-style” story flow unblocked.
- [x] Ensure `DateTimeApproval` is wired through every story that requires system date/time confirmation (currently `tui-setup-story.md`) and that fallback validators still route through `SimpleFallbackFormHandler`.
- [x] Surface the local/memory/bank/seed structure in the completion summary and document the verification procedure in `docs/SEED-INSTALLATION-GUIDE.md`.

## Stability & Self-Heal
- [x] Map out redundant repair handlers (e.g., `commands/repair_handler.py` vs. `services/self_healer.py`) and align their diagnostics so the CLI/`REPAIR` command surfaces the same fixes seen in the automatic health-check banner.
- [x] Expand self-healing coverage for Python dependencies, CLI commands, and the TUI renderer so future milestones can rely on the "hot reload / self-heal" marketing claim.
- [x] Track recovery scripts for non-interactive environments (ghost mode, CI, automation runners) and ensure `SimpleFallbackFormHandler` always steps in when a terminal is unavailable.
- [x] Write Self-Healer diagnostics + Hot Reload stats to `memory/logs/health-training.log` so automation-aware training scripts can assert the hot-reload/self-heal workflow every pass.
- [x] Gate automation scripts (startup/reboot PATTERN flows and REPAIR/SHAKEDOWN runners) on `health-training.log` so we re-run diagnostics only when issues remain, logging the same summary that the TUI banner shows.
- [x] Add the `INTEGRATION` helper so GitHub and Mistral/Ollama wiring (folders, tokens, Wizard config paths) are visible via CLI/TUI as part of the self-heal/repair flow.

## Ecosystem & Accessories
- [x] Build out the Wizard Plugin Ecosystem (modular distribution + bolt-ons) so `WIZARD start` can advertise plugin discovery, installation, and isolation.
- [x] Assess the Sonic Screwdriver toolchain for USB flashing, device database syncing, and Windows-compatible games/media player integrations; capture gaps between the existing services and the desired capabilities (see `sonic/docs/README.md` and `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`).
- [x] Document the CLI commands and dev-ops flows that ship with the next executor so contributors know how to expand the plugin/sonic pipelines safely.
- [x] Surface the Wizard plugin catalog via the Core `PLUGIN` command (list/install/remove) and keep the Sonic Screwdriver gap report updated so the plugin/sonic roadmap stays visible to future milestones.
- [x] Document the Wizard/Sonic plugin/USB roadmap, the all-in-one config panel, and the Font/Pixel/Layer tool coverage in `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`.

## STREAM1 Runtime
- [x] Phase 1C interpolation helpers so state and set blocks can reuse the same variable resolver (documents + tests under `memory/tests/phase1`).
- [x] Phase 1D read-only SQLite executor (requires `better-sqlite3`) to pluck rows into state and share them with panels/forms.
- [x] Phase 1E document runner enhancements that aggregate section output, track executed sections, and return the final state snapshot for integrations.

## Next Milestone Deliverables
- [x] Keep the uCODE TUI running in a stable windowed mode with reliable CLI commands, hot-reload watchers, and self-healing fallbacks.
- [x] Surface any remaining TODOs in `docs/specs/v1.3.1-milestones.md` so later milestones reference the updated Core TUI as their stable slab.
- [x] Align the next milestone work with the Wizard optimization moves in `docs/WIZARD-OPTIMIZATION-v1.3.1.md` so automation cadence is driven by verifiable outcomes instead of time buckets.
