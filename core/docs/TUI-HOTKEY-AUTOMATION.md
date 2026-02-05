# TUI Hotkey Automation Tracker

Milestone work relies on the Hotkey Center as the canonical source of truth for TAB, F1‑F8, and history bindings so every key-binding change is visible to automation scripts before they retrain the hot reload/self-heal loops.

## Visual + Machine-readable signals

- **Web route:** `http://127.0.0.1:8080/hotkeys` renders the table plus a small automation banner that points to the latest snapshot (`memory/logs/hotkey-center.png`) and the JSON endpoint.
- **JSON endpoint:** `GET /hotkeys/data` returns payload like:

  ```json
  {
    "key_map": [
      {"key": "Tab", "action": "Command Selector", "notes": "..."},
      {"key": "F1", "action": "Status / Help banner", "notes": "..."},
      ...
    ],
    "snapshot": "/Users/fredbook/Code/uDOS/memory/logs/hotkey-center.png",
    "last_updated": "2026-02-01T14:21:00.123456"
  }
  ```

- **Reminder signal:** The JSON payload now carries `status.todo_reminder`, which is the latest todo reminder logged via `PROMPT` or `/api/tasks/prompt`. Beacon/Sonic doc watchers should POST new instructions before each automation pass (CLI `PROMPT "<text>"` is available too) and confirm the reminder message appears in `/hotkeys/data`/`memory/logs/hotkey-center.json` before rerunning PATTERN, REPAIR, or any doc-monitoring flows. This surfaces due-soon alerts directly in the Hotkey Center banner so automation sees the reminder before gating the next pass.

- **Automation tip:** Automation scripts should download `/hotkeys/data` before each training window, verify the key_map matches the expected bindings, and store/compare the `snapshot` path plus JSON hash so UI changes cannot accidentally reroute TAB or F1 keys, and copy the same payload into `memory/logs/hotkey-center.json` for offline inspection. Automation runners (startup/reboot/rebuild) should read `memory/logs/hotkey-center.json` before each run to confirm the bindings still match the snapshot referenced in the health log and to echo the file path in the automation banner.
- **CLI helper:** `HOTKEYS` prints the same payload (via `core/commands/hotkey_handler.py`), so headless automation or ghost sessions can read the key map even when the dashboard isn’t running.
- **Local file:** `memory/logs/hotkey-center.json` mirrors the payload so the automation scripts (startup/reboot) can just read it before deciding to retrain the health story.

## Documenting key changes

1. When updating `core/tui/fkey_handler.py` or any `SmartPrompt` bindings, regenerate the hotkey page screenshot (save to `memory/logs/hotkey-center.png`) and rerun the `/hotkeys/data` endpoint to capture the new JSON.
2. The config page under `/config` now links to this hotkey route so testers can see the same table while rotating secrets or installing plugins.
3. Record the JSON payload and snapshot path in `memory/logs/health-training.log` (alongside Self-Healer stats) so automation can assert key stability before rerunning `REPAIR`/`SHAKEDOWN`.
4. Keep this doc synced with `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` (plugin catalog + Sonic roadmap) so the Wizard optimization plan can cite the latest install/hotkey state when gating automation runs.

## Automation Reference

- The Wizard optimization plan in `docs/WIZARD-OPTIMIZATION-v1.3.1.md` points to this hotkey guide before each automation/pattern pass so the key binding snapshot always precedes PATTERN/REPAIR flows. The newest `monitoring_summary` and `notification_history` payloads now sit alongside the hotkey payload in `memory/logs/health-training.log`, letting automation confirm both health metrics and key stability before rebooting.
- Batch jobs that reissue `REPAIR`, `REBOOT`, or `startup-script.md` checks now surface any throttling recorded in `memory/logs/provider-load.log` once the hotkey payload confirms the bindings referenced here; if throttles exist, automation reroutes into the throttling recovery path before replaying key bindings.
