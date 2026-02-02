# uDOS Library

**Version:** Alpha v1.0.0.38+  
**Location:** `/library/` (tracked definitions) + `/memory/library/containers/` (local clones)

This directory contains **approved production extensions** and their container definitions.

## 🏗️ Library Structure

uDOS has **two library folders**:

| Path | Purpose | Status | Management |
|------|---------|--------|------------|
| **`/library/`** (root) | Approved production extensions | ✅ Tracked | Wizard function |
| **`/dev/library/`** | Extensions in development/testing | 🚧 Private | Wizard + Dev server |

**Management Roles:**
- **Wizard Server:** Manages both `/library/` and `/dev/library/`
- **Dev Server (Goblin):** Can manage `/dev/library/` for testing (if in `/dev/` folder)
- **Core:** Does **not** manage libraries (uses them if present, but management is Wizard-only)

---

## 📚 Library Organization

| Path                                | Purpose                                      | Git Tracked | Distribution      |
| ----------------------------------- | -------------------------------------------- | ----------- | ----------------- |
| **`/library/<tool>/container.json`**| uDOS container definition + metadata         | ✅ Yes      | Public repo       |
| **`/memory/library/containers/<tool>`** | Local clone of external repo (dev reference) | ❌ No       | Never distributed |
| **`/dev/library/<tool>/`**          | Extension under development                  | ❌ No       | Private only      |

**Examples:**

- `/library/typo/container.json` — uDOS container definition for Typo (approved)
- `/library/micro/container.json` — uDOS container definition for Micro editor (approved)
- `/memory/library/containers/typo/` — Local clone of `rossrobino/typo`
- `/memory/library/containers/micro/` — Local clone of `zyedidia/micro`
- `/dev/library/experimental-tool/` — New extension being tested (private)

---

## 🔄 Container Promotion Workflow

When a tool graduates from local experimentation to public distribution:

### Phase 1: Local Experimentation (Private Repo Only)

```bash
# Clone external repo for testing
mkdir -p /memory/library/containers
cd /memory/library/containers
git clone https://github.com/external/tool
cd tool/
# Test, modify, evaluate...
```

**Status:** Tool in `/memory/library/containers/tool/` (gitignored, not distributed)

### Phase 2: Create Container Definition (Public Distribution)

```bash
# Create container definition (tracked)
mkdir -p /library/tool/
cd /library/tool/

# Create container.json manifest
cat > container.json << 'EOF'
{
  "$schema": "../container.schema.json",
  "container": {
    "id": "tool",
    "name": "Tool Name",
    "type": "git",
    "source": "https://github.com/external/tool",
    "ref": "main",
    "install": "npm install && npm run build"
  },
  "udos": {
    "wrapper": "extensions/tool/",
    "commands": ["TOOL"],
    "integration": "wizard_downloads"
  }
}
EOF

# Optional: Add README, install script, etc.
```

**Status:** Tool definition in `/library/tool/` (tracked, distributed)

### Phase 3: Test via Wizard (Production Path)

```bash
# Wizard Server clones from upstream, packages, distributes
WIZARD INSTALL tool          # Tests full download → install workflow
TOOL --version               # Verifies integration works
```

### Phase 4: Commit and Distribute

```bash
# Commit container definition (NOT the cloned repo)
git add library/tool/
git commit -m "library: add tool container definition"
git push origin main

# GitHub Actions syncs to public repo (fredporter/uDOS)
# Users can now: WIZARD INSTALL tool
```

**Similar to:** Goblin (dev) → Wizard (production) promotion workflow

---

## 📦 Resource Types

| Type                | Location      | Git Status | Purpose                                   |
| ------------------- | ------------- | ---------- | ----------------------------------------- |
| **OS Images**       | `os-images/`  | Gitignored | ⚠️ DEPRECATED: TinyCore ISOs (use Alpine) |
| **Code Containers** | `containers/` | Gitignored | Cloned GitHub repos                       |
| **Packages**        | `packages/`   | Gitignored | Built APK packages (Alpine)               |
| **Templates**       | `templates/`  | Tracked    | Manifest templates, schemas               |

## ⚠️ DEPRECATED: TinyCore Images

**Status:** DEPRECATED — Use Alpine Linux instead  
**Migration:** See [docs/decisions/ADR-0003-alpine-linux-migration.md](../docs/decisions/ADR-0003-alpine-linux-migration.md)

```
library/tinycore/              # ⚠️ Deprecated
├── DEPRECATED.md             # Migration guide
├── README.md                 # Archived documentation
├── TinyCore-current.iso      # (not needed for Alpine)
└── setup.py                  # (use Alpine installer instead)
```

**For Alpine Linux:**

```bash
# Install from APK repository
apk add udos-core

# Or use installer script
./bin/install.sh
```

See: [docs/howto/alpine-install.md](../docs/howto/alpine-install.md)

---

## 🏗️ Code Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               WIZARD SERVER (Has Web Access)                 │
│                                                              │
│   git clone https://github.com/org/repo → library/          │
│                           ↓                                  │
│   Package as TCZ → Distribute via Private Transport          │
└─────────────────────────────────────────────────────────────┘
                            ↓
              (Mesh / QR Relay / Audio Relay)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  USER DEVICE (Offline)                       │
│                                                              │
│   extensions/cloned/meshcore/  ← Container (read-only)       │
│                    ↓                                         │
│   extensions/transport/meshcore/ ← uDOS Wrapper (our code)   │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** Container code is **read-only** on user devices. All modifications go in uDOS extension layers.

---

## 📦 Active Code Containers

### MeshCore (Primary Transport)

**Repository:** https://github.com/meshcore-dev/MeshCore  
**Type:** Code Container (Wizard-managed)  
**Purpose:** P2P mesh networking for offline communication

**Container Location:** `/memory/library/containers/meshcore/`

**uDOS Wrapper Layers:**
| Layer | Location | Purpose |
|-------|----------|---------|
| Transport | `extensions/transport/meshcore/` | Packet interface |
| Service | `extensions/play/services/meshcore_service.py` | Core service |
| Handler | `core/commands/mesh_handler.py` | TUI commands |

**Installation (Wizard Server):**

```bash
# Clone official repo (Wizard has web access)
git clone https://github.com/meshcore-dev/MeshCore extensions/cloned/meshcore

# Install uDOS integration
python extensions/setup/install_meshcore.py --install
```

**Container Manifest:** `extensions/cloned/meshcore/container.json`

---

### Typo Markdown Editor (Optional)

**Repository:** https://github.com/rossrobino/typo  
**Type:** Code Container  
**Purpose:** Markdown editing with .udos.md support

**Container Location:** `/memory/library/containers/typo/`

---

### Micro Editor (Optional)

**Repository:** https://github.com/zyedidia/micro  
**Type:** Code Container  
**Purpose:** Terminal text editor

**Container Location:** `/memory/library/containers/micro/`

---

## 🎤 Voice Libraries (Alpha v1.0.3.0+)

### Piper TTS (Text-to-Speech)

**Repository:** https://github.com/OHF-Voice/piper1-gpl  
**License:** GPL-3.0  
**Type:** Neural TTS Engine  
**Purpose:** Fast, local text-to-speech for 30+ languages

**Container Location:** `/memory/library/containers/piper/`

**Features:**

- ⚡ ~10x real-time synthesis on Raspberry Pi 4
- 🌍 30+ languages, multiple voice models
- 🔒 Completely offline
- 📦 Small models (16MB - 100MB per voice)

**TUI Commands:**

```bash
VOICE SAY "Hello world"              # Speak text
VOICE MODEL en_US-lessac-medium      # Set voice
VOICE VOICES                         # List voices
```

---

### Handy STT (Speech-to-Text)

**Repository:** https://github.com/cjpais/Handy  
**License:** MIT  
**Type:** Speech Recognition Engine  
**Purpose:** Offline speech-to-text using Whisper/Parakeet models

**Container Location:** `/memory/library/containers/handy/`

**Features:**

- 🆓 Free, open source (MIT)
- 🔒 Private - voice never leaves device
- 🎯 Voice Activity Detection (Silero VAD)
- 🌍 Auto language detection (Parakeet V3)

**Models:**
| Engine | Model | Size | Best For |
|--------|-------|------|----------|
| Parakeet | V3 | 478MB | CPU, auto-language |
| Whisper | Small | 487MB | GPU, fast |
| Whisper | Large | 1.1GB | GPU, best quality |

**TUI Commands:**

```bash
VOICE LISTEN                    # Start listening
VOICE LISTEN -t 30              # Listen 30 seconds
VOICE TRANSCRIBE recording.wav  # Transcribe file
```

---

### Voice Workflow Example

```python
# voice-assistant-script.md
VOICE SAY "How can I help you?"
SET input VOICE LISTEN
VOICE SAY "I heard: $(input)"
```

---

## 🎵 Music Libraries (Alpha v1.0.3.0+)

### Songscribe (Audio-to-Sheet-Music)

**Repository:** https://github.com/gabe-serna/songscribe  
**License:** MIT  
**Type:** Music Transcription Engine  
**Purpose:** Turn any song into sheet music using ML-powered transcription

**Container Location:** `/memory/library/containers/songscribe/`

**Features:**

- 🎵 Audio upload or YouTube URL input
- 🎸 ML-powered instrument separation (Moseca/Demucs)
- 🎹 Audio-to-MIDI conversion (Spotify Basic Pitch)
- 🥁 Specialized drum transcription (ADTOF)
- 📜 Automatic sheet music generation
- 📄 PDF export for printing

**Presets:**
| Preset | Stems | Use Case |
|--------|-------|----------|
| Solo | 1 | Single instrument |
| Duet | 2 | Vocals + accompaniment |
| Small Band | 4 | Rock/pop bands |
| Full Band | 6 | Complex arrangements |

**TUI Commands:**

```bash
MUSIC TRANSCRIBE song.mp3           # Full transcription
MUSIC SEPARATE song.mp3 --preset full_band
MUSIC STEMS song.mp3                # Export stems
MUSIC IMPORT transcription.mid      # Import to Groovebox
```

**Groovebox Integration:**

```
Audio → Songscribe → MIDI → Groovebox → MML Patterns
```

---

## 🔧 Container Management (Wizard Server Only)

### Install Container

```bash
# On Wizard Server
PLUGIN CLONE <name> <github-url>

# Example
PLUGIN CLONE meshcore https://github.com/meshcore-dev/MeshCore
```

### Update Container

```bash
# Check for updates
PLUGIN STATUS meshcore

# Pull updates
PLUGIN UPDATE meshcore
```

### Package for Distribution

```bash
# Create TCZ package
PLUGIN PACKAGE meshcore --format tcz

# Output: distribution/meshcore-1.0.0.tcz
```

### Distribute to Devices

```bash
# Via QR relay (multiple codes for large files)
QR SEND distribution/meshcore-1.0.0.tcz

# Via mesh network
MESH SEND device-id distribution/meshcore-1.0.0.tcz

# Via audio relay
AUDIO SEND distribution/meshcore-1.0.0.tcz
```

---

## 📋 Container Manifest Format

Each container should have a `container.json`:

```json
{
  "container": {
    "id": "meshcore",
    "name": "MeshCore Mesh Networking",
    "type": "git",
    "source": "https://github.com/meshcore-dev/MeshCore",
    "ref": "main",
    "cloned_at": "2026-01-05T12:00:00Z",
    "last_update": "2026-01-05T12:00:00Z",
    "commit": "abc123def456..."
  },
  "policy": {
    "read_only": true,
    "auto_update": false,
    "update_channel": "wizard_only"
  }
}
```

---

## 🔐 Security Model

1. **User devices never access GitHub** - All cloning done by Wizard Server
2. **Wizard verifies commits** - Check signatures before distribution
3. **Read-only containers** - User devices cannot modify container code
4. **Private transport only** - No internet required for updates
5. **Version pinning** - Can lock to specific commits

---

## 📂 Directory Structure

```
/library/
├── container.schema.json
├── container.template.json
├── micro/
│   └── container.json
├── typo/
│   └── container.json
└── meshcore/
    └── container.json

/memory/library/containers/
├── micro/          # git clone https://github.com/zyedidia/micro
├── typo/           # git clone https://github.com/rossrobino/typo
└── meshcore/       # git clone https://github.com/meshcore-dev/MeshCore
```

---

## ℹ️ Notes

- **Git ignored:** All containers ignored by `.gitignore`
- **Wizard-managed:** Updates come from Wizard Server only
- **Offline-first:** User devices work without internet
- **TCZ packaging:** Containers packaged as TCZ for Tiny Core

**See Also:**

- [Credits & Acknowledgments](../wiki/CREDITS.md) - All library credits and licenses
- [WIZARD-PLUGIN-SYSTEM.md](../../dev/roadmap/WIZARD-PLUGIN-SYSTEM.md)
- [CODE-CONTAINER.md](../transport/meshcore/CODE-CONTAINER.md)

---

_Last Updated: 2026-01-07 (Alpha v1.0.0.68)_
