# Groovebox Playback & Config Pages (Round 10)

These endpoints provide the data needed for the Groovebox playback and configuration UI while the Sonics/audio team builds the full sequencer.

## API reference

- `GET /api/groovebox/playback` – returns the current `now_playing` metadata (tempo/key loop/waveform), sample playlists, and sequences so the playback page can animate waveform panels and show timeline cards.  
- `GET /api/groovebox/presets` – exposes color/description presets (Arcade Mode, Nebula Drift, Analog Noir) to seed the UI theme and FX controls.  
- `GET /api/groovebox/config` – exposes master volume, MIDI export flag, default format, monitoring stats, and built-in hotkeys so the controller page can show current settings and status.

## UI guidance

1. Build a Svelte playback page that:
   * Calls `/api/groovebox/playback` to render waveform visuals and show playlists/sequences.
   * Uses the sample sequences to wire step sequencers in preview mode.  
2. Build a Groovebox config panel that reads `/api/groovebox/config` for the current mode/hotkeys/monitoring status and lists the `/api/groovebox/presets` colors with action buttons.
3. Surface the Notion/checklist reminders (from the plugin PROMPT parser) on the playback page to remind operators of queued tasks (e.g., “Render WAV export after plugin install”). The reminder payload is available via the plugin install `prompt` response and the Hotkey Center `status.todo_reminder` entry, so the playback UI can show it next to transport controls.

Use this page as the guide for wiring the Groovebox playback/config views and tie it back to the plugin/task automation docs for future rounds.

## Sample library

- Public-domain samples live in `wizard/groovebox/sample-library.json`; run `bash wizard/groovebox/setup-samples.sh` to download them into `groovebox/library/`. The folder is gitignored so each dev can refresh the samples locally without polluting the repo.
- The `docs/GROOVEBOX-SAMPLE-LIBRARY-SPEC.md` file contains the downloadable spec, curated free-pack links, kit folder tree, and licensing guidance so audio leads can share the manifest with dev teammates.

## Songscribe plugin linkage

- The Songscribe container is defined in `library/songscribe/container.json`; `/api/groovebox/songscribe` reports whether it is installed/enabled so the playback page can show transcribe/export readiness.  
- Trigger `/api/library/integration/songscribe/install` (or the CLI `PLUGIN install songscribe`) when you need the plugin; the resulting prompt payload surfaces Notion checklists, calendar/Gantt previews, and due-soon reminders in the Groovebox UI so audio tasks stay synced with automation.
