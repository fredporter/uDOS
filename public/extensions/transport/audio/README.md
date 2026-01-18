# Audio Transport - Imperial Edition

**Version:** 1.1.0.9  
**Status:** ✅ COMPLETE  
**Aesthetic:** Dark Synth / Vader Vibes

---

## 🎵 Overview

Full acoustic data transfer system with Imperial-themed sounds.

### Components

| Module | Description | Status |
|--------|-------------|--------|
| `sounds.py` | Imperial sound generator (boot, breath, etc.) | ✅ |
| `codec.py` | FSK encoder/decoder (Bell 202) | ✅ |
| `groovebox.py` | MML parser + synthesizer | ✅ |
| `transmitter.py` | Real-time speaker output (pyaudio) | ✅ |
| `receiver.py` | Real-time microphone capture (pyaudio) | ✅ |

### Dependencies

```bash
# Required for real-time I/O
pip install pyaudio

# macOS
brew install portaudio

# Linux  
sudo apt-get install python3-pyaudio
```

---

## 🔊 TUI Commands

```bash
# File encoding (creates WAV file)
AUDIO SEND <file> [output.wav]
AUDIO RECEIVE <audio.wav> [output_file]
AUDIO SAY <text> [output.wav]

# Real-time transfer (through speaker/mic)
AUDIO TRANSMIT <file|text>     # Play FSK through speaker
AUDIO LISTEN [timeout] [file]   # Capture FSK from microphone

# Imperial sounds
AUDIO PLAY <pattern>           # BOOT, BREATH, HANDSHAKE, etc.
AUDIO GROOVE <mml>             # Render MML pattern
AUDIO BOOT                     # Boot sequence shortcut

# Diagnostics
AUDIO TEST                     # System test
AUDIO DEVICES                  # List audio devices
AUDIO HELP                     # Command help
```

---

## 🎵 Design Philosophy

The Dark Side of data transfer. Melodic, ominous, and unmistakably Imperial.

```
┌─────────────────────────────────────────────────────────────┐
│  🌑 AUDIO TRANSPORT - IMPERIAL EDITION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BOOT:      ♪ Deep bass hit → Minor arpeggio → Am chord    │
│  BREATH:    ♪ Vader respirator rhythm (bass + filtered)    │
│  HANDSHAKE: ♪ Imperial theme inspired call/response        │
│  DATA:      ♪ Arpeggiated synth stream (Am7 patterns)      │
│  SUCCESS:   ♪ Rising perfect fifth fanfare                 │
│  ERROR:     ♪ Descending tritone + bass rumble             │
│                                                             │
│       "I find your lack of bandwidth disturbing."          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎛️ Sound Design

### Musical Foundation (A Minor - Dark & Ominous)

| Note | Frequency | Usage |
|------|-----------|-------|
| A2 | 110 Hz | Deep bass foundation |
| C3 | 131 Hz | Minor third (tension) |
| E3 | 165 Hz | Perfect fifth (power) |
| A3 | 220 Hz | Root (carrier tone) |
| C4 | 262 Hz | Melody tension |
| E4 | 330 Hz | Melody resolution |
| G4 | 392 Hz | Minor 7th (ominous) |

### Waveform Palette

| Wave | Character | Usage |
|------|-----------|-------|
| Sine | Pure, warm | Bass, fundamentals |
| Triangle | Soft, hollow | Melody, pads |
| Square | Buzzy, aggressive | Accents, tension |
| Sawtooth | Rich, brassy | Bass growl |

### Processing Chain

```
Generator → Envelope (ADSR) → Filter (LP) → Reverb → Output
```

---

## 📡 Protocol Phases

### Phase 1: BOOT SEQUENCE
```
Duration: ~2 seconds
Sound: Bass hit → Ascending arpeggio → Minor chord swell

Components:
  ♪ 55Hz + 110Hz bass hit (0.3s)
  ♪ A2→C3→E3→A3→C4→E4 arpeggio (0.7s)
  ♪ Am chord with saw bass pad (0.8s)
```

### Phase 2: VADER BREATH (Connection Establishing)
```
Duration: ~2 seconds per cycle
Sound: Rhythmic filtered bass + noise

INHALE (0.8s):
  ♪ Rising 55Hz bass
  ♪ Filtered noise sweep up
  ♪ Smooth attack envelope

EXHALE (1.0s):
  ♪ Descending bass (55Hz → 38Hz)
  ♪ Filtered noise sweep down
  ♪ Gradual decay
```

### Phase 3: HANDSHAKE (Call & Response)
```
Duration: ~1.5 seconds each side
Sound: Imperial-inspired melodic phrases

INITIATOR:
  ♪ E4-E4-E4-C4-G4-E4-C4 (Imperial March rhythm)
  ♪ Layered sine + triangle + octave

RESPONDER:
  ♪ A3-C4-E4-G4-A4 (Rising acknowledgment)
  ♪ Same layered sound, different phrase
```

### Phase 4: DATA TRANSFER
```
Duration: Variable
Sound: Arpeggiated Am7 synth stream

Pattern: A3→C4→E4→G4→E4→C4 (repeating)
Tempo: ~12 notes/second (fast arpeggio)
Bass: Steady A2 underneath
Variation: Random octave jumps (30%)
```

### Phase 5: COMPLETE
```
SUCCESS:
  ♪ A3→E4→A4 (rising perfect fifth)
  ♪ Layered with octave harmonics
  ♪ Long reverb tail (triumphant)

ERROR:
  ♪ E4→A3 (descending fifth)
  ♪ Square wave for harshness
  ♪ 55Hz bass rumble (ominous)
```

---

## 🎮 TUI Commands

```bash
# Send file with Imperial sounds
AUDIO SEND test.txt
# Output: 
#   🌑 Initializing Imperial transport...
#   🫁 *vader breathing*
#   🤝 Handshake: ♪ E-E-E-C-G-E-C ♪
#   📡 Transmitting: [████████████] 100%
#   ✅ Transfer complete (2.3KB)

# Receive (listen mode)
AUDIO RECEIVE output.txt
# Output:
#   👂 Awaiting Imperial transmission...
#   🌑 Signal detected!
#   📡 Receiving: [████████░░░░] 67%

# Quick text message
AUDIO SAY "The Force is strong"
# Output:
#   🌑 ♪ *arpeggio stream* ♪
#   ✅ Message transmitted

# Settings
AUDIO MODE imperial   # Full dark synth (default)
AUDIO MODE silent     # Ultrasonic (inaudible)
AUDIO MODE minimal    # Just data tones, no theatrics
```

---

## 🔊 Generate Test Sounds

```bash
# Generate all sounds to /tmp/
python extensions/transport/audio/sounds.py

# Play full sequence (macOS)
afplay /tmp/imperial_transfer.wav

# Individual sounds:
afplay /tmp/boot.wav
afplay /tmp/vader_breath.wav
afplay /tmp/handshake_init.wav
afplay /tmp/data_stream.wav
afplay /tmp/success.wav
afplay /tmp/error.wav
```

---

## 🎯 Experience Goals

1. **Cinematic** - Sounds like powering up Imperial tech
2. **Musical** - Dark minor key, melodic not harsh
3. **Informative** - Different sounds = different states
4. **Functional** - Actually encodes/decodes data
5. **Memorable** - "That's the uDOS sound"

---

## 📁 File Structure

```
extensions/transport/audio/
├── __init__.py
├── sounds.py         # ImperialSounds generator
├── codec.py          # FSK encoding (coming)
├── transmitter.py    # Audio output (coming)
├── receiver.py       # Audio input (coming)
└── README.md
```

---

*"The data will be with you, always."*
