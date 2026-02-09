# Groovebox Audio System

> **Version:** Transport v1.0.1.0

The Groovebox is uDOS's audio synthesis and data transmission system, using sound for both music creation and acoustic data transfer.

---

## Overview

### Capabilities

1. **Audio Synthesis**: MML-based music creation
2. **Acoustic Transport**: Data transmission via sound
3. **Imperial Patterns**: Pre-built sound patterns
4. **Sound Effects**: System feedback sounds

### Use Cases

- **Data Transfer**: Air-gapped device communication
- **Alerts**: Audio notifications
- **Music**: Background music and jingles
- **Accessibility**: Audio feedback for TUI

---

## MML Music Language

Groovebox uses **Music Macro Language (MML)** for music definition.

### Basic Syntax

```mml
# Note: C D E F G A B
# Octave: o4 (default), < (down), > (up)
# Length: 1=whole, 2=half, 4=quarter, 8=eighth, 16=sixteenth
# Rest: r

o4 c4 d4 e4 f4 g4 a4 b4 >c4
```

### Examples

```mml
# Simple melody
t120 o4 l8 cdefgab>c

# With rests
o4 c4 r4 e4 r4 g2

# Chords (channel mixing)
@1 o4 c4e4g4
@2 o3 c2
```

### MML Commands

| Command | Description | Example |
| ------- | ----------- | ------- |
| `o<n>` | Set octave (1-8) | `o4` |
| `l<n>` | Default length | `l8` |
| `t<n>` | Tempo BPM | `t120` |
| `v<n>` | Volume (0-15) | `v10` |
| `@<n>` | Channel select | `@1` |
| `<` | Octave down | `<c` |
| `>` | Octave up | `>c` |
| `r<n>` | Rest | `r4` |

---

## Imperial Patterns

Pre-built sound patterns for common scenarios.

### Available Patterns

| Pattern | Description | Trigger |
| ------- | ----------- | ------- |
| `startup` | Boot sequence | System start |
| `success` | Task complete | Command success |
| `error` | Error occurred | Command failure |
| `alert` | Attention needed | Notification |
| `receive` | Data incoming | Transport receive |
| `transmit` | Data sending | Transport send |

### Usage

```bash
# Play pattern
SOUND startup
SOUND success
SOUND error

# Custom MML
SOUND PLAY "o4 c4 e4 g4 >c2"
```

---

## Acoustic Data Transport

### Overview

Acoustic transport encodes data as sound for air-gapped transfer between devices.

### Protocol

```
┌─────────────────────────────────────────┐
│           Acoustic Packet               │
├─────────────────────────────────────────┤
│ Preamble │ Header │ Data │ Checksum │ End│
│  (sync)  │ (meta) │(payload)│ (CRC)  │   │
└─────────────────────────────────────────┘
```

### Encoding

- **Frequency Shift Keying (FSK)**
- **Audible range**: 1000-4000 Hz
- **Data rate**: ~50 bps (reliable)
- **Error correction**: Reed-Solomon

### Commands

```bash
# Enable acoustic transport
TRANSPORT AUDIO ON

# Send data
TRANSPORT AUDIO SEND "message"

# Listen for data
TRANSPORT AUDIO LISTEN

# Status
TRANSPORT AUDIO STATUS
```

---

## Sound Configuration

### Settings

`extensions/transport/audio/config.json`:

```json
{
  "audio": {
    "enabled": true,
    "volume": 0.7,
    "sample_rate": 44100,
    "patterns_enabled": true,
    "transport_enabled": false
  }
}
```

### Environment Variables

```bash
UDOS_SOUND=0          # Disable all sound
UDOS_SOUND_VOLUME=0.5 # Set volume (0.0-1.0)
```

---

## API Reference

### Python Interface

```python
from extensions.transport.audio import Groovebox

# Initialize
gb = Groovebox()

# Play pattern
gb.play_pattern('success')

# Play MML
gb.play_mml('o4 c4 e4 g4')

# Transmit data
gb.transmit('Hello, world!')

# Receive data
data = gb.receive(timeout=30)
```

### Module Structure

```
extensions/transport/audio/
├── __init__.py        # Module init
├── groovebox.py       # Main synthesizer
├── codec.py           # Audio encoding/decoding
├── transmitter.py     # Data transmission
├── receiver.py        # Data reception
├── sounds.py          # Sound patterns
├── imperial_patterns.mml  # Built-in MML
└── README.md          # Documentation
```

---

## Hardware Requirements

### Minimum

- Audio output device (speakers/headphones)
- For transport: Microphone input

### Recommended

- Quality speakers for music
- Quiet environment for transport
- USB audio interface for best quality

---

## Troubleshooting

### No Sound

```bash
# Check audio status
SOUND STATUS

# Test audio
SOUND TEST

# Check system audio
python -c "import pygame; pygame.mixer.init(); print('OK')"
```

### Transport Errors

```bash
# Check transport status
TRANSPORT AUDIO STATUS

# Test with echo
TRANSPORT AUDIO ECHO "test"

# Increase volume/reduce noise
```

---

## Examples

### Startup Jingle

```mml
# Imperial startup
t140 o4 l8
c4 e4 g4 >c4 r4
<g4 a4 b4 >c2
```

### Alert Pattern

```mml
# Urgent alert
t180 o5 l16
c c r c c r c c r c4
```

### Data Sync Sound

```mml
# Transmission start
t200 o4 l32
c d e f g a b >c<
b a g f e d c r4
```

---

## Related

- [Transport Policy](VISION.md#transport-policy)
- [Audio Transport](VISION.md#private-transports)
- [MeshCore](transport.md) - Other transports

---

*Part of the [uDOS Wiki](README.md)*
