# Groovebox - Music Production System v1.0.0

**Text-based music production with 808 vibes, MC-303 workflow, and 80s synth aesthetics**

**Status:** Standalone application (migrated from Goblin)
**Location:** `/groovebox/`
**Components:** Python engine + SvelteKit UI

---

## Overview

Groovebox is a standalone music production system for uDOS with:

- **Python Engine** - MML parser, sequencer, MIDI export, synthesis
- **SvelteKit UI** - Web-based producer interface (Mixer, Pattern Grid, Transport)
- **Standalone Mode** - Independent from Goblin dev server
- **.udos.md** - Executable music notation blocks
- **Wizard Server** - Sound pack distribution

---

## Architecture

```
groovebox/
├── version.json                    # Component version v1.0.0
├── README.md                       # Main documentation
├── package.json                    # Node.js dependencies (SvelteKit)
├── svelte.config.js               # Svelte configuration
├── tsconfig.json                  # TypeScript configuration
├── vite.config.ts                 # Vite build configuration
│
├── src/                           # SvelteKit application
│   ├── lib/
│   │   └── components/
│   │       ├── MixerPanel.svelte      # 8-channel mixer
│   │       ├── PatternGrid.svelte     # Pattern editor
│   │       ├── SoundBrowser.svelte    # Instrument browser
│   │       ├── TransportBar.svelte    # Playback controls
│   │       └── index.ts               # Component exports
│   ├── routes/
│   │   ├── +page.svelte               # Main page
│   │   └── api/
│   │       └── pattern/
│   │           └── +server.ts         # Pattern API
│   └── README.md                  # SvelteKit app guide
│
├── engine/                         # Python synthesis engine
│   ├── mml_parser.py              # Music Macro Language parser
│   ├── sequencer.py               # Pattern sequencer
│   ├── midi_export.py             # MIDI export
│   └── lilypond_bridge.py         # Score generation
│
├── instruments/                    # Synthesis modules
│   ├── drum_808.py                # TR-808 emulation
│   ├── bass_303.py                # TB-303 bass synth
│   └── synth_80s.py               # Retro synthesizer
│   ├── bass_303.py           # TB-303/MC-303 bass synthesizer
│   ├── synth_80s.py          # Juno/DX7/Prophet style synths
│   └── sfx_retro.py          # 8-bit game + nostalgic sound effects
├── sounds/
│   ├── kits/                 # Drum kits (808, 909, retro)
│   ├── samples/              # One-shot samples (SFX, vocals, hits)
│   └── presets/              # Synth presets (bass, lead, pad)
├── plugins/
│   ├── plugin_wrapper.py     # Load VST/CLAP/LV2 via ctypes/bridge
│   ├── lmms_bridge.py        # LMMS project export
│   ├── vcvrack_bridge.py     # VCV Rack patch integration
│   └── fluidsynth_bridge.py  # SoundFont rendering
├── library/
│   ├── sound_manager.py      # Sound pack installation/indexing
│   ├── catalog_client.py     # Download from wizard/web/catalog/
│   └── pack_builder.py       # Create distributable sound packs
├── ui/
│   ├── tui_pattern_editor.py # TUI viewport for pattern editing
│   ├── tui_mixer.py          # TUI mixer panel (volume, pan, FX)
│   └── tui_transport.py      # Play/stop/record controls
└── tauri/
    ├── groovebox_mode.svelte # Groovebox Mode UI component
    ├── pattern_grid.svelte   # Pattern grid (16-step sequencer)
    ├── mixer_panel.svelte    # Channel mixer with faders
    ├── sound_browser.svelte  # Sound library browser
    └── transport_bar.svelte  # Transport controls (play/stop/loop)
```

---

## Integration Points

### 1. TUI - `PLAY` / `MUSIC` Command

**Command:** `PLAY [pattern_file.mml]` or `MUSIC [pattern_file.mml]`

**Handler:** [core/commands/music_handler.py](core/commands/music_handler.py)

**Viewport:**

- Pattern editor (16-step grid, MML text view)
- Transport controls (play/stop/bpm/loop)
- Channel mixer (8 tracks: drums, bass, lead, pad, fx1-4)
- Sound browser (kits, samples, presets)

**Example:**

```
uDOS> PLAY memory/music/demo_808.mml
```

### 2. .udos.md - Executable Music Notation

**.udos.md format:**

````markdown
# Song Title

```mml
t125 l16 o4 v14
; drums
[C--- A-A- D--- A-A-]4
; bass
[c8 c16 c16 g'8 f8 ees8 d8]2
```
````

**Execution:**

- `RUN music/my_song.udos.md` → Plays embedded MML
- Editable in Typo markdown app
- Version controlled in memory/music/

### 3. Tauri App - Groovebox Mode

**Mode Switcher:** Terminal | Teledesk | Desktop | **Groovebox** | Dashboard

**UI Components:**

- **Pattern Grid** - 16-step sequencer (Tailwind: grid-cols-16)
- **Mixer Panel** - 8 channel faders with meters
- **Sound Browser** - Categorized library (drums/bass/synth/sfx)
- **Transport Bar** - Play/stop/record/loop/BPM controls
- **Preset Manager** - Save/load patterns and projects

**Styling:** Tailwind with 808-inspired color scheme (orange accents, dark gray panels)

### 4. Wizard Server - Distribution

**Web Catalog:** `http://wizard-ip:8080/catalog/groovebox/`

**Categories:**

- **Sounds** - 808 kits, retro samples, CC0 SFX
- **Plugins** - LMMS instruments, VCV Rack modules, SoundFonts
- **Packs** - Curated bundles (808 Essentials, 80s Synth Pack, Retro Game SFX)

**Pack Format:**

```json
{
  "name": "808-essentials-v1",
  "version": "1.0.0",
  "type": "drum_kit",
  "license": "CC0",
  "files": [
    "sounds/kits/808/kick.wav",
    "sounds/kits/808/snare.wav",
    ...
  ],
  "metadata": {
    "description": "Classic TR-808 drum kit",
    "author": "uDOS Community",
    "tags": ["808", "drums", "retro"]
  }
}
```

---

## Dependencies

**Core Python:**

- `mido` - MIDI file generation
- `numpy` - Audio processing
- `sounddevice` - Realtime playback (optional, Alpine-compatible)

**Optional Bridges:**

- LMMS (installed via TCZ package or Wizard)
- VCV Rack (Wizard Server only, web-capable)
- FluidSynth (Alpine-compatible)
- LilyPond (score generation, optional)

**Distribution:**

- All sound packs: CC0 or open-source licensed
- Plugins: Open-source only (CLAP/LV2 preferred over VST)

---

## Transport Policy

**Realm:** Extension works in both realms with different capabilities

**Device Mesh (Realm A):**

- ✅ Local playback and pattern editing
- ✅ Sound library (pre-installed packs)
- ✅ MIDI export for external gear
- ❌ No web access for sound downloads

**Wizard Server (Realm B):**

- ✅ All Realm A features
- ✅ Web catalog access (download sound packs)
- ✅ Plugin hosting (heavier VSTs/bridges)
- ✅ Community pack uploads

---

## Development Phases

### Phase 1: Core Engine (v1.0.0.0)

- MML parser and sequencer
- Basic 808 drum machine (kick, snare, hats)
- MIDI export
- TUI pattern editor viewport

### Phase 2: Instruments (v1.0.1.0)

- 303-style bass synth
- 80s synth presets (pad, lead, arp)
- Retro game SFX engine
- Sound manager (load/index packs)

### Phase 3: TUI Integration (v1.0.2.0)

- `PLAY`/`MUSIC` command handler
- Transport controls (play/stop/loop)
- Channel mixer viewport
- Sound browser viewport

### Phase 4: Tauri Integration (v1.0.3.0)

- Groovebox Mode UI (Tailwind)
- Pattern grid component
- Mixer panel with faders
- Sound browser with preview

### Phase 5: Wizard Distribution (v1.0.4.0)

- Web catalog (Flask/FastAPI)
- Pack builder (create .tar.gz bundles)
- Catalog client (download/install)
- Plugin wrapper (LMMS/VCV/FluidSynth)

---

## Sound Library Structure

```
memory/groovebox/
├── library/
│   ├── drums/
│   │   ├── 808-essentials/
│   │   ├── 909-classic/
│   │   └── retro-8bit/
│   ├── bass/
│   │   ├── 303-acid/
│   │   ├── sub-bass/
│   │   └── synth-bass/
│   ├── synth/
│   │   ├── 80s-pads/
│   │   ├── fm-leads/
│   │   └── arpeggios/
│   └── sfx/
│       ├── game-retro/
│       ├── funny-nostalgic/
│       └── ui-sounds/
├── projects/
│   ├── demo_808.mml
│   ├── acid_house.mml
│   └── survival_theme.udos.md
└── patterns/
    ├── drums_808.mml
    ├── bass_303.mml
    ├── leads_pads_80s.mml
    └── sfx_game.mml
```

---

## Licensing

**Extension Code:** MIT (matches uDOS core)

**Sound Packs:** CC0 or equivalent (public domain, no attribution required)

**Plugins/Bridges:** Follow upstream licenses (LMMS: GPL, VCV Rack: GPL, FluidSynth: LGPL)

**Community Packs:** Must be CC0 or openly licensed to be hosted on Wizard catalog

---

## References

- [groovebox.md](../../dev/roadmap/audio/groovebox.md) - Original spec
- [audio-resources.md](../../dev/roadmap/audio/audio-resources.md) - Plugin/sound references
- [main_score.ly](../../dev/roadmap/audio/main_score.ly) - LilyPond example
- [drums_808.mml](../../dev/roadmap/audio/drums_808.mml) - MML drum patterns

---

_Last Updated: 2026-01-05_
_Version: v1.0.0.0_
