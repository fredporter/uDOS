# Groovebox Songscribe Spec

The Groovebox + Songscribe milestone pairs the Groovebox sequencer with the Songscribe pattern editor so audio passes can capture both tidy playback data _and_ narrative task guidance. This spec covers the Songscribe grammar, the Groovebox → plugin flows, and how every install/reminder event feeds the shared health/hotkey story described in `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`.

## 1. Songscribe Markdown Grammar (Samples + Patterns)

Songscribe is a lightweight Markdown dialect that describes step sequences, loops, and automation tracks. The spec is intentionally terse so CLI/GUI renderers can surface the same data in 80×30 grids and calendars.

```
Title: Cosmic Draft
Tempo: 118
Key: C minor
Mode: Lydian
Loop: Arcade Strings

Track: bass
Steps: 0001 0900 2400 9000 0a80 2000 0f00 0000

Track: lead
Steps: 0400 0404 0412 0416 0424 0428 0430 0432

Track: fx
Riser: 2 bars
Impact: 1 measure
```

- `Track` names map to grooves/patterns (bass, lead, pad, drums, fx).  
- `Steps` use hex-coded velocity/timer slices so renderers show 8/16-step lanes easily.  
- Optional `Riser`, `Impact`, `Loop` or `Automation` annotations help the grid builders add FX/transition rows without needing dedicated canvases.

Automations may convert each Songscribe pattern into `groovebox` playlists, telemetry sequences, or Matrix-style `teletext` renderings by sampling the `Steps` string per row. The CLI/dashboards can also emit ASCII timelines (80×30) by reading `Steps` and mapping them to `#` vs. `.` characters.

## 2. Playback & Plugin API Mapping

1. **Groovebox routes**  
   - `/api/groovebox/playback`, `/api/groovebox/presets`, and `/api/groovebox/config` supply the transport, color, and monitoring data.  
   - `/api/groovebox/songscribe` reads `WizardLibraryManagerService.get_integration("songscribe")` to return install status. Use this endpoint to gate UI features (enable pattern editor only when the plugin is installed/enabled). citewizard/routes/groovebox_routes.py:87-102

2. **Songscribe parsing + Groovebox pattern endpoints**  
   - `/api/songscribe/parse` returns structured Songscribe metadata/tracks.  
   - `/api/songscribe/render` renders either `ascii` grids or raw Groovebox pattern JSON.  
   - `/api/songscribe/pattern` converts Songscribe markdown into Groovebox-ready patterns.  
   - `/api/groovebox/songscribe/parse` returns `{document, pattern, ascii}` and can persist patterns when `save=true`.  
   - `/api/groovebox/patterns` and `/api/groovebox/pattern` store patterns in `memory/groovebox/patterns/` for UI + CLI reuse.

3. **Plugin installs**  
   - Use `/api/library/integration/songscribe/install` or the CLI `PLUGIN install songscribe` command. Both share `wizard/services/plugin_repository.py` + `wizard/services/library_manager_service.py` so manifest validation, dependency wiring, and health logging stay centralized (per `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`).  
  - Every install response should include: Notion `to_do` blocks, weekly calendar/Gantt output, and the `todo_reminder` payload from the Apertus-guided PROMPT parser so the Hotkey Center can show the due-soon alert before the UI/automation passes run. citecore/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md:28-34

4. **Reminder + health log sync**  
   - `core/services/todo_reminder_service` logs due-soon alerts into `memory/logs/health-training.log` and `notification-history.log`. The Groovebox page should read the latest `status.todo_reminder` from `/hotkeys/data` and surface the ASCII clock banners alongside transport controls.  
  - Mention the reminder payload whenever Songscribe tasks are created so future milestones (Beacon/Sonic watchers, automation scripts) know that a playlist render, WAV export, or Songscribe review is due soon.

## 3. Checklist & Workflow Integration

When automating Songscribe workflows:

- Feed instructions into `PROMPT` (CLI or `/api/tasks/prompt`) with `workflow.schedule` or `todo.checklist` signals such as “Render Groovebox WAV export after Songscribe install.”  
- The resulting tasks go into `TodoManager`, render on the 80×30 calendar/Gantt views, and log reminders that the Hotkey Center / health banners can reuse before PATTERN/HOT reload runs.  
- Document each new Songscribe milestone in `memory/logs/hotkey-center.json` so the config page’s Hotkey Center banner stays in sync with plugin/install updates.

## 4. Delivery Steps

1. Keep `docs/GROOVEBOX-SAMPLE-LIBRARY-SPEC.md` and this spec aligned: the playlists or samples referenced in Songscribe sequences should exist in `wizard/groovebox/sounds/`.  
2. Use `/api/teletext/canvas` to render Songscribe grids; telemetry watchers can fetch `groovebox` data plus teletext layers to draw retro step boards.  
3. When new Songscribe grammar features land (per the Songscribe plugin manifest), update this spec and the Hotkey Center register so automation watchers know which keys or tasks to run next.
