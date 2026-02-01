# Round 10 — Groovebox & Songscribe Outline

Round 10 brings Groovebox audio creation and the Songscribe pattern editor together with Wizard helper services. This wiki page captures the current reference spec (`docs/specs/ROUNDS-3-10.md`) and the pending Songscribe grammar/renderer deliverables so audio contributors can follow the plan.

## Deliverables

- **Sample library + waveform generator** – A database of synthetic loops/samples used by the Groovebox UI; later the Spellbook/Songscribe export should reference `sonic/docs/specs/sonic-stick-media-addon-brief.md` for payload consistency.  
- **Sample library spec** – The downloadable `docs/GROOVEBOX-SAMPLE-LIBRARY-SPEC.md` ties the categories/links, folder schema, and license reminder together so devs can mirror the directory tree locally and share the manifest with audio teammates.
- **Songscribe spec** – `docs/GROOVEBOX-SONGSCRIBE.md` finalizes the Songscribe Markdown grammar, the `/api/groovebox/songscribe` status endpoint, and the guide for funneling plugin installs/checklists through the PROMPT reminder pipeline so Groovebox playlists stay synced with the Hotkey Center.
- **Songscribe Markdown music syntax** – Define a pattern editor grammar that composes sequences/polyrhythms, similar to the Unison/Songscribe pattern rules previously prototyped.  
- **Step sequencer + pattern editor UI** – Wizard dashboard components that visualize step lanes, loops, automation tracks, and transition macros (reuses teletext/canvas tooling from Round 5).  
- **Audio synthesis/export** – Services that output WAV/MIDI/PDF plus waveform previews via the Wizard API routes; mention `groovebox` and `sonic/docs` modules for WAV packing and release.

## Next steps

1. Finalize the Songscribe grammar doc and publish it under `docs/specs/GROOVEBOX-SONGSCRIBE.md`.  
2. Build the Groovebox sample database (use `packages` or `memory` seeds for storage) and expose `/api/groovebox/samples`.  
3. Connect the Step sequencer UI to the playlist scheduler and allow exports to Sonar (MIDI/WAV/PDF).

Use this page as the audio-team checkpoint so future rounds know where Groovebox/Songscribe live even while the main spec doc evolves.
