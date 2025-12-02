# Project Brief for Copilot – MML + LilyPond Groovebox with 808 Vibe

## Goal

Generate a set of **text-based music assets** using:

- **MML (Music Macro Language)** for pattern-based sequencing (groovebox style)
- **LilyPond** for notated scores that can export to **MIDI**

The musical aesthetic should combine:

- **Roland MC-303–style groovebox patterns** (dance / techno / house / electro)
- **TR-808–inspired drum programming** (authentic 808 vibe)
- **80s analogue & FM synth sounds**
- **Open-source retro game sound effects**
- **Open-source funny / nostalgic sounds**

All code, patterns, and references must be compatible with **open-source tooling**.

---

## Tech + File Structure

Copilot, generate and extend files like:

- `patterns/drums_808.mml`
  - MML drum patterns that assume TR-808–style sounds:
    - Long subby kick
    - Snappy snare
    - Closed/open hi-hats
    - Handclap
    - Cowbell, toms, rimshot
  - Use pattern-based, loop-friendly structures for a groovebox feel.

- `patterns/bass_303.mml`
  - Acid / MC-303–style basslines:
    - Squeltchy resonant saw/square
    - Slides and accents
    - 1–2 bar patterns, chained to form 8–16 bar sections.

- `patterns/leads_pads_80s.mml`
  - 80s synth motifs:
    - Juno-style warm pads
    - DX7-style FM electric piano plucks
    - Simple arpeggios and hooky leads.

- `score/main_score.ly`
  - LilyPond score representing the arrangement:
    - Separate voices/staves for: drums, bass, lead, pads, FX.
    - Exportable to MIDI for use in open-source DAWs (e.g. LMMS, Ardour).
    - Mark sections (Intro, Verse, Chorus, Break, Outro).

- `fx/game_sfx_notes.md` / `fx/funny_sfx_notes.md`
  - Describe where **open-licence** / **CC0** retro and funny sounds will be layered:
    - 8-bit style game SFX: jumps, coins, lasers, UI bleeps.
    - Nostalgic / humorous sounds: cartoon boings, “power up” sweeps, arcade insert-coin type sounds, modem/dial-up–style noise textures.
  - Always assume **open-source or CC0 sample packs**, or synthesised equivalents (no proprietary game rips).

---

## Style & Constraints

Copilot, follow these guidelines:

- **Tempo & feel**
  - Default project tempo: **120–130 BPM** (house / techno / synth-pop).
  - Use 4/4 time, emphasising **groovebox-style loops** (1, 2, 4, or 8 bars).

- **Drums (TR-808 vibe)**
  - Program classic patterns:
    - Four-on-the-floor kick with syncopated claps and hats.
    - Electro / early hip-hop variations with off-beat kicks and snare fills.
  - Clearly comment which parts are “808-style” so they can be mapped to 808 kits in Hydrogen/LMMS.

- **Synths (MC-303 / 80s)**
  - Reference:
    - MC-303 rompler-style stabs and dance presets.
    - 80s synths like Juno, Jupiter, DX7, and Prophet.
  - Focus on:
    - Simple, catchy motifs and basslines.
    - Chord stabs, gated pads, and arps.

- **Game & nostalgic SFX**
  - Treat SFX as separate voices/tracks (e.g. `sfx_voice` in MML, extra staff or cue notes in LilyPond).
  - Only reference **generic** retro game tropes:
    - “Coin pickup”, “damage blip”, “menu move”, “laser shot”.
  - Only use **open-source / CC0** style descriptions, avoid anything that implies ripping commercial game audio.

- **Licensing & openness**
  - Assume all generated patterns, text, and structures will be released under an open licence (e.g. MIT / CC0).
  - Do **not** reference or imitate specific copyrighted melodies.
  - Keep everything generic, stylistic, and original.

---

## What Copilot Should Generate

1. **MML pattern templates** for drums, bass, leads, pads, and SFX with comments explaining:
   - Intended sound (808 kick, 303 bass, 80s pad, NES-style blip, etc.).
   - Bar length and how patterns should be chained.

2. **LilyPond scores** that:
   - Mirror the MML patterns in a readable staff notation form.
   - Include instrument names and section markers.
   - Are ready for MIDI export.

3. **Optional examples**:
   - A “demo track” combining:
     - 808-style drum loop
     - MC-303 / 303-style bassline
     - 80s synth lead
     - Retro game SFX and a few funny/nostalgic sound cues.

Use concise, well-commented examples that make it easy to iterate on patterns, remix sections, and swap sound sources in an open-source toolchain.
